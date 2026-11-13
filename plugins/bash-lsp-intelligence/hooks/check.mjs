#!/usr/bin/env node
// Post-edit hook of bash-lsp-intelligence: shfmt -w, then shellcheck, on the shell files a
// tool call changed. Reads one PostToolUse or PostToolUseFailure event on stdin. The tools
// run the way they run from a terminal and read the user's .editorconfig, .shellcheckrc and
// SHELLCHECK_OPTS; the plugin's defaults (shfmt -i 2 -ci -bn, shellcheck -o all -S style
// -x -a -P SCRIPTDIR) apply only when none of those exists. Exit 0 with a systemMessage when
// everything passed, stderr and exit 2 with findings or when a tool failed on a file. Files of
// other languages are ignored in silence.
//
// The hook judges only what the tool call changed and never blocks because it cannot check:
// - A tool that is not installed gives one notice per session and exit 0.
// - Files that a Bash command left under a nested Git work tree count only when Git lists
//   them as modified or untracked there, so a clone, a checkout or a pull is never checked.
// - More than MAX_FILES files found by modification time alone, outside Git, are an arrival
//   (an extracted archive, a generated tree), not an edit: none is checked, and Claude is told.
// Node 18 or later, no dependencies.

import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import {
  existsSync,
  mkdirSync,
  openSync,
  readdirSync,
  readFileSync,
  readSync,
  realpathSync,
  statSync,
  unlinkSync,
  writeFileSync,
} from 'node:fs'
import { homedir, tmpdir } from 'node:os'
import { dirname, join, parse, relative, resolve, sep } from 'node:path'

/** @typedef {{ code: number | null, output: string }} RunResult */
/** @typedef {{ shfmt: string, shellcheck: string }} Tools */
/** @typedef {{ findings: string[], failures: string[], rewrote: boolean }} FileResult */
// The files a tool call changed, and the folder searched by modification time alone: walked is
// null when the list comes from the tool's input, from Claude Code or from Git.
/** @typedef {{ files: string[], walked: string | null }} Changed */

const { CLAUDE_PLUGIN_DATA, CLAUDE_PROJECT_DIR, SHELLCHECK_OPTS, XDG_CONFIG_HOME } = process.env
const PLUGIN = 'bash-lsp-intelligence'
// Closes every message Claude reads, so a hook that checks is never taken for the whole workflow.
const SKILL_HINT = `Use the ${PLUGIN}:${PLUGIN} skill and apply all its knowledge when working on shell scripts.`
const SHELL_SUFFIXES = new Set(['.sh', '.bash'])
const SHEBANG_SHELL = /^#!(?:\S*\/)?(?:env\s+(?:-S\s+)?)?(sh|bash|zsh)(?:\s|$)/
const SKIPPED_DIRS = new Set(['node_modules', '.venv', 'venv', 'site-packages'])
const PRUNED_DIRS = new Set([...SKIPPED_DIRS, '.git', 'dist', 'build', '__pycache__', '.cache'])
// A Bash command that rewrites more files than this gets the rest reported, not checked.
const MAX_FILES = 20
// The modification-time walk gives up after this many files, so a huge tree stays cheap.
const MAX_WALK_FILES = 20_000
// Claude Code saves hook output over 10,000 characters to a file and passes Claude only its
// path and a 2,000-character preview, so the findings must fit under the cap.
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
// The empty files that keep the "not installed" notice to once per session are deleted after this.
const NOTICE_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000
const SHFMT_DEFAULT_ARGS = ['-i', '2', '-ci', '-bn']
const SHELLCHECK_DEFAULT_ARGS = ['-o', 'all', '-S', 'style', '-x', '-a', '-P', 'SCRIPTDIR']

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

/**
 * @param {Record<string, unknown>} event
 * @returns {string | null}
 */
function projectDir(event) {
  const dirs = [CLAUDE_PROJECT_DIR ?? '', textAt(event, 'cwd'), process.cwd()]
  for (const dir of dirs) {
    if (dir && isDir(dir)) {
      return realpath(dir)
    }
  }
  return null
}

