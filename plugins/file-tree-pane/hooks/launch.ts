// How a file reaches another program: its default app, Quick Look, a terminal editor in a tmux
// window or a herdr pane, or a diff tool. Every plan is an argv run without a shell; a file name
// never passes through a command line a shell parses.

import { splitWords } from './activity.ts'
import { parentOf } from './tree.ts'

export type Platform = 'darwin' | 'linux' | 'windows'

export type Host = {
  platform: Platform
  /** Inside tmux (`TMUX` set). */
  isTmux: boolean
  /** The herdr pane Claude Code runs in (`HERDR_PANE_ID`), when it runs inside herdr. */
  herdrPane: string | null
  /** `$VISUAL`, then `$EDITOR`, then `vi`. */
  editor: string
}

/** One process to run. */
export type RunPlan = { kind: 'run'; argv: string[]; env?: Record<string, string>; cwd?: string }

/**
 * A herdr pane split to the right of Claude's, in the file's folder, then a command typed into
 * it. The file's path travels in the pane's environment as `FTP_FILE`, never in the command.
 */
export type HerdrPlan = { kind: 'herdr'; split: string[]; command: string }

/** A terminal editor in tmux that reuses a running nvim when the session has one. */
export type TmuxEditorPlan = {
  kind: 'tmux-editor'
  editor: string[]
  file: string
  line: number
  dir: string
}

export type Notice = { kind: 'notice'; text: string }

export type LaunchPlan = RunPlan | HerdrPlan | TmuxEditorPlan | Notice

export const NO_TERMINAL =
  'A terminal editor needs a tmux window or a herdr pane to run in; start Claude Code inside tmux or herdr, or set Open with to a GUI command.'

/** The platform from `uname -s`; Git Bash and other Windows shells report MINGW, MSYS or CYGWIN. */
export const platformOf = (uname: string): Platform => {
  const name = uname.trim().toLowerCase()
  if (name.startsWith('darwin')) {
    return 'darwin'
  }
  if (/mingw|msys|cygwin|windows/.test(name)) {
    return 'windows'
  }
  return 'linux'
}

/**
 * A template's words with `{path}` and `{line}` filled in; the path is added last when the
 * template does not place it. A word keeps its place, so a name with spaces stays one word.
 */
export const fillTemplate = (template: string, path: string, line: number): string[] => {
  const words = splitWords(template)
  const hasPath = words.some((word) => word.includes('{path}'))
  const filled = words.map((word) =>
    word.replaceAll('{path}', path).replaceAll('{line}', String(line)),
  )
  return hasPath ? filled : [...filled, path]
}

/** The default app for a file or folder. */
export const defaultAppPlan = (host: Host, path: string): RunPlan => {
  switch (host.platform) {
    case 'darwin':
      return { kind: 'run', argv: ['open', path] }
    case 'windows':
      return {
        kind: 'run',
        argv: [
          'powershell',
          '-NoProfile',
          '-NonInteractive',
          '-Command',
          'Start-Process -LiteralPath $env:FTP_FILE',
        ],
        // The path reaches PowerShell through its environment, never through a parsed command line.
        env: Object.fromEntries([['FTP_FILE', path]]),
      }
    default:
      return { kind: 'run', argv: ['xdg-open', path] }
  }
}

// What a herdr pane types: the editor, the line, the file from the environment, then exit so the
// pane closes when the editor does. `"$FTP_FILE"` reads the same in sh, bash, zsh and fish.
const herdrCommand = (program: string, line: number | null): string =>
  `${program}${line === null ? '' : ` +${line}`} "$FTP_FILE"; exit`

const herdrSplit = (pane: string, dir: string, file: string): string[] => [
  'herdr',
  'pane',
  'split',
  pane,
  '--direction',
  'right',
  '--cwd',
  dir,
  '--env',
  `FTP_FILE=${file}`,
  '--focus',
]

/** A terminal program on a file: a tmux window, a herdr pane, or a notice where neither is. */
const inTerminal = (host: Host, program: string, file: string, line: number | null): LaunchPlan => {
  const dir = parentOf(file) || '/'
  if (host.isTmux) {
    const argv = [...splitWords(program), ...(line === null ? [] : [`+${line}`]), file]
    return { kind: 'run', argv: ['tmux', 'new-window', '-c', dir, '--', ...argv] }
  }
  if (host.herdrPane !== null && host.platform !== 'windows') {
    return {
      kind: 'herdr',
      split: herdrSplit(host.herdrPane, dir, file),
      command: herdrCommand(program, line),
    }
  }
  return { kind: 'notice', text: NO_TERMINAL }
}

/** The editor at a line: tmux (reusing a running nvim), herdr, or a notice. */
const editorPlan = (host: Host, file: string, line: number): LaunchPlan => {
  if (host.platform === 'windows') {
    return { kind: 'notice', text: NO_TERMINAL }
  }
  const words = splitWords(host.editor)
  if (host.isTmux && words.length > 0) {
    return { kind: 'tmux-editor', editor: words, file, line, dir: parentOf(file) || '/' }
  }
  return inTerminal(host, host.editor, file, line)
}

