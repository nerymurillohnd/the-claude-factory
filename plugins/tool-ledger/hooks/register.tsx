import type { On, PluginOptions, Register } from 'claude-code'
import { atom, read, update } from 'claude-code'

import type { LedgerRow, LedgerStatus } from '../types'

type Settings = {
  autoOpen: 'never' | 'sidebar'
  showTargets: boolean
  maxRows: number
}

type Line = { key: string; text: string; status: LedgerStatus | null; header: Line | null }

const COMMAND = 'tool-ledger'
const PANE = 'tool-ledger'
const TITLE = 'Tool calls'
const COMMAND_CHARS = 60

const rowsAtom = atom({ plugin: 'tool-ledger', key: 'rows' } as const, [])
const agentsAtom = atom({ plugin: 'tool-ledger', key: 'agents' } as const, {})
const errorsOnlyAtom = atom({ plugin: 'tool-ledger', key: 'isErrorsOnly' } as const, false)
const autoOpenedAtom = atom({ plugin: 'tool-ledger', key: 'isAutoOpened' } as const, false)

// The engine fills in the manifest's defaults; these only cover a value of the wrong type.
const readSettings = (options: PluginOptions): Settings => {
  const { autoOpen, showTargets, maxRows } = options
  return {
    autoOpen: autoOpen === 'sidebar' ? 'sidebar' : 'never',
    showTargets: typeof showTargets === 'boolean' ? showTargets : true,
    maxRows: typeof maxRows === 'number' && maxRows >= 1 ? Math.floor(maxRows) : 500,
  }
}

const stringField = (input: object, key: string): string | undefined => {
  const value: unknown = Reflect.get(input, key)
  return typeof value === 'string' ? value : undefined
}

const relativeTo = (path: string, cwd: string): string => {
  const base = cwd.endsWith('/') ? cwd : `${cwd}/`
  return cwd !== '' && path.startsWith(base) ? path.slice(base.length) : path
}

// What a call acted on: a command, a path, a pattern, a task, or an MCP server and tool.
export const targetOf = (input: object & { tool: string }, cwd: string): string | null => {
  const { tool } = input
  if (tool.startsWith('mcp__')) {
    const [, server, ...name] = tool.split('__')
    return `${server ?? ''} › ${name.join('__')}`
  }
  switch (tool) {
    case 'Bash': {
      const command = stringField(input, 'command')
      return command === undefined ? null : command.replace(/\s+/g, ' ').slice(0, COMMAND_CHARS)
    }
    case 'Read':
    case 'Edit':
    case 'Write': {
      const path = stringField(input, 'file_path')
      return path === undefined ? null : relativeTo(path, cwd)
    }
    case 'Grep':
    case 'Glob':
      return stringField(input, 'pattern') ?? null
    case 'Agent':
      return stringField(input, 'description') ?? null
    default:
      return null
  }
}

// "0.1s" and "14.2s" under a minute, then "2m 05s"; seconds are rounded before the minutes are
// taken, so 119.6 s reads "2m 00s", never "1m 60s".
export const formatDuration = (ms: number): string => {
  const tenths = Math.round(ms / 100)
  if (tenths < 600) {
    return `${(tenths / 10).toFixed(1)}s`
  }
  const seconds = Math.round(ms / 1000)
  return `${Math.floor(seconds / 60)}m ${String(seconds % 60).padStart(2, '0')}s`
}

const clip = (text: string, width: number): string =>
  text.length <= width ? text : `${text.slice(0, Math.max(0, width - 1))}…`

const rowText = (row: LedgerRow, showTargets: boolean, columns: number, indent: number): string => {
  const name = row.tool.startsWith('mcp__') ? 'MCP' : row.tool
  const head = `${' '.repeat(indent)}${row.status.padEnd(6)} ${clip(name, 8).padEnd(8)} `
  const duration = row.durationMs === null ? '' : ` ${formatDuration(row.durationMs)}`
  const room = columns - head.length - duration.length
  const target =
    showTargets && row.target !== null ? clip(row.target, room).padEnd(room) : ''.padEnd(room)
  return `${head}${target}${duration}`.trimEnd()
}

type Entry = { row: LedgerRow } | { agentId: string; rows: LedgerRow[] }

// Main-thread calls in order, and each subagent's calls as one entry placed where that subagent
// first appeared.
const groupByAgent = (shown: readonly LedgerRow[]): Entry[] => {
  const entries: Entry[] = []
  const groups = new Map<string, LedgerRow[]>()
  for (const row of shown) {
    if (row.agentId === null) {
      entries.push({ row })
      continue
    }
    const group = groups.get(row.agentId)
    if (group === undefined) {
      const fresh = [row]
      groups.set(row.agentId, fresh)
      entries.push({ agentId: row.agentId, rows: fresh })
    } else {
      group.push(row)
    }
  }
  return entries
}

