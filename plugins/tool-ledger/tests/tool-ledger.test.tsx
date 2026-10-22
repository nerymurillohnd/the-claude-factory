import type { On } from 'claude-code'
import type { Engine, Mounted } from 'claude-code/testing'
import { expect, test } from 'claude-code/testing'

const SURFACES = ['terminal', 'desktop'] as const
type Surface = (typeof SURFACES)[number]

type Engine$ = { toolRuns: number; opened: string[] }

// Nothing sits beneath the plugin: these hooks stand for the engine. The clock moves
// 100 ms on every read, so a call that reads it twice lasts 0.1s.
const stubEngine = (on: On): Engine$ => {
  const seen: Engine$ = { toolRuns: 0, opened: [] }
  let now = 0
  on('session.start', (_$, e) => ({ cwd: e.cwd }))
  on('command.register', (_$, e) => ({ value: { command: e.name } }))
  on('clock.now', () => {
    now += 100
    return { value: now }
  })
  on('agent.list', () => ({
    value: [
      { id: 'a1', description: 'Find pricing references', type: 'Explore', status: 'running' },
    ],
  }))
  on('ui.open', (_$, e) => {
    seen.opened.push(e.id)
    return { value: { isPlaced: true } }
  })
  on('tool.call', (_$, e) => {
    seen.toolRuns += 1
    return e.tool === 'Bash' && e.command === 'false'
      ? { isError: true, result: 'exit 1', text: 'exit 1' }
      : { result: { ok: e.tool } }
  })
  // What the engine draws where the plugin yields.
  on('ui.render', ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text>engine</Text>
  })
  return seen
}

const start = ($: Engine): Promise<unknown> =>
  $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })

const mountPane = ($: Engine, surface: Surface, bodyRows = 20): Promise<Mounted<Surface, 'Pane'>> =>
  $.ui.mount({
    plugin: 'tool-ledger',
    surface,
    component: 'Pane',
    requestId: 'tool-ledger',
    props: {
      title: 'Tool calls',
      isFocused: false,
      bodyColumns: 70,
      placement: 'dock',
      scroll: { offset: 0, bodyRows },
      view: {},
    },
  })

const textOf = async (ui: Mounted<Surface, 'Pane'>, pattern: RegExp): Promise<string | undefined> =>
  (await ui.find({ type: 'Text', text: pattern }))?.text

test('a call goes from runs to done with its duration', async ($, on) => {
  stubEngine(on)
  await start($)
  const result = await $.tool.call({ tool: 'Read', file_path: '/work/src/lib/catalog.ts' })
  expect(result).toMatchObject({ result: { ok: 'Read' } })

  for (const surface of SURFACES) {
    const ui = await mountPane($, surface)
    expect(await textOf(ui, /catalog/)).toMatch(/^done\s+Read\s+src\/lib\/catalog\.ts\s+0\.1s$/)
    expect(await textOf(ui, /^Tool calls/)).toBe('Tool calls · 1')
    await ui.unmount()
  }
})

test('a deny from a hook beneath shows as denied and reaches the engine intact', async ($, on) => {
  on('tool.call', { tool: 'Write' }, () => ({ deny: 'writes are off' }))
  stubEngine(on)
  await start($)

  const result = await $.tool.call({ tool: 'Write', file_path: '/work/out.txt', content: 'x' })
  expect(result).toEqual({ deny: 'writes are off' })

  const ui = await mountPane($, 'terminal')
  expect(await textOf(ui, /out\.txt/)).toMatch(/^denied\s+Write\s+out\.txt$/)
  await ui.unmount()
})

test('a settings PreToolUse deny, which reaches tool.call as an error, shows as denied', async ($, on) => {
  stubEngine(on)
  on('classic.PreToolUse', () => ({ deny: 'secret file' }))
  await start($)

  const result = await $.tool.call({ tool: 'Read', file_path: '/work/.env', tool_use_id: 'u1' })
  expect(result).toMatchObject({ isError: true })

  const ui = await mountPane($, 'terminal')
  expect(await textOf(ui, /\.env/)).toMatch(/^denied\s+Read\s+\.env$/)
  expect(await textOf(ui, /^Tool calls/)).toBe('Tool calls · 1 · 1 denied')
  await ui.unmount()
})

test('a failed error result shows as error', async ($, on) => {
  stubEngine(on)
  await start($)
  await $.tool.call({ tool: 'Bash', command: 'false' })

  const ui = await mountPane($, 'terminal')
  expect(await textOf(ui, /false/)).toMatch(/^error\s+Bash\s+false\s+0\.1s$/)
  await ui.unmount()
})

for (const failing of ['before', 'after'] as const) {
  test(`a ledger that fails ${failing} the call runs the tool once with its own result`, async ($, on) => {
    let writes = 0
    // The first write opens the row, the second closes it.
    on('state.set', (_$, e, next) => {
      writes += 1
      return (failing === 'before') === (writes === 1) ? { deny: 'state is unavailable' } : next(e)
    })
    const seen = stubEngine(on)
    await start($)

    const result = await $.tool.call({ tool: 'Read', file_path: '/work/a.ts' })
    expect(seen.toolRuns).toBe(1)
    expect(result).toMatchObject({ result: { ok: 'Read' } })
  })
}

