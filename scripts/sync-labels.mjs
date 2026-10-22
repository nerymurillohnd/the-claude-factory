#!/usr/bin/env node
// Creates or updates the repository labels from .github/labels.json plus one "plugin: <name>"
// label per catalog entry. Idempotent. Requires an authenticated `gh` CLI with repo access.
//   node scripts/sync-labels.mjs [--dry-run]

import { execFileSync } from 'node:child_process'
import { join } from 'node:path'
import { loadMarketplace, REPO_SLUG, ROOT, readJson } from './lib.mjs'

const dryRun = process.argv.includes('--dry-run')
const labels = [
  ...readJson(join(ROOT, '.github', 'labels.json')),
  ...loadMarketplace().plugins.map((p) => ({
    name: `plugin: ${p.name}`,
    color: 'EDEDED',
    description: `Issues about the ${p.name} plugin`,
  })),
]

for (const l of labels) {
  const args = [
    'label',
    'create',
    l.name,
    '--repo',
    REPO_SLUG,
    '--color',
    l.color,
    '--description',
    l.description,
    '--force',
  ]
  if (dryRun) {
    console.log(`gh ${args.map((a) => (a.includes(' ') ? JSON.stringify(a) : a)).join(' ')}`)
    continue
  }
  execFileSync('gh', args, { stdio: 'inherit' })
}
console.log(`✔ ${labels.length} labels ${dryRun ? 'planned' : 'synced'}`)
