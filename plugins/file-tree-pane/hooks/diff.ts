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

/** Parses `git diff` output, any number of files. */
export const parseDiff = (text: string): ParsedDiff => {
  const rows: DiffRow[] = []
  const files: number[] = []
  const hunks: number[] = []
  let oldLine = 0
  let newLine = 0
  let isInHunk = false
  for (const line of text.split('\n')) {
    if (line.startsWith('diff --git ')) {
      const match = / b\/(.*)$/.exec(line)
      files.push(rows.length)
      rows.push({ kind: 'file', text: match?.[1] ?? line.slice('diff --git '.length), line: null })
      isInHunk = false
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
