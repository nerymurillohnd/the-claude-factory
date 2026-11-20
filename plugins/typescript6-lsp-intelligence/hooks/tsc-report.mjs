// Runs and reports the post-edit check of typescript6-lsp-intelligence; hooks/tsc-check.sh starts
// it with the PostToolUse event on stdin, or with --new-turn on UserPromptSubmit.
//
// It runs the project's own `tsc --noEmit --pretty false --strict`: under the nearest
// tsconfig.json, from that folder with no file arguments, so tsc loads its config natively; under
// none, on the edited TypeScript files with the compiler defaults. The edited files are every file
// Claude changed with Edit, Write, or Bash (from tool_response.bashEditDiff) since the last
// prompt, kept per session and agent in ${CLAUDE_PLUGIN_DATA}/turns/.
//
// Exit 2 with the issues on stderr when an edited file has errors, so Claude fixes them first.
// Exit 0 with a systemMessage for every other result: a clean run, errors in other files, a check
// that errors elsewhere made blind, edited files tsc does not type-check, or a check that could
// not run. Exit 1 when the output can't be classified or a result can't be reported, so nothing
// passes in silence. Silent exit 0 only when no TypeScript or JavaScript file was edited.
// Node 18 or later, no dependencies; macOS and Linux.

import { spawnSync } from 'node:child_process'
import {
  accessSync,
  appendFileSync,
  constants,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  realpathSync,
  rmSync,
  statSync,
  writeFileSync,
} from 'node:fs'
import { createRequire } from 'node:module'
import { tmpdir } from 'node:os'
import { delimiter, dirname, isAbsolute, join, relative, resolve, sep } from 'node:path'

const PLUGIN = 'typescript6-lsp-intelligence'
const SKILL = `${PLUGIN}:ts-6-writing-and-navigation`
const COMMAND = 'tsc --noEmit --pretty false --strict'
const TSC_ARGS = ['--noEmit', '--pretty', 'false', '--strict']
const SOURCE = /\.(ts|tsx|mts|cts|js|jsx|mjs|cjs)$/
const JAVASCRIPT = /\.(js|jsx|mjs|cjs)$/
const DECLARATION = /\.d\.(ts|mts|cts)$/
const LOCATED = /^(.+?)\((\d+),(\d+)\): error (TS\d+): (.*)$/
const GLOBAL = /^error (TS\d+): (.*)$/
const CONTINUATION = /^\s+\S/
const VERSION = /Version (\S+)/
const TS_CHECK = /@ts-check\b/
const TS_NOCHECK = /@ts-nocheck\b/
const LINE_BREAK = /\r?\n/
const UNSAFE = /[^A-Za-z0-9_-]/g
const MAX_REPORT = 9000
const MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000
const BUDGET_MS = Number(process.env['TSC_CHECK_BUDGET_MS']) || 100_000
const STARTED = Date.now()

/** A failure the hook must not pass in silence: exit 1 with its message. */
class Unreported extends Error {}

/**
 * @typedef {{ file: string, line: string, col: string, code: string, text: string }} Issue
 * @typedef {{ folder: string, tsconfig: string | null, files: string[] }} Group
 * @typedef {{
 *   edited: Issue[], other: number, blind: string[], notChecked: string[], incomplete: boolean,
 *   skipped: string[], askUser: boolean, syntaxHidden: boolean, ran: string[]
 * }} Result
 * @typedef {{ located: Issue[], global: string[], listed: Set<string>, unclassified: string[] }} Output
 * @typedef {{ length: number }} Diagnostics
 * @typedef {{
 *   getSyntacticDiagnostics(): Diagnostics, getConfigFileParsingDiagnostics(): Diagnostics,
 *   getOptionsDiagnostics(): Diagnostics, getGlobalDiagnostics(): Diagnostics
 * }} Program
 * @typedef {{ fileNames: string[], options: object, projectReferences?: readonly object[] }} Parsed
 * @typedef {{
 *   sys: object,
 *   createProgram(input: { rootNames: string[], options: object, projectReferences?: readonly object[] | undefined, configFileParsingDiagnostics?: unknown }): Program,
 *   getParsedCommandLineOfConfigFile(file: string, options: object, host: object): Parsed | undefined,
 *   getConfigFileParsingDiagnostics(parsed: Parsed): unknown
 * }} CompilerApi
 */

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
 * The real path of path, or null when it doesn't exist.
 * @param {string} path
 * @returns {string | null}
 */
