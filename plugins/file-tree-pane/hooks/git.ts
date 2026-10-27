// Git's machine output read into what the tree shows: each file's status and line counts,
// each folder's counts, and the branch line of the header.

import { ancestorsOf } from './tree.ts'

export type GitCode = 'modified' | 'added' | 'deleted' | 'renamed' | 'conflict' | 'untracked'

export type GitFile = {
  code: GitCode
  /** Lines added and removed against HEAD; null where git gives none (binary, not counted). */
  added: number | null
  removed: number | null
}

export type GitHead = {
  /** The branch name, or null when HEAD is detached. */
  branch: string | null
  /** The commit HEAD names, or null before the first commit. */
  oid: string | null
  upstream: string | null
  ahead: number
  behind: number
}

export type FolderCounts = { untracked: number; modified: number; deleted: number }

export type GitSnapshot = {
  head: GitHead
  /** Paths relative to the tree's root. */
  files: Map<string, GitFile>
  folders: Map<string, FolderCounts>
}

/** The tree an empty repository diffs against: git's well-known empty tree object. */
export const EMPTY_TREE = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'

const codeOf = (xy: string): GitCode => {
  if (xy.includes('D')) {
    return 'deleted'
  }
  if (xy.includes('R') || xy.includes('C')) {
    return 'renamed'
  }
  if (xy[0] === 'A') {
    return 'added'
  }
  return 'modified'
}

// Splits a record into `count` fields and the path, which may hold spaces.
const fieldsOf = (record: string, count: number): { fields: string[]; path: string } => {
  const fields: string[] = []
  let rest = record
  for (let i = 0; i < count; i += 1) {
    const cut = rest.indexOf(' ')
    if (cut === -1) {
      return { fields, path: '' }
    }
    fields.push(rest.slice(0, cut))
    rest = rest.slice(cut + 1)
  }
  return { fields, path: rest }
}

/** A path from git (relative to the repository's top) made relative to the tree's root. */
export const underPrefix = (path: string, prefix: string): string | null => {
  if (prefix === '') {
    return path
  }
  return path.startsWith(prefix) ? path.slice(prefix.length) : null
}

// A `# branch.…` header record read into `head`; other headers are left alone.
const readBranchHeader = (head: GitHead, record: string): void => {
  if (record.startsWith('# branch.oid ')) {
    const oid = record.slice('# branch.oid '.length)
    head.oid = oid === '(initial)' ? null : oid
  } else if (record.startsWith('# branch.head ')) {
    const name = record.slice('# branch.head '.length)
    head.branch = name === '(detached)' ? null : name
  } else if (record.startsWith('# branch.upstream ')) {
    head.upstream = record.slice('# branch.upstream '.length)
  } else if (record.startsWith('# branch.ab ')) {
    const match = /^# branch\.ab \+(\d+) -(\d+)$/.exec(record)
    head.ahead = Number(match?.[1] ?? 0)
    head.behind = Number(match?.[2] ?? 0)
  }
}

// A changed, renamed, conflicted or untracked file's record: its path and status, or null.
const entryOf = (record: string): { path: string; code: GitCode } | null => {
  if (record.startsWith('1 ')) {
    const { fields, path } = fieldsOf(record, 8)
    return { path, code: codeOf(fields[1] ?? '') }
  }
  if (record.startsWith('2 ')) {
    const { fields, path } = fieldsOf(record, 9)
    return { path, code: codeOf(fields[1] ?? '') }
  }
  if (record.startsWith('u ')) {
    return { path: fieldsOf(record, 10).path, code: 'conflict' }
  }
  if (record.startsWith('? ')) {
    return { path: record.slice(2), code: 'untracked' }
  }
  return null
}

/**
 * Reads `git status --porcelain=v2 --branch -z`. `prefix` is `git rev-parse --show-prefix`:
 * where the tree's root sits inside the repository, with a trailing slash.
 */
