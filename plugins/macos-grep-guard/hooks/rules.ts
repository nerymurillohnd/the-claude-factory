// Pure rules for macos-grep-guard: shell-aware parsing of a Bash command,
// the recursive-grep and awk IGNORECASE checks, and the BSD error hints.
// No `$` calls here, so every function is unit-tested directly.

/** One shell word, with what the guard needs to know about how it was written. */
export type Word = {
  text: string
  /** Contains an unquoted or double-quoted `$` expansion, `$(...)` or backticks. */
  isDynamic: boolean
  /** Contains an unquoted glob character (`*`, `?`, `[`). */
  isGlob: boolean
  /** Starts with an unquoted `~`. */
  isTilde: boolean
}

type Item =
  | { kind: 'segment'; words: Word[] }
  | { kind: 'open' }
  | { kind: 'close' }
  | { kind: 'substitution'; items: Item[] }

type Heredoc = { delimiter: string; isTabStripped: boolean }

const SEPARATORS = new Set([';', '|', '&', '\n', '(', ')'])
const LEADING_TABS = /^\t+/
const WORD_DELIMITER = /[\s;&|()<>]/
const REDIRECT_END = /[<>]$/
const SHELL_COMMAND_FLAG = /^-[a-zA-Z]*c[a-zA-Z]*$/
const GLOB_CHARS = new Set(['*', '?', '['])
const DELIMITER_QUOTES = new Set(["'", '"', '\\'])

/** The scan state of a `$( ... )` while its closing parenthesis is searched. */
type ParenScan = { depth: number; quote: string }

/** Splits a command into segments, honouring quotes, `$(...)`, backticks, subshells and heredocs. */
class Tokenizer {
  private readonly command: string
  private readonly items: Item[] = []
  private readonly heredocs: Heredoc[] = []
  private words: Word[] = []
  private text = ''
  private started = false
  private isDynamic = false
  private isGlob = false
  private isTilde = false

  constructor(command: string) {
    this.command = command
  }

  run(): Item[] {
    for (let i = 0; i < this.command.length; i += 1) {
      i = this.step(i)
    }
    this.endSegment()
    return this.items
  }

  private endWord(): void {
    if (this.started) {
      this.words.push({
        text: this.text,
        isDynamic: this.isDynamic,
        isGlob: this.isGlob,
        isTilde: this.isTilde,
      })
    }
    this.text = ''
    this.started = false
    this.isDynamic = false
    this.isGlob = false
    this.isTilde = false
  }

  private endSegment(): void {
    this.endWord()
    if (this.words.length > 0) {
      this.items.push({ kind: 'segment', words: this.words })
    }
    this.words = []
  }

  /** Reads a balanced `$( ... )` starting after the `$(`; returns the inner text and the index after `)`. */
  private readParen(from: number): [string, number] {
    const scan: ParenScan = { depth: 1, quote: '' }
    for (let i = from; i < this.command.length; i += 1) {
      const c = this.command[i] ?? ''
      i = scan.quote === '' ? this.parenOutsideQuote(scan, c, i) : this.parenInQuote(scan, c, i)
      if (scan.depth === 0) {
        return [this.command.slice(from, i), i + 1]
      }
    }
    return [this.command.slice(from), this.command.length]
  }

  private parenInQuote(scan: ParenScan, c: string, i: number): number {
    if (c === '\\' && scan.quote === '"') {
      return i + 1
    }
    if (c === scan.quote) {
      scan.quote = ''
    }
    return i
  }

  private parenOutsideQuote(scan: ParenScan, c: string, i: number): number {
    if (c === '\\') {
      return i + 1
    }
    if (c === "'" || c === '"') {
      scan.quote = c
    } else if (c === '(') {
      scan.depth += 1
    } else if (c === ')') {
      scan.depth -= 1
    }
    return i
  }

  /** Reads a backtick substitution starting after the opening backtick. */
  private readBacktick(from: number): [string, number] {
    let i = from
    for (; i < this.command.length; i += 1) {
      if (this.command[i] === '\\') {
        i += 1
      } else if (this.command[i] === '`') {
        return [this.command.slice(from, i), i + 1]
      }
    }
    return [this.command.slice(from), i]
  }

  private substitute(inner: string): void {
    this.items.push({ kind: 'substitution', items: tokenize(inner) })
    this.started = true
    this.isDynamic = true
  }

