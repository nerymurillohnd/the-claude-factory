import type {
  EngineInterface,
  On,
  PluginOptions,
  Register,
  RenderElement,
  RenderInput,
  UiPressArgument,
} from 'claude-code'
import { atom, read, update } from 'claude-code'

import type { Use } from '../types'
import {
  formatDate,
  formatTime,
  HOOK_OUTPUT,
  type Row,
  type SectionKind,
  type Summary,
  sectionLabel,
  summarize,
} from './model'
import {
  agentOrigin,
  bareName,
  type HookDef,
  hookDefs,
  matches,
  matchValue,
  mcpServer,
  skillKey,
  skillOrigin,
} from './names'
import { ROLLUP, toHtml, toMarkdown } from './report'

const PANE = 'model-trace'
const MAX_USES = 5000
const PREVIEW_ROWS = 8
const SETTINGS_SOURCES = ['user', 'project', 'local', 'flag', 'policy'] as const
const WEB_TOOLS = new Set(['WebSearch', 'WebFetch'])
const TRAILING_SLASHES = /\/+$/
const EXPORT_WORD = /^export\s+/
const LEADING_DOT = /^\./

// Bump the shape tag when a stored use's fields change: the new code then
// reads what an earlier version stored as an empty list.
const uses = atom({ plugin: 'model-trace', key: 'uses' } as const, [], { shape: 'uses-2' })
const since = atom({ plugin: 'model-trace', key: 'since' } as const, 0)
const expanded = atom({ plugin: 'model-trace', key: 'expanded' } as const, [])
const showAll = atom({ plugin: 'model-trace', key: 'showAll' } as const, [])

type Dollar = EngineInterface
type Capability = Omit<Use, 'at'>
type SkillUse = { name: string; origin: string; plugin?: string }

// Re-derivable caches: a reload starts them over and they are read again.
let options: PluginOptions = {}
let hookCache: Promise<HookDef[]> | undefined
// Skill tool calls in flight, by short skill name: the skill.prompt raised inside one leaves its origin here
// instead of counting the use a second time. Lost on a reload mid-call, which only drops that one origin.
const skillsInFlight = new Map<string, SkillUse | undefined>()

/** Records uses that happened at one instant; observing never changes the call it watches, so it never throws. */
async function record($: Dollar, found: readonly Capability[], at: number): Promise<void> {
  if (found.length === 0) {
    return
  }
  try {
    const list = await update($, uses, (current) =>
      [...current, ...found.map((use) => ({ ...use, at }))].slice(-MAX_USES),
    )
    if (options['statusLine'] === true) {
      const summary = summarize(list, await read($, since))
      $.ui.status(`${summary.capabilities} used · ${summary.uses} uses`)
    }
  } catch {
    // A lost record is better than a call changed by its observer.
  }
}

/** The settings hooks of one layer; a layer the engine bars from the read adds none. */
async function readLayerHooks(
  $: Dollar,
  source: (typeof SETTINGS_SOURCES)[number],
): Promise<HookDef[]> {
  try {
    const layer = await $.settings.read({ source })
    return hookDefs(source, (layer as { hooks?: unknown }).hooks)
  } catch {
    return []
  }
}

/** Settings hooks fire before session.start (SessionStart, InstructionsLoaded): read them on the first fire. */
function knownHooks($: Dollar): Promise<HookDef[]> {
  hookCache ??= Promise.all(SETTINGS_SOURCES.map((source) => readLayerHooks($, source))).then(
    (layers) => layers.flat(),
  )
  return hookCache
}

/** What a tool call is a use of: a skill to resolve, a capability, or nothing to count. */
function toolTarget(
  tool: string,
  skill: unknown,
): { skill: string } | { use: Capability } | undefined {
  if (tool === 'Skill' && typeof skill === 'string') {
    return { skill }
  }
  const server = mcpServer(tool)
  if (server) {
    return { use: { kind: 'mcp', ...server } }
  }
  if (WEB_TOOLS.has(tool)) {
    return { use: { kind: 'web', name: tool, origin: 'built-in' } }
  }
  return undefined
}

/** A skill's name without its plugin, the part a Skill call and skill.prompt agree on. */
function shortSkill(name: string): string {
  return name.split(':').pop() ?? name
}

