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

const WHITESPACE = /\s/
// A `NAME=value` assignment before a command's name.
const ASSIGNMENT = /^[A-Za-z_]\w*=/
// What ends one command of a line: `&&`, `||`, `;`, a pipe or a new line.
const COMMAND_SEPARATOR = /&&|\|\||[;|\n]/

const stringField = (input: object, key: string): string | undefined => {
  const value: unknown = Reflect.get(input, key)
  return typeof value === 'string' && value !== '' ? value : undefined
}

/** Where splitWords is: the words so far, the one being read, and the quote it is inside. */
type Splitter = { words: string[]; word: string; quote: '"' | "'" | null; hasWord: boolean }

// One step inside quotes, at `line[i]`; returns how many characters it read.
const readQuoted = (split: Splitter, line: string, i: number): number => {
  const char = line[i] ?? ''
  if (char === split.quote) {
    split.quote = null
    return 1
  }
  if (char === '\\' && split.quote === '"' && i + 1 < line.length) {
    split.word += line[i + 1] ?? ''
    return 2
  }
  split.word += char
  return 1
}

// One step outside quotes, at `line[i]`; returns how many characters it read.
const readPlain = (split: Splitter, line: string, i: number): number => {
  const char = line[i] ?? ''
  if (char === '"' || char === "'") {
    split.quote = char
    split.hasWord = true
    return 1
  }
  if (char === '\\' && i + 1 < line.length) {
    split.word += line[i + 1] ?? ''
    split.hasWord = true
    return 2
  }
  if (WHITESPACE.test(char)) {
    if (split.hasWord) {
      split.words.push(split.word)
    }
    split.word = ''
    split.hasWord = false
    return 1
  }
  split.word += char
  split.hasWord = true
  return 1
}

/** Splits a command line into words, honoring quotes and backslashes, without a shell. */
export const splitWords = (line: string): string[] => {
  const split: Splitter = { words: [], word: '', quote: null, hasWord: false }
  let i = 0
  while (i < line.length) {
    i += split.quote === null ? readPlain(split, line, i) : readQuoted(split, line, i)
  }
  if (split.hasWord) {
    split.words.push(split.word)
  }
  return split.words
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

// The git subcommand after git's own options, as an operation when it is one the footer shows.
const gitSubcommandOf = (args: readonly string[]): GitOp | null => {
  for (let i = 0; i < args.length; i += 1) {
    const word = args[i] ?? ''
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

// A `gh <noun> <verb>` the footer shows.
const ghCommandOf = (args: readonly string[]): GitOp | null => {
  const [noun, verb] = args
  if (noun !== undefined && GH_NOUNS.has(noun) && verb !== undefined && !verb.startsWith('-')) {
    return { tool: 'gh', name: `${noun} ${verb}` }
  }
  return null
}

const gitOpOf = (words: readonly string[]): GitOp | null => {
  const [tool, ...rest] = words
  if (tool === 'git') {
    return gitSubcommandOf(rest)
  }
  if (tool === 'gh') {
    return ghCommandOf(rest)
  }
  return null
}

// Redirections write their target whatever the command is.
const redirectTargets = (segment: string): string[] => {
  const targets: string[] = []
  const redirect = /(?:^|[^<>&\d])>>?\s*("[^"]+"|'[^']+'|[^\s;&|]+)/g
  for (const match of segment.matchAll(redirect)) {
    const target = splitWords(match[1] ?? '')[0]
    if (target !== undefined && target !== '/dev/null' && !target.startsWith('&')) {
      targets.push(target)
    }
  }
  return targets
}

// A segment's words without its redirections and the prefixes and variable assignments before
// the command's name.
const commandWords = (segment: string): string[] => {
  const words = splitWords(segment.replace(/\d*>>?\s*("[^"]+"|'[^']+'|[^\s;&|]+)/g, ' '))
  while (words.length > 0 && (PREFIXES.has(words[0] ?? '') || ASSIGNMENT.test(words[0] ?? ''))) {
    words.shift()
  }
  return words
}

// Adds the files a reading or writing command names to `touches`.
const addOperands = (name: string, args: readonly string[], touches: Touches): void => {
  const operands = args.filter((arg) => !arg.startsWith('-'))
  const isInPlace = name === 'sed' && args.some((arg) => arg === '-i' || arg.startsWith('-i'))
  if (WRITERS.has(name) || isInPlace) {
    touches.writes.push(...(isInPlace ? operands.slice(1) : operands))
  } else if (READERS.has(name)) {
    touches.reads.push(...operands)
  } else if (PATTERN_FIRST.has(name)) {
    touches.reads.push(...operands.slice(1))
  }
}

/** The files a shell command reads and writes, and the git or gh operations it runs. */
export const parseCommand = (command: string): Touches => {
  const touches: Touches = { reads: [], writes: [], ops: [] }
  for (const segment of command.split(COMMAND_SEPARATOR)) {
    touches.writes.push(...redirectTargets(segment))
    const words = commandWords(segment)
    const [name, ...args] = words
    if (name === undefined) {
      continue
    }
    const op = gitOpOf(words)
    if (op === null) {
      addOperands(name, args, touches)
    } else {
      touches.ops.push(op)
    }
  }
  return touches
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
