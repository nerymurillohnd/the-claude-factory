/** Why a turn ended, as `turn.complete` reports it. */
export type TurnReason = 'answer' | 'aborted' | 'error' | 'refusal'

/** One finished main-loop turn, as the band shows it. */
export type TurnSummary = {
  durationMs: number
  reason: TurnReason
  /** Tool calls made by the main loop. */
  tools: number
  /** Tool calls made by subagents during the turn. */
  subagentTools: number
  /** Distinct subagents that ran during the turn. */
  subagents: number
  /** Input tokens: uncached, cache reads and cache writes, main loop and subagents. */
  tokensIn: number
  /** Output tokens, main loop and subagents. */
  tokensOut: number
}

declare module 'claude-code' {
  interface PluginState {
    'turn-meter': { last: TurnSummary | null; isHidden: boolean }
  }
}
