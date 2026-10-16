#!/usr/bin/env node
// Tests for the post-edit hook of the TypeScript LSP intelligence plugins, run against the
// real tsc on PATH. Without tsc the compiler cases are skipped.
//   node --test ".github/scripts/tests/*.test.mjs"

import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import {
  chmodSync,
  cpSync,
  mkdirSync,
  mkdtempSync,
  realpathSync,
  rmSync,
  writeFileSync,
} from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { afterEach, beforeEach, describe, test } from 'node:test'
import { fileURLToPath } from 'node:url'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..')
const PLUGIN = join(ROOT, 'plugins', 'typescript6-lsp-intelligence')
const HOOK = join(PLUGIN, 'hooks', 'tsc-check.sh')
const HAVE_TSC = spawnSync('sh', ['-c', 'command -v tsc']).status === 0
const STRICT = '{ "compilerOptions": { "strict": true } }'
const TYPE_ERROR = 'export const x: number = "s";\n'

/**
 * @param {unknown} payload
 * @param {Record<string, string>} env
 * @param {string} [hook]
 * @returns {{ code: number | null, out: string, err: string }}
 */
function fire(payload, env, hook = HOOK) {
  const base = Object.fromEntries(
    Object.entries(process.env).filter(([key]) => !key.startsWith('CLAUDE_')),
  )
  const run = spawnSync('bash', [hook], {
    env: { ...base, ...env },
    input: typeof payload === 'string' ? payload : JSON.stringify(payload),
    encoding: 'utf8',
  })
  return { code: run.status, out: run.stdout, err: run.stderr }
}

/**
 * @param {string} tool
 * @param {Record<string, unknown>} fields
 * @returns {Record<string, unknown>}
 */
function event(tool, fields) {
  return { hook_event_name: 'PostToolUse', session_id: 'test', tool_name: tool, ...fields }
}

/**
 * @typedef {object} HookOutput
 * @property {string} [decision]
 * @property {string} reason
 * @property {string} systemMessage
 * @property {{ hookEventName: string, additionalContext: string }} hookSpecificOutput
 */

/**
 * @param {string} out
 * @returns {HookOutput}
 */
function parsed(out) {
  return JSON.parse(out)
}

function makeWorkspace() {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'tschook-')))
  const home = join(root, 'home')
  mkdirSync(home)
  const env = { HOME: home, CLAUDE_PLUGIN_DATA: join(root, 'data') }
  /**
   * @param {string} name
   * @param {string} text
   */
  const write = (name, text) => {
    const path = join(root, name)
    mkdirSync(dirname(path), { recursive: true })
    writeFileSync(path, text)
    return path
  }
  /** @param {string} path */
  const edit = (path) => event('Write', { tool_input: { file_path: path, content: 'x' } })
  const cleanup = () => rmSync(root, { recursive: true, force: true })
  return { root, env, write, edit, cleanup }
}

/** @typedef {ReturnType<typeof makeWorkspace>} Workspace */

