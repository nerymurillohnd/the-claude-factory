import type { On, PluginOptions, Register, TurnUsage } from 'claude-code'
import { atom, read, update } from 'claude-code'

import type { TurnSummary } from '../types'

type Alert = 'toast' | 'notify' | 'off'

type Settings = {
  alert: Alert
  alertAfterMs: number
  showTokens: boolean
}

const COMMAND = 'turn-meter'
const NARROW_COLUMNS = 60

const last = atom({ plugin: 'turn-meter', key: 'last' } as const, null)
const isHidden = atom({ plugin: 'turn-meter', key: 'isHidden' } as const, false)

// The engine fills in the manifest's defaults; these only cover a value of the wrong type.
const readSettings = (options: PluginOptions): Settings => {
  const { alert, alertAfterSeconds, showTokens } = options
  const seconds =
    typeof alertAfterSeconds === 'number' && alertAfterSeconds > 0 ? alertAfterSeconds : 120

  return {
    alert: alert === 'notify' || alert === 'off' ? alert : 'toast',
    alertAfterMs: seconds * 1000,
    showTokens: typeof showTokens === 'boolean' ? showTokens : true,
  }
}

const tokensIn = (usage: TurnUsage | undefined): number =>
  usage === undefined
    ? 0
    : usage.input_tokens + usage.cache_read_input_tokens + usage.cache_creation_input_tokens

// "3m 12s", "1m 05s" and "40s"; the short form drops the space: "3m12s".
export const formatDuration = (ms: number, isShort = false): string => {
  const total = Math.round(ms / 1000)
  const minutes = Math.floor(total / 60)
  const seconds = total % 60

  if (minutes === 0) {
    return `${seconds}s`
  }

  return `${minutes}m${isShort ? '' : ' '}${String(seconds).padStart(2, '0')}s`
}

// A trailing ".0" left by toFixed(1): "6.0k" reads "6k".
const TRAILING_ZERO_DECIMAL = /\.0$/

// "6.3k" and "41.2k"; the short form rounds to whole thousands: "47k". The unit is picked after
// rounding, so 999,999 reads "1M", never "1000k".
export const formatTokens = (count: number, isShort = false): string => {
  const thousands = isShort ? String(Math.round(count / 1000)) : (count / 1000).toFixed(1)

  if (count >= 1000 && Number(thousands) < 1000) {
    return `${thousands.replace(TRAILING_ZERO_DECIMAL, '')}k`
  }

  if (count >= 1000) {
    return `${(count / 1_000_000).toFixed(1).replace(TRAILING_ZERO_DECIMAL, '')}M`
  }

  return String(count)
}

const plural = (count: number, word: string): string => `${count} ${word}${count === 1 ? '' : 's'}`

const LEAD: Record<TurnSummary['reason'], string> = {
  answer: '',
  aborted: 'interrupted after ',
  error: 'ended by API error after ',
  refusal: 'refused after ',
}

const SHORT_LEAD: Record<TurnSummary['reason'], string> = {
  answer: '',
  aborted: 'interrupted ',
  error: 'API error ',
  refusal: 'refused ',
}

export const bandText = (turn: TurnSummary, showTokens: boolean, columns: number): string => {
  const isShort = columns < NARROW_COLUMNS
  const parts = [
    `${(isShort ? SHORT_LEAD : LEAD)[turn.reason]}${formatDuration(turn.durationMs, isShort)}`,
  ]

  if (turn.reason !== 'refusal') {
    const tools = plural(turn.tools + turn.subagentTools, 'tool')
    const split =
      isShort || turn.subagents === 0
        ? ''
        : ` (${turn.subagentTools} in ${plural(turn.subagents, 'subagent')})`
    parts.push(`${tools}${split}`)
  }

  if (showTokens && turn.tokensIn + turn.tokensOut > 0) {
    parts.push(
      isShort
        ? `${formatTokens(turn.tokensIn + turn.tokensOut, true)} tok`
        : `${formatTokens(turn.tokensIn)} in / ${formatTokens(turn.tokensOut)} out`,
    )
  }

  return `${isShort ? '' : 'Last turn: '}${parts.join(' · ')}`
}

export const register: Register = (on: On, options: PluginOptions): void => {
  const settings = readSettings(options)

  // The turn in progress. A reload in the middle of a turn starts these over,
  // so that one turn comes out short; the last finished turn lives in $.state.
  let tools = 0
  let subagentTools = 0
  let subagentIds = new Set<string>()
  let subagentTokensIn = 0
  let subagentTokensOut = 0

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: COMMAND,
      description: 'Show or hide the last-turn band above the prompt',
    })

    return next(e)
  })

  on('turn.start', (_$, e, next) => {
    if (e.agentId === undefined) {
      tools = 0
      subagentTools = 0
      subagentIds = new Set()
      subagentTokensIn = 0
      subagentTokensOut = 0
    }

    return next(e)
  })

  on('tool.call', (_$, e, next) => {
    if (e.agentId === undefined) {
      tools += 1
    } else {
      subagentTools += 1
      subagentIds.add(e.agentId)
    }

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    if (e.agentId !== undefined) {
      subagentIds.add(e.agentId)
      subagentTokensIn += tokensIn(e.usage)
      subagentTokensOut += e.usage?.output_tokens ?? 0

      return next(e)
    }

    const turn: TurnSummary = {
      durationMs: e.durationMs,
      reason: e.reason,
      tools,
      subagentTools,
      subagents: subagentIds.size,
      tokensIn: tokensIn(e.usage) + subagentTokensIn,
      tokensOut: (e.usage?.output_tokens ?? 0) + subagentTokensOut,
    }
    await update($, last, () => turn)

    // An interrupted turn needs no alert: the person pressed Esc and is watching.
    const isLong = turn.durationMs >= settings.alertAfterMs && turn.reason !== 'aborted'
    if (isLong && settings.alert !== 'off') {
      const text = `That turn took ${formatDuration(turn.durationMs)}`
      // A notification nobody can receive (no terminal channel, the desktop app)
      // falls back to a toast, so the alert is never lost.
      const isSent =
        settings.alert === 'notify' &&
        (await $.ui.notify(text).then(
          (sent) => sent.isSent,
          () => false,
        ))
      if (!isSent) {
        $.ui.toast(text)
      }
    }

    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const turn = await read($, last)

    if (e.props.hasSurvey || turn === null || (await read($, isHidden))) {
      return next(e)
    }

    const { Box, Button, Text } = $.ui.resolve(e)
    // The band is shared: what the mods after this one draw stays beneath the row.
    const below = await next(e)

    return (
      <Box flexDirection="column">
        <Box flexDirection="row" gap={1}>
          <Text dimColor={true}>{bandText(turn, settings.showTokens, e.props.bodyColumns)}</Text>
          <Button
            key="hide"
            label="Hide"
            onPress={(): Promise<boolean> => update($, isHidden, () => true)}
          />
        </Box>
        {below}
      </Box>
    )
  })

  on('command.run', { command: COMMAND }, async ($) => {
    const hidden = await update($, isHidden, (value) => !value)
    const hasTurn = (await read($, last)) !== null

    if (hidden) {
      return { text: 'Turn Meter band hidden. Run /turn-meter to show it again.' }
    }

    return {
      text: hasTurn
        ? 'Turn Meter band shown.'
        : 'Turn Meter band shown. It appears after the first turn ends.',
    }
  })
}
