// Debt ledger rules, as pure functions over plain text. No call on `$` lives here.

import { ADR_ID, DEBT_ID, DEBT_STATUSES, normalize, OUTCOMES } from './paths.ts'

/** The heading that opens an entry, such as `### DEBT-007`. */
const ENTRY_HEADING = /^### (DEBT-\w+)/
/** A heading of level 1 to 3, which closes the open entry or section. */
const SECTION_HEADING = /^#{1,3} /
/** The heading of the ledger's Index section. */
const INDEX_HEADING = /^## .*Index/
/** The separator row under a Markdown table header. */
const TABLE_RULE = /^\|\s*-/
/** A date written YYYY-MM-DD. */
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/
/** The "Superseded by" line of a closed entry, the one field it may still change. */
const SUPERSEDED_BY_LINE = /^(- \*\*Superseded by:\*\*).*$/m

export type Entry = {
  id: string
  text: string
}

export type Ledger = {
  entries: Entry[]
  /** The cells of each Index row. */
  index: string[][]
}

/** The "Entry format" block of a ledger is an HTML comment; it holds no real entry. */
const stripComments = (text: string): string => text.replace(/<!--[\s\S]*?-->/g, '')

function cells(line: string): string[] {
  return line
    .split('|')
    .slice(1, -1)
    .map((cell) => cell.trim())
}

/** Splits a ledger into its entries (the "### DEBT-NNN" blocks) and the rows of its Index. */
export function parseLedger(text: string): Ledger {
  const lines = normalize(stripComments(text)).split('\n')
  const entries: Entry[] = []
  const index: string[][] = []
  let open: { id: string; lines: string[] } | null = null
  let inIndex = false
  const close = (): void => {
    if (open !== null) {
      entries.push({ id: open.id, text: open.lines.join('\n').trimEnd() })
      open = null
    }
  }
  for (const line of lines) {
    const heading = ENTRY_HEADING.exec(line)
    if (heading !== null) {
      close()
      open = { id: heading[1] ?? '', lines: [line] }
      inIndex = false
      continue
    }
    if (SECTION_HEADING.test(line)) {
      close()
      inIndex = INDEX_HEADING.test(line)
      continue
    }
    if (open !== null) {
      open.lines.push(line)
    } else if (inIndex && line.startsWith('|') && !TABLE_RULE.test(line)) {
      index.push(cells(line))
    }
  }
  close()
  return { entries, index: index.slice(1) }
}

const field = (entry: string, name: string): string | null => {
  const match = new RegExp(`^\\|\\s*\\*\\*${name}\\*\\*\\s*\\|\\s*(.*?)\\s*\\|\\s*$`, 'm').exec(
    entry,
  )
  return match === null ? null : (match[1] ?? '')
}

const isDate = (value: string | null): boolean => value !== null && ISO_DATE.test(value)

export type LedgerKind = 'pending-debt' | 'closed-debt'

/**
 * What is wrong with a ledger as it would be saved. An entry is judged only when it is new or
 * changed, so a record already on disk never blocks an unrelated edit.
 * `other` is the other ledger, or null when it does not exist.
 */
export function validateLedger(
  kind: LedgerKind,
  current: string | null,
  resulting: string,
  other: string | null,
): string[] {
  const problems: string[] = []
  const after = parseLedger(resulting)
  const before = current === null ? null : parseLedger(current)
  const known = new Map((before?.entries ?? []).map((entry) => [entry.id, entry.text]))
  const seen = new Set<string>()
  const otherIds = new Set(
    other === null ? [] : parseLedger(other).entries.map((entry) => entry.id),
  )
  for (const entry of after.entries) {
    if (!DEBT_ID.test(entry.id)) {
      problems.push(
        `${entry.id} is not a valid ID. Use DEBT- and at least three digits, such as DEBT-007.`,
      )
      continue
    }
    if (seen.has(entry.id)) {
      problems.push(`${entry.id} appears twice in this ledger. Never reuse an ID.`)
    }
    seen.add(entry.id)
    const unchanged = known.get(entry.id) === entry.text
    if (unchanged) {
      continue
    }
    // A reopened problem gets a new ID. Only moving a pending item to closed puts one ID in both.
    if (kind === 'pending-debt' && !known.has(entry.id) && otherIds.has(entry.id)) {
      problems.push(
        `${entry.id} is already in the closed ledger. A problem that comes back gets a new ID and links back to the closed one.`,
      )
    }
    problems.push(...entryProblems(kind, entry))
  }
  if (kind === 'closed-debt') {
    problems.push(...closedIndexProblems(after.index))
  }
  return problems
}

