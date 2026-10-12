#!/usr/bin/env node
// Repository policy checks that `claude plugin validate` does not cover.
// Exit 0 = pass, exit 1 = at least one error.

import { execFileSync } from 'node:child_process'
import { existsSync, lstatSync, readdirSync, statSync } from 'node:fs'
import { join, relative, sep } from 'node:path'
import { renderReadme } from './catalog.mjs'
import { COMPONENT_TYPES, detectComponents } from './components.mjs'
import {
  changelogSection,
  isMain,
  KEBAB,
  loadCategories,
  loadManifest,
  loadMarketplace,
  MARKETPLACE_NAME,
  pluginDir,
  README_PATH,
  REPO_URL,
  REQUIRED_PLUGIN_SECTIONS,
  RESERVED_NAME,
  ROOT,
  readText,
  SEMVER,
  SURFACE_PROFILES,
  surfaceProfileKey,
} from './lib.mjs'

// ── Portability rules of Anthropic's plugin directory (claude.com/docs/plugins/pre-submission-checklist) ──
const SYSTEM_FILES = new Set(['.ds_store', 'thumbs.db', 'desktop.ini', '__macosx'])
const DEVICE_NAME = /^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?$/i
const IMAGE_OR_FONT = /\.(png|jpe?g|gif|webp|svg|woff2?|ttf|otf)$/i
const MAX_FILE_BYTES = 256 * 1024 // larger files are held for a reviewer
const MAX_FILES = 512 // more files are held for a reviewer

/**
 * Problems in a plugin's files that make the directory block a submission or hold it for a reviewer.
 * `entries`: `{ path, size, symlink }` with `path` relative to the plugin folder, `/`-separated.
 */
export function portabilityProblems(entries) {
  const problems = new Set()
  const seen = new Map()
  for (const { path, size, symlink } of entries) {
    for (const seg of path.split('/')) {
      if (SYSTEM_FILES.has(seg.toLowerCase()))
        problems.add(`${path} is a macOS or Windows system file — remove it`)
      else if (seg.includes(':') || /[. ]$/.test(seg) || DEVICE_NAME.test(seg))
        problems.add(`"${seg}" in ${path} is not a valid file name on Windows`)
    }
    const key = path.toLowerCase()
    if (seen.has(key) && seen.get(key) !== path)
      problems.add(`${[path, seen.get(key)].sort().join(' and ')} differ only by capitalization`)
    else seen.set(key, path)
    if (symlink) problems.add(`${path} is a symbolic link — commit a regular file`)
    else if (size > MAX_FILE_BYTES && !IMAGE_OR_FONT.test(path))
      problems.add(`${path} is over 256 KiB`)
  }
  if (entries.length > MAX_FILES)
    problems.add(`the plugin has ${entries.length} files; the limit is ${MAX_FILES}`)
  return [...problems]
}

/** The plugin's files as a clone holds them: tracked and new untracked, never git-ignored. */
function pluginEntries(dir) {
  let paths
  try {
    paths = execFileSync(
      'git',
      ['-C', ROOT, 'ls-files', '-co', '--exclude-standard', '-z', '--', relative(ROOT, dir)],
      { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] },
    )
      .split('\0')
      .filter(Boolean)
      .map((p) => join(ROOT, p))
  } catch {
    paths = walk(dir) // not a git checkout: every file on disk
  }
  const entries = []
  for (const abs of paths) {
    let st
    try {
      st = lstatSync(abs)
    } catch {
      continue // listed by git but deleted in the working tree
    }
    entries.push({
      path: relative(dir, abs).split(sep).join('/'),
      size: st.size,
      symlink: st.isSymbolicLink(),
    })
  }
  return entries
}

function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((d) =>
    d.isDirectory() ? walk(join(dir, d.name)) : [join(dir, d.name)],
  )
}

