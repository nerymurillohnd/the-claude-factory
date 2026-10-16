#!/usr/bin/env node
// Post-edit hook of the TypeScript LSP intelligence plugins: runs the plugin's own tsc on
// the program that contains each TypeScript or JavaScript file a tool call changed. Reads
// one PostToolUse or PostToolUseFailure event on stdin. The nearest tsconfig.json or
// jsconfig.json above the file is the policy, and a solution-style config is followed
// through its references to the program that lists the file; without any config, tsc
// checks a TypeScript file alone with its defaults and JavaScript is reported as not
// type-checked. Exit 0 with a systemMessage when everything passed, stderr and exit 2 with
// errors or when tsc could not run. Files of other languages are ignored in silence.
// Node 18 or later. This file is byte-identical in typescript6-lsp-intelligence and
// typescript7-lsp-intelligence.

import { spawnSync } from 'node:child_process'
import { existsSync, readdirSync, readFileSync, realpathSync, statSync } from 'node:fs'
import { homedir } from 'node:os'
import { basename, dirname, join, parse, relative, resolve, sep } from 'node:path'

/** @typedef {{ file: string, reason: string }} Uncovered */
/** @typedef {{ findings: string[], failures: string[], uncovered: Uncovered[] }} Outcome */
/** @typedef {{ code: number | null, output: string }} RunResult */

const { CLAUDE_PLUGIN_ROOT, CLAUDE_PROJECT_DIR } = process.env
const PLUGIN_ROOT = CLAUDE_PLUGIN_ROOT ?? resolve(dirname(process.argv[1] ?? ''), '..')
const PLUGIN = pluginName()
const TSC = join(PLUGIN_ROOT, 'node_modules', 'typescript', 'bin', 'tsc')
const TS_SUFFIXES = new Set(['.ts', '.tsx', '.mts', '.cts'])
const JS_SUFFIXES = new Set(['.js', '.jsx', '.mjs', '.cjs'])
const CONFIG_NAMES = ['tsconfig.json', 'jsconfig.json']
const SKIPPED_DIRS = new Set(['node_modules', '.venv', 'venv', 'site-packages'])
const PRUNED_DIRS = new Set([
  ...SKIPPED_DIRS,
  '.git',
  'dist',
  'build',
  '.cache',
  '.next',
  '.svelte-kit',
  '.astro',
  '.wrangler',
  '.output',
  'coverage',
])
// Claude Code saves hook output over 10,000 characters to a file Claude never reads.
const MAX_REPORT_CHARS = 9000
// Clock slack added to duration_ms when looking for files a Bash command changed.
const BASH_SLACK_MS = 2000
// Window used when the event carries no duration_ms.
const FALLBACK_WINDOW_MS = 30_000
// The modification-time walk gives up after this many files, so a huge tree stays cheap.
const MAX_WALK_FILES = 20_000
// Under the hook's 120 s budget, so a slow program is reported instead of cancelled in silence.
const TOOL_TIMEOUT_MS = 110_000
const MS_PER_S = 1000
const ERROR_LINE = /^(.*?)\((\d+),(\d+)\): error TS\d+: /
const BARE_ERROR = /^error TS\d+: /
const CONTINUATION = /^\s+\S/
const LISTED_FILE = /^(?:\/|[A-Za-z]:[\\/])/
const INSTALL_HINT = `the plugin's own TypeScript was not installed; run "npm ci" in ${PLUGIN_ROOT} or reinstall the plugin from the marketplace`

// The plugin's name from its manifest: the install folder is named after the version.
/** @returns {string} */
function pluginName() {
  try {
    const manifest = JSON.parse(
      readFileSync(join(PLUGIN_ROOT, '.claude-plugin', 'plugin.json'), 'utf8'),
    )
    if (typeof manifest.name === 'string' && manifest.name !== '') {
      return manifest.name
    }
  } catch {
    // fall through
  }
  return basename(PLUGIN_ROOT)
}

/**
 * @param {unknown} value
 * @param {...string} keys
 * @returns {string}
 */
function textAt(value, ...keys) {
  /** @type {unknown} */
  let current = value
  for (const key of keys) {
    if (current === null || typeof current !== 'object') {
      return ''
    }
    current = /** @type {Record<string, unknown>} */ (current)[key]
  }
  return typeof current === 'string' ? current : ''
}

/**
 * @param {unknown} value
 * @param {...string} keys
 * @returns {string[] | null}
 */
function stringsAt(value, ...keys) {
  /** @type {unknown} */
  let current = value
  for (const key of keys) {
    if (current === null || typeof current !== 'object') {
      return null
    }
    current = /** @type {Record<string, unknown>} */ (current)[key]
  }
  return Array.isArray(current)
    ? current.filter(/** @returns {item is string} */ (item) => typeof item === 'string')
    : null
}

