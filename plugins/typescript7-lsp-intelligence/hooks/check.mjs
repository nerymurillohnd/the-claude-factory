#!/usr/bin/env node
// Post-edit hook of the TypeScript LSP intelligence plugins: runs the plugin's own tsc on
// the program that contains each TypeScript or JavaScript file a tool call changed. Reads
// one PostToolUse or PostToolUseFailure event on stdin. The nearest tsconfig.json above the
// file is the policy; without one, tsc checks the file alone with its defaults. Exit 0 with
// a systemMessage when everything passed, stderr and exit 2 with errors or when tsc could
// not run. Files of other languages are ignored in silence. Node 18 or later. This file is
// byte-identical in typescript6-lsp-intelligence and typescript7-lsp-intelligence.

import { spawnSync } from 'node:child_process'
import { existsSync, readdirSync, readFileSync, realpathSync, statSync } from 'node:fs'
import { basename, dirname, join, relative, resolve, sep } from 'node:path'

const PLUGIN_ROOT = process.env.CLAUDE_PLUGIN_ROOT ?? resolve(dirname(process.argv[1]), '..')
const PLUGIN = basename(PLUGIN_ROOT)
const TSC = join(PLUGIN_ROOT, 'node_modules', 'typescript', 'bin', 'tsc')
const TS_SUFFIXES = new Set(['.ts', '.tsx', '.mts', '.cts', '.js', '.jsx', '.mjs', '.cjs'])
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
// Under the hook's 120 s budget, so a slow program is reported instead of cancelled in silence.
const TOOL_TIMEOUT_MS = 110_000
const MS_PER_S = 1000
const ERROR_LINE = /^(.*?)\((\d+),(\d+)\): error TS\d+: /
const BARE_ERROR = /^error TS\d+: /
const LISTED_FILE = /^(?:\/|[A-Za-z]:[\\/])/
const INSTALL_HINT = `the plugin's own TypeScript was not installed; run "npm ci" in ${PLUGIN_ROOT} or reinstall the plugin from the marketplace`

function textAt(value, ...keys) {
  let current = value
  for (const key of keys) {
    if (current === null || typeof current !== 'object') {
      return ''
    }
    current = current[key]
  }
  return typeof current === 'string' ? current : ''
}

function stringsAt(value, ...keys) {
  let current = value
  for (const key of keys) {
    if (current === null || typeof current !== 'object') {
      return null
    }
    current = current[key]
  }
  return Array.isArray(current) ? current.filter((item) => typeof item === 'string') : null
}

function readEvent() {
  try {
    const data = JSON.parse(readFileSync(0, 'utf8'))
    return data !== null && typeof data === 'object' && !Array.isArray(data) ? data : null
  } catch {
    return null
  }
}

function isDir(path) {
  try {
    return statSync(path).isDirectory()
  } catch {
    return false
  }
}

// The canonical path (symlinks resolved, as process.cwd() reports it), so that files, the
// project and tsc's --listFiles output compare equal whatever spelling the event used.
function realpath(path) {
  try {
    return realpathSync(path)
  } catch {
    return resolve(path)
  }
}

function projectDir(event) {
  const candidates = [process.env.CLAUDE_PROJECT_DIR ?? '', textAt(event, 'cwd'), process.cwd()]
  for (const candidate of candidates) {
    if (candidate && isDir(candidate)) {
      return realpath(candidate)
    }
  }
  return null
}

function run(argv) {
  const result = spawnSync(argv[0], argv.slice(1), { encoding: 'utf8', timeout: TOOL_TIMEOUT_MS })
  if (result.error) {
    const detail =
      result.error.code === 'ETIMEDOUT'
        ? `timed out after ${TOOL_TIMEOUT_MS / MS_PER_S} s`
        : `could not start: ${result.error.message}`
    return { code: null, output: `${argv[0]} ${detail}` }
  }
  return { code: result.status, output: `${result.stdout}${result.stderr}` }
}

function newerThan(path, sinceMs) {
  try {
    const st = statSync(path)
    return st.isFile() && st.mtimeMs > sinceMs
  } catch {
    return false
  }
}

function walk(dir, sinceMs, found) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name)
    if (entry.isDirectory()) {
      if (!PRUNED_DIRS.has(entry.name)) {
        walk(path, sinceMs, found)
      }
    } else if (newerThan(path, sinceMs)) {
      found.push(path)
    }
  }
}

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
  const found = []
  walk(project, sinceMs, found)
  return found
}

