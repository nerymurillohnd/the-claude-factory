#!/usr/bin/env node
// Releases a plugin: bumps the version and turns [Unreleased] into a dated section.
//   node scripts/bump-version.mjs <plugin-name> <major|minor|patch>

import { existsSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { renderReadme } from './catalog.mjs'
import {
  bumpSemver,
  changelogSection,
  fail,
  loadManifest,
  manifestPath,
  pluginDir,
  pluginTag,
  README_PATH,
  REPO_URL,
  readText,
  today,
  writeJson,
} from './lib.mjs'

const [target, level] = process.argv.slice(2)
if (!target || !level) {
  fail('Usage: bump-version.mjs <plugin-name> <major|minor|patch>')
}
if (target === 'marketplace') {
  fail(
    "The marketplace has no version. Add a line under today's date heading in CHANGELOG.md instead.",
  )
}

const manifest = loadManifest(target)
if (!manifest) {
  fail(`plugins/${target}/.claude-plugin/plugin.json not found`)
}
const current = manifest.version
if (!current) {
  fail(`plugins/${target}/.claude-plugin/plugin.json has no version`)
}
const next = bumpSemver(current, level)
manifest.version = next
const changelogPath = join(pluginDir(target), 'CHANGELOG.md')
const tag = pluginTag(target, next)
rollChangelog()
writeJson(manifestPath(target), manifest)

writeFileSync(README_PATH, renderReadme(readText(README_PATH)))
console.log(`✔ ${target}: ${current} → ${next}`)

function rollChangelog() {
  if (!existsSync(changelogPath)) {
    fail(`${changelogPath} not found`)
  }
  let text = readText(changelogPath)
  const unreleased = changelogSection(text, 'Unreleased')
  if (unreleased === null) {
    fail('CHANGELOG.md has no "## [Unreleased]" section')
  }
  if (!unreleased) {
    fail('[Unreleased] is empty — document the changes before bumping')
  }

  text = text.replace(
    /^## \[Unreleased\]\s*\n/m,
    `## [Unreleased]\n\n## [${next}] - ${today()}\n\n`,
  )
  text = text.replace(/\n{3,}/g, '\n\n')

  // Link references: [Unreleased] compares from the new tag; add the new version's tag link.
  const unreleasedLink = `[Unreleased]: ${REPO_URL}/compare/${tag}...HEAD`
  const versionLink = `[${next}]: ${REPO_URL}/releases/tag/${tag}`
  if (/^\[Unreleased\]:.*$/m.test(text)) {
    text = text.replace(/^\[Unreleased\]:.*$/m, `${unreleasedLink}\n${versionLink}`)
  } else {
    text = `${text.trimEnd()}\n\n${unreleasedLink}\n${versionLink}\n`
  }
  writeFileSync(changelogPath, text)
}
