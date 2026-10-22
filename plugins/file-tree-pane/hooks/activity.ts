// What a tool call of Claude's touches: the files it reads or searches, the files it writes,
// and the git or GitHub operation a shell command runs.

export type ActivityKind = 'read' | 'write' | 'commit'

export type GitOp = {
  tool: 'git' | 'gh'
  /** The subcommand, `commit` or `pr create`. */
  name: string
}

export type Touches = {
  reads: string[]
  writes: string[]
  ops: GitOp[]
}

const NONE: Touches = { reads: [], writes: [], ops: [] }

const stringField = (input: object, key: string): string | undefined => {
  const value: unknown = Reflect.get(input, key)
  return typeof value === 'string' && value !== '' ? value : undefined
}

/** Splits a command line into words, honoring quotes and backslashes, without a shell. */
export const splitWords = (line: string): string[] => {
  const words: string[] = []
  let word = ''
  let quote: '"' | "'" | null = null
  let hasWord = false
  for (let i = 0; i < line.length; i += 1) {
    const char = line[i] ?? ''
    if (quote !== null) {
      if (char === quote) {
        quote = null
      } else if (char === '\\' && quote === '"' && i + 1 < line.length) {
        i += 1
        word += line[i] ?? ''
      } else {
        word += char
      }
      continue
    }
    if (char === '"' || char === "'") {
      quote = char
      hasWord = true
    } else if (char === '\\' && i + 1 < line.length) {
      i += 1
      word += line[i] ?? ''
      hasWord = true
    } else if (/\s/.test(char)) {
      if (hasWord) {
        words.push(word)
      }
      word = ''
      hasWord = false
    } else {
      word += char
      hasWord = true
    }
  }
  if (hasWord) {
    words.push(word)
  }
  return words
}

// Commands whose operands are files or folders they read; the first operand of the second set
// is a pattern or a script, not a path.
const READERS = new Set([
  'cat',
  'head',
  'tail',
  'less',
  'more',
  'bat',
  'wc',
  'nl',
  'file',
  'stat',
  'ls',
  'tree',
  'find',
  'du',
  'diff',
  'xxd',
  'od',
  'strings',
])
const PATTERN_FIRST = new Set(['grep', 'egrep', 'fgrep', 'rg', 'ag', 'ack', 'sed', 'awk'])
const WRITERS = new Set([
  'touch',
  'mkdir',
  'rm',
  'rmdir',
  'mv',
  'cp',
  'tee',
  'ln',
  'truncate',
  'chmod',
])
const PREFIXES = new Set(['sudo', 'time', 'nice', 'nohup', 'command', 'exec', 'env'])

const GIT_OPS = new Set([
  'commit',
  'push',
  'pull',
  'fetch',
  'checkout',
  'switch',
  'merge',
  'rebase',
  'stash',
  'reset',
  'restore',
  'revert',
  'cherry-pick',
  'tag',
  'clone',
  'init',
  'am',
  'apply',
])
const GH_NOUNS = new Set(['pr', 'repo', 'release', 'issue', 'run', 'workflow'])

// git's options that take a value as the next word, before the subcommand.
const GIT_VALUE_OPTIONS = new Set(['-C', '-c', '--git-dir', '--work-tree', '--namespace'])

const gitOpOf = (words: readonly string[]): GitOp | null => {
  const [tool, ...rest] = words
  if (tool === 'git') {
    for (let i = 0; i < rest.length; i += 1) {
      const word = rest[i] ?? ''
      if (GIT_VALUE_OPTIONS.has(word)) {
        i += 1
        continue
      }
      if (word.startsWith('-')) {
        continue
      }
      return GIT_OPS.has(word) ? { tool: 'git', name: word } : null
    }
    return null
  }
  if (tool === 'gh') {
    const [noun, verb] = rest
    if (noun !== undefined && GH_NOUNS.has(noun) && verb !== undefined && !verb.startsWith('-')) {
      return { tool: 'gh', name: `${noun} ${verb}` }
    }
  }
  return null
}

/** The files a shell command reads and writes, and the git or gh operations it runs. */
export const parseCommand = (command: string): Touches => {
  const reads: string[] = []
  const writes: string[] = []
  const ops: GitOp[] = []
  for (const segment of command.split(/&&|\|\||[;|\n]/)) {
    // Redirections write their target whatever the command is.
    const redirect = /(?:^|[^<>&\d])>>?\s*("[^"]+"|'[^']+'|[^\s;&|]+)/g
    for (const match of segment.matchAll(redirect)) {
      const target = splitWords(match[1] ?? '')[0]
      if (target !== undefined && target !== '/dev/null' && !target.startsWith('&')) {
        writes.push(target)
      }
    }
    const words = splitWords(segment.replace(/\d*>>?\s*("[^"]+"|'[^']+'|[^\s;&|]+)/g, ' '))
    while (
      words.length > 0 &&
      (PREFIXES.has(words[0] ?? '') || /^[A-Za-z_]\w*=/.test(words[0] ?? ''))
    ) {
      words.shift()
    }
    const [name, ...args] = words
    if (name === undefined) {
      continue
    }
    const op = gitOpOf(words)
    if (op !== null) {
      ops.push(op)
      continue
    }
    const operands = args.filter((arg) => !arg.startsWith('-'))
    const isInPlace = name === 'sed' && args.some((arg) => arg === '-i' || arg.startsWith('-i'))
    if (WRITERS.has(name) || isInPlace) {
      writes.push(...(isInPlace ? operands.slice(1) : operands))
    } else if (READERS.has(name)) {
      reads.push(...operands)
    } else if (PATTERN_FIRST.has(name)) {
      reads.push(...operands.slice(1))
    }
  }
  return { reads, writes, ops }
}

/** What one tool call touches, by the tool's name and its input. */
export const touchesOf = (tool: string, input: object): Touches => {
  switch (tool) {
    case 'Read':
    case 'NotebookRead': {
      const path = stringField(input, 'file_path') ?? stringField(input, 'notebook_path')
      return path === undefined ? NONE : { reads: [path], writes: [], ops: [] }
    }
    case 'Grep':
    case 'Glob': {
      const path = stringField(input, 'path')
      return path === undefined ? NONE : { reads: [path], writes: [], ops: [] }
    }
    case 'Edit':
    case 'MultiEdit':
    case 'Write': {
      const path = stringField(input, 'file_path')
      return path === undefined ? NONE : { reads: [], writes: [path], ops: [] }
    }
    case 'NotebookEdit': {
      const path = stringField(input, 'notebook_path')
      return path === undefined ? NONE : { reads: [], writes: [path], ops: [] }
    }
    case 'Bash': {
      const command = stringField(input, 'command')
      return command === undefined ? NONE : parseCommand(command)
    }
    default:
      return NONE
  }
}

/** The footer's words for an operation: `git commit`, `gh pr create`. */
export const opLabel = (op: GitOp): string => `${op.tool} ${op.name}`
