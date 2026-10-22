import { expect, test } from 'claude-code/testing'

import { parseCommand, splitWords, touchesOf } from '../hooks/activity.ts'
import { readMessage, thumbOf } from '../hooks/body.ts'
import { nextStop, parseDiff } from '../hooks/diff.ts'
import { clip, formatAge, formatDate, formatSize } from '../hooks/format.ts'
import {
  countsText,
  headText,
  linesText,
  parseNumstat,
  parseStatus,
  parseWc,
  rollUp,
} from '../hooks/git.ts'
import { decideGlyphs, iconFor, isNerdFontFile } from '../hooks/glyphs.ts'
import type { Host } from '../hooks/launch.ts'
import {
  canEdit,
  defaultAppPlan,
  diffToolPlan,
  editPlan,
  fillTemplate,
  herdrClicksWork,
  herdrVersionOf,
  NO_TERMINAL,
  nvimPaneOf,
  nvimReuseSteps,
  openPlan,
  platformOf,
  vimEscape,
} from '../hooks/launch.ts'
import {
  BACKGROUNDS,
  contrast,
  isLightTheme,
  LIGHT,
  LIGHT_BACKGROUND,
  parsePalette,
  TONES,
} from '../hooks/palette.ts'
import { filterDrivers, gitArgv } from '../hooks/register.tsx'
import { searchPaths } from '../hooks/search.ts'
import type { Entry } from '../hooks/tree.ts'
import {
  ancestorsOf,
  clampOffset,
  compareNames,
  flatten,
  maxOffset,
  parseIgnore,
  relativeTo,
  revealOffset,
  withGhosts,
} from '../hooks/tree.ts'

const file = (name: string, size = 1): Entry => ({
  name,
  kind: 'file',
  size,
  mtimeMs: 1,
  isGhost: false,
})
const dir = (name: string): Entry => ({ name, kind: 'dir', size: 0, mtimeMs: 0, isGhost: false })

test('names sort folders first, then in natural order', () => {
  expect(compareNames('file2', 'file10')).toBeLessThan(0)
  expect(compareNames('B', 'a')).toBeGreaterThan(0)
  const listings = new Map([['', [file('z.ts'), dir('src'), file('a10.md'), file('a2.md')]]])
  expect(flatten(listings, new Set(), parseIgnore('')).map((row) => row.name)).toEqual([
    'src',
    'a2.md',
    'a10.md',
    'z.ts',
  ])
})

test('expanded folders open in place and Ignore names leave at any depth', () => {
  const listings = new Map<string, Entry[]>([
    ['', [dir('src'), dir('node_modules'), file('README.md')]],
    ['src', [file('main.ts'), dir('.cache')]],
  ])
  const rows = flatten(listings, new Set(['src']), parseIgnore('.cache, tmp'))
  expect(rows.map((row) => `${row.depth}:${row.path}`)).toEqual([
    '0:src',
    '1:src/main.ts',
    '0:README.md',
  ])
  expect(rows[0]?.isExpanded).toBe(true)
})

test('paths compare under a root on POSIX and Windows spellings', () => {
  expect(relativeTo('/work/src/a.ts', '/work')).toBe('src/a.ts')
  expect(relativeTo('/work', '/work')).toBe('')
  expect(relativeTo('/workshop/a.ts', '/work')).toBeNull()
  expect(relativeTo('C:\\Repo\\src\\a.ts', 'c:/repo')).toBe('src/a.ts')
  expect(ancestorsOf('a/b/c.ts')).toEqual(['a', 'a/b'])
})

test('a deleted file still shows, once, in its folder', () => {
  const entries = withGhosts('src', [file('kept.ts')], ['src/gone.ts', 'other/x.ts', 'src/kept.ts'])
  expect(entries.map((entry) => `${entry.name}:${entry.isGhost}`)).toEqual([
    'kept.ts:false',
    'gone.ts:true',
  ])
})

