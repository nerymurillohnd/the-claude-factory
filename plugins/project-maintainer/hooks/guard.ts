// What the hooks decide, as pure functions over plain data. The hooks in register.ts read the
// files and call these; no call on `$` lives here.

import { adrAuthority, validateAdr } from './adr.ts'
import { closedAuthority, pendingAuthority, validateLedger } from './debt.ts'
import { classify, type RecordRef, resolvePath } from './paths.ts'

/** An absolute path, POSIX or with a Windows drive, with either slash. */
const ABSOLUTE_PATH = /^([A-Za-z]:)?[\\/]/
/** The records folder named in a shell word, with or without a trailing slash. */
const RECORDS_FOLDER = /\.claude\/maintainer(?![\w-])/i
const WHITESPACE = /\s+/
/** A word that starts a redirect, such as `>`, `>>` or `2>file`. */
const REDIRECT = /^\d*>>?/
/** A redirect whose target is the next word. */
const BARE_REDIRECT = /^\d*>>?$/
/** The in-place flag of sed or perl, alone or among other short flags. */
const IN_PLACE_FLAG = /^-\w*i|^--in-place/

/** The arguments of a Write or Edit call, narrowed from the unknown input of `tool.check`. */
export type FileInput = {
  path: string
  content?: string
  oldString?: string
  newString?: string
  replaceAll?: boolean
}

export function fileInput(value: unknown): FileInput | null {
  if (typeof value !== 'object' || value === null) {
    return null
  }
  const text = (key: string): string | undefined => {
    const found: unknown = Reflect.get(value, key)
    return typeof found === 'string' ? found : undefined
  }
  const path = text('file_path')
  if (path === undefined) {
    return null
  }
  const input: FileInput = { path }
  const content = text('content')
  const oldString = text('old_string')
  const newString = text('new_string')
  if (content !== undefined) {
    input.content = content
  }
  if (oldString !== undefined) {
    input.oldString = oldString
  }
  if (newString !== undefined) {
    input.newString = newString
  }
  if (Reflect.get(value, 'replace_all') === true) {
    input.replaceAll = true
  }
  return input
}

/**
 * Whether a Write or Edit call may save a record, judged with no call on `$` so it can run when
 * the check itself broke. Without the session's directory a relative path could land anywhere,
 * so it counts as a record, as does a call it cannot read: when in doubt, the guard holds.
 */
export function mayWriteRecord(value: unknown): boolean {
  try {
    const input = fileInput(value)
    if (input === null) {
      return false
    }
    const absolute = ABSOLUTE_PATH.test(input.path)
    return !absolute || classify(resolvePath(input.path, '/')) !== null
  } catch {
    return true
  }
}

/**
 * The file as the call would leave it: Write replaces the content, Edit swaps one piece of
 * the current text. Null when the call cannot apply, which the tool reports by itself.
 */
export function resultingText(input: FileInput, current: string | null): string | null {
  if (input.content !== undefined) {
    return input.content
  }
  const { oldString, newString } = input
  if (
    current === null ||
    oldString === undefined ||
    newString === undefined ||
    !current.includes(oldString)
  ) {
    return null
  }
  return input.replaceAll === true
    ? current.replaceAll(oldString, () => newString)
    : current.replace(oldString, () => newString)
}

/** What the hooks know about the files around a record. */
export type Surroundings = {
  /** The text of the other debt ledger, or null when it does not exist. */
  otherLedger: string | null
  /** The IDs of the ADRs in the decisions folder. */
  adrIds: ReadonlySet<string>
}

/** Rules nobody can skip: a record that breaks them is malformed. */
export function formatProblems(
  ref: RecordRef,
  current: string | null,
  resulting: string,
  around: Surroundings,
): string[] {
  if (ref.kind === 'adr') {
    return validateAdr(resulting, { name: ref.name, exists: current !== null, ids: around.adrIds })
  }
  return validateLedger(ref.kind, current, resulting, around.otherLedger)
}

/** Rules the owner may waive: a settled record changes only through a new record. */
export function authorityReasons(
  ref: RecordRef,
  current: string | null,
  resulting: string,
  around: Surroundings,
): string[] {
  if (current === null) {
    return []
  }
  if (ref.kind === 'adr') {
    return adrAuthority(current, resulting)
  }
  if (ref.kind === 'closed-debt') {
    return closedAuthority(current, resulting)
  }
  return pendingAuthority(current, resulting, around.otherLedger, around.adrIds)
}

export function refusal(file: string, problems: readonly string[]): string {
  return [
    `Project Maintainer refused to save ${file}. Fix these and write it again:`,
    ...problems.map((problem) => `- ${problem}`),
  ].join('\n')
}

export function askReason(file: string, reasons: readonly string[]): string {
  return [
    `Project Maintainer: this edit to ${file} breaks a rule of the records.`,
    ...reasons.map((reason) => `- ${reason}`),
    'A settled record is not rewritten. Write a new ADR that supersedes it, or open a new debt item that links back. Approve only if you asked for this edit. Where nobody can approve, write the new record instead.',
  ].join('\n')
}

/** Whether a piece of a shell command names the records folder, with or without a trailing slash. */
const mentionsRecords = (piece: string): boolean => RECORDS_FOLDER.test(piece)

