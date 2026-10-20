import type { On } from 'claude-code'
import { expect, mock, test } from 'claude-code/testing'
import { adr, closed, pending, pendingEntry, SETTLED } from './fixtures.ts'

const ROOT = '/work/app'
const DECISIONS = `${ROOT}/.claude/maintainer/decisions`
const DEBT = `${ROOT}/.claude/maintainer/technical-debt`
const SETTLED_ADR = `${DECISIONS}/ADR_2026-03-14_keep-sessions-in-postgres.md`
const NEW_ADR = `${DECISIONS}/ADR_2026-04-01_move-sessions-to-redis.md`
const PENDING = `${DEBT}/pending-debt.md`
const CLOSED = `${DEBT}/closed-debt.md`

type Files = Record<string, string>

/** The project on disk, as the hooks see it through `$.fs` and `$.session`. */
function world(on: On, files: Files, unreadable: readonly string[] = []): void {
  on('fs.read', (_$, e) => {
    const text = files[e.path]
    return text === undefined || unreadable.includes(e.path)
      ? { deny: `EACCES: ${e.path}` }
      : { value: text }
  })
  on('fs.list', (_$, e) => ({
    value: Object.keys(files)
      .filter(
        (path) => path.startsWith(`${e.path}/`) && !path.slice(e.path.length + 1).includes('/'),
      )
      .map((path) => ({
        name: path.slice(e.path.length + 1),
        kind: 'file' as const,
        size: 0,
        mtimeMs: 0,
        isLink: false,
      })),
  }))
  on('fs.exists', (_$, e) => ({
    value: Object.keys(files).some((path) => path === e.path || path.startsWith(`${e.path}/`)),
  }))
  on('session.root', () => ({ value: ROOT }))
  on('session.cwd', () => ({ value: ROOT }))
}

const project = (): Files => ({
  [SETTLED_ADR]: SETTLED,
  [PENDING]: pending(pendingEntry('DEBT-001'), pendingEntry('DEBT-002')),
})

const edit = (
  file: string,
  from: string,
  to: string,
): { tool: 'Edit'; file_path: string; old_string: string; new_string: string } => ({
  tool: 'Edit',
  file_path: file,
  old_string: from,
  new_string: to,
})

test('the format guard refuses a malformed ADR and tells Claude how to fix it', async ($, on) => {
  world(on, project())
  on('tool.call', () => ({ result: 'saved' }))
  const refused = await $.tool.call({
    tool: 'Write',
    file_path: NEW_ADR,
    content: adr({ status: 'maybe', date: '2026-04-02' }),
  })
  expect(JSON.stringify(refused)).toContain(
    'refused to save ADR_2026-04-01_move-sessions-to-redis.md',
  )
  expect(JSON.stringify(refused)).toContain('status must be one of')
  expect(JSON.stringify(refused)).toContain('date must equal the date in the file name')
})

test('the format guard sees a record under a relative path, dots and another case', async ($, on) => {
  world(on, project())
  on('tool.call', () => ({ result: 'saved' }))
  const bad = adr({ status: 'maybe', date: '2026-04-02' })
  const spellings = [
    '.claude/maintainer/decisions/ADR_2026-04-01_move-sessions-to-redis.md',
    `${DECISIONS}/../decisions/ADR_2026-04-01_move-sessions-to-redis.md`,
    `${ROOT}//.claude/./maintainer/decisions/ADR_2026-04-01_move-sessions-to-redis.md`,
    `${ROOT}/.Claude/Maintainer/Decisions/ADR_2026-04-01_move-sessions-to-redis.md`,
  ]
  for (const file_path of spellings) {
    const refused = await $.tool.call({ tool: 'Write', file_path, content: bad })
    expect(JSON.stringify(refused), file_path).toContain('refused to save')
  }
})

test('a record that exists but cannot be read is not saved unchecked', async ($, on) => {
  world(on, project(), [SETTLED_ADR])
  on('tool.call', () => ({ result: 'saved' }))
  on('tool.check', () => ({ decision: 'allow' }))
  const edited = await $.tool.call(edit(SETTLED_ADR, 'status: accepted', 'status: deprecated'))
  expect(JSON.stringify(edited)).toContain('could not read')
  const verdict = await $.tool.check({
    tool: 'Edit',
    input: edit(SETTLED_ADR, 'status: accepted', 'status: deprecated'),
  })
  expect(verdict.decision).toBe('ask')
  expect(verdict.decider).toBe('person')
  expect(verdict.reason).toContain('could not read')
})

test('the format guard lets a well formed ADR, another file and an impossible edit through', async ($, on) => {
  world(on, project())
  on('tool.call', () => ({ result: 'saved' }))
  const good = adr({
    status: 'proposed',
    date: '2026-04-01',
    supersedes: 'ADR_2026-03-14_keep-sessions-in-postgres',
  })
  expect(await $.tool.call({ tool: 'Write', file_path: NEW_ADR, content: good })).toEqual({
    result: 'saved',
  })
  expect(
    await $.tool.call({
      tool: 'Write',
      file_path: `${ROOT}/README.md`,
      content: 'no front matter',
    }),
  ).toEqual({ result: 'saved' })
  expect(await $.tool.call(edit(NEW_ADR, 'not in the file', 'x'))).toEqual({ result: 'saved' })
})

