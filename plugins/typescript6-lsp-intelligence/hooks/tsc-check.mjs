#!/usr/bin/env node
// Post-edit hook of typescript6-lsp-intelligence. Reads one PostToolUse event on stdin and runs
// the project's own `tsc --noEmit` for the TypeScript and JavaScript files the tool call changed,
// with nothing added to the project's configuration:
//
// - A file under a tsconfig.json: tsc runs with no file arguments from that folder, so it loads
//   the project's tsconfig.json as it does from a terminal. Errors in the changed files, and
//   errors with no file that fail the whole run (a broken config, a missing type library),
//   count; errors in other files are not Claude's edit. A changed file the program leaves out
//   (an include that misses it, a solution-style tsconfig) is not checked, and the user is told.
// - A TypeScript file under no tsconfig.json: tsc runs on that file with the compiler's
//   defaults, since TypeScript 6 rejects file arguments next to a tsconfig.json (TS5112).
//   A JavaScript file there is left alone: tsc does not type-check JavaScript by default.
//
// The changed files come from tool_input.file_path for Edit and Write, and from
// tool_response.bashEditDiff.changedFiles for Bash, which Claude Code fills only when it records
// Bash edits. Errors exit 2, so Claude stops and fixes them; a clean check exits 0. The compiler
// is the project's typescript package, then a tsc on PATH. Without one, or when tsc does not
// finish, the user is told and nothing blocks. Node 18 or later, no dependencies.

import { spawnSync } from 'node:child_process'
import { existsSync, readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, isAbsolute, join, relative, resolve } from 'node:path'

const PLUGIN = 'typescript6-lsp-intelligence'
const SKILL_HINT = `Use the ${PLUGIN}:ts-6-writing-and-navigation skill and apply all its knowledge when working on TypeScript and JavaScript files.`
const TS_FILE = /\.(ts|tsx|mts|cts|js|jsx|mjs|cjs)$/
const JS_FILE = /\.(js|jsx|mjs|cjs)$/
const SKIPPED = /[\\/](node_modules|\.git)[\\/]/
const LINE_BREAK = /\r?\n/
const TSC_ERROR = /^(.+?)\(\d+,\d+\): error TS\d+:/
const GLOBAL_ERROR = /^error TS\d+:/
const TSC_ARGS = ['--noEmit', '--pretty', 'false']
// The hook's own timeout in hooks.json is 120 seconds; every tsc run shares this budget.
const DEADLINE = Date.now() + 110_000
const MAX_OUTPUT_BYTES = 64 * 1024 * 1024
const NO_TSC =
  "no tsc was found in the project's node_modules or on PATH, so the changed TypeScript files were not type-checked. Install TypeScript 6: npm install -g typescript@6"

/**
 * The value at keys inside value, or undefined when a step is not an object.
 * @param {unknown} value
 * @param {string[]} keys
 * @returns {unknown}
 */
function at(value, ...keys) {
  let current = value
  for (const key of keys) {
    if (typeof current !== 'object' || current === null) {
      return undefined
    }
    current = /** @type {Record<string, unknown>} */ (current)[key]
  }
  return current
}

/**
 * The changed TypeScript and JavaScript files of the event, as absolute paths.
 * @param {unknown} event
 * @returns {string[]}
 */
function changedFiles(event) {
  const eventCwd = at(event, 'cwd')
  const cwd = typeof eventCwd === 'string' ? eventCwd : process.cwd()
  const listed = at(event, 'tool_response', 'bashEditDiff', 'changedFiles')
  /** @type {unknown[]} */
  const paths = [at(event, 'tool_input', 'file_path'), ...(Array.isArray(listed) ? listed : [])]
  const files = paths
    .filter((path) => typeof path === 'string')
    .map((path) => (isAbsolute(path) ? path : resolve(cwd, path)))
    .filter((path) => TS_FILE.test(path) && !SKIPPED.test(path) && existsSync(path))
  return [...new Set(files)]
}

/**
 * The nearest folder at or above start that holds a tsconfig.json, or null.
 * @param {string} start
 * @returns {string | null}
 */
function projectOf(start) {
  for (let folder = start; ; folder = dirname(folder)) {
    if (existsSync(join(folder, 'tsconfig.json'))) {
      return folder
    }
    if (dirname(folder) === folder) {
      return null
    }
  }
}

/**
 * Runs tsc from folder: the typescript package Node resolves from there, else tsc on PATH.
 * Returns null when there is no compiler.
 * @param {string} folder
 * @param {string[]} args
 * @returns {{ output: string, failure: string } | null}
 */
