#!/usr/bin/env node
// Tests for the Node post-edit hooks of bash-, typescript6- and typescript7-lsp-intelligence.
//   node --test ".github/scripts/tests/*.test.mjs"
// Tool cases run only when the tool is on PATH; the TypeScript cases need `npm ci` in each
// TypeScript plugin folder (CI does it; locally run it once).

import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  utimesSync,
  writeFileSync,
} from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { afterEach, beforeEach, describe, test } from 'node:test'
import { fileURLToPath } from 'node:url'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..')
const PLUGINS = join(ROOT, 'plugins')
const BASH_HOOK = join(PLUGINS, 'bash-lsp-intelligence', 'hooks', 'check.mjs')
const SECONDS_AGO = 600
const MS_PER_S = 1000
const REPORT_CEILING = 9100
const MANY = 23
const UNCHECKED = 3

function onPath(tool) {
  return spawnSync('sh', ['-c', `command -v ${tool}`]).status === 0
}
const HAVE_SHELL_TOOLS = onPath('shfmt') && onPath('shellcheck')

function fire(hook, payload, { cwd, env = {} }) {
  const base = Object.fromEntries(
    Object.entries(process.env).filter(([key]) => !key.startsWith('CLAUDE_')),
  )
  const run = spawnSync(process.execPath, [hook], {
    cwd,
    env: { ...base, CLAUDE_PLUGIN_ROOT: dirname(dirname(hook)), ...env },
    input: typeof payload === 'string' ? payload : JSON.stringify(payload),
    encoding: 'utf8',
  })
  return { code: run.status, out: run.stdout, err: run.stderr }
}

function event(tool, path, extra = {}) {
  const data = { hook_event_name: 'PostToolUse', tool_name: tool, ...extra }
  if (path) {
    data.tool_input = { file_path: path }
  }
  return data
}

function bashEvent(files, extra = {}) {
  return event('Bash', null, {
    tool_input: { command: 'x' },
    tool_response: { bashEditDiff: { changedFiles: files } },
    ...extra,
  })
}

function makeWorkspace() {
  const root = mkdtempSync(join(tmpdir(), 'lsphook-'))
  const home = join(root, 'home')
  const project = join(root, 'project')
  mkdirSync(home)
  mkdirSync(project)
  const env = { HOME: home, XDG_CONFIG_HOME: join(home, '.config'), SHELLCHECK_OPTS: '' }
  const write = (name, text) => {
    const path = join(project, name)
    mkdirSync(dirname(path), { recursive: true })
    writeFileSync(path, text)
    return path
  }
  const age = (path) => {
    const then = Date.now() / MS_PER_S - SECONDS_AGO
    utimesSync(path, then, then)
  }
  const cleanup = () => rmSync(root, { recursive: true, force: true })
  return { root, home, project, env, write, age, cleanup }
}