test('the format guard refuses a repeated debt ID and a closed entry without an outcome', async ($, on) => {
  world(on, project())
  on('tool.call', () => ({ result: 'saved' }))
  const repeated = await $.tool.call({
    tool: 'Write',
    file_path: PENDING,
    content: pending(pendingEntry('DEBT-001'), pendingEntry('DEBT-001')),
  })
  expect(JSON.stringify(repeated)).toContain('appears twice')
  const noOutcome = await $.tool.call({
    tool: 'Write',
    file_path: CLOSED,
    content: closed(['DEBT-001', 'finished']),
  })
  expect(JSON.stringify(noOutcome)).toContain('Outcome must be one of')
})

test('the authority guard asks the person before a settled ADR is rewritten', async ($, on) => {
  world(on, project())
  on('tool.check', () => ({ decision: 'allow' }))
  const verdict = await $.tool.check({
    tool: 'Edit',
    input: edit(SETTLED_ADR, 'Chosen option: **Postgres**.', 'Chosen option: **Redis**.'),
  })
  expect(verdict.decision).toBe('ask')
  expect(verdict.decider).toBe('person')
  expect(verdict.reason).toContain('changes the text of a settled ADR')
  expect(verdict.reason).toContain('Write a new ADR that supersedes it')
})

test('the authority guard covers a subagent and a whole-file Write too', async ($, on) => {
  world(on, project())
  on('tool.check', () => ({ decision: 'allow' }))
  const rewritten = SETTLED.replace('Chosen option: **Postgres**.', 'Chosen option: **Redis**.')
  const verdict = await $.tool.check({
    tool: 'Write',
    input: { file_path: SETTLED_ADR, content: rewritten },
    agentId: 'subagent-1',
  })
  expect(verdict.decision).toBe('ask')
  expect(verdict.decider).toBe('person')
})

test('the authority guard lets the allowed edits and new files through', async ($, on) => {
  world(on, project())
  on('tool.check', () => ({ decision: 'allow' }))
  const status = await $.tool.check({
    tool: 'Edit',
    input: edit(SETTLED_ADR, 'status: accepted', 'status: deprecated'),
  })
  expect(status.decision).toBe('allow')
  const result = await $.tool.check({
    tool: 'Edit',
    input: edit(SETTLED_ADR, '| pending |', '| 31 ms |'),
  })
  expect(result.decision).toBe('allow')
  const created = await $.tool.check({
    tool: 'Write',
    input: { file_path: NEW_ADR, content: adr({ date: '2026-04-01' }) },
  })
  expect(created.decision).toBe('allow')
  const elsewhere = await $.tool.check({
    tool: 'Edit',
    input: edit(`${ROOT}/src/app.ts`, 'a', 'b'),
  })
  expect(elsewhere.decision).toBe('allow')
})

test('the authority guard never weakens a refusal that came from the rules', async ($, on) => {
  world(on, project())
  on('tool.check', () => ({ decision: 'deny', reason: 'blocked by a rule' }))
  const verdict = await $.tool.check({
    tool: 'Edit',
    input: edit(SETTLED_ADR, 'Chosen option: **Postgres**.', 'Chosen option: **Redis**.'),
  })
  expect(verdict).toMatchObject({ decision: 'deny', reason: 'blocked by a rule' })
})

test('a pending item may leave only once its closed entry exists', async ($, on) => {
  const files = project()
  world(on, files)
  on('tool.check', () => ({ decision: 'allow' }))
  const without = pending(pendingEntry('DEBT-002'))
  const asked = await $.tool.check({
    tool: 'Write',
    input: { file_path: PENDING, content: without },
  })
  expect(asked.decision).toBe('ask')
  expect(asked.reason).toContain('no entry with an outcome for it')
})

test('a pending item leaves quietly after its closed entry was written', async ($, on) => {
  const files = { ...project(), [CLOSED]: closed(['DEBT-001', 'obsolete']) }
  world(on, files)
  on('tool.check', () => ({ decision: 'allow' }))
  const verdict = await $.tool.check({
    tool: 'Write',
    input: { file_path: PENDING, content: pending(pendingEntry('DEBT-002')) },
  })
  expect(verdict.decision).toBe('allow')
})

test('a closed entry cannot be rewritten without the person', async ($, on) => {
  world(on, { ...project(), [CLOSED]: closed(['DEBT-001', 'resolved']) })
  on('tool.check', () => ({ decision: 'allow' }))
  const verdict = await $.tool.check({
    tool: 'Edit',
    input: edit(CLOSED, 'Export fixed', 'Export never broke'),
  })
  expect(verdict.decision).toBe('ask')
  expect(verdict.decider).toBe('person')
})