test('the list offset reaches the last row and never past it', () => {
  expect(maxOffset(100, 10)).toBe(90)
  expect(clampOffset(500, 100, 10)).toBe(90)
  expect(clampOffset(-3, 100, 10)).toBe(0)
  expect(revealOffset(95, 0, 100, 10)).toBe(86)
  expect(revealOffset(3, 50, 100, 10)).toBe(3)
  expect(revealOffset(55, 50, 100, 10)).toBe(50)
})

test('ages and dates take a few characters', () => {
  const now = new Date(2026, 9, 22, 12, 0).getTime()
  expect(formatAge(now - 20_000, now)).toBe('now')
  expect(formatAge(now - 12 * 60_000, now)).toBe('12m')
  expect(formatAge(now - 3 * 3_600_000, now)).toBe('3h')
  expect(formatAge(now - 5 * 86_400_000, now)).toBe('5d')
  expect(formatAge(new Date(2026, 9, 9).getTime(), now)).toBe('Oct 9')
  expect(formatAge(new Date(2025, 1, 1).getTime(), now)).toBe('2025')
  expect(formatDate(new Date(2026, 9, 9, 14, 2).getTime(), now)).toBe('Oct 09 14:02')
  expect(formatDate(new Date(2025, 9, 9).getTime(), now)).toBe('2025-10-09')
  expect(formatSize(512)).toBe('512B')
  expect(formatSize(1536)).toBe('1.5K')
  expect(formatSize(34 * 1024)).toBe('34K')
  expect(clip('abcdef', 4)).toBe('abc…')
})

test('git status reads statuses, renames, branch and upstream under the root', () => {
  const output = [
    '# branch.oid 0123456789abcdef',
    '# branch.head main',
    '# branch.upstream origin/main',
    '# branch.ab +2 -1',
    '1 .M N... 100644 100644 100644 aaa bbb app/src/a b.ts',
    '2 R. N... 100644 100644 100644 aaa bbb R100 app/new.ts',
    'app/old.ts',
    '1 .D N... 100644 100644 000000 aaa bbb app/gone.ts',
    '? app/notes.md',
    '? other/outside.md',
    '',
  ].join('\0')
  const { head, files } = parseStatus(output, 'app/')
  expect(headText(head)).toBe('main → origin/main ↑2 ↓1')
  expect([...files.keys()]).toEqual(['src/a b.ts', 'new.ts', 'gone.ts', 'notes.md'])
  expect(files.get('new.ts')?.code).toBe('renamed')
  expect(files.get('gone.ts')?.code).toBe('deleted')
  const folders = rollUp(files)
  expect(countsText(folders.get(''))).toBe('?:1 M:2 D:1')
  expect(countsText(folders.get('src'))).toBe('M:1')
})

test('the header names a new repository, a detached HEAD and a missing upstream', () => {
  expect(headText({ branch: 'main', oid: null, upstream: null, ahead: 0, behind: 0 })).toBe(
    'main · no commits yet',
  )
  expect(headText({ branch: null, oid: 'abcdef1234', upstream: null, ahead: 0, behind: 0 })).toBe(
    'HEAD abcdef1',
  )
  expect(headText({ branch: 'dev', oid: 'abc', upstream: null, ahead: 0, behind: 0 })).toBe(
    'dev · no upstream',
  )
})

test('numstat and wc give line counts, binary files none', () => {
  const counts = parseNumstat(
    ['3\t1\tsrc/a.ts', '-\t-\timg.png', '5\t0\t', 'old.ts', 'new.ts', ''].join('\0'),
  )
  expect(counts.get('src/a.ts')).toEqual({ added: 3, removed: 1 })
  expect(counts.get('img.png')).toEqual({ added: null, removed: null })
  expect(counts.get('new.ts')).toEqual({ added: 5, removed: 0 })
  expect(linesText({ code: 'modified', added: 3, removed: 1 })).toBe('+3 -1')
  expect(linesText({ code: 'modified', added: 0, removed: 2 })).toBe('-2')
  expect(parseWc('  10 a.ts\n   2 dir/b c.md\n  12 total\n')).toEqual(
    new Map([
      ['a.ts', 10],
      ['dir/b c.md', 2],
    ]),
  )
})