function asFiles(names) {
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
  const duration = event.duration_ms
  const windowMs = Number.isInteger(duration) ? duration + BASH_SLACK_MS : FALLBACK_WINDOW_MS
  return asFiles(changedSince(project, nowMs - windowMs))
}

function isTypeScript(path) {
  const name = basename(path)
  const dot = name.lastIndexOf('.')
  return dot > 0 && TS_SUFFIXES.has(name.slice(dot))
}

function skipped(path) {
  return path.split(sep).some((part) => SKIPPED_DIRS.has(part))
}

function nearestTsconfig(path) {
  let dir = dirname(path)
  for (;;) {
    const config = join(dir, 'tsconfig.json')
    if (existsSync(config)) {
      return config
    }
    const parent = dirname(dir)
    if (parent === dir) {
      return null
    }
    dir = parent
  }
}

function groupByProgram(files) {
  const groups = new Map()
  for (const path of files) {
    const key = nearestTsconfig(path) ?? ''
    if (!groups.has(key)) {
      groups.set(key, [])
    }
    groups.get(key).push(path)
  }
  return groups
}

function display(path, base) {
  if (base === null) {
    return path
  }
  const rel = relative(base, path)
  return rel.startsWith('..') ? path : rel.split(sep).join('/')
}

// Sort tsc's error lines: edited files first, then the rest of the program, config errors last.
function orderErrors(lines, edited, configDir) {
  const own = []
  const others = []
  const bare = []
  for (const line of lines) {
    const match = ERROR_LINE.exec(line)
    if (match) {
      const file = realpath(resolve(configDir, match[1]))
      if (edited.has(file)) {
        own.push(line)
      } else {
        others.push(line)
      }
    } else if (BARE_ERROR.test(line)) {
      bare.push(line)
    }
  }
  return [...own, ...others, ...bare]
}

function checkLooseFiles(files, base) {
  const out = { findings: [], failures: [], uncovered: [] }
  const names = files.map((file) => display(file, base)).join(', ')
  const result = run([process.execPath, TSC, '--noEmit', '--pretty', 'false', ...files])
  if (result.code === null) {
    out.failures.push(`tsc failed, so ${names} was not checked:\n${result.output.trim()}`)
  } else if (result.code !== 0) {
    const where = `no tsconfig.json above ${names}; compiler defaults`
    out.findings.push(`tsc (${where}):\n${result.output.trim()}`)
  }
  return out
}

function checkProgram(config, files, base) {
  if (config === '') {
    return checkLooseFiles(files, base)
  }
  const out = { findings: [], failures: [], uncovered: [] }
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
  const errors = orderErrors(lines, new Set(files), dirname(config))
  if (errors.length > 0) {
    out.findings.push(`tsc (${display(config, base)}):\n${errors.join('\n')}`)
  } else if (result.code !== 0) {
    const label = `tsc exited ${result.code} without error lines, so ${display(config, base)} was not checked`
    out.failures.push(`${label}:\n${result.output.trim()}`)
  }
  out.uncovered = files.filter((path) => !listed.has(path))
  return out
}

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

function main() {
  const event = readEvent()
  if (event === null) {
    return 0
  }
  const files = candidates(event, Date.now()).filter((path) => !skipped(path) && isTypeScript(path))
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
  const results = [...groupByProgram(files)].map(([config, group]) => ({
    config,
    ...checkProgram(config, group, base),
  }))
  const names = files.map((file) => display(file, base)).join(', ')
  const parts = results.flatMap((result) => [...result.findings, ...result.failures])
  if (parts.length > 0) {
    parts.push(`Fix these findings in ${names} before continuing; do not suppress them.`)
    process.stderr.write(bounded(`${parts.join('\n')}\n`))
    return 2
  }
  const payload = { systemMessage: `${PLUGIN}: tsc passed · ${names}` }
  const uncovered = results.flatMap((result) =>
    result.uncovered.map(
      (file) =>
        `${display(file, base)} is not part of ${display(result.config, base)}'s program; add it to include or files.`,
    ),
  )
  if (uncovered.length > 0) {
    payload.hookSpecificOutput = {
      hookEventName: textAt(event, 'hook_event_name') || 'PostToolUse',
      additionalContext: uncovered.join(' '),
    }
  }
  process.stdout.write(JSON.stringify(payload))
  return 0
}

process.exitCode = main()
