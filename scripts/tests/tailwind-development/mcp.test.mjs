#!/usr/bin/env node
// Tests for the tailwind-development MCP server's modules. The language-server client runs against
// a stub server; the real Tailwind CSS language server is exercised in the live checks.
//   node --test scripts/tests/tailwind-development/

import assert from 'node:assert/strict'
import { mkdirSync, mkdtempSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { afterEach, beforeEach, describe, test } from 'node:test'
import { fileURLToPath, pathToFileURL } from 'node:url'

import * as config from '../../../plugins/tailwind-development/mcp/config.mjs'
import * as format from '../../../plugins/tailwind-development/mcp/format.mjs'
import * as client from '../../../plugins/tailwind-development/mcp/lsp-client.mjs'
import * as paths from '../../../plugins/tailwind-development/mcp/paths.mjs'

const STUB = join(dirname(fileURLToPath(import.meta.url)), 'fixtures', 'stub-language-server.mjs')

describe('readOptions', () => {
  test('defaults every group on and the lists to their defaults when nothing is set', () => {
    const options = config.readOptions({})
    assert.equal(options.enabledGroups.size, config.FILE_TYPE_GROUPS.size)
    assert.deepEqual([...options.classFunctions], ['clsx', 'cn', 'cva', 'tw', 'twMerge'])
    assert.equal(options.configFile, null)
  })

  test('reads booleans as true/false and 1/0, in any case', () => {
    const options = config.readOptions({
      TAILWIND_CHECK_CSS: 'False',
      TAILWIND_CHECK_HTML: '0',
      TAILWIND_CHECK_VUE: 'TRUE',
    })
    assert.equal(options.enabledGroups.has('check_css'), false)
    assert.equal(options.enabledGroups.has('check_html'), false)
    assert.equal(options.enabledGroups.has('check_vue'), true)
  })

  test('fails loudly on a boolean it cannot read', () => {
    assert.throws(
      () => config.readOptions({ TAILWIND_CHECK_CSS: 'yes' }),
      /TAILWIND_CHECK_CSS must be true or false/u,
    )
  })

  test('reads lists as a JSON array or as comma- or newline-separated names', () => {
    assert.deepEqual(
      [...config.readOptions({ TAILWIND_CLASS_FUNCTIONS: '["cn", " tv "]' }).classFunctions],
      ['cn', 'tv'],
    )
    assert.deepEqual(
      [...config.readOptions({ TAILWIND_CLASS_FUNCTIONS: 'cn, tv\nclsx' }).classFunctions],
      ['cn', 'tv', 'clsx'],
    )
    assert.throws(
      () => config.readOptions({ TAILWIND_CLASS_FUNCTIONS: '[1, 2]' }),
      /list of strings/u,
    )
    assert.throws(
      () => config.readOptions({ TAILWIND_CLASS_FUNCTIONS: '[cn' }),
      /not a valid JSON array/u,
    )
  })

  test('maps each extension to its group and language id, and others to null', () => {
    assert.deepEqual(config.fileType('.tsx'), {
      group: 'check_js_ts',
      languageId: 'typescriptreact',
    })
    assert.deepEqual(config.fileType('.svelte'), { group: 'check_svelte', languageId: 'svelte' })
    assert.equal(config.fileType('.json'), null)
  })

  test('sends the options to the language server as its tailwindCSS settings', () => {
    const settings = config.tailwindSettings(
      config.readOptions({ TAILWIND_CONFIG_FILE: ' src/app.css ' }),
    )
    assert.equal(settings.experimental.configFile, 'src/app.css')
    assert.equal(settings.colorDecorators, true)
    assert.equal(settings.lint.cssConflict, 'warning')
  })
})

describe('paths', () => {
  /** @type {string} */
  let root
  beforeEach(() => {
    root = realpathSync(mkdtempSync(join(tmpdir(), 'tw-paths-')))
    mkdirSync(join(root, 'src'))
    writeFileSync(join(root, 'src', 'a.html'), '<div class="flex"></div>\n')
  })
  afterEach(() => rmSync(root, { recursive: true, force: true }))

  test('resolves a relative path inside the project', async () => {
    const file = await paths.resolveProjectFile(root, 'src/a.html')
    assert.equal(file.relativePath, join('src', 'a.html'))
    assert.equal(file.extension, '.html')
  })

  test('refuses a path that leaves the project, a missing file and a folder', async () => {
    await assert.rejects(paths.resolveProjectFile(root, '/etc/hosts'), paths.ToolInputError)
    await assert.rejects(paths.resolveProjectFile(root, '../../etc/hosts'), paths.ToolInputError)
    await assert.rejects(paths.resolveProjectFile(root, 'src/missing.html'), /does not exist/u)
    await assert.rejects(paths.resolveProjectFile(root, 'src'), /not a file/u)
  })

  test('refuses a symlink that points outside the project', async () => {
    symlinkSync('/etc/hosts', join(root, 'src', 'escape.html'))
    await assert.rejects(paths.resolveProjectFile(root, 'src/escape.html'), /outside the project/u)
  })

  test('refuses a file above the size limit', async () => {
    writeFileSync(join(root, 'src', 'big.css'), 'a'.repeat(paths.MAX_FILE_BYTES + 1))
    await assert.rejects(paths.resolveProjectFile(root, 'src/big.css'), /above the/u)
  })

  test('finds an installed tailwindcss only between the file and the project root', async () => {
    const file = join(root, 'src', 'a.html')
    assert.equal(await paths.hasTailwindInstall(root, file), false)
    mkdirSync(join(root, 'node_modules', 'tailwindcss'), { recursive: true })
    writeFileSync(join(root, 'node_modules', 'tailwindcss', 'package.json'), '{}')
    assert.equal(await paths.hasTailwindInstall(root, file), true)
  })
})

describe('format', () => {
  const finding = {
    line: 1,
    column: 13,
    severity: /** @type {const} */ ('warning'),
    rule: 'cssConflict',
    message: "'flex' applies the same CSS properties as 'block'.",
    fixes: [{ title: "Delete 'block'", line: 1, oldText: 'flex block', newText: 'flex' }],
  }

  test('lists each finding with its exact fix', () => {
    const text = format.findingsText('src/a.html', [finding])
    assert.match(text, /src\/a\.html:1:13 warning \[cssConflict\]/u)
    assert.match(text, /replace "flex block" with "flex"/u)
  })

  test('caps the list and counts the rest', () => {
    const text = format.findingsText(
      'a.html',
      Array.from({ length: format.MAX_DIAGNOSTICS + 3 }, () => finding),
    )
    assert.match(text, /and 3 more/u)
  })

  test('wraps the findings as PostToolUse additionalContext, and says nothing without findings', () => {
    const output = JSON.parse(format.findingsHookOutput('a.html', [finding]))
    assert.equal(output.hookSpecificOutput.hookEventName, 'PostToolUse')
    assert.match(output.hookSpecificOutput.additionalContext, /cssConflict/u)
    assert.equal(format.findingsHookOutput('a.html', []), '')
  })

  test('says a file is clean when its previous check had findings', () => {
    const output = JSON.parse(format.findingsHookOutput('a.html', [], true))
    assert.equal(
      output.hookSpecificOutput.additionalContext,
      'Tailwind CSS: no diagnostics left in a.html.',
    )
  })
})

describe('language-server client', () => {
  const timeouts = { project: 600, grace: 100, diagnostics: 600 }

  /** @param {string} mode */
  function start(mode) {
    process.env['STUB_MODE'] = mode
    return new client.TailwindLanguageServer({
      root: realpathSync(tmpdir()),
      settings: {},
      serverPath: STUB,
      serverArgs: [],
      log: () => undefined,
      timeouts,
    })
  }

  test('returns the diagnostics and quick fixes the server publishes', async () => {
    const server = start('project')
    try {
      const uri = pathToFileURL(join(realpathSync(tmpdir()), 'a.html')).href
      const diagnostics = await server.diagnostics(uri, 'html', '<div class="flex block"></div>')
      assert.ok(diagnostics)
      assert.equal(diagnostics[0]?.code, 'cssConflict')
      const [first] = diagnostics
      assert.ok(first)
      const [fix] = await server.quickFixes(uri, first)
      assert.equal(fix?.title, "Delete 'block'")
      const edit = fix?.edit?.changes?.[uri]?.[0]
      assert.ok(edit)
      assert.equal(client.textInRange('<div class="flex block"></div>', edit.range), 'flex block')
    } finally {
      await server.dispose()
    }
  })

  test('answers null when no project covers the document, and quickly once it has waited', async () => {
    const server = start('no-project')
    try {
      const uri = pathToFileURL(join(realpathSync(tmpdir()), 'b.html')).href
      assert.equal(await server.diagnostics(uri, 'html', '<div></div>'), null)
      const started = Date.now()
      assert.equal(await server.diagnostics(uri, 'html', '<div></div>'), null)
      assert.ok(
        Date.now() - started < timeouts.project,
        'the second answer waits the short grace only',
      )
    } finally {
      await server.dispose()
    }
  })

  test('closes a question-only document after asking', async () => {
    const server = start('project')
    try {
      const uri = pathToFileURL(join(realpathSync(tmpdir()), 'probe.html')).href
      const sorted = await server.withDocument(
        uri,
        'html',
        '<div class="p-4 flex"></div>',
        (connection) => client.TailwindLanguageServer.sortClasses(connection, uri, ['p-4 flex']),
      )
      assert.deepEqual(sorted, ['flex p-4'])
    } finally {
      await server.dispose()
    }
  })
})
