import type { Kind, Use } from '../types'

/** A section of the pane and the reports; Plugins regroups the others. */
export type SectionKind = Kind | 'plugin'

/** One capability Claude used, as the pane and the reports show it. */
export type Row = {
  key: string
  kind: SectionKind
  name: string
  origin: string
  count: number
  times: number[]
  note?: string
  /** A roll-up or a second view of uses other rows already count: left out of the totals. */
  derived?: true
}

export type Section = {
  kind: SectionKind
  title: string
  rows: Row[]
  uses: number
  /** The section only regroups uses other sections count (Plugins). */
  rollup: boolean
}

/** Totals count each use once: Plugins and hook output rows are left out. */
export type Summary = {
  sections: Section[]
  capabilities: number
  uses: number
  since: number
}

export const SECTIONS: ReadonlyArray<{ kind: SectionKind; title: string; noun: string }> = [
  { kind: 'skill', title: 'Skills', noun: 'Skill' },
  { kind: 'agent', title: 'Agents', noun: 'Agent' },
  { kind: 'mcp', title: 'MCP servers', noun: 'MCP server' },
  { kind: 'plugin', title: 'Plugins', noun: 'Plugin' },
  { kind: 'hook', title: 'Hooks', noun: 'Hook' },
  { kind: 'web', title: 'Web', noun: 'Tool' },
]

export const HOOK_OUTPUT = 'hook output'
const OUTPUT_NOTE = 'output any hook gave Claude, plugin hooks included; not in the totals'
const UP_TO_NOTE = 'has an if condition: the count is an upper bound'
const NOUNS: Readonly<Record<Kind, string>> = {
  skill: 'skill',
  agent: 'agent',
  mcp: 'MCP server',
  hook: 'hook',
  web: 'web tool',
}

/** Groups the uses by capability, in the order they first appeared within each section. */
export function summarize(uses: readonly Use[], since: number): Summary {
  const rows = new Map<string, Row>()
  const through = new Map<string, Set<Kind>>()
  const ensure = (kind: SectionKind, name: string, origin: string): Row => {
    const key = kind === 'hook' ? `hook:${origin}:${name}` : `${kind}:${name}`
    let row = rows.get(key)
    if (!row) {
      row = { key, kind, name, origin, count: 0, times: [] }
      rows.set(key, row)
    }
    return row
  }

  for (const use of uses) {
    const row = ensure(use.kind, use.name, use.origin)
    row.count += 1
    row.times.push(use.at)
    if (use.kind === 'hook' && use.origin === HOOK_OUTPUT) {
      row.derived = true
      row.note = OUTPUT_NOTE
    }
    if (use.upTo) {
      row.note = UP_TO_NOTE
    }
    if (use.plugin) {
      const owner = ensure('plugin', use.plugin, '')
      owner.count += 1
      owner.times.push(use.at)
      owner.derived = true
      const kinds = through.get(use.plugin) ?? new Set<Kind>()
      kinds.add(use.kind)
      through.set(use.plugin, kinds)
    }
  }
  for (const [plugin, kinds] of through) {
    const row = rows.get(`plugin:${plugin}`)
    if (row) {
      row.origin = `via ${[...kinds].map((kind) => NOUNS[kind]).join(', ')}`
    }
  }

  const sections = SECTIONS.map(({ kind, title }) => {
    const list = [...rows.values()].filter((row) => row.kind === kind)
    return {
      kind,
      title,
      rows: list,
      uses: list.reduce((n, row) => n + row.count, 0),
      rollup: kind === 'plugin',
    }
  }).filter((section) => section.rows.length > 0)

  const counted = sections
    .filter((s) => !s.rollup)
    .flatMap((s) => s.rows.filter((row) => !row.derived))
  return {
    sections,
    capabilities: counted.length,
    uses: counted.reduce((n, row) => n + row.count, 0),
    since: since || (uses[0]?.at ?? 0),
  }
}

const clock = new Intl.DateTimeFormat(undefined, {
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hourCycle: 'h23',
})
const calendar = new Intl.DateTimeFormat('en-CA', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
})

/** HH:MM:SS in the machine's time zone. */
export function formatTime(at: number): string {
  return clock.format(at)
}

/** YYYY-MM-DD in the machine's time zone. */
export function formatDate(at: number): string {
  return calendar.format(at)
}

export function timeZone(): string {
  return new Intl.DateTimeFormat().resolvedOptions().timeZone
}

/** A span of time as `1h 05m`, `12m 30s` or `45s`. */
export function formatSpan(ms: number): string {
  const total = Math.max(0, Math.round(ms / 1000))
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
  if (h > 0) {
    return `${h}h ${String(m).padStart(2, '0')}m`
  }
  if (m > 0) {
    return `${m}m ${String(s).padStart(2, '0')}s`
  }
  return `${s}s`
}