/**
 * Open with: empty opens the default app; `editor` opens `$VISUAL`/`$EDITOR`/`vi` in tmux or
 * herdr; anything else is a command template.
 */
export const openPlan = (host: Host, setting: string, file: string): LaunchPlan => {
  const value = setting.trim()
  if (value === '') {
    return defaultAppPlan(host, file)
  }
  if (value === 'editor') {
    return editorPlan(host, file, 1)
  }
  return { kind: 'run', argv: fillTemplate(value, file, 1), cwd: parentOf(file) || '/' }
}

/** Whether `e` can open anything with these settings, so its button shows. */
export const canEdit = (host: Host, setting: string): boolean =>
  setting.trim() !== '' || (host.platform !== 'windows' && (host.isTmux || host.herdrPane !== null))

/** Edit with: empty is the terminal editor at `+line`; otherwise a command with `{line}`. */
export const editPlan = (host: Host, setting: string, file: string, line: number): LaunchPlan => {
  const value = setting.trim()
  if (value === '') {
    return editorPlan(host, file, line)
  }
  return { kind: 'run', argv: fillTemplate(value, file, line), cwd: parentOf(file) || '/' }
}

/**
 * Diff with, when set: a terminal diff tool on the path, in a tmux window, a herdr pane, or on
 * Linux a new terminal window through `xdg-terminal-exec`.
 */
export const diffToolPlan = (
  host: Host,
  setting: string,
  path: string,
  root: string,
): LaunchPlan => {
  const words = [...splitWords(setting.trim()), path]
  if (host.isTmux) {
    return { kind: 'run', argv: ['tmux', 'new-window', '-c', root, '--', ...words] }
  }
  if (host.herdrPane !== null && host.platform !== 'windows') {
    return {
      kind: 'herdr',
      split: herdrSplit(host.herdrPane, root, path),
      command: `${setting.trim()} "$FTP_FILE"; exit`,
    }
  }
  if (host.platform === 'linux') {
    return { kind: 'run', argv: ['xdg-terminal-exec', ...words], cwd: root }
  }
  return {
    kind: 'notice',
    text: 'Diff with needs a tmux window or a herdr pane to run in, or xdg-terminal-exec on Linux.',
  }
}

/** Quick Look on macOS; null elsewhere. */
export const quickLookPlan = (host: Host, file: string): RunPlan | null =>
  host.platform === 'darwin' ? { kind: 'run', argv: ['qlmanage', '-p', file] } : null

/** A path escaped for Vim's `:edit`: its special characters each behind a backslash. */
export const vimEscape = (path: string): string =>
  path.replace(/[\s\\%#|"'<>!$`*?[\]{}]/g, (c) => `\\${c}`)

/**
 * The tmux steps that hand a file to a running nvim: leave insert mode, type `:edit +line`, and
 * bring its window forward. Typed with `send-keys -l`, so tmux takes the text literally. Null for
 * a name holding a control character, which typed keys could turn into commands: such a file
 * opens in a new window instead, where its name is an argument.
 */
export const nvimReuseSteps = (pane: string, file: string, line: number): string[][] | null => {
  if (hasControlCharacter(file)) {
    return null
  }
  return [
    ['tmux', 'send-keys', '-t', pane, 'Escape'],
    ['tmux', 'send-keys', '-t', pane, '-l', `:edit +${line} ${vimEscape(file)}`],
    ['tmux', 'send-keys', '-t', pane, 'Enter'],
    ['tmux', 'select-window', '-t', pane],
    ['tmux', 'select-pane', '-t', pane],
  ]
}

/** Whether `text` holds a C0 control character or DEL, which typed keys would act on. */
export const hasControlCharacter = (text: string): boolean =>
  Array.from(text).some((char) => char.charCodeAt(0) < 0x20 || char.charCodeAt(0) === 0x7f)

/** The pane id of a running nvim in `tmux list-panes -s -F '#{pane_id} #{pane_current_command}'`. */
export const nvimPaneOf = (listing: string): string | null => {
  for (const line of listing.split('\n')) {
    const [pane, command] = line.trim().split(/\s+/)
    if (pane !== undefined && command === 'nvim') {
      return pane
    }
  }
  return null
}

/** herdr's version from `herdr --version` (`herdr 0.9.5`), as [major, minor, patch]. */
export const herdrVersionOf = (output: string): [number, number, number] | null => {
  const match = /(\d+)\.(\d+)\.(\d+)/.exec(output)
  return match === null ? null : [Number(match[1]), Number(match[2]), Number(match[3])]
}

/** herdr before 0.9.1 reports clicks at the wrong cells, so rows must not take the mouse. */
export const herdrClicksWork = (version: readonly [number, number, number] | null): boolean => {
  if (version === null) {
    return true
  }
  const [major, minor, patch] = version
  return major > 0 || minor > 9 || (minor === 9 && patch >= 1)
}
