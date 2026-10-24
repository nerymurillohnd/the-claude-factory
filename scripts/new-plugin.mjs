#!/usr/bin/env node
// Scaffolds a plugin from .claude/templates/plugin and registers it in marketplace.json.
//   node scripts/new-plugin.mjs --name my-plugin --category development \
//     --description "One sentence." [--display-name "My Plugin"] [--emoji 🧰] [--min-claude-code 2.1.292]
//     [--claude-code-only]   (default: works in Claude Code and the Claude app)

import { cpSync, existsSync, mkdirSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { parseArgs } from 'node:util'
import { renderReadme } from './generators/catalog.mjs'
import { buildEntries, renderMarketplace } from './generators/marketplace.mjs'
import {
  fail,
  KEBAB,
  loadCategories,
  loadMarketplace,
  MARKETPLACE_PATH,
  pluginDir,
  README_PATH,
  RESERVED_NAME,
  readText,
  render,
  SURFACE_PROFILES,
  TEMPLATES_DIR,
  today,
  writeJson,
} from './lib.mjs'

const { values } = parseArgs({
  options: {
    name: { type: 'string' },
    category: { type: 'string' },
    description: { type: 'string' },
    'display-name': { type: 'string' },
    emoji: { type: 'string', default: '🧩' },
    'min-claude-code': { type: 'string', default: '2.1.292' },
    'claude-code-only': { type: 'boolean', default: false },
  },
})

const { name, category, description } = values
if (!name || !category || !description) {
  fail('Usage: --name <kebab-name> --category <id> --description "<one sentence>"')
}
if (!KEBAB.test(name)) {
  fail(`"${name}" is not kebab-case`)
}
if (RESERVED_NAME.test(name)) {
  fail(`"${name}" passes as an Anthropic plugin name and is rejected by Claude Code`)
}
const categories = loadCategories()
const cat = categories.find((c) => c.id === category)
if (!cat) {
  fail(`Unknown category "${category}". Valid: ${categories.map((c) => c.id).join(', ')}`)
}

const dir = pluginDir(name)
if (existsSync(dir)) {
  fail(`plugins/${name} already exists`)
}
const marketplace = loadMarketplace()
if (marketplace.plugins.some((p) => p.name === name)) {
  fail(`"${name}" is already listed in marketplace.json`)
}
if (marketplace.renames && name in marketplace.renames) {
  fail(`"${name}" is a retired name in renames; pick another`)
}

const displayName =
  values['display-name'] ??
  name
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
const profile = SURFACE_PROFILES[values['claude-code-only'] ? 'claude-code-only' : 'both']
const vars = {
  name,
  displayName,
  description,
  category,
  categoryBadge: encodeURIComponent(cat.title).replaceAll('-', '--'),
  emoji: values.emoji,
  minClaudeCode: values['min-claude-code'],
  date: today(),
  surfacesBadge: profile.badge,
  surfacesText: profile.text,
  surfacesNote: profile.note,
  surfacesJson: JSON.stringify(profile.surfaces),
}
// plugin.json takes each value inside a JSON string, so quotes and backslashes are escaped there.
/** @type {Record<string, unknown>} */
const jsonVars = Object.fromEntries(
  Object.entries(vars).map(([key, value]) => [
    key,
    typeof value === 'string' && key !== 'surfacesJson'
      ? JSON.stringify(value).slice(1, -1)
      : value,
  ]),
)

// The marketplace is rebuilt from every plugin directory: stop before writing if one is broken.
try {
  buildEntries()
} catch (e) {
  fail(e instanceof Error ? e.message : String(e))
}

mkdirSync(join(dir, '.claude-plugin'), { recursive: true })
for (const file of readdirSync(TEMPLATES_DIR)) {
  const src = join(TEMPLATES_DIR, file)
  if (file === 'LICENSE') {
    cpSync(src, join(dir, file))
    continue
  }
  const target =
    file === 'plugin.json' ? join(dir, '.claude-plugin', 'plugin.json') : join(dir, file)
  writeFileSync(target, render(readText(src), file === 'plugin.json' ? jsonVars : vars))
}

try {
  writeJson(MARKETPLACE_PATH, renderMarketplace())
} catch (e) {
  rmSync(dir, { recursive: true, force: true })
  fail(`plugins/${name} was removed again: ${e instanceof Error ? e.message : String(e)}`)
}
writeFileSync(README_PATH, renderReadme(readText(README_PATH)))

console.log(`✔ Scaffolded plugins/${name} and registered it in marketplace.json`)
console.log('  Next: add components, resolve every TODO in README.md, then run the verify skill.')
