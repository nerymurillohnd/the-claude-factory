#!/usr/bin/env node
// @ts-check
// Type-checks the maintainer Python that scripts/pyrightconfig.maintainer.json covers, each file
// against the interpreter that runs it: a PEP 723 entry point against its own uv environment, the
// tests against the environment of the pytest runner that imports them, and every other file
// against the python3 on PATH. Basedpyright resolves imports from one interpreter per run, so one
// run over the folder cannot see each script's dependencies.
//   node scripts/basedpyright-maintainer.mjs   → exit 0 when every group passes

import { execFileSync, spawnSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { fail, isMain, ROOT } from './lib.mjs'

const CONFIG = 'scripts/pyrightconfig.maintainer.json'
const PYTEST_RUNNER = 'scripts/testers/run_pytest.py'
/** The paths the maintainer config includes, relative to the repository root. */
const COVERED = [
  'scripts/validators',
  'scripts/checkers',
  'scripts/generators',
  'scripts/testers/schemas',
  'scripts/testers/validators',
  PYTEST_RUNNER,
]

/**
 * The tracked Python files the maintainer config covers.
 * @param {string} root
 * @returns {string[]}
 */
export function coveredFiles(root) {
  return execFileSync('git', ['ls-files', '-z', '--', ...COVERED], { cwd: root, encoding: 'utf8' })
    .split('\0')
    .filter((f) => f.endsWith('.py'))
    .sort()
}

/**
 * The PEP 723 script whose environment checks `file`, or null for the python3 on PATH.
 * @param {string} root
 * @param {string} file
 * @returns {string | null}
 */
export function environmentFor(root, file) {
  if (
    file === PYTEST_RUNNER ||
    file.startsWith('scripts/testers/schemas/') ||
    file.startsWith('scripts/testers/validators/')
  ) {
    return PYTEST_RUNNER
  }
  const firstLine = readFileSync(join(root, file), 'utf8').split('\n', 1)[0] ?? ''
  return firstLine.includes('uv run --script') ? file : null
}

/**
 * The interpreter path for one environment, syncing a PEP 723 environment first: until
 * `uv sync --script` runs, `uv python find --script` returns the base interpreter.
 * @param {string} root
 * @param {string | null} script
 * @returns {string}
 */
function interpreter(root, script) {
  /** @param {string} cmd @param {string[]} args */
  const run = (cmd, args) => execFileSync(cmd, args, { cwd: root, encoding: 'utf8' }).trim()
  if (script === null) {
    return run('python3', ['-c', 'import sys; print(sys.executable)'])
  }
  run('uv', ['sync', '--quiet', '--script', script])
  return run('uv', ['python', 'find', '--script', script])
}

if (isMain(import.meta.url)) {
  /** @type {Map<string | null, string[]>} */
  const groups = new Map()
  for (const file of coveredFiles(ROOT)) {
    const env = environmentFor(ROOT, file)
    groups.set(env, [...(groups.get(env) ?? []), file])
  }
  if (groups.size === 0) {
    fail(`no tracked Python file under ${COVERED.join(', ')}`)
  }
  let failed = 0
  for (const [env, files] of groups) {
    const label = env ?? 'python3 on PATH'
    let python
    try {
      python = interpreter(ROOT, env)
    } catch (e) {
      console.error(`✖ ${label}: ${e instanceof Error ? e.message : String(e)}`)
      failed = 1
      continue
    }
    console.log(`▶ ${label}: ${files.length} file(s)`)
    const r = spawnSync(
      'basedpyright',
      ['--warnings', '-p', CONFIG, '--pythonpath', python, ...files],
      { cwd: ROOT, stdio: 'inherit' },
    )
    if (r.status !== 0) {
      failed = r.status ?? 1
    }
  }
  process.exit(failed)
}