/** @returns {Record<string, unknown> | null} */
function readEvent() {
  try {
    const data = JSON.parse(readFileSync(0, 'utf8'))
    return data !== null && typeof data === 'object' && !Array.isArray(data) ? data : null
  } catch {
    return null
  }
}

/**
 * @param {string} path
 * @returns {boolean}
 */
function isDir(path) {
  try {
    return statSync(path).isDirectory()
  } catch {
    return false
  }
}

// The canonical path (symlinks resolved, as process.cwd() reports it), so that files, the
// project and tsc's --listFiles output compare equal whatever spelling the event used.
/**
 * @param {string} path
 * @returns {string}
 */
function realpath(path) {
  try {
    return realpathSync(path)
  } catch {
    return resolve(path)
  }
}

/**
 * @param {Record<string, unknown>} event
 * @returns {string | null}
 */
function projectDir(event) {
  const candidates = [CLAUDE_PROJECT_DIR ?? '', textAt(event, 'cwd'), process.cwd()]
  for (const candidate of candidates) {
    if (candidate && isDir(candidate)) {
      return realpath(candidate)
    }
  }
  return null
}

/**
 * @param {[string, ...string[]]} argv
 * @returns {RunResult}
 */
function run(argv) {
  const result = spawnSync(argv[0], argv.slice(1), { encoding: 'utf8', timeout: TOOL_TIMEOUT_MS })
  if (result.error) {
    const detail =
      /** @type {NodeJS.ErrnoException} */ (result.error).code === 'ETIMEDOUT'
        ? `timed out after ${TOOL_TIMEOUT_MS / MS_PER_S} s`
        : `could not start: ${result.error.message}`
    return { code: null, output: `${argv[0]} ${detail}` }
  }
  return { code: result.status, output: `${result.stdout}${result.stderr}` }
}

/**
 * @param {string} path
 * @param {number} sinceMs
 * @returns {boolean}
 */
function newerThan(path, sinceMs) {
  try {
    const st = statSync(path)
    return st.isFile() && st.mtimeMs > sinceMs
  } catch {
    return false
  }
}

// Collects files newer than sinceMs under dir; unreadable folders are skipped and the walk
// stops once budget.left runs out.
/**
 * @param {string} dir
 * @param {number} sinceMs
 * @param {string[]} found
 * @param {{ left: number }} budget
 * @returns {void}
 */
function walk(dir, sinceMs, found, budget) {
  let entries
  try {
    entries = readdirSync(dir, { withFileTypes: true })
  } catch {
    return
  }
  for (const entry of entries) {
    if (budget.left <= 0) {
      return
    }
    const path = join(dir, entry.name)
    if (entry.isDirectory()) {
      if (!PRUNED_DIRS.has(entry.name)) {
        walk(path, sinceMs, found, budget)
      }
    } else {
      budget.left -= 1
      if (newerThan(path, sinceMs)) {
        found.push(path)
      }
    }
  }
}

/**
 * @param {string} project
 * @param {number} sinceMs
 * @returns {string[]}
 */
function changedSince(project, sinceMs) {
  const inside = run(['git', '-C', project, 'rev-parse', '--is-inside-work-tree'])
  if (inside.code === 0) {
    const args = ['-C', project, 'ls-files', '-z', '--modified', '--others', '--exclude-standard']
    return run(['git', ...args])
      .output.split('\0')
      .filter(Boolean)
      .map((rel) => join(project, rel))
      .filter((path) => newerThan(path, sinceMs))
  }
  if (project === realpath(homedir()) || project === parse(project).root) {
    return [] // a walk of the whole home directory or disk is never worth a hook's budget
  }
  /** @type {string[]} */
  const found = []
  walk(project, sinceMs, found, { left: MAX_WALK_FILES })
  return found
}

/**
 * @param {readonly string[]} names
 * @returns {string[]}
 */
function asFiles(names) {
  /** @type {Set<string>} */
  const seen = new Set()
  for (const name of names) {
    if (!name) {
      continue
    }
    const path = realpath(name)
    if (newerThan(path, -1)) {
      seen.add(path)
    }
  }
  return [...seen]
}

/**
 * @param {Record<string, unknown>} event
 * @param {number} nowMs
 * @returns {string[]}
 */
function candidates(event, nowMs) {
  const tool = textAt(event, 'tool_name')
  if (tool === 'Edit' || tool === 'Write') {
    return asFiles([textAt(event, 'tool_input', 'file_path')])
  }
  if (tool !== 'Bash') {
    return []
  }
  const changed = stringsAt(event, 'tool_response', 'bashEditDiff', 'changedFiles')
  if (changed !== null) {
    return asFiles(changed)
  }
  const project = projectDir(event)
  if (project === null) {
    return []
  }
  const { duration_ms: duration } = event
  const windowMs =
    typeof duration === 'number' && Number.isInteger(duration)
      ? duration + BASH_SLACK_MS
      : FALLBACK_WINDOW_MS
  return asFiles(changedSince(project, nowMs - windowMs))
}

