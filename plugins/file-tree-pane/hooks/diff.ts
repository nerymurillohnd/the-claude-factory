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

// How many bytes the UTF-8 sequence that starts with `lead` takes.
const utf8Length = (lead: number): number => {
  if (lead >= 0xf0) {
    return 4
  }
  if (lead >= 0xe0) {
    return 3
  }
  if (lead >= 0xc0) {
    return 2
  }
  return 1
}

// UTF-8 bytes to text, without TextDecoder, which a hooks module may not have.
const fromUtf8 = (bytes: readonly number[]): string => {
  let out = ''
  let i = 0
  while (i < bytes.length) {
    const lead = bytes[i] ?? 0
    const size = utf8Length(lead)
    let code = size === 1 ? lead : lead & (0xff >> (size + 1))
    for (let k = 1; k < size; k += 1) {
      code = (code << 6) | ((bytes[i + k] ?? 0) & 0x3f)
    }
    out += String.fromCodePoint(code)
    i += size
  }
  return out
}

// The three octal digits after a backslash at `body[i]`, or undefined.
const octalAt = (body: string, i: number): string | undefined => {
  if (body[i] !== '\\') {
    return undefined
  }
  return /^[0-3][0-7]{2}/.exec(body.slice(i + 1, i + 4))?.[0]
}

// The character a C escape such as `\n` stands for; any other escaped character is itself.
const unescaped = (char: string): string =>
  char in ESCAPES ? String.fromCharCode(ESCAPES[char] ?? 0) : char

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
    const octal = octalAt(body, i)
    if (octal !== undefined) {
      bytes.push(Number.parseInt(octal, 8))
      i += 3
      continue
    }
    out += fromUtf8(bytes)
    bytes = []
    if (char === '\\') {
      out += unescaped(body[i + 1] ?? '')
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

/** Where parseDiff is: the rows so far and the line numbers the next hunk line takes. */
type DiffReader = ParsedDiff & {
  oldLine: number
  newLine: number
  isInHunk: boolean
  // The file heading's row, named from `diff --git` and renamed from the `---`/`+++` lines, which
  // carry the name alone (the `diff --git` line can't tell `a/x b/y` apart when names hold spaces).
  heading: DiffRow | null
}

// The file name on a `diff --git` line, after the prefix.
const gitLineName = (rest: string): string => {
  const quoted = /"((?:[^"\\]|\\.)*)"$/.exec(rest)?.[0]
  const name =
    quoted === undefined ? (/ b\/(.*)$/.exec(rest)?.[1] ?? rest) : headerName(`+++ ${quoted}`)
  return name ?? rest
}

const startFile = (reader: DiffReader, line: string): void => {
  reader.files.push(reader.rows.length)
  reader.heading = {
    kind: 'file',
    text: gitLineName(line.slice('diff --git '.length)),
    line: null,
  }
  reader.rows.push(reader.heading)
  reader.isInHunk = false
}

const startHunk = (reader: DiffReader, line: string, hunk: RegExpExecArray): void => {
  reader.oldLine = Number(hunk[1])
  reader.newLine = Number(hunk[2])
  reader.hunks.push(reader.rows.length)
  reader.rows.push({ kind: 'hunk', text: line, line: null })
  reader.isInHunk = true
}

// An added, removed, unchanged or `\ No newline` line inside a hunk.
const readHunkLine = (reader: DiffReader, line: string): void => {
  if (line.startsWith('+')) {
    reader.rows.push({ kind: 'add', text: line.slice(1), line: reader.newLine })
    reader.newLine += 1
  } else if (line.startsWith('-')) {
    reader.rows.push({ kind: 'del', text: line.slice(1), line: reader.oldLine })
    reader.oldLine += 1
  } else if (line.startsWith(' ')) {
    reader.rows.push({ kind: 'ctx', text: line.slice(1), line: reader.newLine })
    reader.oldLine += 1
    reader.newLine += 1
  } else if (line.startsWith('\\')) {
    reader.rows.push({ kind: 'note', text: line.slice(2), line: null })
  }
}

// Whether `line` is a `---`/`+++` header of the file being read, before its first hunk.
const isFileHeader = (reader: DiffReader, line: string): boolean =>
  !reader.isInHunk &&
  reader.heading !== null &&
  (line.startsWith('--- ') || line.startsWith('+++ '))

/** Parses `git diff` output, any number of files. */
export const parseDiff = (text: string): ParsedDiff => {
  const reader: DiffReader = {
    rows: [],
    files: [],
    hunks: [],
    oldLine: 0,
    newLine: 0,
    isInHunk: false,
    heading: null,
  }
  for (const line of text.split('\n')) {
    if (line.startsWith('diff --git ')) {
      startFile(reader, line)
      continue
    }
    if (isFileHeader(reader, line)) {
      const name = headerName(line)
      if (reader.heading !== null && name !== null) {
        reader.heading.text = name
      }
      continue
    }
    const hunk = HUNK.exec(line)
    if (hunk !== null) {
      startHunk(reader, line, hunk)
    } else if (reader.isInHunk) {
      readHunkLine(reader, line)
    } else if (line.startsWith('Binary files ')) {
      reader.rows.push({ kind: 'note', text: 'Binary file changed', line: null })
    }
  }
  const { rows, files, hunks } = reader
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
