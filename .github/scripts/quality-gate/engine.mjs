// Quality-gate engine shared by every LSP intelligence plugin: per-session state, locks, freshness,
// the repair budget, full reports and bounded summaries. Language specifics live in pipeline.mjs.

import { createHash } from 'node:crypto'
import {
  mkdirSync,
  readdirSync,
  readFileSync,
  renameSync,
  rmdirSync,
  rmSync,
  statSync,
  unlinkSync,
  writeFileSync,
} from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { completed, hashFile, runStage } from './run.mjs'

export { hashFile }

/** Failed repair verifications allowed after the first failure (specs: correction budget). */
export const REPAIR_BUDGET = 8
/** Claude Code caps hook strings at 10,000 characters; stay under it. */
export const MAX_MESSAGE = 9000
export const BLOCKING = new Set(['Failed', 'Exhausted'])
const FAILED_LIKE = new Set(['Failed', 'Exhausted'])
const LOCK_STALE_MS = 10 * 60 * 1000
const HEAD_CHARS = 512

const safe = (value) => String(value).replace(/[^A-Za-z0-9_.-]/g, '_')

export function sessionDir(dataDir, sessionId) {
  return join(dataDir, 'gate', 'sessions', safe(sessionId))
}

export function sleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms)
}

function pidAlive(pid) {
  try {
    process.kill(pid, 0)
    return true
  } catch (error) {
    return error.code === 'EPERM'
  }
}

function lockIsStale(lockDir, staleMs) {
  try {
    const owner = JSON.parse(readFileSync(join(lockDir, 'owner.json'), 'utf8'))
    return !pidAlive(owner.pid) || Date.now() - owner.startedAt > staleMs
  } catch {
    try {
      return Date.now() - statSync(lockDir).mtimeMs > staleMs
    } catch {
      return false
    }
  }
}

/** Runs fn while holding a directory lock; breaks locks whose owner died or that are too old. */
export function withLock(lockDir, fn, { timeoutMs = 120_000, staleMs = LOCK_STALE_MS } = {}) {
  const deadline = Date.now() + timeoutMs
  mkdirSync(dirname(lockDir), { recursive: true })
  for (;;) {
    try {
      mkdirSync(lockDir)
      writeFileSync(
        join(lockDir, 'owner.json'),
        JSON.stringify({ pid: process.pid, startedAt: Date.now() }),
      )
      break
    } catch (error) {
      if (error.code !== 'EEXIST') {
        throw error
      }
      if (lockIsStale(lockDir, staleMs)) {
        rmSync(lockDir, { recursive: true, force: true })
        continue
      }
      if (Date.now() > deadline) {
        throw new Error(`timed out waiting for lock ${lockDir}`)
      }
      sleep(50)
    }
  }
  try {
    return fn()
  } finally {
    rmSync(lockDir, { recursive: true, force: true })
  }
}

const statePath = (dataDir, sessionId) => join(sessionDir(dataDir, sessionId), 'state.json')

export function loadState(dataDir, sessionId) {
  const path = statePath(dataDir, sessionId)
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch (error) {
    if (error.code === 'ENOENT') {
      return { files: {} }
    }
    throw new Error(`unreadable gate state ${path}: ${error.message}`)
  }
}

function blockedMarker(dataDir, sessionId) {
  return join(dataDir, 'gate', 'blocked', safe(sessionId))
}

/** A session needs the guard while any record is blocking or still waits for its check. */
export function sessionNeedsGuard(state) {
  return Object.values(state.files).some((r) => BLOCKING.has(r.status) || r.status === 'Pending')
}

function updateBlockedMarker(dataDir, sessionId, state) {
  const marker = blockedMarker(dataDir, sessionId)
  if (sessionNeedsGuard(state)) {
    mkdirSync(dirname(marker), { recursive: true })
    writeFileSync(marker, '')
    return
  }
  try {
    unlinkSync(marker)
  } catch (error) {
    if (error.code !== 'ENOENT') {
      throw error
    }
  }
  try {
    rmdirSync(dirname(marker))
  } catch (error) {
    if (!['ENOENT', 'ENOTEMPTY', 'EEXIST'].includes(error.code)) {
      throw error
    }
  }
}

export function saveState(dataDir, sessionId, state) {
  const path = statePath(dataDir, sessionId)
  mkdirSync(dirname(path), { recursive: true })
  const tmp = `${path}.${process.pid}.tmp`
  writeFileSync(tmp, JSON.stringify(state, null, 2))
  renameSync(tmp, path)
  updateBlockedMarker(dataDir, sessionId, state)
}

/** Reads, changes and writes the session state under the session lock; returns fn's result. */
export function updateState(dataDir, sessionId, fn) {
  return withLock(join(sessionDir(dataDir, sessionId), 'state.lock'), () => {
    const state = loadState(dataDir, sessionId)
    const result = fn(state)
    saveState(dataDir, sessionId, state)
    return result
  })
}

