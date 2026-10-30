#!/usr/bin/env node
// @ts-check
// Tests for gates.mjs: the runner on throwaway gates in a temporary folder, the skip checks on
// fixture test files, and the gate list it builds from the real repository (read-only).
//   npm run gates

import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { existsSync, mkdirSync, mkdtempSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { afterEach, beforeEach, describe, test } from 'node:test'
import { fileURLToPath } from 'node:url'
import {
  BIOME_OVERRIDES,
  gatesFor,
  modTypesBlocker,
  nodeTestGate,
  runGates,
  selectGates,
  unittestGate,
} from '../gates.mjs'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..')

/** @type {string} */
let dir
/** @type {string[]} */
let lines
/** @param {string} text */
const write = (text) => {
  lines.push(text)
}

/**
 * A gate that runs a short Node program in the temporary folder.
 * @param {string} id
 * @param {string} code
 * @returns {import('../gates.mjs').Gate}
 */
const nodeGate = (id, code) => ({
  id,
  group: 'policy',
  title: `gate ${id}`,
  cmd: process.execPath,
  args: ['-e', code],
})

/** @param {string} id */
const touches = (id) => nodeGate(id, `require('node:fs').writeFileSync('ran-${id}', '')`)

describe('gates runner', () => {
  beforeEach(() => {
    dir = mkdtempSync(join(tmpdir(), 'gates-'))
    lines = []
  })
  afterEach(() => rmSync(dir, { recursive: true, force: true }))

  test('every gate green returns 0 and runs them all', () => {
    const code = runGates([touches('a'), touches('b')], { root: dir, keepGoing: false, write })
    assert.equal(code, 0)
    assert.ok(existsSync(join(dir, 'ran-a')) && existsSync(join(dir, 'ran-b')))
  })

  test('the first failure stops the run and its exit code is returned', () => {
    const gates = [touches('a'), nodeGate('broken', 'process.exit(3)'), touches('c')]
    const code = runGates(gates, { root: dir, keepGoing: false, write })
    assert.equal(code, 3)
    assert.ok(existsSync(join(dir, 'ran-a')))
    assert.ok(!existsSync(join(dir, 'ran-c')), 'a gate after the failure ran')
    assert.match(lines.join('\n'), /✖ broken/)
  })

  test('a blocked gate fails with its message and runs nothing', () => {
    const gate = { ...touches('a'), blocker: 'types are missing' }
    assert.equal(runGates([gate], { root: dir, keepGoing: false, write }), 1)
    assert.ok(!existsSync(join(dir, 'ran-a')), 'a blocked gate ran its command')
    assert.match(lines.join('\n'), /✖ a \(exit 1\): types are missing/)
  })

  test('a passing gate prints only its check mark; a failing one prints its output', () => {
    const gates = [
      nodeGate('quiet', "console.log('noise-from-pass')"),
      nodeGate('loud', "console.log('why-it-failed'); process.exit(2)"),
    ]
    runGates(gates, { root: dir, keepGoing: true, write })
    const out = lines.join('\n')
    assert.match(out, /✔ quiet/)
    assert.doesNotMatch(out, /noise-from-pass/)
    assert.match(out, /why-it-failed/)
  })

  test('verbose prints the output of passing gates too', () => {
    runGates([nodeGate('quiet', "console.log('noise-from-pass')")], {
      root: dir,
      keepGoing: false,
      write,
      verbose: true,
    })
    assert.match(lines.join('\n'), /noise-from-pass/)
  })

  test('keepGoing runs the rest and returns the first failure code', () => {
    const gates = [
      nodeGate('one', 'process.exit(3)'),
      touches('b'),
      nodeGate('two', 'process.exit(5)'),
    ]
    const code = runGates(gates, { root: dir, keepGoing: true, write })
    assert.equal(code, 3)
    assert.ok(existsSync(join(dir, 'ran-b')))
    assert.match(lines.join('\n'), /Failed: one \(exit 3\), two \(exit 5\)/)
  })

  test('a gate killed by a signal fails with 1', () => {
    const gate = nodeGate('killed', "process.kill(process.pid, 'SIGKILL')")
    assert.equal(runGates([gate], { root: dir, keepGoing: false, write }), 1)
    assert.match(lines.join('\n'), /killed by SIGKILL/)
  })

  test('an after check reads stderr as well as stdout', () => {
    /** @type {import('../gates.mjs').Gate} */
    const gate = {
      ...nodeGate('stderr', "process.stderr.write('marker-on-stderr')"),
      after: (stdout, stderr) =>
        `${stdout}${stderr}`.includes('marker-on-stderr') ? null : 'lost',
    }
    assert.equal(runGates([gate], { root: dir, keepGoing: false, write }), 0, lines.join('\n'))
  })

  test('a missing tool fails with 1 and names the tool', () => {
    const gate = { ...touches('x'), cmd: 'no-such-tool-for-gates' }
    assert.equal(runGates([gate], { root: dir, keepGoing: false, write }), 1)
    assert.match(lines.join('\n'), /no-such-tool-for-gates is not on PATH/)
  })

  test('a skipped Node test fails the gate', () => {
    writeFileSync(
      join(dir, 'x.test.mjs'),
      "import { test } from 'node:test'\ntest('kept', () => {})\ntest('left out', { skip: true }, () => {})\n",
    )
    const gate = nodeTestGate('node', [join(dir, 'x.test.mjs')], join(dir, 'tap.txt'))
    assert.equal(runGates([gate], { root: dir, keepGoing: false, write }), 1)
    assert.match(lines.join('\n'), /1 skipped test: left out/)
  })

  test('Node tests that all run pass the gate', () => {
    writeFileSync(
      join(dir, 'x.test.mjs'),
      "import { test } from 'node:test'\ntest('kept', () => {})\n",
    )
    const gate = nodeTestGate('node', [join(dir, 'x.test.mjs')], join(dir, 'tap.txt'))
    assert.equal(runGates([gate], { root: dir, keepGoing: false, write }), 0)
  })

  test('a skipped Python test fails the gate even though unittest exits 0', () => {
    mkdirSync(join(dir, 'py'))
    writeFileSync(
      join(dir, 'py', 'test_x.py'),
      'import unittest\n\nclass T(unittest.TestCase):\n    def test_kept(self) -> None:\n        pass\n\n    @unittest.skip("no tool")\n    def test_left_out(self) -> None:\n        pass\n',
    )
    const gate = unittestGate('py', join(dir, 'py'))
    assert.equal(runGates([gate], { root: dir, keepGoing: false, write }), 4)
    assert.match(lines.join('\n'), /skipped: .*test_left_out \(no tool\)/)
  })
})

describe('gate list', () => {
  test('--ci keeps maintainer tooling and plugin structure, and leaves plugin behavior local', () => {
    const local = gatesFor({ root: ROOT, ci: false, base: '' })
    const ci = gatesFor({ root: ROOT, ci: true, base: '' }).map((g) => g.id)
    const localOnly = local.filter((g) => g.group === 'local').map((g) => g.id)
    for (const id of [
      'signatures',
      'unittest:python-lsp-intelligence',
      'by-path:block-no-verify',
      'node-tests:typescript6-lsp-intelligence',
      'mod-test:project-maintainer',
      'mod-tsc:project-maintainer',
      'tsc-plugins',
      'basedpyright-plugins',
      'shellcheck-plugins',
    ]) {
      assert.ok(localOnly.includes(id), `${id} should run only locally`)
      assert.ok(!ci.includes(id), `${id} should not run in CI`)
    }
    for (const id of [
      'node-tests',
      'check-repo',
      'version-bump',
      'tsc-scripts',
      'basedpyright-maintainer-other',
      'basedpyright-skills',
      'basedpyright-maintainer',
      'unittest-maintainer',
      'claude-validate:marketplace',
      'claude-validate:block-no-verify',
      'biome-maintainer',
    ]) {
      assert.ok(ci.includes(id), `${id} should run in CI`)
    }
    assert.ok(!ci.includes('pytest-scripts'), 'pytest-scripts should be gone')
  })

  test('a PEP 723 plugin script is type-checked in its own uv environment', () => {
    const script = 'plugins/github-operations/skills/github/scripts/check-forms.py'
    const local = gatesFor({ root: ROOT, ci: false, base: '' })
    const all = local.find((g) => g.id === 'basedpyright-plugins')
    assert.ok(all?.args.includes('plugins/github-operations/hooks/github_hooks.py'))
    assert.ok(!all?.args.includes(script), 'the shared run cannot see the script dependencies')
    const own = local.find((g) => g.id === `basedpyright-plugins:${script}`)
    assert.equal(own?.group, 'local')
    assert.equal(own?.cmd, 'uv')
    assert.deepEqual(own?.args, [
      'run',
      '--quiet',
      '--no-project',
      '--with-requirements',
      script,
      'basedpyright',
      '--warnings',
      script,
    ])
  })

  test('the maintainer Node tests leave out the plugin test folders', () => {
    const gate = gatesFor({ root: ROOT, ci: true, base: '' }).find((g) => g.id === 'node-tests')
    assert.ok(gate?.args.some((a) => a.endsWith('scripts.test.mjs')))
    assert.ok(!gate?.args.some((a) => /tests\/[a-z0-9-]+\//.test(a)), 'a plugin test runs in CI')
  })

  test('the version-bump base comes from --base in CI and is skipped when it is no commit', () => {
    const bump = gatesFor({ root: ROOT, ci: true, base: '0'.repeat(40) }).find(
      (g) => g.id === 'version-bump',
    )
    assert.match(bump?.skipReason ?? '', /no comparable base commit/)
  })

  test("a mod's tsc gate is blocked, naming the fix, while its types are missing", () => {
    const copy = mkdtempSync(join(tmpdir(), 'gates-mod-'))
    try {
      const types = join(copy, 'plugins', 'tool-ledger', '.claude-plugin', 'types')
      assert.match(
        modTypesBlocker(copy, 'tool-ledger') ?? '',
        /^plugins\/tool-ledger\/\.claude-plugin\/types\/ is missing: run npm run setup/,
      )
      mkdirSync(types, { recursive: true })
      writeFileSync(join(types, 'tsconfig.json'), '{}')
      assert.equal(modTypesBlocker(copy, 'tool-ledger'), null)
    } finally {
      rmSync(copy, { recursive: true, force: true })
    }
  })

  test('plugin test gates run only for folders named after a plugin', () => {
    const ids = gatesFor({ root: ROOT, ci: false, base: '' }).map((g) => g.id)
    assert.ok(
      !ids.includes('unittest:schemas'),
      'the maintainer schema tests run as a plugin suite',
    )
    assert.ok(ids.includes('unittest:python-lsp-intelligence'))
  })

  test('no gate runs mypy: Basedpyright is the only Python type checker', () => {
    for (const gate of gatesFor({ root: ROOT, ci: false, base: '' })) {
      assert.notEqual(gate.cmd, 'mypy', `${gate.id} runs mypy`)
    }
  })

  test('every gate runs the installed tool, never npx or uvx', () => {
    for (const gate of gatesFor({ root: ROOT, ci: false, base: '' })) {
      assert.ok(!['npx', 'uvx'].includes(gate.cmd), `${gate.id} runs through ${gate.cmd}`)
    }
  })
})

describe('selectGates', () => {
  /**
   * @param {string} id
   * @param {import('../gates.mjs').Group} group
   * @returns {import('../gates.mjs').Gate}
   */
  const g = (id, group) => ({ id, group, title: id, cmd: 'true', args: [] })
  const gates = [
    g('tsc-scripts', 'policy'),
    g('ruff-check-plugins', 'local'),
    g('tsc-plugins', 'local'),
  ]

  test('keeps the gate order and matches ids by prefix, local gates included', () => {
    const ids = selectGates(gates, ['tsc-'], undefined).map((x) => x.id)
    assert.deepEqual(ids, ['tsc-scripts', 'tsc-plugins'])
  })

  test('a selector without a trailing - or : matches one id exactly', () => {
    const more = [...gates, g('tsc-scripts-extra', 'local')]
    assert.deepEqual(
      selectGates(more, ['tsc-scripts'], undefined).map((x) => x.id),
      ['tsc-scripts'],
    )
  })

  test('fails on a prefix that matches no gate, naming it', () => {
    assert.throws(() => selectGates(gates, ['tsc-', 'nope'], undefined), /no gate matches "nope"/)
  })

  test('combines --only with --group', () => {
    assert.deepEqual(
      selectGates(gates, ['tsc-'], 'local').map((x) => x.id),
      ['tsc-plugins'],
    )
  })
})

describe('runGates inside a git hook', () => {
  test('does not pass the repository variables git exports to its hooks', () => {
    const saved = process.env['GIT_INDEX_FILE']
    process.env['GIT_INDEX_FILE'] = '.git/index'
    try {
      /** @type {import('../gates.mjs').Gate} */
      const gate = {
        id: 'env',
        group: 'local',
        title: 'env',
        cmd: process.execPath,
        args: ['-e', 'process.exit(process.env.GIT_INDEX_FILE === undefined ? 0 : 1)'],
      }
      /** @type {string[]} */
      const output = []
      const code = runGates([gate], { root: ROOT, keepGoing: false, write: (l) => output.push(l) })
      assert.equal(code, 0, output.join('\n'))
    } finally {
      if (saved === undefined) {
        delete process.env['GIT_INDEX_FILE']
      } else {
        process.env['GIT_INDEX_FILE'] = saved
      }
    }
  })
})

describe('Biome gates', () => {
  const biome = join(ROOT, 'node_modules', '.bin', 'biome')
  const migrate = gatesFor({ root: ROOT, ci: true, base: '' }).find((g) => g.id === 'biome-migrate')

  test('biome-migrate runs in the CI lint group', () => {
    assert.equal(migrate?.group, 'lint')
    assert.deepEqual(migrate?.args, ['migrate', '--colors=off'])
  })

  test('biome-migrate fails on a deprecated key and passes on an up-to-date biome.jsonc', () => {
    assert.ok(migrate)
    const tmp = mkdtempSync(join(tmpdir(), 'gates-migrate-'))
    try {
      /** @param {object} rules @returns {number} */
      const run = (rules) => {
        writeFileSync(join(tmp, 'biome.jsonc'), JSON.stringify({ linter: { rules } }))
        /** @type {string[]} */
        const out = []
        return runGates([{ ...migrate, cmd: biome }], {
          root: tmp,
          keepGoing: false,
          write: (l) => out.push(l),
        })
      }
      assert.equal(run({ recommended: true }), 1, 'a deprecated key passed')
      assert.equal(run({ preset: 'recommended' }), 0, 'an up-to-date config failed')
    } finally {
      rmSync(tmp, { recursive: true, force: true })
    }
  })

  for (const name of BIOME_OVERRIDES) {
    test(`a Biome gate refuses to run while ${name} is set, naming it but not its value`, () => {
      const saved = process.env[name]
      process.env[name] = '/secret/value'
      /** @type {string[]} */
      const out = []
      try {
        /** @type {import('../gates.mjs').Gate} */
        const gate = { id: 'b', group: 'lint', title: 'b', cmd: 'biome', args: ['--version'] }
        /** @type {import('../gates.mjs').Gate} */
        const other = {
          id: 'n',
          group: 'lint',
          title: 'n',
          cmd: process.execPath,
          args: ['-e', ''],
        }
        const opts = {
          root: ROOT,
          keepGoing: true,
          write: (/** @type {string} */ l) => out.push(l),
        }
        assert.equal(runGates([gate], opts), 1)
        assert.match(out.join('\n'), new RegExp(`✖ b \\(exit 1\\): ${name} is set`))
        assert.doesNotMatch(out.join('\n'), /secret/)
        assert.equal(runGates([other], opts), 0, 'a gate that is not Biome refused too')
      } finally {
        if (saved === undefined) {
          delete process.env[name]
        } else {
          process.env[name] = saved
        }
      }
    })
  }
})

describe('validator gates', () => {
  test('every validator runs in the CI python group on Python 3.15', () => {
    const gates = gatesFor({ root: ROOT, ci: true, base: '' })
    const files = readdirSync(join(ROOT, 'scripts', 'validators')).filter((f) => f.endsWith('.py'))
    assert.equal(files.length, 10)
    for (const file of files) {
      const gate = gates.find((x) => x.id === `validator:${file.replace(/\.py$/, '')}`)
      assert.ok(gate, `no gate for ${file}`)
      assert.equal(gate.group, 'python')
      const path = join('scripts', 'validators', file)
      assert.ok(
        gate.cmd === path ||
          (gate.cmd === 'uv' && gate.args.includes('3.15') && gate.args.includes(path)),
        `${file} runs as ${gate.cmd} ${gate.args.join(' ')}`,
      )
    }
  })
})

describe('gates.mjs --only', () => {
  test('fails when --only has no prefix list instead of running every gate', () => {
    const r = spawnSync(process.execPath, ['scripts/gates.mjs', '--only'], {
      cwd: ROOT,
      encoding: 'utf8',
    })
    assert.equal(r.status, 1)
    assert.match(r.stderr, /--only needs a prefix list/)
  })
})
