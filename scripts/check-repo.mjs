#!/usr/bin/env node
// Repository policy checks that `claude plugin validate` and scripts/validators/ do not cover.
// Exit 0 = pass, exit 1 = at least one error.

import { execFileSync } from 'node:child_process'
import { existsSync, lstatSync, readdirSync } from 'node:fs'
import { join, relative, sep } from 'node:path'
import { COMPONENT_TYPES, detectComponents } from './components.mjs'
import {
  changelogSection,
  isMain,
  loadManifest,
  loadMarketplace,
  MARKETPLACE_NAME,
  pluginDir,
  REPO_URL,
  REQUIRED_PLUGIN_SECTIONS,
  ROOT,
  readJson,
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

// ── Author placeholders of the building-plugins README template ──
const README_TEMPLATE = join(ROOT, '.claude/skills/building-plugins/assets/README-template.md')
const AUTHOR_PLACEHOLDER = /<[A-Z][^<>\n]*>/g // innermost marks, so nested ones count one by one
/** @type {Set<string> | undefined} */
let templateMarks

/**
 * The author placeholders the README template holds, such as `<Skill name>` and `<Display Name>`.
 * Throws when the template is missing or holds none, so the code check never passes by default,
 * and when one is a single word, which code such as `Array<Type>` could hold.
 * @returns {Set<string>}
 */
function templatePlaceholders() {
  if (templateMarks === undefined) {
    if (!existsSync(README_TEMPLATE)) {
      throw new Error(
        `${relative(ROOT, README_TEMPLATE)} is missing: the README placeholder check needs it`,
      )
    }
    templateMarks = new Set(readText(README_TEMPLATE).match(AUTHOR_PLACEHOLDER) ?? [])
    if (templateMarks.size === 0) {
      throw new Error(`${relative(ROOT, README_TEMPLATE)} holds no <…> placeholders`)
    }
    const single = [...templateMarks].filter((mark) => !mark.includes(' '))
    if (single.length > 0) {
      throw new Error(
        `${relative(ROOT, README_TEMPLATE)} has one-word placeholders, which code can hold: ${single.join(' ')}`,
      )
    }
  }
  return templateMarks
}

/** @typedef {{ path: string, size: number, symlink: boolean }} FileEntry */

/**
 * Problems in a plugin's files that make the directory block a submission or hold it for a reviewer.
 * `entries`: `{ path, size, symlink }` with `path` relative to the plugin folder, `/`-separated.
 * @param {readonly FileEntry[]} entries
 * @returns {string[]}
 */
export function portabilityProblems(entries) {
  /** @type {Set<string>} */
  const problems = new Set()
  /** @type {Map<string, string>} */
  const seen = new Map()
  for (const { path, size, symlink } of entries) {
    for (const seg of path.split('/')) {
      if (SYSTEM_FILES.has(seg.toLowerCase())) {
        problems.add(`${path} is a macOS or Windows system file — remove it`)
      }
      if (seg.includes(':') || /[. ]$/.test(seg) || DEVICE_NAME.test(seg)) {
        problems.add(`"${seg}" in ${path} is not a valid file name on Windows`)
      }
    }
    const key = path.toLowerCase()
    if (seen.has(key) && seen.get(key) !== path) {
      problems.add(`${[path, seen.get(key)].sort().join(' and ')} differ only by capitalization`)
    } else {
      seen.set(key, path)
    }
    if (symlink) {
      problems.add(`${path} is a symbolic link — commit a regular file`)
    } else if (size > MAX_FILE_BYTES && !IMAGE_OR_FONT.test(path)) {
      problems.add(`${path} is over 256 KiB`)
    }
  }
  if (entries.length > MAX_FILES) {
    problems.add(`the plugin has ${entries.length} files; the limit is ${MAX_FILES}`)
  }
  return [...problems]
}

// ── LSP server configs (code.claude.com/docs/en/plugins/manifest-reference#lspservers) ──
// `claude plugin validate` does not read .lsp.json, and an unknown key makes Claude Code
// skip the whole file at load, so nothing else catches a bad key before users do.
/** @type {Record<string, (v: unknown) => boolean>} */
const LSP_FIELDS = {
  command: (v) => typeof v === 'string' && v !== '' && (!v.includes(' ') || v.startsWith('/')),
  extensionToLanguage: (v) =>
    isRecord(v) &&
    Object.keys(v).length > 0 &&
    Object.entries(v).every(([ext, lang]) => ext.startsWith('.') && typeof lang === 'string'),
  args: (v) => Array.isArray(v) && v.every((a) => typeof a === 'string'),
  transport: (v) => v === 'stdio' || v === 'socket',
  env: (v) => isRecord(v) && Object.values(v).every((e) => typeof e === 'string'),
  initializationOptions: () => true,
  settings: () => true,
  workspaceFolder: (v) => typeof v === 'string',
  startupTimeout: (v) => Number.isInteger(v) && Number(v) > 0,
  shutdownTimeout: (v) => Number.isInteger(v) && Number(v) > 0,
  requestTimeout: (v) => Number.isInteger(v) && Number(v) > 0,
  restartOnCrash: (v) => typeof v === 'boolean',
  maxRestarts: (v) => Number.isInteger(v) && Number(v) >= 0,
  diagnostics: (v) => typeof v === 'boolean',
}
const LSP_REQUIRED = ['command', 'extensionToLanguage']

/**
 * @param {unknown} v
 * @returns {v is Record<string, unknown>}
 */
function isRecord(v) {
  return typeof v === 'object' && v !== null && !Array.isArray(v)
}

/**
 * Problems in a parsed .lsp.json: a map of server name to a strict server config.
 * @param {unknown} config
 * @returns {string[]}
 */
export function lspConfigProblems(config) {
  if (!isRecord(config) || Object.keys(config).length === 0) {
    return ['.lsp.json must map at least one server name to its config']
  }
  /** @type {string[]} */
  const problems = []
  for (const [server, cfg] of Object.entries(config)) {
    if (!isRecord(cfg)) {
      problems.push(`.lsp.json server "${server}" must be an object`)
      continue
    }
    for (const key of LSP_REQUIRED) {
      if (!(key in cfg)) {
        problems.push(`.lsp.json server "${server}" is missing ${key}`)
      }
    }
    for (const [key, value] of Object.entries(cfg)) {
      const valid = LSP_FIELDS[key]
      if (!valid) {
        problems.push(
          `.lsp.json server "${server}" has unknown key "${key}" — Claude Code skips the file`,
        )
      } else if (!valid(value)) {
        problems.push(`.lsp.json server "${server}" has an invalid ${key}`)
      }
    }
  }
  return problems
}

// ── Root package.json: maintainer tooling only, never a plugin runtime (ADR_2026-10-21_maintainer-only-root-package-json) ──
const RUNTIME_FIELDS = [
  'dependencies',
  'optionalDependencies',
  'peerDependencies',
  'bundleDependencies',
  'bundledDependencies',
  'main',
  'exports',
  'bin',
  'type',
  'workspaces',
]
// Scripts npm runs without being named: install and publish lifecycles, and pre<name>/post<name>
// around every `npm run <name>`. `npm ci --ignore-scripts` stops only the install ones.
const AUTO_SCRIPTS = new Set([
  'install',
  'prepare',
  'prepack',
  'prepublish',
  'prepublishOnly',
  'publish',
  'version',
  'dependencies',
])

/**
 * Problems in the root package.json. It may only pin exact @types/* packages for the
 * maintainers' type checks, with @types/node on the Node major of .nvmrc: a runtime field
 * would let a plugin resolve packages that no user receives, and "type" would change how
 * Node and tsc read the plugins' .js and .ts files.
 * @param {{ private?: unknown, devDependencies?: unknown, scripts?: unknown } & Record<string, unknown>} pkg
 * @param {string} nodeVersion the content of .nvmrc
 * @returns {string[]}
 */
export function rootPackageProblems(pkg, nodeVersion) {
  /** @type {string[]} */
  const problems = []
  if (pkg.private !== true) {
    problems.push('must set "private": true')
  }
  for (const field of RUNTIME_FIELDS) {
    if (field in pkg) {
      problems.push(`must not declare "${field}": it is maintainer tooling, never a plugin runtime`)
    }
  }
  const scripts = isRecord(pkg.scripts) ? pkg.scripts : {}
  for (const name of Object.keys(scripts)) {
    if (AUTO_SCRIPTS.has(name) || /^(pre|post)/.test(name)) {
      problems.push(
        `script "${name}" runs on its own: name every script so it runs only when called`,
      )
    }
  }
  const dev = isRecord(pkg.devDependencies) ? pkg.devDependencies : {}
  for (const [name, version] of Object.entries(dev)) {
    if (!name.startsWith('@types/')) {
      problems.push(
        `devDependency "${name}" is not a type package: tools run as installed, by bare name`,
      )
    } else if (typeof version !== 'string' || !SEMVER.test(version)) {
      problems.push(`devDependency "${name}" must be pinned to an exact version`)
    }
  }
  const types = dev['@types/node']
  const nodeMajor = nodeVersion.trim().replace(/^v/, '').split('.')[0]
  if (types === undefined) {
    problems.push('must declare "@types/node" in devDependencies for the scripts\' type check')
  } else if (typeof types === 'string' && types.split('.')[0] !== nodeMajor) {
    problems.push(`@types/node ${types} does not match the Node major ${nodeMajor} of .nvmrc`)
  }
  return problems
}

/**
 * The plugin's files as a clone holds them: tracked and new untracked, never git-ignored.
 * @param {string} dir
 * @returns {FileEntry[]}
 */
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
  /** @type {FileEntry[]} */
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

/**
 * @param {string} dir
 * @returns {string[]}
 */
function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((d) =>
    d.isDirectory() ? walk(join(dir, d.name)) : [join(dir, d.name)],
  )
}

