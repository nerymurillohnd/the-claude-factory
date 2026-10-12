#!/usr/bin/env node
// Regenerates the generated blocks in README.md from marketplace.json + plugin manifests.
//   node .github/scripts/catalog.mjs          → rewrite README.md
//   node .github/scripts/catalog.mjs --check  → exit 1 if README.md is out of date (CI)

import { writeFileSync } from 'node:fs'
import { COMPONENT_TYPES, componentBadges, detectComponents } from './components.mjs'
import {
  isMain,
  loadCategories,
  loadManifest,
  loadMarketplace,
  MARKETPLACE_NAME,
  README_PATH,
  readText,
  SURFACE_PROFILES,
  surfaceProfileKey,
} from './lib.mjs'

function block(name) {
  return { start: `<!-- ${name}:start -->`, end: `<!-- ${name}:end -->` }
}

export function replaceBlock(text, name, content) {
  const { start, end } = block(name)
  const i = text.indexOf(start)
  const j = text.indexOf(end)
  if (i === -1 || j === -1 || j < i) {
    throw new Error(`README.md is missing the ${start} … ${end} markers`)
  }
  return `${text.slice(0, i + start.length)}\n${content}\n${text.slice(j)}`
}

function escapeCell(s) {
  return String(s ?? '')
    .replaceAll('|', '\\|')
    .replaceAll('\n', ' ')
}

export function buildCatalog() {
  const marketplace = loadMarketplace()
  const categories = loadCategories()
  const entries = marketplace.plugins.map((entry) => {
    const manifest = loadManifest(entry.name) ?? {}
    return {
      name: entry.name,
      displayName: entry.displayName ?? manifest.displayName ?? entry.name,
      description: entry.description ?? manifest.description ?? '',
      version: manifest.version ?? entry.version ?? '—',
      category: entry.category,
      components: componentBadges(detectComponents(entry.name)),
      worksIn: SURFACE_PROFILES[surfaceProfileKey(manifest.metadata?.surfaces)]?.catalog ?? '—',
    }
  })

  if (entries.length === 0) {
    return [
      '> [!NOTE]',
      '> 🏗️ **The factory floor is being set up.** The first plugins are on their way.',
      '> ⭐ Star or 👀 watch this repository to be notified when they ship.',
    ].join('\n')
  }

  const out = []
  const used = categories.filter((c) => entries.some((e) => e.category === c.id))

  out.push('| Category | Plugins |', '| :-- | :--: |')
  for (const c of used) {
    const n = entries.filter((e) => e.category === c.id).length
    out.push(`| [${c.emoji} ${c.title}](#${anchor(`${c.emoji} ${c.title}`)}) | ${n} |`)
  }

  for (const c of used) {
    out.push('', `### ${c.emoji} ${c.title}`, '', `*${c.description}*`, '')
    out.push(
      '| Plugin | What it does | Works in | Version | Includes |',
      '| :-- | :-- | :-- | :--: | :-- |',
    )
    for (const e of entries
      .filter((x) => x.category === c.id)
      .sort((a, b) => a.name.localeCompare(b.name))) {
      out.push(
        `| [**${escapeCell(e.displayName)}**](./plugins/${e.name}#readme)<br>\`${e.name}@${MARKETPLACE_NAME}\` | ${escapeCell(e.description)} | ${e.worksIn} | \`${e.version}\` | ${e.components || '—'} |`,
      )
    }
  }

  const legend = COMPONENT_TYPES.map((t) => `${t.emoji} ${t.label}`).join(' · ')
  out.push('', `<sub>**Legend:** ${legend}</sub>`)
  return out.join('\n')
}

/** GitHub heading anchor: lowercase, drop punctuation/emoji, spaces → hyphens. */
export function anchor(heading) {
  return heading
    .toLowerCase()
    .replace(/[^\p{L}\p{M}\p{N}\s_-]/gu, '')
    .replace(/\s/g, '-')
}

export function buildCountBadge() {
  const n = loadMarketplace().plugins.length
  return `[![Plugins](https://img.shields.io/badge/plugins-${n}-D97757?style=for-the-badge)](#-catalog)`
}

export function renderReadme(text) {
  let next = replaceBlock(text, 'catalog', buildCatalog())
  next = replaceBlock(next, 'plugin-count', buildCountBadge())
  return next
}

if (isMain(import.meta.url)) {
  const current = readText(README_PATH)
  const next = renderReadme(current)
  if (process.argv.includes('--check')) {
    if (current !== next) {
      console.error('✖ README.md catalog is out of date. Run: node .github/scripts/catalog.mjs')
      process.exit(1)
    }
    console.log('✔ README.md catalog is up to date')
  } else {
    writeFileSync(README_PATH, next)
    console.log(
      current === next
        ? '✔ README.md catalog already up to date'
        : '✔ README.md catalog regenerated',
    )
  }
}