export function hashFiles(paths) {
  const hash = createHash('sha256')
  for (const path of [...new Set(paths)].sort()) {
    hash.update(`${path}\0${hashFile(path) ?? 'missing'}\n`)
  }
  return hash.digest('hex')
}

function cachedVersions(pipeline, ctx) {
  const path = join(sessionDir(ctx.dataDir, ctx.sessionId), `versions-${safe(pipeline.id)}.json`)
  try {
    return readFileSync(path, 'utf8')
  } catch {
    const key = JSON.stringify(pipeline.versions(ctx))
    mkdirSync(dirname(path), { recursive: true })
    writeFileSync(path, key)
    return key
  }
}

/** What a result must match to still be valid: file content, its configuration, tool versions. */
export function currentKeys(pipeline, file, ctx) {
  return {
    contentHash: hashFile(file),
    configHash: hashFiles(pipeline.configFiles(file, ctx.projectDir)),
    versionsKey: cachedVersions(pipeline, ctx),
  }
}

export function isFresh(record, keys) {
  return Boolean(
    record &&
      record.contentHash === keys.contentHash &&
      record.configHash === keys.configHash &&
      record.versionsKey === keys.versionsKey,
  )
}

/** Marks a file as needing a check, keeping its repair history. */
export function markPending(dataDir, sessionId, file, { agentId, preHash } = {}) {
  updateState(dataDir, sessionId, (state) => {
    const prev = state.files[file]
    state.files[file] = {
      ...prev,
      status: 'Pending',
      attempts: prev?.attempts ?? 0,
      failedBefore: Boolean(prev && (FAILED_LIKE.has(prev.status) || prev.failedBefore)),
      preHash: preHash ?? prev?.preHash ?? null,
      agents: [...new Set([...(prev?.agents ?? []), ...(agentId ? [agentId] : [])])],
      pendingSince: Date.now(),
    }
  })
}

function readHead(file) {
  try {
    return readFileSync(file, 'utf8').slice(0, HEAD_CHARS)
  } catch {
    return null
  }
}

function stageLine(r) {
  if (r.notExecuted) {
    return `- ${r.name}: not executed: ${r.notExecuted}`
  }
  if (r.timedOut) {
    return `- ${r.name}: timed out after ${r.durationMs} ms`
  }
  const parts = [`- ${r.name}: exit ${r.exitCode}`]
  if (r.failure) {
    parts.push(`failed: ${r.failure}`)
  }
  if (r.findings.length > 0) {
    parts.push(`${r.findings.length} finding${r.findings.length === 1 ? '' : 's'}`)
  }
  if (r.rewrote) {
    parts.push('rewrote the file: re-read it before editing')
  }
  return parts.join(' — ')
}

function findingLine(f) {
  const where = [f.file, f.line, f.column].filter((x) => x !== undefined && x !== null).join(':')
  const what = [f.tool, f.code, f.severity].filter(Boolean).join(' ')
  const fix = f.fix ? ` [fix: ${f.fix}]` : ''
  return `  ${where} ${what}: ${f.message}${fix}`
}

function statusLine(record, pluginName) {
  if (record.status === 'Exhausted') {
    return `Repair budget of ${REPAIR_BUDGET} exhausted: a person must decide with /${pluginName}:gate status | retry | waive.`
  }
  if (record.status === 'Failed' && record.attempts > 0) {
    return `Repair attempt ${record.attempts} of ${REPAIR_BUDGET} after the first failure.`
  }
  return null
}

/** Bounded text for Claude: every stage outcome, as many findings as fit, and the report path. */
export function summarize(file, record, results, pluginName, max = MAX_MESSAGE) {
  const findings = results.flatMap((r) => r.findings)
  const head = [`[${pluginName}] ${record.status}: ${file}`]
  const status = statusLine(record, pluginName)
  if (status) {
    head.push(status)
  }
  head.push(...results.map(stageLine))
  if (findings.length > 0) {
    head.push(`${findings.length} finding${findings.length === 1 ? '' : 's'}:`)
  }
  const footer = `full report: ${record.reportPath}`
  const lines = [...head]
  let used = head.join('\n').length + footer.length + 2
  let shown = 0
  for (const f of findings) {
    const line = findingLine(f)
    const reserve = 80
    if (used + line.length + 1 + reserve > max) {
      break
    }
    lines.push(line)
    used += line.length + 1
    shown += 1
  }
  if (shown < findings.length) {
    lines.push(`  … ${findings.length - shown} more findings omitted (see the full report)`)
  }
  lines.push(footer)
  return lines.join('\n').slice(0, max)
}

