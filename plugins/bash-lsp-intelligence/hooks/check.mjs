#!/usr/bin/env node
// Post-edit hook of bash-lsp-intelligence: shfmt -w, then shellcheck, on the shell files a
// tool call changed. Reads one PostToolUse or PostToolUseFailure event on stdin. The tools
// run the way they run from a terminal and read the user's .editorconfig, .shellcheckrc and
// SHELLCHECK_OPTS; the plugin's defaults (shfmt -i 2 -ci -bn, shellcheck -o all -S style
// -x -a -P SCRIPTDIR) apply only when none of those exists. Exit 0 with a systemMessage when
// everything passed, stderr and exit 2 with findings or when a tool could not run. Files of
// other languages are ignored in silence. Node 18 or later, no dependencies.

import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import {
  existsSync,
  openSync,
  readdirSync,
  readFileSync,
  readSync,
  realpathSync,
  statSync,
} from 'node:fs'
import { homedir } from 'node:os'
import { dirname, join, relative, resolve, sep } from 'node:path'

const PLUGIN = 'bash-lsp-intelligence'
const SHELL_SUFFIXES = new Set(['.sh', '.bash'])
const SHEBANG_SHELL = /^#!(?:\S*\/)?(?:env\s+(?:-S\s+)?)?(sh|bash|zsh)(?:\s|$)/
const SKIPPED_DIRS = new Set(['node_modules', '.venv', 'venv', 'site-packages'])
const PRUNED_DIRS = new Set([...SKIPPED_DIRS, '.git', 'dist', 'build', '__pycache__', '.cache'])
// A Bash command that rewrites more files than this gets the rest reported, not checked.
const MAX_FILES = 20
// Claude Code saves hook output over 10,000 characters to a file Claude never reads.
const MAX_REPORT_CHARS = 9000
// Clock slack added to duration_ms when looking for files a Bash command changed.
const BASH_SLACK_MS = 2000
// Window used when the event carries no duration_ms.
const FALLBACK_WINDOW_MS = 30_000
// Under the hook's 60 s budget, so a hung tool is reported instead of cancelled in silence.
const TOOL_TIMEOUT_MS = 50_000
const MS_PER_S = 1000
const HEAD_BYTES = 256
const SHELLCHECK_FINDINGS_EXIT = 1
const INSTALL_HINTS = {
  shfmt: 'brew install shfmt (macOS) or your distribution package, see the README',
  shellcheck: 'brew install shellcheck (macOS) or your distribution package, see the README',
}
const SHFMT_DEFAULT_ARGS = ['-i', '2', '-ci', '-bn']
const SHELLCHECK_DEFAULT_ARGS = ['-o', 'all', '-S', 'style', '-x', '-a', '-P', 'SCRIPTDIR']

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

function projectDir(event) {
  const candidates = [process.env.CLAUDE_PROJECT_DIR ?? '', textAt(event, 'cwd'), process.cwd()]
  for (const candidate of candidates) {
    if (candidate && isDir(candidate)) {
      return realpath(candidate)
    }
  }
  return null
}

// The canonical path (symlinks resolved, as process.cwd() reports it), so that files and the
// project compare equal whatever spelling the event used.
function realpath(path) {
  try {
    return realpathSync(path)
  } catch {
    return resolve(path)
  }
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
  return { code: result.status, output: `${result.stdout}${result.stderr}`.trim() }
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
  return changedSince(project, nowMs - windowMs)
}

function firstLine(path) {
  try {
    const fd = openSync(path, 'r')
    const buffer = Buffer.alloc(HEAD_BYTES)
    const read = readSync(fd, buffer, 0, HEAD_BYTES, 0)
    return buffer.toString('utf8', 0, read).split('\n')[0]
  } catch {
    return ''
  }
}

// 'sh' | 'bash' | 'zsh' | null: the dialect by suffix or shebang; null means not a shell file.
function dialect(path) {
  const name = path.slice(path.lastIndexOf(sep) + 1)
  const dot = name.lastIndexOf('.')
  const suffix = dot > 0 ? name.slice(dot) : ''
  if (suffix === '.zsh') {
    return 'zsh'
  }
  const match = SHEBANG_SHELL.exec(firstLine(path))
  if (SHELL_SUFFIXES.has(suffix)) {
    return match?.[1] === 'zsh' ? 'zsh' : 'bash'
  }
  if (suffix !== '') {
    return null
  }
  return match ? match[1] : null
}

function skipped(path) {
  return path.split(sep).some((part) => SKIPPED_DIRS.has(part))
}

function findUp(start, names) {
  let dir = start
  for (;;) {
    for (const name of names) {
      if (existsSync(join(dir, name))) {
        return join(dir, name)
      }
    }
    const parent = dirname(dir)
    if (parent === dir) {
      return null
    }
    dir = parent
  }
}

function hasEditorconfig(path) {
  return findUp(dirname(path), ['.editorconfig']) !== null
}