// The canonical path (symlinks resolved, as process.cwd() reports it), so that files and the
// project compare equal whatever spelling the event used.
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
  return { code: result.status, output: `${result.stdout}${result.stderr}`.trim() }
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

// The files Git lists as modified or untracked in work tree `tree`; null outside one, or
// without git.
/**
 * @param {string} tree
 * @returns {string[] | null}
 */
function gitChanged(tree) {
  const inside = run(['git', '-C', tree, 'rev-parse', '--is-inside-work-tree'])
  if (inside.code !== 0) {
    return null
  }
  const args = ['-C', tree, 'ls-files', '-z', '--modified', '--others', '--exclude-standard']
  return run(['git', ...args])
    .output.split('\0')
    .filter(Boolean)
    .map((rel) => join(tree, rel))
}

// Files under project modified after sinceMs: Git's view in a work tree, else a pruned walk.
/**
 * @param {string} project
 * @param {number} sinceMs
 * @returns {Changed}
 */
function changedSince(project, sinceMs) {
  const listed = gitChanged(project)
  if (listed !== null) {
    return { files: listed.filter((path) => newerThan(path, sinceMs)), walked: null }
  }
  if (project === realpath(homedir()) || project === parse(project).root) {
    // A walk of the whole home directory or disk is never worth a hook's budget.
    return { files: [], walked: null }
  }
  /** @type {string[]} */
  const found = []
  walk(project, sinceMs, found, { left: MAX_WALK_FILES })
  return { files: found, walked: project }
}

// The nearest folder between path and top that holds a .git entry: a nested work tree. known
// remembers the answer for every folder visited, so each folder is examined once.
/**
 * @param {string} path
 * @param {string} top
 * @param {Map<string, string | null>} known
 * @returns {string | null}
 */
function nestedTree(path, top, known) {
  /** @type {string[]} */
  const trail = []
  /** @type {string | null} */
  let tree = null
  let dir = dirname(path)
  while (dir !== top && dir.startsWith(`${top}${sep}`)) {
    const seen = known.get(dir)
    if (seen !== undefined) {
      tree = seen
      break
    }
    trail.push(dir)
    if (existsSync(join(dir, '.git'))) {
      tree = dir
      break
    }
    dir = dirname(dir)
  }
  for (const visited of trail) {
    known.set(visited, tree)
  }
  return tree
}

// Splits the files found by modification time under walked. A clone, a checkout or a pull
// writes files with a new modification time that nobody edited: inside a nested Git work tree
// only the files Git lists as modified or untracked are a change (verified), and the rest are
// dropped. Files outside every work tree are loose: nothing tells an edit from an arrival there.
/**
 * @param {readonly string[]} files
 * @param {string} walked
 * @returns {{ verified: string[], loose: string[] }}
 */