/** A Skill tool call's skill when no skill.prompt named its origin: a plugin skill is `<plugin>:<skill>`. */
function skillFromTool(name: string): SkillUse {
  const cut = name.indexOf(':')
  if (cut <= 0) {
    return { name, origin: 'user or built-in' }
  }
  const plugin = name.slice(0, cut)
  return { name, origin: plugin, plugin }
}

/** Runs a Skill tool call and names its skill by what a skill.prompt inside it reported. */
async function runSkillCall<T>(
  skill: string,
  run: () => Promise<T>,
): Promise<{ ran: T; use: Capability }> {
  const short = shortSkill(skill)
  skillsInFlight.set(short, undefined)
  try {
    const ran = await run()
    return { ran, use: { kind: 'skill', ...(skillsInFlight.get(short) ?? skillFromTool(skill)) } }
  } finally {
    skillsInFlight.delete(short)
  }
}

async function expandHome($: Dollar, dir: string): Promise<string> {
  if (dir !== '~' && !dir.startsWith('~/')) {
    return dir
  }
  const home = await $.env.get('HOME')
  return home ? `${home}${dir.slice(1)}` : dir
}

function stamp(at: number): string {
  return `${formatDate(at).replaceAll('-', '')}-${formatTime(at).replaceAll(':', '')}`
}

async function currentSummary($: Dollar): Promise<Summary> {
  return summarize(await read($, uses), await read($, since))
}

/** Writes the report to the export folder; resolves its path, or why it was not written. */
async function exportReport(
  $: Dollar,
  format: 'md' | 'html',
): Promise<{ path?: string; error?: string }> {
  const summary = await currentSummary($)
  const now = await $.clock.now()
  const configured =
    typeof options['exportDir'] === 'string' && options['exportDir'].trim()
      ? options['exportDir'].trim()
      : '~/Downloads'
  const dir = (await expandHome($, configured)).replace(TRAILING_SLASHES, '')
  if (!(await $.fs.exists(dir))) {
    return { error: `the folder ${dir} does not exist; set exportDir to one that does` }
  }
  const path = `${dir}/model-trace-${stamp(now)}.${format}`
  try {
    await $.fs.write(path, format === 'md' ? toMarkdown(summary, now) : toHtml(summary, now))
    return { path }
  } catch (err) {
    return { error: `could not write ${path}: ${err instanceof Error ? err.message : String(err)}` }
  }
}

/** The text a command answers where no pane draws, such as `claude -p`. */
function textSummary(summary: Summary): string {
  const lines = [
    `Model Trace: ${summary.capabilities} capabilities, ${summary.uses} uses since ${formatTime(summary.since)}.`,
  ]
  for (const section of summary.sections) {
    lines.push(
      `${section.title}: ${section.rows.map((row) => `${row.name} ×${row.count}`).join(', ')}`,
    )
  }
  return lines.join('\n')
}

async function onSessionStart($: Dollar): Promise<void> {
  try {
    const now = await $.clock.now()
    await update($, since, (value) => value || now)
    await $.command.register({
      name: 'model-trace',
      description:
        'Show the skills, agents, MCP servers, plugins, hooks and web tools Claude used this session',
      argumentHint: '[md | html]',
    })
  } catch {
    // The session goes on without the command rather than failing at start.
  }
}

async function onCommand($: Dollar, args: string): Promise<{ text?: string }> {
  const format = args.trim().toLowerCase().replace(EXPORT_WORD, '').replace(LEADING_DOT, '')
  if (format === 'md' || format === 'html') {
    const { path, error } = await exportReport($, format)
    return { text: path ? `Model Trace saved to ${path}` : `Model Trace: ${error}` }
  }
  const opened = await $.ui.open({
    id: PANE,
    title: 'Model Trace',
    focus: true,
    closeOnEscape: true,
  })
  // What a command returns, Claude reads: an open pane needs no words in its context.
  return opened.isPlaced ? {} : { text: textSummary(await currentSummary($)) }
}

function truncate(text: string, room: number): string {
  if (room <= 1) {
    return text.slice(0, Math.max(0, room))
  }
  return text.length <= room ? text : `${text.slice(0, room - 1)}…`
}

function toggle<T extends string>(list: readonly T[], key: T): T[] {
  return list.includes(key) ? list.filter((k) => k !== key) : [...list, key]
}

async function save($: Dollar, format: 'md' | 'html'): Promise<void> {
  const { path, error } = await exportReport($, format)
  $.ui.toast(path ? `Saved ${path}` : `Not saved: ${error}`)
}

