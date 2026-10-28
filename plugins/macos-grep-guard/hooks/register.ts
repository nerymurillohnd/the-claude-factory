// macos-grep-guard: one tool.call hook on Bash.
// Before the command runs, it denies a recursive grep whose results would be
// incomplete without an explicit choice, and an awk program that relies on
// IGNORECASE. After it runs, it adds the macOS form of a BSD or zsh error.

import type { EngineInterface, ProcessRunResult, Register } from 'claude-code'
import {
  type Analysis,
  AWK_DENIAL,
  analyze,
  fallbackDenial,
  type GrepFinding,
  grepDenial,
  hintsFor,
} from './rules'

/**
 * A git probe never runs a program the searched repository names in its own config:
 * \`core.fsmonitor\` is run by git when it reads the index, and a cloned repository can set it.
 */
const GIT = ['git', '-c', 'core.fsmonitor=false']

/** Every probe runs from `/` with absolute paths and gives up after 5 seconds. */
const PROBE = { cwd: '/', timeoutMs: 5000 }

let isDarwinCache: boolean | undefined
let awkIgnoresCaseCache: boolean | undefined

function probe($: EngineInterface, argv: string[]): Promise<ProcessRunResult> {
  return $.process.run(argv, PROBE)
}

/** Whether this machine runs macOS. A failed probe means "unknown" (`undefined`), and the guard stays out of the way. */
async function detectDarwin($: EngineInterface): Promise<boolean | undefined> {
  if (isDarwinCache === undefined) {
    try {
      const uname = await probe($, ['uname', '-s'])
      isDarwinCache = uname.exitCode === 0 && uname.stdout.trim() === 'Darwin'
    } catch {
      return undefined
    }
  }
  return isDarwinCache
}

/**
 * The folder the command starts in. A subagent's Bash folder does not follow the
 * session's (tools reference: "Subagent sessions never carry over working directory
 * changes"), so a subagent call counts as an unknown folder.
 */
async function startFolder(
  $: EngineInterface,
  agentId: string | undefined,
): Promise<string | null> {
  if (agentId !== undefined) {
    return null
  }
  try {
    return await $.session.cwd()
  } catch {
    return null
  }
}

/** Whether a nested repository or submodule sits under the root. A find that fails counts as one, so the grep is stopped. */
async function hasNestedRepository($: EngineInterface, root: string): Promise<boolean> {
  const nested = await probe($, [
    '/usr/bin/find',
    root,
    '-mindepth',
    '2',
    '-name',
    '.git',
    '-print',
    '-quit',
  ])
  return nested.exitCode !== 0 || nested.stdout.trim() !== ''
}

/** Steps 2 and 3 for a root that holds a .gitignore: whether ugrep would skip anything there. */
async function gitignoreHidesFiles($: EngineInterface, root: string): Promise<boolean> {
  const inside = await probe($, [...GIT, '-C', root, 'rev-parse', '--is-inside-work-tree'])
  if (inside.exitCode !== 0 || inside.stdout.trim() !== 'true') {
    /** A .gitignore outside a work tree. */
    return true
  }
  if (await hasNestedRepository($, root)) {
    /** A nested repository or submodule: ugrep applies its .gitignore, which the outer repository's git does not report. */
    return true
  }
  /** Untracked ignored entries, then tracked files that match .gitignore. */
  const others = await probe($, [
    ...GIT,
    '-C',
    root,
    'ls-files',
    '--others',
    '--ignored',
    '--exclude-per-directory=.gitignore',
    '--directory',
    '--',
    '.',
  ])
  const cached = await probe($, [
    ...GIT,
    '-C',
    root,
    'ls-files',
    '--cached',
    '--ignored',
    '--exclude-per-directory=.gitignore',
    '--',
    '.',
  ])
  return (
    others.exitCode !== 0 ||
    cached.exitCode !== 0 ||
    others.stdout.trim() !== '' ||
    cached.stdout.trim() !== ''
  )
}

