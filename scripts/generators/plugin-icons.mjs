#!/usr/bin/env node
// @ts-check
// Renders each plugin's directory listing icon from its SVG source
// (ADR_2026-11-05_every-plugin-ships-a-directory-icon).
//   node scripts/generators/plugin-icons.mjs              → render every plugin
//   node scripts/generators/plugin-icons.mjs <plugin>...  → render only those plugins
//
// Source: scripts/generators/plugin-icons/<plugin>.svg, a 1024 × 1024 viewBox.
// Output: plugins/<plugin>/.claude-plugin/icon.png, 1024 × 1024, 256 colors, transparent corners.
// Run by hand after changing a source, never in the gates: it needs Playwright with its Chromium,
// ImageMagick (`magick`, or `convert` on ImageMagick 6) and the JetBrains Mono font, which only the
// maintainer's machine holds. scripts/validators/plugin-icons.py checks the committed PNGs.

import { spawnSync } from 'node:child_process'
import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync } from 'node:fs'
import { createRequire } from 'node:module'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fail, ROOT } from '../lib.mjs'

const SOURCES = join(ROOT, 'scripts', 'generators', 'plugin-icons')
const PLUGINS = join(ROOT, 'plugins')
const SIZE = 1024
// Loaded with require, which also searches NODE_PATH and the global folders: Playwright is not a
// dependency of this repository. Kept in a variable so tsc does not resolve it.
const PLAYWRIGHT = 'playwright'

/** @returns {string[]} */
function pluginNames() {
  return readdirSync(PLUGINS, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name)
    .sort()
}

/** @returns {string} The ImageMagick command on PATH. */
function imageMagick() {
  for (const cmd of ['magick', 'convert']) {
    if (spawnSync(cmd, ['-version'], { stdio: 'ignore' }).status === 0) {
      return cmd
    }
  }
  return fail('ImageMagick is not on PATH: install it to compress the icons')
}

async function main() {
  const all = pluginNames()
  const args = process.argv.slice(2)
  const unknown = args.filter((a) => !all.includes(a))
  if (unknown.length > 0) {
    fail(`not a plugin: ${unknown.join(', ')}`)
  }
  const names = args.length > 0 ? args : all
  const missing = names.filter((n) => !existsSync(join(SOURCES, `${n}.svg`)))
  if (missing.length > 0) {
    fail(`no SVG source in scripts/generators/plugin-icons/ for: ${missing.join(', ')}`)
  }
  const magick = imageMagick()
  /** @type {any} */
  let playwright
  try {
    playwright = createRequire(import.meta.url)(PLAYWRIGHT)
  } catch {
    fail('Playwright is not installed: install it with its Chromium to render the icons')
  }
  const tmp = mkdtempSync(join(tmpdir(), 'tcf-icons-'))
  const browser = await playwright.chromium.launch()
  try {
    // One page per icon, rendered side by side.
    await Promise.all(names.map((name) => render(browser, name, tmp, magick)))
  } finally {
    await browser.close()
    rmSync(tmp, { recursive: true, force: true })
  }
}

/**
 * Renders one plugin's SVG source and writes its compressed PNG into the plugin.
 * @param {any} browser A Playwright Chromium browser.
 * @param {string} name
 * @param {string} tmp A temporary folder for the full-color screenshot.
 * @param {string} magick The ImageMagick command.
 */
async function render(browser, name, tmp, magick) {
  const page = await browser.newPage({
    viewport: { width: SIZE, height: SIZE },
    deviceScaleFactor: 1,
  })
  const svg = readFileSync(join(SOURCES, `${name}.svg`), 'utf8')
  await page.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`)
  // A string, evaluated in the page: this file is type-checked without the DOM library.
  await page.evaluate('document.fonts.ready.then(() => true)')
  const raw = join(tmp, `${name}.png`)
  await page.locator('svg').screenshot({ path: raw, omitBackground: true })
  await page.close()
  const out = join(PLUGINS, name, '.claude-plugin', 'icon.png')
  // 256 colors, no dithering and no metadata: about 50 KB, and the same bytes on every run.
  const result = spawnSync(
    magick,
    [raw, '-strip', '-dither', 'None', '-colors', '256', `PNG8:${out}`],
    { encoding: 'utf8' },
  )
  if (result.status !== 0) {
    fail(`ImageMagick failed on ${name}: ${result.stderr.trim()}`)
  }
  process.stdout.write(`✔ plugins/${name}/.claude-plugin/icon.png\n`)
}

await main()
