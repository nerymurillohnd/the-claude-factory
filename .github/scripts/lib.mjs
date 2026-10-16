#!/usr/bin/env node
// Shared helpers for the repository's maintenance scripts.
// Zero dependencies: runs on the Node.js version pinned in CI (24 LTS) and locally on Node ≥ 22.

import { existsSync, readFileSync, realpathSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

export const SCRIPTS_DIR = dirname(fileURLToPath(import.meta.url))

/** Repository root. Overridable with TCF_ROOT so tests can run against a temp copy. */
const { TCF_ROOT } = process.env
export const ROOT = resolve(TCF_ROOT ?? join(SCRIPTS_DIR, '..', '..'))

/**
 * A plugin entry of marketplace.json, as read; check-repo.mjs validates it.
 * @typedef {object} MarketplaceEntry
 * @property {string} name
 * @property {string} [source]
 * @property {string} [description]
 * @property {string} [displayName]
 * @property {string} [version]
 * @property {string} [category]
 */
/**
 * marketplace.json, as read; check-repo.mjs validates it.
 * @typedef {object} Marketplace
 * @property {string} [$schema]
 * @property {string} [name]
 * @property {string} [description]
 * @property {MarketplaceEntry[]} plugins
 * @property {Record<string, string | null>} [renames]
 */
/** @typedef {{ id: string, emoji: string, title: string, description: string }} Category */
/**
 * A plugin's .claude-plugin/plugin.json, as read; check-repo.mjs validates it.
 * @typedef {object} Manifest
 * @property {string} [name]
 * @property {string} [version]
 * @property {string} [displayName]
 * @property {string} [description]
 * @property {unknown} [author]
 * @property {string[]} [keywords]
 * @property {string} [license]
 * @property {string} [homepage]
 * @property {string} [repository]
 * @property {unknown} [hooks]
 * @property {unknown} [mcpServers]
 * @property {unknown} [lspServers]
 * @property {{ monitors?: unknown }} [experimental]
 * @property {{ surfaces?: unknown }} [metadata]
 */

export const MARKETPLACE_NAME = 'the-claude-factory'
export const REPO_SLUG = 'nerymurillohnd/the-claude-factory'
export const REPO_URL = `https://github.com/${REPO_SLUG}`
export const TEMPLATES_DIR = join(ROOT, '.claude', 'templates', 'plugin')
export const MARKETPLACE_PATH = join(ROOT, '.claude-plugin', 'marketplace.json')
export const README_PATH = join(ROOT, 'README.md')

export const SEMVER =
  /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/
export const KEBAB = /^[a-z0-9]+(?:-[a-z0-9]+)*$/

/** Plugin-name prefixes and words Claude Code rejects as passing for Anthropic's own (manifest reference). */
export const RESERVED_NAME = /^(claude|anthropics?|cc-plugin)(-|$)|^claude-code$|^claude-mods$/

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
]

/**
 * Surface profiles. A plugin declares one in plugin.json `metadata.surfaces` (Claude Code ignores
 * `metadata`); the README badge, the catalog column and check-repo.mjs all derive from it.
 * Matrix: docs/compatibility.md
 */
export const SURFACE_PROFILES = {
  both: {
    surfaces: ['claude-code', 'claude-app'],
    badge: 'Claude%20Code%20%C2%B7%20Claude%20app',
    text: '💻 Claude Code · 🖥️ Claude app',
    catalog: '💻 Code · 🖥️ Claude app',
    note: '',
  },
  'claude-code-only': {
    surfaces: ['claude-code'],
    badge: 'Claude%20Code%20only',
    text: '💻 **Claude Code only**',
    catalog: '💻 Code only',
    note: '💻 **Claude Code only** — <!-- TODO: say why, e.g. "it ships an LSP server" or "it needs bin/ executables" -->. It doesn\'t install in the Claude app (chat or Cowork).\n\n',
  },
}

/**
 * Returns the profile key for a surfaces array, or null when it matches none.
 * @param {unknown} surfaces
 * @returns {keyof typeof SURFACE_PROFILES | null}
 */
