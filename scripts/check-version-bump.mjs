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
 * @param {string} base
 * @returns {{ errors: string[], notes: string[], checked: string[] }}
 */
export function checkVersionBump(base) {
  /** @type {string[]} */
  const errors = []
  /** @type {string[]} */
  const notes = []
  const changed = git(['diff', '--name-only', `${base}...HEAD`])
    .split('\n')
    .filter(Boolean)
  /** @type {Map<string, string[]>} */
  const byPlugin = new Map()
  for (const file of changed) {
    const m = file.match(/^plugins\/([^/]+)\/(.+)$/)
    const [, name, rest] = m ?? []
    if (name === undefined || rest === undefined) {
      continue
    }
    const files = byPlugin.get(name)
    if (files === undefined) {
      byPlugin.set(name, [rest])
    } else {
      files.push(rest)
    }
  }

  for (const [name, files] of byPlugin) {
    if (!existsSync(pluginDir(name))) {
      continue // plugin removed: handled by renames / check-repo
    }
    if (files.every((f) => DOC_ONLY.has(f))) {
      continue
    }

    let baseVersion = null
    try {
      baseVersion = JSON.parse(
        git(['show', `${base}:plugins/${name}/.claude-plugin/plugin.json`]),
      ).version
    } catch {
      continue // new plugin: nothing to compare against
    }
    const manifest = loadManifest(name)
    const version = manifest?.version
    if (!version || compareSemver(version, baseVersion) <= 0) {
      errors.push(
        `plugins/${name}: files changed (${files.join(', ')}) but version is still ${baseVersion}. Run bump-version.mjs ${name} <level>.`,
      )
      continue
    }
    const allowed = ['patch', 'minor', 'major'].map((level) => bumpSemver(baseVersion, level))
    const stepped = allowed.find((next) => compareSemver(version, next) === 0)
    if (stepped === undefined) {
      errors.push(
        `plugins/${name}: version jumps from ${baseVersion} to ${version}; one step above ${baseVersion} is ${allowed.join(', ')}. Run bump-version.mjs ${name} <level> once from ${baseVersion}.`,
      )
      continue
    }
    if (stepped === allowed[2] && compareSemver(baseVersion, '1.0.0') < 0) {
      notes.push(
        `plugins/${name}: ${baseVersion} → ${version} promises a stable interface: it needs Nery's explicit authorization (release-and-versioning, rule 4).`,
      )
    }
    const changelog = readText(join(pluginDir(name), 'CHANGELOG.md'))
    if (!changelogSection(changelog, version)) {
      errors.push(`plugins/${name}: CHANGELOG.md has no entry for ${version}`)
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