test('a subagent’s calls are grouped under its description', async ($, on) => {
  stubEngine(on)
  await start($)
  await $.tool.call({
    tool: 'Agent',
    description: 'Find pricing references',
    prompt: 'go',
    subagent_type: 'Explore',
  })
  await $.tool.call({ tool: 'mcp__docs__search', query: 'FOB price', agentId: 'a1' })
  await $.tool.call({ tool: 'Bash', command: 'ls' })
  await $.tool.call({ tool: 'Read', file_path: '/work/docs/pricing.md', agentId: 'a1' })

  for (const surface of SURFACES) {
    const ui = await mountPane($, surface)
    expect(await textOf(ui, /▸/)).toBe('▸ Explore · "Find pricing references"')
    expect(await textOf(ui, /docs › search/)).toMatch(/^ {2}done\s+MCP\s+docs › search/)
    expect(await textOf(ui, /pricing\.md/)).toMatch(/^ {2}done\s+Read\s+docs\/pricing\.md/)
    expect(await textOf(ui, /\bls\b/)).toMatch(/^done\s+Bash\s+ls/)
    await ui.unmount()
  }
})

test('Errors only filters the rows', async ($, on) => {
  on('tool.call', { tool: 'Write' }, () => ({ deny: 'no' }))
  stubEngine(on)
  await start($)
  await $.tool.call({ tool: 'Read', file_path: '/work/ok.ts' })
  await $.tool.call({ tool: 'Bash', command: 'false' })
  await $.tool.call({ tool: 'Write', file_path: '/work/no.txt', content: 'x' })

  for (const surface of SURFACES) {
    const ui = await mountPane($, surface)
    await ui.press({ key: 'errors-only' })
    expect(await textOf(ui, /ok\.ts/)).toBeUndefined()
    expect(await textOf(ui, /false/)).toMatch(/^error/)
    expect(await textOf(ui, /no\.txt/)).toMatch(/^denied/)
    await ui.press({ key: 'errors-only' })
    expect(await textOf(ui, /ok\.ts/)).toMatch(/^done/)
    await ui.unmount()
  }
})

test(
  'showTargets off hides what each call acted on',
  { options: { showTargets: false } },
  async ($, on) => {
    stubEngine(on)
    await start($)
    await $.tool.call({ tool: 'Read', file_path: '/work/secret-plan.md' })
    await $.tool.call({ tool: 'mcp__docs__search', query: 'FOB price', agentId: 'a1' })

    const ui = await mountPane($, 'terminal')
    expect(await textOf(ui, /secret-plan|docs|pricing/)).toBeUndefined()
    expect(await textOf(ui, /^done\s+Read/)).toMatch(/^done\s+Read\s+0\.1s$/)
    expect(await textOf(ui, /▸/)).toBe('▸ Explore')
    await ui.unmount()
  },
)

test('past maxRows the latest calls are kept', { options: { maxRows: 10 } }, async ($, on) => {
  stubEngine(on)
  await start($)
  for (let i = 1; i <= 12; i += 1) {
    await $.tool.call({ tool: 'Bash', command: `echo call-${i}` })
  }

  const ui = await mountPane($, 'terminal', 30)
  expect(await textOf(ui, /^Tool calls/)).toBe('Tool calls · 10')
  expect(await textOf(ui, /call-2$/)).toBeUndefined()
  expect(await textOf(ui, /call-3\b/)).toMatch(/call-3/)
  expect(await textOf(ui, /call-12/)).toMatch(/call-12/)
  await ui.unmount()
})

test(
  '/tool-ledger opens the panel; sidebar opens it alone only in fullscreen',
  { options: { autoOpen: 'sidebar' } },
  async ($, on) => {
    const seen = stubEngine(on)
    await start($)

    const band = (isFullscreen: boolean): Promise<Mounted<'terminal', 'AbovePrompt'>> =>
      $.ui.mount({
        plugin: 'tool-ledger',
        surface: 'terminal',
        component: 'AbovePrompt',
        viewport: { columns: 150, rows: 40, isFullscreen },
        props: {
          hasSurvey: false,
          isWorking: false,
          maxRows: 10,
          bodyColumns: 145,
          scroll: { offset: 0, bodyRows: 10 },
          view: {},
        },
      })

    const mainScreen = await band(false)
    expect(seen.opened).toEqual([])
    await mainScreen.unmount()

    const fullscreen = await band(true)
    expect(seen.opened).toEqual(['tool-ledger'])
    await fullscreen.unmount()

    const reply = await $.command.run({
      command: 'tool-ledger',
      args: '',
      origin: { kind: 'composer' },
      presentation: { isFullscreen: true, columns: 150 },
    })
    expect(reply.text).toBe('Tool Ledger opened.')
    expect(seen.opened).toEqual(['tool-ledger', 'tool-ledger'])
  },
)
