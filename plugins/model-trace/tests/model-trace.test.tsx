import type { On } from 'claude-code'
import { describe, expect, mock, test } from 'claude-code/testing'

import { sectionLabel, summarize } from '../hooks/model'
import { hookDefs, hookName, matches, mcpServer } from '../hooks/names'
import { toHtml, toMarkdown } from '../hooks/report'

const NOW = Date.UTC(2026, 9, 28, 15, 0, 0)

const PANE = {
  plugin: 'model-trace',
  component: 'Pane',
  requestId: 'model-trace',
  props: {
    title: 'Model Trace',
    isFocused: false,
    bodyColumns: 60,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 40 },
    view: {},
  },
} as const

const USER_LAYER = {
  hooks: {
    PostToolUse: [
      {
        matcher: 'Bash',
        hooks: [{ type: 'command', command: '~/.claude/hooks/lint-after.sh --quiet' }],
      },
    ],
    Stop: [
      {
        hooks: [{ type: 'command', command: 'node ./notify.mjs', statusMessage: 'Notify on stop' }],
      },
    ],
    SessionStart: [
      {
        matcher: 'startup|resume',
        hooks: [{ type: 'command', command: 'bash ~/.claude/hooks/greet.sh' }],
      },
    ],
  },
}

/** The engine beneath the plugin: what the session has available. */
function world(
  on: On,
  writes: Array<{ path: string; text: string }> = [],
  skillGate?: Promise<void>,
): void {
  mock.clock(on, { now: NOW })
  mock.env(on, { HOME: '/home/ana' })
  on('command.register', () => ({ value: { command: 'model-trace' } }))
  on('settings.read', (_$, e) => ({
    value: 'source' in e && e.source === 'user' ? USER_LAYER : {},
  }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.status', () => ({ value: undefined }))
  on('classic.PostToolUse', () => ({}))
  on('classic.SessionStart', () => ({}))
  on('fs.exists', () => ({ value: true }))
  on('fs.write', (_$, e) => {
    writes.push({ path: e.path, text: e.text })
    return { value: undefined }
  })
  on('tool.call', async (_$, e) => {
    // A Skill call stays open until the test has expanded its skill, as Claude Code expands it inside the call.
    if (e.tool === 'Skill' && skillGate !== undefined) {
      await skillGate
    }
    if (e.tool === 'WebFetch' && e.url.includes('blocked')) {
      return { deny: 'refused by a permission rule' }
    }
    return { result: { ok: true } }
  })
  on('skill.prompt', (_$, e) => ({ text: e.text, frontmatter: e.frontmatter }))
  on('session.start', (_$, e) => ({ cwd: e.cwd }))
}

describe('names', () => {
  test('an MCP tool shows as its server, never the tool', async () => {
    expect(mcpServer('mcp__plugin_docs-kit_search__query')).toEqual({
      name: 'search',
      origin: 'docs-kit',
      plugin: 'docs-kit',
    })
    expect(mcpServer('mcp__claude_ai_Google_Drive__fetch')).toEqual({
      name: 'Google Drive',
      origin: 'claude.ai',
    })
    expect(mcpServer('mcp__memory__read_graph')).toEqual({ name: 'memory', origin: 'MCP' })
    expect(mcpServer('Bash')).toBeUndefined()
  })

  test('a hook is named without its command line', async () => {
    expect(
      hookName({
        type: 'command',
        command: '"$CLAUDE_PROJECT_DIR"/.claude/hooks/checkout.sh --all',
      }),
    ).toBe('checkout.sh')
    expect(hookName({ type: 'command', command: 'python3 /opt/hooks/guard.py' })).toBe('guard.py')
    expect(hookName({ type: 'command', command: 'x', statusMessage: 'Checking secrets' })).toBe(
      'Checking secrets',
    )
    expect(hookName({ type: 'http', url: 'https://example.com' })).toBe('http hook')
  })

  test('matchers follow the hooks docs', async () => {
    expect(matches('PostToolUse', 'Edit|Write', 'Write')).toBe(true)
    expect(matches('PostToolUse', 'Edit, Write', 'NotebookEdit')).toBe(false)
    expect(matches('PostToolUse', 'Edit.*', 'NotebookEdit')).toBe(true)
    expect(matches('PostToolUse', 'mcp__memory__.*', 'mcp__memory__read')).toBe(true)
    expect(matches('PostToolUse', '', 'Bash')).toBe(true)
    expect(matches('Stop', 'anything', undefined)).toBe(true)
    expect(matches('SessionStart', 'startup', undefined)).toBe(false)
    expect(matches('StopFailure', 'rate-limit', 'rate_limit')).toBe(false)
  })

  test('an if condition marks the hook conditional', async () => {
    const [def] = hookDefs('project', {
      PreToolUse: [
        { matcher: 'Bash', hooks: [{ type: 'command', command: 'a.sh', if: 'Bash(rm *)' }] },
      ],
    })
    expect(def?.conditional).toBe(true)
    expect(def?.name).toBe('a.sh')
  })
})

describe('totals', () => {
  test('a plugin skill counts once in the totals, though its plugin row rolls it up', async () => {
    const summary = summarize(
      [
        {
          kind: 'skill',
          name: 'docs-kit:write-guide',
          origin: 'docs-kit',
          plugin: 'docs-kit',
          at: NOW,
        },
      ],
      NOW,
    )
    expect(summary.uses).toBe(1)
    expect(summary.capabilities).toBe(1)
    const plugins = summary.sections.find((s) => s.kind === 'plugin')
    expect(plugins?.rows[0]?.count).toBe(1)
    expect(plugins?.rows[0]?.origin).toBe('via skill')
    expect(plugins?.rollup).toBe(true)
  })

  test('hook output is shown but left out of the totals', async () => {
    const summary = summarize(
      [{ kind: 'hook', name: 'SessionStart', origin: 'hook output', at: NOW }],
      NOW,
    )
    expect(summary.uses).toBe(0)
    expect(summary.sections.find((s) => s.kind === 'hook')?.rows[0]?.count).toBe(1)
  })

  test('a section title separates the hook output the totals leave out', async () => {
    const summary = summarize(
      [
        { kind: 'hook', name: 'lint-after.sh', origin: 'user · PostToolUse', at: NOW },
        ...Array.from({ length: 9 }, (_, i) => ({
          kind: 'hook' as const,
          name: 'PostToolUse',
          origin: 'hook output',
          at: NOW + i,
        })),
      ],
      NOW,
    )
    const hooks = summary.sections.find((s) => s.kind === 'hook')
    expect(hooks && sectionLabel(hooks)).toBe('1 · 1 use · 9 output')
    expect(summary.uses).toBe(1)
  })

  test('only what was used has a section, in the order it first appeared', async () => {
    const summary = summarize(
      [
        { kind: 'web', name: 'WebFetch', origin: 'built-in', at: NOW },
        { kind: 'web', name: 'WebSearch', origin: 'built-in', at: NOW + 1 },
        { kind: 'web', name: 'WebFetch', origin: 'built-in', at: NOW + 2 },
      ],
      NOW,
    )
    expect(summary.sections.map((s) => s.kind)).toEqual(['web'])
    expect(summary.sections[0]?.rows.map((row) => `${row.name}×${row.count}`)).toEqual([
      'WebFetch×2',
      'WebSearch×1',
    ])
  })

  test('the reports carry names and counts, never a command', async () => {
    const summary = summarize(
      [{ kind: 'web', name: 'WebSearch', origin: 'built-in', at: NOW }],
      NOW,
    )
    const md = toMarkdown(summary, NOW)
    expect(md).toContain('| WebSearch | built-in | 1 |')
    expect(md).not.toContain('Not used')
    const html = toHtml(summary, NOW)
    expect(html).toContain('<td class="n">1</td>')
    expect(html).not.toContain('<script')
  })
})

describe('the session', () => {
  test('a capability appears when first used and its count grows, on every surface', async ($, on) => {
    world(on)
    await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })

    const before = await $.ui.mount({ ...PANE, surface: 'terminal' })
    expect(await before.find({ key: 'row:mcp:search' })).toBeUndefined()
    expect(await before.find({ type: 'Text', text: /Waiting for Claude/ })).toBeDefined()
    await before.unmount()

    await $.skill.prompt({
      skill: 'write-guide',
      text: 'x',
      source: 'plugin',
      pluginName: 'docs-kit@acme',
      frontmatter: {},
    })
    await $.tool.call({ tool: 'mcp__plugin_docs-kit_search__query', q: 'a' })
    await $.tool.call({ tool: 'mcp__plugin_docs-kit_search__query', q: 'b' })
    await $.tool.call({ tool: 'WebSearch', query: 'mods', mode: 'standard' })
    await $.tool.call({ tool: 'Bash', command: 'ls' })

    for (const surface of ['terminal', 'desktop', 'vscode', 'mobile'] as const) {
      const ui = await $.ui.mount({ ...PANE, surface })
      expect((await ui.find({ type: 'Text', text: /^4$/ }))?.text).toBe('4')
      expect(await ui.find({ key: 'row:skill:docs-kit:write-guide' })).toBeDefined()
      expect(await ui.find({ key: 'row:mcp:search' })).toBeDefined()
      expect(await ui.find({ type: 'Text', text: /^×2$/ })).toBeDefined()
      expect(await ui.find({ key: 'row:web:WebSearch' })).toBeDefined()
      expect(await ui.find({ key: 'row:plugin:docs-kit' })).toBeDefined()
      expect(await ui.find({ type: 'Text', text: /Bash/ })).toBeUndefined()
      await ui.unmount()
    }
  })

  test('a settings hook counts when its matcher selects the fire', async ($, on) => {
    world(on)
    const postToolUse = $.classic.PostToolUse
    await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
    await postToolUse({
      tool_name: 'Bash',
      tool_input: {},
      tool_response: {},
      tool_use_id: 't1',
    } as never)
    await postToolUse({
      tool_name: 'Read',
      tool_input: {},
      tool_response: {},
      tool_use_id: 't2',
    } as never)
    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    const row = await ui.find({ key: 'row:hook:user · PostToolUse:lint-after.sh' })
    expect(row?.text).toContain('lint-after.sh')
    expect(await ui.find({ type: 'Text', text: /×1/ })).toBeDefined()
    await ui.unmount()
  })

  test('a narrow pane keeps the whole name and shows the origin in the details', async ($, on) => {
    world(on)
    const postToolUse = $.classic.PostToolUse
    await $.session.start({ cwd: '/work', surface: 'desktop', isInteractive: true })
    await postToolUse({
      tool_name: 'Bash',
      tool_input: {},
      tool_response: {},
      tool_use_id: 't1',
    } as never)
    const narrow = { ...PANE, props: { ...PANE.props, bodyColumns: 30 } }
    const ui = await $.ui.mount({ ...narrow, surface: 'desktop' })
    const key = 'row:hook:user · PostToolUse:lint-after.sh'
    expect((await ui.find({ key }))?.text).toContain('lint-after.sh')
    expect((await ui.find({ key }))?.text).not.toContain('PostToolUse')
    await ui.press({ key })
    expect(await ui.find({ type: 'Text', text: /^user · PostToolUse$/ })).toBeDefined()
    await ui.unmount()
  })

  test('a SessionStart hook that fires before session.start still counts', async ($, on) => {
    world(on)
    const sessionStart = $.classic.SessionStart
    await sessionStart({ source: 'startup' } as never)
    await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
    await sessionStart({ source: 'clear' } as never)
    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    const row = await ui.find({ key: 'row:hook:user · SessionStart:greet.sh' })
    expect(row?.text).toContain('greet.sh')
    await ui.unmount()
  })

  test('a skill Claude calls counts once, with its origin, though its prompt is expanded inside the call', async ($, on) => {
    let release: () => void = (): void => undefined
    world(
      on,
      [],
      new Promise<void>((resolve) => {
        release = resolve
      }),
    )
    await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
    const call = $.tool.call({ tool: 'Skill', skill: 'docs-kit:write-guide' })
    await $.skill.prompt({
      skill: 'write-guide',
      text: 'x',
      source: 'plugin',
      pluginName: 'docs-kit@acme',
      frontmatter: {},
    })
    release()
    await call
    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    expect(await ui.find({ key: 'row:skill:docs-kit:write-guide' })).toBeDefined()
    expect((await ui.find({ type: 'Text', text: /^1$/ }))?.text).toBe('1')
    expect(await ui.find({ type: 'Text', text: /^×2$/ })).toBeUndefined()
    await ui.unmount()
  })

  test('a Skill call still counts where skill.prompt never reaches the mod', async ($, on) => {
    world(on)
    await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
    await $.tool.call({ tool: 'Skill', skill: 'docs-kit:write-guide' })
    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    expect(await ui.find({ key: 'row:skill:docs-kit:write-guide' })).toBeDefined()
    expect(await ui.find({ key: 'row:plugin:docs-kit' })).toBeDefined()
    await ui.unmount()
  })

  test('a call that was refused is not a use', async ($, on) => {
    world(on)
    await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
    const ran = await $.tool.call({ tool: 'WebFetch', url: 'https://blocked.example', prompt: 'x' })
    expect(ran.deny).toBe('refused by a permission rule')
    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    expect(await ui.find({ key: 'row:web:WebFetch' })).toBeUndefined()
    await ui.unmount()
  })

  test('observing never changes a call, even when recording fails', async ($, on) => {
    world(on)
    on('state.set', () => ({ deny: 'store unavailable' }))
    const ran = await $.tool.call({ tool: 'WebSearch', query: 'x', mode: 'standard' })
    expect(ran.result).toEqual({ ok: true })
  })

  test('the report is written to the export folder with names and times', async ($, on) => {
    const writes: Array<{ path: string; text: string }> = []
    world(on, writes)
    await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
    await $.tool.call({ tool: 'WebFetch', url: 'https://example.com', prompt: 'summarize' })
    const answer = await $.command.run({ command: 'model-trace', args: 'md' } as never)
    expect(String((answer as { text?: string }).text)).toContain('/home/ana/Downloads/model-trace-')
    expect(writes[0]?.path).toMatch(/^\/home\/ana\/Downloads\/model-trace-\d{8}-\d{6}\.md$/)
    expect(writes[0]?.text).toContain('| WebFetch | built-in | 1 |')
    expect(writes[0]?.text).not.toContain('example.com')
  })
})
