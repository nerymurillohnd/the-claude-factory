import type { CommandRunResult, On, TurnCompleteReason, TurnUsage } from 'claude-code'
import type { Engine, Mounted } from 'claude-code/testing'
import { expect, test } from 'claude-code/testing'

const SURFACES = ['terminal', 'desktop'] as const
type Surface = (typeof SURFACES)[number]

const USAGE: TurnUsage = {
  input_tokens: 1200,
  output_tokens: 6300,
  cache_read_input_tokens: 38_000,
  cache_creation_input_tokens: 2000,
  model: 'claude-test',
}

type Sent = { toasts: string[]; notifications: string[] }

// Nothing sits beneath the plugin: these hooks stand for the engine.
const stubEngine = (on: On, isNotifySent = true): Sent => {
  const sent: Sent = { toasts: [], notifications: [] }
  on('session.start', (_$, e) => ({ cwd: e.cwd }))
  on('command.register', (_$, e) => ({ value: { command: e.name } }))
  on('turn.start', (_$, e) => ({ turnId: e.turnId }))
  on('tool.call', () => ({ result: {} }))
  on('turn.complete', () => ({ text: '' }))
  // What the engine draws when the plugin yields the band.
  on('ui.render', ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text>engine</Text>
  })
  on('ui.toast', (_$, e) => {
    sent.toasts.push(e.text)
    return { value: undefined }
  })
  on('ui.notify', (_$, e) => {
    sent.notifications.push(e.text)
    return {
      value: isNotifySent
        ? { isSent: true, channel: 'iterm2' }
        : { isSent: false, reason: 'no-channel' },
    }
  })
  return sent
}

type Turn = {
  durationMs: number
  reason?: TurnCompleteReason
  mainTools?: number
  subagentTools?: number
  usage?: TurnUsage
  subagentUsage?: TurnUsage
}

// One main-loop turn: its tool calls, one subagent's run when it has any, then the end.
const runTurn = async ($: Engine, turn: Turn): Promise<void> => {
  const reason = turn.reason ?? 'answer'
  await $.turn.start({ text: 'go', turnId: 't1' })
  for (let i = 0; i < (turn.mainTools ?? 0); i += 1) {
    await $.tool.call({ tool: 'Bash', command: 'ls' })
  }
  if ((turn.subagentTools ?? 0) > 0 || turn.subagentUsage !== undefined) {
    await $.turn.start({ text: 'look', turnId: 's1', agentId: 'a1' })
    for (let i = 0; i < (turn.subagentTools ?? 0); i += 1) {
      await $.tool.call({ tool: 'Bash', command: 'ls', agentId: 'a1' })
    }
    await $.turn.complete({
      answer: 'found it',
      durationMs: 1000,
      isAborted: false,
      turnId: 's1',
      agentId: 'a1',
      reason: 'answer',
      ...(turn.subagentUsage === undefined ? {} : { usage: turn.subagentUsage }),
    })
  }
  const end = {
    answer: '',
    durationMs: turn.durationMs,
    isAborted: reason === 'aborted',
    turnId: 't1',
    ...(turn.usage === undefined ? {} : { usage: turn.usage }),
  }
  await (reason === 'refusal'
    ? $.turn.complete({ ...end, reason, refusal: { category: null, explanation: null } })
    : $.turn.complete({ ...end, reason }))
}

const mountBand = (
  $: Engine,
  surface: Surface,
  options: { hasSurvey?: boolean; bodyColumns?: number } = {},
): Promise<Mounted<Surface, 'AbovePrompt'>> =>
  $.ui.mount({
    plugin: 'turn-meter',
    surface,
    component: 'AbovePrompt',
    props: {
      hasSurvey: options.hasSurvey ?? false,
      isWorking: false,
      maxRows: 10,
      bodyColumns: options.bodyColumns ?? 120,
      scroll: { offset: 0, bodyRows: 10 },
      view: {},
    },
  })

const bandLine = async ($: Engine, surface: Surface): Promise<string | undefined> => {
  const ui = await mountBand($, surface)
  const line = (await ui.find({ type: 'Text', text: /Last turn|tools|refused/ }))?.text
  await ui.unmount()
  return line
}

// /turn-meter typed at the prompt.
const toggle = ($: Engine): Promise<CommandRunResult> =>
  $.command.run({
    command: 'turn-meter',
    args: '',
    origin: { kind: 'composer' },
    presentation: { isFullscreen: false, columns: 120 },
  })

const start = ($: Engine): Promise<unknown> =>
  $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

test('main-loop and subagent tools add up, and the split is shown', async ($, on) => {
  stubEngine(on)
  await start($)
  await runTurn($, { durationMs: 192_000, mainTools: 3, subagentTools: 2, usage: USAGE })

  for (const surface of SURFACES) {
    expect(await bandLine($, surface)).toBe(
      'Last turn: 3m 12s · 5 tools (2 in 1 subagent) · 41.2k in / 6.3k out',
    )
  }
})

test('subagent tokens are added to the main loop’s', async ($, on) => {
  stubEngine(on)
  await start($)
  await runTurn($, {
    durationMs: 5000,
    mainTools: 1,
    subagentTools: 1,
    usage: USAGE,
    subagentUsage: {
      ...USAGE,
      input_tokens: 0,
      cache_read_input_tokens: 800,
      cache_creation_input_tokens: 0,
      output_tokens: 700,
    },
  })

  expect(await bandLine($, 'terminal')).toBe(
    'Last turn: 5s · 2 tools (1 in 1 subagent) · 42k in / 7k out',
  )
})

