// What the hooks module and the body's surface module say to each other: the props it draws and
// the messages it posts back. Plain JSON both ways.

/** One run of text in a row, with its look. */
export type Segment = {
  text: string
  color: string | null
  isDim: boolean
  isBold: boolean
  isStruck: boolean
}

export type BodyLine = {
  key: string
  segments: Segment[]
  /** The segment holding the row's name, which the shimmer sweeps; -1 for none. */
  nameIndex: number
  /** The activity color to shimmer in, or null when Claude is not touching this row. */
  shimmer: string | null
  /** The row's own background (a diff's added or removed line), under a selection or hover. */
  bg: string | null
}

export type BodyProps = {
  /** The lines in view, starting at list row `first`; empty when `code` is drawn instead. */
  lines: BodyLine[]
  /** A file's lines in view, drawn by Claude Code's code view, or null for rows. */
  code: { source: string; path: string; startLine: number } | null
  first: number
  total: number
  /** The selected list row, or null. */
  selected: number | null
  selectedBg: string
  hoveredBg: string
  barColor: string
  trackColor: string
  /** True under herdr before 0.9.1, whose click positions are wrong: the rows ignore the mouse. */
  isPointerOff: boolean
}

export type BodyMessage =
  | { type: 'size'; rows: number; columns: number }
  | { type: 'click'; index: number }
  | { type: 'open'; index: number }
  | { type: 'key'; key: string; ctrl: boolean; shift: boolean }
  | { type: 'scrollTo'; ratio: number }

export const DOUBLE_CLICK_MS = 400
export const SHIMMER_MS = 90

/** The scrollbar's thumb in a window of `room` rows, or null when everything fits. */
export const thumbOf = (
  first: number,
  total: number,
  room: number,
): { start: number; end: number } | null => {
  if (total <= room || room <= 0) {
    return null
  }
  const size = Math.max(1, Math.round((room * room) / total))
  const span = Math.max(1, total - room)
  const start = Math.round((Math.min(first, span) / span) * (room - size))
  return { start, end: start + size }
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value)

const isIndex = (value: unknown): value is number =>
  typeof value === 'number' && Number.isInteger(value) && value >= 0

/** A post from the surface module, checked field by field; null for anything else. */
export const readMessage = (data: unknown): BodyMessage | null => {
  if (!isRecord(data)) {
    return null
  }
  const { type, rows, columns, index, key, ctrl, shift, ratio } = data
  switch (type) {
    case 'size':
      return isIndex(rows) && isIndex(columns) ? { type, rows, columns } : null
    case 'click':
    case 'open':
      return isIndex(index) ? { type, index } : null
    case 'key':
      return typeof key === 'string'
        ? { type, key, ctrl: ctrl === true, shift: shift === true }
        : null
    case 'scrollTo':
      return typeof ratio === 'number' && ratio >= 0 && ratio <= 1 ? { type, ratio } : null
    default:
      return null
  }
}
