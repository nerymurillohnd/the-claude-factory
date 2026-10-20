import { expect, test } from 'claude-code/testing'
import { type AdrContext, adrAuthority, parseFrontmatter, validateAdr } from '../hooks/adr.ts'
import { adr, SETTLED } from './fixtures.ts'

const NAME = 'ADR_2026-03-14_keep-sessions-in-postgres.md'
const IDS = new Set(['ADR_2026-01-02_use-redis', 'ADR_2026-03-14_keep-sessions-in-postgres'])

const context: AdrContext = { name: NAME, exists: false, ids: IDS }

test('a well formed ADR has no problem', () => {
  expect(validateAdr(adr(), context)).toEqual([])
})

test('the frontmatter is read as scalars and lists', () => {
  const parsed = parseFrontmatter(adr({ makers: 'Nery' }))
  expect(parsed?.scalars.get('status')).toBe('accepted')
  expect(parsed?.lists.get('decision-makers')).toEqual(['Nery'])
})

test('each rule refuses its own violation', () => {
  const cases: [string, string, string][] = [
    ['status', adr({ status: 'pending' }), 'status must be one of'],
    ['date', adr({ date: '2026-03-15' }), 'date must equal the date in the file name'],
    [
      'decision makers placeholder',
      adr({ makers: '{Accountable person or role}' }),
      'decision-makers',
    ],
    [
      'supersedes with extension',
      adr({ supersedes: 'ADR_2026-01-02_use-redis.md' }),
      'holds an ID',
    ],
    [
      'supersedes without a file',
      adr({ supersedes: 'ADR_2026-01-02_use-memcached' }),
      'has no file in the decisions folder',
    ],
    [
      'supersedes itself',
      adr({ supersedes: 'ADR_2026-03-14_keep-sessions-in-postgres' }),
      'cannot point at the record itself',
    ],
    ['superseded without a successor', adr({ status: 'superseded' }), 'needs superseded-by'],
    [
      'template comment',
      `${adr()}\n<!-- Optional: remove this section -->\n`,
      'Remove the template comments',
    ],
    ['no title', adr({}, 'No heading here.'), 'Give the record a title'],
    [
      'placeholder title',
      adr({}, '# {Short title naming the decision}'),
      'Give the record a title',
    ],
  ]
  for (const [label, text, expected] of cases) {
    const problems = validateAdr(text, context).join('\n')
    expect(problems, label).toContain(expected)
  }
})

test('a missing frontmatter and a bad name are refused', () => {
  expect(validateAdr('# Title\n', context).join('\n')).toContain(
    'Start the file with the YAML frontmatter',
  )
  const misnamed = { name: 'adr-postgres.md', exists: false, ids: IDS }
  expect(validateAdr(adr(), misnamed).join('\n')).toContain('Name the file ADR_')
})

test('a file that was already there and is not named like an ADR is left alone', () => {
  expect(validateAdr('Anything', { name: 'README.md', exists: true, ids: IDS })).toEqual([])
})

test('a valid supersession points at an existing ID', () => {
  const text = adr({ supersedes: 'ADR_2026-01-02_use-redis' })
  expect(validateAdr(text, context)).toEqual([])
})

test('a proposed ADR changes freely', () => {
  const proposed = adr({ status: 'proposed' })
  expect(adrAuthority(proposed, proposed.replace('Sessions.', 'Sessions and caches.'))).toEqual([])
})

test('a settled ADR accepts a new status, a successor and a Confirmation result', () => {
  const superseded = SETTLED.replace('status: accepted', 'status: superseded').replace(
    'superseded-by: none',
    'superseded-by: ADR_2026-01-02_use-redis',
  )
  expect(adrAuthority(SETTLED, superseded)).toEqual([])
  expect(adrAuthority(SETTLED, SETTLED.replace('| pending |', '| 31 ms on 2026-04-02 |'))).toEqual(
    [],
  )
  expect(adrAuthority(SETTLED, SETTLED.replace('status: accepted', 'status: deprecated'))).toEqual(
    [],
  )
})

test('a settled ADR does not accept new reasoning, a lost frontmatter or a reopened status', () => {
  const reasoning = adrAuthority(
    SETTLED,
    SETTLED.replace('Chosen option: **Postgres**.', 'Chosen option: **Redis**.'),
  )
  expect(reasoning.join('\n')).toContain('changes the text of a settled ADR')
  const evidence = adrAuthority(
    SETTLED,
    SETTLED.replace('Linked to the migration plan.', 'Linked to something else.'),
  )
  expect(evidence.join('\n')).toContain('changes the text of a settled ADR')
  const reopened = adrAuthority(SETTLED, SETTLED.replace('status: accepted', 'status: proposed'))
  expect(reopened.join('\n')).toContain('from accepted to proposed')
  expect(adrAuthority(SETTLED, '# Just a title\n').join('\n')).toContain('removes the frontmatter')
})

test('a file without a status is not judged', () => {
  expect(adrAuthority('# Notes\n', '# Other notes\n')).toEqual([])
})
