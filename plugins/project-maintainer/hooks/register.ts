// Project Maintainer's guardrails. Every call on `$` lives in this file; the rules themselves are
// pure functions in the sibling modules, so the tests can run them without an engine.
//
// - Format guard: refuses to save a malformed ADR or debt ledger, or one it could not check.
//   Nobody can waive it.
// - Authority guard: asks the person before a settled record is rewritten. Claude cannot waive it.
// - Compaction note: keeps decisions, open items and record IDs in the summary.
// - Commit nudge: after a commit that looks like a decision, reminds Claude of write-records.

import type { EngineInterface, On, PluginOptions } from 'claude-code'
import {
  askReason,
  authorityReasons,
  bashReason,
  commitSignals,
  fileInput,
  formatProblems,
  mayWriteRecord,
  nudgeText,
  refusal,
  resultingText,
  type Surroundings,
  withKeepNote,
} from './guard.ts'
import { ADR_NAME, adrId, classify, type RecordRef, resolvePath } from './paths.ts'

type Read = {
  /** The text of the file, or null when it does not exist (or could not be read). */
  text: string | null
  /** True when the file exists and could not be read: nothing can be checked against it. */
  failed: boolean
}

async function readText($: EngineInterface, path: string): Promise<Read> {
  try {
    if (!(await $.fs.exists(path))) {
      return { text: null, failed: false }
    }
    return { text: await $.fs.read(path), failed: false }
  } catch {
    return { text: null, failed: true }
  }
}

async function around($: EngineInterface, ref: RecordRef): Promise<Surroundings> {
  const decisions =
    ref.kind === 'adr' ? ref.dir : ref.dir.replace(/\/technical-debt$/, '/decisions')
  let names: string[] = []
  try {
    names = (await $.fs.list(decisions))
      .filter((entry) => entry.kind === 'file')
      .map((entry) => entry.name)
  } catch {
    // The folder does not exist yet: there is no ADR to point at.
  }
  const adrIds = new Set(names.filter((name) => ADR_NAME.test(name)).map(adrId))
  if (ref.kind === 'adr') {
    return { otherLedger: null, adrIds }
  }
  const other = ref.kind === 'pending-debt' ? 'closed-debt.md' : 'pending-debt.md'
  return { otherLedger: (await readText($, `${ref.dir}/${other}`)).text, adrIds }
}

async function headOf($: EngineInterface, cwd: string): Promise<string> {
  try {
    const head = await $.process.run(['git', 'rev-parse', 'HEAD'], { cwd, timeoutMs: 5000 })
    return head.exitCode === 0 ? head.stdout.trim() : ''
  } catch {
    return ''
  }
}

export function register(on: On, options: PluginOptions): void {
  const { commitNudge } = options
  const nudge = commitNudge !== false

  // Format guard: runs before the permission check, so a malformed record never reaches a prompt.
  on('tool.call', { tool: ['Write', 'Edit'] }, async ($, e, next) => {
    const input = fileInput(e)
    const path = input === null ? null : resolvePath(input.path, await $.session.cwd())
    const ref = path === null ? null : classify(path)
    if (input === null || path === null || ref === null) {
      return next(e)
    }
    const { text: current, failed } = await readText($, path)
    if (failed) {
      return {
        deny: `Project Maintainer could not read ${ref.name} to check the edit. Try the edit again.`,
      }
    }
    const resulting = resultingText(input, current)
    if (resulting === null) {
      return next(e)
    }
    const problems = formatProblems(ref, current, resulting, await around($, ref))
    return problems.length > 0 ? { deny: refusal(ref.name, problems) } : next(e)
  }).catch(async (_$, e, next) => {
    // Fail closed for records only: a broken check never blocks a save outside the records.
    if (next.called || !mayWriteRecord(e)) {
      return next(e)
    }
    return {
      deny: 'Project Maintainer could not check this record against its format, so it was not saved. Try the save again, and tell the user if it fails again.',
    }
  })

  // Authority guard: only the person can approve rewriting a settled record.
  on('tool.check', { tool: ['Write', 'Edit'] }, async ($, e, next) => {
    const decided = await next(e)
    const input = decided.decision === 'deny' ? null : fileInput(e.input)
    const path = input === null ? null : resolvePath(input.path, await $.session.cwd())
    const ref = path === null ? null : classify(path)
    if (input === null || path === null || ref === null) {
      return decided
    }
    const { text: current, failed } = await readText($, path)
    if (failed) {
      return {
        decision: 'ask',
        reason: `Project Maintainer could not read ${ref.name} to check the edit against the rules of the records. Approve only if it leaves the records as they are.`,
      }
    }
    const resulting = resultingText(input, current)
    if (current === null || resulting === null) {
      return decided
    }
    const reasons = authorityReasons(ref, current, resulting, await around($, ref))
    return reasons.length > 0 ? { decision: 'ask', reason: askReason(ref.name, reasons) } : decided
  }).catch(async (_$, e, next) => {
    // Any file outside the records keeps the verdict beneath. A record asks, unless that verdict
    // is a deny; if the verdict itself cannot be read, the record still asks.
    if (!mayWriteRecord(e.input)) {
      return next(e)
    }
    const beneath = await next(e).catch(() => null)
    return beneath?.decision === 'deny'
      ? beneath
      : {
          decision: 'ask',
          reason:
            'Project Maintainer could not check this edit against the rules of the records. Approve only if it leaves the records as they are.',
        }
  })

  // The same guard for the shell, as far as a command can be read.
  on('tool.check', { tool: 'Bash' }, async (_$, e, next) => {
    const decided = await next(e)
    const command =
      typeof e.input === 'object' && e.input !== null && 'command' in e.input
        ? e.input.command
        : null
    const reason =
      decided.decision === 'deny' || typeof command !== 'string' ? null : bashReason(command)
    return reason === null ? decided : { decision: 'ask', reason: `Project Maintainer: ${reason}` }
  }).catch(async () => ({
    decision: 'ask',
    reason: 'Project Maintainer could not check this command against the rules of the records.',
  }))

  // A compaction summarizes the conversation; this keeps what the records need out of the loss.
  on('session.compact', async ($, e, next) => {
    if (e.agentId !== undefined || (e.trigger !== 'auto' && e.trigger !== 'manual')) {
      return next(e)
    }
    const root = await $.session.root()
    const hasRecords =
      (await $.fs.exists(`${root}/.claude/maintainer`)) ||
      (await $.fs.exists(`${root}/.claude/session-handoff`))
    return hasRecords ? next({ ...e, instructions: withKeepNote(e.instructions) }) : next(e)
  })

  // After a commit that changes dependencies, schema, CI or infrastructure, or whose message says
  // workaround, temporary or revert, remind Claude that a decision or a debt may be worth recording.
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    if (!nudge || !/\bgit\s+commit\b/.test(e.command)) {
      return next(e)
    }
    const cwd = await $.session.cwd()
    const before = await headOf($, cwd)
    const result = await next(e)
    const after = await headOf($, cwd)
    if (after === '' || after === before) {
      return result
    }
    try {
      const shown = await $.process.run(
        ['git', 'show', '--name-only', '--format=%s', '-1', 'HEAD'],
        { cwd, timeoutMs: 5000 },
      )
      const signals = shown.exitCode === 0 ? commitSignals(shown.stdout) : []
      if (signals.length > 0) {
        await $.session.append({
          message: { type: 'user', content: [{ type: 'text', text: nudgeText(signals) }] },
        })
      }
    } catch {
      // The reminder is a courtesy: the commit result stands whatever happens here.
    }
    return result
  })
}