const unquote = (token: string): string => token.replace(/^['"]|['"]$/g, '')
const SEGMENTS = /&&|\|\||[;|\n]/
const REMOVES_OR_MOVES = new Set(['rm', 'mv', 'unlink', 'shred', 'truncate'])
const WRITES_LAST_ARGUMENT = new Set(['cp', 'install', 'ln'])

/** One piece of a shell command, split into words, with `git` folded into its subcommand. */
type Segment = {
  tokens: string[]
  verb: string
  args: string[]
}

function parseSegment(segment: string): Segment {
  const tokens = segment
    .trim()
    .split(WHITESPACE)
    .map(unquote)
    .filter((token) => token !== '')
  const [first = '', ...rest] = tokens
  return first === 'git'
    ? { tokens, verb: rest[0] ?? '', args: rest.slice(1) }
    : { tokens, verb: first, args: rest }
}

/** Whether a redirect in the segment points into the records folder. */
function redirectsIntoRecords(tokens: readonly string[]): boolean {
  return tokens.some(
    (token, index) =>
      REDIRECT.test(token) &&
      (mentionsRecords(token) ||
        (BARE_REDIRECT.test(token) && mentionsRecords(tokens[index + 1] ?? ''))),
  )
}

/** Whether the verb of the segment writes, moves or deletes a file it names in the records. */
function verbWritesRecords(
  { verb, args }: Segment,
  names: boolean,
  insideRecords: boolean,
): boolean {
  const inPlace = (verb === 'sed' || verb === 'perl') && args.some((arg) => IN_PLACE_FLAG.test(arg))
  return (
    (REMOVES_OR_MOVES.has(verb) && names) ||
    (WRITES_LAST_ARGUMENT.has(verb) && (mentionsRecords(args.at(-1) ?? '') || insideRecords)) ||
    (verb === 'tee' && names) ||
    (verb === 'dd' &&
      args.some((arg) => arg.startsWith('of=') && (mentionsRecords(arg) || insideRecords))) ||
    (inPlace && names)
  )
}

/** Whether one segment changes files in the records folder, given whether an earlier `cd` entered it. */
function segmentChangesRecords(segment: Segment, insideRecords: boolean): boolean {
  const names = segment.args.some(mentionsRecords) || insideRecords
  return (
    redirectsIntoRecords(segment.tokens) ||
    (insideRecords && segment.tokens.some((token) => REDIRECT.test(token))) ||
    verbWritesRecords(segment, names, insideRecords)
  )
}

/**
 * Whether a shell command rewrites, moves or deletes the records folders, or writes into them.
 * Reading, and copying out of the folder, stay quiet. Best effort: a shell has too many spellings.
 */
export function bashReason(command: string): string | null {
  let insideRecords = false
  for (const piece of command.split(SEGMENTS)) {
    const segment = parseSegment(piece)
    if (segment.verb === 'cd') {
      insideRecords = insideRecords || segment.args.some(mentionsRecords)
      continue
    }
    if (segmentChangesRecords(segment, insideRecords)) {
      return 'The command changes files in .claude/maintainer/. Records are written with the Write and Edit tools, which apply the rules of the records, and not through the shell.'
    }
  }
  return null
}

/** Appended to the instructions of a compaction so the summary keeps what the records need. */
export const KEEP_IN_SUMMARY =
  'Keep verbatim: every decision made and the reason for it, every correction the user gave, every open item, and every ADR_ and DEBT- ID mentioned, so the project records can be reconciled after the compaction.'

export function withKeepNote(instructions: string | undefined): string {
  return instructions === undefined || instructions.trim() === ''
    ? KEEP_IN_SUMMARY
    : `${instructions}\n\n${KEEP_IN_SUMMARY}`
}

const SIGNAL_FILES: readonly (readonly [RegExp, string])[] = [
  [
    /(^|\/)(package\.json|pyproject\.toml|requirements[\w.-]*\.txt|Pipfile|go\.mod|Cargo\.toml|Gemfile|composer\.json|pom\.xml|build\.gradle(\.kts)?)$/,
    'a dependency manifest',
  ],
  [/(^|\/)(Dockerfile[\w.-]*|docker-compose[\w.-]*\.ya?ml)$|\.tf$/, 'infrastructure files'],
  [/(^|\/)migrations?\/|\.sql$|(^|\/)schema\.[\w]+$/, 'a database schema or migration'],
  [/^\.github\/workflows\//, 'a CI workflow'],
]
const SIGNAL_WORDS =
  /\b(workaround|work-around|temporary|temporarily|hack|hacky|revert(ed)?|todo|fixme|deprecat\w*|drop(ped)? support|migrat\w*)\b/i

/** Why a commit may deserve a record. The first line is the subject; the rest are the files it touched. */
export function commitSignals(shown: string): string[] {
  const [subject = '', ...rest] = shown.split('\n')
  const files = rest.map((line) => line.trim()).filter((line) => line !== '')
  if (files.length === 0 || files.every((file) => file.startsWith('.claude/maintainer/'))) {
    return []
  }
  const signals = new Set<string>()
  for (const file of files) {
    for (const [pattern, label] of SIGNAL_FILES) {
      if (pattern.test(file)) {
        signals.add(label)
      }
    }
  }
  const word = SIGNAL_WORDS.exec(subject)
  if (word !== null) {
    signals.add(`the word "${word[0]}" in its message`)
  }
  return [...signals]
}

export function nudgeText(signals: readonly string[]): string {
  return `Project Maintainer: the commit just made shows ${signals.join(' and ')}. If it settles a decision or leaves a problem that cannot be fixed now, record it with the write-records skill. If not, ignore this note.`
}
