// Tests for typescript6-lsp-intelligence's hooks/tsc-check.mjs, run as Claude Code runs it: a
// subprocess with the event JSON on stdin. They need a TypeScript package that resolves from
// here, such as the marketplace repository's devDependency, and skip without one.

import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { mkdirSync, mkdtempSync, rmSync, symlinkSync, writeFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { after, describe, it } from 'node:test'
import { fileURLToPath } from 'node:url'

const HOOK = join(dirname(fileURLToPath(import.meta.url)), '..', 'hooks', 'tsc-check.mjs')

/** @returns {string | null} */
function typescriptPackage() {
  try {
    return dirname(createRequire(import.meta.url).resolve('typescript/package.json'))
  } catch {
    return null
  }
}

const TYPESCRIPT = typescriptPackage()
const ROOT = mkdtempSync(join(tmpdir(), 'tsc-check-test-'))
after(() => rmSync(ROOT, { recursive: true, force: true }))

/**
 * A folder with files, and a node_modules/typescript link unless withCompiler is false.
 * @param {string} name
 * @param {Record<string, string>} files
 * @param {boolean} [withCompiler]
 * @returns {string}
 */
function project(name, files, withCompiler = true) {
  const folder = join(ROOT, name)
  for (const [path, text] of Object.entries(files)) {
    mkdirSync(dirname(join(folder, path)), { recursive: true })
    writeFileSync(join(folder, path), text)
  }
  if (withCompiler && TYPESCRIPT !== null) {
    mkdirSync(join(folder, 'node_modules'), { recursive: true })
    symlinkSync(TYPESCRIPT, join(folder, 'node_modules', 'typescript'), 'dir')
  }
  return folder
}

/**
 * The PostToolUse event of an Edit of file in folder.
 * @param {string} folder
 * @param {string} file
 */
function edit(folder, file) {
  return { tool_name: 'Edit', cwd: folder, tool_input: { file_path: join(folder, file) } }
}

/**
 * Runs the hook with event on stdin; noCompiler hides every TypeScript outside the project.
 * @param {Record<string, unknown>} event
 * @param {string} [noCompilerPath]
 */
function runHook(event, noCompilerPath) {
  const env =
    noCompilerPath === undefined
      ? process.env
      : { ...process.env, PATH: noCompilerPath, NODE_PATH: '' }
  return spawnSync(process.execPath, [HOOK], {
    input: JSON.stringify({ hook_event_name: 'PostToolUse', ...event }),
    encoding: 'utf8',
    env,
  })
}

const TSCONFIG = JSON.stringify({ compilerOptions: { strict: true }, include: ['src'] })
const BROKEN = 'export const x: number = "a"\n'
const CLEAN = 'export const y: number = 1\n'
const SKIP = TYPESCRIPT === null ? 'no typescript package resolves' : false

describe('tsc-check.mjs', { skip: SKIP, concurrency: true }, () => {
  it('blocks an edit that leaves a type error in the edited file', () => {
    const folder = project('broken', { 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const run = runHook(edit(folder, 'src/a.ts'))
    assert.equal(run.status, 2)
    assert.match(run.stderr, /src[\\/]a\.ts\(1,14\): error TS2322/)
    assert.match(run.stderr, /ts-6-writing-and-navigation/)
  })

  it('lets a clean edit through in silence', () => {
    const folder = project('clean', { 'tsconfig.json': TSCONFIG, 'src/b.ts': CLEAN })
    const run = runHook(edit(folder, 'src/b.ts'))
    assert.equal(run.status, 0)
    assert.equal(run.stdout + run.stderr, '')
  })

  it('ignores errors in files the tool call did not change', () => {
    const folder = project('other', {
      'tsconfig.json': TSCONFIG,
      'src/a.ts': BROKEN,
      'src/b.ts': CLEAN,
    })
    assert.equal(runHook(edit(folder, 'src/b.ts')).status, 0)
  })

  it('blocks on an error with no file that fails the whole run', () => {
    const config = JSON.stringify({
      compilerOptions: { types: ['no-such-types'] },
      include: ['src'],
    })
    const folder = project('global', { 'tsconfig.json': config, 'src/b.ts': CLEAN })
    const run = runHook(edit(folder, 'src/b.ts'))
    assert.equal(run.status, 2)
    assert.match(run.stderr, /error TS2688/)
  })

  it('tells the user when the program leaves the changed file out', () => {
    const folder = project('outside', {
      'tsconfig.json': TSCONFIG,
      'src/b.ts': CLEAN,
      'scripts/x.ts': BROKEN,
    })
    const run = runHook(edit(folder, 'scripts/x.ts'))
    assert.equal(run.status, 0)
    assert.match(JSON.parse(run.stdout).systemMessage, /not part of the program/)
  })

  it('checks a TypeScript file under no tsconfig.json with the compiler defaults', () => {
    const folder = project('loose', { 'a.ts': BROKEN })
    const run = runHook(edit(folder, 'a.ts'))
    assert.equal(run.status, 2)
    assert.match(run.stderr, /a\.ts\(1,14\): error TS2322/)
  })

  it('leaves a JavaScript file under no tsconfig.json alone', () => {
    const folder = project('loosejs', { 'a.js': 'const x = 1\n' })
    const run = runHook(edit(folder, 'a.js'))
    assert.equal(run.status, 0)
    assert.equal(run.stdout + run.stderr, '')
  })

  it('checks the files a Bash command changed, from bashEditDiff', () => {
    const folder = project('bash', { 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const run = runHook({
      tool_name: 'Bash',
      cwd: folder,
      tool_input: { command: 'sed -i s/1/2/ src/a.ts' },
      tool_response: { bashEditDiff: { changedFiles: [join(folder, 'src/a.ts')] } },
    })
    assert.equal(run.status, 2)
  })

  it('does nothing for a file that is not TypeScript or JavaScript', () => {
    const folder = project('docs', { 'README.md': '# x\n' })
    const run = runHook(edit(folder, 'README.md'))
    assert.equal(run.status, 0)
    assert.equal(run.stdout + run.stderr, '')
  })

  it('tells the user and does not block without a compiler', () => {
    const folder = project('nocompiler', { 'a.ts': BROKEN }, false)
    const emptyPath = join(ROOT, 'empty-bin')
    mkdirSync(emptyPath, { recursive: true })
    const run = runHook(edit(folder, 'a.ts'), emptyPath)
    assert.equal(run.status, 0)
    assert.match(JSON.parse(run.stdout).systemMessage, /no tsc was found/)
  })
})