async function copy($: Dollar, surface: RenderInput<'Pane'>['surface']): Promise<void> {
  const copied = await $.ui.copy({
    text: toMarkdown(await currentSummary($), await $.clock.now()),
    surface,
  })
  $.ui.toast(copied.isCopied ? 'Markdown copied' : 'Nothing was copied')
}

async function renderPane($: Dollar, e: RenderInput<'Pane'>): Promise<RenderElement> {
  const { Box, Text, Button } = $.ui.resolve(e)
  const summary = await currentSummary($)
  const open = new Set(await read($, expanded))
  const full = new Set(await read($, showAll))
  const width = Math.max(24, e.props.bodyColumns)

  const row = (item: Row): RenderElement => {
    const last = item.times.at(-1)
    const right = last === undefined ? `×${item.count}` : `×${item.count}  ${formatTime(last)}`
    // The name comes first: the origin shares its line only when both fit, else it moves to the details.
    const room = Math.max(8, width - right.length - 4)
    const originInline = item.name.length + 1 + item.origin.length <= room
    const isOpen = open.has(item.key)
    return (
      <Box flexDirection="column">
        <Box flexDirection="row" gap={1} justifyContent="space-between">
          <Button
            key={`row:${item.key}`}
            onPress={(): Promise<string[]> => update($, expanded, (list) => toggle(list, item.key))}
            plain={true}
          >
            {isOpen ? '▾ ' : '▸ '}
            {truncate(item.name, room)}
            {originInline ? <Text dimColor={true}>{` ${item.origin}`}</Text> : ''}
          </Button>
          <Text tabular={true}>
            <Text color="claude" weight="semibold">{`×${item.count}`}</Text>
            {last === undefined ? '' : <Text dimColor={true}>{`  ${formatTime(last)}`}</Text>}
          </Text>
        </Box>
        {isOpen && (
          <Box flexDirection="column" paddingLeft={2}>
            {!originInline && (
              <Text dimColor={true} wrap="wrap">
                {item.origin}
              </Text>
            )}
            <Text dimColor={true} tabular={true} wrap="wrap">
              {item.times.map(formatTime).join(' · ')}
            </Text>
            {item.note && (
              <Text dimColor={true} italic={true} wrap="wrap">
                {item.note}
              </Text>
            )}
          </Box>
        )}
      </Box>
    )
  }

  const more = (kind: SectionKind, count: number, isFull: boolean): RenderElement => (
    <Button
      dimColor={true}
      key={`more:${kind}`}
      onPress={(): Promise<string[]> => update($, showAll, (list) => toggle(list, kind))}
      plain={true}
    >
      {isFull ? '  Show fewer' : `  + ${count - PREVIEW_ROWS} more`}
    </Button>
  )

  const usesLabel = summary.uses === 1 ? ' use' : ' uses'
  const sinceLabel = summary.since ? formatTime(summary.since) : '—'
  return (
    <Box flexDirection="column" gap={1}>
      <Text>
        <Text color="claude" tabular={true} weight="semibold">
          {summary.capabilities}
        </Text>
        <Text dimColor={true}>
          {summary.capabilities === 1 ? ' capability · ' : ' capabilities · '}
        </Text>
        <Text tabular={true} weight="semibold">
          {summary.uses}
        </Text>
        <Text dimColor={true}>{`${usesLabel} · since ${sinceLabel}`}</Text>
      </Text>
      {summary.sections.length === 0 && (
        <Text dimColor={true} wrap="wrap">
          Waiting for Claude to use a skill, agent, MCP server, hook or web tool. Each one appears
          here the first time it is used.
        </Text>
      )}
      {summary.sections.map((section): RenderElement => {
        const isFull = full.has(section.kind) || section.rows.length <= PREVIEW_ROWS
        const count = sectionLabel(section)
        return (
          <Box flexDirection="column">
            <Box flexDirection="row" gap={1} justifyContent="space-between">
              <Text weight="semibold">{section.title}</Text>
              <Text dimColor={true} tabular={true}>
                {count}
              </Text>
            </Box>
            {section.rollup && (
              <Text dimColor={true} italic={true} wrap="wrap">
                {ROLLUP}
              </Text>
            )}
            {(isFull ? section.rows : section.rows.slice(0, PREVIEW_ROWS)).map(row)}
            {section.rows.length > PREVIEW_ROWS && more(section.kind, section.rows.length, isFull)}
          </Box>
        )
      })}
      <Box columnGap={3} flexDirection="row" flexWrap="wrap">
        <Button hotkey="m" key="save-md" onPress={(): Promise<void> => save($, 'md')} plain={true}>
          Save .md
        </Button>
        <Button
          hotkey="h"
          key="save-html"
          onPress={(): Promise<void> => save($, 'html')}
          plain={true}
        >
          Save .html
        </Button>
        <Button
          hotkey="c"
          key="copy-md"
          onPress={(press: UiPressArgument): Promise<void> => copy($, press.surface)}
          plain={true}
        >
          Copy Markdown
        </Button>
      </Box>
    </Box>
  )
}