/**
 * @param {string} path
 * @returns {string}
 */
function suffixOf(path) {
  const name = basename(path)
  const dot = name.lastIndexOf('.')
  return dot > 0 ? name.slice(dot) : ''
}

/**
 * @param {string} path
 * @returns {boolean}
 */
function isTypeScript(path) {
  return TS_SUFFIXES.has(suffixOf(path))
}

/**
 * @param {string} path
 * @returns {boolean}
 */
function isJavaScript(path) {
  return JS_SUFFIXES.has(suffixOf(path))
}

/**
 * @param {string} path
 * @returns {boolean}
 */
function skipped(path) {
  return path.split(sep).some((part) => SKIPPED_DIRS.has(part))
}

// The nearest tsconfig.json, else jsconfig.json, above the file; null without either.
/**
 * @param {string} path
 * @returns {string | null}
 */
function nearestConfig(path) {
  let dir = dirname(path)
  for (;;) {
    for (const name of CONFIG_NAMES) {
      const config = join(dir, name)
      if (existsSync(config)) {
        return config
      }
    }
    const parent = dirname(dir)
    if (parent === dir) {
      return null
    }
    dir = parent
  }
}

/**
 * @param {readonly string[]} files
 * @returns {Map<string, string[]>}
 */
function groupByProgram(files) {
  /** @type {Map<string, string[]>} */
  const groups = new Map()
  for (const path of files) {
    const key = nearestConfig(path) ?? ''
    const group = groups.get(key)
    if (group === undefined) {
      groups.set(key, [path])
    } else {
      group.push(path)
    }
  }
  return groups
}

/**
 * @param {string} path
 * @param {string | null} base
 * @returns {string}
 */
function display(path, base) {
  if (base === null) {
    return path
  }
  const rel = relative(base, path)
  return rel.startsWith('..') ? path : rel.split(sep).join('/')
}

// Groups tsc's output into errors with their indented explanation lines, then sorts them:
// edited files first, the rest of the program after, config errors last. tsc prints file
// paths relative to its own working directory, which is the hook's.
/**
 * @param {readonly string[]} lines
 * @param {ReadonlySet<string>} edited
 * @returns {string[]}
 */
function orderErrors(lines, edited) {
  /** @type {string[]} */
  const own = []
  /** @type {string[]} */
  const others = []
  /** @type {string[]} */
  const bare = []
  /** @type {string[] | null} */
  let current = null
  for (const line of lines) {
    const match = ERROR_LINE.exec(line)
    if (match) {
      current = edited.has(realpath(resolve(match[1] ?? ''))) ? own : others
      current.push(line)
    } else if (BARE_ERROR.test(line)) {
      current = bare
      current.push(line)
    } else if (current !== null && CONTINUATION.test(line)) {
      current.push(line)
    } else {
      current = null
    }
  }
  return [...own, ...others, ...bare]
}

// The configs a solution-style config refers to, resolved through tsc so comments and
// extends are handled; a directory reference means the tsconfig.json inside it.
/**
 * @param {string} config
 * @returns {string[]}
 */
function referencedConfigs(config) {
  const shown = run([process.execPath, TSC, '--showConfig', '-p', config])
  if (shown.code !== 0) {
    return []
  }
  let parsed
  try {
    parsed = JSON.parse(shown.output)
  } catch {
    return []
  }
  const references = Array.isArray(parsed.references) ? parsed.references : []
  const configs = []
  for (const reference of references) {
    if (typeof reference?.path !== 'string') {
      continue
    }
    const target = resolve(dirname(config), reference.path)
    const file = isDir(target) ? join(target, 'tsconfig.json') : target
    if (existsSync(file)) {
      configs.push(realpath(file))
    }
  }
  return configs
}

/**
 * @param {readonly string[]} files
 * @param {string | null} base
 * @returns {Outcome}
 */
function checkLooseFiles(files, base) {
  /** @type {Outcome} */
  const out = { findings: [], failures: [], uncovered: [] }
  const typescript = files.filter(isTypeScript)
  for (const file of files.filter(isJavaScript)) {
    out.uncovered.push({
      file,
      reason: 'no tsconfig.json or jsconfig.json above it; JavaScript not type-checked',
    })
  }
  if (typescript.length === 0) {
    return out
  }
  const names = typescript.map((file) => display(file, base)).join(', ')
  const result = run([process.execPath, TSC, '--noEmit', '--pretty', 'false', ...typescript])
  if (result.code === null) {
    out.failures.push(`tsc failed, so ${names} was not checked:\n${result.output.trim()}`)
  } else if (result.code !== 0) {
    const where = `no tsconfig.json above ${names}; compiler defaults`
    out.findings.push(`tsc (${where}):\n${result.output.trim()}`)
  }
  return out
}