/** @returns {{ errors: string[] }} */
export function checkRepo() {
  /** @type {string[]} */
  const errors = []
  /**
   * @param {string} scope
   * @param {string} msg
   */
  const err = (scope, msg) => errors.push(`[${scope}] ${msg}`)

  // ── Marketplace ────────────────────────────────────────────────────────────
  const mp = loadMarketplace()
  if (mp.name !== MARKETPLACE_NAME) {
    err('marketplace', `name must stay "${MARKETPLACE_NAME}" (it is permanent)`)
  }
  if (!mp.description) {
    err('marketplace', 'missing description')
  }
  if ('version' in mp) {
    err(
      'marketplace',
      'the marketplace carries no version: remove "version"; plugins are versioned',
    )
  }
  if (!Array.isArray(mp.plugins)) {
    err('marketplace', 'plugins must be an array')
  }

  /** @type {Set<string>} */
  const listed = new Set()
  for (const entry of mp.plugins ?? []) {
    listed.add(entry.name)
  }

  // ── Plugin directories ─────────────────────────────────────────────────────
  for (const entry of mp.plugins ?? []) {
    const name = entry.name
    const dir = pluginDir(name)
    if (!existsSync(dir)) {
      continue
    }
    const scope = `plugins/${name}`
    const manifest = loadManifest(name)
    if (!manifest) {
      continue
    }
    for (const f of /** @type {const} */ (['displayName', 'description', 'author', 'keywords'])) {
      if (!manifest[f]) {
        err(scope, `plugin.json missing ${f}`)
      }
    }
    if (manifest.license !== 'MIT') {
      err(scope, 'plugin.json license must be "MIT"')
    }
    if (manifest.repository !== REPO_URL) {
      err(scope, `plugin.json repository must be ${REPO_URL}`)
    }

    if (existsSync(join(dir, '.lsp.json'))) {
      try {
        for (const problem of lspConfigProblems(readJson(join(dir, '.lsp.json')))) {
          err(scope, problem)
        }
      } catch (e) {
        err(scope, `.lsp.json is not valid JSON: ${e instanceof Error ? e.message : String(e)}`)
      }
    }

    if (existsSync(join(dir, 'hooks', 'hooks.json'))) {
      try {
        readJson(join(dir, 'hooks', 'hooks.json'))
      } catch (e) {
        err(
          scope,
          `hooks/hooks.json is not valid JSON: ${e instanceof Error ? e.message : String(e)}`,
        )
      }
    }

    const readmePath = join(dir, 'README.md')
    const readme = existsSync(readmePath) ? readText(readmePath) : null
    if (readme !== null) {
      const headings = [...readme.matchAll(/^## (.+)$/gm)].map((m) => m[1] ?? '')
      for (const section of REQUIRED_PLUGIN_SECTIONS) {
        if (!headings.some((h) => h.includes(section))) {
          err(scope, `README.md missing the "${section}" section`)
        }
      }
      if (/\{\{\w+\}\}/.test(readme)) {
        err(scope, 'README.md has unresolved {{placeholders}}')
      }
      if (/<!--\s*(TODO|TEMPLATE)\b/.test(readme)) {
        err(scope, 'README.md has unresolved TODO/TEMPLATE comments')
      }
      // The building-plugins README template marks what the author fills with a `<` and a capital
      // letter. Outside code any such mark is reported; inside code only the template's own marks
      // are, since code keeps other `<…>` text on purpose (`<YYYY-MM-DD>`, `Promise<Result>`).
      const code = [...readme.matchAll(/^```[\s\S]*?^```|`[^`\n]*`/gm)].map((m) => m[0]).join('\n')
      const prose = readme.replace(/^```[\s\S]*?^```/gm, '').replace(/`[^`\n]*`/g, '')
      const leftInCode = [...new Set(code.match(AUTHOR_PLACEHOLDER) ?? [])].filter((p) =>
        templatePlaceholders().has(p),
      )
      if (/<[A-Z][^>]*>/.test(prose) || leftInCode.length > 0) {
        const where = leftInCode.length > 0 ? ` (in code: ${leftInCode.join(', ')})` : ''
        err(scope, `README.md has unresolved <…> placeholders${where}`)
      }
    }

    if (existsSync(join(dir, 'CHANGELOG.md')) && manifest.version) {
      const changelog = readText(join(dir, 'CHANGELOG.md'))
      if (changelogSection(changelog, manifest.version) === '') {
        err(scope, `CHANGELOG.md entry for ${manifest.version} is empty`)
      }
      if (/\{\{\w+\}\}/.test(changelog)) {
        err(scope, 'CHANGELOG.md has unresolved {{placeholders}}')
      }
    }

    // ── Cross-surface declaration (docs/compatibility.md) ──
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
      if (readme !== null) {
        const profile = SURFACE_PROFILES[profileKey]
        if (!readme.includes(`works%20in-${profile.badge}-`)) {
          err(
            scope,
            `README.md is missing the "works in" badge for ${JSON.stringify(profile.surfaces)}`,
          )
        }
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
          if (components[t.id] && !present) {
            err(
              scope,
              `README.md Compatibility table has no row for ${t.label}, which the plugin ships`,
            )
          }
          if (!components[t.id] && present) {
            err(
              scope,
              `README.md Compatibility table lists ${t.label}, which the plugin doesn't ship — remove the row`,
            )
          }
        }
      }
    }
  }

  // ── Portability (Anthropic's plugin directory) ─────────────────────────────
  for (const name of listed) {
    if (!existsSync(pluginDir(name))) {
      continue
    }
    for (const problem of portabilityProblems(pluginEntries(pluginDir(name)))) {
      err(`plugins/${name}`, problem)
    }
  }

  // ── Root package.json ──────────────────────────────────────────────────────
  try {
    const pkg = readJson(join(ROOT, 'package.json'))
    const nodeVersion = readText(join(ROOT, '.nvmrc'))
    for (const problem of rootPackageProblems(isRecord(pkg) ? pkg : {}, nodeVersion)) {
      err('package.json', problem)
    }
  } catch (e) {
    err('package.json', e instanceof Error ? e.message : String(e))
  }

  return { errors }
}

if (isMain(import.meta.url)) {
  const { errors } = checkRepo()
  for (const e of errors) {
    console.error(`✖ ${e}`)
  }
  if (errors.length) {
    console.error(`\n✖ Repository checks failed: ${errors.length} error(s)`)
    process.exit(1)
  }
  console.log('✔ Repository checks passed')
}