function writeReport(dataDir, sessionId, file, record, results) {
  const dir = join(sessionDir(dataDir, sessionId), 'reports')
  mkdirSync(dir, { recursive: true })
  const path = join(dir, `${createHash('sha256').update(file).digest('hex').slice(0, 16)}.txt`)
  const blocks = [`file: ${file}`, `status: ${record.status}`, `attempts: ${record.attempts}`]
  for (const r of results) {
    blocks.push(
      [
        `== ${r.name}`,
        `argv: ${JSON.stringify(r.argv)}`,
        `cwd: ${r.cwd ?? ''}`,
        `exit: ${r.exitCode} timedOut: ${r.timedOut} rewrote: ${r.rewrote} durationMs: ${r.durationMs}`,
        r.notExecuted ? `not executed: ${r.notExecuted}` : '',
        r.failure ? `failure: ${r.failure}` : '',
        '-- findings',
        ...r.findings.map(findingLine),
        '-- stdout',
        r.stdout,
        '-- stderr',
        r.stderr,
      ].join('\n'),
    )
  }
  writeFileSync(path, blocks.join('\n\n'))
  return path
}

function runPipeline(pipeline, file, governed, ctx) {
  const stages = pipeline.stages({ ...ctx, file, dialect: governed.dialect })
  const results = []
  for (const stage of stages) {
    results.push(runStage(stage, file, results.at(-1)))
  }
  return results
}

function nextRecord(prev, results, keys) {
  const failed = results.some((r) => !completed(r) || r.findings.length > 0)
  if (!failed) {
    return { status: 'Passed', attempts: 0, failedBefore: false }
  }
  const repairing = Boolean(prev && (FAILED_LIKE.has(prev.status) || prev.failedBefore))
  const attempts = repairing ? (prev.attempts ?? 0) + 1 : 0
  return {
    status: attempts >= REPAIR_BUDGET ? 'Exhausted' : 'Failed',
    attempts,
    failedBefore: true,
    ...keys,
  }
}

function checkOne(file, opts) {
  const { pipeline, dataDir, sessionId, agentId, pluginName } = opts
  const ctx = { ...opts, sessionDir: sessionDir(dataDir, sessionId) }
  const head = readHead(file)
  if (head === null) {
    updateState(dataDir, sessionId, (state) => {
      delete state.files[file]
    })
    return null
  }
  const governed = pipeline.detect(file, head)
  if (!governed.governed) {
    return null
  }
  const prev = loadState(dataDir, sessionId).files[file]
  const before = currentKeys(pipeline, file, ctx)
  if (prev && prev.status !== 'Pending' && isFresh(prev, before)) {
    return { file, record: prev, results: [], summary: prev.summary }
  }
  const agents = [...new Set([...(prev?.agents ?? []), ...(agentId ? [agentId] : [])])]
  if (governed.unsupported) {
    const record = {
      ...before,
      status: 'Unsupported',
      attempts: 0,
      agents,
      summary: `[${pluginName}] Unsupported: ${file} — not checked: ${governed.unsupported}`,
      updatedAt: Date.now(),
    }
    updateState(dataDir, sessionId, (state) => {
      state.files[file] = record
    })
    return { file, record, results: [], summary: record.summary }
  }
  const results = runPipeline(pipeline, file, governed, ctx)
  const after = currentKeys(pipeline, file, ctx)
  const record = { ...nextRecord(prev, results, after), ...after, agents, updatedAt: Date.now() }
  record.reportPath = writeReport(dataDir, sessionId, file, record, results)
  record.summary = summarize(file, record, results, pluginName)
  updateState(dataDir, sessionId, (state) => {
    state.files[file] = record
  })
  return { file, record, results, summary: record.summary }
}

/**
 * Checks each governed file once per content version. Concurrent callers on the same file wait for
 * its lock and reuse the fresh result instead of running the pipeline again.
 */
export function checkFiles(opts) {
  const entries = []
  for (const file of [...new Set(opts.files)]) {
    const lock = join(
      sessionDir(opts.dataDir, opts.sessionId),
      'locks',
      createHash('sha256').update(file).digest('hex').slice(0, 16),
    )
    const entry = withLock(lock, () => checkOne(file, opts), { timeoutMs: 15 * 60 * 1000 })
    if (entry) {
      entries.push(entry)
    }
  }
  return entries
}

const registryDir = (sessionId) => join(tmpdir(), 'claude-quality-gates', safe(sessionId))

/** Publishes this plugin's blocked files so other gates allow repairs to them. */
export function writeRegistry(sessionId, pluginName, files) {
  const dir = registryDir(sessionId)
  mkdirSync(dir, { recursive: true })
  const path = join(dir, `${safe(pluginName)}.json`)
  const tmp = `${path}.${process.pid}.tmp`
  writeFileSync(tmp, JSON.stringify([...files]))
  renameSync(tmp, path)
}

/** Every file any quality gate of this session currently blocks on. */
export function readRegistry(sessionId) {
  const blocked = new Set()
  let names = []
  try {
    names = readdirSync(registryDir(sessionId))
  } catch {
    return blocked
  }
  for (const name of names.filter((n) => n.endsWith('.json'))) {
    try {
      for (const file of JSON.parse(readFileSync(join(registryDir(sessionId), name), 'utf8'))) {
        blocked.add(file)
      }
    } catch {
      // A registry file mid-write or removed: the next read sees it whole.
    }
  }
  return blocked
}
