#!/usr/bin/env node
// The maintainers' gates, in order: the one source of the commands that local runs and CI share
// (ADR_2026-10-21_gates-run-from-one-script).
//   npm run gates                    every gate, stopping at the first failure
//   npm run gates:ci -- --group <g>  the gates of one CI job, going on after a failure
//
// What CI runs (ADR_2026-10-21_ci-checks-maintainer-tooling-and-plugin-structure): our own tooling
// under scripts/ and the plugins' structure, which no user's machine changes. The plugins' behavior
// (the tests in scripts/tests/<plugin>/, claude plugin test, the mods' tsc) and the static analysis
// of plugin code run only here, before the push, because they depend on the interpreter and the
// tools of whoever installs the plugin. Those gates carry group "local".
//
// --ci changes three things and nothing else: it leaves out the "local" gates, the version-bump
// base comes from --base instead of origin/main, and the run goes on after a failure. The commands,
// their arguments, the output and the skip checks are the same in both. Keep it that way.
//
// Every gate runs without a shell, as a command and an argument list, from the repository root.
// A test skipped anywhere fails its gate: a skip means a tool is missing. A skip that is legitimate
// goes into ALLOWED_SKIPS with its reason, never into a counter.
//
// Each gate runs the tool installed on the machine by its bare name, never through npx or uvx.
// Locally that is the maintainer's install; CI installs the pins of the env block of
// validate.yml before the gates. The gates are written for macOS and Linux: without a shell,
// Windows cannot start an npm .cmd shim such as tsc.cmd.

import { spawnSync } from 'node:child_process'
import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { isMain, ROOT } from './lib.mjs'

/** The JavaScript and TypeScript extensions, ready for files the repository does not have yet. */
const JS_FAMILY = ['js', 'cjs', 'mjs', 'jsx', 'ts', 'cts', 'mts', 'tsx']

/**
 * Python under scripts/ that follows the maintainer tooling rules and never runs mypy
 * (ADR_2026-10-24_basedpyright-is-the-only-python-type-checker). mypy-scripts checks only the
 * rest, until each unit migrates on touch.
 */
const MIGRATED_PYTHON = ['scripts/schemas/', 'scripts/generators/', 'scripts/validators/']

/** Tests that may be skipped, by Node test name or unittest id, each with why. */
const ALLOWED_SKIPS = new Map(/** @type {[string, string][]} */ ([]))

/** @typedef {'local' | 'policy' | 'python' | 'claude' | 'lint'} Group */

/**
 * @typedef {object} Gate
 * @property {string} id
 * @property {Group} group the CI job that runs it; "local" runs only on the maintainer's machine
 * @property {string} title
 * @property {string} cmd
 * @property {string[]} args
 * @property {Record<string, string>} [env]
 * @property {string} [skipReason] set when the gate cannot apply here, such as no base commit
 * @property {(stdout: string) => string | null} [after] a failure message for an exit-0 run, or null
 */

/**
 * `node --test` on files, with the spec report on stdout and a TAP copy whose skips fail the gate.
 * @param {string} id
 * @param {string[]} files
 * @param {string} tapFile
 * @param {Group} [group]
 * @returns {Gate}
 */