describe('typescript lsp hook', () => {
  /** @type {Workspace} */
  let ws
  beforeEach(() => {
    ws = makeWorkspace()
  })
  afterEach(() => ws.cleanup())

  test('an event without tool_name fails instead of passing in silence', () => {
    const r = fire('{"tool_input":', ws.env)
    assert.equal(r.code, 1)
    assert.match(r.err, /no tool_name/)
  })

  test('an edited file that is missing is reported as not checked', () => {
    const r = fire(ws.edit(join(ws.root, 'gone.ts')), ws.env)
    assert.equal(r.code, 0)
    assert.match(
      parsed(r.out).hookSpecificOutput.additionalContext,
      /gone\.ts \(not found on disk\)/,
    )
  })

  test('a compiler that crashes is never a pass', () => {
    ws.write('crash/tsconfig.json', STRICT)
    const file = ws.write('crash/a.ts', 'export const x = 1;\n')
    const stub = ws.write(
      'crash/node_modules/.bin/tsc',
      '#!/bin/sh\ncase "$*" in *--version*) echo "Version 6.0.3" ;; *) echo boom >&2; exit 139 ;; esac\n',
    )
    chmodSync(stub, 0o755)
    const r = fire(ws.edit(file), ws.env)
    assert.equal(r.code, 0)
    const reason = parsed(r.out).reason
    assert.match(reason, /exited with status 139 without reporting a TypeScript error/)
    assert.match(reason, /boom/)
  })

  test('CRLF compiler output still gives valid JSON', () => {
    ws.write('crlf/tsconfig.json', STRICT)
    const file = ws.write('crlf/a.ts', 'export const x = 1;\n')
    const stub = ws.write(
      'crlf/node_modules/.bin/tsc',
      [
        '#!/bin/sh',
        'case "$*" in',
        '  *--version*) echo "Version 6.0.3" ;;',
        `  *--listFilesOnly*) echo "${file}" ;;`,
        "  *) printf 'a.ts(1,14): error TS2322: bad\\r\\n  detail\\r\\n'; exit 2 ;;",
        'esac',
        '',
      ].join('\n'),
    )
    chmodSync(stub, 0o755)
    const r = fire(ws.edit(file), ws.env)
    assert.equal(r.code, 0)
    const reason = parsed(r.out).reason
    assert.match(reason, /error TS2322: bad\n {2}detail/)
    assert.doesNotMatch(reason, /\r/)
  })

  test('a policy that lost noCheck stops the hook', () => {
    const plugin = join(ws.root, 'plugin')
    cpSync(PLUGIN, plugin, { recursive: true })
    writeFileSync(
      join(plugin, '.claude-plugin', 'plugin.json'),
      '{"name":"typescript6-lsp-intelligence"}',
    )
    writeFileSync(
      join(plugin, 'hooks', 'tsconfig.strictest.json'),
      '{"compilerOptions":{"strict":true,"noEmit":true}}',
    )
    const file = ws.write('p/a.ts', 'export const x = 1;\n')
    const r = fire(ws.edit(file), ws.env, join(plugin, 'hooks', 'tsc-check.sh'))
    assert.equal(r.code, 1)
    assert.match(r.err, /does not set noEmit true and noCheck false/)
  })

  describe('with tsc', { skip: !HAVE_TSC }, () => {
    test('a type error blocks with its code', () => {
      ws.write('app/tsconfig.json', STRICT)
      const r = fire(ws.edit(ws.write('app/a.ts', TYPE_ERROR)), ws.env)
      assert.match(parsed(r.out).reason, /a\.ts\(1,14\): error TS2322/)
    })

    test('a project noCheck does not switch the check off', () => {
      ws.write('nc/tsconfig.json', '{ "compilerOptions": { "strict": true, "noCheck": true } }')
      const r = fire(ws.edit(ws.write('nc/a.ts', TYPE_ERROR)), ws.env)
      assert.match(parsed(r.out).reason, /TS2322/)
    })

    test('a minified policy gives the same strict flags', () => {
      const plugin = join(ws.root, 'plugin')
      cpSync(PLUGIN, plugin, { recursive: true })
      const policy = join(plugin, 'hooks', 'tsconfig.strictest.json')
      const minified = JSON.stringify(
        JSON.parse(spawnSync('cat', [policy], { encoding: 'utf8' }).stdout),
      )
      writeFileSync(policy, minified)
      ws.write('m/tsconfig.json', '{ "compilerOptions": { "strict": false } }')
      const file = ws.write('m/a.ts', 'export function f(a) { return a }\n')
      const r = fire(ws.edit(file), ws.env, join(plugin, 'hooks', 'tsc-check.sh'))
      assert.match(parsed(r.out).reason, /TS7006/)
    })

    test('a JSON-escaped path is decoded', () => {
      ws.write('uni/tsconfig.json', STRICT)
      ws.write('uni/niño.ts', TYPE_ERROR)
      const payload = JSON.stringify(ws.edit(join(ws.root, 'uni', 'niño.ts'))).replace(
        'ñ',
        '\\u00f1',
      )
      const r = fire(payload, ws.env)
      assert.match(parsed(r.out).reason, /niño\.ts\(1,14\): error TS2322/)
    })

    test('the path comes from tool_input, not from tool_response', () => {
      ws.write('in/tsconfig.json', STRICT)
      const file = ws.write('in/a.ts', TYPE_ERROR)
      const payload = { ...ws.edit(file), tool_response: { file_path: join(ws.root, 'other.ts') } }
      const r = fire(payload, ws.env)
      assert.match(parsed(r.out).reason, /TS2322/)
    })

    test('a file outside a composite program is checked without a rootDir error', () => {
      ws.write(
        'comp/tsconfig.json',
        '{ "compilerOptions": { "composite": true, "strict": true, "outDir": "dist" }, "include": ["src"] }',
      )
      ws.write('comp/src/lib.ts', 'export const v = 1;\n')
      const file = ws.write(
        'comp/scripts/run.ts',
        'import { v } from "../src/lib";\nexport const w: string = v;\n',
      )
      const reason = parsed(fire(ws.edit(file), ws.env).out).reason
      assert.match(reason, /TS2322/)
      assert.doesNotMatch(reason, /TS6059|TS6307/)
    })

    test('strictest-only errors in other files are disclosed, not hidden behind a pass', () => {
      ws.write(
        'dep/tsconfig.json',
        '{ "compilerOptions": { "strict": false }, "include": ["*.ts"] }',
      )
      ws.write('dep/b.ts', 'import { f } from "./a";\nexport function g(x) { return f(x) }\n')
      const file = ws.write(
        'dep/a.ts',
        'export function f(a?: string): string { return a ?? "" }\n',
      )
      const message = parsed(fire(ws.edit(file), ws.env).out).systemMessage
      assert.match(message, /tsc \d+\.\d+\.\d+ · the edited files pass the strictest policy/)
      assert.match(message, /not counted, since the project's own config accepts them: 1/)
    })

    test('a Bash failure reports through additionalContext', () => {
      ws.write('f/tsconfig.json', STRICT)
      const file = ws.write('f/a.ts', TYPE_ERROR)
      const payload = event('Bash', {
        hook_event_name: 'PostToolUseFailure',
        tool_input: { command: 'x' },
        tool_response: { bashEditDiff: { changedFiles: [file] } },
      })
      const out = parsed(fire(payload, ws.env).out)
      assert.equal(out.decision, undefined)
      assert.equal(out.hookSpecificOutput.hookEventName, 'PostToolUseFailure')
      assert.match(out.hookSpecificOutput.additionalContext, /TS2322/)
    })

    test('a file the command staged is found without a diff', () => {
      const repo = join(ws.root, 'repo')
      mkdirSync(repo)
      const git = (/** @type {string[]} */ ...args) =>
        spawnSync(
          'git',
          [
            '-C',
            repo,
            '-c',
            'commit.gpgsign=false',
            '-c',
            'user.name=t',
            '-c',
            'user.email=t@t',
            ...args,
          ],
          {
            encoding: 'utf8',
          },
        )
      git('init', '-q')
      ws.write('repo/tsconfig.json', STRICT)
      git('add', '.')
      git('commit', '-qm', 'init')
      ws.write('repo/n.ts', TYPE_ERROR)
      git('add', 'n.ts')
      const payload = event('PowerShell', {
        cwd: repo,
        tool_input: { command: 'x' },
        duration_ms: 1000,
      })
      const r = fire(payload, ws.env)
      assert.match(parsed(r.out).reason, /n\.ts\(1,14\): error TS2322/)
    })

    test('a non-ASCII file name from git is found, not skipped as a quoted path', () => {
      const repo = join(ws.root, 'repo-utf8')
      mkdirSync(repo)
      const git = (/** @type {string[]} */ ...args) =>
        spawnSync(
          'git',
          [
            '-C',
            repo,
            '-c',
            'commit.gpgsign=false',
            '-c',
            'user.name=t',
            '-c',
            'user.email=t@t',
            ...args,
          ],
          { encoding: 'utf8' },
        )
      git('init', '-q')
      ws.write('repo-utf8/tsconfig.json', STRICT)
      git('add', '.')
      git('commit', '-qm', 'init')
      ws.write('repo-utf8/café.ts', TYPE_ERROR)
      const payload = event('Bash', { cwd: repo, tool_input: { command: 'x' }, duration_ms: 1000 })
      const r = fire(payload, ws.env)
      assert.match(parsed(r.out).reason, /café\.ts\(1,14\): error TS2322/)
    })
  })
})
