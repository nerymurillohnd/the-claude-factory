// Text the rows show: ages, dates, sizes, and fitting a line into the pane's width.

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const MINUTE: number = 60_000
const HOUR: number = 60 * MINUTE
const DAY: number = 24 * HOUR

/** How long ago, in a few characters: `now`, `12m`, `3h`, `5d`, `Oct 9`, then `2025`. */
export const formatAge = (mtimeMs: number, now: number): string => {
  if (mtimeMs <= 0) {
    return ''
  }
  const ago = Math.max(0, now - mtimeMs)
  if (ago < MINUTE) {
    return 'now'
  }
  if (ago < HOUR) {
    return `${Math.floor(ago / MINUTE)}m`
  }
  if (ago < DAY) {
    return `${Math.floor(ago / HOUR)}h`
  }
  if (ago < 7 * DAY) {
    return `${Math.floor(ago / DAY)}d`
  }
  const date = new Date(mtimeMs)
  if (ago < 365 * DAY) {
    return `${MONTHS[date.getMonth()] ?? ''} ${date.getDate()}`
  }
  return String(date.getFullYear())
}

const two = (n: number): string => String(n).padStart(2, '0')

/** `Oct 09 14:02` within the current year, `2025-10-09` before it. */
export const formatDate = (mtimeMs: number, now: number): string => {
  if (mtimeMs <= 0) {
    return ''
  }
  const date = new Date(mtimeMs)
  if (date.getFullYear() === new Date(now).getFullYear()) {
    return `${MONTHS[date.getMonth()] ?? ''} ${two(date.getDate())} ${two(date.getHours())}:${two(date.getMinutes())}`
  }
  return `${date.getFullYear()}-${two(date.getMonth() + 1)}-${two(date.getDate())}`
}

/** `512B`, `1.2K`, `34K`, `1.5M`, `2.0G`, in powers of 1024. */
export const formatSize = (bytes: number): string => {
  if (bytes < 1024) {
    return `${Math.max(0, Math.round(bytes))}B`
  }
  const units = ['K', 'M', 'G', 'T']
  let value = bytes / 1024
  let unit = 0
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024
    unit += 1
  }
  return `${value < 10 ? value.toFixed(1) : Math.round(value)}${units[unit] ?? ''}`
}

/** Cuts `text` to `width` characters, ending with `…` when it had to cut. */
export const clip = (text: string, width: number): string => {
  if (width <= 0) {
    return ''
  }
  return text.length <= width ? text : `${text.slice(0, Math.max(0, width - 1))}…`
}

// What a name, a diff line or a preview line must never draw raw: C0 controls but tab, DEL and C1
// controls, which a terminal can read as escape sequences, and the direction marks, overrides and
// isolates that make a name read as another (`invoice‮fdp.exe` shows as `invoiceexe.pdf`).
const isUnprintable = (code: number): boolean =>
  (code < 0x20 && code !== 0x09) ||
  (code >= 0x7f && code <= 0x9f) ||
  code === 0x061c ||
  code === 0x200e ||
  code === 0x200f ||
  (code >= 0x202a && code <= 0x202e) ||
  (code >= 0x2066 && code <= 0x2069)

/** `text` with every unprintable character drawn as U+FFFD, one for one, so widths stay. */
export const printable = (text: string): string => {
  let shown = ''
  for (const char of text) {
    shown += isUnprintable(char.codePointAt(0) ?? 0) ? '\uFFFD' : char
  }
  return shown
}
