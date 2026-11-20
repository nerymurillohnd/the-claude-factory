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
 * A folder with files, and a node_modules/typescript link when withCompiler is true.
 * @param {string} name
 * @param {Record<string, string>} files
 * @param {boolean} withCompiler
 * @returns {string}
 */
function project(name, files, withCompiler = true) {
  const folder = join(ROOT, name)
  mkdirSync(folder, { recursive: true })
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
 * Runs the hook with event on stdin and the given PATH.
 * @param {Record<string, unknown>} event
 * @param {string} [path]
 */
function runHook(event, path = process.env['PATH'] ?? '') {
  const run = spawnSync(process.execPath, [HOOK], {
    input: JSON.stringify({ hook_event_name: 'PostToolUse', ...event }),
    encoding: 'utf8',
    env: { ...process.env, PATH: path },
  })
  return { code: run.status, stdout: run.stdout, stderr: run.stderr }
}

const TSCONFIG = JSON.stringify({
  compilerOptions: { strict: true, noEmit: true },
  include: ['src'],
})
const BROKEN = 'export const x: number = "a"\n'
const CLEAN = 'export const y: number = 1\n'

describe('tsc-check.mjs', {
  skip: TYPESCRIPT === null ? 'no typescript package resolves' : false,
}, () => {
  it('blocks an edit that leaves a type error in the edited file', () => {
    const folder = project('broken', { 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const result = runHook({
      tool_name: 'Edit',
      cwd: folder,
      tool_input: { file_path: join(folder, 'src/a.ts') },
    })
    assert.equal(result.code, 2)
    assert.match(result.stderr, /src[\\/]a\.ts\(1,14\): error TS2322/)
    assert.match(result.stderr, /ts-6-writing-and-navigation/)
  })

  it('lets a clean edit through in silence', () => {
    const folder = project('clean', { 'tsconfig.json': TSCONFIG, 'src/b.ts': CLEAN })
    const result = runHook({
      tool_name: 'Write',
      cwd: folder,
      tool_input: { file_path: join(folder, 'src/b.ts') },
    })
    assert.equal(result.code, 0)
    assert.equal(result.stdout + result.stderr, '')
  })

  it('ignores errors in files the tool call did not change', () => {
    const folder = project('other', {
      'tsconfig.json': TSCONFIG,
      'src/a.ts': BROKEN,
      'src/b.ts': CLEAN,
    })
    const result = runHook({
      tool_name: 'Edit',
      cwd: folder,
      tool_input: { file_path: join(folder, 'src/b.ts') },
    })
    assert.equal(result.code, 0)
  })

  it('checks a file under no tsconfig.json with the compiler defaults', () => {
    const folder = project('loose', { 'a.ts': BROKEN })
    const result = runHook({
      tool_name: 'Write',
      cwd: folder,
      tool_input: { file_path: join(folder, 'a.ts') },
    })
    assert.equal(result.code, 2)
    assert.match(result.stderr, /a\.ts\(1,14\): error TS2322/)
  })

  it('checks the files a Bash command changed, from bashEditDiff', () => {
    const folder = project('bash', { 'tsconfig.json': TSCONFIG, 'src/a.ts': BROKEN })
    const result = runHook({
      tool_name: 'Bash',
      cwd: folder,
      tool_input: { command: 'sed -i s/1/2/ src/a.ts' },
      tool_response: { bashEditDiff: { changedFiles: [join(folder, 'src/a.ts')] } },
    })
    assert.equal(result.code, 2)
  })

  it('does nothing for a file that is not TypeScript or JavaScript', () => {
    const folder = project('docs', { 'README.md': '# x\n' })
    const result = runHook({
      tool_name: 'Edit',
      cwd: folder,
      tool_input: { file_path: join(folder, 'README.md') },
    })
    assert.equal(result.code, 0)
    assert.equal(result.stdout + result.stderr, '')
  })

  it('tells the user and does not block without a compiler', () => {
    const folder = project('nocompiler', { 'a.ts': BROKEN }, false)
    const emptyPath = join(ROOT, 'empty-bin')
    mkdirSync(emptyPath, { recursive: true })
    const result = runHook(
      { tool_name: 'Edit', cwd: folder, tool_input: { file_path: join(folder, 'a.ts') } },
      emptyPath,
    )
    assert.equal(result.code, 0)
    assert.match(JSON.parse(result.stdout).systemMessage, /no tsc was found/)
  })
})
