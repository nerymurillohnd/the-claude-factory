// A client for the Tailwind CSS language server. It starts the server on first use, keeps it for
// the MCP server's life, and asks it for diagnostics, quick fixes, hovers, colors, completions and
// the official class order. It never writes a file.

import { spawn } from 'node:child_process'
import { access } from 'node:fs/promises'
import { fileURLToPath, pathToFileURL } from 'node:url'
import {
  createMessageConnection,
  StreamMessageReader,
  StreamMessageWriter,
} from 'vscode-jsonrpc/node'

/** @typedef {import('vscode-jsonrpc/node').MessageConnection} MessageConnection */
/** @typedef {{ line: number, character: number }} Position */
/** @typedef {{ start: Position, end: Position }} Range */
/** @typedef {{ range: Range, newText: string }} TextEdit */
/** @typedef {{ range: Range, severity?: number, code?: string | number, message: string }} Diagnostic */
/** @typedef {{ title: string, kind?: string, edit?: { changes?: Record<string, TextEdit[]> } }} CodeAction */
/** @typedef {{ range: Range, color: { red: number, green: number, blue: number, alpha: number } }} ColorInformation */
/** @typedef {{ label: string, kind?: number, detail?: string }} CompletionItem */
/** @typedef {{ uri: string, config?: string, tailwind?: { version?: string } }} ProjectDetails */

/** Where Claude Code installs the language server: the plugin's own node_modules. */
export const SERVER_PATH = fileURLToPath(
  new URL(
    '../node_modules/@tailwindcss/language-server/bin/tailwindcss-language-server',
    import.meta.url,
  ),
)

const PROJECT_POLL_MS = 250
/** The first project load reads the whole project; later documents of a loaded project are fast. */
const PROJECT_TIMEOUT_MS = 10_000
/** Once a project is loaded, a document no project covers is known quickly. */
const LOADED_PROJECT_GRACE_MS = 1000
const DIAGNOSTICS_TIMEOUT_MS = 5000
/** The server's settings section, as workspace/configuration names it. */
const SETTINGS_SECTION = 'tailwindCSS'

export class TailwindLanguageServer {
  /** @type {Promise<MessageConnection> | undefined} */
  #ready
  /** @type {Map<string, number>} document versions by URI */
  #versions = new Map()
  /** @type {Map<string, { version: number | undefined, diagnostics: Diagnostic[] }>} */
  #published = new Map()
  /** @type {Set<() => void>} */
  #listeners = new Set()
  /** @type {ProjectDetails[]} */
  #projects = []
  /** Whether some project has loaded, so a null getProject answer is final after a short grace. */
  #loaded = false
  /** @type {import('node:child_process').ChildProcess | undefined} */
  #child

  /**
   * @param {object} init
   * @param {string} init.root real path of the project root, the server's workspace folder
   * @param {object} init.settings the tailwindCSS settings section
   * @param {string} [init.serverPath]
   * @param {string[]} [init.serverArgs] arguments after the server path; tests start a stub server
   * @param {(message: string) => void} [init.log] defaults to stderr
   * @param {{ project?: number, grace?: number, diagnostics?: number }} [init.timeouts] in ms; tests shorten them
   */
  constructor({
    root,
    settings,
    serverPath = SERVER_PATH,
    serverArgs = ['--stdio'],
    log,
    timeouts = {},
  }) {
    this.root = root
    this.rootUri = pathToFileURL(root).href
    this.settings = settings
    this.serverPath = serverPath
    this.serverArgs = serverArgs
    this.log = log ?? ((message) => process.stderr.write(`[tailwind-development] ${message}\n`))
    this.timeouts = {
      project: timeouts.project ?? PROJECT_TIMEOUT_MS,
      grace: timeouts.grace ?? LOADED_PROJECT_GRACE_MS,
      diagnostics: timeouts.diagnostics ?? DIAGNOSTICS_TIMEOUT_MS,
    }
  }

