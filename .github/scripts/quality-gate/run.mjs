// Runs one checker stage and captures everything it did: exit status, output, duration, whether
// it rewrote the file, and why it could not run. Nothing here decides pass or fail.

import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'

const MAX_OUTPUT_BYTES = 64 * 1024 * 1024

/** sha256 of a file's bytes, or null when the file doesn't exist. */
export function hashFile(path) {
  try {
    return createHash('sha256').update(readFileSync(path)).digest('hex')
  } catch (error) {
    if (error.code === 'ENOENT') {
      return null
    }
    throw error
  }
}

/** True when a stage ran to the end, whatever it found. */
export function completed(result) {
  return !(result.notExecuted || result.timedOut || result.failure)
}

function launchError(argv0, error) {
  if (error.code === 'ENOENT') {
    return `${argv0}: not found on PATH (ENOENT)`
  }
  if (error.code === 'EACCES') {
    return `${argv0}: not executable (EACCES)`
  }
  return `${argv0}: could not start (${error.code ?? error.message})`
}

/**
 * @param stage {name, argv, cwd?, env?, timeoutMs, rewrites?, skipIfPreviousFailed?, parse}
 * @param file the file the stage checks (hashed before and after when the stage rewrites)
 * @param previous the result of the stage before, if any
 */
export function runStage(stage, file, previous) {
  const base = {
    name: stage.name,
    argv: stage.argv,
    cwd: stage.cwd,
    exitCode: null,
    stdout: '',
    stderr: '',
    durationMs: 0,
    rewrote: false,
    timedOut: false,
    notExecuted: undefined,
    failure: undefined,
    findings: [],
  }
  if (stage.skipIfPreviousFailed && previous && !completed(previous)) {
    return { ...base, notExecuted: `earlier stage ${previous.name} did not complete` }
  }
  const before = stage.rewrites ? hashFile(file) : null
  const started = Date.now()
  const run = spawnSync(stage.argv[0], stage.argv.slice(1), {
    cwd: stage.cwd,
    env: { ...process.env, ...stage.env },
    timeout: stage.timeoutMs,
    killSignal: 'SIGKILL',
    encoding: 'utf8',
    maxBuffer: MAX_OUTPUT_BYTES,
  })
  const result = {
    ...base,
    exitCode: run.status,
    stdout: run.stdout ?? '',
    stderr: run.stderr ?? '',
    durationMs: Date.now() - started,
    rewrote: stage.rewrites ? hashFile(file) !== before : false,
  }
  if (run.error?.code === 'ETIMEDOUT') {
    return { ...result, timedOut: true }
  }
  if (run.error) {
    return { ...result, notExecuted: launchError(stage.argv[0], run.error) }
  }
  if (run.signal) {
    return { ...result, failure: `killed by ${run.signal}` }
  }
  try {
    const parsed = stage.parse(result.stdout, result.stderr, run.status)
    return { ...result, findings: parsed.findings ?? [], failure: parsed.failure }
  } catch (error) {
    return { ...result, failure: `could not read ${stage.name} output: ${error.message}` }
  }
}