/** The Index rows of the closed ledger whose outcome is not one of the known outcomes. */
function closedIndexProblems(index: readonly string[][]): string[] {
  const problems: string[] = []
  for (const row of index) {
    const outcome = row[2] ?? ''
    if (row.length > 0 && !(OUTCOMES as readonly string[]).includes(outcome)) {
      problems.push(
        `The Index row of ${row[1] ?? 'an item'} has outcome "${outcome}". Use ${OUTCOMES.join(', ')}.`,
      )
    }
  }
  return problems
}

/** Text with its code removed, so a literal `{{ x }}` in a code span is not taken for a placeholder. */
const withoutCode = (text: string): string =>
  text.replace(/```[\s\S]*?```/g, '').replace(/`[^`\n]*`/g, '')

function entryProblems(kind: LedgerKind, entry: Entry): string[] {
  const problems: string[] = []
  if (withoutCode(entry.text).includes('{{')) {
    problems.push(`${entry.id}: replace every {{placeholder}} of the template.`)
  }
  if (kind === 'pending-debt') {
    const status = field(entry.text, 'Status') ?? ''
    if (!DEBT_STATUSES.some((name) => status.includes(name))) {
      problems.push(`${entry.id}: Status must be one of ${DEBT_STATUSES.join(', ')}.`)
    }
    if (!isDate(field(entry.text, 'Logged'))) {
      problems.push(`${entry.id}: Logged must be a date, YYYY-MM-DD.`)
    }
    return problems
  }
  const outcome = field(entry.text, 'Outcome') ?? ''
  if (!(OUTCOMES as readonly string[]).includes(outcome)) {
    problems.push(`${entry.id}: Outcome must be one of ${OUTCOMES.join(', ')}.`)
  }
  for (const name of ['Closed on', 'Logged on']) {
    if (!isDate(field(entry.text, name))) {
      problems.push(`${entry.id}: ${name} must be a date, YYYY-MM-DD.`)
    }
  }
  const owner = field(entry.text, 'Owner') ?? ''
  if (owner === '' || owner.startsWith('{{')) {
    problems.push(`${entry.id}: copy Owner from the pending entry.`)
  }
  return problems
}

/** The closed entry with its one editable field blanked out. */
const settledEntry = (text: string): string => text.replace(SUPERSEDED_BY_LINE, '$1 _')

/** Why an edit to a closed ledger needs the owner's approval: it rewrites a closed record. */
export function closedAuthority(current: string, resulting: string): string[] {
  const before = parseLedger(current)
  const after = new Map(parseLedger(resulting).entries.map((entry) => [entry.id, entry.text]))
  const reasons: string[] = []
  for (const entry of before.entries) {
    const next = after.get(entry.id)
    if (next === undefined) {
      reasons.push(`The edit removes the closed entry ${entry.id}.`)
    } else if (settledEntry(next) !== settledEntry(entry.text)) {
      reasons.push(
        `The edit changes the closed entry ${entry.id} beyond its "Superseded by" field.`,
      )
    }
  }
  const rows = new Set(parseLedger(resulting).index.map((row) => row.slice(0, -1).join('|')))
  for (const row of before.index) {
    if (!rows.has(row.slice(0, -1).join('|'))) {
      reasons.push(
        `The edit changes the Index row of ${row[1] ?? 'a closed item'} beyond its "Superseded by" cell.`,
      )
    }
  }
  return reasons
}

/**
 * Why an edit to the pending ledger needs the owner's approval: it removes an item that has
 * no closed entry yet. `closed` is the closed ledger, or null when it does not exist, and
 * `adrIds` are the IDs of the ADRs in the decisions folder.
 */
export function pendingAuthority(
  current: string,
  resulting: string,
  closed: string | null,
  adrIds: ReadonlySet<string>,
): string[] {
  const kept = new Set(parseLedger(resulting).entries.map((entry) => entry.id))
  const closedEntries = new Map(
    (closed === null ? [] : parseLedger(closed).entries).map((entry) => [entry.id, entry.text]),
  )
  const reasons: string[] = []
  for (const { id } of parseLedger(current).entries) {
    if (kept.has(id)) {
      continue
    }
    const entry = closedEntries.get(id)
    const outcome = entry === undefined ? null : field(entry, 'Outcome')
    if (
      entry === undefined ||
      outcome === null ||
      !(OUTCOMES as readonly string[]).includes(outcome)
    ) {
      reasons.push(
        `The edit removes ${id} from the pending ledger, and the closed ledger has no entry with an outcome for it.`,
      )
    } else if (
      outcome === 'accepted' &&
      !(entry.match(/ADR_[\w-]+/g) ?? []).some((cited) => ADR_ID.test(cited) && adrIds.has(cited))
    ) {
      reasons.push(
        `${id} is closed as accepted, and its closed entry cites no ADR that exists in the decisions folder.`,
      )
    }
  }
  return reasons
}