  /** Substitutes the `$(...)` that starts at `i`; returns the index of its last character. */
  private parenSubstitution(i: number): number {
    const [inner, after] = this.readParen(i + 2)
    this.substitute(inner)
    return after - 1
  }

  /** Substitutes the backtick pair that opens at `i`; returns the index of its last character. */
  private backtickSubstitution(i: number): number {
    const [inner, after] = this.readBacktick(i + 1)
    this.substitute(inner)
    return after - 1
  }

  /** Skips heredoc bodies that start at the line after index `i` (a newline). */
  private skipHeredocs(i: number): number {
    let at = i + 1
    for (let doc = this.heredocs.shift(); doc !== undefined; doc = this.heredocs.shift()) {
      at = this.skipHeredocBody(doc, at)
    }
    return at - 1
  }

  /** Returns the index after the line that ends one heredoc body that starts at `from`. */
  private skipHeredocBody(doc: Heredoc, from: number): number {
    let at = from
    for (;;) {
      const end = this.command.indexOf('\n', at)
      const line = this.command.slice(at, end === -1 ? this.command.length : end)
      at = end === -1 ? this.command.length : end + 1
      const body = doc.isTabStripped ? line.replace(LEADING_TABS, '') : line
      if (body === doc.delimiter || end === -1) {
        return at
      }
    }
  }

  /** Handles one character at `i`; returns the index of the last character it consumed. */
  private step(i: number): number {
    const c = this.command[i] ?? ''
    const next = this.command[i + 1] ?? ''
    return this.stepQuoting(c, next, i) ?? this.stepSyntax(c, next, i)
  }

  /** Quotes, escapes, substitutions and comments; `null` when `c` is none of them. */
  private stepQuoting(c: string, next: string, i: number): number | null {
    if (c === "'") {
      return this.singleQuoted(i)
    }
    if (c === '"') {
      return this.doubleQuoted(i)
    }
    if (c === '\\') {
      return this.backslash(next, i)
    }
    if (c === '$' && next === '(') {
      return this.parenSubstitution(i)
    }
    if (c === '`') {
      return this.backtickSubstitution(i)
    }
    if (c === '#' && !this.started) {
      return this.comment(i)
    }
    return null
  }

  /** Heredocs, redirections, separators, blanks and ordinary characters. */
  private stepSyntax(c: string, next: string, i: number): number {
    if (c === '<' && next === '<' && this.command[i + 2] !== '<') {
      return this.heredocStart(i)
    }
    if (c === '&' && (REDIRECT_END.test(this.text) || next === '>')) {
      this.text += c
      this.started = true
    } else if (SEPARATORS.has(c)) {
      return this.separator(c, i)
    } else if (c === ' ' || c === '\t') {
      this.endWord()
    } else {
      this.plainChar(c)
    }
    return i
  }

  private singleQuoted(i: number): number {
    const end = this.command.indexOf("'", i + 1)
    this.text += this.command.slice(i + 1, end === -1 ? this.command.length : end)
    this.started = true
    return end === -1 ? this.command.length : end
  }

  private doubleQuoted(i: number): number {
    this.started = true
    let j = i + 1
    while (j < this.command.length && this.command[j] !== '"') {
      j = this.doubleQuotedChar(j) + 1
    }
    return j
  }

  /** Handles one character inside double quotes; returns the index of the last character it consumed. */
  private doubleQuotedChar(j: number): number {
    const d = this.command[j] ?? ''
    if (d === '\\') {
      this.text += this.command[j + 1] ?? ''
      return j + 1
    }
    if (d === '$' && this.command[j + 1] === '(') {
      return this.parenSubstitution(j)
    }
    if (d === '`') {
      return this.backtickSubstitution(j)
    }
    if (d === '$') {
      this.isDynamic = true
    }
    this.text += d
    return j
  }

  private backslash(next: string, i: number): number {
    if (next !== '\n') {
      this.text += next
      this.started = true
    }
    return i + 1
  }

  private comment(i: number): number {
    const end = this.command.indexOf('\n', i)
    return (end === -1 ? this.command.length : end) - 1
  }

  /** Reads the delimiter word of a heredoc from `from`; returns it and the index after it. */
  private readDelimiter(from: number): [string, number] {
    let j = from
    let delimiter = ''
    for (; j < this.command.length && !WORD_DELIMITER.test(this.command[j] ?? ''); j += 1) {
      const d = this.command[j] ?? ''
      if (!DELIMITER_QUOTES.has(d)) {
        delimiter += d
      }
    }
    return [delimiter, j]
  }