/** Whether ugrep would skip files under one search root. A probe that cannot start, times out or is refused leaves the root unresolved, which counts as yes. */
async function rootSkipsFiles($: EngineInterface, root: string): Promise<boolean> {
  try {
    /** Step 1: ugrep reads only the .gitignore files inside the tree it searches. */
    const found = await probe($, ['/usr/bin/find', root, '-name', '.gitignore', '-print', '-quit'])
    if (found.exitCode !== 0) {
      return true
    }
    return found.stdout.trim() !== '' && (await gitignoreHidesFiles($, root))
  } catch {
    return true
  }
}

/** Whether the command must state its ignore-files choice: it states none and a root could not be ruled out. */
async function mustChooseIgnore($: EngineInterface, grep: GrepFinding): Promise<boolean> {
  if (!grep.lacksIgnoreChoice) {
    return false
  }
  if (grep.roots === null) {
    return true
  }
  const skips = await Promise.all(grep.roots.map((root) => rootSkipsFiles($, root)))
  return skips.some(Boolean)
}

/** The denial for one recursive grep, or `null` when it would miss nothing. */
async function grepVerdict($: EngineInterface, grep: GrepFinding): Promise<string | null> {
  const isIgnoreMissing = await mustChooseIgnore($, grep)
  if (!(isIgnoreMissing || grep.lacksBinaryChoice)) {
    return null
  }
  const ignoreReason =
    grep.roots === null
      ? 'the guard cannot tell which folder this recursive grep searches, so it cannot rule out skipped files. Run it again with an absolute search path, so the guard can check that folder and let it run when nothing would be skipped, or append the flags below.'
      : 'this recursive grep would skip files in this search, or the guard could not rule that out.'
  const reason = isIgnoreMissing ? ignoreReason : 'this recursive grep would skip binary files.'
  return grepDenial(isIgnoreMissing, grep.lacksBinaryChoice, reason)
}

/** Whether this machine's awk ignores `IGNORECASE`. A probe that fails counts as yes. */
async function awkIgnoresCase($: EngineInterface): Promise<boolean> {
  if (awkIgnoresCaseCache === undefined) {
    try {
      const result = await probe($, ['awk', 'BEGIN { IGNORECASE = 1; print ("A" ~ "a") }'])
      awkIgnoresCaseCache = result.stdout.trim() !== '1'
    } catch {
      awkIgnoresCaseCache = true
    }
  }
  return awkIgnoresCaseCache
}

/** The denial text for a command, or `null` when nothing in it needs stopping. */
async function denialFor($: EngineInterface, analysis: Analysis): Promise<string | null> {
  const verdicts = await Promise.all(analysis.greps.map((grep) => grepVerdict($, grep)))
  const grepDenied = verdicts.find((verdict) => verdict !== null)
  if (grepDenied !== undefined) {
    return grepDenied
  }
  return analysis.usesAwkIgnoreCase && (await awkIgnoresCase($)) ? AWK_DENIAL : null
}

function stderrOf(result: unknown): string {
  return typeof result === 'object' &&
    result !== null &&
    'stderr' in result &&
    typeof result.stderr === 'string'
    ? result.stderr
    : ''
}

/** The error text of a finished Bash call: its message when it failed, its stderr otherwise. */
function outputOf(ran: {
  result?: unknown
  text?: string | undefined
  isError?: boolean | undefined
}): string {
  if (ran.isError === true) {
    return ran.text ?? (typeof ran.result === 'string' ? ran.result : '')
  }
  return stderrOf(ran.result)
}

export const register: Register = (on: Parameters<Register>[0]) => {
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    if ((await detectDarwin($)) !== true) {
      return next(e)
    }
    const analysis = analyze(e.command, await startFolder($, e.agentId))
    const denial = await denialFor($, analysis)
    if (denial !== null) {
      return { deny: denial }
    }

    const ran = await next(e)
    if (ran.deny !== undefined) {
      return ran
    }
    const hints = hintsFor(analysis.programs, outputOf(ran))
    return hints.length === 0 ? ran : { ...ran, context: [...(ran.context ?? []), ...hints] }
  }).catch((_$, e, next) => {
    if (next.called || isDarwinCache !== true) {
      return next(e)
    }
    const denial = fallbackDenial(e.command)
    return denial === null ? next(e) : { deny: denial }
  })
}
