// Project Maintainer's guardrails. Every call on `$` lives in this file; the rules themselves are
// pure functions in the sibling modules, so the tests can run them without an engine.
//
// - Format guard: refuses to save a malformed ADR or debt ledger. Nobody can waive it.
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
  nudgeText,
  refusal,
  resultingText,
  type Surroundings,
  withKeepNote,
} from './guard.ts'
import { ADR_NAME, adrId, classify, type RecordRef } from './paths.ts'

async function readText($: EngineInterface, path: string): Promise<string | null> {
  try {
    return await $.fs.read(path)
  } catch {
    return null
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
  return { otherLedger: await readText($, `${ref.dir}/${other}`), adrIds }
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
    const ref = input === null ? null : classify(input.path)
    if (input === null || ref === null) {
      return next(e)
    }
    const current = await readText($, input.path)
    const resulting = resultingText(input, current)
    if (resulting === null) {
      return next(e)
    }
    const problems = formatProblems(ref, current, resulting, await around($, ref))
    return problems.length > 0 ? { deny: refusal(ref.name, problems) } : next(e)
  }).catch(async ($, e, next) => {
    $.ui.log('Project Maintainer could not check this record, so it was saved unchecked.')
    return next(e)
  })

  // Authority guard: only the person can approve rewriting a settled record.
  on('tool.check', { tool: ['Write', 'Edit'] }, async ($, e, next) => {
    const decided = await next(e)
    const input = fileInput(e.input)
    const ref = input === null || decided.decision === 'deny' ? null : classify(input.path)
    if (input === null || ref === null) {
      return decided
    }
    const current = await readText($, input.path)
    const resulting = resultingText(input, current)
    if (current === null || resulting === null) {
      return decided
    }
    const reasons = authorityReasons(ref, current, resulting, await around($, ref))
    return reasons.length > 0
      ? { decision: 'ask', decider: 'person', reason: askReason(ref.name, reasons) }
      : decided
  }).catch(async () => ({
    decision: 'ask',
    decider: 'person',
    reason:
      'Project Maintainer could not check this edit against the rules of the records. Approve only if it leaves the records as they are.',
  }))

  // The same guard for the shell, as far as a command can be read.
  on('tool.check', { tool: 'Bash' }, async (_$, e, next) => {
    const decided = await next(e)
    const command =
      typeof e.input === 'object' && e.input !== null && 'command' in e.input
        ? e.input.command
        : null
    const reason =
      decided.decision === 'deny' || typeof command !== 'string' ? null : bashReason(command)
    return reason === null
      ? decided
      : { decision: 'ask', decider: 'person', reason: `Project Maintainer: ${reason}` }
  }).catch(async () => ({
    decision: 'ask',
    decider: 'person',
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
