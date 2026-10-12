#!/usr/bin/env node
// Releases a plugin or the marketplace: bumps the version and turns [Unreleased] into a dated section.
//   node .github/scripts/bump-version.mjs <plugin-name|marketplace> <major|minor|patch>

import { existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { renderReadme } from './catalog.mjs';
import {
  bumpSemver,
  fail,
  loadManifest,
  loadMarketplace,
  MARKETPLACE_PATH,
  pluginDir,
  readText,
  README_PATH,
  REPO_URL,
  ROOT,
  today,
  writeJson,
} from './lib.mjs';

const [target, level] = process.argv.slice(2);
if (!target || !level) fail('Usage: bump-version.mjs <plugin-name|marketplace> <major|minor|patch>');

const isMarketplace = target === 'marketplace';
let current;
let next;
let changelogPath;
let tagPrefix;

if (isMarketplace) {
  const mp = loadMarketplace();
  current = mp.version;
  next = bumpSemver(current, level);
  mp.version = next;
  changelogPath = join(ROOT, 'CHANGELOG.md');
  tagPrefix = 'marketplace--v';
  rollChangelog();
  writeJson(MARKETPLACE_PATH, mp);
} else {
  const manifest = loadManifest(target);
  if (!manifest) fail(`plugins/${target}/.claude-plugin/plugin.json not found`);
  current = manifest.version;
  next = bumpSemver(current, level);
  manifest.version = next;
  changelogPath = join(pluginDir(target), 'CHANGELOG.md');
  tagPrefix = `${target}--v`;
  rollChangelog();
  writeJson(join(pluginDir(target), '.claude-plugin', 'plugin.json'), manifest);
}

writeFileSync(README_PATH, renderReadme(readText(README_PATH)));
console.log(`✔ ${target}: ${current} → ${next}`);

function rollChangelog() {
  if (!existsSync(changelogPath)) fail(`${changelogPath} not found`);
  let text = readText(changelogPath);
  const m = text.match(/^## \[Unreleased\]\s*\n([\s\S]*?)(?=^## \[|^\[[^\]]+\]:|(?![\s\S]))/m);
  if (!m) fail('CHANGELOG.md has no "## [Unreleased]" section');
  if (!m[1].trim()) fail('[Unreleased] is empty — document the changes before bumping');

  text = text.replace(/^## \[Unreleased\]\s*\n/m, `## [Unreleased]\n\n## [${next}] - ${today()}\n\n`);
  text = text.replace(/\n{3,}/g, '\n\n');

  // Link references: [Unreleased] compares from the new tag; add the new version's tag link.
  const unreleasedLink = `[Unreleased]: ${REPO_URL}/compare/${tagPrefix}${next}...HEAD`;
  const versionLink = `[${next}]: ${REPO_URL}/releases/tag/${tagPrefix}${next}`;
  if (/^\[Unreleased\]:.*$/m.test(text)) text = text.replace(/^\[Unreleased\]:.*$/m, `${unreleasedLink}\n${versionLink}`);
  else text = `${text.trimEnd()}\n\n${unreleasedLink}\n${versionLink}\n`;
  writeFileSync(changelogPath, text);
}
