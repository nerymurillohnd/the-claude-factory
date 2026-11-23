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
 * A folder holding only a `node` link and a stub `tsc` whose body is script (bash), which answers
 * --version with version first.
 * @param {string} script
 * @param {string} [version]
 * @returns {string}
 */
function stubTsc(script, version = 'Version 6.0.3') {
  const bin = freshDir()
  symlinkSync(process.execPath, join(bin, 'node'))
  writeFileSync(
    join(bin, 'tsc'),
    `#!/usr/bin/env bash\n[ "$1" = --version ] && { echo '${version}'; exit 0; }\n${script}\n`,
  )
  chmodSync(join(bin, 'tsc'), 0o755)
  return bin
}

/**
 * A folder holding a `node` link and a `tsc` link to the real compiler, standing for a global
 * install on PATH.
 * @returns {string}
 */
function globalTsc() {
  const bin = freshDir()
  symlinkSync(process.execPath, join(bin, 'node'))
  symlinkSync(join(TYPESCRIPT ?? '', 'bin', 'tsc'), join(bin, 'tsc'))
  return bin
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
    tool_response: { filePath: join(folder, file) },
    ...extra,
  }
}

/**
 * The PostToolUse event of a Bash call in folder that changed files (bashEditDiff).
 * @param {string} folder
 * @param {string[]} files
 */
function bash(folder, files) {
  return {
    hook_event_name: 'PostToolUse',
    session_id: 'session-1',
    tool_name: 'Bash',
    cwd: folder,
    tool_input: { command: 'generate' },
    tool_response: {
      stdout: '',
      bashEditDiff: { changedFiles: files.map((file) => join(folder, file)) },
    },
  }
}

/**
 * The PostToolBatch event of tool calls in folder, each a [tool name, file] pair.
 * @param {string} folder
 * @param {[string, string][]} calls
 */
function batch(folder, calls) {
  return {
    hook_event_name: 'PostToolBatch',
    session_id: 'session-1',
    cwd: folder,
    tool_calls: calls.map(([tool, file], i) => ({
      tool_name: tool,
      tool_input: tool === 'Bash' ? { command: file } : { file_path: join(folder, file) },
      tool_use_id: `toolu_${i}`,
      tool_response: 'done',
    })),
  }
}

/**
 * Runs the hook with event on stdin.
 * @param {Record<string, unknown>} event
 * @param {{ project?: string, data?: string | null, path?: string, args?: string[] }} [options]
 */
