// What the hooks decide, as pure functions over plain data. The hooks in register.ts read the
// files and call these; no call on `$` lives here.

import { adrAuthority, validateAdr } from './adr.ts'
import { closedAuthority, pendingAuthority, validateLedger } from './debt.ts'
import type { RecordRef } from './paths.ts'

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

/** Shell commands that rewrite, move or delete the records folders, or write into them. Best effort. */
const RECORD_FOLDERS = /\.claude\/maintainer\//
const CHANGES_FILES =
  /(^|[\s;&|(])(rm|mv|cp|truncate|tee|dd|install|ln)\s|\bsed\s+(-\w*i|--in-place)|\bperl\s+-\w*i|>>?\s*\S*\.claude\/maintainer\//

export function bashReason(command: string): string | null {
  if (!RECORD_FOLDERS.test(command) || !CHANGES_FILES.test(command)) {
    return null
  }
  return 'The command changes a file in .claude/maintainer/. Records are written with the Write tool, which applies the rules of the records, and not through the shell.'
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
