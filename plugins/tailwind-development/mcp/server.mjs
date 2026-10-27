#!/usr/bin/env node
// The tailwind-development MCP server: the Tailwind CSS language server's diagnostics, quick fixes,
// hovers, colors, completions and class order as four read-only tools. Claude Code starts it over
// stdio with the session; the PostToolUse hook calls check_file after every Edit or Write.

import { readFileSync } from 'node:fs'
import { readFile } from 'node:fs/promises'
import { dirname, join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { McpServer } from '@modelcontextprotocol/server'
import { serveStdio } from '@modelcontextprotocol/server/stdio'
import { z } from 'zod'
import { fileType, readOptions, tailwindSettings } from './config.mjs'
import { findingsHookOutput, findingsText, severityName } from './format.mjs'
import { TailwindLanguageServer, textInRange } from './lsp-client.mjs'
import { hasTailwindInstall, projectRoot, resolveProjectFile, ToolInputError } from './paths.mjs'

/** @typedef {import('./format.mjs').Finding} Finding */
/** @typedef {{ content: { type: 'text', text: string }[], isError?: boolean }} ToolResult */

const PLUGIN_VERSION = /** @type {{ version: string }} */ (
  JSON.parse(readFileSync(new URL('../.claude-plugin/plugin.json', import.meta.url), 'utf8'))
).version

const READ_ONLY = {
  readOnlyHint: true,
  destructiveHint: false,
  idempotentHint: true,
  openWorldHint: false,
}

/** Characters a class list may hold: it is placed inside a class="…" attribute. */
const CLASS_LIST = /^[^"'<>`\r\n]+$/u

const options = readOptions(process.env)

/** @type {Promise<{ root: string, server: TailwindLanguageServer }> | undefined} */
let shared

/** Whether the hook has already told Claude that no project covers an edited file. */
let noProjectHintGiven = false

/** Files whose last check reported findings, so the next clean check can say so. */
const filesWithFindings = new Set()

/** Numbers the question-only documents, so calls Claude Code runs in parallel never share one. */
let probeCount = 0

/** The project root and the language-server client, shared by every MCP server instance. */
function state() {
  shared ??= projectRoot(process.env).then((root) => ({
    root,
    server: new TailwindLanguageServer({ root, settings: tailwindSettings(options) }),
  }))
  return shared
}

/** @param {string} text @returns {ToolResult} */
const text = (text) => ({ content: [{ type: 'text', text }] })

/** @param {string} message @returns {ToolResult} */
const failure = (message) => ({ content: [{ type: 'text', text: message }], isError: true })

/**
 * Why the server found no project, with the projects it did find.
 * @param {TailwindLanguageServer} server
 * @param {string} target
 */
function noProjectText(server, target) {
  const found = server.projects
    .map(
      (p) =>
        `${p.config ?? p.uri}${p.tailwind?.version ? ` (Tailwind CSS ${p.tailwind.version})` : ''}`,
    )
    .join(', ')
  return [
    `No Tailwind CSS project covers ${target}.`,
    'The language server needs tailwindcss installed in the project (npm, pnpm or yarn) and, for v4, a .css entry point with @import "tailwindcss"; Less, Sass and Stylus files cannot be one.',
    'In a monorepo or a project with several entry points, set the plugin option config_file (/config).',
    found === ''
      ? 'The server found no Tailwind CSS project in this workspace.'
      : `Projects found: ${found}.`,
  ].join(' ')
}

/**
 * Reports a refusal as a tool error and rethrows anything else.
 * @param {unknown} error
 * @returns {ToolResult}
 */
function refusal(error) {
  if (error instanceof ToolInputError) {
    return failure(error.message)
  }
  throw error
}

/**
 * @param {{ filePath: string, format: 'text' | 'hook' }} args
 * @returns {Promise<ToolResult>}
 */
async function checkFile({ filePath, format }) {
  const hook = format === 'hook'
  const { root, server } = await state()
  /** @type {Awaited<ReturnType<typeof resolveProjectFile>>} */
  let file
  try {
    file = await resolveProjectFile(root, filePath)
  } catch (error) {
    // The hook runs after every edit, including files outside the project: it stays silent there.
    return hook && error instanceof ToolInputError ? text('') : refusal(error)
  }
  const type = fileType(file.extension)
  if (type === null) {
    return hook
      ? text('')
      : failure(
          `${file.relativePath}: the Tailwind CSS language server does not read ${file.extension} files.`,
        )
  }
  if (hook && !options.enabledGroups.has(type.group)) {
    return text('')
  }
  if (!(await hasTailwindInstall(root, file.path))) {
    return text(hook ? '' : noProjectText(server, file.relativePath))
  }
  const content = await readFile(file.path, 'utf8')
  const uri = pathToFileURL(file.path).href
  const diagnostics = await server.diagnostics(uri, type.languageId, content)
  if (diagnostics === null) {
    if (!hook) {
      return text(noProjectText(server, file.relativePath))
    }
    // Tailwind CSS is installed, yet no project covers the file: often a CSS module or <style> block
    // with @reference that the server took as the entry point. Say so once, then stay silent.
    if (noProjectHintGiven) {
      return text('')
    }
    noProjectHintGiven = true
    return text(
      JSON.stringify({
        hookSpecificOutput: {
          hookEventName: 'PostToolUse',
          additionalContext: `Tailwind CSS diagnostics are off for ${file.relativePath}: ${noProjectText(server, file.relativePath)} This note is shown once per session.`,
        },
      }),
    )
  }
  /** @type {Finding[]} */
  const findings = []
  for (const diagnostic of diagnostics) {
    const actions = await server.quickFixes(uri, diagnostic)
    findings.push({
      line: diagnostic.range.start.line + 1,
      column: diagnostic.range.start.character + 1,
      severity: severityName(diagnostic.severity),
      rule: String(diagnostic.code ?? 'tailwindcss'),
      message: diagnostic.message,
      fixes: actions.flatMap((action) =>
        (action.edit?.changes?.[uri] ?? []).map((edit) => ({
          title: action.title,
          line: edit.range.start.line + 1,
          oldText: textInRange(content, edit.range),
          newText: edit.newText,
        })),
      ),
    })
  }
  const hadFindings = filesWithFindings.has(file.path)
  if (findings.length > 0) {
    filesWithFindings.add(file.path)
  } else {
    filesWithFindings.delete(file.path)
  }
  return text(
    hook
      ? findingsHookOutput(file.relativePath, findings, hadFindings)
      : findingsText(file.relativePath, findings),
  )
}

/**
 * A document URI next to the given file, or at the project root, that exists only for one question
 * and is never written to disk.
 * @param {string} root
 * @param {string | undefined} filePath
 */
async function probeUri(root, filePath) {
  const dir =
    filePath === undefined ? root : dirname((await resolveProjectFile(root, filePath)).path)
  probeCount += 1
  return pathToFileURL(join(dir, `.tailwind-development-probe-${process.pid}-${probeCount}.html`))
    .href
}

const PROBE_PREFIX = '<div class="'

/**
 * An LSP color as #rrggbb, or #rrggbbaa when it is not opaque.
 * @param {{ red: number, green: number, blue: number, alpha: number }} color
 */
function hexColor({ red, green, blue, alpha }) {
  const channels = alpha < 1 ? [red, green, blue, alpha] : [red, green, blue]
  return `#${channels
    .map((v) =>
      Math.round(v * 255)
        .toString(16)
        .padStart(2, '0'),
    )
    .join('')}`
}

/**
 * @param {{ classes: string, filePath?: string | undefined }} args
 * @returns {Promise<ToolResult>}
 */
async function classCss({ classes, filePath }) {
  const { root, server } = await state()
  let uri
  try {
    uri = await probeUri(root, filePath)
  } catch (error) {
    return refusal(error)
  }
  const names = classes.split(/\s+/u).filter((name) => name !== '')
  const line = `${PROBE_PREFIX}${names.join(' ')}"></div>`
  const answer = await server.withDocument(uri, 'html', line, async (connection) => {
    const colors = await TailwindLanguageServer.colors(connection, uri)
    const parts = []
    let character = PROBE_PREFIX.length
    for (const name of names) {
      const css = await TailwindLanguageServer.hover(connection, uri, { line: 0, character })
      const color = colors.find(
        (c) => c.range.start.character <= character && character < c.range.end.character,
      )?.color
      const colorText = color === undefined ? '' : `\ncolor: ${hexColor(color)}`
      parts.push(
        css === null ? `${name}: not a class in this project.` : `${name}:\n${css}${colorText}`,
      )
      character += name.length + 1
    }
    return parts.join('\n\n')
  })
  return text(answer ?? noProjectText(server, filePath ?? 'the project root'))
}

/**
 * @param {{ prefix: string, filePath?: string | undefined, limit: number }} args
 * @returns {Promise<ToolResult>}
 */
async function projectClasses({ prefix, filePath, limit }) {
  const { root, server } = await state()
  let uri
  try {
    uri = await probeUri(root, filePath)
  } catch (error) {
    return refusal(error)
  }
  const line = `${PROBE_PREFIX}${prefix}"></div>`
  const answer = await server.withDocument(uri, 'html', line, async (connection) => {
    const items = await TailwindLanguageServer.completion(connection, uri, {
      line: 0,
      character: PROBE_PREFIX.length + prefix.length,
    })
    // After a variant (hover:, md:dark:) the server completes the utility alone, so its labels
    // carry no variant: match them on the utility part and put the variants back.
    const variants = prefix.slice(0, prefix.lastIndexOf(':') + 1)
    const utility = prefix.slice(variants.length)
    const labels = [
      ...new Set(
        items
          .map((item) => item.label)
          .filter((label) => label.startsWith(utility))
          .map((label) => `${variants}${label}`),
      ),
    ]
    if (labels.length === 0) {
      return `No class in this project starts with ${prefix}.`
    }
    const shown = labels.slice(0, limit)
    const rest = labels.length - shown.length
    return [
      `Classes in this project that start with ${prefix} (${labels.length}):`,
      shown.join(' '),
      ...(rest > 0 ? [`… and ${rest} more; use a longer prefix to narrow them.`] : []),
    ].join('\n')
  })
  return text(answer ?? noProjectText(server, filePath ?? 'the project root'))
}

/**
 * @param {{ classes: string, filePath?: string | undefined }} args
 * @returns {Promise<ToolResult>}
 */
async function sortClasses({ classes, filePath }) {
  const { root, server } = await state()
  let uri
  try {
    uri = await probeUri(root, filePath)
  } catch (error) {
    return refusal(error)
  }
  const list = classes.trim().split(/\s+/u).join(' ')
  const answer = await server.withDocument(
    uri,
    'html',
    `${PROBE_PREFIX}${list}"></div>`,
    (connection) => TailwindLanguageServer.sortClasses(connection, uri, [list]),
  )
  if (answer === null) {
    return text(noProjectText(server, filePath ?? 'the project root'))
  }
  return text(answer[0] ?? list)
}

const filePathField = z
  .string()
  .min(1)
  .describe('Path of a file in the project, absolute or relative to the project root.')
const optionalContext = filePathField
  .optional()
  .describe(
    'A file in the project whose Tailwind CSS setup applies, for projects with several entry points. Defaults to the project root.',
  )
const classesField = z
  .string()
  .min(1)
  .max(4000)
  .regex(CLASS_LIST)
  .describe(
    'Class names separated by spaces, as written in a class attribute, such as "flex items-center gap-4".',
  )

/** A new MCP server per connection, as serveStdio requires; all share one language server. */
function createServer() {
  const server = new McpServer({ name: 'tailwind-development', version: PLUGIN_VERSION })

  server.registerTool(
    'check_file',
    {
      title: 'Check Tailwind CSS in a file',
      description:
        'Runs the Tailwind CSS language server on one file of the project and returns its diagnostics: class conflicts, invalid or non-canonical classes, invalid @apply and variants, with the exact replacement text of every quick fix the server offers. Reads the file; changes nothing. Returns why when no Tailwind CSS project covers the file.',
      inputSchema: z.object({
        filePath: filePathField,
        format: z
          .enum(['text', 'hook'])
          .default('text')
          .describe(
            '"text" for a readable list; "hook" for the PostToolUse hook JSON, used by the plugin\'s own hook.',
          ),
      }),
      annotations: { title: 'Check Tailwind CSS in a file', ...READ_ONLY },
    },
    checkFile,
  )

  server.registerTool(
    'class_css',
    {
      title: 'CSS generated by Tailwind CSS classes',
      description:
        "Returns the CSS each class generates in this project's Tailwind CSS setup, with pixel equivalents of rem values and the resolved color of color classes. A class the project does not define is reported as such. Changes nothing.",
      inputSchema: z.object({ classes: classesField, filePath: optionalContext }),
      annotations: { title: 'CSS generated by Tailwind CSS classes', ...READ_ONLY },
    },
    classCss,
  )

  server.registerTool(
    'project_classes',
    {
      title: "Classes in the project's Tailwind CSS theme",
      description:
        "Lists the class names that exist in this project's Tailwind CSS theme and start with a prefix, such as bg- or font-, including the project's own theme tokens. Does not list every class at once: the prefix is required. Changes nothing.",
      inputSchema: z.object({
        prefix: z
          .string()
          .min(1)
          .max(100)
          .regex(CLASS_LIST)
          .describe('Start of the class names to list, such as "bg-" or "text-brand".'),
        filePath: optionalContext,
        limit: z
          .number()
          .int()
          .min(1)
          .max(200)
          .default(50)
          .describe('Most class names to return. At most 200.'),
      }),
      annotations: { title: "Classes in the project's Tailwind CSS theme", ...READ_ONLY },
    },
    projectClasses,
  )

  server.registerTool(
    'sort_classes',
    {
      title: 'Sort Tailwind CSS classes',
      description:
        "Returns a class list in Tailwind CSS's official order, the order prettier-plugin-tailwindcss applies. Changes nothing; the sorted list is the answer.",
      inputSchema: z.object({ classes: classesField, filePath: optionalContext }),
      annotations: { title: 'Sort Tailwind CSS classes', ...READ_ONLY },
    },
    sortClasses,
  )

  return server
}

const connection = serveStdio(createServer, {
  onerror: (error) => process.stderr.write(`[tailwind-development] ${error.message}\n`),
})

/** Stops the language server when Claude Code closes the connection or ends the process. */
async function shutdown() {
  await connection.close()
  if (shared !== undefined) {
    await (await shared).server.dispose()
  }
  process.exit(0)
}
process.stdin.on('close', () => void shutdown())
process.on('SIGTERM', () => void shutdown())
