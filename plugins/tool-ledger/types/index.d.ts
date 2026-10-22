/** How a tool call stands: still running, finished, failed, or refused before it ran. */
export type LedgerStatus = 'runs' | 'done' | 'error' | 'denied'

/** One tool call, as the panel lists it. */
export type LedgerRow = {
  id: string
  tool: string
  /** What the call acted on (a command, a path, a pattern), or null for tools without one. */
  target: string | null
  /** The subagent that made the call, or null for the main thread. */
  agentId: string | null
  status: LedgerStatus
  startedAt: number
  durationMs: number | null
}

declare module 'claude-code' {
  interface PluginState {
    'tool-ledger': {
      rows: LedgerRow[]
      /** Each subagent's label, `type · "description"`, by agent id. */
      agents: Record<string, string>
      isErrorsOnly: boolean
    }
  }
}