function real(path) {
  try {
    return realpathSync.native(path)
  } catch {
    return null
  }
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
 * The first executable tsc in a folder of PATH, or null.
 * @returns {string | null}
 */
function tscOnPath() {
  for (const entry of (process.env['PATH'] ?? '').split(delimiter)) {
    const candidate = join(entry, 'tsc')
    try {
      accessSync(candidate, constants.X_OK)
      return candidate
    } catch {
      // Not in this folder of PATH.
    }
  }
  return null
}

/**
 * The project's node_modules/.bin/tsc nearest to folder, else the first tsc on PATH.
 * @param {string} folder
 * @returns {string | null}
 */
function findCompiler(folder) {
  const local = findUp(folder, join('node_modules', '.bin', 'tsc'))
  return local === null ? tscOnPath() : join(local, 'node_modules', '.bin', 'tsc')
}

/**
 * Runs the compiler with args from folder, within what is left of the time budget.
 * @param {string} tsc
 * @param {string[]} args
 * @param {string} folder
 * @returns {{ status: number | null, output: string, timedOut: boolean, failure: string }}
 */
function runTsc(tsc, args, folder) {
  const left = BUDGET_MS - (Date.now() - STARTED)
  if (left <= 0) {
    return { status: null, output: '', timedOut: true, failure: '' }
  }
  const run = spawnSync(tsc, args, {
    cwd: folder,
    encoding: 'utf8',
    timeout: left,
    maxBuffer: 256 * 1024 * 1024,
  })
  const code = /** @type {NodeJS.ErrnoException | undefined} */ (run.error)?.code
  return {
    status: run.status,
    output: `${run.stdout ?? ''}${run.stderr ?? ''}`,
    timedOut: code === 'ETIMEDOUT' || (run.signal !== null && run.error === undefined),
    failure: run.error && code !== 'ETIMEDOUT' ? run.error.message : '',
  }
}

/**
 * The comments at the top of text, before the first statement.
 * @param {string} text
 * @returns {string}
 */
function leadingComments(text) {
  let rest = (text.startsWith('#!') ? text.slice(text.indexOf('\n') + 1) : text).trimStart()
  let comments = ''
  while (rest.startsWith('//') || rest.startsWith('/*')) {
    const line = rest.startsWith('//')
    const end = line ? rest.indexOf('\n') : rest.indexOf('*/')
    const stop = end === -1 ? rest.length : end + (line ? 0 : 2)
    comments += `${rest.slice(0, stop)}\n`
    rest = rest.slice(stop).trimStart()
  }
  return comments
}

/**
 * The pragmas in the leading comments of a file: @ts-check and @ts-nocheck.
 * @param {string} file
 * @returns {{ check: boolean, nocheck: boolean }}
 */
function pragmas(file) {
  try {
    const comments = leadingComments(readFileSync(file, 'utf8').slice(0, 8192))
    return { check: TS_CHECK.test(comments), nocheck: TS_NOCHECK.test(comments) }
  } catch {
    return { check: false, nocheck: false }
  }
}

/**
 * True when value has the compiler API functions the phase check calls.
 * @param {unknown} value
 * @returns {value is CompilerApi}
 */
function isCompilerApi(value) {
  if (typeof value !== 'object' || value === null) {
    return false
  }
  const api = /** @type {Record<string, unknown>} */ (value)
  return (
    typeof api['sys'] === 'object' &&
    ['createProgram', 'getParsedCommandLineOfConfigFile', 'getConfigFileParsingDiagnostics'].every(
      (name) => typeof api[name] === 'function',
    )
  )
}

/**
 * The compiler API of the package the tsc at tsc belongs to, or null.
 * @param {string} tsc
 * @returns {CompilerApi | null}
 */
function compilerApi(tsc) {
  const bin = real(tsc)
  if (bin === null) {
    return null
  }
  try {
    const loaded = createRequire(bin)(join(dirname(dirname(bin)), 'lib', 'typescript.js'))
    return isCompilerApi(loaded) ? loaded : null
  } catch {
    return null
  }
}

/**
 * The program tsc built for group, or null when its config can't be parsed at all.
 * @param {CompilerApi} ts
 * @param {Group} group
 * @returns {Program | null}
 */
function buildProgram(ts, group) {
  const cli = { noEmit: true, strict: true }
  if (group.tsconfig === null) {
    return ts.createProgram({ rootNames: group.files, options: cli })
  }
  const host = { ...ts.sys, onUnRecoverableConfigFileDiagnostic: () => undefined }
  const parsed = ts.getParsedCommandLineOfConfigFile(group.tsconfig, cli, host)
  if (parsed === undefined) {
    return null
  }
  return ts.createProgram({
    rootNames: parsed.fileNames,
    options: parsed.options,
    projectReferences: parsed.projectReferences,
    configFileParsingDiagnostics: ts.getConfigFileParsingDiagnostics(parsed),
  })
}

/**
 * Whether semantic checking was suppressed in this run: tsc reports semantic errors only when
 * the config, option, global and syntactic diagnostics are all empty. Asks the compiler API of
 * the package the tsc that ran belongs to. Returns null when that package can't be loaded.
 * @param {string} tsc
 * @param {Group} group
 * @returns {{ suppressed: boolean, syntactic: boolean } | null}
 */
function phases(tsc, group) {
  const ts = compilerApi(tsc)
  if (ts === null) {
    return null
  }
  const program = buildProgram(ts, group)
  if (program === null) {
    return { suppressed: true, syntactic: false }
  }
  const syntactic = program.getSyntacticDiagnostics().length > 0
  const suppressed =
    syntactic ||
    program.getConfigFileParsingDiagnostics().length > 0 ||
    program.getOptionsDiagnostics().length > 0 ||
    program.getGlobalDiagnostics().length > 0
  return { suppressed, syntactic }
}

/**
 * Adds one line of tsc output to parsed and returns whether it was an error line, whose
 * indented continuation lines follow.
 * @param {string} line
 * @param {{ parsed: Output, folder: string, listsFiles: boolean, afterError: boolean }} state
 * @returns {boolean}
 */
function addLine(line, state) {
  const { parsed, folder, listsFiles, afterError } = state
  const match = LOCATED.exec(line)
  if (match) {
    const [, file = '', row = '', col = '', code = '', text = ''] = match
    const absolute = resolve(folder, file)
    parsed.located.push({ file: real(absolute) ?? absolute, line: row, col, code, text })
    return true
  }
  const bare = GLOBAL.exec(line)
  if (bare) {
    parsed.global.push(`${bare[1]}  ${bare[2]}`)
    return true
  }
  if (afterError && CONTINUATION.test(line)) {
    return true
  }
  if (listsFiles && isAbsolute(line)) {
    parsed.listed.add(real(line) ?? line)
  } else if (line.trim() !== '') {
    parsed.unclassified.push(line)
  }
  return false
}

/**
 * Sorts every line of tsc output: located errors, file-less errors, --listFiles paths,
 * continuation lines (dropped), blank lines (dropped) and anything else (unclassified).
 * @param {string} output
 * @param {string} folder
 * @param {boolean} listsFiles
 * @returns {Output}
 */
function parseOutput(output, folder, listsFiles) {
  /** @type {Output} */
  const parsed = { located: [], global: [], listed: new Set(), unclassified: [] }
  let afterError = false
  for (const line of output.split(LINE_BREAK)) {
    afterError = addLine(line, { parsed, folder, listsFiles, afterError })
  }
  return parsed
}

/**
 * The reason tsc does not type-check file, or '' when it does.
 * @param {string} file
 * @param {Group} group
 * @param {Set<string>} listed
 * @param {Record<string, unknown>} options
 * @param {(path: string) => string} show
 * @returns {string}
 */
function uncheckedReason(file, group, listed, options, show) {
  const { check, nocheck } = pragmas(file)
  if (group.tsconfig !== null && !listed.has(file)) {
    return `not part of the program of ${show(group.tsconfig)}`
  }
  if (options['noCheck'] === true) {
    return 'noCheck is on'
  }
  if (nocheck) {
    return '// @ts-nocheck'
  }
  if (DECLARATION.test(file) && options['skipLibCheck'] === true) {
    return 'skipLibCheck skips .d.ts files'
  }
  if (group.tsconfig !== null && JAVASCRIPT.test(file) && options['checkJs'] !== true && !check) {
    return 'JavaScript without checkJs or // @ts-check'
  }
  return ''
}

/**
 * The compiler and its version for group, or null after recording why the check was skipped.
 * @param {Group} group
 * @param {Result} result
 * @returns {{ tsc: string, version: string } | null}
 */
function compilerFor(group, result) {
  const tsc = findCompiler(group.folder)
  if (tsc === null) {
    result.skipped.push(
      "no tsc was found in the project's node_modules/.bin or on PATH (install TypeScript 6: npm install -g typescript@6)",
    )
    return null
  }
  const answer = runTsc(tsc, ['--version'], group.folder)
  const version = VERSION.exec(answer.output)?.[1]
  if (answer.timedOut || version === undefined) {
    result.skipped.push(`${tsc} --version did not answer, so nothing was checked`)
    return null
  }
  if (!version.startsWith('6.')) {
    result.skipped.push(
      `the tsc found is Version ${version} (${tsc}); this plugin checks TypeScript 6 only`,
    )
    result.askUser = true
    return null
  }
  return { tsc, version }
}

/**
 * The effective compilerOptions from `tsc --showConfig`, or null after recording a blind check.
 * @param {string} tsc
 * @param {string} folder
 * @param {Result} result
 * @returns {Record<string, unknown> | null}
 */
function effectiveOptions(tsc, folder, result) {
  const shown = runTsc(tsc, ['--showConfig'], folder)
  try {
    const value = at(JSON.parse(shown.output), 'compilerOptions')
    return typeof value === 'object' && value !== null
      ? /** @type {Record<string, unknown>} */ (value)
      : {}
  } catch {
    const first = shown.output.split(LINE_BREAK).find((line) => line.trim() !== '') ?? '(no output)'
    result.blind.push(`tsc --showConfig in ${folder} printed no JSON: ${first}`)
    return null
  }
}

/**
 * Throws when tsc's output or exit status can't be reported faithfully.
 * @param {Output} output
 * @param {number | null} status
 * @param {string} folder
 */
function assertReportable(output, status, folder) {
  if (output.unclassified.length > 0) {
    throw new Unreported(
      `tsc printed output the hook could not classify, so the edited files were not verified:\n${output.unclassified.slice(0, 20).join('\n')}`,
    )
  }
  const diagnostics = output.located.length + output.global.length
  if (status !== 0 && diagnostics === 0) {
    throw new Unreported(
      `unhandled result (tsc exit ${status ?? 'none'}, no diagnostic in ${folder}), so the edited files were not verified`,
    )
  }
  if (status === 0 && diagnostics > 0) {
    throw new Unreported(
      `unhandled result (tsc exit 0 with diagnostics in ${folder}), so the edited files were not verified`,
    )
  }
}

/**
 * Records the errors of one run in result: edited-file errors, a blind check, or errors in
 * other files, telling the phase apart through the compiler API.
 * @param {Output} output
 * @param {{ tsc: string, group: Group, edited: Set<string>, show: (path: string) => string }} context
 * @param {Result} result
 */
function recordErrors(output, context, result) {
  const { tsc, group, edited, show } = context
  const line = (/** @type {Issue} */ issue) =>
    `${show(issue.file)}:${issue.line}:${issue.col}  ${issue.code}  ${issue.text}`
  const mine = output.located.filter((issue) => edited.has(issue.file))
  const elsewhere = output.located.filter((issue) => !edited.has(issue.file))
  const config = elsewhere.filter(
    (issue) => group.tsconfig !== null && !output.listed.has(issue.file),
  )
  const others = elsewhere.filter((issue) => !config.includes(issue))
  result.edited.push(...mine.map((issue) => ({ ...issue, file: show(issue.file) })))
  if (config.length > 0 || output.global.length > 0) {
    result.blind.push(...config.map(line), ...output.global)
    return
  }
  if (others.length === 0 && mine.length === 0) {
    return
  }
  const phase = phases(tsc, group)
  if (others.length > 0 && phase === null) {
    result.incomplete = true
    result.other += others.length
  } else if (others.length > 0 && phase?.suppressed && mine.length === 0) {
    result.blind.push(...others.map(line))
  } else {
    result.other += others.length
    result.syntaxHidden ||= phase?.syntactic ?? false
  }
}

/**
 * Runs the check of group: from its tsconfig folder with --listFiles and a build-info file in a
 * temporary folder, or on its files with the compiler defaults.
 * @param {string} tsc
 * @param {Group} group
 * @param {string[]} files
 * @returns {ReturnType<typeof runTsc>}
 */
function runCheck(tsc, group, files) {
  const scratch = mkdtempSync(join(tmpdir(), 'tsc-check-'))
  try {
    const args =
      group.tsconfig === null
        ? [...TSC_ARGS, ...files]
        : [...TSC_ARGS, '--listFiles', '--tsBuildInfoFile', join(scratch, 'tsc-check.tsbuildinfo')]
    return runTsc(tsc, args, group.folder)
  } finally {
    rmSync(scratch, { recursive: true, force: true })
  }
}

/**
 * Checks one group and records its findings in result.
 * @param {Group} group
 * @param {Set<string>} edited
 * @param {string} base
 * @param {Result} result
 */
function checkGroup(group, edited, base, result) {
  const show = (/** @type {string} */ path) => relative(base, path) || '.'
  const compiler = compilerFor(group, result)
  if (compiler === null) {
    return
  }
  const options =
    group.tsconfig === null ? {} : effectiveOptions(compiler.tsc, group.folder, result)
  if (options === null) {
    return
  }
  const loose = group.tsconfig === null ? group.files.filter((file) => JAVASCRIPT.test(file)) : []
  result.notChecked.push(
    ...loose.map(
      (file) =>
        `${show(file)} not type-checked (no tsconfig.json: tsc does not type-check JavaScript by default)`,
    ),
  )
  const toRun = group.files.filter((file) => !loose.includes(file))
  if (toRun.length === 0) {
    return
  }
  const run = runCheck(compiler.tsc, group, toRun)
  if (run.timedOut || run.failure !== '') {
    const why = run.timedOut
      ? 'tsc did not finish within the time budget'
      : `tsc could not run (${run.failure})`
    result.skipped.push(`${why} in ${group.folder}, so it was not checked`)
    return
  }
  result.ran.push(`tsc ${compiler.version}, ${compiler.tsc}, run from ${group.folder}`)
  const output = parseOutput(run.output, group.folder, group.tsconfig !== null)
  const listed = group.tsconfig === null ? new Set([...output.listed, ...toRun]) : output.listed
  const checked = { ...output, listed }
  assertReportable(checked, run.status, group.folder)
  for (const file of toRun) {
    const reason = uncheckedReason(file, group, listed, options, show)
    result.notChecked.push(...(reason === '' ? [] : [`${show(file)} not type-checked (${reason})`]))
  }
  recordErrors(checked, { tsc: compiler.tsc, group, edited, show }, result)
}

/**
 * Text cut to limit characters at a line boundary, with a line saying how many were left out.
 * @param {string[]} lines
 * @param {number} limit
 * @returns {string}
 */
function bounded(lines, limit) {
  const kept = []
  let size = 0
  for (const line of lines) {
    if (size + line.length + 1 > limit) {
      kept.push(
        `… ${lines.length - kept.length} more issues in these files (run ${COMMAND} to see them all)`,
      )
      break
    }
    kept.push(line)
    size += line.length + 1
  }
  return kept.join('\n')
}

/**
 * True when this session already got the notice named kind; else records it. Without plugin
 * data, every run gets the notice.
 * @param {string} data
 * @param {string} key
 * @param {string} kind
 * @returns {boolean}
 */
function announced(data, key, kind) {
  if (data === '') {
    return false
  }
  try {
    const folder = join(data, 'notices')
    mkdirSync(folder, { recursive: true })
    const marker = join(folder, `${key}.${kind}`)
    if (existsSync(marker)) {
      return true
    }
    writeFileSync(marker, '')
  } catch {
    return false
  }
  return false
}

/**
 * Deletes files older than MAX_AGE_MS in folder; a failure is ignored.
 * @param {string} folder
 */
function prune(folder) {
  try {
    for (const name of readdirSync(folder)) {
      const path = join(folder, name)
      if (Date.now() - statSync(path).mtimeMs > MAX_AGE_MS) {
        rmSync(path, { force: true })
      }
    }
  } catch {
    // A folder that doesn't exist yet has nothing to prune.
  }
}

/**
 * Prints the outcome after checking that each required field is a non-empty string.
 * @param {string} user
 * @param {string} claude
 * @param {string} name
 */
function emit(user, claude, name) {
  /** @type {Record<string, unknown>} */
  const value = { systemMessage: `${PLUGIN}: ${user}` }
  if (claude !== '') {
    value['hookSpecificOutput'] = { hookEventName: 'PostToolUse', additionalContext: claude }
  }
  const text = JSON.stringify(value)
  const back = JSON.parse(text)
  const contextOk =
    claude === '' || typeof at(back, 'hookSpecificOutput', 'additionalContext') === 'string'
  if (typeof back.systemMessage !== 'string' || user.trim() === '' || !contextOk) {
    throw new Unreported(`the ${name} result could not be reported`)
  }
  process.stdout.write(text)
}

/**
 * The edited files of the turn: this call's files added to the turn list, then the whole list.
 * @param {string[]} now
 * @param {string} list
 * @param {(path: string) => boolean} inProject
 * @returns {string[] | null} null when the list can't be read or written.
 */
function turnFiles(now, list, inProject) {
  try {
    mkdirSync(dirname(list), { recursive: true })
    if (now.length > 0) {
      appendFileSync(list, `${now.join('\n')}\n`)
    }
    const recorded = existsSync(list) ? readFileSync(list, 'utf8').split('\n') : []
    return [
      ...new Set(recorded.filter((path) => path !== '' && existsSync(path) && inProject(path))),
    ]
  } catch {
    return null
  }
}

/**
 * The files of the union grouped by their nearest tsconfig.json, or by folder without one.
 * @param {string[]} union
 * @returns {Group[]}
 */
function groupFiles(union) {
  /** @type {Map<string, Group>} */
  const groups = new Map()
  for (const file of union) {
    const project = findUp(dirname(file), 'tsconfig.json')
    const key = project === null ? `defaults:${dirname(file)}` : `project:${project}`
    const group = groups.get(key) ?? {
      folder: project ?? dirname(file),
      tsconfig: project === null ? null : join(project, 'tsconfig.json'),
      files: [],
    }
    group.files.push(file)
    groups.set(key, group)
  }
  return [...groups.values()]
}

/**
 * Adds the notes for a check that could not run: one for the user every run, and one for Claude
 * once per session.
 * @param {Result} result
 * @param {{ data: string, session: string }} context
 * @param {{ user: string[], claude: string[] }} messages
 */
function skippedNotes(result, context, messages) {
  if (result.skipped.length === 0) {
    return
  }
  const skipped = result.skipped.join('; ')
  messages.user.push(`tsc check skipped: ${skipped}.`)
  if (!announced(context.data, context.session, result.askUser ? 'version' : 'skipped')) {
    messages.claude.push(
      result.askUser
        ? `${PLUGIN}: ${skipped}: tell the user and ask the user what to do before you rely on type checking.`
        : `${PLUGIN}: ${skipped}: tell the user the edited files were not type-checked.`,
    )
  }
}

/**
 * The messages for the user and for Claude about everything except edited-file errors.
 * @param {Result} result
 * @param {{ shown: string, tracking: boolean, data: string, session: string }} context
 * @returns {{ user: string[], claude: string[] }}
 */
function notes(result, context) {
  const user = context.tracking
    ? []
    : ["turn tracking unavailable: only this call's files were checked."]
  const claude = []
  if (result.blind.length > 0) {
    const errors = result.blind.join('\n')
    user.push(
      `errors stopped tsc from type-checking, so the edited files were not type-checked:\n${errors}`,
    )
    claude.push(
      `${PLUGIN}: these errors stopped tsc from type-checking, so the files you edited were not type-checked:\n${errors}\nThen report this to the user before you end your turn.`,
    )
  }
  if (result.notChecked.length > 0) {
    user.push(`${result.notChecked.join('; ')}.`)
    claude.push(
      `${PLUGIN}: ${result.notChecked.join('; ')}; tell the user these files were not type-checked.`,
    )
  }
  if (result.incomplete) {
    user.push(
      'check may be incomplete: errors elsewhere can hide errors in the edited files, and the hook could not load the compiler to tell.',
    )
    claude.push(
      `${PLUGIN}: the check may be incomplete, because errors in other files can hide errors in the files you edited; tell the user.`,
    )
  }
  skippedNotes(result, context, { user, claude })
  if (result.other > 0) {
    const noun = result.other === 1 ? 'issue' : 'issues'
    user.push(
      `no issues reported in the type-checked edited files (${context.shown}); ${result.other} ${noun} in other files (their pre-existence was not verified).`,
    )
  }
  return { user, claude }
}

/**
 * Reports the edited-file errors to Claude on stderr and to the user, and returns exit 2.
 * @param {Result} result
 * @param {{ user: string[], claude: string[] }} messages
 * @returns {number}
 */
function reportEdited(result, messages) {
  const files = [...new Set(result.edited.map((issue) => issue.file))]
  const noun = result.edited.length === 1 ? 'issue' : 'issues'
  const head = `Issues were found in these files you changed: ${files.join(', ')}`
  const tail = [
    ...(result.syntaxHidden ? ['Other files were not type-checked until this is fixed.'] : []),
    `Before you continue: if its instructions aren't in your context, call the Skill tool with skill "${SKILL}"; navigate and explore with the LSP tool and Grep as the skill says; fix these issues; only then go on with the task.`,
  ].join('\n')
  const lines = result.edited.map(
    (issue) => `${issue.file}:${issue.line}:${issue.col}  ${issue.code}  ${issue.text}`,
  )
  process.stderr.write(
    `${head}\n${bounded(lines, MAX_REPORT - head.length - tail.length - 200)}\n${tail}\n`,
  )
  const summary = `${COMMAND} found ${result.edited.length} ${noun} in ${files.join(', ')} (${result.ran.join('; ')}); Claude was told to fix ${result.edited.length === 1 ? 'it' : 'them'} first.`
  emit([summary, ...messages.user].join(' '), messages.claude.join('\n'), 'edited-file errors')
  return 2
}

/**
 * The event's changed files that are TypeScript or JavaScript inside the project, as real paths.
 * @param {unknown} event
 * @param {string} cwd
 * @param {(path: string) => boolean} inProject
 * @returns {string[]}
 */
function changedFiles(event, cwd, inProject) {
  const listed = at(event, 'tool_response', 'bashEditDiff', 'changedFiles')
  /** @type {unknown[]} */
  const raw = [at(event, 'tool_input', 'file_path'), ...(Array.isArray(listed) ? listed : [])]
  const files = raw.flatMap((path) => {
    const file =
      typeof path === 'string' ? real(isAbsolute(path) ? path : resolve(cwd, path)) : null
    return file !== null && inProject(file) ? [file] : []
  })
  return [...new Set(files)]
}

/**
 * The event on stdin.
 * @returns {unknown}
 */
function readEvent() {
  try {
    return JSON.parse(readFileSync(0, 'utf8'))
  } catch {
    throw new Unreported('the hook input is not JSON, so nothing was checked')
  }
}

/**
 * True when nothing but a clean run was recorded.
 * @param {Result} result
 * @returns {boolean}
 */
function isClean(result) {
  return (
    result.blind.length === 0 &&
    result.notChecked.length === 0 &&
    !result.incomplete &&
    result.skipped.length === 0 &&
    result.other === 0
  )
}

/**
 * Checks every group of the union and reports the outcome.
 * @param {string[]} union
 * @param {{ base: string, tracking: boolean, data: string, session: string }} context
 * @returns {number}
 */
function checkAndReport(union, context) {
  /** @type {Result} */
  const result = {
    edited: [],
    other: 0,
    blind: [],
    notChecked: [],
    incomplete: false,
    skipped: [],
    askUser: false,
    syntaxHidden: false,
    ran: [],
  }
  const edited = new Set(union)
  for (const group of groupFiles(union)) {
    checkGroup(group, edited, context.base, result)
  }
  const shown = union.map((file) => relative(context.base, file) || file).join(', ')
  const messages = notes(result, { ...context, shown })
  if (result.edited.length > 0) {
    return reportEdited(result, messages)
  }
  if (isClean(result)) {
    messages.user.push(
      `${COMMAND}: the compiler completed without diagnostics under the project's configuration (${shown}; ${result.ran.join('; ')}).`,
    )
  }
  if (messages.user.length === 0) {
    throw new Unreported(
      'unhandled result (no outcome matched), so the edited files were not verified',
    )
  }
  emit(messages.user.join(' '), messages.claude.join('\n'), 'check')
  return 0
}

/** @returns {number} The hook's exit code. */
function main() {
  const event = readEvent()
  const data = process.env['CLAUDE_PLUGIN_DATA'] ?? ''
  const session = String(at(event, 'session_id') ?? 'unknown').replace(UNSAFE, '_')
  const agentId = at(event, 'agent_id')
  const agent = typeof agentId === 'string' ? agentId.replace(UNSAFE, '_') : 'main'
  const turns = data === '' ? '' : join(data, 'turns')
  if (turns !== '') {
    prune(turns)
    prune(join(data, 'notices'))
  }
  if (process.argv.includes('--new-turn')) {
    if (turns !== '') {
      rmSync(join(turns, `${session}-main.list`), { force: true })
    }
    return 0
  }
  const eventCwd = at(event, 'cwd')
  const cwd = typeof eventCwd === 'string' ? eventCwd : process.cwd()
  const base = real(process.env['CLAUDE_PROJECT_DIR'] || cwd) ?? cwd
  const prefix = base.endsWith(sep) ? base : `${base}${sep}`
  const inProject = (/** @type {string} */ file) =>
    file.startsWith(prefix) &&
    SOURCE.test(file) &&
    file.split(sep).every((part) => part !== 'node_modules' && part !== '.git')
  const now = changedFiles(event, cwd, inProject)
  const recorded =
    turns === '' ? null : turnFiles(now, join(turns, `${session}-${agent}.list`), inProject)
  const union = recorded ?? now
  if (union.length === 0) {
    return 0
  }
  return checkAndReport(union, { base, tracking: recorded !== null, data, session })
}

try {
  process.exitCode = main()
} catch (error) {
  const detail = error instanceof Error ? error.message : String(error)
  const message = error instanceof Unreported ? detail : `the check failed unexpectedly: ${detail}`
  process.stderr.write(`${PLUGIN}: ${message}\n`)
  process.exitCode = 1
}
