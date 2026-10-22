#!/usr/bin/env node
// End-to-end tests for the maintenance scripts. Each test runs against a fresh temp copy of the
// repository (TCF_ROOT), so the real working tree is never modified.
//   node --test ".github/scripts/tests/*.test.mjs"

import assert from 'node:assert/strict'
import { execFileSync, spawnSync } from 'node:child_process'
import {
  cpSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve, sep } from 'node:path'
import { afterEach, beforeEach, describe, test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { anchor } from '../catalog.mjs'
import { lspConfigProblems, portabilityProblems, rootPackageProblems } from '../check-repo.mjs'
import { changelogSection } from '../lib.mjs'

const REAL_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..')
/** @type {string} */
let root

// The files a clone would hold: tracked plus new untracked ones, never git-ignored ones (such as a
// local .DS_Store), so the copy matches what CI checks out.
const CLONE_FILES = new Set(
  execFileSync('git', ['-C', REAL_ROOT, 'ls-files', '-co', '--exclude-standard', '-z'], {
    encoding: 'utf8',
  })
    .split('\0')
    .filter(Boolean),
)
const CLONE_DIRS = new Set(
  [...CLONE_FILES].flatMap((f) =>
    f
      .split('/')
      .slice(0, -1)
      .map((_, i, a) => a.slice(0, i + 1).join('/')),
  ),
)

function copyRepo() {
  const dir = mkdtempSync(join(tmpdir(), 'tcf-'))
  cpSync(REAL_ROOT, dir, {
    recursive: true,
    filter: (src) => {
      const rel = src
        .slice(REAL_ROOT.length + 1)
        .split(sep)
        .join('/')
      return rel === '' || CLONE_FILES.has(rel) || CLONE_DIRS.has(rel)
    },
  })
  return dir
}

/**
 * Run a script from the temp copy, so its own lib.mjs resolves ROOT to the temp copy.
 * @param {string} script
 * @param {string[]} [args]
 * @returns {{ code: number | null, out: string }}
 */
function run(script, args = []) {
  const r = spawnSync(process.execPath, [join(root, '.github', 'scripts', script), ...args], {
    cwd: root,
    encoding: 'utf8',
    env: { ...process.env, TCF_ROOT: root },
  })
  return { code: r.status, out: `${r.stdout}${r.stderr}` }
}

/** @param {string} p */
const read = (p) => readFileSync(join(root, p), 'utf8')
/**
 * @param {string} p
 * @param {string} s
 */
const write = (p, s) => writeFileSync(join(root, p), s)
/** @param {string} p */
const json = (p) => JSON.parse(read(p))

/** @param {...string} args */
const git = (...args) => execFileSync('git', args, { cwd: root, encoding: 'utf8' })

/**
 * Make the temp copy a git repository with one commit of everything in it.
 * @param {boolean} [withOrigin] also point refs/remotes/origin/main at that commit
 */
function initRepo(withOrigin = false) {
  git('init', '-q', '-b', 'main')
  git('config', 'user.email', 'test@example.com')
  git('config', 'user.name', 'Test')
  git('add', '-A')
  git('commit', '-qm', 'base')
  if (withOrigin) {
    git('update-ref', 'refs/remotes/origin/main', 'HEAD')
  }
}

/**
 * @param {string} [name]
 * @param {string} [category]
 * @param {string[]} [extra]
 */
function scaffold(name = 'demo-tool', category = 'productivity', extra = []) {
  const r = run('new-plugin.mjs', [
    '--name',
    name,
    '--category',
    category,
    '--description',
    'Does demo things.',
    ...extra,
  ])
  assert.equal(r.code, 0, r.out)
}

/**
 * Keep only the Compatibility rows whose text contains one of `keep`.
 * @param {string} name
 * @param {string[]} keep
 */
function pruneCompat(name, keep) {
  const p = `plugins/${name}/README.md`
  const text = read(p)
  const start = text.search(/^## .*Compatibility/m)
  const end = text.indexOf('\n## ', start + 1)
  const section = text
    .slice(start, end)
    .split('\n')
    .filter(
      (l) =>
        !l.startsWith('| ') || /^\| (Component|:--)/.test(l) || keep.some((k) => l.includes(k)),
    )
    .join('\n')
  write(p, text.slice(0, start) + section + text.slice(end))
}

/** Simulate a maintainer finishing the plugin: add one skill, resolve TODOs, trim the Compatibility table. */
function resolveTodos(name = 'demo-tool') {
  mkdirSync(join(root, `plugins/${name}/skills/demo`), { recursive: true })
  write(
    `plugins/${name}/skills/demo/SKILL.md`,
    '---\ndescription: Demo skill. Use when testing.\n---\nDo it.\n',
  )
  const p = `plugins/${name}/README.md`
  write(p, read(p).replace(/<!--\s*(TODO|TEMPLATE)[\s\S]*?-->\n?/g, ''))
  pruneCompat(name, ['Skills'])
  assert.equal(run('catalog.mjs').code, 0)
}

/** Scaffold the default plugin and finish it, so check-repo.mjs has nothing left to flag. */
function scaffoldReady() {
  scaffold()
  resolveTodos()
}

beforeEach(() => {
  root = copyRepo()
})
afterEach(() => {
  rmSync(root, { recursive: true, force: true })
})

describe('check-repo', () => {
  test('passes on the pristine repository', () => {
    const r = run('check-repo.mjs')
    assert.equal(r.code, 0, r.out)
  })

  test('fails on a freshly scaffolded plugin until its TODOs are resolved', () => {
    scaffold()
    const before = run('check-repo.mjs')
    assert.equal(before.code, 1)
    assert.match(before.out, /unresolved TODO\/TEMPLATE comments/)

    resolveTodos()
    const after = run('check-repo.mjs')
    assert.equal(after.code, 0, after.out)
  })

  test('flags a plugin directory missing from marketplace.json', () => {
    mkdirSync(join(root, 'plugins', 'orphan', '.claude-plugin'), { recursive: true })
    const r = run('check-repo.mjs')
    assert.equal(r.code, 1)
    assert.match(r.out, /plugins\/orphan.*not listed/)
  })

  test('flags a root package.json that declares runtime dependencies', () => {
    const pkg = json('package.json')
    pkg.dependencies = { lodash: '4.17.21' }
    write('package.json', `${JSON.stringify(pkg, null, 2)}\n`)
    const r = run('check-repo.mjs')
    assert.equal(r.code, 1)
    assert.match(r.out, /\[package\.json\] must not declare "dependencies"/)
  })

  test('flags a version on the marketplace itself', () => {
    const mp = json('.claude-plugin/marketplace.json')
    mp.version = '0.3.0'
    write('.claude-plugin/marketplace.json', `${JSON.stringify(mp, null, 2)}\n`)
    const r = run('check-repo.mjs')
    assert.equal(r.code, 1)
    assert.match(r.out, /marketplace carries no version/)
  })

  test('flags a version on the marketplace entry', () => {
    scaffoldReady()
    const mp = json('.claude-plugin/marketplace.json')
    mp.plugins[0].version = '9.9.9'
    write('.claude-plugin/marketplace.json', `${JSON.stringify(mp, null, 2)}\n`)
    const r = run('check-repo.mjs')
    assert.equal(r.code, 1)
    assert.match(r.out, /do not set version on the entry/)
  })

  test('flags a manifest name that differs from the entry name', () => {
    scaffoldReady()
    const p = 'plugins/demo-tool/.claude-plugin/plugin.json'
    write(p, read(p).replace('"name": "demo-tool"', '"name": "other"'))
    const r = run('check-repo.mjs')
    assert.equal(r.code, 1)
    assert.match(r.out, /must equal the entry name/)
  })

  test('flags a missing required README section', () => {
    scaffoldReady()
    const p = 'plugins/demo-tool/README.md'
    write(p, read(p).replace(/^## 🧭 Compatibility$/m, '## Platforms'))
    const r = run('check-repo.mjs')
    assert.equal(r.code, 1)
    assert.match(r.out, /missing the "Compatibility" section/)
  })

  test('requires a valid metadata.surfaces declaration', () => {
    scaffoldReady()
    const p = 'plugins/demo-tool/.claude-plugin/plugin.json'
    const m = json(p)
    m.metadata.surfaces = ['claude-app']
    write(p, `${JSON.stringify(m, null, 2)}\n`)
    const r = run('check-repo.mjs')
    assert.equal(r.code, 1)
    assert.match(r.out, /metadata\.surfaces must be one of/)
  })

  test('rejects the retired cowork surface value', () => {
    scaffoldReady()
    const p = 'plugins/demo-tool/.claude-plugin/plugin.json'
    const m = json(p)
    assert.deepEqual(m.metadata.surfaces, ['claude-code', 'claude-app'])
    assert.match(
      read('plugins/demo-tool/README.md'),
      /works%20in-Claude%20Code%20%C2%B7%20Claude%20app-/,
    )
    m.metadata.surfaces = ['claude-code', 'cowork']
    write(p, `${JSON.stringify(m, null, 2)}\n`)
    const r = run('check-repo.mjs')
    assert.equal(r.code, 1)
    assert.match(r.out, /metadata\.surfaces must be one of: \["claude-code","claude-app"\]/)
  })

  test('a bin/ plugin must be declared Claude Code-only', () => {
    scaffoldReady()
    mkdirSync(join(root, 'plugins/demo-tool/bin'), { recursive: true })
    write('plugins/demo-tool/bin/tool', '#!/bin/sh\necho hi\n')
    const r = run('check-repo.mjs')
    assert.equal(r.code, 1)
    assert.match(r.out, /bin\/, which makes the Claude app refuse the plugin/)
    assert.match(r.out, /no row for Executables/)
  })

  test('a Claude Code-only plugin passes when declared everywhere', () => {
    scaffold('lang-tool', 'language-support', ['--claude-code-only'])
    mkdirSync(join(root, 'plugins/lang-tool/bin'), { recursive: true })
    write('plugins/lang-tool/bin/tool', '#!/bin/sh\necho hi\n')
    const p = 'plugins/lang-tool/README.md'
    write(p, read(p).replace(/<!--\s*(TODO|TEMPLATE)[\s\S]*?-->\n?/g, 'it needs bin/ executables'))
    pruneCompat('lang-tool', ['Executables'])
    assert.equal(run('catalog.mjs').code, 0)
    assert.deepEqual(json('plugins/lang-tool/.claude-plugin/plugin.json').metadata.surfaces, [
      'claude-code',
    ])
    assert.match(read(p), /works%20in-Claude%20Code%20only-/)
    assert.match(read('README.md'), /💻 Code only/)
    const r = run('check-repo.mjs')
    assert.equal(r.code, 0, r.out)
  })

  test('flags Compatibility rows for components the plugin does not ship', () => {
    scaffoldReady()
    const p = 'plugins/demo-tool/README.md'
    write(p, read(p).replace('| 🎯 Skills |', '| 🤖 Agents | ✅ | ⚠️ |\n| 🎯 Skills |'))
    const r = run('check-repo.mjs')
    assert.equal(r.code, 1)
    assert.match(r.out, /lists Agents, which the plugin doesn't ship/)
  })

  test('flags system files, symlinks and oversized files in a plugin', () => {
    scaffoldReady()
    write('plugins/demo-tool/.DS_Store', 'x')
    write('plugins/demo-tool/skills/big.md', 'a'.repeat(300 * 1024))
    symlinkSync('../README.md', join(root, 'plugins/demo-tool/skills/link.md'))
    const r = run('check-repo.mjs')
    assert.equal(r.code, 1)
    assert.match(r.out, /\.DS_Store is a macOS or Windows system file/)
    assert.match(r.out, /skills\/big\.md is over 256 KiB/)
    assert.match(r.out, /skills\/link\.md is a symbolic link/)
  })

  test('in a git checkout, counts tracked and new files but never git-ignored or deleted ones', () => {
    /** @param {...string} args */
    const git = (...args) => execFileSync('git', ['-C', root, ...args], { stdio: 'ignore' })
    git('init', '-q')
    write('plugins/skill-diagnostics/gone.md', 'x')
    git('add', '-A')
    rmSync(join(root, 'plugins/skill-diagnostics/gone.md'))
    write('plugins/skill-diagnostics/.DS_Store', 'x') // git-ignored: a clone never has it
    assert.equal(run('check-repo.mjs').code, 0)
    write('plugins/skill-diagnostics/desktop.ini', 'x') // new, not ignored
    const r = run('check-repo.mjs')
    assert.equal(r.code, 1)
    assert.match(r.out, /desktop\.ini is a macOS or Windows system file/)
    assert.doesNotMatch(r.out, /\.DS_Store/)
  })

  test('flags a stale README catalog', () => {
    scaffoldReady()
    write('README.md', read('README.md').replace(/demo-tool@the-claude-factory/, 'stale'))
    const r = run('check-repo.mjs')
    assert.equal(r.code, 1)
    assert.match(r.out, /catalog is out of date/)
  })
})

describe('new-plugin', () => {
  test('rejects names Claude Code reserves for Anthropic', () => {
    const r = run('new-plugin.mjs', [
      '--name',
      'claude-helper',
      '--category',
      'productivity',
      '--description',
      'x',
    ])
    assert.equal(r.code, 1)
    assert.match(r.out, /passes as an Anthropic plugin name/)
  })

  test('rejects unknown categories', () => {
    const r = run('new-plugin.mjs', [
      '--name',
      'demo-tool',
      '--category',
      'nope',
      '--description',
      'x',
    ])
    assert.equal(r.code, 1)
    assert.match(r.out, /Unknown category/)
  })

  test('registers the entry, renders templates and updates the catalog', () => {
    const before = json('.claude-plugin/marketplace.json').plugins
    scaffold()
    const mp = json('.claude-plugin/marketplace.json')
    const expected = [
      ...before,
      {
        name: 'demo-tool',
        source: './plugins/demo-tool',
        description: 'Does demo things.',
        category: 'productivity',
      },
    ].sort((a, b) => a.name.localeCompare(b.name))
    assert.deepEqual(mp.plugins, expected)
    const manifest = json('plugins/demo-tool/.claude-plugin/plugin.json')
    assert.equal(manifest.version, '0.1.0')
    assert.equal(manifest.displayName, 'Demo Tool')
    assert.doesNotMatch(read('plugins/demo-tool/README.md'), /\{\{\w+\}\}/)
    assert.ok(existsSync(join(root, 'plugins/demo-tool/LICENSE')))
    const readme = read('README.md')
    assert.match(readme, /\[\*\*Demo Tool\*\*\]\(\.\/plugins\/demo-tool#readme\)/)
    assert.match(readme, new RegExp(`plugins-${before.length + 1}-D97757`))
    assert.equal(run('catalog.mjs', ['--check']).code, 0)
  })

  test('refuses to overwrite an existing plugin', () => {
    scaffold()
    const r = run('new-plugin.mjs', [
      '--name',
      'demo-tool',
      '--category',
      'productivity',
      '--description',
      'x',
    ])
    assert.equal(r.code, 1)
    assert.match(r.out, /already exists/)
  })
})

describe('bump-version', () => {
  test('refuses to release an empty [Unreleased] section', () => {
    scaffold()
    const r = run('bump-version.mjs', ['demo-tool', 'minor'])
    assert.equal(r.code, 1)
    assert.match(r.out, /\[Unreleased\] is empty/)
  })

  test('bumps plugin.json and rolls the changelog with links', () => {
    scaffold()
    const p = 'plugins/demo-tool/CHANGELOG.md'
    write(p, read(p).replace('## [Unreleased]\n', '## [Unreleased]\n\n### Fixed\n\n- A bug.\n'))
    const r = run('bump-version.mjs', ['demo-tool', 'minor'])
    assert.equal(r.code, 0, r.out)
    assert.equal(json('plugins/demo-tool/.claude-plugin/plugin.json').version, '0.2.0')
    const log = read(p)
    assert.match(
      log,
      /## \[Unreleased\]\n\n## \[0\.2\.0\] - \d{4}-\d{2}-\d{2}\n\n### Fixed\n\n- A bug\./,
    )
    assert.match(log, /\[Unreleased\]: .*compare\/demo-tool--v0\.2\.0\.\.\.HEAD/)
    assert.match(log, /\[0\.2\.0\]: .*releases\/tag\/demo-tool--v0\.2\.0/)
    assert.match(read('README.md'), /`0\.2\.0`/)
  })

  test('refuses to bump the marketplace, which has no version', () => {
    const before = read('.claude-plugin/marketplace.json')
    const r = run('bump-version.mjs', ['marketplace', 'patch'])
    assert.notEqual(r.code, 0)
    assert.match(r.out, /marketplace has no version/)
    assert.equal(read('.claude-plugin/marketplace.json'), before)
  })

  test('release-notes prints a plugin tag and refuses the marketplace', () => {
    scaffoldReady()
    const tag = run('release-notes.mjs', ['demo-tool', '--tag'])
    assert.equal(tag.code, 0, tag.out)
    assert.equal(tag.out.trim(), 'demo-tool--v0.1.0')
    assert.notEqual(run('release-notes.mjs', ['marketplace', '--tag']).code, 0)
  })
})

describe('check-version-bump', () => {
  test('fails when shipped files change without a bump, passes after bumping', () => {
    scaffold()
    initRepo()
    mkdirSync(join(root, 'plugins/demo-tool/skills/demo'), { recursive: true })
    write('plugins/demo-tool/skills/demo/SKILL.md', '---\ndescription: Demo.\n---\nDo it.\n')
    git('add', '-A')
    git('commit', '-qm', 'change')

    const before = run('check-version-bump.mjs', ['HEAD~1'])
    assert.equal(before.code, 1)
    assert.match(before.out, /version is still 0\.1\.0/)

    const p = 'plugins/demo-tool/CHANGELOG.md'
    write(
      p,
      read(p).replace('## [Unreleased]\n', '## [Unreleased]\n\n### Added\n\n- Demo skill.\n'),
    )
    assert.equal(run('bump-version.mjs', ['demo-tool', 'minor']).code, 0)
    git('add', '-A')
    git('commit', '-qm', 'bump')
    const after = run('check-version-bump.mjs', ['HEAD~2'])
    assert.equal(after.code, 0, after.out)
  })

  test('a new plugin passes without git noise: there is no base version to compare', () => {
    initRepo()
    scaffold()
    git('add', '-A')
    git('commit', '-qm', 'new plugin')

    const r = run('check-version-bump.mjs', ['HEAD~1'])
    assert.equal(r.code, 0, r.out)
    assert.match(r.out, /Version bumps OK \(demo-tool\)/)
    assert.doesNotMatch(r.out, /fatal:/)
  })

  test('does not require a bump for README-only edits', () => {
    scaffold()
    initRepo()
    write('plugins/demo-tool/README.md', `${read('plugins/demo-tool/README.md')}\nMore docs.\n`)
    git('commit', '-qam', 'docs')
    const r = run('check-version-bump.mjs', ['HEAD~1'])
    assert.equal(r.code, 0, r.out)
  })
})

describe('version-bump-gate hook', () => {
  /**
   * Run the standalone hook script the way Claude Code does: by its path, the event on stdin.
   * @param {string} input
   */
  const hookWith = (input) => {
    const r = spawnSync(join(root, '.claude', 'hooks', 'version-bump-gate.sh'), {
      cwd: root,
      encoding: 'utf8',
      env: { ...process.env, CLAUDE_PROJECT_DIR: root },
      input,
    })
    return { code: r.status, out: `${r.stdout}${r.stderr}` }
  }
  const hook = (command = 'git push origin feat/demo') =>
    hookWith(JSON.stringify({ tool_name: 'Bash', tool_input: { command } }))
  function addSkill() {
    mkdirSync(join(root, 'plugins/demo-tool/skills/demo'), { recursive: true })
    write('plugins/demo-tool/skills/demo/SKILL.md', '---\ndescription: Demo.\n---\nDo it.\n')
    git('add', '-A')
    git('commit', '-qm', 'change')
  }

  test('denies the push while a changed plugin has no version bump', () => {
    scaffold()
    initRepo(true)
    addSkill()
    const r = hook()
    assert.equal(r.code, 0, r.out)
    const { hookSpecificOutput: out } = JSON.parse(r.out)
    assert.equal(out.hookEventName, 'PreToolUse')
    assert.equal(out.permissionDecision, 'deny')
    assert.match(out.permissionDecisionReason, /bump-version\.mjs demo-tool <level>/)
    assert.match(out.permissionDecisionReason, /major: breaking/)
  })

  test('lets the push through once the plugin is bumped', () => {
    scaffold()
    initRepo(true)
    addSkill()
    const p = 'plugins/demo-tool/CHANGELOG.md'
    write(
      p,
      read(p).replace('## [Unreleased]\n', '## [Unreleased]\n\n### Added\n\n- Demo skill.\n'),
    )
    assert.equal(run('bump-version.mjs', ['demo-tool', 'minor']).code, 0)
    git('add', '-A')
    git('commit', '-qm', 'bump')
    const r = hook()
    assert.equal(r.code, 0, r.out)
    assert.equal(r.out, '')
  })

  test('lets the push through for README-only edits', () => {
    scaffold()
    initRepo(true)
    write('plugins/demo-tool/README.md', `${read('plugins/demo-tool/README.md')}\nMore docs.\n`)
    git('commit', '-qam', 'docs')
    const r = hook()
    assert.equal(r.code, 0, r.out)
    assert.equal(r.out, '')
  })

  test('denies every spelling of a push and only a push', () => {
    scaffold()
    initRepo(true)
    addSkill()
    const denied = [
      'git push',
      'git push --force-with-lease origin feat/demo',
      'FOO=1 git -C . push origin feat/demo',
      'git status && git -c core.editor=true push',
      'npm test; git push origin main',
    ]
    for (const command of denied) {
      assert.match(hook(command).out, /"permissionDecision":"deny"/, command)
    }
    const allowed = [
      'git status',
      'git log --grep push',
      'echo $(npm root -g)',
      'echo git push',
      'gh pr view 3 --json reviews',
    ]
    for (const command of allowed) {
      assert.equal(hook(command).out, '', command)
    }
    assert.equal(hookWith('not json').out, '')
  })

  test('lets the push through when origin/main does not exist', () => {
    scaffold()
    initRepo()
    addSkill()
    const r = hook()
    assert.equal(r.code, 0, r.out)
    assert.equal(r.out, '')
  })
})

describe('eval-targets', () => {
  /** @param {string} name */
  const touchManifest = (name) => {
    const p = `plugins/${name}/.claude-plugin/plugin.json`
    write(p, `${read(p).trimEnd()}\n\n`)
  }
  /** @param {string} message */
  function commitAll(message) {
    git('add', '-A')
    git('commit', '-qm', message)
  }
  const changed = () => run('eval-targets.mjs', ['--changed', 'HEAD~1', 'HEAD'])

  test('selects only changed plugins that ship evals; plugins without evals never count', () => {
    scaffold()
    initRepo()
    touchManifest('skill-diagnostics')
    touchManifest('demo-tool')
    commitAll('both manifests')
    const r = changed()
    assert.equal(r.code, 0, r.out)
    assert.deepEqual(JSON.parse(r.out), ['skill-diagnostics'])
  })

  test('selects nothing when no manifest changed, even if other plugin files did', () => {
    initRepo()
    write(
      'plugins/skill-diagnostics/README.md',
      `${read('plugins/skill-diagnostics/README.md')}\nx\n`,
    )
    commitAll('readme')
    assert.deepEqual(JSON.parse(changed().out), [])
  })

  test('picks up a plugin once it ships evals, and leaves unchanged ones out', () => {
    scaffold()
    initRepo()
    mkdirSync(join(root, 'plugins/demo-tool/evals/case'), { recursive: true })
    write('plugins/demo-tool/evals/case/prompt.md', 'Do it.\n')
    touchManifest('demo-tool')
    commitAll('demo evals')
    assert.deepEqual(JSON.parse(changed().out), ['demo-tool'])
  })

  test('manual runs: all plugins with evals, or one that has them', () => {
    scaffold()
    // Every plugin of the repository that ships an evals/ folder, found on disk so a new suite never stales this test.
    const withEvals = readdirSync(join(REAL_ROOT, 'plugins'), { withFileTypes: true })
      .filter(
        (entry) =>
          entry.isDirectory() && existsSync(join(REAL_ROOT, 'plugins', entry.name, 'evals')),
      )
      .map((entry) => entry.name)
      .sort()
    assert.ok(withEvals.includes('skill-diagnostics'))
    assert.deepEqual(JSON.parse(run('eval-targets.mjs', ['--only', 'all']).out), withEvals)
    assert.deepEqual(JSON.parse(run('eval-targets.mjs', ['--only', 'skill-diagnostics']).out), [
      'skill-diagnostics',
    ])
    const none = run('eval-targets.mjs', ['--only', 'demo-tool'])
    assert.equal(none.code, 1)
    assert.match(none.out, /demo-tool has no evals\/ folder/)
    assert.match(run('eval-targets.mjs', ['--only', 'nope']).out, /no plugin named "nope"/)
  })
})

describe('portability rules', () => {
  /**
   * @param {string} path
   * @param {number} [size]
   * @param {boolean} [symlink]
   */
  const entry = (path, size = 10, symlink = false) => ({ path, size, symlink })

  test('flag names Windows or macOS cannot hold, and case-only duplicates', () => {
    const problems = portabilityProblems([
      entry('a:b.md'),
      entry('notes.'),
      entry('trail /x.md'),
      entry('con.md'),
      entry('docs/LPT1'),
      entry('Readme.md'),
      entry('README.md'),
      entry('__MACOSX/x'),
      entry('thumbs.db'),
    ]).join('\n')
    for (const name of ['a:b.md', 'notes.', 'trail ', 'con.md', 'LPT1']) {
      assert.ok(problems.includes(`"${name}"`), `${name} not flagged:\n${problems}`)
    }
    assert.match(problems, /README\.md and Readme\.md differ only by capitalization/)
    assert.match(problems, /__MACOSX\/x is a macOS or Windows system file/)
    assert.match(problems, /thumbs\.db is a macOS or Windows system file/)
    const both = portabilityProblems([entry('__MACOSX/a:b')]).join('\n')
    assert.match(both, /__MACOSX\/a:b is a macOS or Windows system file/)
    assert.match(both, /"a:b" in __MACOSX\/a:b is not a valid file name on Windows/)
  })

  test('size limit spares images and fonts; file count is capped at 512', () => {
    const big = 300 * 1024
    assert.deepEqual(portabilityProblems([entry('logo.png', big), entry('font.woff2', big)]), [])
    assert.equal(portabilityProblems([entry('data.json', big)]).length, 1)
    const many = Array.from({ length: 513 }, (_, i) => entry(`f${i}.md`))
    assert.match(portabilityProblems(many).join('\n'), /513 files; the limit is 512/)
    assert.deepEqual(portabilityProblems(many.slice(0, 512)), [])
  })
})

describe('lsp config rules', () => {
  test('accept a valid config and flag unknown keys, missing fields and invalid values', () => {
    assert.deepEqual(
      lspConfigProblems({
        svelte: {
          command: 'svelteserver',
          args: ['--stdio'],
          extensionToLanguage: { '.svelte': 'svelte' },
          startupTimeout: 30000,
          restartOnCrash: true,
        },
      }),
      [],
    )
    const problems = lspConfigProblems({
      a: { command: 'x', extensionToLanguage: { '.x': 'x' }, bogusKey: true },
      b: { args: [] },
      c: { command: 'x', extensionToLanguage: { '.x': 'x' }, startupTimeout: 0 },
    }).join('\n')
    assert.match(problems, /"a" has unknown key "bogusKey"/)
    assert.match(problems, /"b" is missing command/)
    assert.match(problems, /"c" has an invalid startupTimeout/)
    assert.equal(lspConfigProblems({}).length, 1)
  })
})

describe('root package.json rules', () => {
  const pkg = { private: true, devDependencies: { '@types/node': '26.6.5' } }

  test('accept the maintainer-only package', () => {
    assert.deepEqual(rootPackageProblems(pkg, '26.12.1'), [])
  })

  test('flag anything that could make it a plugin runtime', () => {
    const problems = rootPackageProblems(
      {
        dependencies: { lodash: '4.17.21' },
        main: 'index.js',
        type: 'module',
        devDependencies: { typescript: '6.0.3', '@types/node': '^26.6.5' },
      },
      '26.12.1',
    ).join('\n')
    assert.match(problems, /"private": true/)
    assert.match(problems, /must not declare "dependencies"/)
    assert.match(problems, /must not declare "main"/)
    assert.match(problems, /must not declare "type"/)
    assert.match(problems, /"typescript" is not a type package/)
    assert.match(problems, /"@types\/node" must be pinned to an exact version/)
  })

  test('flag @types/node on another major than .nvmrc', () => {
    assert.match(
      rootPackageProblems(pkg, 'v27.0.0').join('\n'),
      /@types\/node 26\.6\.5 does not match the Node major 27 of \.nvmrc/,
    )
  })

  test('flag a missing @types/node', () => {
    assert.match(
      rootPackageProblems({ private: true, devDependencies: {} }, '26.12.1').join('\n'),
      /must declare "@types\/node"/,
    )
  })
})

describe('lib', () => {
  test('changelogSection extracts one version body', () => {
    const text =
      '# C\n\n## [Unreleased]\n\n## [1.1.0] - 2026-01-02\n\n- b\n\n## [1.0.0] - 2026-01-01\n\n- a\n\n[1.1.0]: x\n'
    assert.equal(changelogSection(text, '1.1.0'), '- b')
    assert.equal(changelogSection(text, '1.0.0'), '- a')
    assert.equal(changelogSection(text, '2.0.0'), null)
  })

  test('anchor matches GitHub heading slugs, keeping emoji variation selectors', () => {
    assert.equal(anchor('⚡ Productivity'), '-productivity')
    assert.equal(anchor('🛠️ Development'), '️-development')
    assert.equal(anchor('🧪 Testing & Quality'), '-testing--quality')
  })
})
