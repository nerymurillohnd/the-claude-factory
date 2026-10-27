// Row icons: Nerd Font glyphs where a Nerd Font is sure to draw them, plain Unicode otherwise.

export type Glyphs = 'nerd' | 'plain'

export type GlyphSetting = 'auto' | Glyphs

/** Font file names a Nerd Font ships under: `…NerdFont…`, `… Nerd Font …`, `MesloLGS NF …`. */
export const NERD_FONT_FILE = /nerd[\s_-]?font|(?:^|[\s_-])NF[MP]?(?:[\s_.-]|$)/i

const FONT_FILE = /\.(ttf|otf|ttc|woff2?)$/i

export const isNerdFontFile = (name: string): boolean =>
  FONT_FILE.test(name) && NERD_FONT_FILE.test(name)

export type GlyphFacts = {
  setting: GlyphSetting
  surface: string
  isSsh: boolean
  /** Modification times of the Nerd Font files found on this machine. */
  nerdFonts: readonly number[]
  /** When the terminal that draws this session started, where it could be found. */
  terminalStartedAt: number | null
}

/**
 * `auto`: plain in the desktop app (its own font), Nerd over SSH (the font is the client's,
 * which nothing here can see), and in a local terminal Nerd only when a Nerd Font is
 * installed and was installed before the terminal started, so the terminal has loaded it.
 */
export const decideGlyphs = (facts: GlyphFacts): Glyphs => {
  if (facts.setting !== 'auto') {
    return facts.setting
  }
  if (facts.surface !== 'terminal') {
    return 'plain'
  }
  if (facts.isSsh) {
    return 'nerd'
  }
  if (facts.nerdFonts.length === 0) {
    return 'plain'
  }
  if (facts.terminalStartedAt === null) {
    return 'nerd'
  }
  const startedAt = facts.terminalStartedAt
  return facts.nerdFonts.some((installedAt) => installedAt <= startedAt) ? 'nerd' : 'plain'
}

const NERD_BY_EXTENSION: Readonly<Record<string, string>> = {
  ts: '\u{e628}',
  tsx: '\u{e7ba}',
  js: '\u{e74e}',
  jsx: '\u{e7ba}',
  mjs: '\u{e74e}',
  json: '\u{e60b}',
  md: '\u{e609}',
  py: '\u{e606}',
  rs: '\u{e7a8}',
  go: '\u{e627}',
  rb: '\u{e791}',
  java: '\u{e738}',
  c: '\u{e61e}',
  h: '\u{e61e}',
  cpp: '\u{e61d}',
  cs: '\u{f031b}',
  swift: '\u{e755}',
  kt: '\u{e634}',
  php: '\u{e73d}',
  sh: '\u{f489}',
  zsh: '\u{f489}',
  bash: '\u{f489}',
  html: '\u{e736}',
  css: '\u{e749}',
  scss: '\u{e749}',
  svelte: '\u{e697}',
  vue: '\u{e6a0}',
  yml: '\u{e6a8}',
  yaml: '\u{e6a8}',
  toml: '\u{e6b2}',
  lock: '\u{f023}',
  png: '\u{f1c5}',
  jpg: '\u{f1c5}',
  jpeg: '\u{f1c5}',
  gif: '\u{f1c5}',
  svg: '\u{f1c5}',
  pdf: '\u{f1c1}',
  zip: '\u{f1c6}',
  txt: '\u{f15c}',
}

const NERD_FILE = '\u{f15b}'
const NERD_FOLDER = '\u{f07b}'
const NERD_FOLDER_OPEN = '\u{f07c}'

/** The icon before a row's name, one cell wide plus a space. */
export const iconFor = (
  name: string,
  kind: string,
  isExpanded: boolean,
  glyphs: Glyphs,
): string => {
  if (glyphs === 'plain') {
    if (kind === 'dir') {
      return isExpanded ? '▾ ' : '▸ '
    }
    return '  '
  }
  if (kind === 'dir') {
    return `${isExpanded ? NERD_FOLDER_OPEN : NERD_FOLDER} `
  }
  const dot = name.lastIndexOf('.')
  const extension = dot === -1 ? '' : name.slice(dot + 1).toLowerCase()
  return `${NERD_BY_EXTENSION[extension] ?? NERD_FILE} `
}
