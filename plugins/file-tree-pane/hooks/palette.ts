// The pane's colors. On a dark theme they are the theme's own keys, so they follow the person's
// theme and its switches; on a light theme they are a palette of their own whose every text
// color reaches WCAG AAA (7:1) on the background, the selected row and the hovered row. Where the
// theme's background is unknown (`auto`, which follows the terminal, or a custom theme without a
// readable base) every color is a theme key, so none is a fixed hue drawn on the wrong background.

export type Tone =
  | 'read'
  | 'write'
  | 'commit'
  | 'modified'
  | 'added'
  | 'deleted'
  | 'untracked'
  | 'conflict'
  | 'muted'
  | 'accent'
  | 'selected'
  | 'hovered'

export type Palette = Record<Tone, string>

export const TONES: readonly Tone[] = [
  'read',
  'write',
  'commit',
  'modified',
  'added',
  'deleted',
  'untracked',
  'conflict',
  'muted',
  'accent',
  'selected',
  'hovered',
]

/** Backgrounds: the selected and hovered rows. Every other tone is a text color. */
export const BACKGROUNDS: readonly Tone[] = ['selected', 'hovered']

// Dark themes: theme keys where one carries the meaning, fixed hues where the spec names a hue
// (reads purple, writes orange, commits green) that no key promises.
export const DARK: Palette = {
  read: '#b48ef7',
  write: '#ff9e57',
  commit: '#5fd38d',
  modified: 'warning',
  added: 'success',
  deleted: 'error',
  untracked: 'success',
  conflict: 'error',
  muted: 'subtle',
  accent: 'claude',
  selected: '#2f3a52',
  hovered: '#262b36',
}

/** The background a light theme draws on, which the AAA palette is measured against. */
export const LIGHT_BACKGROUND = '#ffffff'

export const LIGHT: Palette = {
  read: '#55278f',
  write: '#733000',
  commit: '#0b4a24',
  modified: '#574000',
  added: '#0b4a24',
  deleted: '#8a0c1a',
  untracked: '#144714',
  conflict: '#8a0c1a',
  muted: '#404040',
  accent: '#6b2d12',
  selected: '#e8edf6',
  hovered: '#f2f4f8',
}

/** Every tone a theme key, for a theme whose background the pane can't know. */
export const THEMED: Palette = {
  read: 'merged',
  write: 'claude',
  commit: 'success',
  modified: 'warning',
  added: 'success',
  deleted: 'error',
  untracked: 'success',
  conflict: 'error',
  muted: 'subtle',
  accent: 'claude',
  selected: 'selectionBg',
  hovered: 'userMessageBackgroundHover',
}

export type Look = 'dark' | 'light' | 'themed'

/**
 * The palette a theme setting calls for: the built-in presets by name (`light`,
 * `light-daltonized`, `light-ansi` and their dark twins), a custom theme (`custom:<slug>`) by the
 * `base` its file names, and `auto` or a custom theme whose base can't be read by theme keys.
 */
export const lookOf = (theme: string | undefined, customBase: string | null = null): Look => {
  if (theme === undefined) {
    return 'dark'
  }
  if (theme.startsWith('custom:')) {
    if (customBase === null) {
      return 'themed'
    }
    return /light/i.test(customBase) ? 'light' : 'dark'
  }
  if (theme === 'auto') {
    return 'themed'
  }
  return /light/i.test(theme) ? 'light' : 'dark'
}

const HEX = /^#([0-9a-f]{6})$/i

const channel = (value: number): number => {
  const c = value / 255
  return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
}

const luminance = (hex: string): number => {
  const digits = HEX.exec(hex)?.[1] ?? '000000'
  const r = Number.parseInt(digits.slice(0, 2), 16)
  const g = Number.parseInt(digits.slice(2, 4), 16)
  const b = Number.parseInt(digits.slice(4, 6), 16)
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)
}

/** WCAG's contrast ratio between two `#rrggbb` colors, 1 to 21. */
export const contrast = (a: string, b: string): number => {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x)
  return ((hi ?? 0) + 0.05) / ((lo ?? 0) + 0.05)
}

/**
 * The Palette setting: `tone=#rrggbb` pairs separated by spaces or commas, laid over the
 * theme's palette. Unknown tones and malformed colors are reported, not applied.
 */
export const parsePalette = (text: string): { colors: Partial<Palette>; problems: string[] } => {
  const colors: Partial<Palette> = {}
  const problems: string[] = []
  for (const pair of text.split(/[\s,]+/)) {
    if (pair === '') {
      continue
    }
    const [tone, color] = pair.split('=')
    const known = TONES.find((t) => t === tone)
    if (known === undefined || color === undefined || !HEX.test(color)) {
      problems.push(pair)
      continue
    }
    colors[known] = color
  }
  return { colors, problems }
}

const PRESETS: Record<Look, Palette> = { dark: DARK, light: LIGHT, themed: THEMED }

/** The palette in force: the theme's, then the person's own colors over it. */
export const paletteFor = (look: Look, own: Partial<Palette>): Palette => ({
  ...PRESETS[look],
  ...own,
})