  private heredocStart(i: number): number {
    this.endWord()
    let j = i + 2
    const isTabStripped = this.command[j] === '-'
    if (isTabStripped) {
      j += 1
    }
    while (this.command[j] === ' ' || this.command[j] === '\t') {
      j += 1
    }
    const [delimiter, after] = this.readDelimiter(j)
    this.heredocs.push({ delimiter, isTabStripped })
    return after - 1
  }

  private separator(c: string, i: number): number {
    this.endSegment()
    if (c === '(') {
      this.items.push({ kind: 'open' })
    } else if (c === ')') {
      this.items.push({ kind: 'close' })
    } else if (c === '\n' && this.heredocs.length > 0) {
      return this.skipHeredocs(i)
    }
    return i
  }

  private plainChar(c: string): void {
    if (c === '$') {
      this.isDynamic = true
    } else if (GLOB_CHARS.has(c)) {
      this.isGlob = true
    } else if (c === '~' && !this.started) {
      this.isTilde = true
    }
    this.text += c
    this.started = true
  }
}

function tokenize(command: string): Item[] {
  return new Tokenizer(command).run()
}

/** How a segment's command reaches its program in Claude's shell. */
export type Route = 'wrapper' | 'bsd'

type Resolved = { name: string; args: Word[]; route: Route }

/** A command prefix that hands the program after it to BSD tools, and the options it takes. */
type Prefix = { takesOptions: boolean; valueOptions: ReadonlySet<string> }

const ASSIGNMENT = /^[A-Za-z_][A-Za-z0-9_]*=/
const SHELLS = new Set(['sh', 'bash', 'zsh', 'dash', 'ksh'])
const NO_VALUES: ReadonlySet<string> = new Set()
const SUDO_VALUE = new Set(['-u', '-g', '-C', '-D', '-h', '-p', '-r', '-t', '-T', '-U'])
const XARGS_VALUE = new Set(['-I', '-J', '-L', '-n', '-P', '-s', '-E', '-R', '-S'])
const ROUTING_PREFIXES = new Map<string, Prefix>([
  ['command', { takesOptions: true, valueOptions: NO_VALUES }],
  ['env', { takesOptions: true, valueOptions: new Set(['-u', '-P', '-S']) }],
  ['sudo', { takesOptions: true, valueOptions: SUDO_VALUE }],
  ['exec', { takesOptions: true, valueOptions: new Set(['-a']) }],
  ['nohup', { takesOptions: false, valueOptions: NO_VALUES }],
  ['nice', { takesOptions: true, valueOptions: new Set(['-n']) }],
])

/** Index of the first word at or after `from` that is not a `NAME=value` assignment. */
function skipAssignments(words: Word[], from: number): number {
  let at = from
  while (at < words.length && ASSIGNMENT.test(words[at]?.text ?? '')) {
    at += 1
  }
  return at
}

/** Index of the first word at or after `from` that is neither an assignment nor `time [-p]` or `!`. */
function skipLeading(words: Word[], from: number): number {
  let at = skipAssignments(words, from)
  while (words[at]?.text === 'time' || words[at]?.text === '!') {
    at = skipAssignments(words, at + (words[at + 1]?.text === '-p' ? 2 : 1))
  }
  return at
}

/** Index of the first word at or after `from` that is not an option, skipping the value of the ones that take one. */
function skipOptions(words: Word[], from: number, valueOptions: ReadonlySet<string>): number {
  let at = from
  while (at < words.length && (words[at]?.text ?? '').startsWith('-')) {
    at += valueOptions.has(words[at]?.text ?? '') ? 2 : 1
  }
  return at
}

/** The program a segment runs, named by its last path segment; a path bypasses Claude's shell functions. */
function programOf(word: string, args: Word[], route: Route): Resolved {
  const isPath = word.includes('/')
  return {
    name: isPath ? (word.split('/').pop() ?? word) : word,
    args,
    route: isPath ? 'bsd' : route,
  }
}

/** Index after a routing prefix and its options, or `null` when the prefix only looks a program up (`command -v`). */
function skipPrefix(words: Word[], at: number, prefix: Prefix): number | null {
  if (words[at]?.text === 'command' && ['-v', '-V'].includes(words[at + 1]?.text ?? '')) {
    return null
  }
  return prefix.takesOptions ? skipOptions(words, at + 1, prefix.valueOptions) : at + 1
}

