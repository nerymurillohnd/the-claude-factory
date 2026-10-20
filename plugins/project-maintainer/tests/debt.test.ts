import { expect, test } from 'claude-code/testing'
import { closedAuthority, parseLedger, pendingAuthority, validateLedger } from '../hooks/debt.ts'
import { closed, pending, pendingEntry } from './fixtures.ts'

test('the ledger parser reads entries and index rows and ignores the Entry format comment', () => {
  const ledger = parseLedger(pending(pendingEntry('DEBT-001'), pendingEntry('DEBT-002')))
  expect(ledger.entries.map((entry) => entry.id)).toEqual(['DEBT-001', 'DEBT-002'])
  expect(ledger.index.map((row) => row[0])).toEqual(['DEBT-001', 'DEBT-002'])
})

test('a well formed pending ledger and a well formed closed ledger have no problem', () => {
  expect(validateLedger('pending-debt', null, pending(pendingEntry('DEBT-001')), null)).toEqual([])
  expect(validateLedger('closed-debt', null, closed(['DEBT-001', 'resolved']), null)).toEqual([])
})

test('each ledger rule refuses its own violation', () => {
  const run = (
    kind: 'pending-debt' | 'closed-debt',
    text: string,
    other: string | null = null,
  ): string => validateLedger(kind, null, text, other).join('\n')
  expect(
    run('pending-debt', pending(pendingEntry('DEBT-001'), pendingEntry('DEBT-001'))),
  ).toContain('appears twice')
  expect(run('pending-debt', pending(pendingEntry('DEBT-1')))).toContain('not a valid ID')
  expect(run('pending-debt', pending(pendingEntry('DEBT-001', '🟣 Maybe')))).toContain(
    'Status must be one of',
  )
  expect(
    run('pending-debt', pending(pendingEntry('DEBT-001', '🟡 Pending', 'yesterday'))),
  ).toContain('Logged must be a date')
  expect(
    run('pending-debt', `${pending(pendingEntry('DEBT-001'))}\n{{Short debt title}}\n`),
  ).toContain('replace every {{placeholder}}')
  expect(run('closed-debt', closed(['DEBT-001', 'forgotten']))).toContain('Outcome must be one of')
  expect(
    run(
      'closed-debt',
      closed(['DEBT-001', 'resolved']).replace(
        '| **Closed on** | 2026-03-20 |',
        '| **Closed on** | soon |',
      ),
    ),
  ).toContain('Closed on must be a date')
  expect(
    run(
      'closed-debt',
      closed(['DEBT-001', 'resolved']).replace('| **Owner** | unassigned |', '| **Owner** |  |'),
    ),
  ).toContain('copy Owner')
})

test('a problem that comes back gets a new ID, and moving a pending item to closed is fine', () => {
  const reopened = validateLedger(
    'pending-debt',
    null,
    pending(pendingEntry('DEBT-001')),
    closed(['DEBT-001', 'resolved']),
  )
  expect(reopened.join('\n')).toContain('already in the closed ledger')
  const moved = validateLedger(
    'closed-debt',
    null,
    closed(['DEBT-001', 'obsolete']),
    pending(pendingEntry('DEBT-001')),
  )
  expect(moved).toEqual([])
})

test('a literal {{ }} in unchanged content or in code is not a placeholder', () => {
  const withTemplateSyntax = pending(pendingEntry('DEBT-001')).replace(
    'ask the vendor',
    'ask about {{ secrets.TOKEN }}',
  )
  // An entry already on disk that holds {{ }} never blocks an unrelated edit.
  const edited = withTemplateSyntax.replace('Export', 'Exports')
  expect(validateLedger('pending-debt', withTemplateSyntax, edited, null)).toEqual([])
  // A new entry may quote {{ }} inside a code span.
  const quoted = pending(pendingEntry('DEBT-001')).replace(
    'ask the vendor',
    'use the `{{ name }}` form',
  )
  expect(validateLedger('pending-debt', null, quoted, null)).toEqual([])
})

test('an entry that did not change is never judged', () => {
  const broken = pending(pendingEntry('DEBT-001', '🟣 Maybe'), pendingEntry('DEBT-002'))
  const edited = broken.replace('ask the vendor', 'ask the vendor again')
  expect(validateLedger('pending-debt', broken, edited, null).join('\n')).toContain('DEBT-001')
  const untouched = broken.replace(
    '| Export | 🟡 Pending |\n| DEBT-002',
    '| Export | 🟡 Pending |\n| DEBT-002',
  )
  const onlySecond = untouched
    .replace('ask the vendor\n', 'ask the vendor\n')
    .replace('### DEBT-002 — Export fails over 2 GB', '### DEBT-002 — Export fails over 3 GB')
  expect(validateLedger('pending-debt', broken, onlySecond, null).join('\n')).not.toContain(
    'DEBT-001',
  )
})

const ADR_IDS = new Set(['ADR_2026-03-10_keep-the-limit'])

test('a pending item leaves only after a closed entry with an outcome exists', () => {
  const before = pending(pendingEntry('DEBT-001'), pendingEntry('DEBT-002'))
  const after = pending(pendingEntry('DEBT-002'))
  expect(pendingAuthority(before, after, null, ADR_IDS).join('\n')).toContain(
    'no entry with an outcome for it',
  )
  expect(pendingAuthority(before, after, closed(['DEBT-001', 'resolved']), ADR_IDS)).toEqual([])
  expect(pendingAuthority(before, after, closed(['DEBT-001', 'obsolete']), ADR_IDS)).toEqual([])
  expect(
    pendingAuthority(
      before,
      pending(pendingEntry('DEBT-001'), pendingEntry('DEBT-002')),
      null,
      ADR_IDS,
    ),
  ).toEqual([])
})

test('closing as accepted needs an ADR that exists', () => {
  const before = pending(pendingEntry('DEBT-001'))
  const after = pending()
  const withoutAdr = closed(['DEBT-001', 'accepted'])
  expect(pendingAuthority(before, after, withoutAdr, ADR_IDS).join('\n')).toContain(
    'cites no ADR that exists',
  )
  const missingAdr = withoutAdr.replace(
    '- **Closed by:** none',
    '- **Closed by:** ADR_2026-03-11_not-written',
  )
  expect(pendingAuthority(before, after, missingAdr, ADR_IDS).join('\n')).toContain(
    'cites no ADR that exists',
  )
  const withAdr = withoutAdr.replace(
    '- **Closed by:** none',
    '- **Closed by:** ADR_2026-03-10_keep-the-limit',
  )
  expect(pendingAuthority(before, after, withAdr, ADR_IDS)).toEqual([])
})

test('a closed entry changes only in its Superseded by field', () => {
  const base = closed(['DEBT-001', 'resolved'])
  const successor = base
    .replaceAll('- **Superseded by:** none', '- **Superseded by:** DEBT-004')
    .replace('| Export fixed | none |', '| Export fixed | DEBT-004 |')
  expect(closedAuthority(base, successor)).toEqual([])
  expect(
    closedAuthority(base, base.replace('Export fixed', 'Export fixed again')).join('\n'),
  ).toContain('beyond its "Superseded by"')
  expect(closedAuthority(base, closed()).join('\n')).toContain('removes the closed entry DEBT-001')
  expect(
    closedAuthority(
      base,
      base.replace('| 2026-03-20 | DEBT-001 | resolved |', '| 2026-03-21 | DEBT-001 | resolved |'),
    ).join('\n'),
  ).toContain('Index row')
  const added = closed(['DEBT-001', 'resolved'], ['DEBT-002', 'obsolete'])
  expect(closedAuthority(base, added)).toEqual([])
})