test('tool calls name what they read and write', () => {
  expect(touchesOf('Read', { file_path: '/w/a.ts' })).toEqual({
    reads: ['/w/a.ts'],
    writes: [],
    ops: [],
  })
  expect(touchesOf('Edit', { file_path: '/w/a.ts' }).writes).toEqual(['/w/a.ts'])
  expect(touchesOf('NotebookEdit', { notebook_path: 'n.ipynb' }).writes).toEqual(['n.ipynb'])
  expect(touchesOf('Grep', { pattern: 'x', path: 'src' }).reads).toEqual(['src'])
  const shell = parseCommand(
    'cat "a b.txt" | grep -n foo src/x.ts && rg needle lib > out.log; sed -i s/a/b/ c.ts',
  )
  expect(shell.reads).toEqual(['a b.txt', 'src/x.ts', 'lib'])
  expect(shell.writes).toEqual(['out.log', 'c.ts'])
})

test('shell commands name their git and gh operations', () => {
  const ops = parseCommand(
    'git add -A && git -C repo commit -m "x" && git push origin main; gh pr create --fill',
  ).ops
  expect(ops).toEqual([
    { tool: 'git', name: 'commit' },
    { tool: 'git', name: 'push' },
    { tool: 'gh', name: 'pr create' },
  ])
  expect(parseCommand('git status').ops).toEqual([])
  expect(splitWords(`a 'b c' "d \\" e" f\\ g`)).toEqual(['a', 'b c', 'd " e', 'f g'])
})

test('a diff reads into rows with line numbers, files and hunks', () => {
  const text = [
    'diff --git a/a.ts b/a.ts',
    'index 1..2 100644',
    '--- a/a.ts',
    '+++ b/a.ts',
    '@@ -1,2 +1,2 @@',
    ' keep',
    '-old',
    '+new',
    '@@ -10,1 +10,2 @@ fn',
    ' ten',
    '+eleven',
    'diff --git a/b.ts b/b.ts',
    'Binary files a/b.ts and b/b.ts differ',
  ].join('\n')
  const parsed = parseDiff(text)
  expect(parsed.rows.map((row) => `${row.kind}:${row.line ?? ''}:${row.text}`)).toEqual([
    'file::a.ts',
    'hunk::@@ -1,2 +1,2 @@',
    'ctx:1:keep',
    'del:2:old',
    'add:2:new',
    'hunk::@@ -10,1 +10,2 @@ fn',
    'ctx:10:ten',
    'add:11:eleven',
    'file::b.ts',
    'note::Binary file changed',
  ])
  expect(parsed.files).toEqual([0, 8])
  expect(nextStop(parsed.hunks, 1, 1)).toBe(5)
  expect(nextStop(parsed.hunks, 5, -1)).toBe(1)
  expect(nextStop(parsed.hunks, 5, 1)).toBe(5)
})

test('every light palette text color reaches WCAG AAA on every background it is drawn on', () => {
  const backgrounds = [LIGHT_BACKGROUND, LIGHT.selected, LIGHT.hovered]
  for (const tone of TONES.filter((t) => !BACKGROUNDS.includes(t))) {
    for (const background of backgrounds) {
      expect(contrast(LIGHT[tone], background)).toBeGreaterThanOrEqual(7)
    }
  }
  expect(isLightTheme('light-daltonized')).toBe(true)
  expect(isLightTheme('dark')).toBe(false)
})

test('the Palette setting lays colors over the theme and reports what it ignores', () => {
  expect(parsePalette('read=#112233, write=#445566 nope=#000000 deleted=red')).toEqual({
    colors: { read: '#112233', write: '#445566' },
    problems: ['nope=#000000', 'deleted=red'],
  })
})

