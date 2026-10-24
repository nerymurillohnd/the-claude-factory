// A unified diff read into one row per line the pane draws: a heading per file, one per hunk,
// and each added, removed or unchanged line with its line number.

export type DiffRowKind = 'file' | 'hunk' | 'add' | 'del' | 'ctx' | 'note'

export type DiffRow = {
  kind: DiffRowKind
  text: string
  /** The line's number in the new file (old file for a removed line); null for headings. */
  line: number | null
}

export type ParsedDiff = {
  rows: DiffRow[]
  /** Row indices where each file's heading sits. */
  files: number[]
  /** Row indices where each hunk's heading sits. */
  hunks: number[]
}

const HUNK = /^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@ ?(.*)$/

const ESCAPES: Record<string, number> = { a: 7, b: 8, t: 9, n: 10, v: 11, f: 12, r: 13 }

// UTF-8 bytes to text, without TextDecoder, which a hooks module may not have.
const fromUtf8 = (bytes: readonly number[]): string => {
  let out = ''
  let i = 0
  while (i < bytes.length) {
    const lead = bytes[i] ?? 0
    const size = lead >= 0xf0 ? 4 : lead >= 0xe0 ? 3 : lead >= 0xc0 ? 2 : 1
    let code = size === 1 ? lead : lead & (0xff >> (size + 1))
    for (let k = 1; k < size; k += 1) {
      code = (code << 6) | ((bytes[i + k] ?? 0) & 0x3f)
    }
    out += String.fromCodePoint(code)
    i += size
  }
  return out
}

/**
 * A path as git prints it in a diff header: as is, or C-quoted (`"caf\303\251"`) when it holds
 * a quote, a backslash, a control character or, under the default `core.quotePath`, a byte past
 * ASCII. Octal escapes are UTF-8 bytes.
 */
export const unquotePath = (text: string): string => {
  if (!(text.length >= 2 && text.startsWith('"') && text.endsWith('"'))) {
    return text
  }
  const body = text.slice(1, -1)
  let out = ''
  let bytes: number[] = []
  for (let i = 0; i < body.length; i += 1) {
    const char = body[i] ?? ''
    const octal = char === '\\' ? /^[0-3][0-7]{2}/.exec(body.slice(i + 1, i + 4))?.[0] : undefined
    if (octal !== undefined) {
      bytes.push(Number.parseInt(octal, 8))
      i += 3
      continue
    }
    out += fromUtf8(bytes)
    bytes = []
    if (char === '\\') {
      const next = body[i + 1] ?? ''
      out += next in ESCAPES ? String.fromCharCode(ESCAPES[next] ?? 0) : next
      i += 1
    } else {
      out += char
    }
  }
  return out + fromUtf8(bytes)
}

// The name in a `--- a/x` or `+++ b/x` header line, or null for /dev/null.
const headerName = (line: string): string | null => {
  const name = unquotePath(line.slice(4))
  return name === '/dev/null' ? null : name.replace(/^[ab]\//, '')
}

/** Parses `git diff` output, any number of files. */
export const parseDiff = (text: string): ParsedDiff => {
  const rows: DiffRow[] = []
  const files: number[] = []
  const hunks: number[] = []
  let oldLine = 0
  let newLine = 0
  let isInHunk = false
  // The file heading's row, named from `diff --git` and renamed from the `---`/`+++` lines, which
  // carry the name alone (the `diff --git` line can't tell `a/x b/y` apart when names hold spaces).
  let heading: DiffRow | null = null
  for (const line of text.split('\n')) {
    if (line.startsWith('diff --git ')) {
      const rest = line.slice('diff --git '.length)
      const quoted = /"((?:[^"\\]|\\.)*)"$/.exec(rest)?.[0]
      const name =
        quoted === undefined ? (/ b\/(.*)$/.exec(rest)?.[1] ?? rest) : headerName(`+++ ${quoted}`)
      files.push(rows.length)
      heading = { kind: 'file', text: name ?? rest, line: null }
      rows.push(heading)
      isInHunk = false
      continue
    }
    if (!isInHunk && heading !== null && (line.startsWith('--- ') || line.startsWith('+++ '))) {
      const name = headerName(line)
      if (name !== null) {
        heading.text = name
      }
      continue
    }
    const hunk = HUNK.exec(line)
    if (hunk !== null) {
      oldLine = Number(hunk[1])
      newLine = Number(hunk[2])
      hunks.push(rows.length)
      rows.push({ kind: 'hunk', text: line, line: null })
      isInHunk = true
      continue
    }
    if (!isInHunk) {
      if (line.startsWith('Binary files ')) {
        rows.push({ kind: 'note', text: 'Binary file changed', line: null })
      }
      continue
    }
    if (line.startsWith('+')) {
      rows.push({ kind: 'add', text: line.slice(1), line: newLine })
      newLine += 1
    } else if (line.startsWith('-')) {
      rows.push({ kind: 'del', text: line.slice(1), line: oldLine })
      oldLine += 1
    } else if (line.startsWith(' ')) {
      rows.push({ kind: 'ctx', text: line.slice(1), line: newLine })
      oldLine += 1
      newLine += 1
    } else if (line.startsWith('\\')) {
      rows.push({ kind: 'note', text: line.slice(2), line: null })
    }
  }
  return { rows, files, hunks }
}

/** The next stop after `current` (or the previous one before it), or `current` when none. */
export const nextStop = (stops: readonly number[], current: number, direction: 1 | -1): number => {
  if (direction === 1) {
    return stops.find((stop) => stop > current) ?? current
  }
  for (let i = stops.length - 1; i >= 0; i -= 1) {
    const stop = stops[i] ?? 0
    if (stop < current) {
      return stop
    }
  }
  return current
}

/** The same rows without the file headings, for a diff of one file. */
export const withoutHeadings = (diff: ParsedDiff): ParsedDiff => {
  const rows: DiffRow[] = []
  const hunks: number[] = []
  diff.rows.forEach((row, i) => {
    if (row.kind === 'file') {
      return
    }
    if (diff.hunks.includes(i)) {
      hunks.push(rows.length)
    }
    rows.push(row)
  })
  return { rows, files: [], hunks }
}
