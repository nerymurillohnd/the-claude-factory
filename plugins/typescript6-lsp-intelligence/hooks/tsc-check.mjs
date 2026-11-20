#!/usr/bin/env node
// Post-edit hook of typescript6-lsp-intelligence. Reads one PostToolUse event on stdin and runs
// the project's own `tsc --noEmit` for the TypeScript and JavaScript files the tool call changed,
// with nothing added to the project's configuration:
//
// - A file under a tsconfig.json: tsc runs with no file arguments from that folder, so it loads
//   the project's tsconfig.json as it does from a terminal. Only errors in the changed files
//   count; the rest of the project is not Claude's edit.
// - A file under no tsconfig.json: tsc runs on that file with the compiler's defaults. With a
//   tsconfig.json present, file arguments are an error in TypeScript 6 (TS5112).
//
// The changed files come from tool_input.file_path for Edit and Write, and from
// tool_response.bashEditDiff.changedFiles for Bash, which Claude Code fills only when it
// records Bash edits. Errors in the changed files exit 2, so Claude stops and fixes them; a
// clean check exits 0. The compiler is the project's node_modules/typescript first, then a tsc
// on PATH; without one, the user is told and nothing blocks. Node 18 or later, no dependencies.

import { spawnSync } from 'node:child_process'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, isAbsolute, join, relative, resolve } from 'node:path'

const PLUGIN = 'typescript6-lsp-intelligence'
const SKILL_HINT = `Use the ${PLUGIN}:ts-6-writing-and-navigation skill and apply all its knowledge when working on TypeScript and JavaScript files.`
const TS_FILE = /\.(ts|tsx|mts|cts|js|jsx|mjs|cjs)$/
const SKIPPED = /[\\/](node_modules|\.git)[\\/]/
const TSC_TIMEOUT_MS = 110_000
const LINE_BREAK = /\r?\n/
const TSC_ERROR = /^(.+?)\(\d+,\d+\): error TS\d+:/

/** @returns {unknown} */
function readEvent() {
  try {
    return JSON.parse(readFileSync(0, 'utf8'))
  } catch {
    return null
  }
}

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
 * The changed TypeScript and JavaScript files, as absolute paths.
 * @param {unknown} event
 * @returns {string[]}
 */
function changedFiles(event) {
  const eventCwd = at(event, 'cwd')
  const cwd = typeof eventCwd === 'string' ? eventCwd : process.cwd()
  /** @type {string[]} */
  const paths = []
  const edited = at(event, 'tool_input', 'file_path')
  if (typeof edited === 'string') {
    paths.push(edited)
  }
  const listed = at(event, 'tool_response', 'bashEditDiff', 'changedFiles')
  if (Array.isArray(listed)) {
    paths.push(...listed.filter((path) => typeof path === 'string'))
  }
  const files = paths
    .map((path) => (isAbsolute(path) ? path : resolve(cwd, path)))
    .filter((path) => TS_FILE.test(path) && !SKIPPED.test(path) && existsSync(path))
  return [...new Set(files)]
}

/**
 * The nearest folder at or above start that holds name, or null.
 * @param {string} start
 * @param {string} name
 * @returns {string | null}
 */
function findUp(start, name) {
  for (let folder = start; ; folder = dirname(folder)) {
    if (existsSync(join(folder, name))) {
      return folder
    }
    if (dirname(folder) === folder) {
      return null
    }
  }
}

/**
 * Runs tsc from folder with args: the project's typescript package first, then tsc on PATH.
 * @param {string} folder
 * @param {string[]} args
 * @returns {{ output: string, found: boolean }}
 */
function runTsc(folder, args) {
  const local = findUp(folder, join('node_modules', 'typescript', 'bin', 'tsc'))
  const run = local
    ? spawnSync(
        process.execPath,
        [join(local, 'node_modules', 'typescript', 'bin', 'tsc'), ...args],
        {
          cwd: folder,
          encoding: 'utf8',
          timeout: TSC_TIMEOUT_MS,
        },
      )
    : spawnSync('tsc', args, {
        cwd: folder,
        encoding: 'utf8',
        timeout: TSC_TIMEOUT_MS,
        shell: process.platform === 'win32',
      })
  if (run.error && /** @type {NodeJS.ErrnoException} */ (run.error).code === 'ENOENT') {
    return { output: '', found: false }
  }
  if (run.error) {
    return { output: `tsc did not finish: ${run.error.message}\n`, found: true }
  }
  return { output: `${run.stdout ?? ''}${run.stderr ?? ''}`, found: true }
}

/**
 * The lines of tsc output about the files in wanted, each error with its indented lines.
 * @param {string} output
 * @param {string} folder
 * @param {Set<string>} wanted
 * @returns {string}
 */
function errorsFor(output, folder, wanted) {
  const kept = []
  let keep = false
  for (const line of output.split(LINE_BREAK)) {
    const match = TSC_ERROR.exec(line)
    if (match) {
      keep = wanted.has(resolve(folder, match[1] ?? ''))
    } else if (!line.startsWith(' ')) {
      keep = false
    }
    if (keep && line !== '') {
      kept.push(line)
    }
  }
  return kept.join('\n')
}

function main() {
  const event = readEvent()
  const files = changedFiles(event)
  if (files.length === 0) {
    return 0
  }
  /** @type {Map<string | null, string[]>} */
  const groups = new Map()
  for (const file of files) {
    const project = findUp(dirname(file), 'tsconfig.json')
    groups.set(project, [...(groups.get(project) ?? []), file])
  }
  const reports = []
  for (const [project, group] of groups) {
    const folder = project ?? dirname(group[0] ?? '')
    const args = project
      ? ['--noEmit', '--pretty', 'false']
      : ['--noEmit', '--pretty', 'false', ...group]
    const { output, found } = runTsc(folder, args)
    if (!found) {
      const message = `${PLUGIN}: no tsc was found in the project's node_modules or on PATH, so the edited TypeScript and JavaScript files were not type-checked. Install TypeScript 6 (npm install -g typescript@6).`
      process.stdout.write(JSON.stringify({ systemMessage: message }))
      return 0
    }
    const errors = errorsFor(output, folder, new Set(group))
    if (errors !== '') {
      const shown = group.map((file) => relative(folder, file)).join(', ')
      reports.push(`tsc --noEmit found errors in ${shown} (run from ${folder}):\n${errors}`)
    }
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
