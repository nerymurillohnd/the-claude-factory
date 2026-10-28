/** One settings hook handler, named without its command line. */
export type HookDef = {
  id: string
  name: string
  event: string
  source: string
  matcher: string
  conditional: boolean
}

/** A capability's plugin by its bare name: `superpowers@market` → `superpowers`. */
export function bareName(id: string): string {
  return id.split('@')[0] ?? id
}

/** The server behind an MCP tool name, never the tool itself. */
export type McpServer = { name: string; origin: string; plugin?: string }

/**
 * `mcp__<server>__<tool>` → its server. A plugin's server is
 * `plugin_<plugin>_<server>` (plugin names are kebab-case, so the first `_`
 * after the plugin ends it); a claude.ai connector is `claude_ai_<Name>`.
 */
export function mcpServer(tool: string): McpServer | undefined {
  if (!tool.startsWith('mcp__')) {
    return undefined
  }
  const segment = tool.slice('mcp__'.length).split('__')[0]
  if (!segment) {
    return undefined
  }
  if (segment.startsWith('plugin_')) {
    const rest = segment.slice('plugin_'.length)
    const cut = rest.indexOf('_')
    if (cut > 0) {
      const plugin = rest.slice(0, cut)
      return { name: rest.slice(cut + 1), origin: plugin, plugin }
    }
  }
  if (segment.startsWith('claude_ai_')) {
    return { name: segment.slice('claude_ai_'.length).replaceAll('_', ' '), origin: 'claude.ai' }
  }
  return { name: segment, origin: 'MCP' }
}

/** A skill source in a person's words. */
export function skillOrigin(source: string, plugin: string | undefined): string {
  if (plugin) {
    return plugin
  }
  switch (source) {
    case 'userSettings':
      return 'user'
    case 'projectSettings':
      return 'project'
    case 'policySettings':
      return 'managed'
    case 'built-in':
      return 'built-in'
    case 'mcp':
      return 'MCP'
    case 'syncedSkills':
      return 'synced'
    default:
      return source
  }
}

/** An agent provider in a person's words: `engine` is Claude Code itself. */
export function agentOrigin(provider: string): { origin: string; plugin?: string } {
  if (provider === 'engine') {
    return { origin: 'built-in' }
  }
  if (provider === 'user' || provider === 'project' || provider === 'local') {
    return { origin: provider }
  }
  const plugin = bareName(provider)
  return { origin: plugin, plugin }
}

/** A skill named as the slash menu names it: plugin skills carry their plugin. */
export function skillKey(skill: string, plugin: string | undefined): string {
  return plugin && !skill.includes(':') ? `${plugin}:${skill}` : skill
}

