// Tests for typescript6-lsp-intelligence's hooks/tsc-check.sh, run as Claude Code runs it: bash
// as a subprocess with the event JSON on stdin. Cases with the real compiler need a TypeScript 6
// package that resolves from here (the marketplace repository's devDependency) and skip without
// one; the other cases put a stub tsc first on PATH.

import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import {
  chmodSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs'
import { createRequire } from 'node:module'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { after, describe, it } from 'node:test'
import { fileURLToPath } from 'node:url'

const HOOK = join(dirname(fileURLToPath(import.meta.url)), '..', 'hooks', 'tsc-check.sh')
const SKILL = 'typescript6-lsp-intelligence:ts-6-writing-and-navigation'

/** @returns {string | null} */
function typescriptPackage() {
  try {
    return dirname(createRequire(import.meta.url).resolve('typescript/package.json'))
  } catch {
    return null
  }
}

const TYPESCRIPT = typescriptPackage()
const BASH = spawnSync('sh', ['-c', 'command -v bash'], { encoding: 'utf8' }).stdout.trim()
// The system PATH without any folder that holds a tsc, so a stub folder put first is the only tsc.
const PATH_WITHOUT_TSC = (process.env['PATH'] ?? '')
  .split(':')
  .filter((folder) => folder !== '' && !existsSync(join(folder, 'tsc')))
  .join(':')
const ROOT = mkdtempSync(join(tmpdir(), 'tsc-check-sh-test-'))
after(() => rmSync(ROOT, { recursive: true, force: true }))

let counter = 0
/** @returns {string} A new empty folder under ROOT. */
function freshDir() {
  counter += 1
  const folder = join(ROOT, `d${counter}`)
  mkdirSync(folder, { recursive: true })
  return folder
}

/**
 * A project folder with files, and node_modules/typescript plus node_modules/.bin/tsc linked to
 * the real compiler unless withCompiler is false.
 * @param {Record<string, string>} files
 * @param {boolean} [withCompiler]
 * @returns {string}
 */
function project(files, withCompiler = true) {
  const folder = freshDir()
  for (const [path, text] of Object.entries(files)) {
    mkdirSync(dirname(join(folder, path)), { recursive: true })
    writeFileSync(join(folder, path), text)
  }
  if (withCompiler && TYPESCRIPT !== null) {
    mkdirSync(join(folder, 'node_modules', '.bin'), { recursive: true })
    symlinkSync(TYPESCRIPT, join(folder, 'node_modules', 'typescript'), 'dir')
    symlinkSync('../typescript/bin/tsc', join(folder, 'node_modules', '.bin', 'tsc'))
  }
  return folder
}

/**
 * A folder holding only a `node` link and a stub `tsc` whose body is script (bash).
 * @param {string} script
 * @returns {string}
 */
function stubBin(script) {
  const bin = freshDir()
  symlinkSync(process.execPath, join(bin, 'node'))
  writeFileSync(join(bin, 'tsc'), `#!/usr/bin/env bash\n${script}\n`)
  chmodSync(join(bin, 'tsc'), 0o755)
  return bin
}

/**
 * A stub tsc answering --version and --showConfig, then running main.
 * @param {string} main
 * @param {{ version?: string, showConfig?: string }} [options]
 * @returns {string}
 */
function stubTsc(main, { version = 'Version 6.0.3', showConfig = '{"compilerOptions":{}}' } = {}) {
  return stubBin(
    [
      'case " $* " in',
      `  *" --version "*) echo '${version}'; exit 0 ;;`,
      `  *" --showConfig "*) echo '${showConfig}'; exit 0 ;;`,
      'esac',
      main,
    ].join('\n'),
  )
}

/**
 * The PostToolUse event of an Edit of file in folder.
 * @param {string} folder
 * @param {string} file
 * @param {Record<string, unknown>} [extra]
 */
function edit(folder, file, extra = {}) {
  return {
    hook_event_name: 'PostToolUse',
    session_id: 'session-1',
    tool_name: 'Edit',
    cwd: folder,
    tool_input: { file_path: join(folder, file) },
    ...extra,
  }
}

/**
 * Runs the hook with event on stdin.
 * @param {Record<string, unknown>} event
 * @param {{ project?: string, data?: string | null, path?: string, args?: string[], env?: Record<string, string> }} [options]
 */
function runHook(event, options = {}) {
  const { CLAUDE_PLUGIN_DATA: _inherited, ...inherited } = process.env
  /** @type {Record<string, string | undefined>} */
  const env = {
    ...inherited,
    ...options.env,
    CLAUDE_PROJECT_DIR: options.project ?? String(event['cwd'] ?? ROOT),
  }
  if (options.data !== null) {
    env['CLAUDE_PLUGIN_DATA'] = options.data ?? freshDir()
  }
  if (options.path !== undefined) {
    env['PATH'] = `${options.path}:${PATH_WITHOUT_TSC}`
  }
  const run = spawnSync(BASH, [HOOK, ...(options.args ?? [])], {
    input: JSON.stringify(event),
    encoding: 'utf8',
    env,
  })
  return { code: run.status, stdout: run.stdout, stderr: run.stderr }
}

/**
 * The JSON object the hook printed on stdout.
 * @param {string} stdout
 * @returns {{ systemMessage?: string, hookSpecificOutput?: { additionalContext?: string } }}
 */
function output(stdout) {
  assert.notEqual(stdout.trim(), '', 'the hook printed nothing on stdout')
  return JSON.parse(stdout)
}

/** @param {string} stdout */
function context(stdout) {
  return output(stdout).hookSpecificOutput?.additionalContext ?? ''
}

const TSCONFIG = JSON.stringify({ include: ['src'] })
const BROKEN = 'export const x: number = "a"\n'
const CLEAN = 'export const y: number = 1\n'
const REAL = TYPESCRIPT === null ? 'no typescript package resolves' : false

describe('tsc-check.sh with the real compiler', { skip: REAL, concurrency: true }, () => {
  it('blocks an error in the edited file, listing where it is and how to fix it', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 2, run.stderr)
    assert.match(run.stderr, /Issues were found in these files you changed: src\/a\.ts/)
    assert.match(
      run.stderr,
      /src\/a\.ts:1:14\s+TS2322\s+Type 'string' is not assignable to type 'number'\./,
    )
    assert.ok(run.stderr.includes(`call the Skill tool with skill "${SKILL}"`), run.stderr)
    assert.match(run.stderr, /the LSP tool and Grep/)
    assert.match(output(run.stdout).systemMessage ?? '', /found 1 issue/)
  })

  it('reports a clean check without claiming every file was type-checked', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/b.ts': CLEAN })
    const run = runHook(edit(folder, 'src/b.ts'))
    assert.equal(run.code, 0, run.stderr)
    const message = output(run.stdout).systemMessage ?? ''
    assert.match(
      message,
      /the compiler completed without diagnostics under the project's configuration/,
    )
    assert.doesNotMatch(message, /all type-checked/)
  })

  it('lets errors in other files through with their count', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN, 'src/b.ts': CLEAN })
    const run = runHook(edit(folder, 'src/b.ts'))
    assert.equal(run.code, 0, run.stderr)
    const message = output(run.stdout).systemMessage ?? ''
    assert.match(message, /1 issue in other files/)
    assert.match(message, /pre-existence was not verified/)
  })

  it('does not count TS6133 in another file as a blind check', () => {
    const config = JSON.stringify({ compilerOptions: { noUnusedLocals: true }, include: ['src'] })
    const folder = project({
      'tsconfig.json': config,
      'src/b.ts': CLEAN,
      'src/o.ts': 'export function g() { const unused = 1 }\n',
    })
    const run = runHook(edit(folder, 'src/b.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /1 issue in other files/)
    assert.doesNotMatch(output(run.stdout).systemMessage ?? '', /not type-checked/)
  })

  it('reports an edited file the program leaves out', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/b.ts': CLEAN, 'scripts/x.ts': BROKEN })
    const run = runHook(edit(folder, 'scripts/x.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /scripts\/x\.ts.*not part of the program/)
    assert.match(context(run.stdout), /tell the user/)
  })

  it('never passes a project with noCheck on', () => {
    const config = JSON.stringify({ compilerOptions: { noCheck: true }, include: ['src'] })
    const folder = project({ 'tsconfig.json': config, 'src/a.ts': BROKEN })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /noCheck is on/)
    assert.match(context(run.stdout), /noCheck is on/)
    assert.doesNotMatch(output(run.stdout).systemMessage ?? '', /completed without diagnostics/)
  })

  it('reports configured JavaScript without checkJs as not type-checked', () => {
    const config = JSON.stringify({ compilerOptions: { allowJs: true }, include: ['src'] })
    const folder = project({ 'tsconfig.json': config, 'src/a.js': 'const v = 1\n' })
    const run = runHook(edit(folder, 'src/a.js'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /src\/a\.js.*JavaScript without checkJs/)
  })

  it('checks configured JavaScript that opts in with // @ts-check', () => {
    const config = JSON.stringify({ compilerOptions: { allowJs: true }, include: ['src'] })
    const folder = project({
      'tsconfig.json': config,
      'src/a.js': '// @ts-check\n/** @type {number} */\nconst v = "a"\n',
    })
    const run = runHook(edit(folder, 'src/a.js'))
    assert.equal(run.code, 2, run.stderr)
    assert.match(run.stderr, /src\/a\.js:3:7\s+TS2322/)
  })

  it('reports a file with // @ts-nocheck as not type-checked', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': `// @ts-nocheck\n${BROKEN}` })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /@ts-nocheck/)
  })

  it('reports an edited declaration file under skipLibCheck as not type-checked', () => {
    const config = JSON.stringify({ compilerOptions: { skipLibCheck: true }, include: ['src'] })
    const folder = project({
      'tsconfig.json': config,
      'src/types.d.ts': 'export declare const q: number\n',
    })
    const run = runHook(edit(folder, 'src/types.d.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /skipLibCheck/)
  })

  it('warns, and tells Claude to report, when a missing type library blinds the check', () => {
    const config = JSON.stringify({
      compilerOptions: { types: ['no-such-types'] },
      include: ['src'],
    })
    const folder = project({ 'tsconfig.json': config, 'src/a.ts': BROKEN })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /TS2688/)
    assert.match(output(run.stdout).systemMessage ?? '', /not type-checked/)
    assert.match(context(run.stdout), /report this to the user before you end your turn/)
  })

  it('treats an unknown option in tsconfig.json as a blind check', () => {
    const config = JSON.stringify({ compilerOptions: { bogusOption: true }, include: ['src'] })
    const folder = project({ 'tsconfig.json': config, 'src/a.ts': BROKEN })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /TS5023/)
    assert.match(context(run.stdout), /report this to the user/)
  })

  it('treats a syntax error in another file as a blind check', () => {
    const folder = project({
      'tsconfig.json': TSCONFIG,
      'src/a.ts': BROKEN,
      'src/other.ts': 'export const b = (\n',
    })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /TS1109/)
    assert.match(context(run.stdout), /report this to the user/)
  })

  it('blocks a syntax error in the edited file and says the rest went unchecked', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': 'export const = 1\n' })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 2, run.stderr)
    assert.match(run.stderr, /Other files were not type-checked until this is fixed/)
  })

  it('finds a nested tsconfig.json from the edited file', () => {
    const folder = project({
      'tsconfig.json': TSCONFIG,
      'src/root.ts': CLEAN,
      'packages/a/tsconfig.json': '{}\n',
      'packages/a/src/a.ts': BROKEN,
    })
    const run = runHook(edit(folder, 'packages/a/src/a.ts'))
    assert.equal(run.code, 2, run.stderr)
    assert.match(run.stderr, /packages\/a\/src\/a\.ts:1:14\s+TS2322/)
  })

  it('checks a TypeScript file under no tsconfig.json with the compiler defaults', () => {
    const folder = project({ 'a.ts': BROKEN })
    const run = runHook(edit(folder, 'a.ts'))
    assert.equal(run.code, 2, run.stderr)
    assert.match(run.stderr, /a\.ts:1:14\s+TS2322/)
  })

  it('reports a JavaScript file under no tsconfig.json as not type-checked', () => {
    const folder = project({ 'a.js': 'const v = 1\n' })
    const run = runHook(edit(folder, 'a.js'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /a\.js.*not type-checked/)
  })

  it('checks the files a Bash command changed, from bashEditDiff', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const event = {
      hook_event_name: 'PostToolUse',
      session_id: 'session-1',
      tool_name: 'Bash',
      cwd: folder,
      tool_input: { command: 'sed -i s/1/2/ src/a.ts' },
      tool_response: { bashEditDiff: { changedFiles: [join(folder, 'src/a.ts')] } },
    }
    assert.equal(runHook(event).code, 2)
  })

  it('stays silent for a Bash call without bashEditDiff and no files this turn', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const event = {
      hook_event_name: 'PostToolUse',
      session_id: 's',
      tool_name: 'Bash',
      cwd: folder,
      tool_input: { command: 'ls' },
    }
    const run = runHook(event)
    assert.equal(run.code, 0, run.stderr)
    assert.equal(run.stdout + run.stderr, '')
  })

  it('stays silent for a file that is not TypeScript or JavaScript', () => {
    const folder = project({ 'README.md': '# x\n' })
    const run = runHook(edit(folder, 'README.md'))
    assert.equal(run.code, 0)
    assert.equal(run.stdout + run.stderr, '')
  })

  it('stays silent for a file outside the project', () => {
    const outside = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const folder = project({ 'src/b.ts': CLEAN })
    const run = runHook(edit(outside, 'src/a.ts'), { project: folder })
    assert.equal(run.code, 0)
    assert.equal(run.stdout + run.stderr, '')
  })

  it('matches files reached through a symlinked project folder', () => {
    const real = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const link = join(freshDir(), 'link')
    symlinkSync(real, link, 'dir')
    const run = runHook(edit(link, 'src/a.ts'), { project: link })
    assert.equal(run.code, 2, run.stderr)
  })

  it('keeps the report under 10,000 characters with many errors', () => {
    const lines = Array.from({ length: 300 }, (_, i) => `export const v${i}: number = "a"`).join(
      '\n',
    )
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': `${lines}\n` })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 2)
    assert.ok(run.stderr.length < 10_000, `stderr is ${run.stderr.length} characters`)
    assert.match(run.stderr, /more issues in these files/)
  })

  it('leaves no .tsbuildinfo in an incremental project', () => {
    const config = JSON.stringify({ compilerOptions: { incremental: true }, include: ['src'] })
    const folder = project({ 'tsconfig.json': config, 'src/b.ts': CLEAN })
    const run = runHook(edit(folder, 'src/b.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /completed without diagnostics/)
    assert.deepEqual(
      readdirSync(folder).filter((name) => name.endsWith('.tsbuildinfo')),
      [],
    )
  })

  it('blocks on an error in a file edited earlier in the same turn', () => {
    const folder = project({
      'tsconfig.json': TSCONFIG,
      'src/a.ts': 'const n: number = f()\n',
      'src/b.ts': 'function f(): number { return 1 }\n',
    })
    const data = freshDir()
    assert.equal(runHook(edit(folder, 'src/a.ts'), { data }).code, 0)
    writeFileSync(join(folder, 'src/b.ts'), 'function f(): string { return "x" }\n')
    const second = runHook(edit(folder, 'src/b.ts'), { data })
    assert.equal(second.code, 2, second.stderr)
    assert.match(second.stderr, /src\/a\.ts:1:7\s+TS2322/)
    const prompt = {
      hook_event_name: 'UserPromptSubmit',
      session_id: 'session-1',
      cwd: folder,
      prompt: 'next',
    }
    const reset = runHook(prompt, { data, args: ['--new-turn'] })
    assert.equal(reset.code, 0)
    assert.equal(reset.stdout, '')
    writeFileSync(join(folder, 'src/c.ts'), CLEAN)
    const third = runHook(edit(folder, 'src/c.ts'), { data })
    assert.equal(third.code, 0, third.stderr)
    assert.match(output(third.stdout).systemMessage ?? '', /in other files/)
  })

  it('keeps a subagent turn list apart from the main one', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN, 'src/b.ts': CLEAN })
    const data = freshDir()
    assert.equal(runHook(edit(folder, 'src/a.ts', { agent_id: 'agent-1' }), { data }).code, 2)
    const main = runHook(edit(folder, 'src/b.ts'), { data })
    assert.equal(main.code, 0, main.stderr)
    assert.match(output(main.stdout).systemMessage ?? '', /in other files/)
  })

  it('says turn tracking is unavailable without CLAUDE_PLUGIN_DATA', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/b.ts': CLEAN })
    const run = runHook(edit(folder, 'src/b.ts'), { data: null })
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /turn tracking unavailable/)
  })
})