  /** The projects the server has reported, with their config file and Tailwind CSS version. */
  get projects() {
    return [...this.#projects]
  }

  /** Starts the server once; a crashed server is started again on the next call. */
  connection() {
    this.#ready ??= this.#start().catch((/** @type {unknown} */ error) => {
      this.#ready = undefined
      throw error
    })
    return this.#ready
  }

  async #start() {
    try {
      await access(this.serverPath)
    } catch {
      throw new Error(
        `The Tailwind CSS language server is not installed at ${this.serverPath}. Claude Code installs it with the plugin; run "claude plugin list" to see whether the dependency install failed.`,
      )
    }
    const child = spawn(process.execPath, [this.serverPath, ...this.serverArgs], {
      cwd: this.root,
      stdio: ['pipe', 'pipe', 'pipe'],
    })
    this.#child = child
    // An unhandled 'error' event would end the MCP server itself, which Claude Code then marks
    // failed until the user reconnects it in /mcp. A dead language server is restarted instead.
    child.on('error', (error) => this.log(`language server: ${error.message}`))
    child.stdin.on('error', (error) => this.log(`language server stdin: ${error.message}`))
    child.stderr.on('data', (/** @type {Buffer} */ chunk) => this.log(chunk.toString().trimEnd()))
    const connection = createMessageConnection(
      new StreamMessageReader(child.stdout),
      new StreamMessageWriter(child.stdin),
    )
    child.on('exit', (code, signal) => {
      this.log(`language server exited (${signal ?? code})`)
      this.#ready = undefined
      this.#loaded = false
      this.#versions.clear()
      this.#published.clear()
      connection.dispose()
    })
    this.#handleServerMessages(connection)
    connection.listen()

    const folder = { uri: this.rootUri, name: 'project' }
    await connection.sendRequest('initialize', {
      processId: process.pid,
      clientInfo: { name: 'tailwind-development' },
      rootUri: this.rootUri,
      workspaceFolders: [folder],
      initializationOptions: {},
      capabilities: {
        workspace: { configuration: true, workspaceFolders: true },
        textDocument: {
          synchronization: { didSave: false },
          publishDiagnostics: { relatedInformation: false, versionSupport: true },
          hover: { contentFormat: ['markdown', 'plaintext'] },
          completion: { completionItem: { documentationFormat: ['markdown', 'plaintext'] } },
          codeAction: { codeActionLiteralSupport: { codeActionKind: { valueSet: ['quickfix'] } } },
          colorProvider: {},
        },
        experimental: { tailwind: { projectDetails: true } },
      },
    })
    await connection.sendNotification('initialized', {})
    await connection.sendNotification('workspace/didChangeConfiguration', {
      settings: { [SETTINGS_SECTION]: this.settings },
    })
    return connection
  }

  /** @param {MessageConnection} connection */
  #handleServerMessages(connection) {
    connection.onRequest(
      'workspace/configuration',
      (/** @type {{ items: { section?: string }[] }} */ params) =>
        params.items.map(({ section }) => {
          if (section === SETTINGS_SECTION) {
            return this.settings
          }
          if (section === 'editor') {
            return { tabSize: 2 }
          }
          return {}
        }),
    )
    connection.onRequest('workspace/workspaceFolders', () => [
      { uri: this.rootUri, name: 'project' },
    ])
    connection.onRequest('client/registerCapability', () => null)
    connection.onRequest('client/unregisterCapability', () => null)
    connection.onRequest('window/workDoneProgress/create', () => null)
    connection.onRequest('@/tailwindCSS/getDocumentSymbols', () => [])
    connection.onNotification(
      'textDocument/publishDiagnostics',
      (/** @type {{ uri: string, version?: number, diagnostics: Diagnostic[] }} */ params) => {
        this.#published.set(params.uri, {
          version: params.version,
          diagnostics: params.diagnostics,
        })
        for (const listener of this.#listeners) {
          listener()
        }
      },
    )
    connection.onNotification(
      '@/tailwindCSS/projectDetails',
      (/** @type {ProjectDetails} */ details) => {
        this.#projects = [...this.#projects.filter((p) => p.uri !== details.uri), details]
      },
    )
    connection.onNotification('@/tailwindCSS/projectsDestroyed', () => {
      this.#projects = []
    })
    connection.onNotification('window/logMessage', (/** @type {{ message: string }} */ params) =>
      this.log(params.message),
    )
    connection.onUnhandledNotification(() => undefined)
  }

  /**
   * Opens a document, or sends its new full text when it is already open.
   * @param {MessageConnection} connection
   * @param {string} uri
   * @param {string} languageId
   * @param {string} text
   */
  async #sync(connection, uri, languageId, text) {
    const previous = this.#versions.get(uri)
    const version = (previous ?? 0) + 1
    this.#versions.set(uri, version)
    if (previous === undefined) {
      await connection.sendNotification('textDocument/didOpen', {
        textDocument: { uri, languageId, version, text },
      })
    } else {
      await connection.sendNotification('textDocument/didChange', {
        textDocument: { uri, version },
        contentChanges: [{ text }],
      })
    }
    return version
  }

  /**
   * Closes a document this client opened only to ask about it.
   * @param {MessageConnection} connection
   * @param {string} uri
   */
  async #close(connection, uri) {
    this.#versions.delete(uri)
    this.#published.delete(uri)
    await connection.sendNotification('textDocument/didClose', { textDocument: { uri } })
  }

  /**
   * Waits until the server has a Tailwind CSS project for the document, or the time runs out.
   * @param {MessageConnection} connection
   * @param {string} uri
   * @returns {Promise<{ version: string } | null>}
   */
  async #project(connection, uri) {
    const deadline = Date.now() + (this.#loaded ? this.timeouts.grace : this.timeouts.project)
    for (;;) {
      /** @type {{ version: string } | null} */
      const project = await connection.sendRequest('@/tailwindCSS/getProject', { uri })
      if (project !== null) {
        this.#loaded = true
        return project
      }
      if (Date.now() >= deadline) {
        // A cold start that found nothing in time is not retried at full length on every edit.
        this.#loaded = true
        return null
      }
      await new Promise((done) => setTimeout(done, PROJECT_POLL_MS))
    }
  }

  /**
   * Resolves with the diagnostics the server publishes for `uri` at `version` or later, or null
   * when none arrive in time.
   * @param {string} uri
   * @param {number} version
   * @returns {Promise<Diagnostic[] | null>}
   */
  #publishedAfter(uri, version) {
    return new Promise((done) => {
      const check = () => {
        const entry = this.#published.get(uri)
        if (entry !== undefined && (entry.version === undefined || entry.version >= version)) {
          finish(entry.diagnostics)
        }
      }
      const timer = setTimeout(() => finish(null), this.timeouts.diagnostics)
      /** @param {Diagnostic[] | null} result */
      const finish = (result) => {
        clearTimeout(timer)
        this.#listeners.delete(check)
        done(result)
      }
      this.#listeners.add(check)
    })
  }

  /**
   * The document's diagnostics, or null when the server finds no Tailwind CSS project for it.
   * @param {string} uri
   * @param {string} languageId
   * @param {string} text
   */
  async diagnostics(uri, languageId, text) {
    const connection = await this.connection()
    await this.#sync(connection, uri, languageId, text)
    if ((await this.#project(connection, uri)) === null) {
      return null
    }
    // The project may have finished loading after the first publish; a new version makes the
    // server lint the document again with the loaded project.
    this.#published.delete(uri)
    const version = await this.#sync(connection, uri, languageId, text)
    return (await this.#publishedAfter(uri, version)) ?? []
  }

  /**
   * The quick fixes the server offers for one diagnostic.
   * @param {string} uri
   * @param {Diagnostic} diagnostic
   * @returns {Promise<CodeAction[]>}
   */
  async quickFixes(uri, diagnostic) {
    const connection = await this.connection()
    /** @type {CodeAction[] | null} */
    const actions = await connection.sendRequest('textDocument/codeAction', {
      textDocument: { uri },
      range: diagnostic.range,
      context: { diagnostics: [diagnostic], only: ['quickfix'] },
    })
    return actions ?? []
  }

  /**
   * Opens a document that exists only for this question, runs `ask`, and closes it.
   * @template T
   * @param {string} uri
   * @param {string} languageId
   * @param {string} text
   * @param {(connection: MessageConnection) => Promise<T>} ask
   * @returns {Promise<T | null>} null when the server finds no Tailwind CSS project
   */
  async withDocument(uri, languageId, text, ask) {
    const connection = await this.connection()
    await this.#sync(connection, uri, languageId, text)
    try {
      if ((await this.#project(connection, uri)) === null) {
        return null
      }
      return await ask(connection)
    } finally {
      await this.#close(connection, uri)
    }
  }

  /**
   * @param {MessageConnection} connection
   * @param {string} uri
   * @param {Position} position
   * @returns {Promise<string | null>} the hover's text
   */
  static async hover(connection, uri, position) {
    /** @type {{ contents: string | { value: string } | (string | { value: string })[] } | null} */
    const hover = await connection.sendRequest('textDocument/hover', {
      textDocument: { uri },
      position,
    })
    if (hover === null) {
      return null
    }
    const parts = Array.isArray(hover.contents) ? hover.contents : [hover.contents]
    return parts.map((part) => (typeof part === 'string' ? part : part.value)).join('\n')
  }

  /**
   * @param {MessageConnection} connection
   * @param {string} uri
   * @returns {Promise<ColorInformation[]>}
   */
  static async colors(connection, uri) {
    /** @type {ColorInformation[] | null} */
    const colors = await connection.sendRequest('textDocument/documentColor', {
      textDocument: { uri },
    })
    return colors ?? []
  }

  /**
   * @param {MessageConnection} connection
   * @param {string} uri
   * @param {Position} position
   * @returns {Promise<CompletionItem[]>}
   */
  static async completion(connection, uri, position) {
    /** @type {CompletionItem[] | { items: CompletionItem[] } | null} */
    const result = await connection.sendRequest('textDocument/completion', {
      textDocument: { uri },
      position,
    })
    if (result === null) {
      return []
    }
    return Array.isArray(result) ? result : result.items
  }

  /**
   * The class lists in Tailwind CSS's official order.
   * @param {MessageConnection} connection
   * @param {string} uri
   * @param {string[]} classLists
   * @returns {Promise<string[] | null>}
   */
  static async sortClasses(connection, uri, classLists) {
    /** @type {{ classLists?: string[], error?: string }} */
    const result = await connection.sendRequest('@/tailwindCSS/sortSelection', { uri, classLists })
    return result.classLists ?? null
  }

  /** Stops the server: a polite shutdown, then the process is ended whatever it answered. */
  async dispose() {
    const ready = this.#ready
    const child = this.#child
    this.#ready = undefined
    this.#child = undefined
    try {
      if (ready !== undefined) {
        const connection = await ready
        const timeout = new Promise((done) => setTimeout(done, 2000))
        await Promise.race([connection.sendRequest('shutdown'), timeout])
        await connection.sendNotification('exit')
        connection.dispose()
      }
    } catch (error) {
      this.log(`shutdown: ${error instanceof Error ? error.message : String(error)}`)
    } finally {
      child?.kill()
    }
  }
}

/**
 * The text a range covers.
 * @param {string} text
 * @param {Range} range
 */
export function textInRange(text, range) {
  const lines = text.split('\n')
  /** @param {Position} position */
  const offset = (position) => {
    let total = 0
    for (let i = 0; i < position.line && i < lines.length; i += 1) {
      total += (lines[i]?.length ?? 0) + 1
    }
    return total + position.character
  }
  return text.slice(offset(range.start), offset(range.end))
}