export function nodeTestGate(id, files, tapFile, group = 'policy') {
  return {
    id,
    group,
    title: 'node --test, no skips',
    cmd: process.execPath,
    args: [
      '--test',
      '--test-reporter=spec',
      '--test-reporter-destination=stdout',
      '--test-reporter=tap',
      `--test-reporter-destination=${tapFile}`,
      ...files,
    ],
    after: () => {
      const tap = readFileSync(tapFile, 'utf8')
      const skipped = [...tap.matchAll(/^\s*ok \d+ - (.*?) # SKIP\b/gm)]
        .map((m) => m[1] ?? '')
        .filter((name) => !ALLOWED_SKIPS.has(name))
      return skipped.length === 0
        ? null
        : `${skipped.length} skipped test${skipped.length === 1 ? '' : 's'}: ${skipped.join('; ')}`
    },
  }
}

// unittest exits 0 with skips, so its result object decides: exit 4 on a skip not allowed.
const UNITTEST_RUNNER = `import sys, unittest
d, allowed = sys.argv[1], set(sys.argv[2:])
r = unittest.TextTestRunner().run(unittest.defaultTestLoader.discover(d, top_level_dir=d))
bad = [f"{t.id()} ({why})" for t, why in r.skipped if t.id() not in allowed]
if bad:
    print("skipped: " + "; ".join(bad))
    sys.exit(4)
sys.exit(0 if r.wasSuccessful() else 1)
`

/**
 * The unittest suite of one folder, run by the first python3 on PATH, as the plugins' users run it.
 * @param {string} id
 * @param {string} dir
 * @returns {Gate}
 */
export function unittestGate(id, dir) {
  return {
    id,
    group: 'local',
    title: `python3 unittest ${dir}, no skips`,
    cmd: 'python3',
    args: ['-c', UNITTEST_RUNNER, dir, ...ALLOWED_SKIPS.keys()],
  }
}

/**
 * @param {string} root
 * @param {string[]} args
 * @returns {string}
 */
function git(root, args) {
  const r = spawnSync('git', ['-C', root, ...args], { encoding: 'utf8' })
  if (r.status !== 0) {
    throw new Error(`git ${args.join(' ')} failed: ${r.stderr.trim()}`)
  }
  return r.stdout
}

/**
 * @param {string} root
 * @param {string} rev
 * @returns {boolean}
 */
function isCommit(root, rev) {
  return (
    rev !== '' &&
    spawnSync('git', ['-C', root, 'cat-file', '-e', `${rev}^{commit}`], { stdio: 'ignore' })
      .status === 0
  )
}

/**
 * The tracked files matching the patterns, sorted.
 * @param {string} root
 * @param {string[]} patterns
 * @returns {string[]}
 */
function tracked(root, patterns) {
  return git(root, ['ls-files', '-z', '--', ...patterns])
    .split('\0')
    .filter((f) => f !== '')
    .sort()
}

/**
 * The plugin folders under scripts/tests that hold a file matching test.
 * @param {string} root
 * @param {(name: string) => boolean} test
 * @returns {string[]}
 */
function pluginTestFolders(root, test) {
  const base = join(root, 'scripts', 'tests')
  return readdirSync(base, { withFileTypes: true })
    .filter((d) => d.isDirectory() && readdirSync(join(base, d.name)).some(test))
    .map((d) => d.name)
    .sort()
}

/**
 * One environment variable; built from a string so its name keeps the casing the tool reads.
 * @param {string} name
 * @param {string} value
 * @returns {Record<string, string>}
 */
function envVar(name, value) {
  return Object.fromEntries([[name, value]])
}

/**
 * The gates in order.
 * @param {{ root: string, ci: boolean, base: string }} options
 * @returns {Gate[]}
 */
export function gatesFor({ root, ci, base }) {
  const shellOpts = ['-o', 'all', '-S', 'style', '-x', '-a', '-P', 'SCRIPTDIR']
  const plugins = readdirSync(join(root, 'plugins'), { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name)
    .sort()
  const bumpBase = ci ? base : 'origin/main'
  // Biome on everything but plugin code: the top-level folders and the root files it reads.
  const maintainerBiome = [
    ...new Set(
      tracked(root, [...JS_FAMILY.map((e) => `*.${e}`), '*.json', '*.jsonc'])
        .filter((f) => !f.startsWith('plugins/'))
        .map((f) => (f.includes('/') ? f.slice(0, f.indexOf('/')) : f)),
    ),
  ].sort()
  const tap = (/** @type {string} */ name) => join(tmpdir(), `gates-${process.pid}-${name}.tap`)
  const nodeTests = (/** @type {string} */ dir) =>
    readdirSync(join(root, dir))
      .filter((f) => f.endsWith('.test.mjs'))
      .sort()
      .map((f) => join(dir, f))

  /** @type {Gate[]} */
  const gates = [
    // ── Before anything: the branch and what it carries ─────────────────────────────────────
    {
      id: 'branch',
      group: 'local',
      title: 'the intended branch',
      cmd: 'git',
      args: ['branch', '--show-current'],
    },
    {
      id: 'status',
      group: 'local',
      title: 'nothing staged you did not change',
      cmd: 'git',
      args: ['status', '--short'],
    },
    {
      id: 'signatures',
      group: 'local',
      title: 'every commit since origin/main signed (G)',
      cmd: 'git',
      args: ['log', '--format=%G? %h %s', 'origin/main..HEAD'],
      ...(isCommit(root, 'origin/main') ? {} : { skipReason: 'origin/main does not exist' }),
      after: (out) => {
        const unsigned = out.split('\n').filter((l) => l !== '' && !l.startsWith('G '))
        return unsigned.length === 0 ? null : `not signed with G: ${unsigned.join('; ')}`
      },
    },

    // ── Maintainer tooling and plugin structure (CI) ────────────────────────────────────────
    nodeTestGate('node-tests', nodeTests(join('scripts', 'tests')), tap('maintainer')),
    {
      id: 'check-repo',
      group: 'policy',
      title: 'repository policy',
      cmd: 'node',
      args: ['scripts/check-repo.mjs'],
    },
    {
      id: 'catalog',
      group: 'policy',
      title: 'README catalog in sync',
      cmd: 'node',
      args: ['scripts/catalog.mjs', '--check'],
    },
    {
      id: 'version-bump',
      group: 'policy',
      title: `version bumps since ${bumpBase || 'the base'}`,
      cmd: 'node',
      args: ['scripts/check-version-bump.mjs', bumpBase],
      ...(isCommit(root, bumpBase)
        ? {}
        : { skipReason: `no comparable base commit (${bumpBase || 'none'})` }),
    },
    {
      id: 'tsc-scripts',
      group: 'policy',
      title: 'tsc on scripts/',
      cmd: 'tsc',
      args: ['-p', 'scripts/tsconfig.json', '--noEmit'],
    },
    {
      id: 'shellcheck-scripts',
      group: 'policy',
      title: 'ShellCheck on scripts/',
      cmd: 'shellcheck',
      args: [...shellOpts, ...tracked(root, ['scripts/*.sh'])],
    },
    {
      id: 'shfmt-scripts',
      group: 'policy',
      title: 'shfmt drift on scripts/',
      cmd: 'shfmt',
      args: ['-d', ...tracked(root, ['scripts/*.sh'])],
    },
    {
      id: 'ruff-check-scripts',
      group: 'python',
      title: 'ruff check scripts/',
      cmd: 'ruff',
      args: ['check', 'scripts'],
    },
    {
      id: 'ruff-format-scripts',
      group: 'python',
      title: 'ruff format --check scripts/',
      cmd: 'ruff',
      args: ['format', '--check', 'scripts'],
    },
    {
      id: 'mypy-scripts',
      group: 'python',
      title: 'mypy --strict on the unmigrated scripts/',
      cmd: 'mypy',
      args: [
        '--strict',
        ...tracked(root, ['scripts/*.py', ...MIGRATED_PYTHON.map((p) => `:(exclude)${p}`)]),
      ],
    },
    {
      id: 'basedpyright-scripts',
      group: 'python',
      title: 'basedpyright on scripts/',
      cmd: 'basedpyright',
      args: ['--warnings', 'scripts'],
    },
    {
      id: 'claude-validate:marketplace',
      group: 'claude',
      title: 'claude plugin validate the marketplace',
      cmd: 'claude',
      // An empty catalog is a validator warning, not a defect.
      args: ['plugin', 'validate', ...(plugins.length > 0 ? ['--strict'] : []), '.'],
    },
    ...plugins.map(
      (p) =>
        /** @type {Gate} */ ({
          id: `claude-validate:${p}`,
          group: 'claude',
          title: `claude plugin validate ${p}`,
          cmd: 'claude',
          args: ['plugin', 'validate', '--strict', join('plugins', p)],
        }),
    ),
    {
      id: 'biome-maintainer',
      group: 'lint',
      title: 'Biome outside plugins/',
      cmd: 'biome',
      args: ['ci', '--error-on-warnings', ...maintainerBiome],
    },
    {
      id: 'actionlint',
      group: 'lint',
      title: 'actionlint',
      cmd: 'actionlint',
      args: [],
      env: envVar('SHELLCHECK_OPTS', shellOpts.join(' ')),
    },

    // ── Plugin behavior and plugin code analysis (local only) ───────────────────────────────
    ...pluginTestFolders(root, (f) => f.endsWith('.test.mjs')).map((p) =>
      nodeTestGate(`node-tests:${p}`, nodeTests(join('scripts', 'tests', p)), tap(p), 'local'),
    ),
    ...pluginTestFolders(root, (f) => /^test_.*\.py$/.test(f)).map((p) =>
      unittestGate(`unittest:${p}`, join('scripts', 'tests', p)),
    ),
    ...pluginTestFolders(root, (f) => f === 'by_path.sh').map(
      (p) =>
        /** @type {Gate} */ ({
          id: `by-path:${p}`,
          group: 'local',
          title: `${p} scripts run by path`,
          cmd: join('scripts', 'tests', p, 'by_path.sh'),
          args: [],
        }),
    ),
    ...plugins
      .filter(
        (p) => tracked(root, [`plugins/${p}/*.test.ts`, `plugins/${p}/*.test.tsx`]).length > 0,
      )
      .map(
        (p) =>
          /** @type {Gate} */ ({
            id: `mod-test:${p}`,
            group: 'local',
            title: `claude plugin test ${p}`,
            cmd: 'claude',
            args: ['plugin', 'test', join('plugins', p)],
          }),
      ),
    ...plugins
      .filter((p) => existsSync(join(root, 'plugins', p, 'tsconfig.json')))
      .map(
        (p) =>
          /** @type {Gate} */ ({
            id: `mod-tsc:${p}`,
            group: 'local',
            title: `tsc on the ${p} mod`,
            cmd: 'tsc',
            args: ['-p', join('plugins', p, 'tsconfig.json'), '--noEmit'],
          }),
      ),
    {
      id: 'tsc-plugins',
      group: 'local',
      title: "tsc on the plugins' .mjs files",
      cmd: 'tsc',
      args: ['-p', 'scripts/tsconfig.plugins.json', '--noEmit'],
    },
    {
      id: 'biome-plugins',
      group: 'local',
      title: 'Biome on plugins/',
      cmd: 'biome',
      args: ['ci', '--error-on-warnings', 'plugins'],
    },
    {
      id: 'shellcheck-plugins',
      group: 'local',
      title: 'ShellCheck on plugins/',
      cmd: 'shellcheck',
      args: [...shellOpts, ...tracked(root, ['plugins/*.sh'])],
    },
    {
      id: 'shfmt-plugins',
      group: 'local',
      title: 'shfmt drift on plugins/',
      cmd: 'shfmt',
      args: ['-d', ...tracked(root, ['plugins/*.sh'])],
    },
    {
      id: 'ruff-check-plugins',
      group: 'local',
      title: 'ruff check plugins/',
      cmd: 'ruff',
      args: ['check', 'plugins'],
    },
    {
      id: 'ruff-format-plugins',
      group: 'local',
      title: 'ruff format --check plugins/',
      cmd: 'ruff',
      args: ['format', '--check', 'plugins'],
    },
    {
      id: 'mypy-plugins',
      group: 'local',
      title: 'mypy --strict on plugins/',
      cmd: 'mypy',
      args: ['--strict', ...tracked(root, ['plugins/*.py'])],
    },
    {
      id: 'basedpyright-plugins',
      group: 'local',
      title: 'basedpyright on plugins/',
      cmd: 'basedpyright',
      args: ['--warnings', 'plugins'],
    },
  ]
  return ci ? gates.filter((g) => g.group !== 'local') : gates
}

/**
 * Runs the gates in order and returns the exit code of the first failure, or 0.
 * @param {Gate[]} gates
 * @param {{ root: string, keepGoing: boolean, write: (text: string) => void }} options
 * @returns {number}
 */
export function runGates(gates, { root, keepGoing, write }) {
  /** @type {{ id: string, code: number }[]} */
  const failed = []
  for (const gate of gates) {
    write(`▶ ${gate.id} · ${gate.title}`)
    if (gate.skipReason !== undefined) {
      write(`○ ${gate.id} not applicable: ${gate.skipReason}`)
      continue
    }
    // A gate starts its own node --test runner even when the gates run inside one, as in their
    // tests: a child that inherits NODE_TEST_CONTEXT reports to the parent and writes no reporter.
    const { NODE_TEST_CONTEXT: _parentRunner, ...inherited } = process.env
    const r = spawnSync(gate.cmd, gate.args, {
      cwd: root,
      encoding: 'utf8',
      env: { ...inherited, ...gate.env },
      maxBuffer: 256 * 1024 * 1024,
      stdio: ['ignore', 'pipe', 'pipe'],
    })
    const output = `${r.stdout ?? ''}${r.stderr ?? ''}`.trimEnd()
    if (output !== '') {
      write(output)
    }
    /** @type {string | null} */
    let problem = null
    let code = 0
    if (r.error) {
      const missing = /** @type {NodeJS.ErrnoException} */ (r.error).code === 'ENOENT'
      problem = missing ? `${gate.cmd} is not on PATH` : r.error.message
      code = 1
    } else if (r.status === null) {
      problem = `killed by ${r.signal ?? 'a signal'}`
      code = 1
    } else if (r.status !== 0) {
      code = r.status
    } else {
      problem = gate.after?.(r.stdout) ?? null
      code = problem === null ? 0 : 1
    }
    if (code === 0) {
      write(`✔ ${gate.id}`)
      continue
    }
    write(`✖ ${gate.id} (exit ${code})${problem === null ? '' : `: ${problem}`}`)
    failed.push({ id: gate.id, code })
    if (!keepGoing) {
      break
    }
  }
  if (failed.length > 0) {
    write(`\nFailed: ${failed.map((f) => `${f.id} (exit ${f.code})`).join(', ')}`)
    return failed[0]?.code ?? 1
  }
  write('\n✔ All gates passed')
  return 0
}

if (isMain(import.meta.url)) {
  const argv = process.argv.slice(2)
  /** @param {string} flag */
  const value = (flag) => {
    const i = argv.indexOf(flag)
    return i === -1 ? undefined : argv[i + 1]
  }
  const ci = argv.includes('--ci')
  const group = value('--group')
  const gates = gatesFor({ root: ROOT, ci, base: value('--base') ?? '' }).filter(
    (g) => group === undefined || g.group === group,
  )
  if (gates.length === 0) {
    console.error(`✖ no gate in group "${group}"`)
    process.exit(1)
  }
  process.exit(runGates(gates, { root: ROOT, keepGoing: ci, write: (t) => console.log(t) }))
}
