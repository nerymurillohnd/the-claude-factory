#!/usr/bin/env node
// @ts-check
// The maintainers' gates, in order: the one source of the commands that local runs and CI share
// (ADR_2026-10-21_gates-run-from-one-script).
//   npm run gates                    every gate, stopping at the first failure
//   npm run gates:ci -- --group <g>  the gates of one CI job, going on after a failure
//   node scripts/gates.mjs --only <s,…>  the gates the selectors pick, local ones included: a
//                                      selector ending in - or : is a prefix, any other one id
//   --verbose                          print the output of passing gates too
//
// What CI runs (ADR_2026-10-21_ci-checks-maintainer-tooling-and-plugin-structure): our own tooling
// under scripts/ and the plugins' structure, which no user's machine changes. The plugins' behavior
// (the tests in scripts/testers/<plugin>/, claude plugin test) and the static analysis of plugin
// code run only here, before the push, because they need the maintainer's installed Claude Code and
// tools, and they judge only that build. Those gates carry group "local".
//
// --ci changes three things and nothing else: it leaves out the "local" gates, the version-bump
// base comes from --base instead of origin/main, and the run goes on after a failure. The commands,
// their arguments, the output and the skip checks are the same in both. Keep it that way.
//
// Every gate runs without a shell, as a command and an argument list, from the repository root.
// A test skipped anywhere fails its gate: a skip means a tool is missing. A skip that is legitimate
// goes into ALLOWED_SKIPS with its reason, never into a counter.
//
// Each gate runs its tool by bare name, never through npx or uvx. Under npm run (npm run gates,
// the npm scripts, the Husky hooks, CI) node_modules/.bin comes first on PATH, so the npm tools are
// the versions package-lock.json pins; the other tools are the ones installed on the machine. The gates are written for macOS and Linux: without a shell,
// Windows cannot start an npm .cmd shim such as tsc.cmd.

import { spawnSync } from 'node:child_process'
import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { isMain, ROOT } from './lib.mjs'

/** The JavaScript and TypeScript extensions, ready for files the repository does not have yet. */
const JS_FAMILY = ['js', 'cjs', 'mjs', 'jsx', 'ts', 'cts', 'mts', 'tsx']

/**
 * The Python that scripts/basedpyright-maintainer.mjs checks under the maintainer config, each file
 * against its own interpreter; basedpyright-maintainer-other checks the rest outside plugins/.
 */
/** The shebang of a maintainer script that runs in its own uv environment (PEP 723). */
const UV_SHEBANG = '#!/usr/bin/env -S uv run --script'

/** The repository variables git exports to a hook; gates resolve the repository from their cwd. */
const GIT_HOOK_VARIABLES = new Set([
  'GIT_DIR',
  'GIT_WORK_TREE',
  'GIT_INDEX_FILE',
  'GIT_PREFIX',
  'GIT_COMMON_DIR',
  'GIT_OBJECT_DIRECTORY',
  'GIT_ALTERNATE_OBJECT_DIRECTORIES',
])

/**
 * Variables that make the pinned Biome run another binary or another configuration. A Biome gate
 * refuses to run while one is set, so it never checks with anything but package-lock.json's Biome
 * and biome.jsonc (ADR_2026-10-27_biome-gates-refuse-binary-and-config-overrides).
 */
export const BIOME_OVERRIDES = ['BIOME_BINARY', 'BIOME_CONFIG_PATH']

/** Pathspecs that keep a maintainer gate outside the plugins and outside .github/. */
const OUTSIDE_PLUGINS = [':(exclude)plugins', ':(exclude).github']

const MAINTAINER_PYTHON = [
  'scripts/validators',
  'scripts/checkers',
  'scripts/generators',
  'scripts/testers/schemas',
  'scripts/testers/validators',
  'scripts/testers/run_unittest.py',
]

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
 * @property {(stdout: string, stderr: string) => string | null} [after] a failure message for an
 *   exit-0 run, or null
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
 * Whether a tracked file is a PEP 723 script that runs in its own uv environment.
 * @param {string} root
 * @param {string} file
 * @returns {boolean}
 */