test('an interrupted, a failed and a refused turn say how they ended', async ($, on) => {
  stubEngine(on)
  await start($)

  await runTurn($, { durationMs: 65_000, reason: 'aborted', mainTools: 7 })
  expect(await bandLine($, 'terminal')).toBe('Last turn: interrupted after 1m 05s · 7 tools')

  await runTurn($, { durationMs: 40_000, reason: 'error', mainTools: 3 })
  expect(await bandLine($, 'terminal')).toBe('Last turn: ended by API error after 40s · 3 tools')

  await runTurn($, { durationMs: 12_000, reason: 'refusal' })
  expect(await bandLine($, 'terminal')).toBe('Last turn: refused after 12s')
})

test(
  'a long turn alerts as the alert option says',
  { options: { alert: 'notify', alertAfterSeconds: 60 } },
  async ($, on) => {
    const sent = stubEngine(on)
    await start($)

    await runTurn($, { durationMs: 30_000 })
    expect(sent.notifications).toEqual([])

    await runTurn($, { durationMs: 192_000 })
    expect(sent.notifications).toEqual(['That turn took 3m 12s'])
    expect(sent.toasts).toEqual([])

    // Esc means the person is watching: no alert.
    await runTurn($, { durationMs: 192_000, reason: 'aborted' })
    expect(sent.notifications).toHaveLength(1)
  },
)

test(
  'alert off sends nothing',
  { options: { alert: 'off', alertAfterSeconds: 1 } },
  async ($, on) => {
    const sent = stubEngine(on)
    await start($)
    await runTurn($, { durationMs: 192_000 })

    expect(sent.notifications).toEqual([])
    expect(sent.toasts).toEqual([])
  },
)

test(
  'a notification nobody can receive falls back to a toast',
  { options: { alert: 'notify', alertAfterSeconds: 60 } },
  async ($, on) => {
    const sent = stubEngine(on, false)
    await start($)
    await runTurn($, { durationMs: 192_000 })

    expect(sent.notifications).toEqual(['That turn took 3m 12s'])
    expect(sent.toasts).toEqual(['That turn took 3m 12s'])
  },
)

test('Hide and /turn-meter toggle the band', async ($, on) => {
  stubEngine(on)
  await start($)
  await runTurn($, { durationMs: 5000, mainTools: 1 })

  for (const surface of SURFACES) {
    const ui = await mountBand($, surface)
    expect((await ui.find({ type: 'Text', text: /Last turn/ }))?.text).toBe(
      'Last turn: 5s · 1 tool',
    )

    await ui.press({ key: 'hide' })
    expect(await ui.find({ type: 'Text', text: /Last turn/ })).toBeUndefined()

    const shown = await toggle($)
    expect(shown.text).toBe('Turn Meter band shown.')
    expect((await ui.find({ type: 'Text', text: /Last turn/ }))?.text).toBe(
      'Last turn: 5s · 1 tool',
    )

    const hidden = await toggle($)
    expect(hidden.text).toMatch(/hidden/)
    expect(await ui.find({ type: 'Text', text: /Last turn/ })).toBeUndefined()

    await toggle($)
    await ui.unmount()
  }
})

test('the band yields to a survey and waits for the first turn', async ($, on) => {
  stubEngine(on)
  await start($)

  const before = await mountBand($, 'terminal')
  expect(await before.find({ type: 'Text', text: /Last turn/ })).toBeUndefined()
  await before.unmount()

  await runTurn($, { durationMs: 5000 })
  for (const surface of SURFACES) {
    const ui = await mountBand($, surface, { hasSurvey: true })
    expect(await ui.find({ type: 'Text', text: /Last turn/ })).toBeUndefined()
    expect((await ui.find({ type: 'Text', text: /engine/ }))?.text).toBe('engine')
    await ui.unmount()
  }
})

test('the band keeps what the mods after it draw', async ($, on) => {
  stubEngine(on)
  await start($)
  await runTurn($, { durationMs: 5000 })

  for (const surface of SURFACES) {
    const ui = await mountBand($, surface)
    expect((await ui.find({ type: 'Text', text: /Last turn/ }))?.text).toBe(
      'Last turn: 5s · 0 tools',
    )
    expect((await ui.find({ type: 'Text', text: /engine/ }))?.text).toBe('engine')
    await ui.unmount()
  }
})

test('tokens switch to millions once they round to a thousand thousands', async ($, on) => {
  stubEngine(on)
  await start($)
  await runTurn($, {
    durationMs: 5000,
    usage: {
      ...USAGE,
      input_tokens: 999_999,
      cache_read_input_tokens: 0,
      cache_creation_input_tokens: 0,
      output_tokens: 999_960,
    },
  })

  expect(await bandLine($, 'terminal')).toBe('Last turn: 5s · 0 tools · 1M in / 1M out')
})

test('a narrow band shows the short form', async ($, on) => {
  stubEngine(on)
  await start($)
  await runTurn($, { durationMs: 192_000, mainTools: 22, subagentTools: 2, usage: USAGE })

  for (const surface of SURFACES) {
    const ui = await mountBand($, surface, { bodyColumns: 50 })
    expect((await ui.find({ type: 'Text', text: /tools/ }))?.text).toBe(
      '3m12s · 24 tools · 48k tok',
    )
    await ui.unmount()
  }
})

test('showTokens off leaves the tokens out', { options: { showTokens: false } }, async ($, on) => {
  stubEngine(on)
  await start($)
  await runTurn($, { durationMs: 192_000, mainTools: 3, usage: USAGE })

  expect(await bandLine($, 'terminal')).toBe('Last turn: 3m 12s · 3 tools')
})