/** Finds the program a segment runs and whether it bypasses Claude's shell functions. */
function resolve(words: Word[]): Resolved | null {
  let i = 0
  let route: Route = 'wrapper'
  for (;;) {
    i = skipLeading(words, i)
    const word = words[i]?.text
    if (word === undefined || word === 'builtin') {
      return null
    }
    const prefix = ROUTING_PREFIXES.get(word)
    if (prefix !== undefined) {
      const after = skipPrefix(words, i, prefix)
      if (after === null) {
        return null
      }
      i = after
      route = 'bsd'
    } else {
      return programOf(word, words.slice(i + 1), route)
    }
  }
}

/** Glob patterns from Claude Code's `grep` function that hand the call to BSD grep (`declare -f grep`, 2.1.296). */
const WRAPPER_BYPASS = [
  /^-.*-filter/,
  /^-.*-pager/,
  /^-.*-view/,
  /^-.*-format-open/,
  /^-.*-config/,
  /^---/,
  /^-@/,
  /^-.*-save-config/,
  /^-[Zz]/,
  /^-[^-].*[Zz]/,
  /^--null$/,
  /^--null-data$/,
]

const SHORT_WITH_VALUE = new Set([
  'e',
  'f',
  'g',
  'm',
  'A',
  'B',
  'C',
  'D',
  'd',
  'M',
  'N',
  'O',
  't',
  'K',
])
const LONG_WITH_VALUE = new Set([
  '--regexp',
  '--file',
  '--after-context',
  '--before-context',
  '--context',
  '--max-count',
  '--include',
  '--exclude',
  '--include-dir',
  '--exclude-dir',
  '--glob',
  '--file-type',
  '--directories',
  '--devices',
])
const RECURSIVE_LONG = new Set(['--recursive', '--dereference-recursive'])
const IGNORE_CHOICE_LONG = new Set(['--no-ignore-files', '--ignore-files'])
const BINARY_CHOICE_LONG = new Set([
  '--binary-files',
  '--text',
  '--with-hex',
  '--ignore-binary',
  '--no-ignore-binary',
])
const PATTERN_LONG = new Set(['--regexp', '--file'])
const BINARY_CHOICE_SHORT = new Set(['a', 'W', 'I'])
const PATTERN_SHORT = new Set(['e', 'f'])

/** What the guard found about one recursive grep that reaches Claude's ugrep wrapper. */
export type GrepFinding = {
  /** Absolute search roots, or `null` when one of them cannot be placed with certainty. */
  roots: string[] | null
  /** The command states neither `--no-ignore-files` nor `--ignore-files`. */
  lacksIgnoreChoice: boolean
  /** The command states no binary choice. */
  lacksBinaryChoice: boolean
}

/** What a grep's options say: whether it is recursive and which choices it states. */
type GrepScan = {
  isRecursive: boolean
  isBypass: boolean
  hasIgnoreChoice: boolean
  hasBinaryChoice: boolean
  hasPatternOption: boolean
}

/** Notes what a long option (`--name` or `--name=value`) says; returns the index of the last word it consumed. */
function readLongOption(scan: GrepScan, args: Word[], i: number): number {
  const [name = '', value] = (args[i]?.text ?? '').split('=', 2)
  if (RECURSIVE_LONG.has(name) || (name === '--directories' && value === 'recurse')) {
    scan.isRecursive = true
  } else if (IGNORE_CHOICE_LONG.has(name)) {
    scan.hasIgnoreChoice = true
  } else if (BINARY_CHOICE_LONG.has(name)) {
    scan.hasBinaryChoice = true
  } else if (PATTERN_LONG.has(name)) {
    scan.hasPatternOption = true
  }
  if (value !== undefined || !LONG_WITH_VALUE.has(name)) {
    return i
  }
  if (name === '--directories' && args[i + 1]?.text === 'recurse') {
    scan.isRecursive = true
  }
  return i + 1
}

/** Notes what the value-taking short option `letter` says; returns the index of the last word it consumed. */
function readShortValue(
  scan: GrepScan,
  args: Word[],
  i: number,
  letter: string,
  attached: string,
): number {
  if (PATTERN_SHORT.has(letter)) {
    scan.hasPatternOption = true
  }
  const isRecurseValue =
    attached === 'recurse' || (attached === '' && args[i + 1]?.text === 'recurse')
  if (letter === 'd' && isRecurseValue) {
    scan.isRecursive = true
  }
  return attached === '' ? i + 1 : i
}

