/** What a row counts: one capability family of the session. */
export type Kind = 'skill' | 'agent' | 'mcp' | 'hook' | 'web'

/** One use of a capability, with the instant it happened (epoch ms). */
export type Use = {
  kind: Kind
  name: string
  origin: string
  plugin?: string
  /** A settings hook with an `if` condition: the fire matched, the handler may not have run. */
  upTo?: true
  at: number
}

declare module 'claude-code' {
  interface PluginState {
    'model-trace': {
      uses: Shaped<Use[]>
      since: number
      expanded: string[]
      showAll: string[]
    }
  }
}