function pep723(root, file) {
  return readFileSync(join(root, file), 'utf8').startsWith(UV_SHEBANG)
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
 * The plugin folders under scripts/testers that hold a file matching test.
 * @param {string} root
 * @param {(name: string) => boolean} test
 * @returns {string[]}
 */
function pluginTestFolders(root, test) {
  const base = join(root, 'scripts', 'testers')
  return readdirSync(base, { withFileTypes: true })
    .filter(
      (d) =>
        d.isDirectory() &&
        existsSync(join(root, 'plugins', d.name)) &&
        readdirSync(join(base, d.name)).some(test),
    )
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
  const pluginPython = tracked(root, ['plugins/*.py'])
  // Biome on everything but plugin code: the top-level folders and the root files it reads.
  const maintainerBiome = [
    ...new Set(
      tracked(root, [
        ...JS_FAMILY.map((e) => `*.${e}`),
        '*.json',
        '*.jsonc',
        '*.md',
        '*.yml',
        '*.yaml',
      ])
        .filter((f) => !f.startsWith('plugins/') && !f.startsWith('.github/'))
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
    nodeTestGate('node-tests', nodeTests(join('scripts', 'testers')), tap('maintainer')),
    {
      id: 'check-repo',
      group: 'policy',
      title: 'repository policy',
      cmd: 'node',
      args: ['scripts/check-repo.mjs'],
    },
    {
      id: 'marketplace',
      group: 'policy',
      title: 'marketplace.json plugins in sync',
      cmd: 'node',
      args: ['scripts/generators/marketplace.mjs', '--check'],
    },
    {
      id: 'catalog',
      group: 'policy',
      title: 'README catalog in sync',
      cmd: 'node',
      args: ['scripts/generators/catalog.mjs', '--check'],
    },
    {
      id: 'version-bump',
      group: 'policy',
      title: `version bumps since ${bumpBase || 'the base'}`,
      cmd: 'python3',
      args: [
        join('.claude', 'skills', 'release-and-versioning', 'scripts', 'check-version-bump.py'),
        bumpBase,
      ],
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
      id: 'shellcheck-maintainer',
      group: 'policy',
      title: 'ShellCheck outside plugins/ and .github/',
      cmd: 'shellcheck',
      args: [...shellOpts, ...tracked(root, ['*.sh', ...OUTSIDE_PLUGINS])],
    },
    {
      id: 'shfmt-maintainer',
      group: 'policy',
      title: 'shfmt drift outside plugins/ and .github/',
      cmd: 'shfmt',
      args: ['-d', ...tracked(root, ['*.sh', ...OUTSIDE_PLUGINS])],
    },
    {
      id: 'ruff-check-maintainer',
      group: 'python',
      title: 'ruff check outside plugins/ and .github/',
      cmd: 'ruff',
      args: ['check', ...tracked(root, ['*.py', ...OUTSIDE_PLUGINS])],
    },
    {
      id: 'ruff-format-maintainer',
      group: 'python',
      title: 'ruff format --check outside plugins/ and .github/',
      cmd: 'ruff',
      args: ['format', '--check', ...tracked(root, ['*.py', ...OUTSIDE_PLUGINS])],
    },
    {
      id: 'basedpyright-maintainer-other',
      group: 'python',
      title: 'basedpyright outside plugins/, .github/ and .claude/, beyond the maintainer config',
      cmd: 'basedpyright',
      args: [
        '--warnings',
        ...tracked(root, [
          '*.py',
          ...OUTSIDE_PLUGINS,
          ':(exclude).claude',
          ...MAINTAINER_PYTHON.map((p) => `:(exclude)${p}`),
        ]),
      ],
    },
    {
      // Basedpyright always skips paths under a dot folder relative to its project root, even when
      // named on the command line, so the skills' Python gets a config rooted inside .claude/skills.
      id: 'basedpyright-skills',
      group: 'python',
      title: 'basedpyright on the project skills in .claude/skills/',
      cmd: 'basedpyright',
      args: ['--warnings', '-p', '.claude/skills/pyrightconfig.json'],
    },
    {
      id: 'basedpyright-maintainer',
      group: 'python',
      title: 'basedpyright on the maintainer Python, each file with its own interpreter',
      cmd: 'node',
      args: ['scripts/basedpyright-maintainer.mjs'],
    },
    // The validators of scripts/validators/ (DEBT-006): a PEP 723 one runs by path in its own uv
    // environment; a standard-library one runs on Python 3.15 through uv, which CI installs.
    ...readdirSync(join(root, 'scripts', 'validators'))
      .filter((f) => f.endsWith('.py'))
      .sort()
      .map((f) => {
        const path = join('scripts', 'validators', f)
        const byPath = pep723(root, path)
        return /** @type {Gate} */ ({
          id: `validator:${f.slice(0, -'.py'.length)}`,
          group: 'python',
          title: `validator ${f}`,
          cmd: byPath ? path : 'uv',
          args: byPath ? [] : ['run', '--no-project', '--python', '3.15', path],
        })
      }),
    {
      id: 'unittest-maintainer',
      group: 'python',
      title: 'unittest on the maintainer tests, no skips',
      cmd: 'scripts/testers/run_unittest.py',
      args: ['scripts/testers/schemas', 'scripts/testers/validators'],
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
      args: ['ci', '--error-on-warnings', '--max-diagnostics=none', ...maintainerBiome],
    },
    {
      // A deprecated key reaches Biome as an information diagnostic, which passes biome ci even with
      // --error-on-warnings, and biome migrate exits 0 either way: only its message tells.
      id: 'biome-migrate',
      group: 'lint',
      title: 'biome.jsonc needs no migration',
      cmd: 'biome',
      args: ['migrate', '--colors=off'],
      after: (stdout, stderr) =>
        `${stdout}${stderr}`.includes('no migration needed')
          ? null
          : 'biome migrate proposes a configuration change: run it, review the diff, then --write',
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
      nodeTestGate(`node-tests:${p}`, nodeTests(join('scripts', 'testers', p)), tap(p), 'local'),
    ),
    ...pluginTestFolders(root, (f) => f.startsWith('test_') && f.endsWith('.py')).map((p) =>
      unittestGate(`unittest:${p}`, join('scripts', 'testers', p)),
    ),
    ...pluginTestFolders(root, (f) => f === 'by_path.sh').map(
      (p) =>
        /** @type {Gate} */ ({
          id: `by-path:${p}`,
          group: 'local',
          title: `${p} scripts run by path`,
          cmd: join('scripts', 'testers', p, 'by_path.sh'),
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
      args: ['ci', '--error-on-warnings', '--max-diagnostics=none', 'plugins'],
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
      id: 'basedpyright-plugins',
      group: 'local',
      title: 'basedpyright on plugins/, beyond the PEP 723 scripts',
      cmd: 'basedpyright',
      args: ['--warnings', ...pluginPython.filter((f) => !pep723(root, f))],
    },
    // A PEP 723 script imports what its own metadata declares, which the python3 on PATH lacks.
    ...pluginPython
      .filter((f) => pep723(root, f))
      .map(
        (f) =>
          /** @type {Gate} */ ({
            id: `basedpyright-plugins:${f}`,
            group: 'local',
            title: `basedpyright on ${f} in its own uv environment`,
            cmd: 'uv',
            args: [
              'run',
              '--quiet',
              '--no-project',
              '--with-requirements',
              f,
              'basedpyright',
              '--warnings',
              f,
            ],
          }),
      ),
  ]
  return ci ? gates.filter((g) => g.group !== 'local') : gates
}

/**
 * The gates of `group` that `only` selects, in their order. A selector ending in "-" or ":" is a
 * prefix (`tsc-`, `node-tests:`); any other selector is one exact id (`node-tests`). Throws when a
 * selector matches no gate, so a mistyped npm script never passes by running nothing.
 * @param {Gate[]} gates
 * @param {string[] | undefined} only
 * @param {string | undefined} group
 * @returns {Gate[]}
 */
export function selectGates(gates, only, group) {
  const inGroup = gates.filter((g) => group === undefined || g.group === group)
  if (only === undefined) {
    return inGroup
  }
  /** @param {string} id @param {string} selector */
  const matches = (id, selector) =>
    selector.endsWith('-') || selector.endsWith(':') ? id.startsWith(selector) : id === selector
  for (const selector of only) {
    if (!inGroup.some((g) => matches(g.id, selector))) {
      throw new Error(`no gate matches "${selector}"`)
    }
  }
  return inGroup.filter((g) => only.some((selector) => matches(g.id, selector)))
}

/**
 * The exit code of a finished gate and, when it failed without a status of its own, why.
 * @param {Gate} gate
 * @param {import('node:child_process').SpawnSyncReturns<string>} r
 * @returns {{ code: number, problem: string | null }}
 */
function outcome(gate, r) {
  if (r.error) {
    const missing = /** @type {NodeJS.ErrnoException} */ (r.error).code === 'ENOENT'
    return { code: 1, problem: missing ? `${gate.cmd} is not on PATH` : r.error.message }
  }
  if (r.status === null) {
    return { code: 1, problem: `killed by ${r.signal ?? 'a signal'}` }
  }
  if (r.status !== 0) {
    return { code: r.status, problem: null }
  }
  const problem = gate.after?.(r.stdout, r.stderr) ?? null
  return { code: problem === null ? 0 : 1, problem }
}

/**
 * Runs one gate, writes its result line (and its output when it fails or `verbose` is set), and
 * returns its exit code; a gate that does not apply returns 0.
 * @param {Gate} gate
 * @param {{ root: string, write: (text: string) => void, verbose: boolean }} options
 * @returns {number}
 */
function runGate(gate, { root, write, verbose }) {
  if (verbose) {
    write(`▶ ${gate.id} · ${gate.title}`)
  }
  if (gate.skipReason !== undefined) {
    write(`○ ${gate.id} not applicable: ${gate.skipReason}`)
    return 0
  }
  const override = gate.cmd === 'biome' && BIOME_OVERRIDES.find((name) => name in process.env)
  if (override) {
    write(
      `✖ ${gate.id} (exit 1): ${override} is set; unset it, the gates run only the pinned Biome`,
    )
    return 1
  }
  // A gate starts its own node --test runner even when the gates run inside one, as in their
  // tests: a child that inherits NODE_TEST_CONTEXT reports to the parent and writes no reporter.
  // Inside a git hook (Husky), git exports the variables of the repository that started it, such as
  // GIT_INDEX_FILE=.git/index; a gate that runs git in another repository would act on that one.
  const { NODE_TEST_CONTEXT: _parentRunner, ...outer } = process.env
  const inherited = Object.fromEntries(
    Object.entries(outer).filter(([name]) => !GIT_HOOK_VARIABLES.has(name)),
  )
  const r = spawnSync(gate.cmd, gate.args, {
    cwd: root,
    encoding: 'utf8',
    env: { ...inherited, ...gate.env },
    maxBuffer: 256 * 1024 * 1024,
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  const output = `${r.stdout ?? ''}${r.stderr ?? ''}`.trimEnd()
  const { code, problem } = outcome(gate, r)
  if (output !== '' && (verbose || code !== 0)) {
    write(output)
  }
  if (code === 0) {
    write(`✔ ${gate.id}`)
  } else {
    write(`✖ ${gate.id} (exit ${code})${problem === null ? '' : `: ${problem}`}`)
  }
  return code
}

/**
 * Runs the gates in order and returns the exit code of the first failure, or 0.
 * @param {Gate[]} gates
 * A passing gate prints only its check mark; a failing one prints its whole output, so the failure
 * is the only thing to read. `verbose` prints every gate's output.
 * @param {{ root: string, keepGoing: boolean, write: (text: string) => void, verbose?: boolean }} options
 * @returns {number}
 */
export function runGates(gates, { root, keepGoing, write, verbose = false }) {
  /** @type {{ id: string, code: number }[]} */
  const failed = []
  for (const gate of gates) {
    const code = runGate(gate, { root, write, verbose })
    if (code !== 0) {
      failed.push({ id: gate.id, code })
      if (!keepGoing) {
        break
      }
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
  const onlyValue = value('--only')
  if (argv.includes('--only') && (onlyValue === undefined || onlyValue.startsWith('--'))) {
    console.error('✖ --only needs a prefix list, such as --only tsc-,ruff-')
    process.exit(1)
  }
  const only = onlyValue?.split(',').filter((p) => p !== '')
  /** @type {Gate[]} */
  let gates
  try {
    gates = selectGates(gatesFor({ root: ROOT, ci, base: value('--base') ?? '' }), only, group)
  } catch (e) {
    console.error(`✖ ${e instanceof Error ? e.message : e}`)
    process.exit(1)
  }
  if (gates.length === 0) {
    console.error(`✖ no gate in group "${group}"`)
    process.exit(1)
  }
  process.exit(
    runGates(gates, {
      root: ROOT,
      keepGoing: ci,
      verbose: argv.includes('--verbose'),
      write: (t) => console.log(t),
    }),
  )
}