describe('tsc-check.sh with a stub or no compiler', { concurrency: true }, () => {
  it('reports a missing compiler on every run, and tells Claude once per session', () => {
    const folder = project({ 'a.ts': BROKEN }, false)
    const bin = stubBin('exit 0')
    rmSync(join(bin, 'tsc'))
    const data = freshDir()
    const first = runHook(edit(folder, 'a.ts'), { data, path: bin })
    const second = runHook(edit(folder, 'a.ts'), { data, path: bin })
    assert.equal(first.code, 0, first.stderr)
    assert.equal(second.code, 0, second.stderr)
    assert.match(output(first.stdout).systemMessage ?? '', /tsc check skipped/)
    assert.match(output(second.stdout).systemMessage ?? '', /tsc check skipped/)
    assert.match(context(first.stdout), /tell the user/)
    assert.equal(context(second.stdout), '')
    const unmarked = runHook(edit(folder, 'a.ts'), { data: null, path: bin })
    assert.match(context(unmarked.stdout), /tell the user/)
  })

  it('skips a tsc that is not TypeScript 6 and has Claude ask the user', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN }, false)
    const bin = stubTsc('exit 0', { version: 'Version 7.0.0' })
    const run = runHook(edit(folder, 'src/a.ts'), { path: bin })
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /Version 7\.0\.0/)
    assert.match(context(run.stdout), /ask the user what to do/)
  })

  it('treats a --showConfig that is not JSON as a blind check', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': CLEAN }, false)
    const bin = stubTsc('exit 0', { showConfig: 'not json' })
    const run = runHook(edit(folder, 'src/a.ts'), { path: bin })
    assert.equal(run.code, 0, run.stderr)
    assert.match(context(run.stdout), /report this to the user/)
  })

  it('says the check may be incomplete when it cannot load the compiler to tell the phase', () => {
    const folder = project(
      { 'tsconfig.json': TSCONFIG, 'src/a.ts': CLEAN, 'src/o.ts': BROKEN },
      false,
    )
    const bin = stubTsc(
      'echo "$PWD/src/a.ts"; echo "$PWD/src/o.ts"; echo "src/o.ts(1,14): error TS2322: Nope."; exit 2',
    )
    const run = runHook(edit(folder, 'src/a.ts'), { path: bin })
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /check may be incomplete/)
    assert.doesNotMatch(output(run.stdout).systemMessage ?? '', /completed without diagnostics/)
  })

  it('reports a tsc that does not finish in time as not checked', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': CLEAN }, false)
    const bin = stubTsc('sleep 5; exit 0')
    const run = runHook(edit(folder, 'src/a.ts'), {
      path: bin,
      env: { TSC_CHECK_BUDGET_MS: '1000' },
    })
    assert.equal(run.code, 0, run.stderr)
    assert.match(output(run.stdout).systemMessage ?? '', /tsc check skipped/)
  })

  it('fails explicitly on tsc output it cannot classify', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': CLEAN }, false)
    const bin = stubTsc('echo "$PWD/src/a.ts"; echo "something tsc never prints"; exit 2')
    const run = runHook(edit(folder, 'src/a.ts'), { path: bin })
    assert.equal(run.code, 1)
    assert.match(run.stderr, /could not classify/)
  })

  it('fails explicitly when tsc fails without any diagnostic', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': CLEAN }, false)
    const bin = stubTsc('exit 2')
    const run = runHook(edit(folder, 'src/a.ts'), { path: bin })
    assert.equal(run.code, 1)
    assert.match(run.stderr, /unhandled result/)
  })

  it('treats the turn reset as silent', () => {
    const run = runHook(
      { hook_event_name: 'UserPromptSubmit', session_id: 's', cwd: ROOT, prompt: 'x' },
      { args: ['--new-turn'] },
    )
    assert.equal(run.code, 0)
    assert.equal(run.stdout + run.stderr, '')
  })
})