describe('bash-lsp-intelligence hook', () => {
  let ws
  beforeEach(() => {
    ws = makeWorkspace()
  })
  afterEach(() => ws.cleanup())

  test('ignores non-shell files and bad input', () => {
    const md = ws.write('notes.md', '# hi\n')
    const silent = { code: 0, out: '', err: '' }
    assert.deepEqual(fire(BASH_HOOK, event('Edit', md), { cwd: ws.project, env: ws.env }), silent)
    assert.deepEqual(fire(BASH_HOOK, 'not json', { cwd: ws.project, env: ws.env }), silent)
  })

  test('zsh is reported as not checked, without blocking', () => {
    const zsh = ws.write('z.sh', '#!/usr/bin/env zsh\necho hi\n')
    const r = fire(BASH_HOOK, event('Edit', zsh), { cwd: ws.project, env: ws.env })
    assert.equal(r.code, 0)
    assert.match(JSON.parse(r.out).hookSpecificOutput.additionalContext, /zsh/)
  })

  test('missing shfmt is reported with its install command', () => {
    const sh = ws.write('a.sh', '#!/usr/bin/env bash\necho hi\n')
    const empty = join(ws.root, 'bin')
    mkdirSync(empty)
    const r = fire(BASH_HOOK, event('Edit', sh), {
      cwd: ws.project,
      env: { ...ws.env, PATH: empty },
    })
    assert.equal(r.code, 2)
    assert.match(r.err, /shfmt is not installed/)
    assert.match(r.err, /brew install shfmt/)
  })

  describe('with shfmt and shellcheck', { skip: !HAVE_SHELL_TOOLS }, () => {
    test('clean file confirms', () => {
      const sh = ws.write(
        'clean.sh',
        "#!/usr/bin/env bash\nset -euo pipefail\nprintf '%s\\n' hello\n",
      )
      const r = fire(BASH_HOOK, event('Edit', sh), { cwd: ws.project, env: ws.env })
      assert.equal(r.err, '')
      assert.equal(r.code, 0)
      assert.match(
        JSON.parse(r.out).systemMessage,
        /bash-lsp-intelligence: shfmt, shellcheck passed · clean\.sh/,
      )
    })

    test('default style is two spaces when no editorconfig exists', () => {
      const sh = ws.write('fmt.sh', '#!/usr/bin/env bash\nif true; then\n\techo a\nfi\n')
      const r = fire(BASH_HOOK, event('Write', sh), { cwd: ws.project, env: ws.env })
      assert.equal(r.code, 0)
      assert.match(JSON.parse(r.out).hookSpecificOutput.additionalContext, /re-read/)
      assert.equal(readFileSync(sh, 'utf8'), '#!/usr/bin/env bash\nif true; then\n  echo a\nfi\n')
    })

    test('editorconfig in a parent directory wins', () => {
      ws.write('.editorconfig', 'root = true\n[[shell]]\nindent_style = tab\n')
      const sh = ws.write('sub/tabs.sh', '#!/usr/bin/env bash\nif true; then\n\techo a\nfi\n')
      const r = fire(BASH_HOOK, event('Edit', sh), { cwd: ws.root, env: ws.env })
      assert.equal(r.code, 0)
      assert.equal(readFileSync(sh, 'utf8'), '#!/usr/bin/env bash\nif true; then\n\techo a\nfi\n')
    })

    test('findings block with exit 2 and the SC code', () => {
      const sh = ws.write('bad.sh', '#!/usr/bin/env bash\nx="a b"\necho $x\n')
      const r = fire(BASH_HOOK, event('Edit', sh), { cwd: ws.project, env: ws.env })
      assert.equal(r.code, 2)
      assert.match(r.err, /SC2086/)
      assert.match(r.err, /SC2250/)
      assert.match(r.err, /Fix these findings in bad\.sh/)
    })

    test('a user shellcheckrc replaces the defaults', () => {
      ws.write('.shellcheckrc', 'disable=SC2086,SC2250\n')
      const sh = ws.write('ok.sh', '#!/usr/bin/env bash\nx="a b"\necho $x\n')
      const r = fire(BASH_HOOK, event('Edit', sh), { cwd: ws.project, env: ws.env })
      assert.equal(r.err, '')
      assert.equal(r.code, 0)
    })

    test('extensionless bash script by shebang, Bash tool with edit diff', () => {
      const tool = ws.write('bin/tool', '#!/bin/bash\nx="a b"\necho $x\n')
      const r = fire(BASH_HOOK, bashEvent([tool]), { cwd: ws.project, env: ws.env })
      assert.equal(r.code, 2)
      assert.match(r.err, /SC2086/)
    })

    test('Bash tool without diff finds files newer than the window', () => {
      ws.age(ws.write('old.sh', '#!/usr/bin/env bash\nx="a b"\necho $x\n'))
      ws.write('new.sh', '#!/usr/bin/env bash\nx="a b"\necho $x\n')
      const payload = event('Bash', null, { tool_input: { command: 'x' }, duration_ms: 20 })
      const env = { ...ws.env, CLAUDE_PROJECT_DIR: ws.project }
      const r = fire(BASH_HOOK, payload, { cwd: ws.home, env })
      assert.equal(r.code, 2)
      assert.match(r.err, /new\.sh/)
      assert.doesNotMatch(r.err, /old\.sh/)
    })

    test('more than twenty files reports the rest', () => {
      const files = Array.from({ length: MANY }, (_, i) =>
        ws.write(`many/f${i}.sh`, '#!/usr/bin/env bash\nprintf hi\n'),
      )
      const r = fire(BASH_HOOK, bashEvent(files), { cwd: ws.project, env: ws.env })
      assert.equal(r.code, 2)
      assert.match(r.err, /not checked/)
      const unchecked = r.err.split('\n').filter((line) => line.startsWith('  many/f'))
      assert.equal(unchecked.length, UNCHECKED)
    })

    test('oversized report is cut', () => {
      const lines = Array.from({ length: 600 }, (_, i) => `v${i}="a b"\necho $v${i}`).join('\n')
      const sh = ws.write('huge.sh', `#!/usr/bin/env bash\n${lines}\n`)
      const r = fire(BASH_HOOK, event('Edit', sh), { cwd: ws.project, env: ws.env })
      assert.equal(r.code, 2)
      assert.ok(r.err.length <= REPORT_CEILING)
      assert.match(r.err, /more lines/)
    })
  })
})

const TS7 = join(PLUGINS, 'typescript7-lsp-intelligence')
const TS6 = join(PLUGINS, 'typescript6-lsp-intelligence')
const STRICT_TSCONFIG =
  '{ "compilerOptions": { "strict": true, "noEmit": true, "target": "es2022", "module": "esnext", "moduleResolution": "bundler", "types": [] }, "include": ["**/*.ts"] }\n'