function ownChanges(files, walked) {
  /** @type {Map<string, string | null>} */
  const known = new Map()
  /** @type {Map<string, Set<string> | null>} */
  const listed = new Map()
  /** @type {string[]} */
  const verified = []
  /** @type {string[]} */
  const loose = []
  for (const path of files) {
    const tree = nestedTree(path, walked, known)
    if (tree === null) {
      loose.push(path)
      continue
    }
    let changed = listed.get(tree)
    if (changed === undefined) {
      const names = gitChanged(tree)
      changed = names === null ? null : new Set(names)
      listed.set(tree, changed)
    }
    if (changed === null) {
      loose.push(path) // a .git entry Git does not accept as a work tree, or no git
    } else if (changed.has(path)) {
      verified.push(path)
    }
  }
  return { verified, loose }
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
 * The files Git does not ignore. What a command writes into an ignored place, such as the
 * hook scripts a package manager generates on install or a build folder, is output, not
 * source the project maintains. A file outside every work tree is kept.
 * @param {string[]} files
 * @returns {string[]}
 */
function notIgnored(files) {
  /** @type {Map<string, string[]>} */
  const byFolder = new Map()
  for (const file of files) {
    const folder = dirname(file)
    byFolder.set(folder, [...(byFolder.get(folder) ?? []), file])
  }
  /** @type {Set<string>} */
  const ignored = new Set()
  for (const [folder, group] of byFolder) {
    // Exit 0 lists the ignored paths, 1 means none is, 128 that the folder is in no work tree.
    // NUL-separated both ways, which git accepts only on standard input.
    const result = spawnSync('git', ['-C', folder, 'check-ignore', '--stdin', '-z'], {
      input: group.map((file) => `${file}\0`).join(''),
      encoding: 'utf8',
      timeout: TOOL_TIMEOUT_MS,
    })
    if (result.status === 0) {
      for (const path of result.stdout.split('\0')) {
        ignored.add(path)
      }
    }
  }
  return files.filter((file) => !ignored.has(file))
}

/**
 * @param {Record<string, unknown>} event
 * @param {number} nowMs
 * @returns {Changed}
 */
function candidates(event, nowMs) {
  const tool = textAt(event, 'tool_name')
  if (tool === 'Edit' || tool === 'Write') {
    return { files: asFiles([textAt(event, 'tool_input', 'file_path')]), walked: null }
  }
  if (tool !== 'Bash') {
    return { files: [], walked: null }
  }
  const changed = stringsAt(event, 'tool_response', 'bashEditDiff', 'changedFiles')
  if (changed !== null) {
    return { files: notIgnored(asFiles(changed)), walked: null }
  }
  const project = projectDir(event)
  if (project === null) {
    return { files: [], walked: null }
  }
  const { duration_ms: duration } = event
  const windowMs =
    typeof duration === 'number' && Number.isInteger(duration)
      ? duration + BASH_SLACK_MS
      : FALLBACK_WINDOW_MS
  return changedSince(project, nowMs - windowMs)
}

/**
 * @param {string} path
 * @returns {string}
 */
function firstLine(path) {
  try {
    const fd = openSync(path, 'r')
    const buffer = Buffer.alloc(HEAD_BYTES)
    const read = readSync(fd, buffer, 0, HEAD_BYTES, 0)
    return buffer.toString('utf8', 0, read).split('\n')[0] ?? ''
  } catch {
    return ''
  }
}

// 'sh' | 'bash' | 'zsh' | null: the dialect by suffix or shebang; null means not a shell file.
/**
 * @param {string} path
 * @returns {'sh' | 'bash' | 'zsh' | null}
 */
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
  const shell = match?.[1]
  return shell === 'sh' || shell === 'bash' || shell === 'zsh' ? shell : null
}

/**
 * @param {string} path
 * @returns {boolean}
 */
function skipped(path) {
  return path.split(sep).some((part) => SKIPPED_DIRS.has(part))
}

/**
 * @param {string} start
 * @param {readonly string[]} names
 * @returns {string | null}
 */
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

/**
 * @param {string} path
 * @returns {boolean}
 */
function hasEditorconfig(path) {
  return findUp(dirname(path), ['.editorconfig']) !== null
}

/**
 * @param {string} path
 * @returns {boolean}
 */
function hasShellcheckConfig(path) {
  if ((SHELLCHECK_OPTS ?? '').trim() !== '') {
    return true
  }
  if (findUp(dirname(path), ['.shellcheckrc', 'shellcheckrc']) !== null) {
    return true
  }
  const xdg = XDG_CONFIG_HOME ?? join(homedir(), '.config')
  return existsSync(join(homedir(), '.shellcheckrc')) || existsSync(join(xdg, 'shellcheckrc'))
}

/**
 * @param {string} path
 * @returns {string}
 */
function digest(path) {
  try {
    return createHash('sha256').update(readFileSync(path)).digest('hex')
  } catch {
    return ''
  }
}

/**
 * @param {string} path
 * @param {Tools} tools
 * @returns {FileResult}
 */