export const parseStatus = (
  output: string,
  prefix: string,
): { head: GitHead; files: Map<string, GitFile> } => {
  const head: GitHead = { branch: null, oid: null, upstream: null, ahead: 0, behind: 0 }
  const files = new Map<string, GitFile>()
  const records = output.split('\0')
  for (let i = 0; i < records.length; i += 1) {
    const record = records[i] ?? ''
    if (record.startsWith('# ')) {
      readBranchHeader(head, record)
      continue
    }
    if (record.startsWith('2 ')) {
      i += 1 // the original path follows as its own record
    }
    const entry = entryOf(record)
    const rel = entry === null ? null : underPrefix(entry.path, prefix)
    // An untracked folder git did not open (a trailing slash) is not a file of its own.
    if (entry !== null && rel !== null && !(entry.code === 'untracked' && rel.endsWith('/'))) {
      files.set(rel, { code: entry.code, added: null, removed: null })
    }
  }
  return { head, files }
}

/** Reads `git diff --relative --numstat -z`: lines added and removed per path. */
export const parseNumstat = (
  output: string,
): Map<string, { added: number | null; removed: number | null }> => {
  const counts = new Map<string, { added: number | null; removed: number | null }>()
  const records = output.split('\0')
  for (let i = 0; i < records.length; i += 1) {
    const record = records[i] ?? ''
    const match = /^(-|\d+)\t(-|\d+)\t(.*)$/s.exec(record)
    if (match === null) {
      continue
    }
    const added = match[1] === '-' ? null : Number(match[1])
    const removed = match[2] === '-' ? null : Number(match[2])
    let path = match[3] ?? ''
    if (path === '') {
      // A rename: the old and the new path follow as their own records.
      path = records[i + 2] ?? ''
      i += 2
    }
    if (path !== '') {
      counts.set(path, { added, removed })
    }
  }
  return counts
}

/** Reads `wc -l a b c`: the line count of each file named, by name. */
export const parseWc = (output: string): Map<string, number> => {
  const counts = new Map<string, number>()
  for (const line of output.split('\n')) {
    const match = /^\s*(\d+)\s(.+)$/.exec(line)
    if (match !== null && match[2] !== 'total') {
      counts.set(match[2] ?? '', Number(match[1]))
    }
  }
  return counts
}

/** Each folder's `?` untracked, `M` changed and `D` deleted files below it, at any depth. */
export const rollUp = (files: ReadonlyMap<string, GitFile>): Map<string, FolderCounts> => {
  const folders = new Map<string, FolderCounts>()
  for (const [path, file] of files) {
    for (const folder of ['', ...ancestorsOf(path)]) {
      const counts = folders.get(folder) ?? { untracked: 0, modified: 0, deleted: 0 }
      if (file.code === 'untracked') {
        counts.untracked += 1
      } else if (file.code === 'deleted') {
        counts.deleted += 1
      } else {
        counts.modified += 1
      }
      folders.set(folder, counts)
    }
  }
  return folders
}

/** `?:2 M:5 D:1`, leaving out the counts that are zero. */
export const countsText = (counts: FolderCounts | undefined): string => {
  if (counts === undefined) {
    return ''
  }
  const parts: string[] = []
  if (counts.untracked > 0) {
    parts.push(`?:${counts.untracked}`)
  }
  if (counts.modified > 0) {
    parts.push(`M:${counts.modified}`)
  }
  if (counts.deleted > 0) {
    parts.push(`D:${counts.deleted}`)
  }
  return parts.join(' ')
}

/** `+12 -3`, or the half that is not zero. */
export const linesText = (file: GitFile | undefined): string => {
  if (file === undefined || (file.added === null && file.removed === null)) {
    return ''
  }
  const parts: string[] = []
  if ((file.added ?? 0) > 0) {
    parts.push(`+${file.added}`)
  }
  if ((file.removed ?? 0) > 0) {
    parts.push(`-${file.removed}`)
  }
  return parts.join(' ')
}

/** The header's branch line: `main → origin/main ↑2 ↓1`, a detached commit, or a new repo. */
export const headText = (head: GitHead): string => {
  const name = head.branch ?? (head.oid === null ? 'HEAD' : `HEAD ${head.oid.slice(0, 7)}`)
  if (head.oid === null && head.branch !== null) {
    return `${name} · no commits yet`
  }
  if (head.upstream === null) {
    return head.branch === null ? name : `${name} · no upstream`
  }
  const sync: string[] = []
  if (head.ahead > 0) {
    sync.push(`↑${head.ahead}`)
  }
  if (head.behind > 0) {
    sync.push(`↓${head.behind}`)
  }
  return [`${name} → ${head.upstream}`, ...sync].join(' ')
}