test('auto glyphs use a Nerd Font only where one is sure to draw', () => {
  const base = {
    setting: 'auto',
    surface: 'terminal',
    isSsh: false,
    nerdFonts: [],
    terminalStartedAt: 1000,
  } as const
  expect(decideGlyphs(base)).toBe('plain')
  expect(decideGlyphs({ ...base, nerdFonts: [500] })).toBe('nerd')
  expect(decideGlyphs({ ...base, nerdFonts: [5000] })).toBe('plain')
  expect(decideGlyphs({ ...base, surface: 'desktop', nerdFonts: [500] })).toBe('plain')
  expect(decideGlyphs({ ...base, isSsh: true })).toBe('nerd')
  expect(decideGlyphs({ ...base, setting: 'nerd' })).toBe('nerd')
  expect(isNerdFontFile('JetBrainsMonoNerdFont-Regular.ttf')).toBe(true)
  expect(isNerdFontFile('MesloLGS NF Regular.ttf')).toBe(true)
  expect(isNerdFontFile('Hack Regular Nerd Font Complete.otf')).toBe(true)
  expect(isNerdFontFile('Menlo.ttc')).toBe(false)
  expect(iconFor('src', 'dir', false, 'plain')).toBe('▸ ')
  expect(iconFor('a.ts', 'file', false, 'nerd')).toBe('\u{e628} ')
})

const mac: Host = { platform: 'darwin', isTmux: false, herdrPane: null, editor: 'nvim' }

test('files open with the default app of each platform, never through a shell', () => {
  expect(defaultAppPlan(mac, '/w/a b.pdf')).toEqual({ kind: 'run', argv: ['open', '/w/a b.pdf'] })
  expect(defaultAppPlan({ ...mac, platform: 'linux' }, '/w/a')).toEqual({
    kind: 'run',
    argv: ['xdg-open', '/w/a'],
  })
  const windows = defaultAppPlan({ ...mac, platform: 'windows' }, 'C:/w/a&b.txt')
  expect(windows.argv.join(' ')).not.toContain('a&b')
  expect(windows.env).toEqual({ FTP_FILE: 'C:/w/a&b.txt' })
  expect(platformOf('MINGW64_NT-10.0-19045')).toBe('windows')
  expect(platformOf('Darwin\n')).toBe('darwin')
})

test('templates fill path and line as whole words', () => {
  expect(fillTemplate('code -g {path}:{line}', '/w/a b.ts', 7)).toEqual([
    'code',
    '-g',
    '/w/a b.ts:7',
  ])
  expect(fillTemplate('zed', '/w/a.ts', 1)).toEqual(['zed', '/w/a.ts'])
  expect(openPlan(mac, 'subl -n', '/w/a.ts')).toEqual({
    kind: 'run',
    argv: ['subl', '-n', '/w/a.ts'],
    cwd: '/w',
  })
})

test('a terminal editor runs in tmux, in a herdr pane, or not at all', () => {
  expect(openPlan(mac, 'editor', '/w/a.ts')).toEqual({ kind: 'notice', text: NO_TERMINAL })
  expect(canEdit(mac, '')).toBe(false)
  expect(canEdit(mac, 'code -g {path}:{line}')).toBe(true)
  expect(editPlan({ ...mac, isTmux: true }, '', '/w/a.ts', 12)).toEqual({
    kind: 'tmux-editor',
    editor: ['nvim'],
    file: '/w/a.ts',
    line: 12,
    dir: '/w',
  })
  const herdr = editPlan({ ...mac, herdrPane: 'p3' }, '', '/w/my file.ts', 4)
  expect(herdr).toEqual({
    kind: 'herdr',
    split: [
      'herdr',
      'pane',
      'split',
      'p3',
      '--direction',
      'right',
      '--cwd',
      '/w',
      '--env',
      'FTP_FILE=/w/my file.ts',
      '--focus',
    ],
    command: 'nvim +4 "$FTP_FILE"; exit',
  })
  expect(diffToolPlan({ ...mac, isTmux: true }, 'hunk diff --', 'src/a.ts', '/w')).toEqual({
    kind: 'run',
    argv: ['tmux', 'new-window', '-c', '/w', '--', 'hunk', 'diff', '--', 'src/a.ts'],
  })
  expect(diffToolPlan({ ...mac, platform: 'linux' }, 'lazygit -f', 'a', '/w')).toEqual({
    kind: 'run',
    argv: ['xdg-terminal-exec', 'lazygit', '-f', 'a'],
    cwd: '/w',
  })
})