function hasShellcheckConfig(path) {
  if ((process.env.SHELLCHECK_OPTS ?? '').trim() !== '') {
    return true
  }
  if (findUp(dirname(path), ['.shellcheckrc', 'shellcheckrc']) !== null) {
    return true
  }
  const xdg = process.env.XDG_CONFIG_HOME ?? join(homedir(), '.config')
  return existsSync(join(homedir(), '.shellcheckrc')) || existsSync(join(xdg, 'shellcheckrc'))
}

function digest(path) {
  try {
    return createHash('sha256').update(readFileSync(path)).digest('hex')
  } catch {
    return ''
  }
}

function checkFile(path, tools) {
  const out = { findings: [], failures: [], rewrote: false }
  const before = digest(path)
  const shfmtArgs = hasEditorconfig(path) ? ['-w', path] : [...SHFMT_DEFAULT_ARGS, '-w', path]
  const format = run([tools.shfmt, ...shfmtArgs])
  if (format.code === null) {
    out.failures.push(`shfmt failed, so ${path} was not checked:\n${format.output}`)
  } else if (format.code !== 0) {
    out.findings.push(`shfmt (${path}):\n${format.output}`)
  }
  out.rewrote = digest(path) !== before
  const checkArgs = hasShellcheckConfig(path) ? [path] : [...SHELLCHECK_DEFAULT_ARGS, path]
  const check = run([tools.shellcheck, ...checkArgs])
  if (check.code === SHELLCHECK_FINDINGS_EXIT) {
    out.findings.push(`shellcheck (${path}):\n${check.output}`)
  } else if (check.code !== 0) {
    out.failures.push(`shellcheck failed, so ${path} was not checked:\n${check.output}`)
  }
  return out
}

function which(tool) {
  const result = spawnSync('sh', ['-c', 'command -v "$1"', 'sh', tool], { encoding: 'utf8' })
  return result.status === 0 ? result.stdout.trim() : null
}

function findTools() {
  const found = {}
  for (const [name, hint] of Object.entries(INSTALL_HINTS)) {
    const executable = which(name)
    if (executable === null) {
      return `${PLUGIN}: ${name} is not installed, so no shell file was checked. Install it: ${hint}\n`
    }
    found[name] = executable
  }
  return found
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

function display(path, base) {
  if (base === null) {
    return path
  }
  const rel = relative(base, path)
  return rel.startsWith('..') ? path : rel.split(sep).join('/')
}

function report(checked, results, unchecked, base) {
  const parts = results.flatMap((result) => [...result.findings, ...result.failures])
  if (unchecked.length > 0) {
    const names = unchecked.map((path) => `  ${display(path, base)}`).join('\n')
    const summary = `${unchecked.length} more shell files changed and were not checked`
    parts.push(`${summary}; run the toolchain on them:\n${names}`)
  }
  if (parts.length === 0) {
    return ''
  }
  const names = checked.map((path) => display(path, base)).join(', ')
  parts.push(`Fix these findings in ${names} before continuing; do not suppress them.`)
  return `${parts.join('\n')}\n`
}

function success(event, checked, results, zsh, base) {
  const eventName = textAt(event, 'hook_event_name') || 'PostToolUse'
  const payload = {}
  if (checked.length > 0) {
    const names = checked.map((path) => display(path, base)).join(', ')
    payload.systemMessage = `${PLUGIN}: shfmt, shellcheck passed · ${names}`
  }
  const notes = []
  const rewritten = checked.filter((_, i) => results[i].rewrote).map((path) => display(path, base))
  if (rewritten.length > 0) {
    notes.push(`shfmt reformatted ${rewritten.join(', ')}; re-read before the next edit.`)
  }
  if (zsh.length > 0) {
    const names = zsh.map((path) => display(path, base)).join(', ')
    notes.push(`ShellCheck does not support zsh; ${names} was not checked.`)
  }
  if (notes.length > 0) {
    payload.hookSpecificOutput = { hookEventName: eventName, additionalContext: notes.join(' ') }
  }
  return Object.keys(payload).length > 0 ? JSON.stringify(payload) : ''
}

function main() {
  const event = readEvent()
  if (event === null) {
    return 0
  }
  const shell = []
  const zsh = []
  for (const path of candidates(event, Date.now())) {
    if (skipped(path)) {
      continue
    }
    const kind = dialect(path)
    if (kind === 'zsh') {
      zsh.push(path)
    } else if (kind !== null) {
      shell.push(path)
    }
  }
  if (shell.length === 0 && zsh.length === 0) {
    return 0
  }
  const base = projectDir(event)
  const tools = shell.length > 0 ? findTools() : {}
  if (typeof tools === 'string') {
    process.stderr.write(tools)
    return 2
  }
  const checked = shell.slice(0, MAX_FILES)
  const unchecked = shell.slice(MAX_FILES)
  const results = checked.map((path) => checkFile(path, tools))
  const text = report(checked, results, unchecked, base)
  if (text !== '') {
    process.stderr.write(bounded(text))
    return 2
  }
  process.stdout.write(success(event, checked, results, zsh, base))
  return 0
}

process.exitCode = main()