function runTsc(folder, args) {
  let tsc = ''
  try {
    tsc = createRequire(join(folder, 'noop.js')).resolve('typescript/bin/tsc')
  } catch {
    // No TypeScript package resolves from the project: use a tsc on PATH.
  }
  // On Windows a tsc on PATH is tsc.cmd, which only a shell starts; quote each argument for it.
  const windows = process.platform === 'win32' && tsc === ''
  const run = spawnSync(
    tsc === '' ? 'tsc' : process.execPath,
    tsc === '' ? args.map((arg) => (windows ? `"${arg}"` : arg)) : [tsc, ...args],
    {
      cwd: folder,
      encoding: 'utf8',
      timeout: Math.max(DEADLINE - Date.now(), 1000),
      maxBuffer: MAX_OUTPUT_BYTES,
      shell: windows,
    },
  )
  if (/** @type {NodeJS.ErrnoException | undefined} */ (run.error)?.code === 'ENOENT') {
    return null
  }
  return { output: `${run.stdout}${run.stderr}`, failure: run.error?.message ?? '' }
}

/**
 * The errors in tsc output that belong to the changed files or to no file, each with its
 * indented lines, and the files tsc listed as part of its program.
 * @param {string} output
 * @param {string} folder
 * @param {Set<string>} changed
 * @returns {{ errors: string, listed: Set<string> }}
 */
function readOutput(output, folder, changed) {
  const kept = []
  const listed = new Set()
  let keep = false
  for (const line of output.split(LINE_BREAK)) {
    const match = TSC_ERROR.exec(line)
    if (match) {
      keep = changed.has(resolve(folder, match[1] ?? ''))
    } else if (GLOBAL_ERROR.test(line)) {
      keep = true
    } else if (!line.startsWith(' ')) {
      keep = false
      if (line !== '') {
        listed.add(resolve(folder, line))
      }
    }
    if (keep) {
      kept.push(line)
    }
  }
  return { errors: kept.join('\n'), listed }
}

/**
 * Checks one group of changed files: the errors for Claude, empty when clean, and the notes for
 * the user. Returns null when there is no compiler.
 * @param {string | null} project
 * @param {string[]} files
 * @returns {{ errors: string, notes: string[] } | null}
 */
function checkGroup(project, files) {
  const folder = project ?? dirname(files[0] ?? '')
  const run = runTsc(
    folder,
    project === null ? [...TSC_ARGS, ...files] : [...TSC_ARGS, '--listFiles'],
  )
  if (run === null) {
    return null
  }
  const shown = files.map((file) => relative(folder, file)).join(', ')
  if (run.failure !== '') {
    return {
      errors: '',
      notes: [
        `tsc did not finish in ${folder} (${run.failure}), so ${shown} were not type-checked.`,
      ],
    }
  }
  const { errors, listed } = readOutput(run.output, folder, new Set(files))
  const outside = project === null ? [] : files.filter((file) => !listed.has(file))
  const notes =
    outside.length === 0
      ? []
      : [
          `${outside.map((file) => relative(folder, file)).join(', ')} are not part of the program of ${join(folder, 'tsconfig.json')}, so tsc did not check them.`,
        ]
  return {
    errors:
      errors === ''
        ? ''
        : `tsc --noEmit found errors for ${shown} (run from ${folder}):\n${errors}`,
    notes,
  }
}

function main() {
  let event = null
  try {
    event = JSON.parse(readFileSync(0, 'utf8'))
  } catch {
    return 0
  }
  /** @type {Map<string | null, string[]>} */
  const groups = new Map()
  for (const file of changedFiles(event)) {
    const project = projectOf(dirname(file))
    if (project === null && JS_FILE.test(file)) {
      continue
    }
    const group = groups.get(project)
    if (group) {
      group.push(file)
    } else {
      groups.set(project, [file])
    }
  }
  const reports = []
  const notes = []
  for (const [project, files] of groups) {
    const result = checkGroup(project, files)
    if (result === null) {
      notes.push(NO_TSC)
      break
    }
    if (result.errors !== '') {
      reports.push(result.errors)
    }
    notes.push(...result.notes)
  }
  if (notes.length > 0) {
    process.stdout.write(JSON.stringify({ systemMessage: `${PLUGIN}: ${notes.join(' ')}` }))
  }
  if (reports.length === 0) {
    return 0
  }
  process.stderr.write(
    `${reports.join('\n\n')}\n\nFix these errors before you continue.\n${SKILL_HINT}\n`,
  )
  return 2
}

process.exitCode = main()
