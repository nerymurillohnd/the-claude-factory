// ADR rules, as pure functions over plain text. No call on `$` lives here, so the same code
// runs in the hooks and in the tests.

import { ADR_ID, ADR_NAME, ADR_STATUSES, adrId, normalize } from './paths.ts'

export type Frontmatter = {
  scalars: Map<string, string>
  lists: Map<string, string[]>
}

function unquote(value: string): string {
  const trimmed = value.trim()
  const quote = trimmed[0]
  if ((quote === '"' || quote === "'") && trimmed.length >= 2 && trimmed.endsWith(quote)) {
    return trimmed.slice(1, -1)
  }
  return trimmed
}

/** Reads the YAML frontmatter the ADR template uses: scalars and lists of scalars. */
export function parseFrontmatter(text: string): Frontmatter | null {
  const lines = normalize(text).split('\n')
  if (lines[0] !== '---') {
    return null
  }
  const end = lines.indexOf('---', 1)
  if (end === -1) {
    return null
  }
  const scalars = new Map<string, string>()
  const lists = new Map<string, string[]>()
  let listKey: string | null = null
  for (const line of lines.slice(1, end)) {
    const item = /^\s+-\s+(.*)$/.exec(line)
    if (item !== null && listKey !== null) {
      lists.get(listKey)?.push(unquote(item[1] ?? ''))
      continue
    }
    const pair = /^([A-Za-z][\w-]*):\s*(.*)$/.exec(line)
    if (pair === null) {
      listKey = null
      continue
    }
    const key = pair[1] ?? ''
    const value = (pair[2] ?? '').trim()
    if (value === '') {
      listKey = key
      lists.set(key, [])
    } else {
      listKey = null
      scalars.set(key, unquote(value))
    }
  }
  return { scalars, lists }
}

const isPlaceholder = (value: string): boolean => /^\{.*\}$/.test(value.trim())

export type AdrContext = {
  name: string
  /** True when the file is already on disk. */
  exists: boolean
  /** The IDs of the ADRs in the folder. */
  ids: ReadonlySet<string>
}

/** What is wrong with an ADR as it would be saved. An empty list means the record is well formed. */
export function validateAdr(text: string, context: AdrContext): string[] {
  const nameMatch = ADR_NAME.exec(context.name)
  if (nameMatch === null) {
    // A file that was already there and is not an ADR is not ours to judge.
    return context.exists
      ? []
      : [
          `Name the file ADR_<YYYY-MM-DD>_<slug>.md with a lowercase kebab-case slug. "${context.name}" does not match.`,
        ]
  }
  const frontmatter = parseFrontmatter(text)
  if (frontmatter === null) {
    return [
      'Start the file with the YAML frontmatter of the ADR template: status, date, decision-makers, supersedes and superseded-by.',
    ]
  }
  const problems: string[] = []
  const status = frontmatter.scalars.get('status') ?? ''
  if (!(ADR_STATUSES as readonly string[]).includes(status)) {
    problems.push(`status must be one of ${ADR_STATUSES.join(', ')}. Found "${status}".`)
  }
  const date = frontmatter.scalars.get('date') ?? ''
  if (date !== nameMatch[1]) {
    problems.push(
      `date must equal the date in the file name (${nameMatch[1] ?? ''}). Found "${date}".`,
    )
  }
  const makers = frontmatter.lists.get('decision-makers') ?? []
  if (makers.length === 0 || makers.some((maker) => maker === '' || isPlaceholder(maker))) {
    problems.push(
      'decision-makers must list at least one real person or role, with no template placeholder.',
    )
  }
  for (const key of ['consulted', 'informed'] as const) {
    if (
      (frontmatter.lists.get(key) ?? []).some((person) => person === '' || isPlaceholder(person))
    ) {
      problems.push(
        `Remove the ${key} lines, or name a real person or role: ${key} still holds a template placeholder.`,
      )
    }
  }
  const selfId = adrId(context.name)
  for (const key of ['supersedes', 'superseded-by'] as const) {
    const value = frontmatter.scalars.get(key)
    if (value === undefined) {
      problems.push(`Add "${key}: none" to the frontmatter.`)
    } else if (value !== 'none') {
      if (!ADR_ID.test(value)) {
        problems.push(`${key} holds an ID, the ADR file name without .md. Found "${value}".`)
      } else if (value === selfId) {
        problems.push(`${key} cannot point at the record itself.`)
      } else if (!context.ids.has(value)) {
        problems.push(`${key} points at ${value}, which has no file in the decisions folder.`)
      }
    }
  }
  if (status === 'superseded' && (frontmatter.scalars.get('superseded-by') ?? 'none') === 'none') {
    problems.push(
      'A superseded record needs superseded-by set to the ID of the record that replaces it. Change status and superseded-by in one edit.',
    )
  }
  if (
    /Template for \.claude\/maintainer\/decisions\//.test(text) ||
    /<!--\s*Optional:/.test(text)
  ) {
    problems.push('Remove the template comments from the record.')
  }
  const title = /^# (.+)$/m.exec(normalize(text))
  if (title === null || isPlaceholder(title[1] ?? '')) {
    problems.push('Give the record a title: one "# " heading that names the decision.')
  }
  return problems
}

/** Drops the one section a settled ADR may still fill in: Confirmation, up to the next heading. */
function withoutConfirmation(lines: string[]): string[] {
  const start = lines.findIndex((line) => line.trim() === '### Confirmation')
  if (start === -1) {
    return lines
  }
  const next = lines.findIndex((line, index) => index > start && /^#{1,6} /.test(line))
  return [...lines.slice(0, start), ...(next === -1 ? [] : lines.slice(next))]
}

/** The record with the parts a settled ADR may still change blanked out. */
function settledShape(text: string): string {
  const lines = normalize(text).split('\n')
  const masked = lines.map((line) =>
    /^(status|superseded-by):/.test(line) ? line.replace(/:.*$/, ': _') : line,
  )
  return withoutConfirmation(masked).join('\n')
}

/** The only status changes a settled record accepts. */
const NEXT_STATUS: Readonly<Record<string, readonly string[]>> = {
  accepted: ['superseded', 'deprecated'],
  deprecated: ['superseded'],
}

/**
 * Why an edit to an ADR needs the owner's approval. A `proposed` record is still open and
 * changes freely. Any other record changes only its status, its superseded-by and its Confirmation.
 */
export function adrAuthority(current: string, resulting: string): string[] {
  const before = parseFrontmatter(current)
  const status = before?.scalars.get('status')
  if (before === null || status === undefined || status === 'proposed') {
    return []
  }
  const after = parseFrontmatter(resulting)
  if (after === null) {
    return ['The edit removes the frontmatter of a settled ADR.']
  }
  const reasons: string[] = []
  const nextStatus = after.scalars.get('status') ?? ''
  if (nextStatus !== status && !(NEXT_STATUS[status] ?? []).includes(nextStatus)) {
    reasons.push(
      `The edit changes the status of a settled ADR from ${status} to ${nextStatus || 'nothing'}.`,
    )
  }
  if (settledShape(current) !== settledShape(resulting)) {
    reasons.push(
      'The edit changes the text of a settled ADR beyond its status, superseded-by and Confirmation section.',
    )
  }
  return reasons
}