const LOOSE_TSCONFIG =
  '{ "compilerOptions": { "strict": false, "noEmit": true, "types": [] }, "include": ["**/*.ts"] }\n'

function tsSuite(name, plugin) {
  const hook = join(plugin, 'hooks', 'check.mjs')
  const ready = existsSync(join(plugin, 'node_modules', 'typescript', 'bin', 'tsc'))
  describe(`${name} hook`, { skip: !ready }, () => {
    let ws
    beforeEach(() => {
      ws = makeWorkspace()
    })
    afterEach(() => ws.cleanup())

    test('ignores non-TypeScript files', () => {
      const md = ws.write('notes.md', '# hi\n')
      const r = fire(hook, event('Edit', md), { cwd: ws.project, env: ws.env })
      assert.deepEqual(r, { code: 0, out: '', err: '' })
    })

    test('clean file in a program confirms', () => {
      ws.write('tsconfig.json', STRICT_TSCONFIG)
      const ts = ws.write('src/a.ts', 'export const n: number = 1\n')
      const r = fire(hook, event('Edit', ts), { cwd: ws.project, env: ws.env })
      assert.equal(r.err, '')
      assert.equal(r.code, 0)
      assert.match(JSON.parse(r.out).systemMessage, new RegExp(`${name}: tsc passed · src/a\\.ts`))
    })

    test('type error blocks with the TS code', () => {
      ws.write('tsconfig.json', STRICT_TSCONFIG)
      const ts = ws.write('src/bad.ts', 'export const n: number = "x"\n')
      const r = fire(hook, event('Edit', ts), { cwd: ws.project, env: ws.env })
      assert.equal(r.code, 2)
      assert.match(r.err, /TS2322/)
      assert.match(r.err, /Fix these findings in src\/bad\.ts/)
    })

    test('nearest tsconfig wins and sibling errors come after', () => {
      ws.write('tsconfig.json', LOOSE_TSCONFIG)
      ws.write('packages/app/tsconfig.json', STRICT_TSCONFIG)
      ws.write('packages/app/sibling.ts', 'export const s: number = "y"\n')
      const ts = ws.write('packages/app/edited.ts', 'export const e: number = "x"\n')
      const r = fire(hook, event('Edit', ts), { cwd: ws.project, env: ws.env })
      assert.equal(r.code, 2)
      assert.ok(r.err.indexOf('edited.ts') < r.err.indexOf('sibling.ts'))
      assert.match(r.err, /packages\/app\/tsconfig\.json/)
    })

    test('file outside every program is reported, not passed over', () => {
      ws.write(
        'tsconfig.json',
        '{ "compilerOptions": { "noEmit": true, "types": [] }, "include": ["src/**/*.ts"] }\n',
      )
      ws.write('src/ok.ts', 'export const ok = 1\n') // the program needs one input, or tsc reports TS18003
      const ts = ws.write('scripts/loose.ts', 'export const n: number = 1\n')
      const r = fire(hook, event('Edit', ts), { cwd: ws.project, env: ws.env })
      assert.equal(r.code, 0)
      assert.match(JSON.parse(r.out).hookSpecificOutput.additionalContext, /not part of/)
    })

    test('no tsconfig: compiler defaults on the file alone', () => {
      const ts = ws.write('alone.ts', 'export const n: number = "x"\n')
      const r = fire(hook, event('Edit', ts), { cwd: ws.project, env: ws.env })
      assert.equal(r.code, 2)
      assert.match(r.err, /TS2322/)
    })

    test('two files in one program run tsc once', () => {
      ws.write('tsconfig.json', STRICT_TSCONFIG)
      const a = ws.write('src/a.ts', 'export const a = 1\n')
      const b = ws.write('src/b.ts', 'export const b = 2\n')
      const r = fire(hook, bashEvent([a, b]), { cwd: ws.project, env: ws.env })
      assert.equal(r.code, 0)
      assert.match(JSON.parse(r.out).systemMessage, /src\/a\.ts, src\/b\.ts/)
    })

    test('a config error is a finding', () => {
      ws.write(
        'tsconfig.json',
        '{ "compilerOptions": { "noEmit": true, "types": [] }, "include": ["nothing/**/*.ts"] }\n',
      )
      const ts = ws.write('src/a.ts', 'export const a = 1\n')
      const r = fire(hook, event('Edit', ts), { cwd: ws.project, env: ws.env })
      assert.equal(r.code, 2)
      assert.match(r.err, /TS18003/)
    })
  })
}

tsSuite('typescript7-lsp-intelligence', TS7)
tsSuite('typescript6-lsp-intelligence', TS6)
