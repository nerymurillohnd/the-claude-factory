#!/usr/bin/env node
// Prints the release tag and notes for a plugin at its current version.
//   node scripts/release-notes.mjs <plugin-name> --tag    → prints the tag
//   node scripts/release-notes.mjs <plugin-name>          → prints the notes

import { join } from 'node:path'
import {
  changelogSection,
  fail,
  loadManifest,
  MARKETPLACE_NAME,
  pluginDir,
  pluginTag,
  readText,
} from './lib.mjs'

const target = process.argv[2]
if (!target) {
  fail('Usage: release-notes.mjs <plugin-name> [--tag]')
}

const version = loadManifest(target)?.version
if (!version) {
  fail(`No version found for ${target}`)
}
const tag = pluginTag(target, version)

if (process.argv.includes('--tag')) {
  console.log(tag)
} else {
  const body = changelogSection(readText(join(pluginDir(target), 'CHANGELOG.md')), version)
  if (!body) {
    fail(`No CHANGELOG entry for ${tag}`)
  }
  const install = `\`\`\`bash\nclaude plugin update ${target}@${MARKETPLACE_NAME}\n\`\`\``
  console.log(`${body}\n\n---\n\n**Update:**\n\n${install}`)
}
