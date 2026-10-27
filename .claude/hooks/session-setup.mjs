#!/usr/bin/env node
// SessionStart setup for The Claude Factory checkout, called by .claude/hooks/checkout.sh: syncs node_modules with
// the lockfile, runs the maintainer validators, lists outdated packages and compares the installed
// packages with the global tools run by bare name. Prints plain-text lines for Claude's context and
// always exits 0, so a failed probe never stops the session.

import { execFileSync, spawnSync } from 'node:child_process'
import { existsSync, readFileSync } from 'node:fs'

/** Global CLIs that a devDependency of the same tool would shadow under `npx`. */
const GLOBAL_CLI = { '@biomejs/biome': 'biome', typescript: 'tsc' }

/** @typedef {{ packages?: Record<string, { version?: string, optional?: boolean }> }} Lockfile */
/** @typedef {{ version?: string, devDependencies?: Record<string, string> }} PackageJson */

/**
 * @template T
 * @param {string} path
 * @returns {T | undefined}
 */
function readJson(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch {
    return undefined
  }
}

/**
 * @param {string} cmd
 * @param {string[]} args
 */
function run(cmd, args) {
  const r = spawnSync(cmd, args, { encoding: 'utf8' })
  return { ok: r.status === 0, out: `${r.stdout ?? ''}${r.stderr ?? ''}`.trim() }
}

// npm ci only when node_modules no longer matches the lockfile: a clean start costs nothing, and
// the lockfile is never rewritten, as `npm install` could do. Optional packages for other platforms
// are never installed, so their absence still counts as in sync.
function syncNodeModules() {
  const want = /** @type {Lockfile | undefined} */ (readJson('package-lock.json'))?.packages
  if (!want) {
    return '- npm: no readable package-lock.json.'
  }
  // Read each package's own package.json: the hidden lockfile in node_modules stays put when a
  // package folder is deleted by hand.
  const inSync = Object.entries(want).every(([key, pkg]) => {
    if (key === '' || !key.startsWith('node_modules/')) {
      return true
    }
    const installed = /** @type {PackageJson | undefined} */ (readJson(`${key}/package.json`))
    return installed ? installed.version === pkg.version : Boolean(pkg.optional)
  })
  if (inSync) {
    return '- npm: node_modules matches package-lock.json.'
  }
  const r = run('npm', ['ci', '--no-audit', '--no-fund'])
  return r.ok
    ? '- npm: ran npm ci; node_modules now matches package-lock.json.'
    : `- npm: npm ci FAILED: ${r.out.split('\n').slice(-3).join(' | ')}`
}

function runValidators() {
  const r = run('npm', ['run', '--silent', 'validate'])
  if (r.ok) {
    return '- Validators (scripts/validators/): all passed.'
  }
  const lines = r.out
    .split('\n')
    .filter((l) => /✖|error/i.test(l))
    .slice(0, 20)
  return ['- Validators (scripts/validators/) FAILED:', ...lines.map((l) => `    ${l}`)].join('\n')
}

function reportOutdated() {
  // npm outdated exits 1 when something is outdated; the JSON on stdout is what counts.
  const r = spawnSync('npm', ['outdated', '--json'], { encoding: 'utf8' })
  /** @type {Record<string, {current?: string, wanted: string, latest: string}> | undefined} */
  let rows
  try {
    rows = JSON.parse(r.stdout || '{}')
  } catch {
    return '- npm outdated: could not read its output.'
  }
  const entries = Object.entries(rows ?? {})
  if (entries.length === 0) {
    return '- npm outdated: every package is on its latest version.'
  }
  return [
    '- npm outdated:',
    ...entries.map(
      ([name, v]) =>
        `    ${name}: installed ${v.current ?? 'none'}, wanted ${v.wanted}, latest ${v.latest}`,
    ),
  ].join('\n')
}

/** @param {string} cmd */
function globalVersion(cmd) {
  try {
    return (
      execFileSync(cmd, ['--version'], { encoding: 'utf8' }).match(/\d+\.\d+\.\d+/)?.[0] ??
      'unknown'
    )
  } catch {
    return 'not found'
  }
}

// @types/node follows the global node major; a pinned tool package should equal the global CLI the
// editor uses, so both report the same findings.
function compareWithGlobals() {
  const dev =
    /** @type {PackageJson | undefined} */ (readJson('package.json'))?.devDependencies ?? {}
  const lines = []
  for (const name of Object.keys(dev)) {
    const pkg = /** @type {PackageJson | undefined} */ (
      readJson(`node_modules/${name}/package.json`)
    )
    const have = pkg?.version ?? 'not installed'
    if (name === '@types/node') {
      const node = process.versions.node
      const same = have.split('.')[0] === node.split('.')[0]
      lines.push(`${same ? 'OK' : 'MISMATCH'} @types/node ${have} vs global node ${node} (majors)`)
    } else if (name in GLOBAL_CLI) {
      const cli = GLOBAL_CLI[/** @type {keyof typeof GLOBAL_CLI} */ (name)]
      const g = globalVersion(cli)
      lines.push(`${g === have ? 'OK' : 'MISMATCH'} ${name} ${have} vs global ${cli} ${g}`)
    }
  }
  return ['- Installed vs global:', ...lines.map((l) => `    ${l}`)].join('\n')
}

// Husky's prepare sets core.hooksPath on npm ci; a clone set up some other way has no git hooks.
function reportGitHooks() {
  const r = run('git', ['config', '--get', 'core.hooksPath'])
  return r.out === '.husky/_'
    ? '- Git hooks: Husky is active (pre-commit biome check --staged and npm test, pre-push npm run gates).'
    : `- Git hooks: NOT active (core.hooksPath is "${r.out}"); run npm run prepare.`
}

if (!existsSync('package.json')) {
  console.log('- Setup skipped: no package.json in the project root.')
} else {
  for (const step of [
    syncNodeModules,
    reportGitHooks,
    runValidators,
    reportOutdated,
    compareWithGlobals,
  ]) {
    try {
      console.log(step())
    } catch (e) {
      console.log(`- ${step.name} could not run: ${e instanceof Error ? e.message : e}`)
    }
  }
}