export const register: Register = (on: On, pluginOptions: PluginOptions): void => {
  options = pluginOptions

  on('session.start', async ($, e, next) => {
    const started = await next(e)
    await onSessionStart($)
    return started
  }).catch((_$, e, next) => next(e))

  // /clear, /resume and /branch reset $.state and raise no session.start: the trace starts over from here.
  on('classic.SessionStart', { source: ['clear', 'resume', 'fork'] }, async ($, e, next) => {
    const started = await next(e)
    try {
      const now = await $.clock.now()
      await update($, since, () => now)
      $.ui.status(undefined)
    } catch {
      // The header then dates the trace from its first use.
    }
    return started
  }).catch((_$, e, next) => next(e))

  // Where the built-in guard loads, this hook does not run: the Skill tool call below still counts the model's uses.
  on('skill.prompt', async ($, e, next) => {
    const at = await $.clock.now()
    const prompted = await next(e)
    const plugin = e.pluginName ? bareName(e.pluginName) : undefined
    const skill: SkillUse = {
      name: skillKey(e.skill, plugin),
      origin: skillOrigin(e.source, plugin),
      ...(plugin ? { plugin } : {}),
    }
    const short = shortSkill(skill.name)
    if (skillsInFlight.has(short)) {
      skillsInFlight.set(short, skill)
    } else {
      await record($, [{ kind: 'skill', ...skill }], at)
    }
    return prompted
  }).catch((_$, e, next) => next(e))

  on('agent.spawn', async ($, e, next) => {
    const at = await $.clock.now()
    const spawned = await next(e)
    if (!e.resume && spawned.deny === undefined) {
      const { origin, plugin } = agentOrigin(e.provider.plugin)
      await record(
        $,
        [{ kind: 'agent', name: e.subagentType, origin, ...(plugin ? { plugin } : {}) }],
        at,
      )
    }
    return spawned
  }).catch((_$, e, next) => next(e))

  // A call counts once it ran: one a permission rule, a hook or another mod refused was not a use.
  on('tool.call', async ($, e, next) => {
    const target = toolTarget(String(e.tool), 'skill' in e ? e.skill : undefined)
    if (!target) {
      return next(e)
    }
    const at = await $.clock.now()
    if ('skill' in target) {
      const { ran, use } = await runSkillCall(target.skill, () => next(e))
      await record($, ran.deny === undefined ? [use] : [], at)
      return ran
    }
    const ran = await next(e)
    await record($, ran.deny === undefined ? [target.use] : [], at)
    return ran
  }).catch((_$, e, next) => next(e))

  on('classic.*', async ($, e, next) => {
    const event = next.event.slice('classic.'.length)
    const defs = (await knownHooks($)).filter((def) => def.event === event)
    if (defs.length === 0) {
      return next(e)
    }
    const at = await $.clock.now()
    const ran = next(e)
    const value = matchValue(event, e as Readonly<Record<string, unknown>>)
    const fired = defs
      .filter((def) => matches(event, def.matcher, value))
      .map(
        (def): Capability => ({
          kind: 'hook',
          name: def.name,
          origin: `${def.source} · ${def.event}`,
          ...(def.conditional ? { upTo: true as const } : {}),
        }),
      )
    await record($, fired, at)
    return ran
  }).catch((_$, e, next) => next(e))

  on('session.append', async ($, e, next) => {
    const appended = await next(e)
    const origin = e.origin
    if (origin.kind === 'hook') {
      await record(
        $,
        [{ kind: 'hook', name: origin.event, origin: HOOK_OUTPUT }],
        await $.clock.now(),
      )
    }
    return appended
  }).catch((_$, e, next) => next(e))

  on('command.run', { command: 'model-trace' }, async ($, e) => onCommand($, e.args))

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => renderPane($, e))
}