// One entry's lines: a main-thread row, or a subagent's header followed by its indented rows.
const entryLines = (
  entry: Entry,
  agents: Readonly<Record<string, string>>,
  showTargets: boolean,
  columns: number,
): Line[] => {
  if ('row' in entry) {
    return [
      {
        key: entry.row.id,
        text: rowText(entry.row, showTargets, columns, 0),
        status: entry.row.status,
        header: null,
      },
    ]
  }
  const label = agents[entry.agentId] ?? entry.agentId
  // Without targets, keep only the subagent's type: its description can say as much as a target.
  const header = showTargets ? label : (label.split(' · ')[0] ?? label)
  const headerLine: Line = {
    key: `agent-${entry.agentId}`,
    text: clip(`▸ ${header}`, columns),
    status: null,
    header: null,
  }
  return [
    headerLine,
    ...entry.rows.map((row) => ({
      key: row.id,
      text: rowText(row, showTargets, columns, 2),
      status: row.status,
      header: headerLine,
    })),
  ]
}

// The panel's lines: main-thread calls in order, each subagent's calls grouped under one
// header placed where that subagent first appeared, then the last ones that fit.
export const layout = (
  rows: readonly LedgerRow[],
  agents: Readonly<Record<string, string>>,
  isErrorsOnly: boolean,
  showTargets: boolean,
  columns: number,
  room: number,
): Line[] => {
  const shown = isErrorsOnly
    ? rows.filter((r) => r.status === 'error' || r.status === 'denied')
    : rows
  const lines = groupByAgent(shown).flatMap((entry) =>
    entryLines(entry, agents, showTargets, columns),
  )
  const kept = lines.slice(-Math.max(1, room))
  // A subagent's rows never show without its header: it takes the place of the oldest kept row.
  const first = kept[0]
  if (first?.header != null) {
    kept[0] = first.header
  }
  return kept
}

export const summary = (rows: readonly LedgerRow[]): string => {
  const count = (status: LedgerStatus): number => rows.filter((r) => r.status === status).length
  const parts = [`${TITLE} · ${rows.length}`]
  const running = count('runs')
  const errors = count('error')
  const denied = count('denied')
  if (running > 0) {
    parts.push(`${running} running`)
  }
  if (errors > 0) {
    parts.push(`${errors} error${errors === 1 ? '' : 's'}`)
  }
  if (denied > 0) {
    parts.push(`${denied} denied`)
  }
  return parts.join(' · ')
}

// A deny seen beneath counts only when the call did not run: a mod above this one can still
// allow it.
const finalStatus = (
  result: { deny?: unknown; isError?: boolean | undefined },
  wasDeniedBeneath: boolean,
): LedgerStatus => {
  if (result.deny !== undefined || (wasDeniedBeneath && result.isError === true)) {
    return 'denied'
  }
  return result.isError === true ? 'error' : 'done'
}

const COLOR: Record<LedgerStatus, 'green' | 'red' | 'yellow' | undefined> = {
  runs: undefined,
  done: 'green',
  error: 'red',
  denied: 'yellow',
}

const colorOf = (status: LedgerStatus | null): { color?: 'green' | 'red' | 'yellow' } => {
  const color = status === null ? undefined : COLOR[status]
  return color === undefined ? {} : { color }
}

