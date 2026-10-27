// The tree's model: directory listings joined into the rows the pane shows, and the paths
// between them. Paths are relative to the tree's root, with `/` separators; '' is the root.

export type EntryKind = 'file' | 'dir' | 'other'

export type Entry = {
  name: string
  kind: EntryKind
  size: number
  mtimeMs: number
  /** A file git still tracks that is gone from disk: shown so its deletion is visible. */
  isGhost: boolean
}

export type Row = {
  path: string
  name: string
  depth: number
  kind: EntryKind
  isExpanded: boolean
  entry: Entry
}

/** Names left out at any depth whatever the Ignore setting says. */
export const BUILT_IN_IGNORE: readonly string[] = ['.git', 'node_modules']

export const joinPath = (dir: string, name: string): string =>
  dir === '' ? name : `${dir}/${name}`

export const parentOf = (path: string): string => {
  const cut = path.lastIndexOf('/')
  return cut === -1 ? '' : path.slice(0, cut)
}

export const baseName = (path: string): string => path.slice(path.lastIndexOf('/') + 1)

/** Every folder above `path`, outermost first: `a/b/c` gives `a`, `a/b`. */
export const ancestorsOf = (path: string): string[] => {
  const parts = path.split('/')
  const out: string[] = []
  for (let i = 1; i < parts.length; i += 1) {
    out.push(parts.slice(0, i).join('/'))
  }
  return out
}

/** Backslashes to slashes and no trailing slash, so Windows and POSIX paths compare alike. */
export const normalizePath = (path: string): string => {
  const slashed = path.replaceAll('\\', '/')
  return slashed.length > 1 && slashed.endsWith('/') ? slashed.slice(0, -1) : slashed
}

/** `abs` relative to `root`, or null when it lies outside it. Drive letters compare case-blind. */
export const relativeTo = (abs: string, root: string): string | null => {
  const path = normalizePath(abs)
  const base = normalizePath(root)
  const isDrive = /^[a-z]:/i.test(base)
  const a = isDrive ? path.toLowerCase() : path
  const b = isDrive ? base.toLowerCase() : base
  if (a === b) {
    return ''
  }
  const prefix = b.endsWith('/') ? b : `${b}/`
  return a.startsWith(prefix) ? path.slice(prefix.length) : null
}

export const absoluteOf = (rel: string, root: string): string => {
  const base = normalizePath(root)
  if (rel === '') {
    return base
  }
  return base.endsWith('/') ? `${base}${rel}` : `${base}/${rel}`
}

/** The Ignore setting: names separated by spaces or commas, matched exactly. */
export const parseIgnore = (text: string): Set<string> => {
  const names = new Set(BUILT_IN_IGNORE)
  for (const name of text.split(/[\s,]+/)) {
    if (name !== '') {
      names.add(name)
    }
  }
  return names
}

export const isIgnored = (path: string, ignore: ReadonlySet<string>): boolean =>
  path.split('/').some((part) => ignore.has(part))

// Natural order by hand: the hooks environment does not promise Intl.
export const compareNames = (a: string, b: string): number => {
  const left = a.toLowerCase().match(/\d+|\D+/g) ?? []
  const right = b.toLowerCase().match(/\d+|\D+/g) ?? []
  for (let i = 0; i < Math.min(left.length, right.length); i += 1) {
    const x = left[i] ?? ''
    const y = right[i] ?? ''
    if (x === y) {
      continue
    }
    const isNumber = /^\d/.test(x) && /^\d/.test(y)
    if (isNumber && Number(x) !== Number(y)) {
      return Number(x) - Number(y)
    }
    return x < y ? -1 : 1
  }
  if (left.length !== right.length) {
    return left.length - right.length
  }
  if (a === b) {
    return 0
  }
  return a < b ? -1 : 1
}

/** Folders first, then names in natural order (`file2` before `file10`), case-blind. */
export const sortEntries = (entries: readonly Entry[]): Entry[] =>
  [...entries].sort((a, b) => {
    if ((a.kind === 'dir') !== (b.kind === 'dir')) {
      return a.kind === 'dir' ? -1 : 1
    }
    return compareNames(a.name, b.name)
  })

/** Adds the files git lists as deleted under `dir` that the listing no longer has. */
export const withGhosts = (
  dir: string,
  entries: readonly Entry[],
  deleted: Iterable<string>,
): Entry[] => {
  const names = new Set(entries.map((entry) => entry.name))
  const ghosts: Entry[] = []
  for (const path of deleted) {
    if (parentOf(path) === dir) {
      const name = baseName(path)
      if (!names.has(name)) {
        names.add(name)
        ghosts.push({ name, kind: 'file', size: 0, mtimeMs: 0, isGhost: true })
      }
    }
  }
  return ghosts.length === 0 ? [...entries] : [...entries, ...ghosts]
}

/** The rows the tree shows: each loaded folder's entries, expanded folders opened in place. */
export const flatten = (
  listings: ReadonlyMap<string, readonly Entry[]>,
  expanded: ReadonlySet<string>,
  ignore: ReadonlySet<string>,
): Row[] => {
  const rows: Row[] = []
  const walk = (dir: string, depth: number): void => {
    const entries = listings.get(dir)
    if (entries === undefined) {
      return
    }
    for (const entry of sortEntries(entries)) {
      const path = joinPath(dir, entry.name)
      if (ignore.has(entry.name)) {
        continue
      }
      const isExpanded = entry.kind === 'dir' && expanded.has(path)
      rows.push({ path, name: entry.name, depth, kind: entry.kind, isExpanded, entry })
      if (isExpanded) {
        walk(path, depth + 1)
      }
    }
  }
  walk('', 0)
  return rows
}

/** The largest list offset that still fills the window: the last row sits on its last line. */
export const maxOffset = (total: number, room: number): number =>
  Math.max(0, total - Math.max(1, room))

export const clampOffset = (offset: number, total: number, room: number): number =>
  Math.min(Math.max(0, Math.round(offset)), maxOffset(total, room))

/** The offset that brings row `index` into a window of `room` rows, moving as little as it can. */
export const revealOffset = (
  index: number,
  offset: number,
  total: number,
  room: number,
): number => {
  const span = Math.max(1, room)
  if (index < offset) {
    return clampOffset(index, total, span)
  }
  if (index >= offset + span) {
    return clampOffset(index - span + 1, total, span)
  }
  return clampOffset(offset, total, span)
}
