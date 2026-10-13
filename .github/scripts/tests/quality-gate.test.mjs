#!/usr/bin/env node
// Tests for the shared quality-gate engine (.github/scripts/quality-gate). A fake pipeline runs
// small `node -e` programs as its stages, so these tests need no linter or formatter installed.
//   node --test ".github/scripts/tests/*.test.mjs"

import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  utimesSync,
  writeFileSync,
} from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { afterEach, beforeEach, describe, test } from 'node:test'
import { fileURLToPath, pathToFileURL } from 'node:url'

const GATE_DIR = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'quality-gate')
const engine = await import(pathToFileURL(join(GATE_DIR, 'engine.mjs')).href)
const NODE = process.execPath

let work
let dataDir
let file

beforeEach(() => {
  work = mkdtempSync(join(tmpdir(), 'qg-'))
  dataDir = join(work, 'data')
  file = join(work, 'project', 'a.txt')
  mkdirSync(dirname(file), { recursive: true })
  writeFileSync(file, 'hello\n')
})

afterEach(() => {
  rmSync(work, { recursive: true, force: true })
})

/** A stage that runs `code` with node; stdout lines become findings, exit > 1 is a failure. */
function stage(name, code, extra = {}) {
  return {
    name,
    argv: [NODE, '-e', code, file],
    timeoutMs: 10_000,
    parse: (stdout, _stderr, exitCode) => ({
      findings: stdout
        .split('\n')
        .filter(Boolean)
        .map((message) => ({ tool: name, file, message, severity: 'error' })),
      failure: exitCode > 1 ? `exit ${exitCode}` : undefined,
    }),
    ...extra,
  }
}

function pipeline(stages, { configFiles = [], versions = { fake: '1.0.0' } } = {}) {
  return {
    id: 'fake',
    detect: () => ({ governed: true }),
    configFiles: () => configFiles,
    configNames: [],
    stages: () => stages,
    versions: () => versions,
  }
}

function check(p, files = [file]) {
  return engine.checkFiles({
    pipeline: p,
    files,
    dataDir,
    sessionId: 's1',
    agentId: undefined,
    projectDir: dirname(file),
    pluginRoot: work,
    pluginName: 'fake-plugin',
  })
}

const PASS = 'process.exit(0)'
const FIND = 'console.log("bad thing"); process.exit(1)'