function runHook(event, options = {}) {
  const { CLAUDE_PLUGIN_DATA: _inherited, ...inherited } = process.env
  /** @type {Record<string, string | undefined>} */
  const env = { ...inherited, CLAUDE_PROJECT_DIR: options.project ?? String(event['cwd'] ?? ROOT) }
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
 * @returns {{ systemMessage?: string, hookSpecificOutput?: { hookEventName?: string, additionalContext?: string } }}
 */
function output(stdout) {
  assert.notEqual(stdout.trim(), '', 'the hook printed nothing on stdout')
  assert.doesNotThrow(() => JSON.parse(stdout), `the hook's stdout is not JSON: ${stdout}`)
  return JSON.parse(stdout)
}

/** @param {string} stdout */
function message(stdout) {
  return output(stdout).systemMessage ?? ''
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
  it('blocks an Edit error on PostToolUse with where it is and the skill to fix it', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 2, run.stderr)
    assert.match(run.stderr, /Unresolved type errors in files changed this turn \(src\/a\.ts\)/)
    assert.match(
      run.stderr,
      /src\/a\.ts:1:14 {2}TS2322 {2}Type 'string' is not assignable to type 'number'\./,
    )
    assert.ok(run.stderr.includes(`"${SKILL}"`), run.stderr)
    assert.match(run.stderr, /the LSP tool and Grep/)
    assert.match(message(run.stdout), /found 1 issue in src\/a\.ts/)
  })

  it('blocks the files a Bash command changed, from bashEditDiff', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const run = runHook(bash(folder, ['src/a.ts']))
    assert.equal(run.code, 2, run.stderr)
    assert.match(run.stderr, /src\/a\.ts:1:14 {2}TS2322/)
  })

  it('gives Claude the errors of a whole batch in additionalContext, without stopping the loop', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN, 'src/b.ts': CLEAN })
    const run = runHook(
      batch(folder, [
        ['Edit', 'src/b.ts'],
        ['Write', 'src/a.ts'],
        ['Bash', 'ls'],
      ]),
    )
    assert.equal(run.code, 0, run.stderr)
    assert.equal(output(run.stdout).hookSpecificOutput?.hookEventName, 'PostToolBatch')
    assert.match(context(run.stdout), /src\/a\.ts:1:14 {2}TS2322/)
    assert.match(message(run.stdout), /found 1 issue in src\/a\.ts/)
  })

  it('reports a clean check without claiming every file was type-checked', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/b.ts': CLEAN })
    const run = runHook(edit(folder, 'src/b.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(
      message(run.stdout),
      /the compiler completed without diagnostics under the project's configuration/,
    )
    assert.doesNotMatch(message(run.stdout), /all type-checked/)
  })

  it('lets errors in other files through with their count', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN, 'src/b.ts': CLEAN })
    const run = runHook(edit(folder, 'src/b.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(
      message(run.stdout),
      /1 issue in other files \(their pre-existence was not verified\)/,
    )
  })

  it('counts a TS6133 in another file as an issue there, not as an unchecked run', () => {
    const config = JSON.stringify({ compilerOptions: { noUnusedLocals: true }, include: ['src'] })
    const folder = project({
      'tsconfig.json': config,
      'src/b.ts': CLEAN,
      'src/o.ts': 'export function g() { const unused = 1 }\n',
    })
    const run = runHook(edit(folder, 'src/b.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(message(run.stdout), /1 issue in other files/)
    assert.doesNotMatch(message(run.stdout), /not type-checked/)
  })

  it('reports an edited file the program leaves out', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/b.ts': CLEAN, 'scripts/x.ts': BROKEN })
    const run = runHook(edit(folder, 'scripts/x.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(
      message(run.stdout),
      /scripts\/x\.ts \(not part of the program of .*tsconfig\.json\)/,
    )
    assert.match(context(run.stdout), /did not cover: scripts\/x\.ts/)
  })

  it('reports a solution-style tsconfig.json as not covering the edited file', () => {
    const folder = project({
      'tsconfig.json': JSON.stringify({ files: [], references: [{ path: './tsconfig.app.json' }] }),
      'tsconfig.app.json': JSON.stringify({
        compilerOptions: { composite: true },
        include: ['src'],
      }),
      'src/a.ts': BROKEN,
    })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(message(run.stdout), /src\/a\.ts \(not part of the program/)
    assert.doesNotMatch(message(run.stdout), /completed without diagnostics/)
  })

  it('never passes a project with noCheck on', () => {
    const config = JSON.stringify({ compilerOptions: { noCheck: true }, include: ['src'] })
    const folder = project({ 'tsconfig.json': config, 'src/a.ts': BROKEN })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(message(run.stdout), /did not type-check \(no Check time/)
    assert.match(context(run.stdout), /did not cover the changed files/)
    assert.doesNotMatch(message(run.stdout), /completed without diagnostics/)
  })

  it('reports a missing type library that stops type-checking, with the error', () => {
    const config = JSON.stringify({
      compilerOptions: { types: ['no-such-types'] },
      include: ['src'],
    })
    const folder = project({ 'tsconfig.json': config, 'src/a.ts': BROKEN })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(message(run.stdout), /did not type-check/)
    assert.match(message(run.stdout), /TS2688/)
  })

  it('reports a syntax error in another file that stops type-checking', () => {
    const folder = project({
      'tsconfig.json': TSCONFIG,
      'src/a.ts': BROKEN,
      'src/other.ts': 'export const b = (\n',
    })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(message(run.stdout), /did not type-check/)
    assert.match(message(run.stdout), /TS1109/)
    assert.doesNotMatch(message(run.stdout), /in other files/)
  })

  it('blocks a syntax error in the edited file and says more errors can follow', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': 'export const = 1\n' })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 2, run.stderr)
    assert.match(run.stderr, /tsc stopped before type-checking, so more errors can appear/)
  })

  it('checks configured JavaScript that opts in with // @ts-check', () => {
    const config = JSON.stringify({ compilerOptions: { allowJs: true }, include: ['src'] })
    const folder = project({
      'tsconfig.json': config,
      'src/a.js': '// @ts-check\n/** @type {number} */\nconst v = "a"\n',
    })
    const run = runHook(edit(folder, 'src/a.js'))
    assert.equal(run.code, 2, run.stderr)
    assert.match(run.stderr, /src\/a\.js:3:7 {2}TS2322/)
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
    assert.match(run.stderr, /packages\/a\/src\/a\.ts:1:14 {2}TS2322/)
  })

  it('checks a TypeScript file under no tsconfig.json with the compiler defaults', () => {
    const folder = project({ 'a.ts': BROKEN })
    const run = runHook(edit(folder, 'a.ts'))
    assert.equal(run.code, 2, run.stderr)
    assert.match(run.stderr, /a\.ts:1:14 {2}TS2322/)
  })

  it('reports a JavaScript file under no tsconfig.json as not type-checked', () => {
    const folder = project({ 'a.js': 'const v = 1\n' })
    const run = runHook(edit(folder, 'a.js'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(
      message(run.stdout),
      /a\.js \(no tsconfig\.json: tsc does not type-check JavaScript/,
    )
  })

  it('runs with only a global tsc and no package.json or tsconfig.json', () => {
    const folder = project({ 'a.ts': BROKEN }, false)
    const run = runHook(edit(folder, 'a.ts'), { path: globalTsc() })
    assert.equal(run.code, 2, run.stderr)
    assert.match(run.stderr, /a\.ts:1:14 {2}TS2322/)
  })

  it('runs a pnpm-style shell shim like any tsc', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const shim = join(folder, 'node_modules', '.bin', 'tsc')
    rmSync(shim)
    writeFileSync(shim, `#!/bin/sh\nexec node "${join(TYPESCRIPT ?? '', 'bin', 'tsc')}" "$@"\n`)
    chmodSync(shim, 0o755)
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 2, run.stderr)
  })

  it('stays silent for a Bash call that changed no source file', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const event = { ...bash(folder, []), tool_response: { stdout: '' } }
    const run = runHook(event)
    assert.equal(run.code, 0, run.stderr)
    assert.equal(run.stdout + run.stderr, '')
  })

  it('stays silent for a batch with no Edit or Write of a source file', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN, 'README.md': '# x\n' })
    const run = runHook(
      batch(folder, [
        ['Bash', 'ls'],
        ['Edit', 'README.md'],
      ]),
    )
    assert.equal(run.code, 0, run.stderr)
    assert.equal(run.stdout + run.stderr, '')
  })

  it('stays silent for a file outside the project, or under node_modules or .git', () => {
    const outside = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const folder = project({
      'src/b.ts': CLEAN,
      'node_modules/pkg/x.ts': BROKEN,
      '.git/x.ts': BROKEN,
    })
    for (const run of [
      runHook(edit(outside, 'src/a.ts'), { project: folder }),
      runHook(edit(folder, 'node_modules/pkg/x.ts')),
      runHook(edit(folder, '.git/x.ts')),
    ]) {
      assert.equal(run.code, 0, run.stderr)
      assert.equal(run.stdout + run.stderr, '')
    }
  })

  it('matches files reached through a symlinked project folder', () => {
    const real = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const link = join(freshDir(), 'link')
    symlinkSync(real, link, 'dir')
    const run = runHook(edit(link, 'src/a.ts'), { project: link })
    assert.equal(run.code, 2, run.stderr)
  })

  it('caps the issue list at 100 lines with a count of the rest', () => {
    const lines = Array.from({ length: 300 }, (_, i) => `export const v${i}: number = "a"`).join(
      '\n',
    )
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': `${lines}\n` })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.code, 2)
    assert.match(
      run.stderr,
      /… 200 more \(run tsc --noEmit --pretty false --strict to see them all\)/,
    )
  })

  it('leaves no .tsbuildinfo in an incremental project', () => {
    const config = JSON.stringify({ compilerOptions: { incremental: true }, include: ['src'] })
    const folder = project({ 'tsconfig.json': config, 'src/b.ts': CLEAN })
    const run = runHook(edit(folder, 'src/b.ts'))
    assert.equal(run.code, 0, run.stderr)
    assert.match(message(run.stdout), /completed without diagnostics/)
    assert.deepEqual(
      readdirSync(folder).filter((name) => name.endsWith('.tsbuildinfo')),
      [],
    )
  })

  it('blocks on an error in a file changed earlier in the same turn, until the next prompt', () => {
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
    assert.match(second.stderr, /src\/a\.ts:1:7 {2}TS2322/)
    const prompt = {
      hook_event_name: 'UserPromptSubmit',
      session_id: 'session-1',
      cwd: folder,
      prompt: 'x',
    }
    const reset = runHook(prompt, { data, args: ['--new-turn'] })
    assert.equal(reset.code, 0)
    assert.equal(reset.stdout + reset.stderr, '')
    writeFileSync(join(folder, 'src/c.ts'), CLEAN)
    const third = runHook(edit(folder, 'src/c.ts'), { data })
    assert.equal(third.code, 0, third.stderr)
    assert.match(message(third.stdout), /in other files/)
  })

  it('keeps a subagent turn list apart from the main one', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN, 'src/b.ts': CLEAN })
    const data = freshDir()
    assert.equal(runHook(edit(folder, 'src/a.ts', { agent_id: 'agent-1' }), { data }).code, 2)
    const main = runHook(edit(folder, 'src/b.ts'), { data })
    assert.equal(main.code, 0, main.stderr)
    assert.match(message(main.stdout), /in other files/)
  })

  it('says turn tracking is unavailable without CLAUDE_PLUGIN_DATA', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/b.ts': CLEAN })
    const run = runHook(edit(folder, 'src/b.ts'), { data: null })
    assert.equal(run.code, 0, run.stderr)
    assert.match(message(run.stdout), /turn tracking unavailable/)
  })
})