test('a running nvim takes the file in place', () => {
  expect(nvimPaneOf('%1 zsh\n%4 nvim\n')).toBe('%4')
  expect(nvimPaneOf('%1 zsh\n')).toBeNull()
  expect(vimEscape('/w/a b%#.ts')).toBe('/w/a\\ b\\%\\#.ts')
  expect(nvimReuseSteps('%4', '/w/a.ts', 3)?.[1]).toEqual([
    'tmux',
    'send-keys',
    '-t',
    '%4',
    '-l',
    ':edit +3 /w/a.ts',
  ])
})

test('herdr before 0.9.1 keeps the mouse off the rows', () => {
  expect(herdrClicksWork(herdrVersionOf('herdr 0.9.0'))).toBe(false)
  expect(herdrClicksWork(herdrVersionOf('herdr 0.9.1'))).toBe(true)
  expect(herdrClicksWork(herdrVersionOf('herdr 1.0.0'))).toBe(true)
})

test('search ranks names that start with the query first', () => {
  const paths = ['docs/readme-notes.md', 'README.md', 'src/lib/reader.ts', 'tests/thread.ts']
  expect(searchPaths(paths, 'read', 10)).toEqual([
    'README.md',
    'src/lib/reader.ts',
    'docs/readme-notes.md',
    'tests/thread.ts',
  ])
  expect(searchPaths(paths, '  ', 10)).toEqual([])
})

test('the scrollbar thumb spans the window and reaches the bottom', () => {
  expect(thumbOf(0, 5, 10)).toBeNull()
  expect(thumbOf(0, 100, 10)).toEqual({ start: 0, end: 1 })
  expect(thumbOf(90, 100, 10)).toEqual({ start: 9, end: 10 })
})

test('posts from the surface module are checked field by field', () => {
  expect(readMessage({ type: 'click', index: 3 })).toEqual({ type: 'click', index: 3 })
  expect(readMessage({ type: 'click', index: -1 })).toBeNull()
  expect(readMessage({ type: 'scrollTo', ratio: 2 })).toBeNull()
  expect(readMessage({ type: 'key', key: 'j' })).toEqual({
    type: 'key',
    key: 'j',
    ctrl: false,
    shift: false,
  })
  expect(readMessage('nope')).toBeNull()
})

test('a name holding a control character is never typed into a running editor', () => {
  expect(nvimReuseSteps('%4', '/w/a\n:!touch pwned\n.ts', 1)).toBeNull()
  expect(nvimReuseSteps('%4', '/w/a\u001b.ts', 1)).toBeNull()
})

test('filter drivers are read from git config, and a name -c cannot blank stops git', () => {
  expect(
    filterDrivers(
      'filter.lfs.clean git-lfs clean -- %f\nfilter.lfs.smudge x\nfilter.my.drv.process y\n',
    ),
  ).toEqual(['lfs', 'my.drv'])
  expect(filterDrivers('')).toEqual([])
  expect(filterDrivers('filter.a=b.clean evil\n')).toBeNull()
  expect(gitArgv(['status'], ['lfs'])).toEqual([
    'git',
    '-c',
    'core.fsmonitor=false',
    '-c',
    'filter.lfs.clean=',
    '-c',
    'filter.lfs.smudge=',
    '-c',
    'filter.lfs.process=',
    '-c',
    'filter.lfs.required=false',
    'status',
  ])
  expect(gitArgv(['log', '-1'])).toEqual([
    'git',
    '-c',
    'core.fsmonitor=false',
    'log',
    '--no-show-signature',
    '-1',
  ])
})