/** Notes what a cluster of short options (`-rn`, `-A 3`) says; returns the index of the last word it consumed. */
function readShortOptions(scan: GrepScan, args: Word[], i: number): number {
  const arg = args[i]?.text ?? ''
  for (let k = 1; k < arg.length; k += 1) {
    const letter = arg[k] ?? ''
    if (letter === 'r' || letter === 'R') {
      scan.isRecursive = true
    } else if (BINARY_CHOICE_SHORT.has(letter)) {
      scan.hasBinaryChoice = true
    }
    if (SHORT_WITH_VALUE.has(letter)) {
      return readShortValue(scan, args, i, letter, arg.slice(k + 1))
    }
  }
  return i
}

/** Reads a grep's arguments: whether it is recursive, which choices it states, and its search paths. */
function readGrep(args: Word[]): GrepScan & { paths: Word[] } {
  const scan: GrepScan = {
    isRecursive: false,
    isBypass: false,
    hasIgnoreChoice: false,
    hasBinaryChoice: false,
    hasPatternOption: false,
  }
  const positionals: Word[] = []
  let isAfterDashes = false
  for (let i = 0; i < args.length; i += 1) {
    const word = args[i]
    const arg = word?.text ?? '-'
    if (word === undefined || isAfterDashes || !arg.startsWith('-') || arg === '-') {
      if (word !== undefined) {
        positionals.push(word)
      }
    } else if (arg === '--') {
      isAfterDashes = true
    } else {
      scan.isBypass ||= WRAPPER_BYPASS.some((pattern) => pattern.test(arg))
      i = arg.startsWith('--') ? readLongOption(scan, args, i) : readShortOptions(scan, args, i)
    }
  }
  return { ...scan, paths: scan.hasPatternOption ? positionals : positionals.slice(1) }
}

/** Joins and normalises a POSIX path. */
export function joinPath(base: string, path: string): string {
  const parts = (path.startsWith('/') ? path : `${base}/${path}`).split('/')
  const out: string[] = []
  for (const part of parts) {
    if (part === '' || part === '.') {
      continue
    }
    if (part === '..') {
      out.pop()
    } else {
      out.push(part)
    }
  }
  return `/${out.join('/')}`
}

/** A folder a `cd` argument moves to, or `null` when it cannot be placed with certainty. */
function moveDir(dir: string | null, arg: Word | undefined): string | null {
  if (
    arg === undefined ||
    arg.isDynamic ||
    arg.isGlob ||
    arg.isTilde ||
    arg.text === '-' ||
    arg.text === ''
  ) {
    return null
  }
  if (arg.text.startsWith('/')) {
    return joinPath('/', arg.text)
  }
  return dir === null ? null : joinPath(dir, arg.text)
}

/** Everything the guard needs from one Bash command. */
export type Analysis = {
  greps: GrepFinding[]
  /** An `awk` program in the command mentions `IGNORECASE`. */
  usesAwkIgnoreCase: boolean
  /** Every program name the command runs, for matching error hints. */
  programs: Set<string>
}

const CURRENT_DIR: Word = { text: '.', isDynamic: false, isGlob: false, isTilde: false }

/** Analyses a Bash command. `cwd` is the folder it starts in, or `null` when unknown. */
export function analyze(command: string, cwd: string | null): Analysis {
  const analysis: Analysis = { greps: [], usesAwkIgnoreCase: false, programs: new Set() }
  walk(tokenize(command), cwd, 'wrapper', analysis)
  return analysis
}

function walk(items: Item[], start: string | null, forced: Route, analysis: Analysis): void {
  let dir = start
  const scopes: (string | null)[] = []
  for (const item of items) {
    if (item.kind === 'open') {
      scopes.push(dir)
    } else if (item.kind === 'close') {
      dir = scopes.length > 0 ? (scopes.pop() ?? null) : dir
    } else if (item.kind === 'substitution') {
      walk(item.items, dir, forced, analysis)
    } else {
      dir = visit(item.words, dir, forced, analysis)
    }
  }
}

/** Whether a search path can be turned into an absolute folder with certainty. */
function isPlaceable(word: Word, dir: string | null): boolean {
  return (
    !word.isDynamic && !word.isGlob && !word.isTilde && (word.text.startsWith('/') || dir !== null)
  )
}