const WHITESPACE = /\s+/
const QUOTES = /^["']|["']$/g
const ENV_ASSIGNMENT = /^[A-Z_][A-Z0-9_]*=/

const INTERPRETERS = new Set([
  'bash',
  'sh',
  'zsh',
  'node',
  'python',
  'python3',
  'uv',
  'uvx',
  'npx',
  'bun',
  'deno',
  'env',
])

/**
 * A handler's name without its command line: its status message, else the
 * file name of the program it runs, else its type.
 */
export function hookName(handler: Readonly<Record<string, unknown>>): string {
  const status = handler['statusMessage']
  if (typeof status === 'string' && status.trim()) {
    return status.trim()
  }
  const command = handler['command']
  if (typeof command === 'string') {
    const tokens = command
      .trim()
      .split(WHITESPACE)
      .map((token) => token.replace(QUOTES, ''))
      .filter((token) => token && !ENV_ASSIGNMENT.test(token) && !token.startsWith('-'))
    const program =
      tokens.find((token) => !INTERPRETERS.has(token.split('/').pop() ?? token)) ?? tokens[0]
    if (program) {
      return program.split('/').pop() || program
    }
  }
  const type = handler['type']
  return `${typeof type === 'string' ? type : 'command'} hook`
}

type HookGroups = Readonly<Record<string, ReadonlyArray<{ matcher?: unknown; hooks?: unknown }>>>

/** Every handler a settings layer configures, named and keyed. */
export function hookDefs(source: string, hooks: unknown): HookDef[] {
  if (!hooks || typeof hooks !== 'object') {
    return []
  }
  const defs: HookDef[] = []
  for (const [event, groups] of Object.entries(hooks as HookGroups)) {
    if (!Array.isArray(groups)) {
      continue
    }
    groups.forEach((group, g) => {
      const matcher = typeof group?.matcher === 'string' ? group.matcher : ''
      const handlers = Array.isArray(group?.hooks) ? (group.hooks as Record<string, unknown>[]) : []
      handlers.forEach((handler, i) => {
        if (!handler || typeof handler !== 'object') {
          return
        }
        defs.push({
          id: `${source}:${event}:${g}:${i}`,
          name: hookName(handler),
          event,
          source,
          matcher,
          conditional: typeof handler['if'] === 'string' && handler['if'].length > 0,
        })
      })
    })
  }
  return defs
}

// The matcher forms the hooks docs define: an exact name or list, else a regular expression.
const EXACT = /^[A-Za-z0-9_\- ,|]+$/
const NARROW_EXACT = /^[A-Za-z0-9_|]+$/
const LIST_SEPARATOR = /[|,]/

const TOOL_EVENTS = new Set([
  'PreToolUse',
  'PostToolUse',
  'PostToolUseFailure',
  'PermissionRequest',
  'PermissionDenied',
])

/** The input field each settings hook event matches its matcher on. */
const MATCH_FIELD: ReadonlyMap<string, string> = new Map([
  ['SessionStart', 'source'],
  ['Setup', 'trigger'],
  ['SessionEnd', 'reason'],
  ['Notification', 'notification_type'],
  ['SubagentStart', 'agent_type'],
  ['SubagentStop', 'agent_type'],
  ['PreCompact', 'trigger'],
  ['PostCompact', 'trigger'],
  ['ConfigChange', 'source'],
  ['DirectoryAdded', 'source'],
  ['StopFailure', 'error'],
  ['InstructionsLoaded', 'load_reason'],
  ['Elicitation', 'mcp_server_name'],
  ['ElicitationResult', 'mcp_server_name'],
  ['PreModelSwitch', 'to_model'],
  ['PostModelSwitch', 'to_model'],
])

/** Events the hooks docs list with no matcher support: every fire counts. */
const NO_MATCHER = new Set([
  'UserPromptSubmit',
  'PostToolBatch',
  'Stop',
  'TeammateIdle',
  'TaskCreated',
  'TaskCompleted',
  'WorktreeCreate',
  'WorktreeRemove',
  'MessageDisplay',
  'CwdChanged',
])

/** The value an event's matcher is tested on; undefined where none is known. */
export function matchValue(
  event: string,
  input: Readonly<Record<string, unknown>>,
): string | undefined {
  const pick = (key: string): string | undefined => {
    const found = input[key]
    return typeof found === 'string' ? found : undefined
  }
  if (TOOL_EVENTS.has(event)) {
    return pick('tool_name') ?? pick('tool')
  }
  if (event === 'FileChanged') {
    return pick('file_path')?.split('/').pop()
  }
  const field = MATCH_FIELD.get(event)
  return field ? pick(field) : undefined
}

/** Whether a settings hook's matcher selects this fire, per the hooks docs. */
export function matches(event: string, matcher: string, value: string | undefined): boolean {
  if (NO_MATCHER.has(event) || matcher === '' || matcher === '*') {
    return true
  }
  if (value === undefined) {
    return false
  }
  const narrow = event === 'FileChanged' || event === 'StopFailure'
  const exact = narrow ? NARROW_EXACT : EXACT
  if (exact.test(matcher)) {
    return matcher
      .split(narrow ? '|' : LIST_SEPARATOR)
      .map((part) => part.trim())
      .includes(value)
  }
  try {
    return new RegExp(matcher).test(value)
  } catch {
    return false
  }
}
