#!/usr/bin/env node
// Prints the release tag and notes for a plugin (or the marketplace) at its current version.
//   node .github/scripts/release-notes.mjs <plugin-name|marketplace> --tag    → prints the tag
//   node .github/scripts/release-notes.mjs <plugin-name|marketplace>          → prints the notes

import { join } from 'node:path'
import {
  changelogSection,
  fail,
  loadManifest,
  loadMarketplace,
  pluginDir,
  ROOT,
  readText,
} from './lib.mjs'

const target = process.argv[2]
if (!target) {
  fail('Usage: release-notes.mjs <plugin-name|marketplace> [--tag]')
}

const isMarketplace = target === 'marketplace'
const version = isMarketplace ? loadMarketplace().version : loadManifest(target)?.version
if (!version) {
  fail(`No version found for ${target}`)
}
const tag = isMarketplace ? `marketplace--v${version}` : `${target}--v${version}`

if (process.argv.includes('--tag')) {
  console.log(tag)
} else {
  const changelog = readText(
    isMarketplace ? join(ROOT, 'CHANGELOG.md') : join(pluginDir(target), 'CHANGELOG.md'),
  )
  const body = changelogSection(changelog, version)
  if (!body) {
    fail(`No CHANGELOG entry for ${tag}`)
  }
  const install = isMarketplace
    ? '```bash\nclaude plugin marketplace update the-claude-factory\n```'
    : `\`\`\`bash\nclaude plugin update ${target}@the-claude-factory\n\`\`\``
  console.log(`${body}\n\n---\n\n**Update:**\n\n${install}`)
}