/** Records a recursive grep that reaches Claude's ugrep wrapper without both explicit choices. */
function recordGrep(args: Word[], dir: string | null, analysis: Analysis): void {
  const grep = readGrep(args)
  if (!grep.isRecursive || grep.isBypass || (grep.hasIgnoreChoice && grep.hasBinaryChoice)) {
    return
  }
  const paths = grep.paths.length > 0 ? grep.paths : [CURRENT_DIR]
  analysis.greps.push({
    roots: paths.every((word) => isPlaceable(word, dir))
      ? paths.map((word) => joinPath(dir ?? '/', word.text))
      : null,
    lacksIgnoreChoice: !grep.hasIgnoreChoice,
    lacksBinaryChoice: !grep.hasBinaryChoice,
  })
}

/** Analyses the script of `sh -c '...'`, which runs outside Claude's shell functions. */
function visitShell(args: Word[], dir: string | null, analysis: Analysis): void {
  const flag = args.findIndex((word) => SHELL_COMMAND_FLAG.test(word.text))
  const script = flag === -1 ? undefined : args[flag + 1]
  if (script !== undefined) {
    walk(tokenize(script.text), dir, 'bsd', analysis)
  }
}

/** Analyses the command `xargs` runs, which also runs outside Claude's shell functions. */
function visitXargs(args: Word[], dir: string | null, analysis: Analysis): void {
  const inner = args.slice(skipOptions(args, 0, XARGS_VALUE))
  if (inner.length > 0) {
    visit(inner, dir, 'bsd', analysis)
  }
}

/** Checks one segment and returns the folder the next segment starts in. */
function visit(
  words: Word[],
  dir: string | null,
  forced: Route,
  analysis: Analysis,
): string | null {
  const resolved = resolve(words)
  if (resolved === null) {
    return dir
  }
  const route: Route = forced === 'bsd' ? 'bsd' : resolved.route
  const { name, args } = resolved
  analysis.programs.add(name)
  if (name === 'cd' || name === 'pushd') {
    return moveDir(
      dir,
      args.find((word) => !word.text.startsWith('-')),
    )
  }
  if (name === 'popd') {
    return null
  }
  if (SHELLS.has(name)) {
    visitShell(args, dir, analysis)
  } else if (name === 'xargs') {
    visitXargs(args, dir, analysis)
  } else if (name === 'awk' && args.some((word) => word.text.includes('IGNORECASE'))) {
    analysis.usesAwkIgnoreCase = true
  } else if (name === 'grep' && route === 'wrapper') {
    recordGrep(args, dir, analysis)
  }
  return dir
}

/** The text Claude reads when a recursive grep is denied. */
export function grepDenial(
  lacksIgnoreChoice: boolean,
  lacksBinaryChoice: boolean,
  reason: string,
): string {
  const complete = [
    lacksIgnoreChoice ? '--no-ignore-files' : '',
    lacksBinaryChoice ? '--binary-files=binary' : '',
  ]
    .filter((flag) => flag !== '')
    .join(' ')
  const omit = [
    lacksIgnoreChoice
      ? '--ignore-files (to skip gitignored files such as node_modules or .venv)'
      : '',
    lacksBinaryChoice ? '-I (to skip binary files)' : '',
  ]
    .filter((flag) => flag !== '')
    .join(' and ')
  return [
    `macos-grep-guard: ${reason}`,
    "On macOS, `grep` in Claude's shell runs ugrep with --ignore-files and -I, so a recursive search silently skips gitignored files and binary files.",
    `For complete results, run the same command with \`${complete}\` appended at the end.`,
    `To skip them on purpose, append ${omit} instead.`,
  ].join('\n')
}

/** What the hook's `.catch` answers when the guard failed before deciding: a denial for a recursive grep, or `null` to let the command run. */
export function fallbackDenial(command: unknown): string | null {
  const grep = typeof command === 'string' ? analyze(command, null).greps[0] : undefined
  if (grep === undefined) {
    return null
  }
  return grepDenial(
    grep.lacksIgnoreChoice,
    grep.lacksBinaryChoice,
    'the guard failed before it could check this recursive grep, so the command was not run.',
  )
}

/** The text Claude reads when an awk program relies on IGNORECASE. */
export const AWK_DENIAL = [
  'macos-grep-guard: macOS awk is BSD awk, which ignores IGNORECASE silently, so the match would be case-sensitive.',
  'Compare in lower case instead, for example `tolower($0) ~ /pattern/`.',
].join('\n')

