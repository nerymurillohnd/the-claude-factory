#!/usr/bin/env node
// Regenerates the plugins[] of .claude-plugin/marketplace.json from plugins/*/.claude-plugin/plugin.json.
// Every other top-level field of marketplace.json is kept as it is.
//   node scripts/generators/marketplace.mjs          → rewrite marketplace.json
//   node scripts/generators/marketplace.mjs --check  → exit 1 if marketplace.json is out of date (CI)

import { readdirSync } from 'node:fs'
import { join } from 'node:path'
import {
  fail,
  isMain,
  loadCategories,
  loadManifest,
  loadMarketplace,
  MARKETPLACE_PATH,
  ROOT,
  writeJson,
} from '../lib.mjs'

/**
 * The entry of one plugin folder, or the problems that keep it out.
 * @param {import('node:fs').Dirent} dirent
 * @param {Set<string>} categoryIds
 * @returns {{ entry?: import('../lib.mjs').MarketplaceEntry, problems: string[] }}
 */
function entryFor(dirent, categoryIds) {
  const scope = `plugins/${dirent.name}`
  /** @type {import('../lib.mjs').Manifest | null} */
  let manifest
  try {
    manifest = loadManifest(dirent.name)
  } catch (e) {
    return {
      problems: [
        `${scope}: .claude-plugin/plugin.json is not valid JSON: ${e instanceof Error ? e.message : String(e)}`,
      ],
    }
  }
  if (manifest === null) {
    return { problems: [`${scope}: .claude-plugin/plugin.json is missing`] }
  }
  /** @type {string[]} */
  const problems = []
  const { name, description } = manifest
  const category = manifest.metadata?.category
  if (name !== dirent.name) {
    problems.push(`${scope}: name "${String(name)}" does not match its directory`)
  }
  if (typeof description !== 'string' || description.trim() === '') {
    problems.push(`${scope}: description must be a non-empty string`)
  }
  if (category === undefined) {
    problems.push(`${scope}: metadata.category is required`)
  } else if (typeof category !== 'string' || !categoryIds.has(category)) {
    problems.push(
      `${scope}: metadata.category "${String(category)}" is not in categories.json (${[...categoryIds].join(', ')})`,
    )
  }
  if (problems.length > 0 || typeof description !== 'string' || typeof category !== 'string') {
    return { problems }
  }
  return {
    entry: { name: dirent.name, source: `./plugins/${dirent.name}`, description, category },
    problems,
  }
}

/**
 * One marketplace entry per real directory in plugins/, sorted by name.
 * Throws an Error listing every problem, so nothing is written from a partial read.
 * @returns {import('../lib.mjs').MarketplaceEntry[]}
 */
export function buildEntries() {
  const categoryIds = new Set(loadCategories().map((c) => c.id))
  /** @type {string[]} */
  const problems = []
  /** @type {import('../lib.mjs').MarketplaceEntry[]} */
  const entries = []
  for (const dirent of readdirSync(join(ROOT, 'plugins'), { withFileTypes: true })) {
    if (dirent.isSymbolicLink()) {
      problems.push(`plugins/${dirent.name}: must be a directory, not a symlink`)
    } else if (dirent.isDirectory()) {
      const result = entryFor(dirent, categoryIds)
      problems.push(...result.problems)
      if (result.entry !== undefined) {
        entries.push(result.entry)
      }
    }
  }
  if (problems.length > 0) {
    throw new Error(problems.join('\n'))
  }
  return entries.sort((a, b) => a.name.localeCompare(b.name))
}

/**
 * The current marketplace.json with plugins[] regenerated and every other field kept in place.
 * @returns {import('../lib.mjs').Marketplace}
 */
export function renderMarketplace() {
  return { ...loadMarketplace(), plugins: buildEntries() }
}

if (isMain(import.meta.url)) {
  /** @type {import('../lib.mjs').Marketplace} */
  let current
  /** @type {import('../lib.mjs').Marketplace} */
  let next
  try {
    current = loadMarketplace()
    next = renderMarketplace()
  } catch (e) {
    fail(e instanceof Error ? e.message : String(e))
  }
  const same = JSON.stringify(current, null, 2) === JSON.stringify(next, null, 2)
  if (process.argv.includes('--check')) {
    if (!same) {
      fail('marketplace.json plugins are out of date. Run: node scripts/generators/marketplace.mjs')
    }
    console.log('✔ marketplace.json plugins are up to date')
  } else {
    writeJson(MARKETPLACE_PATH, next)
    console.log(
      same
        ? '✔ marketplace.json plugins already up to date'
        : '✔ marketplace.json plugins regenerated',
    )
  }
}
