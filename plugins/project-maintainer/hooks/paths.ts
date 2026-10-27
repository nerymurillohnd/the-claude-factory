// The words every guard shares with the skills and their templates: folders, file names,
// statuses and outcomes. Change one here only together with the skill text that names it.

export const ADR_STATUSES = [
  'proposed',
  'accepted',
  'rejected',
  'deprecated',
  'superseded',
] as const
export const DEBT_STATUSES = ['Pending', 'In progress', 'Blocked', 'Risk accepted'] as const
export const OUTCOMES = ['resolved', 'obsolete', 'accepted'] as const

export const ADR_NAME = /^ADR_(\d{4}-\d{2}-\d{2})_([a-z0-9]+(?:-[a-z0-9]+)*)\.md$/
export const ADR_ID = /^ADR_\d{4}-\d{2}-\d{2}_[a-z0-9]+(?:-[a-z0-9]+)*$/
export const DEBT_ID = /^DEBT-\d{3,}$/

export type RecordKind = 'adr' | 'pending-debt' | 'closed-debt'

export type RecordRef = {
  kind: RecordKind
  /** The folder that holds the file, with forward slashes. */
  dir: string
  name: string
}

const RECORD_PATH = /^(.*\/\.claude\/maintainer)\/(decisions|technical-debt)\/([^/]+)$/i
/** An absolute path once backslashes are slashes, POSIX or with a Windows drive. */
const ABSOLUTE_SLASHED = /^([A-Za-z]:)?\//
/** A Windows drive at the start of a path, such as `C:`. */
const DRIVE = /^[A-Za-z]:/

/**
 * The absolute path a tool call really writes: relative paths are taken from the session's
 * directory, and `.`, `..`, repeated slashes and backslashes are folded away.
 */
export function resolvePath(path: string, cwd: string): string {
  const slashed = path.replaceAll('\\', '/')
  const absolute = ABSOLUTE_SLASHED.test(slashed)
    ? slashed
    : `${cwd.replaceAll('\\', '/')}/${slashed}`
  const drive = DRIVE.exec(absolute)?.[0] ?? ''
  const parts: string[] = []
  for (const part of absolute.slice(drive.length).split('/')) {
    if (part === '..') {
      parts.pop()
    } else if (part !== '' && part !== '.') {
      parts.push(part)
    }
  }
  return `${drive}/${parts.join('/')}`
}

/** Says which record a resolved path is, or null for any other file. A case-insensitive disk folds the case. */
export function classify(path: string): RecordRef | null {
  const match = RECORD_PATH.exec(path.replaceAll('\\', '/'))
  if (match === null) {
    return null
  }
  const [, base = '', folder = '', name = ''] = match
  if (folder.toLowerCase() === 'decisions') {
    return name.toLowerCase().endsWith('.md')
      ? { kind: 'adr', dir: `${base}/${folder}`, name }
      : null
  }
  if (name.toLowerCase() === 'pending-debt.md') {
    return { kind: 'pending-debt', dir: `${base}/${folder}`, name }
  }
  if (name.toLowerCase() === 'closed-debt.md') {
    return { kind: 'closed-debt', dir: `${base}/${folder}`, name }
  }
  return null
}

/** The ID of an ADR is its file name without the extension. */
export function adrId(name: string): string {
  return name.endsWith('.md') ? name.slice(0, -'.md'.length) : name
}

/** Line endings and trailing spaces never count as a change. */
export function normalize(text: string): string {
  return text
    .replaceAll('\r\n', '\n')
    .split('\n')
    .map((line) => line.trimEnd())
    .join('\n')
    .trimEnd()
}