type Signature = { program: string | null; pattern: RegExp; hint: string }

/** The awk program that replaces `uniq -w N`. */
const UNIQ_PREFIX_AWK = ["awk '{k=substr($0,1,N)}", 'NR==1||k!=p', "{print} {p=k}'"].join(' ')

/** BSD and zsh errors verified on macOS, each with the macOS form to use. */
const SIGNATURES: Signature[] = [
  {
    program: 'uniq',
    pattern: /uniq: invalid option -- w/,
    hint: `macOS uniq is BSD and has no -w/--check-chars. To compare the first N characters of adjacent lines, use ${UNIQ_PREFIX_AWK}.`,
  },
  {
    program: 'stat',
    pattern: /stat: illegal option -- c/,
    hint: "macOS stat is BSD: use -f FORMAT instead of -c, for example stat -f '%z %m %N' FILE (size, modification time in epoch seconds, name).",
  },
  {
    program: 'sed',
    pattern: /sed: illegal option -- -|sed: -I or -i may not be used with stdin/,
    hint: "macOS sed is BSD: it has no long options, and an in-place edit takes an explicit empty suffix: sed -i '' 's/a/b/' FILE.",
  },
  {
    program: 'sed',
    pattern: /sed: \d+: "/,
    hint: "macOS sed is BSD: `-i` takes the next word as the backup suffix, so your script was read as a suffix and the file name as the script. Write sed -i '' 'SCRIPT' FILE.",
  },
  {
    program: 'awk',
    pattern: /awk: calling undefined function (gensub|strftime|systime|asorti?)/,
    hint: 'macOS awk is BSD awk without the gawk functions gensub, strftime, systime and asort. Use perl -ne or perl -pe, which ships with macOS.',
  },
  {
    program: 'awk',
    pattern: /awk: unknown option -i ignored/,
    hint: "macOS awk is BSD awk and has no `-i inplace`. Write to a temporary file and move it: awk 'PROGRAM' FILE > FILE.tmp && mv FILE.tmp FILE.",
  },
  {
    program: 'grep',
    pattern: /grep: invalid option -- P/,
    hint: "This grep ran as BSD grep (a child process such as sh -c or xargs, or `command grep`), which has no -P. Run grep directly in the Bash command, where Claude's grep is ugrep and supports -P, or use perl -ne 'print if /PATTERN/' FILE.",
  },
  {
    program: 'grep',
    pattern: /grep: unrecognized option `/,
    hint: 'This grep ran as BSD grep (a child process such as sh -c or xargs, or `command grep`), which lacks GNU long options. Run grep directly in the Bash command, where it is ugrep, or check /usr/bin/grep --help.',
  },
  {
    program: 'find',
    pattern: /find: -printf: unknown primary or operator/,
    hint: "This find ran as BSD find, which has no -printf. Use -exec stat -f '%N %z' {} + (name and size), with any stat -f format.",
  },
  {
    program: 'timeout',
    pattern: /timeout: command not found|command not found: timeout/,
    hint: "macOS has no timeout command. Use perl, which ships with macOS: perl -e 'alarm N; exec @ARGV' COMMAND ARGS (exit code 142 means it timed out).",
  },
  {
    program: 'gtimeout',
    pattern: /gtimeout: command not found|command not found: gtimeout/,
    hint: "gtimeout is not installed. Use perl, which ships with macOS: perl -e 'alarm N; exec @ARGV' COMMAND ARGS (exit code 142 means it timed out).",
  },
  {
    program: null,
    pattern: /zsh:\d+: no matches found:/,
    hint: "zsh treats a glob that matches nothing as an error. Add zsh's (N) qualifier so it expands to nothing, for example print -l -- *.log(N), or quote the pattern when a program should receive it.",
  },
]

/** The hints for BSD or zsh errors in `output`, limited to programs the command actually ran. */
export function hintsFor(programs: ReadonlySet<string>, output: string): string[] {
  const hints: string[] = []
  for (const signature of SIGNATURES) {
    if (
      (signature.program === null || programs.has(signature.program)) &&
      signature.pattern.test(output) &&
      !hints.includes(signature.hint)
    ) {
      hints.push(signature.hint)
    }
  }
  return hints.map((hint) => `macos-grep-guard: ${hint}`)
}
