#!/usr/bin/env node
// PostToolUse hook: runs `biome check --write` on the file an Edit or Write changed.
// Files Biome does not read (other extensions, or paths biome.jsonc excludes, such as the
// Markdown Claude reads as instructions) pass in silence. Findings Biome cannot fix go to
// Claude on stderr with exit 2. A missing Biome is reported with exit 1 (non-blocking).

import { spawnSync } from 'node:child_process'
import { existsSync, readFileSync } from 'node:fs'
import { extname, join } from 'node:path'

const BIOME_EXTENSIONS = new Set([
  '.js',
  '.cjs',
  '.mjs',
  '.jsx',
  '.ts',
  '.cts',
  '.mts',
  '.tsx',
  '.json',
  '.jsonc',
  '.md',
  '.yml',
  '.yaml',
])

let input
try {
  input = JSON.parse(readFileSync(0, 'utf8'))
} catch {
  process.exit(0)
}

const file = input?.tool_input?.file_path
if (typeof file !== 'string' || !BIOME_EXTENSIONS.has(extname(file))) {
  process.exit(0)
}

const root = process.env['CLAUDE_PROJECT_DIR'] || input.cwd || process.cwd()
const biome = join(root, 'node_modules', '.bin', 'biome')
if (!existsSync(biome)) {
  process.stderr.write('biome-check: node_modules/.bin/biome is missing; run `npm run setup`.\n')
  process.exit(1)
}

const run = spawnSync(biome, ['check', '--write', '--no-errors-on-unmatched', file], {
  cwd: root,
  encoding: 'utf8',
})
if (run.status === 0) {
  process.exit(0)
}
process.stderr.write(
  `Biome found problems it could not fix in ${file}. Fix them, then re-read the file:\n` +
    `${run.stdout}${run.stderr}`,
)
process.exit(2)
