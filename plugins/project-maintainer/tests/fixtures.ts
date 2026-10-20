// Sample records for the tests: well formed by default, changed one field at a time.

export type Fields = {
  status?: string
  date?: string
  makers?: string
  supersedes?: string
  supersededBy?: string
}

export function adr(
  fields: Fields = {},
  body = '# Keep sessions in Postgres\n\n## Scope\n\nSessions.\n',
): string {
  const lines = [
    '---',
    `status: ${fields.status ?? 'accepted'}`,
    `date: ${fields.date ?? '2026-03-14'}`,
    'decision-makers:',
    `  - "${fields.makers ?? 'Project owner'}"`,
    `supersedes: ${fields.supersedes ?? 'none'}`,
    `superseded-by: ${fields.supersededBy ?? 'none'}`,
    '---',
    '',
    body,
  ]
  return lines.join('\n')
}

export const SETTLED = adr(
  { status: 'accepted' },
  [
    '# Keep sessions in Postgres',
    '',
    '## Decision outcome',
    '',
    'Chosen option: **Postgres**.',
    '',
    '### Confirmation',
    '',
    '| What must be true | How it is checked | Result | When to re-check |',
    '| --- | --- | --- | --- |',
    '| Latency under 50 ms | load test | pending | 2026-06-01 |',
    '',
    '## More information',
    '',
    'Linked to the migration plan.',
    '',
  ].join('\n'),
)

export const pendingEntry = (id: string, status = '🟡 Pending', logged = '2026-03-01'): string =>
  [
    `### ${id} — Export fails over 2 GB`,
    '',
    '| Field | Value |',
    '| --- | --- |',
    `| **Status** | ${status} |`,
    '| **Category** | quality |',
    '| **Owner** | unassigned |',
    `| **Logged** | ${logged} |`,
    '',
    '#### 📈 Impact and next step',
    '',
    '- **Next action:** ask the vendor',
    '',
  ].join('\n')

export const closedEntry = (id: string, outcome = 'resolved', extra = ''): string =>
  [
    `### ${id} — Export fixed`,
    '',
    '| Field | Value |',
    '| --- | --- |',
    `| **Outcome** | ${outcome} |`,
    '| **Closed on** | 2026-03-20 |',
    '| **Logged on** | 2026-03-01 |',
    '| **Owner** | unassigned |',
    '',
    '#### 🔗 Follow-up',
    '',
    `- **Closed by:** ${extra || 'none'}`,
    '- **Superseded by:** none',
    '',
  ].join('\n')

const TEMPLATE_COMMENT =
  '<!--\nEntry format.\n\n### DEBT-NNN — {{Short debt title}}\n\n| **Status** | 🟡 Pending |\n-->\n'

export function pending(...entries: string[]): string {
  const rows = entries.map(
    (entry) => `| ${/DEBT-\d+/.exec(entry)?.[0] ?? ''} | Export | 🟡 Pending |`,
  )
  return [
    '# 🧾 Pending Debt',
    '',
    '## 📋 Index',
    '',
    '| ID | Title | Status |',
    '| --- | --- | --- |',
    ...rows,
    '',
    '## 📂 Open items',
    '',
    ...entries,
    TEMPLATE_COMMENT,
  ].join('\n')
}

export function closed(...entries: [string, string][]): string {
  const rows = entries.map(
    ([id, outcome]) => `| 2026-03-20 | ${id} | ${outcome} | Export fixed | none |`,
  )
  const bodies = entries.map(([id, outcome]) => closedEntry(id, outcome))
  return [
    '# ✅ Closed Debt',
    '',
    '## 📚 Index',
    '',
    '| Date | ID | Outcome | Closure | Superseded by |',
    '| --- | --- | --- | --- | --- |',
    ...rows,
    '',
    '## 🏁 Closed items',
    '',
    ...bodies,
    TEMPLATE_COMMENT,
  ].join('\n')
}
