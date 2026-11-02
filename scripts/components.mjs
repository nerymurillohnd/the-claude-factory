#!/usr/bin/env node
// @ts-check
// Detects which component types a plugin ships, from its standard layout and manifest.

import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { loadManifest, pluginDir } from './lib.mjs'

/** @typedef {'skills' | 'commands' | 'agents' | 'hooks' | 'mods' | 'mcp' | 'lsp' | 'outputStyles' | 'monitors' | 'workflows' | 'themes' | 'bin'} ComponentId */
/** @typedef {{ id: ComponentId, emoji: string, label: string, row: string }} ComponentType */
/** @typedef {Partial<Record<ComponentId, number>>} Components */

/**
 * `row` is the text the README Compatibility table must contain for that component.
 * @type {ComponentType[]}
 */
export const COMPONENT_TYPES = [
  { id: 'skills', emoji: '🎯', label: 'Skills', row: 'Skills' },
  { id: 'commands', emoji: '⌨️', label: 'Commands', row: 'Commands' },
  { id: 'agents', emoji: '🤖', label: 'Agents', row: 'Agents' },
  { id: 'hooks', emoji: '🪝', label: 'Hooks', row: 'Hooks' },
  { id: 'mods', emoji: '🧩', label: 'Mods', row: 'Mods' },
  { id: 'mcp', emoji: '🔌', label: 'MCP', row: 'MCP server' },
  { id: 'lsp', emoji: '🧠', label: 'LSP', row: 'LSP' },
  { id: 'outputStyles', emoji: '🎨', label: 'Output styles', row: 'Output styles' },
  { id: 'monitors', emoji: '📡', label: 'Monitors', row: 'Monitors' },
  { id: 'workflows', emoji: '🔁', label: 'Workflows', row: 'Workflows' },
  { id: 'themes', emoji: '🌈', label: 'Themes', row: 'Themes' },
  { id: 'bin', emoji: '⚙️', label: 'Executables', row: 'Executables' },
]

/**
 * Component types counted from the files of one folder: [id, folder, which file names count].
 * @type {[ComponentId, string, (file: string) => boolean][]}
 */
const FOLDER_COMPONENTS = [
  ['commands', 'commands', (f) => f.endsWith('.md')],
  ['agents', 'agents', (f) => f.endsWith('.md')],
  ['outputStyles', 'output-styles', (f) => f.endsWith('.md')],
  ['workflows', 'workflows', (f) => f.endsWith('.js')],
  ['themes', 'themes', (f) => f.endsWith('.json')],
  ['bin', 'bin', () => true],
]

/**
 * @param {string} dir
 * @param {(entry: string, full: string) => boolean} predicate
 * @returns {number}
 */
function countFiles(dir, predicate) {
  if (!existsSync(dir)) {
    return 0
  }
  let n = 0
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry)
    if (statSync(full).isDirectory()) {
      n += countFiles(full, predicate)
    } else if (predicate(entry, full)) {
      n += 1
    }
  }
  return n
}

/**
 * Which component types a hooks/hooks.json declares: settings hooks under `hooks`, a mod's hooks
 * module under `modules`. A file that is not a JSON object counts as settings hooks, as any
 * hooks.json did before mods existed; check-repo reports it as invalid.
 * @param {string} text
 * @returns {{ hooks: boolean, mods: boolean }}
 */
export function hooksFileKinds(text) {
  /** @type {unknown} */
  let parsed
  try {
    parsed = JSON.parse(text)
  } catch {
    return { hooks: true, mods: false }
  }
  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
    return { hooks: true, mods: false }
  }
  return { hooks: 'hooks' in parsed, mods: 'modules' in parsed }
}

/** The frontmatter block at the start of a Markdown file, without its `---` lines. */
const FRONTMATTER = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/
/** A top-level `hooks` key in a frontmatter block. */
const HOOKS_KEY = /^hooks:/m

/**
 * Whether a skill's or an agent's Markdown declares hooks: a top-level `hooks` key in the
 * frontmatter between its opening and closing `---` lines. Such hooks ship with the plugin even
 * without a hooks/hooks.json.
 * @param {string} text
 * @returns {boolean}
 */
export function frontmatterHasHooks(text) {
  const match = FRONTMATTER.exec(text)
  return match !== null && HOOKS_KEY.test(match[1] ?? '')
}

/**
 * Whether any SKILL.md under skills/ or any agent file under agents/ of a plugin declares hooks.
 * @param {string} dir
 * @returns {boolean}
 */
function markdownHooks(dir) {
  /** @type {string[]} */
  const files = []
  /** @param {string} folder @param {(f: string) => boolean} keep */
  const walk = (folder, keep) => {
    if (!existsSync(folder)) {
      return
    }
    for (const entry of readdirSync(folder, { withFileTypes: true })) {
      const path = join(folder, entry.name)
      if (entry.isDirectory()) {
        walk(path, keep)
      } else if (keep(entry.name)) {
        files.push(path)
      }
    }
  }
  walk(join(dir, 'skills'), (f) => f === 'SKILL.md')
  walk(join(dir, 'agents'), (f) => f.endsWith('.md'))
  return files.some((f) => frontmatterHasHooks(readFileSync(f, 'utf8')))
}

/**
 * Returns { skills: 2, agents: 1, ... } with only the component types present.
 * @param {string} name
 * @returns {Components}
 */
export function detectComponents(name) {
  const dir = pluginDir(name)
  /** @type {import('./lib.mjs').Manifest} */
  const manifest = loadManifest(name) ?? {}
  /** @type {Components} */
  const found = {}
  /**
   * @param {ComponentId} id
   * @param {number} n
   */
  const set = (id, n) => {
    if (n > 0) {
      found[id] = n
    }
  }

  set(
    'skills',
    countFiles(join(dir, 'skills'), (f) => f === 'SKILL.md') +
      (existsSync(join(dir, 'SKILL.md')) ? 1 : 0),
  )
  const hooksPath = join(dir, 'hooks', 'hooks.json')
  const kinds = existsSync(hooksPath)
    ? hooksFileKinds(readFileSync(hooksPath, 'utf8'))
    : { hooks: false, mods: false }
  set('hooks', kinds.hooks || manifest.hooks || markdownHooks(dir) ? 1 : 0)
  set('mods', kinds.mods ? 1 : 0)
  set('mcp', existsSync(join(dir, '.mcp.json')) || manifest.mcpServers ? 1 : 0)
  set('lsp', existsSync(join(dir, '.lsp.json')) || manifest.lspServers ? 1 : 0)
  set(
    'monitors',
    existsSync(join(dir, 'monitors', 'monitors.json')) || manifest.experimental?.monitors ? 1 : 0,
  )
  for (const [id, folder, counts] of FOLDER_COMPONENTS) {
    set(id, countFiles(join(dir, folder), counts))
  }
  return found
}

/**
 * @param {Components} found
 * @returns {string}
 */
export function componentBadges(found) {
  return COMPONENT_TYPES.filter((t) => found[t.id])
    .map((t) => `${t.emoji} ${t.label}`)
    .join(' · ')
}