export const register: Register = (on: On, options: PluginOptions): void => {
  const settings = readSettings(options)
  let cwd = ''
  let calls = 0
  // tool_use_ids a settings PreToolUse hook or the permission check denied. Their deny
  // reaches tool.call as an errored result, so the ledger learns of it here.
  const deniedIds = new Set<string>()
  // Set when autoOpen opened the panel; saved to $.state by the next tool call.
  let isAutoOpened = false
  let isAutoOpenSaved = false

  // The ledger is best-effort: a failure here is dropped so it can never touch the call.
  const quietly = async <T,>(work: () => Promise<T>): Promise<T | undefined> => {
    try {
      return await work()
    } catch {
      return undefined
    }
  }

  on('session.start', async ($, e, next) => {
    cwd = e.cwd
    await quietly(() =>
      $.command.register({
        name: COMMAND,
        description: 'Open the panel that lists every tool call',
      }),
    )
    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    calls += 1
    const id = e.tool_use_id ?? `call-${calls}`
    const agentId = e.agentId ?? null
    const startedAt = (await quietly(() => $.clock.now())) ?? null
    if (isAutoOpened && !isAutoOpenSaved) {
      isAutoOpenSaved = (await quietly(() => update($, autoOpenedAtom, () => true))) === true
    }

    await quietly(async () => {
      if (agentId !== null && !(agentId in (await read($, agentsAtom)))) {
        const info = (await $.agent.list()).find((agent) => agent.id === agentId)
        if (info !== undefined) {
          await update($, agentsAtom, (agents) => ({
            ...agents,
            [agentId]: `${info.type} · "${info.description}"`,
          }))
        }
      }
    })
    const row: LedgerRow = {
      id,
      tool: e.tool,
      target: targetOf(e, cwd),
      agentId,
      status: 'runs',
      startedAt: startedAt ?? 0,
      durationMs: null,
    }
    await quietly(() => update($, rowsAtom, (rows) => [...rows, row].slice(-settings.maxRows)))

    // Always awaited: returning while next(e) is pending would abort the call.
    const result = await next(e)

    const status = finalStatus(result, deniedIds.delete(id))
    const endedAt = startedAt === null ? undefined : await quietly(() => $.clock.now())
    const durationMs =
      startedAt === null || endedAt === undefined || status === 'denied'
        ? null
        : endedAt - startedAt
    await quietly(() =>
      update($, rowsAtom, (rows) =>
        rows.map((r) => (r.id === id ? { ...r, status, durationMs } : r)),
      ),
    )

    return result
  }).catch((_$, e, next) => next(e))
  // Replay-safe: when the hook already called next, this returns that call's result without
  // running the tool again; when it had not, it runs the tool once.

  on('classic.PreToolUse', async (_$, e, next) => {
    const decision = await next(e)
    if (decision.deny !== undefined && e.tool_use_id !== undefined) {
      deniedIds.add(e.tool_use_id)
    }
    return decision
  }).catch((_$, e, next) => next(e))

  on('tool.check', async (_$, e, next) => {
    const verdict = await next(e)
    if (verdict.decision === 'deny' && e.tool_use_id !== undefined) {
      deniedIds.add(e.tool_use_id)
    }
    return verdict
  }).catch((_$, e, next) => next(e))

  on('command.run', { command: COMMAND }, async ($) => {
    const opened = await quietly(() => $.ui.open({ id: PANE, title: TITLE }))
    if (opened === undefined) {
      return { text: 'Tool Ledger could not open its panel.' }
    }
    return {
      text: opened.isPlaced
        ? 'Tool Ledger opened.'
        : `Tool Ledger is open but not shown yet: ${opened.reason}`,
    }
  }).catch(() => ({ text: 'Tool Ledger could not open its panel.' }))

  // The band above the prompt is the first place a surface says whether it docks panes.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (settings.autoOpen === 'sidebar' && !isAutoOpened && e.viewport?.isFullscreen === true) {
      // Once per session. A draw may read $.state but not write it, so the flag is saved by the
      // next tool call, and a reload after that doesn't reopen a panel the user closed.
      if ((await quietly(() => read($, autoOpenedAtom))) !== true) {
        isAutoOpened = true
        await quietly(() => $.ui.open({ id: PANE, title: TITLE }))
      }
    }
    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const rows = await read($, rowsAtom)
    const agents = await read($, agentsAtom)
    const isErrorsOnly = await read($, errorsOnlyAtom)
    const { Box, Button, Text } = $.ui.resolve(e)
    const lines = layout(
      rows,
      agents,
      isErrorsOnly,
      settings.showTargets,
      e.props.bodyColumns,
      e.props.scroll.bodyRows - 2,
    )

    return (
      <Box flexDirection="column">
        <Box flexDirection="row" gap={1}>
          <Text weight="bold">{summary(rows)}</Text>
          <Button
            key="errors-only"
            label={isErrorsOnly ? 'All calls' : 'Errors only'}
            onPress={(): Promise<boolean> => update($, errorsOnlyAtom, (value) => !value)}
          />
        </Box>
        {lines.length === 0 ? (
          <Text dimColor={true}>
            {isErrorsOnly ? 'No errors or denied calls.' : 'No tool calls yet.'}
          </Text>
        ) : (
          lines.map((line) => (
            <Text
              key={line.key}
              wrap="truncate"
              dimColor={line.status === null}
              {...colorOf(line.status)}
            >
              {line.text}
            </Text>
          ))
        )}
      </Box>
    )
  })
}
