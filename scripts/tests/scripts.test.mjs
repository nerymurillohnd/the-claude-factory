#!/usr/bin/env node
// End-to-end tests for the maintenance scripts. Each test runs against a fresh temp copy of the
// repository (TCF_ROOT), so the real working tree is never modified.
//   node --test "scripts/tests/*.test.mjs"

import assert from 'node:assert/strict'
import { execFileSync, spawnSync } from 'node:child_process'
import {
  cpSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve, sep } from 'node:path'
import { afterEach, beforeEach, describe, test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { lspConfigProblems, portabilityProblems, rootPackageProblems } from '../check-repo.mjs'
import { hooksFileKinds } from '../components.mjs'
import { anchor } from '../generators/catalog.mjs'
import { changelogSection } from '../lib.mjs'

const REAL_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..')
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
  const r = spawnSync(process.execPath, [join(root, 'scripts', script), ...args], {
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
 * Create a new plugin the way the repository gets one: the building-plugins skill's scaffold writes
 * plugins/<name>/, then the marketplace and catalog are regenerated. It runs the temp copy's script
 * with TCF_ROOT, so it writes into the copy.
 * @param {string} [name]
 * @param {string} [category]
 * @param {boolean} [claudeCodeOnly]
 */
function scaffold(name = 'demo-tool', category = 'productivity', claudeCodeOnly = false) {
  const script = join(root, '.claude/skills/building-plugins/scripts/scaffold-plugin.py')
  const args = ['--name', name, '--category', category, '--description', 'Does demo things.']
  const r = spawnSync(script, claudeCodeOnly ? [...args, '--claude-code-only'] : args, {
    cwd: root,
    encoding: 'utf8',
    env: { ...process.env, TCF_ROOT: root },
  })
  assert.equal(r.status, 0, `${r.stdout}${r.stderr}`)
  for (const generator of ['generators/marketplace.mjs', 'generators/catalog.mjs']) {
    const g = run(generator)
    assert.equal(g.code, 0, g.out)
  }
}

/**
 * Fill every placeholder the author fills (a `<` followed by a capital letter) with `text`,
 * nested ones included.
 * @param {string} name
 * @param {string} [text]
 */
function resolvePlaceholders(name, text = 'x') {
  const p = `plugins/${name}/README.md`
  let readme = read(p)
  while (/<[A-Z][^>]*>/.test(readme)) {
    readme = readme.replace(/<[A-Z][^>]*>/g, text)
  }
  write(p, readme)
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

/** Simulate a maintainer finishing the plugin: add one skill, fill the placeholders, trim the Compatibility table. */
function finishPlugin(name = 'demo-tool') {
  mkdirSync(join(root, `plugins/${name}/skills/demo`), { recursive: true })
  write(
    `plugins/${name}/skills/demo/SKILL.md`,
    '---\ndescription: Demo skill. Use when testing.\n---\nDo it.\n',
  )
  resolvePlaceholders(name)
  pruneCompat(name, ['Skills'])
  assert.equal(run('generators/catalog.mjs').code, 0)
}

/** Scaffold the default plugin and finish it, so check-repo.mjs has nothing left to flag. */
function scaffoldReady() {
  scaffold()
  finishPlugin()
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

  test('fails on a freshly scaffolded plugin until its placeholders are filled', () => {
    scaffold()
    const before = run('check-repo.mjs')
    assert.equal(before.code, 1)
    assert.match(before.out, /unresolved <…> placeholders/)

    finishPlugin()
    const after = run('check-repo.mjs')
    assert.equal(after.code, 0, after.out)
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
    scaffold('lang-tool', 'language-support', true)
    mkdirSync(join(root, 'plugins/lang-tool/bin'), { recursive: true })
    write('plugins/lang-tool/bin/tool', '#!/bin/sh\necho hi\n')
    const p = 'plugins/lang-tool/README.md'
    resolvePlaceholders('lang-tool', 'it needs bin/ executables')
    pruneCompat('lang-tool', ['Executables'])
    assert.equal(run('generators/catalog.mjs').code, 0)
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
    write(p, read(p).replace(/^\| 🎯 Skills /m, '| 🤖 Agents | ✅ | ⚠️ |\n$&'))
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
})

describe('marketplace generator', () => {
  const MARKETPLACE = '.claude-plugin/marketplace.json'
  const generate = (/** @type {string[]} */ args = []) => run('generators/marketplace.mjs', args)
  /** @param {string} name */
  const manifestOf = (name) => `plugins/${name}/.claude-plugin/plugin.json`
  /**
   * @param {string} name
   * @param {(m: { name?: string, metadata: { category?: string | undefined } }) => void} change
   */
  const editManifest = (name, change) => {
    const m = json(manifestOf(name))
    change(m)
    write(manifestOf(name), `${JSON.stringify(m, null, 2)}\n`)
  }

  test('matches the committed marketplace.json', () => {
    const r = generate(['--check'])
    assert.equal(r.code, 0, r.out)
    assert.match(r.out, /marketplace\.json plugins are up to date/)
  })

  test('is idempotent', () => {
    const before = read(MARKETPLACE)
    assert.equal(generate().code, 0)
    assert.equal(read(MARKETPLACE), before)
    assert.equal(generate(['--check']).code, 0)
  })

  test('keeps the top-level fields', () => {
    const { plugins: _plugins, ...before } = json(MARKETPLACE)
    write(MARKETPLACE, `${JSON.stringify({ ...before, plugins: [] }, null, 2)}\n`)
    assert.equal(generate().code, 0)
    const { plugins, ...after } = json(MARKETPLACE)
    assert.deepEqual(after, before)
    assert.deepEqual(Object.keys(after), Object.keys(before))
    assert.ok(plugins.length > 0)
  })

  test('picks up a new plugin', () => {
    cpSync(join(root, 'plugins/block-no-verify'), join(root, 'plugins/zz-demo'), {
      recursive: true,
    })
    editManifest('zz-demo', (m) => {
      m.name = 'zz-demo'
    })
    assert.equal(generate(['--check']).code, 1)
    assert.equal(generate().code, 0)
    const entries = json(MARKETPLACE).plugins
    assert.deepEqual(entries.at(-1), {
      name: 'zz-demo',
      source: './plugins/zz-demo',
      description: json(manifestOf('zz-demo')).description,
      category: 'security',
    })
  })

  test('fails on a plugin directory without a manifest', () => {
    const before = read(MARKETPLACE)
    mkdirSync(join(root, 'plugins/empty'))
    const r = generate()
    assert.equal(r.code, 1)
    assert.match(r.out, /plugins\/empty: \.claude-plugin\/plugin\.json is missing/)
    assert.equal(read(MARKETPLACE), before)
  })

  test('fails on a missing or unknown category', () => {
    editManifest('block-no-verify', (m) => {
      m.metadata.category = undefined // JSON.stringify drops the key
    })
    let r = generate()
    assert.equal(r.code, 1)
    assert.match(r.out, /plugins\/block-no-verify: metadata\.category is required/)
    editManifest('block-no-verify', (m) => {
      m.metadata.category = 'nope'
    })
    r = generate()
    assert.equal(r.code, 1)
    assert.match(r.out, /metadata\.category "nope" is not in categories\.json/)
  })

  test('fails when the manifest name differs from its directory', () => {
    editManifest('block-no-verify', (m) => {
      m.name = 'x'
    })
    const r = generate()
    assert.equal(r.code, 1)
    assert.match(r.out, /plugins\/block-no-verify: name "x" does not match its directory/)
  })

  test('names the plugin whose manifest is not valid JSON, and keeps collecting', () => {
    write(manifestOf('block-no-verify'), '{ broken')
    editManifest('tool-ledger', (m) => {
      m.name = 'x'
    })
    const r = generate()
    assert.equal(r.code, 1)
    assert.match(r.out, /plugins\/block-no-verify: \.claude-plugin\/plugin\.json is not valid JSON/)
    assert.match(r.out, /plugins\/tool-ledger: name "x" does not match its directory/)
  })

  test('ignores plain files in plugins/', () => {
    write('plugins/.DS_Store', 'x')
    assert.equal(generate(['--check']).code, 0)
  })

  test('fails on a symlink in plugins/', () => {
    symlinkSync(join(root, 'plugins/block-no-verify'), join(root, 'plugins/linked'))
    const r = generate()
    assert.equal(r.code, 1)
    assert.match(r.out, /plugins\/linked: must be a directory, not a symlink/)
  })
})

describe('catalog generator', () => {
  test('is idempotent', () => {
    const before = read('README.md')
    const r = run('generators/catalog.mjs')
    assert.equal(r.code, 0, r.out)
    assert.equal(read('README.md'), before)
    assert.equal(run('generators/catalog.mjs', ['--check']).code, 0)
  })
  test('--check flags a stale README catalog', () => {
    write('README.md', read('README.md').replace(/block-no-verify@the-claude-factory/, 'stale'))
    const r = run('generators/catalog.mjs', ['--check'])
    assert.equal(r.code, 1)
    assert.match(r.out, /catalog is out of date/)
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

  /**
   * Commit a shipped change with `version` written by hand in plugin.json and its CHANGELOG.
   * @param {string} version
   */
  function commitVersion(version) {
    scaffold()
    initRepo()
    mkdirSync(join(root, 'plugins/demo-tool/skills/demo'), { recursive: true })
    write('plugins/demo-tool/skills/demo/SKILL.md', '---\ndescription: Demo.\n---\nDo it.\n')
    const manifest = 'plugins/demo-tool/.claude-plugin/plugin.json'
    write(manifest, read(manifest).replace('"version": "0.1.0"', `"version": "${version}"`))
    const changelog = 'plugins/demo-tool/CHANGELOG.md'
    write(
      changelog,
      read(changelog).replace(
        '## [Unreleased]\n',
        `## [Unreleased]\n\n## [${version}] - 2026-10-26\n\n### Added\n\n- Demo skill.\n`,
      ),
    )
    git('add', '-A')
    git('commit', '-qm', 'change')
  }

  test('fails a bump that skips a version', () => {
    commitVersion('0.3.0')
    const r = run('check-version-bump.mjs', ['HEAD~1'])
    assert.equal(r.code, 1)
    assert.match(
      r.out,
      /version jumps from 0\.1\.0 to 0\.3\.0; one step above 0\.1\.0 is 0\.1\.1, 0\.2\.0, 1\.0\.0/,
    )
  })

  test('passes the promotion to 1.0.0 with a note that it needs authorization', () => {
    commitVersion('1.0.0')
    const r = run('check-version-bump.mjs', ['HEAD~1'])
    assert.equal(r.code, 0, r.out)
    assert.match(r.out, /0\.1\.0 → 1\.0\.0 promises a stable interface/)
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

  test('flag lifecycle scripts, which npm runs on its own', () => {
    for (const name of ['postinstall', 'prepare', 'pregates', 'postgates']) {
      assert.match(
        rootPackageProblems({ ...pkg, scripts: { [name]: 'node x.mjs' } }, '26.12.1').join('\n'),
        new RegExp(`script "${name}" runs on its own`),
        name,
      )
    }
    assert.deepEqual(
      rootPackageProblems(
        { ...pkg, scripts: { gates: 'node .github/scripts/gates.mjs' } },
        '26.12.1',
      ),
      [],
    )
  })

  test('flag a package without "private": true', () => {
    const { private: _ignored, ...open } = pkg
    assert.match(rootPackageProblems(open, '26.12.1').join('\n'), /"private": true/)
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

describe('component detection', () => {
  test('hooks.json counts settings hooks under hooks and a mod under modules', () => {
    assert.deepEqual(hooksFileKinds('{"hooks": {}}'), { hooks: true, mods: false })
    assert.deepEqual(hooksFileKinds('{"modules": ["./register.ts"]}'), { hooks: false, mods: true })
    assert.deepEqual(hooksFileKinds('{"modules": ["./r.ts"], "hooks": {}}'), {
      hooks: true,
      mods: true,
    })
    assert.deepEqual(hooksFileKinds('{"description": "x"}'), { hooks: false, mods: false })
  })

  test('a hooks.json that is not a JSON object counts as settings hooks', () => {
    assert.deepEqual(hooksFileKinds('{ not json'), { hooks: true, mods: false })
    assert.deepEqual(hooksFileKinds('[]'), { hooks: true, mods: false })
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