describe('quality-gate engine', () => {
  test('passes a clean file and reports every stage', () => {
    const [entry] = check(pipeline([stage('lint', PASS), stage('types', PASS)]))
    assert.equal(entry.record.status, 'Passed')
    assert.equal(entry.record.attempts, 0)
    assert.match(entry.summary, /lint: exit 0/)
    assert.match(entry.summary, /types: exit 0/)
    assert.ok(existsSync(entry.record.reportPath))
  })

  test('fails on findings and carries them', () => {
    const [entry] = check(pipeline([stage('lint', FIND)]))
    assert.equal(entry.record.status, 'Failed')
    assert.equal(entry.results[0].findings[0].message, 'bad thing')
    assert.match(entry.summary, /bad thing/)
  })

  test('a missing tool is an explicit failure, never a pass', () => {
    const missing = { ...stage('lint', PASS), argv: ['definitely-not-a-tool-qg', file] }
    const [entry] = check(pipeline([missing, stage('types', PASS)]))
    assert.equal(entry.record.status, 'Failed')
    assert.match(entry.results[0].notExecuted, /not found|ENOENT/)
    assert.equal(entry.results[1].exitCode, 0)
    assert.match(entry.summary, /lint: not executed/)
  })

  test('a stage marked skipIfPreviousFailed reports not executed after a failed launch', () => {
    const missing = { ...stage('format', PASS), argv: ['definitely-not-a-tool-qg', file] }
    const [entry] = check(
      pipeline([missing, stage('analyze', PASS, { skipIfPreviousFailed: true })]),
    )
    assert.equal(entry.record.status, 'Failed')
    assert.match(entry.results[1].notExecuted, /format did not complete/)
  })

  test('a timeout is an explicit failure', () => {
    const slow = stage('lint', 'setTimeout(() => {}, 5000)', { timeoutMs: 200 })
    const [entry] = check(pipeline([slow]))
    assert.equal(entry.record.status, 'Failed')
    assert.equal(entry.results[0].timedOut, true)
    assert.match(entry.summary, /timed out/)
  })

  test('a rewrite is detected and the summary asks to re-read the file', () => {
    const fmt = stage('format', 'require("fs").appendFileSync(process.argv[1], "x\\n")', {
      rewrites: true,
    })
    const [entry] = check(pipeline([fmt]))
    assert.equal(entry.results[0].rewrote, true)
    assert.match(entry.summary, /re-read/)
    assert.equal(entry.record.contentHash, engine.hashFile(file))
  })

  test('the budget counts failed repairs after the first failure', () => {
    const p = pipeline([stage('lint', FIND)])
    assert.equal(check(p)[0].record.attempts, 0)
    let last
    for (let i = 1; i <= engine.REPAIR_BUDGET; i += 1) {
      writeFileSync(file, `attempt ${i}\n`)
      last = check(p)[0].record
    }
    assert.equal(last.attempts, engine.REPAIR_BUDGET)
    assert.equal(last.status, 'Exhausted')
    writeFileSync(file, 'fixed\n')
    const passed = check(pipeline([stage('lint', PASS)]))[0].record
    assert.equal(passed.status, 'Passed')
    assert.equal(passed.attempts, 0)
  })

  test('an unchanged failed file is not re-run and spends no attempt', () => {
    const counter = join(work, 'runs.txt')
    const p = pipeline([
      stage('lint', `require("fs").appendFileSync(${JSON.stringify(counter)}, "r\\n"); ${FIND}`),
    ])
    check(p)
    const again = check(p)[0].record
    assert.equal(readFileSync(counter, 'utf8'), 'r\n')
    assert.equal(again.attempts, 0)
  })

  test('freshness follows content, configuration and tool versions', () => {
    const config = join(work, 'project', 'lint.toml')
    writeFileSync(config, 'a = 1\n')
    const p = pipeline([stage('lint', PASS)], { configFiles: [config] })
    const record = check(p)[0].record
    const current = () => engine.currentKeys(p, file, { dataDir, sessionId: 's1' })
    assert.equal(engine.isFresh(record, current()), true)
    writeFileSync(config, 'a = 2\n')
    assert.equal(engine.isFresh(record, current()), false)
    writeFileSync(config, 'a = 1\n')
    writeFileSync(file, 'changed\n')
    assert.equal(engine.isFresh(record, current()), false)
    writeFileSync(file, 'hello\n')
    const newer = pipeline([stage('lint', PASS)], {
      configFiles: [config],
      versions: { fake: '2.0.0' },
    })
    assert.equal(
      engine.isFresh(record, engine.currentKeys(newer, file, { dataDir, sessionId: 's2' })),
      false,
    )
  })

  test('two concurrent checks of one file run the pipeline once', async () => {
    const counter = join(work, 'runs.txt')
    const script = join(work, 'run-check.mjs')
    const stageCode = `require("fs").appendFileSync(${JSON.stringify(counter)}, "r\\n"); Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 400)`
    const options = {
      files: [file],
      dataDir,
      sessionId: 's1',
      projectDir: dirname(file),
      pluginRoot: work,
      pluginName: 'fake-plugin',
    }
    writeFileSync(
      script,
      [
        `import { checkFiles } from ${JSON.stringify(pathToFileURL(join(GATE_DIR, 'engine.mjs')).href)}`,
        `const stage = { name: 'lint', argv: [process.execPath, '-e', ${JSON.stringify(stageCode)}], timeoutMs: 10000, parse: () => ({ findings: [] }) }`,
        `const pipeline = { id: 'fake', detect: () => ({ governed: true }), configFiles: () => [], configNames: [], stages: () => [stage], versions: () => ({ fake: '1' }) }`,
        `checkFiles({ pipeline, ...${JSON.stringify(options)} })`,
        '',
      ].join('\n'),
    )
    const run = () =>
      new Promise((done, fail) => {
        const child = spawn(NODE, [script], { stdio: 'inherit' })
        child.on('exit', (code) => (code === 0 ? done() : fail(new Error(`exit ${code}`))))
      })
    await Promise.all([run(), run()])
    assert.equal(readFileSync(counter, 'utf8'), 'r\n')
  })

  test('summaries stay under the cap and point to the full report', () => {
    const many = Array.from({ length: 800 }, (_, i) => `finding number ${i} ${'x'.repeat(40)}`)
    const [entry] = check(
      pipeline([stage('lint', `console.log(${JSON.stringify(many.join('\n'))}); process.exit(1)`)]),
    )
    assert.ok(
      entry.summary.length <= engine.MAX_MESSAGE,
      `summary is ${entry.summary.length} chars`,
    )
    assert.match(entry.summary, /800 findings/)
    assert.match(entry.summary, /omitted/)
    assert.ok(entry.summary.includes(entry.record.reportPath))
    const report = readFileSync(entry.record.reportPath, 'utf8')
    assert.ok(report.includes('finding number 0 ') && report.includes('finding number 799 '))
  })

  test('a stale lock left by a dead process is broken', () => {
    const lock = join(work, 'lock')
    mkdirSync(lock)
    writeFileSync(join(lock, 'owner.json'), JSON.stringify({ pid: 999_999_999, startedAt: 0 }))
    const old = new Date(Date.now() - 3_600_000)
    utimesSync(lock, old, old)
    assert.equal(
      engine.withLock(lock, () => 'ran', { timeoutMs: 1000 }),
      'ran',
    )
    assert.equal(existsSync(lock), false)
  })

  test('the blocked marker follows the session state', () => {
    check(pipeline([stage('lint', FIND)]))
    assert.equal(existsSync(join(dataDir, 'gate', 'blocked', 's1')), true)
    writeFileSync(file, 'fixed\n')
    check(pipeline([stage('lint', PASS)]))
    assert.equal(existsSync(join(dataDir, 'gate', 'blocked')), false)
  })
})