test('a shell command that rewrites the records asks the person, a read does not', async ($, on) => {
  world(on, project())
  on('tool.check', () => ({ decision: 'allow' }))
  const removal = await $.tool.check({ tool: 'Bash', input: { command: `rm ${SETTLED_ADR}` } })
  expect(removal.decision).toBe('ask')
  expect(removal.decider).toBe('person')
  expect(removal.reason).toContain('Write and Edit tools')
  const read = await $.tool.check({ tool: 'Bash', input: { command: `cat ${SETTLED_ADR}` } })
  expect(read.decision).toBe('allow')
})

const MESSAGES = [{ role: 'user' as const, text: 'We chose Postgres.', toolUses: [] }]

/** Answers the compaction in Claude Code's place and remembers the instructions it was given. */
function compaction(on: On): { instructions: string | undefined } {
  const seen: { instructions: string | undefined } = { instructions: undefined }
  on('session.compact', (_$, e) => {
    seen.instructions = e.instructions
    return { messages: e.messages }
  })
  return seen
}

test('a compaction keeps the records out of the loss when the project has them', async ($, on) => {
  world(on, project())
  const seen = compaction(on)
  await $.session.compact({ trigger: 'auto', messages: MESSAGES })
  expect(seen.instructions).toContain('DEBT-')
  await $.session.compact({
    trigger: 'manual',
    instructions: 'Focus on the API',
    messages: MESSAGES,
  })
  expect(seen.instructions).toContain('Focus on the API')
  expect(seen.instructions).toContain('DEBT-')
})

test('a compaction is left alone when the project has no records', async ($, on) => {
  world(on, {})
  const seen = compaction(on)
  await $.session.compact({ trigger: 'auto', messages: MESSAGES })
  expect(seen.instructions).toBeUndefined()
})

test('a compaction is left alone for a subagent and for a precompute', async ($, on) => {
  world(on, project())
  const seen = compaction(on)
  await $.session.compact({ trigger: 'auto', agentId: 'subagent-1', messages: MESSAGES })
  expect(seen.instructions).toBeUndefined()
  await $.session.compact({ trigger: 'precompute', messages: MESSAGES })
  expect(seen.instructions).toBeUndefined()
})

function commits(on: On, head: { value: string }, shown: string): void {
  on('tool.call', () => {
    head.value = 'bbb222'
    return { result: 'committed' }
  })
  on('process.run', (_$, e) => ({
    value: {
      exitCode: 0,
      stdout: e.argv[1] === 'rev-parse' ? head.value : shown,
      stderr: '',
      isStdoutTruncated: false,
      isStderrTruncated: false,
    },
  }))
}

test('a commit that changes a dependency manifest adds one reminder', async ($, on) => {
  world(on, project())
  const session = mock.session(on)
  commits(on, { value: 'aaa111' }, 'Add a cache layer\npackage.json\nsrc/cache.ts\n')
  await $.tool.call({ tool: 'Bash', command: 'git commit -m "Add a cache layer"' })
  const rows = JSON.stringify(session.appended())
  expect(rows).toContain('a dependency manifest')
  expect(rows).toContain('write-records')
  expect(session.appended().length).toBe(1)
})

test('a commit without a signal adds nothing', async ($, on) => {
  world(on, project())
  const session = mock.session(on)
  commits(on, { value: 'aaa111' }, 'Fix a typo\nREADME.md\n')
  await $.tool.call({ tool: 'Bash', command: 'git commit -m "Fix a typo"' })
  expect(session.appended().length).toBe(0)
})

test('a commit that did not happen adds nothing', async ($, on) => {
  world(on, project())
  const session = mock.session(on)
  on('tool.call', () => ({ result: 'nothing to commit' }))
  on('process.run', (_$, e) => ({
    value: {
      exitCode: 0,
      stdout: e.argv[1] === 'rev-parse' ? 'aaa111' : 'Add a cache layer\npackage.json\n',
      stderr: '',
      isStdoutTruncated: false,
      isStderrTruncated: false,
    },
  }))
  await $.tool.call({ tool: 'Bash', command: 'git commit -m "Add a cache layer"' })
  expect(session.appended().length).toBe(0)
})

test('a command that is not a commit adds nothing', async ($, on) => {
  world(on, project())
  const session = mock.session(on)
  commits(on, { value: 'aaa111' }, 'Add a cache layer\npackage.json\n')
  await $.tool.call({ tool: 'Bash', command: 'ls -la' })
  expect(session.appended().length).toBe(0)
})

test('the reminder can be turned off', { options: { commitNudge: false } }, async ($, on) => {
  world(on, project())
  const session = mock.session(on)
  commits(on, { value: 'aaa111' }, 'Add a cache layer\npackage.json\n')
  await $.tool.call({ tool: 'Bash', command: 'git commit -m "Add a cache layer"' })
  expect(session.appended().length).toBe(0)
})
