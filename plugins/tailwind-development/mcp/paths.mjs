// Path checks for tool input. A path comes from Claude, and a prompt-injected page can make Claude
// pass any path, so every file is resolved, symlinks included, and must stay inside the project.

import { realpath, stat } from 'node:fs/promises'
import { extname, isAbsolute, relative, resolve } from 'node:path'

/** Files larger than this are not sent to the language server. */
export const MAX_FILE_BYTES = 1_000_000

/** A refusal the tool reports to Claude as an error result. */
export class ToolInputError extends Error {}

/**
 * The project root: Claude Code sets CLAUDE_PROJECT_DIR in a stdio server's environment.
 * @param {Readonly<Record<string, string | undefined>>} env
 */
export async function projectRoot(env) {
  const dir = env['CLAUDE_PROJECT_DIR']
  if (dir === undefined || dir === '') {
    throw new Error('CLAUDE_PROJECT_DIR is not set; Claude Code sets it for plugin MCP servers')
  }
  return realpath(dir)
}

/**
 * Whether `path` is `root` or inside it. Both must already be real paths.
 * @param {string} root
 * @param {string} path
 */
export function isInside(root, path) {
  const rel = relative(root, path)
  return rel === '' || (!rel.startsWith('..') && !isAbsolute(rel))
}

/**
 * Resolves a file path from tool input against the project root and checks it.
 * @param {string} root real path of the project root
 * @param {string} input absolute, or relative to the project root
 * @returns {Promise<{ path: string, relativePath: string, extension: string }>}
 */
export async function resolveProjectFile(root, input) {
  const candidate = resolve(root, input)
  /** @type {string} */
  let real
  try {
    real = await realpath(candidate)
  } catch {
    throw new ToolInputError(
      `${input} does not exist. Pass the path of an existing file in the project.`,
    )
  }
  if (!isInside(root, real)) {
    throw new ToolInputError(
      `${input} is outside the project (${root}). Only files inside the project can be checked.`,
    )
  }
  const info = await stat(real)
  if (!info.isFile()) {
    throw new ToolInputError(`${input} is not a file.`)
  }
  if (info.size > MAX_FILE_BYTES) {
    throw new ToolInputError(
      `${input} is ${info.size} bytes, above the ${MAX_FILE_BYTES}-byte limit; it was not checked.`,
    )
  }
  return { path: real, relativePath: relative(root, real), extension: extname(real).toLowerCase() }
}