describe('tsc-check.sh with a stub or no compiler', { concurrency: true }, () => {
  it('reports a missing compiler', () => {
    const folder = project({ 'a.ts': BROKEN }, false)
    const bin = stubTsc('exit 0')
    rmSync(join(bin, 'tsc'))
    const run = runHook(edit(folder, 'a.ts'), { path: bin })
    assert.equal(run.code, 0, run.stderr)
    assert.match(message(run.stdout), /tsc check skipped: no tsc/)
    assert.match(context(run.stdout), /did not run/)
  })

  it('does not run on a Node.js older than 24, the floor the README states', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN }, false)
    const bin = freshDir()
    writeFileSync(join(bin, 'node'), '#!/bin/sh\necho v22.12.0\n')
    chmodSync(join(bin, 'node'), 0o755)
    const run = runHook(edit(folder, 'src/a.ts'), { path: bin })
    assert.equal(run.code, 0, run.stderr)
    assert.match(
      message(run.stdout),
      /Node\.js v22\.12\.0 is on PATH, and the plugin needs Node\.js 24 or later/,
    )
  })

  it('skips a tsc that is not TypeScript 6 and leaves the decision to the user', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN }, false)
    const run = runHook(edit(folder, 'src/a.ts'), { path: stubTsc('exit 0', 'Version 7.0.0') })
    assert.equal(run.code, 0, run.stderr)
    assert.match(message(run.stdout), /Version 7\.0\.0/)
    assert.match(context(run.stdout), /the user's decision/)
  })

  it('reports a tsc that stops with a signal as not checked', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': CLEAN }, false)
    const run = runHook(edit(folder, 'src/a.ts'), { path: stubTsc('kill -9 $$') })
    assert.equal(run.code, 0, run.stderr)
    assert.match(message(run.stdout), /tsc stopped with status 137/)
  })

  it('fails explicitly on tsc output it cannot classify', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': CLEAN }, false)
    const bin = stubTsc(
      'echo "$PWD/src/a.ts"; echo "something tsc never prints"; echo "Check time: 0.1s"; exit 0',
    )
    const run = runHook(edit(folder, 'src/a.ts'), { path: bin })
    assert.equal(run.code, 1)
    assert.match(run.stderr, /could not classify/)
  })

  it('fails explicitly when tsc fails without any diagnostic', () => {
    const folder = project({ 'tsconfig.json': TSCONFIG, 'src/a.ts': CLEAN }, false)
    const run = runHook(edit(folder, 'src/a.ts'), { path: stubTsc('exit 2') })
    assert.equal(run.code, 1)
    assert.match(run.stderr, /without a diagnostic/)
  })

  it('fails explicitly on input that is not JSON', () => {
    const run = spawnSync(BASH, [HOOK], { input: 'not json', encoding: 'utf8' })
    assert.equal(run.status, 1)
    assert.match(run.stderr, /the hook failed/)
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