export function surfaceProfileKey(surfaces) {
  if (!Array.isArray(surfaces)) {
    return null
  }
  const key = [...surfaces].sort().join(',')
  // Object.keys of the literal above returns exactly its keys.
  for (const name of /** @type {(keyof typeof SURFACE_PROFILES)[]} */ (
    Object.keys(SURFACE_PROFILES)
  )) {
    if ([...SURFACE_PROFILES[name].surfaces].sort().join(',') === key) {
      return name
    }
  }
  return null
}

/**
 * @param {string} path
 * @returns {any}
 */
export function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'))
}

/**
 * @param {string} path
 * @param {unknown} data
 * @returns {void}
 */
export function writeJson(path, data) {
  writeFileSync(path, `${JSON.stringify(data, null, 2)}\n`)
}

/**
 * @param {string} path
 * @returns {string}
 */
export function readText(path) {
  return readFileSync(path, 'utf8')
}

/** @returns {Marketplace} */
export function loadMarketplace() {
  return readJson(MARKETPLACE_PATH)
}

/** @returns {Category[]} */
export function loadCategories() {
  return readJson(join(SCRIPTS_DIR, 'categories.json')).categories
}

/**
 * @param {string} name
 * @returns {string}
 */
export function pluginDir(name) {
  return join(ROOT, 'plugins', name)
}

/**
 * @param {string} name
 * @returns {Manifest | null}
 */
export function loadManifest(name) {
  const path = join(pluginDir(name), '.claude-plugin', 'plugin.json')
  return existsSync(path) ? readJson(path) : null
}

/**
 * The numeric MAJOR.MINOR.PATCH of a version, pre-release and build metadata dropped.
 * @param {string} version
 * @returns {number[]}
 */
function coreTriple(version) {
  return (version.split(/[-+]/)[0] ?? '').split('.').map(Number)
}

/**
 * Compare two semver strings (pre-release ignored for ordering of the core triple).
 * @param {string} a
 * @param {string} b
 * @returns {number}
 */
export function compareSemver(a, b) {
  const pa = coreTriple(a)
  const pb = coreTriple(b)
  for (let i = 0; i < 3; i += 1) {
    const x = pa[i] ?? 0
    const y = pb[i] ?? 0
    if (x !== y) {
      return x > y ? 1 : -1
    }
  }
  return 0
}

/**
 * @param {string} version
 * @param {string} level
 * @returns {string}
 */
export function bumpSemver(version, level) {
  const [major = 0, minor = 0, patch = 0] = coreTriple(version)
  if (level === 'major') {
    return `${major + 1}.0.0`
  }
  if (level === 'minor') {
    return `${major}.${minor + 1}.0`
  }
  if (level === 'patch') {
    return `${major}.${minor}.${patch + 1}`
  }
  throw new Error(`Unknown bump level "${level}" (use major, minor or patch)`)
}

/** @returns {string} */
export function today() {
  return new Date().toISOString().slice(0, 10)
}

/**
 * Replace {{key}} placeholders. Unknown keys are left in place so checks can catch them.
 * @param {string} template
 * @param {Record<string, unknown>} vars
 * @returns {string}
 */
export function render(template, vars) {
  return template.replace(
    /\{\{(\w+)\}\}/g,
    (/** @type {string} */ match, /** @type {string} */ key) =>
      key in vars ? String(vars[key]) : match,
  )
}

/**
 * Extract the body of a "## [x.y.z]" section from a Keep a Changelog file.
 * @param {string} text
 * @param {string} version
 * @returns {string | null}
 */
export function changelogSection(text, version) {
  const escaped = version.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const re = new RegExp(
    `^## \\[${escaped}\\][^\\n]*\\n([\\s\\S]*?)(?=^## \\[|^\\[[^\\]]+\\]:|(?![\\s\\S]))`,
    'm',
  )
  const m = text.match(re)
  return m ? (m[1] ?? '').trim() : null
}

/**
 * True when the module is the script Node started. import.meta.url is the real path, so resolve
 * symlinks in argv[1] too (macOS temp folders live under the /var → /private/var link).
 * @param {string} metaUrl
 * @returns {boolean}
 */
export function isMain(metaUrl) {
  return (
    process.argv[1] !== undefined && metaUrl === pathToFileURL(realpathSync(process.argv[1])).href
  )
}

/**
 * @param {string} message
 * @returns {never}
 */
export function fail(message) {
  console.error(`✖ ${message}`)
  process.exit(1)
}