function checkFile(path, tools) {
  /** @type {FileResult} */
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

/**
 * @param {string} tool
 * @returns {string | null}
 */
function which(tool) {
  const result = spawnSync('sh', ['-c', 'command -v "$1"', 'sh', tool], { encoding: 'utf8' })
  return result.status === 0 ? result.stdout.trim() : null
}

// The tools' paths, or the name of the first one that is not installed.
/** @returns {Tools | keyof typeof INSTALL_HINTS} */
function findTools() {
  const shfmt = which('shfmt')
  if (shfmt === null) {
    return 'shfmt'
  }
  const shellcheck = which('shellcheck')
  if (shellcheck === null) {
    return 'shellcheck'
  }
  return { shfmt, shellcheck }
}

// True when this session already got the notice about tool; else records it. One empty file
// per session and tool, in ${CLAUDE_PLUGIN_DATA}/notices or, when that variable is unset, in a
// folder named after the plugin in the temporary directory.
/**
 * @param {Record<string, unknown>} event
 * @param {string} tool
 * @returns {boolean}
 */
function announced(event, tool) {
  const session = (textAt(event, 'session_id') || 'unknown').replace(/[^A-Za-z0-9_-]/g, '_')
  const folder = join(CLAUDE_PLUGIN_DATA || join(tmpdir(), PLUGIN), 'notices')
  const marker = join(folder, `${session}.${tool}`)
  if (newerThan(marker, -1)) {
    return true
  }
  try {
    mkdirSync(folder, { recursive: true })
    const expired = Date.now() - NOTICE_MAX_AGE_MS
    for (const entry of readdirSync(folder, { withFileTypes: true })) {
      const old = join(folder, entry.name)
      if (entry.isFile() && statSync(old).mtimeMs < expired) {
        unlinkSync(old)
      }
    }
    writeFileSync(marker, '')
  } catch {
    // Without a marker the notice repeats, which beats never telling the user.
  }
  return false
}

// One JSON object that adds context for Claude and, with message, a line for the user.
/**
 * @param {Record<string, unknown>} event
 * @param {string} context
 * @param {string} [message]
 * @returns {string}
 */
function contextJson(event, context, message) {
  const hookEventName = textAt(event, 'hook_event_name') || 'PostToolUse'
  const hookSpecificOutput = { hookEventName, additionalContext: context }
  return JSON.stringify(
    message ? { systemMessage: message, hookSpecificOutput } : { hookSpecificOutput },
  )
}

// The JSON stdout that says tool is not installed, once per session; '' afterwards.
/**
 * @param {Record<string, unknown>} event
 * @param {keyof typeof INSTALL_HINTS} tool
 * @returns {string}
 */
function missingNotice(event, tool) {
  if (announced(event, tool)) {
    return ''
  }
  return contextJson(
    event,
    `${PLUGIN}: ${tool} is not installed, so the hook does not check the shell files changed in this session. Do not treat them as checked. ${SKILL_HINT}`,
    `${PLUGIN}: ${tool} is not installed, so shell files are not checked. Install it: ${INSTALL_HINTS[tool]}`,
  )
}

// What Claude is told when a command left more loose files than the hook checks.
/**
 * @param {number} count
 * @returns {string}
 */
function arrivalNote(count) {
  return `${PLUGIN}: this command left ${count} shell files outside a Git work tree, more than the ${MAX_FILES} the hook checks per command, so none of them was checked or reformatted. If you edited them, run shfmt and shellcheck on them.`
}

// Cuts text so that it and the reserved characters (the skill hint) fit under the cap.
/**
 * @param {string} text
 * @param {number} reserve
 * @returns {string}
 */
function bounded(text, reserve) {
  const limit = MAX_REPORT_CHARS - reserve
  if (text.length <= limit) {
    return text
  }
  const lines = text.split('\n')
  /** @type {string[]} */
  const kept = []
  let size = 0
  for (const line of lines) {
    if (size + line.length + 1 > limit) {
      break
    }
    kept.push(line)
    size += line.length + 1
  }
  return `${kept.join('\n')}\n… ${lines.length - kept.length} more lines\n`
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

/**
 * @param {readonly string[]} checked
 * @param {readonly FileResult[]} results
 * @param {readonly string[]} unchecked
 * @param {string | null} base
 * @returns {string}
 */
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

/**
 * @param {Record<string, unknown>} event
 * @param {readonly string[]} checked
 * @param {readonly FileResult[]} results
 * @param {readonly string[]} zsh
 * @param {string | null} base
 * @param {string} arrival
 * @returns {string}
 */
function success(event, checked, results, zsh, base, arrival) {
  const eventName = textAt(event, 'hook_event_name') || 'PostToolUse'
  /** @type {{ systemMessage?: string, hookSpecificOutput?: { hookEventName: string, additionalContext: string } }} */
  const payload = {}
  if (checked.length > 0) {
    const names = checked.map((path) => display(path, base)).join(', ')
    payload.systemMessage = `${PLUGIN}: shfmt, shellcheck passed · ${names}`
  }
  /** @type {string[]} */
  const notes = []
  const rewritten = checked
    .filter((_, i) => results[i]?.rewrote === true)
    .map((path) => display(path, base))
  if (rewritten.length > 0) {
    notes.push(`shfmt reformatted ${rewritten.join(', ')}; re-read before the next edit.`)
  }
  if (zsh.length > 0) {
    const names = zsh.map((path) => display(path, base)).join(', ')
    notes.push(`ShellCheck does not support zsh; ${names} was not checked.`)
  }
  if (arrival !== '') {
    notes.push(arrival)
  }
  if (notes.length > 0) {
    notes.push(SKILL_HINT)
    payload.hookSpecificOutput = { hookEventName: eventName, additionalContext: notes.join(' ') }
  }
  return Object.keys(payload).length > 0 ? JSON.stringify(payload) : ''
}

// The shell and zsh files to check, and the note about loose files left unchecked ('' for none).
/**
 * @param {Record<string, unknown>} event
 * @returns {{ shell: string[], zsh: string[], arrival: string }}
 */
function changedShell(event) {
  const changed = candidates(event, Date.now())
  /** @type {Map<string, 'sh' | 'bash' | 'zsh'>} */
  const kinds = new Map()
  for (const path of changed.files) {
    const kind = skipped(path) ? null : dialect(path)
    if (kind !== null) {
      kinds.set(path, kind)
    }
  }
  let files = [...kinds.keys()]
  let arrival = ''
  if (changed.walked !== null) {
    const { verified, loose } = ownChanges(files, changed.walked)
    if (loose.length > MAX_FILES) {
      arrival = arrivalNote(loose.length)
      files = verified
    } else {
      files = [...verified, ...loose]
    }
  }
  return {
    shell: files.filter((path) => kinds.get(path) !== 'zsh'),
    zsh: files.filter((path) => kinds.get(path) === 'zsh'),
    arrival,
  }
}

/** @returns {number} */
function main() {
  const event = readEvent()
  if (event === null) {
    return 0
  }
  const { shell, zsh, arrival } = changedShell(event)
  if (shell.length === 0 && zsh.length === 0) {
    if (arrival !== '') {
      process.stdout.write(contextJson(event, `${arrival} ${SKILL_HINT}`))
    }
    return 0
  }
  const base = projectDir(event)
  const tools = shell.length > 0 ? findTools() : null
  if (typeof tools === 'string') {
    process.stdout.write(missingNotice(event, tools))
    return 0
  }
  const checked = shell.slice(0, MAX_FILES)
  const unchecked = shell.slice(MAX_FILES)
  const results = tools === null ? [] : checked.map((path) => checkFile(path, tools))
  const text = report(checked, results, unchecked, base)
  if (text !== '') {
    const full = arrival === '' ? text : `${text}${arrival}\n`
    process.stderr.write(`${bounded(full, SKILL_HINT.length + 1)}${SKILL_HINT}\n`)
    return 2
  }
  process.stdout.write(success(event, checked, results, zsh, base, arrival))
  return 0
}

process.exitCode = main()
