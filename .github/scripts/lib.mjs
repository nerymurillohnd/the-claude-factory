// Shared helpers for the repository's maintenance scripts.
// Zero dependencies: runs on the Node.js version pinned in CI (24 LTS) and locally on Node ≥ 22.

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

export const SCRIPTS_DIR = dirname(fileURLToPath(import.meta.url));

/** Repository root. Overridable with TCF_ROOT so tests can run against a temp copy. */
export const ROOT = resolve(process.env.TCF_ROOT ?? join(SCRIPTS_DIR, '..', '..'));

export const MARKETPLACE_NAME = 'the-claude-factory';
export const REPO_SLUG = 'nerymurillohnd/the-claude-factory';
export const REPO_URL = `https://github.com/${REPO_SLUG}`;
export const TEMPLATES_DIR = join(ROOT, '.claude', 'templates', 'plugin');
export const MARKETPLACE_PATH = join(ROOT, '.claude-plugin', 'marketplace.json');
export const README_PATH = join(ROOT, 'README.md');

export const SEMVER = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/;
export const KEBAB = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

/** Plugin-name prefixes and words Claude Code rejects as passing for Anthropic's own (manifest reference). */
export const RESERVED_NAME = /^(claude|anthropics?|cc-plugin)(-|$)|^claude-code$|^claude-mods$/;

/** README sections every plugin must keep (matched on heading text, emoji-insensitive). */
export const REQUIRED_PLUGIN_SECTIONS = [
  'Why use it',
  "What's inside",
  'Requirements',
  'Installation',
  'Usage',
  'Updating',
  'Uninstalling',
  'Compatibility',
  'Changelog',
  'License',
];

/**
 * Surface profiles. A plugin declares one in plugin.json `metadata.surfaces` (Claude Code ignores
 * `metadata`); the README badge, the catalog column and check-repo.mjs all derive from it.
 * Matrix and rules: .claude/rules/cross-surface-compatibility.md
 */
export const SURFACE_PROFILES = {
  both: {
    surfaces: ['claude-code', 'cowork'],
    badge: 'Claude%20Code%20%C2%B7%20Cowork',
    text: '💻 Claude Code · 🤝 Cowork',
    catalog: '💻 Code · 🤝 Cowork',
    note: '',
  },
  'claude-code-only': {
    surfaces: ['claude-code'],
    badge: 'Claude%20Code%20only',
    text: '💻 **Claude Code only**',
    catalog: '💻 Code only',
    note: '💻 **Claude Code only** — <!-- TODO: say why, e.g. "it ships an LSP server" or "it needs bin/ executables" -->. It doesn\'t install or work in Cowork or Claude chat.\n\n',
  },
};

/** Returns the profile key for a surfaces array, or null when it matches none. */
export function surfaceProfileKey(surfaces) {
  if (!Array.isArray(surfaces)) return null;
  const key = [...surfaces].sort().join(',');
  for (const [name, profile] of Object.entries(SURFACE_PROFILES)) {
    if ([...profile.surfaces].sort().join(',') === key) return name;
  }
  return null;
}

export function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'));
}

export function writeJson(path, data) {
  writeFileSync(path, `${JSON.stringify(data, null, 2)}\n`);
}

export function readText(path) {
  return readFileSync(path, 'utf8');
}

export function loadMarketplace() {
  return readJson(MARKETPLACE_PATH);
}

export function loadCategories() {
  return readJson(join(SCRIPTS_DIR, 'categories.json')).categories;
}

export function pluginDir(name) {
  return join(ROOT, 'plugins', name);
}

export function loadManifest(name) {
  const path = join(pluginDir(name), '.claude-plugin', 'plugin.json');
  return existsSync(path) ? readJson(path) : null;
}

/** Compare two semver strings (pre-release ignored for ordering of the core triple). */
export function compareSemver(a, b) {
  const pa = a.split(/[-+]/)[0].split('.').map(Number);
  const pb = b.split(/[-+]/)[0].split('.').map(Number);
  for (let i = 0; i < 3; i += 1) {
    if (pa[i] !== pb[i]) return pa[i] > pb[i] ? 1 : -1;
  }
  return 0;
}

export function bumpSemver(version, level) {
  const [major, minor, patch] = version.split(/[-+]/)[0].split('.').map(Number);
  if (level === 'major') return `${major + 1}.0.0`;
  if (level === 'minor') return `${major}.${minor + 1}.0`;
  if (level === 'patch') return `${major}.${minor}.${patch + 1}`;
  throw new Error(`Unknown bump level "${level}" (use major, minor or patch)`);
}

export function today() {
  return new Date().toISOString().slice(0, 10);
}

/** Replace {{key}} placeholders. Unknown keys are left in place so checks can catch them. */
export function render(template, vars) {
  return template.replace(/\{\{(\w+)\}\}/g, (match, key) => (key in vars ? String(vars[key]) : match));
}

/** Extract the body of a "## [x.y.z]" section from a Keep a Changelog file. */
export function changelogSection(text, version) {
  const escaped = version.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp(`^## \\[${escaped}\\][^\\n]*\\n([\\s\\S]*?)(?=^## \\[|^\\[[^\\]]+\\]:|(?![\\s\\S]))`, 'm');
  const m = text.match(re);
  return m ? m[1].trim() : null;
}

/** True when the calling module is the script being executed (not imported). */
export function isMain(metaUrl) {
  return process.argv[1] !== undefined && metaUrl === pathToFileURL(resolve(process.argv[1])).href;
}

export function fail(message) {
  console.error(`✖ ${message}`);
  process.exit(1);
}
