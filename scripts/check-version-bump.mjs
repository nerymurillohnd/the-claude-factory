#!/usr/bin/env node
// Fails when a plugin's files changed since <base-ref> without a one-step version bump (the next
// patch, minor or major; a skipped version fails) and its changelog entry. A step from 0.x to
// 1.0.0 passes with a note: it needs Nery's explicit authorization.
//   node scripts/check-version-bump.mjs <base-ref>
// Documentation-only edits (README.md, CHANGELOG.md [Unreleased]) do not reach users through
// `claude plugin update`, so changes limited to README.md do not require a bump.

import { execFileSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { join } from 'node:path'
import {
  bumpSemver,
  changelogSection,
  compareSemver,
  fail,
  isMain,
  loadManifest,
  pluginDir,
  ROOT,
  readText,
} from './lib.mjs'

const DOC_ONLY = new Set(['README.md'])
// plugins/<name>/<path inside the plugin>
const PLUGIN_FILE = /^plugins\/([^/]+)\/(.+)$/

/**
 * @param {string[]} args
 * @returns {string}
 */
function git(args) {
  // stderr is piped, not inherited: `git show` on a new plugin fails on purpose (no base version
  // to compare), and an inherited stderr would print that expected `fatal:` into the run's output.
  // A real failure still throws, and its message keeps git's stderr.
  return execFileSync('git', args, {
    cwd: ROOT,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  }).trim()
}

/**
 * The files changed under each plugin since `base`, relative to the plugin folder.
 * @param {string} base
 * @returns {Map<string, string[]>}
 */
function changedFilesByPlugin(base) {
  /** @type {Map<string, string[]>} */
  const byPlugin = new Map()
  for (const file of git(['diff', '--name-only', `${base}...HEAD`]).split('\n')) {
    const [, name, rest] = file.match(PLUGIN_FILE) ?? []
    if (name !== undefined && rest !== undefined) {
      byPlugin.set(name, [...(byPlugin.get(name) ?? []), rest])
    }
  }
  return byPlugin
}

/**
 * The bump check of one changed plugin: an error, a note, or neither.
 * @param {string} name
 * @param {string[]} files changed files, relative to the plugin folder
 * @param {string} base
 * @returns {{ error?: string, note?: string }}
 */
function bumpResult(name, files, base) {
  if (!existsSync(pluginDir(name)) || files.every((f) => DOC_ONLY.has(f))) {
    return {} // removed (handled by renames / check-repo) or documentation only
  }
  let baseVersion = null
  try {
    baseVersion = JSON.parse(
      git(['show', `${base}:plugins/${name}/.claude-plugin/plugin.json`]),
    ).version
  } catch {
    return {} // new plugin: nothing to compare against
  }
  const version = loadManifest(name)?.version
  if (!version || compareSemver(version, baseVersion) <= 0) {
    return {
      error: `plugins/${name}: files changed (${files.join(', ')}) but version is still ${baseVersion}. Run bump-version.mjs ${name} <level>.`,
    }
  }
  const allowed = ['patch', 'minor', 'major'].map((level) => bumpSemver(baseVersion, level))
  const stepped = allowed.find((next) => compareSemver(version, next) === 0)
  if (stepped === undefined) {
    return {
      error: `plugins/${name}: version jumps from ${baseVersion} to ${version}; one step above ${baseVersion} is ${allowed.join(', ')}. Run bump-version.mjs ${name} <level> once from ${baseVersion}.`,
    }
  }
  /** @type {{ error?: string, note?: string }} */
  const result = {}
  if (stepped === allowed[2] && compareSemver(baseVersion, '1.0.0') < 0) {
    result.note = `plugins/${name}: ${baseVersion} → ${version} promises a stable interface: it needs Nery's explicit authorization (release-and-versioning, rule 4).`
  }
  if (!changelogSection(readText(join(pluginDir(name), 'CHANGELOG.md')), version)) {
    result.error = `plugins/${name}: CHANGELOG.md has no entry for ${version}`
  }
  return result
}

/**
 * @param {string} base
 * @returns {{ errors: string[], notes: string[], checked: string[] }}
 */
export function checkVersionBump(base) {
  /** @type {string[]} */
  const errors = []
  /** @type {string[]} */
  const notes = []
  const byPlugin = changedFilesByPlugin(base)
  for (const [name, files] of byPlugin) {
    const { error, note } = bumpResult(name, files, base)
    if (note !== undefined) {
      notes.push(note)
    }
    if (error !== undefined) {
      errors.push(error)
    }
  }
  return { errors, notes, checked: [...byPlugin.keys()] }
}

if (isMain(import.meta.url)) {
  const base = process.argv[2]
  if (!base) {
    fail('Usage: check-version-bump.mjs <base-ref>')
  }
  const { errors, notes, checked } = checkVersionBump(base)
  for (const n of notes) {
    console.error(`! ${n}`)
  }
  for (const e of errors) {
    console.error(`✖ ${e}`)
  }
  if (errors.length) {
    process.exit(1)
  }
  console.log(`✔ Version bumps OK (${checked.length ? checked.join(', ') : 'no plugin changes'})`)
}