/**
 * @param {string} config
 * @param {readonly string[]} files
 * @param {string | null} base
 * @param {Set<string>} [visited]
 * @returns {Outcome}
 */
function checkProgram(config, files, base, visited = new Set()) {
  if (config === '') {
    return checkLooseFiles(files, base)
  }
  /** @type {Outcome} */
  const out = { findings: [], failures: [], uncovered: [] }
  visited.add(config)
  const result = run([
    process.execPath,
    TSC,
    '--noEmit',
    '--listFiles',
    '--pretty',
    'false',
    '-p',
    config,
  ])
  if (result.code === null) {
    out.failures.push(
      `tsc failed, so ${display(config, base)} was not checked:\n${result.output.trim()}`,
    )
    return out
  }
  const lines = result.output.split('\n')
  const listed = new Set(
    lines.filter((line) => LISTED_FILE.test(line)).map((line) => realpath(line.trim())),
  )
  const errors = orderErrors(lines, new Set(files))
  if (errors.length > 0) {
    out.findings.push(`tsc (${display(config, base)}):\n${errors.join('\n')}`)
  } else if (result.code !== 0) {
    const label = `tsc exited ${result.code} without error lines, so ${display(config, base)} was not checked`
    out.failures.push(`${label}:\n${result.output.trim()}`)
  }
  let missing = files.filter((path) => !listed.has(path))
  if (missing.length > 0) {
    for (const referenced of referencedConfigs(config)) {
      if (missing.length === 0 || visited.has(referenced)) {
        continue
      }
      const nested = checkProgram(referenced, missing, base, visited)
      out.findings.push(...nested.findings)
      out.failures.push(...nested.failures)
      const stillMissing = new Set(nested.uncovered.map((entry) => entry.file))
      missing = missing.filter((path) => stillMissing.has(path))
    }
  }
  for (const file of missing) {
    out.uncovered.push({
      file,
      reason: `not part of ${display(config, base)}'s program; add it to include or files`,
    })
  }
  return out
}

/**
 * @param {string} text
 * @returns {string}
 */
function bounded(text) {
  if (text.length <= MAX_REPORT_CHARS) {
    return text
  }
  const lines = text.split('\n')
  const kept = []
  let size = 0
  for (const line of lines) {
    if (size + line.length + 1 > MAX_REPORT_CHARS) {
      break
    }
    kept.push(line)
    size += line.length + 1
  }
  return `${kept.join('\n')}\n… ${lines.length - kept.length} more lines\n`
}

/** @returns {number} */
function main() {
  const event = readEvent()
  if (event === null) {
    return 0
  }
  const files = candidates(event, Date.now()).filter(
    (path) => !skipped(path) && (isTypeScript(path) || isJavaScript(path)),
  )
  if (files.length === 0) {
    return 0
  }
  if (!existsSync(TSC)) {
    process.stderr.write(
      `${PLUGIN}: ${INSTALL_HINT}; ${files.length} TypeScript file(s) not checked.\n`,
    )
    return 2
  }
  const base = projectDir(event)
  const results = [...groupByProgram(files)].map(([config, group]) =>
    checkProgram(config, group, base),
  )
  const parts = results.flatMap((result) => [...result.findings, ...result.failures])
  if (parts.length > 0) {
    const names = files.map((file) => display(file, base)).join(', ')
    parts.push(`Fix these findings in ${names} before continuing; do not suppress them.`)
    process.stderr.write(bounded(`${parts.join('\n')}\n`))
    return 2
  }
  const uncovered = results.flatMap((result) => result.uncovered)
  const unchecked = new Set(uncovered.map((entry) => entry.file))
  const checked = files.filter((file) => !unchecked.has(file)).map((file) => display(file, base))
  const summary = []
  if (checked.length > 0) {
    summary.push(`tsc passed · ${checked.join(', ')}`)
  }
  if (uncovered.length > 0) {
    summary.push(`not checked · ${uncovered.map((entry) => display(entry.file, base)).join(', ')}`)
  }
  /** @type {{ systemMessage: string, hookSpecificOutput?: { hookEventName: string, additionalContext: string } }} */
  const payload = { systemMessage: `${PLUGIN}: ${summary.join('; ')}` }
  if (uncovered.length > 0) {
    payload.hookSpecificOutput = {
      hookEventName: textAt(event, 'hook_event_name') || 'PostToolUse',
      additionalContext: uncovered
        .map((entry) => `${display(entry.file, base)}: ${entry.reason}.`)
        .join(' '),
    }
  }
  process.stdout.write(JSON.stringify(payload))
  return 0
}

process.exitCode = main()
