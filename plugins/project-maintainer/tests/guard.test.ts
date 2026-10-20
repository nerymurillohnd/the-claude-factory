import { expect, test } from 'claude-code/testing'
import {
  bashReason,
  commitSignals,
  fileInput,
  resultingText,
  withKeepNote,
} from '../hooks/guard.ts'
import { adrId, classify } from '../hooks/paths.ts'

test('a path is a record only inside .claude/maintainer', () => {
  expect(classify('/work/app/.claude/maintainer/decisions/ADR_2026-03-14_x.md')).toEqual({
    kind: 'adr',
    dir: '/work/app/.claude/maintainer/decisions',
    name: 'ADR_2026-03-14_x.md',
  })
  expect(classify('/work/app/.claude/maintainer/technical-debt/pending-debt.md')?.kind).toBe(
    'pending-debt',
  )
  expect(classify('C:\\work\\app\\.claude\\maintainer\\technical-debt\\closed-debt.md')?.kind).toBe(
    'closed-debt',
  )
  expect(classify('/work/app/.claude/maintainer/technical-debt/notes.md')).toBeNull()
  expect(classify('/work/app/docs/decisions/ADR_2026-03-14_x.md')).toBeNull()
  expect(classify('/work/app/.claude/maintainer/decisions/diagram.png')).toBeNull()
  expect(adrId('ADR_2026-03-14_x.md')).toBe('ADR_2026-03-14_x')
})

test('the tool input is read into camelCase fields', () => {
  expect(fileInput({ file_path: '/a.md', content: 'x' })).toEqual({ path: '/a.md', content: 'x' })
  expect(
    fileInput({ file_path: '/a.md', old_string: 'a', new_string: 'b', replace_all: true }),
  ).toEqual({
    path: '/a.md',
    oldString: 'a',
    newString: 'b',
    replaceAll: true,
  })
  expect(fileInput({ command: 'ls' })).toBeNull()
  expect(fileInput('text')).toBeNull()
  expect(fileInput(null)).toBeNull()
})

test('the saved file is computed from a Write or an Edit', () => {
  expect(resultingText({ path: '/a', content: 'new' }, 'old')).toBe('new')
  expect(resultingText({ path: '/a', oldString: 'b', newString: 'X' }, 'abcb')).toBe('aXcb')
  expect(
    resultingText({ path: '/a', oldString: 'b', newString: 'X', replaceAll: true }, 'abcb'),
  ).toBe('aXcX')
  expect(resultingText({ path: '/a', oldString: 'b', newString: '$&$1' }, 'abc')).toBe('a$&$1c')
  expect(resultingText({ path: '/a', oldString: 'zzz', newString: 'X' }, 'abc')).toBeNull()
  expect(resultingText({ path: '/a', oldString: 'a', newString: 'X' }, null)).toBeNull()
})

test('a shell command that changes the records folders is flagged, a read is not', () => {
  const flagged = [
    'rm .claude/maintainer/decisions/ADR_2026-03-14_x.md',
    'mv .claude/maintainer/technical-debt/pending-debt.md /tmp/',
    "sed -i '' 's/a/b/' .claude/maintainer/technical-debt/closed-debt.md",
    'echo done >> .claude/maintainer/technical-debt/pending-debt.md',
    'cat notes | tee .claude/maintainer/decisions/ADR_2026-03-14_x.md',
  ]
  for (const command of flagged) {
    expect(bashReason(command), command).toContain('Write tool')
  }
  const fine = [
    'cat .claude/maintainer/technical-debt/pending-debt.md',
    'ls .claude/maintainer/decisions/',
    'grep -r Postgres .claude/maintainer/',
    'rm build/output.txt',
    'git status',
  ]
  for (const command of fine) {
    expect(bashReason(command), command).toBeNull()
  }
})

test('a commit that changes dependencies, schema, CI or infrastructure carries a signal', () => {
  expect(commitSignals('Add a cache layer\npackage.json\nsrc/cache.ts')).toEqual([
    'a dependency manifest',
  ])
  expect(commitSignals('Move to a new table\ndb/migrations/001_users.sql')).toEqual([
    'a database schema or migration',
  ])
  expect(commitSignals('Speed up CI\n.github/workflows/validate.yml')).toEqual(['a CI workflow'])
  expect(commitSignals('Run in a container\nDockerfile\ninfra/main.tf')).toEqual([
    'infrastructure files',
  ])
})

test('a commit message with a warning word carries a signal, a plain commit does not', () => {
  expect(commitSignals('Temporary workaround for the export\nsrc/export.ts')).toEqual([
    'the word "Temporary" in its message',
  ])
  expect(commitSignals('Revert the retry change\nsrc/retry.ts')).toEqual([
    'the word "Revert" in its message',
  ])
  expect(commitSignals('Fix a typo in the README\nREADME.md')).toEqual([])
  expect(commitSignals('Bump deps\npackage.json\nnotes.md').length).toBe(1)
})

test('a commit that only touches the records carries no signal', () => {
  expect(
    commitSignals('Temporary notes\n.claude/maintainer/decisions/ADR_2026-03-14_x.md'),
  ).toEqual([])
  expect(commitSignals('Empty commit')).toEqual([])
})

test('the compaction note joins the instructions already given', () => {
  expect(withKeepNote(undefined)).toContain('DEBT-')
  expect(withKeepNote('  ')).toContain('DEBT-')
  expect(withKeepNote('Focus on the API').startsWith('Focus on the API\n\n')).toBe(true)
})