export function checkRepo() {
  const errors = []
  const err = (scope, msg) => errors.push(`[${scope}] ${msg}`)

  // ── Marketplace ────────────────────────────────────────────────────────────
  const mp = loadMarketplace()
  const categoryIds = new Set(loadCategories().map((c) => c.id))
  if (mp.name !== MARKETPLACE_NAME)
    err('marketplace', `name must stay "${MARKETPLACE_NAME}" (it is permanent)`)
  if (!mp.$schema) err('marketplace', 'missing $schema')
  if (!mp.description) err('marketplace', 'missing description')
  if (!SEMVER.test(mp.version ?? '')) err('marketplace', `version "${mp.version}" is not semver`)
  if (!Array.isArray(mp.plugins)) err('marketplace', 'plugins must be an array')

  const listed = new Set()
  for (const [i, entry] of (mp.plugins ?? []).entries()) {
    const scope = `marketplace.plugins[${i}] ${entry.name ?? '?'}`
    if (!KEBAB.test(entry.name ?? '')) err(scope, 'name must be kebab-case')
    if (RESERVED_NAME.test(entry.name ?? ''))
      err(scope, 'name passes as an Anthropic plugin (reserved prefix)')
    if (listed.has(entry.name)) err(scope, 'duplicate entry')
    listed.add(entry.name)
    if (entry.source !== `./plugins/${entry.name}`)
      err(scope, `source must be "./plugins/${entry.name}"`)
    if (!categoryIds.has(entry.category))
      err(scope, `category "${entry.category}" is not in categories.json`)
    if (!entry.description) err(scope, 'missing description')
    if ('version' in entry)
      err(scope, 'do not set version on the entry; plugin.json is the single source of truth')
    if (!existsSync(pluginDir(entry.name)))
      err(scope, `directory plugins/${entry.name} does not exist`)
  }
  if (mp.renames) {
    for (const [from, to] of Object.entries(mp.renames)) {
      if (listed.has(from)) err('marketplace.renames', `"${from}" is renamed but still listed`)
      if (to !== null && !listed.has(to))
        err('marketplace.renames', `"${from}" → "${to}" points to an unlisted plugin`)
    }
  }

  // ── Plugin directories ─────────────────────────────────────────────────────
  const pluginsRoot = join(ROOT, 'plugins')
  const dirs = existsSync(pluginsRoot)
    ? readdirSync(pluginsRoot).filter((d) => statSync(join(pluginsRoot, d)).isDirectory())
    : []
  for (const d of dirs)
    if (!listed.has(d)) err(`plugins/${d}`, 'directory is not listed in marketplace.json')

  for (const entry of mp.plugins ?? []) {
    const name = entry.name
    const dir = pluginDir(name)
    if (!existsSync(dir)) continue
    const scope = `plugins/${name}`
    const manifest = loadManifest(name)
    if (!manifest) {
      err(scope, 'missing .claude-plugin/plugin.json')
      continue
    }
    if (manifest.name !== name)
      err(scope, `plugin.json name "${manifest.name}" must equal the entry name "${name}"`)
    if (!SEMVER.test(manifest.version ?? ''))
      err(scope, `plugin.json version "${manifest.version}" is not semver`)
    for (const f of ['displayName', 'description', 'author', 'keywords'])
      if (!manifest[f]) err(scope, `plugin.json missing ${f}`)
    if (manifest.license !== 'MIT') err(scope, 'plugin.json license must be "MIT"')
    if (manifest.homepage !== `${REPO_URL}/tree/main/plugins/${name}#readme`)
      err(scope, 'plugin.json homepage must point to the plugin README on main')
    if (manifest.repository !== REPO_URL) err(scope, `plugin.json repository must be ${REPO_URL}`)

    for (const f of ['README.md', 'CHANGELOG.md', 'LICENSE'])
      if (!existsSync(join(dir, f))) err(scope, `missing ${f}`)

    if (existsSync(join(dir, 'README.md'))) {
      const readme = readText(join(dir, 'README.md'))
      const headings = [...readme.matchAll(/^## (.+)$/gm)].map((m) => m[1])
      for (const section of REQUIRED_PLUGIN_SECTIONS) {
        if (!headings.some((h) => h.includes(section)))
          err(scope, `README.md missing the "${section}" section`)
      }
      if (/\{\{\w+\}\}/.test(readme)) err(scope, 'README.md has unresolved {{placeholders}}')
      if (/<!--\s*(TODO|TEMPLATE)\b/.test(readme))
        err(scope, 'README.md has unresolved TODO/TEMPLATE comments')
    }

    if (existsSync(join(dir, 'CHANGELOG.md')) && manifest.version) {
      const changelog = readText(join(dir, 'CHANGELOG.md'))
      if (!/^## \[Unreleased\]/m.test(changelog))
        err(scope, 'CHANGELOG.md missing "## [Unreleased]"')
      const body = changelogSection(changelog, manifest.version)
      if (body === null)
        err(scope, `CHANGELOG.md has no "## [${manifest.version}]" entry for the current version`)
      else if (!body) err(scope, `CHANGELOG.md entry for ${manifest.version} is empty`)
      if (/\{\{\w+\}\}/.test(changelog)) err(scope, 'CHANGELOG.md has unresolved {{placeholders}}')
    }

    // ── Cross-surface declaration (.claude/rules/cross-surface-compatibility.md) ──
    const profileKey = surfaceProfileKey(manifest.metadata?.surfaces)
    const components = detectComponents(name)
    if (!profileKey) {
      err(
        scope,
        `plugin.json metadata.surfaces must be one of: ${Object.values(SURFACE_PROFILES)
          .map((p) => JSON.stringify(p.surfaces))
          .join(' or ')}`,
      )
    } else {
      if (components.bin && profileKey !== 'claude-code-only') {
        err(
          scope,
          'ships a top-level bin/, which makes the Claude app refuse the plugin — declare metadata.surfaces ["claude-code"] or move the code into a skill\'s scripts/',
        )
      }
      if (existsSync(join(dir, 'README.md'))) {
        const readme = readText(join(dir, 'README.md'))
        const profile = SURFACE_PROFILES[profileKey]
        if (!readme.includes(`works%20in-${profile.badge}-`))
          err(
            scope,
            `README.md is missing the "works in" badge for ${JSON.stringify(profile.surfaces)}`,
          )
        if (profileKey === 'claude-code-only' && !readme.includes('**Claude Code only**')) {
          err(
            scope,
            'README.md must state "**Claude Code only**" (and why) for a Claude Code-only plugin',
          )
        }
        const compat =
          readme.match(/^## [^\n]*Compatibility[^\n]*\n([\s\S]*?)(?=^## |(?![\s\S]))/m)?.[1] ?? ''
        const rows = compat
          .split('\n')
          .filter(
            (l) => l.startsWith('|') && !/^\|\s*:?-/.test(l) && !/^\|\s*Component\s*\|/.test(l),
          )
        for (const t of COMPONENT_TYPES) {
          const present = rows.some((r) => r.includes(t.row))
          if (components[t.id] && !present)
            err(
              scope,
              `README.md Compatibility table has no row for ${t.label}, which the plugin ships`,
            )
          if (!components[t.id] && present)
            err(
              scope,
              `README.md Compatibility table lists ${t.label}, which the plugin doesn't ship — remove the row`,
            )
        }
      }
    }
  }

  // ── Portability (Anthropic's plugin directory) ─────────────────────────────
  for (const name of listed) {
    if (!existsSync(pluginDir(name))) continue
    for (const problem of portabilityProblems(pluginEntries(pluginDir(name))))
      err(`plugins/${name}`, problem)
  }

  // ── Root README generated blocks ───────────────────────────────────────────
  try {
    const readme = readText(README_PATH)
    if (renderReadme(readme) !== readme)
      err('README.md', 'catalog is out of date — run node .github/scripts/catalog.mjs')
  } catch (e) {
    err('README.md', e.message)
  }

  // ── Root CHANGELOG ─────────────────────────────────────────────────────────
  const rootChangelog = join(ROOT, 'CHANGELOG.md')
  if (!existsSync(rootChangelog)) err('CHANGELOG.md', 'missing')
  else if (changelogSection(readText(rootChangelog), mp.version) === null) {
    err('CHANGELOG.md', `no "## [${mp.version}]" entry for the marketplace version`)
  }

  return { errors }
}

if (isMain(import.meta.url)) {
  const { errors } = checkRepo()
  for (const e of errors) console.error(`✖ ${e}`)
  if (errors.length) {
    console.error(`\n✖ Repository checks failed: ${errors.length} error(s)`)
    process.exit(1)
  }
  console.log('✔ Repository checks passed')
}
