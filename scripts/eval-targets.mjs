#!/usr/bin/env node
// Prints, as a JSON array, the plugins whose eval suite CI should run. Evals are optional: only a
// plugin with an evals/ folder is ever selected, and a plugin without one never fails the job.
//   node scripts/eval-targets.mjs --changed <base> <head>  plugins with evals whose
//                                                                  plugin.json changed in base...head
//   node scripts/eval-targets.mjs --only <plugin|all>     a manual run

import { execFileSync } from 'node:child_process'
import { existsSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
import { fail, isMain, pluginDir, ROOT } from './lib.mjs'

const MANIFEST = /^plugins\/([^/]+)\/\.claude-plugin\/plugin\.json$/

/** @param {string} name */
const hasEvals = (name) => existsSync(join(pluginDir(name), 'evals'))

/**
 * Plugins with evals whose `plugin.json` changed between the merge base of `base` and `head`.
 * @param {string} base
 * @param {string} head
 * @returns {string[]}
 */
export function changedTargets(base, head) {
  const names = execFileSync(
    'git',
    ['-C', ROOT, 'diff', '--name-only', `${base}...${head}`, '--', 'plugins/'],
    { encoding: 'utf8' },
  )
    .split('\n')
    .map((path) => MANIFEST.exec(path)?.[1])
    .filter(/** @returns {name is string} */ (name) => Boolean(name))
  return [...new Set(names)].filter(hasEvals).sort()
}

/**
 * `all`: every plugin with evals. A name: that plugin, which must exist and have evals.
 * @param {string} only
 * @returns {string[]}
 */
export function onlyTargets(only) {
  if (only === 'all') {
    return readdirSync(join(ROOT, 'plugins'), { withFileTypes: true })
      .filter((d) => d.isDirectory() && hasEvals(d.name))
      .map((d) => d.name)
      .sort()
  }
  if (!existsSync(pluginDir(only))) {
    fail(`no plugin named "${only}"`)
  }
  if (!hasEvals(only)) {
    fail(`${only} has no evals/ folder`)
  }
  return [only]
}

if (isMain(import.meta.url)) {
  const [mode, ...args] = process.argv.slice(2)
  const [first, second] = args
  if (mode === '--changed' && args.length === 2 && first && second) {
    console.log(JSON.stringify(changedTargets(first, second)))
  } else if (mode === '--only' && args.length === 1 && first) {
    console.log(JSON.stringify(onlyTargets(first)))
  } else {
    fail('Usage: eval-targets.mjs --changed <base> <head> | --only <plugin|all>')
  }
}
