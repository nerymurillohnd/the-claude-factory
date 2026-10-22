#!/usr/bin/env node
// Tests for gates.mjs: the runner on throwaway gates in a temporary folder, the skip checks on
// fixture test files, and the gate list it builds from the real repository (read-only).
//   npm run gates

import assert from 'node:assert/strict'
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { afterEach, beforeEach, describe, test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { gatesFor, loadPins, nodeTestGate, runGates, unittestGate } from '../gates.mjs'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..')
const PINS = loadPins(readFileSync(join(ROOT, '.github', 'workflows', 'validate.yml'), 'utf8'))

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
    const local = gatesFor({ root: ROOT, ci: false, base: '', pins: PINS })
    const ci = gatesFor({ root: ROOT, ci: true, base: '', pins: PINS }).map((g) => g.id)
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
      'basedpyright-scripts',
      'claude-validate:marketplace',
      'claude-validate:block-no-verify',
      'biome-maintainer',
    ]) {
      assert.ok(ci.includes(id), `${id} should run in CI`)
    }
  })

  test('the maintainer Node tests leave out the plugin test folders', () => {
    const gate = gatesFor({ root: ROOT, ci: true, base: '', pins: PINS }).find(
      (g) => g.id === 'node-tests',
    )
    assert.ok(gate?.args.some((a) => a.endsWith('scripts.test.mjs')))
    assert.ok(!gate?.args.some((a) => /tests\/[a-z0-9-]+\//.test(a)), 'a plugin test runs in CI')
  })

  test('the version-bump base comes from --base in CI and is skipped when it is no commit', () => {
    const bump = gatesFor({ root: ROOT, ci: true, base: '0'.repeat(40), pins: PINS }).find(
      (g) => g.id === 'version-bump',
    )
    assert.match(bump?.skipReason ?? '', /no comparable base commit/)
  })

  test('a pin missing from validate.yml stops the run instead of running an unpinned tool', () => {
    const { BIOME_VERSION: _dropped, ...pins } = PINS
    assert.throws(() => gatesFor({ root: ROOT, ci: false, base: '', pins }), /BIOME_VERSION/)
  })

  test('the pins are read from the env block of validate.yml', () => {
    assert.match(
      Object.entries(PINS).find(([name]) => name === 'RUFF_VERSION')?.[1] ?? '',
      /^\d+\.\d+\.\d+$/,
    )
    assert.deepEqual(
      loadPins('on: push\nenv:\n  A_VERSION: "1.2.3"\n  B: 4\njobs:\n  x:\n    env:\n      C: 5\n'),
      {
        A_VERSION: '1.2.3',
        B: '4',
      },
    )
  })
})
