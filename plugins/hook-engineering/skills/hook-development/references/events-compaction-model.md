# Compaction and model-switch events

PreCompact · PostCompact · PreModelSwitch · PostModelSwitch

Sources: https://code.claude.com/docs/en/hooks (read 2026-10-20) and the Claude Code CHANGELOG.md through v2.1.305; changelog-only facts are tagged *(changelog vX.Y.Z)*. Fields listed are in addition to the common input fields. All four support `command`, `http`, `mcp_tool` handlers only.

---

## PreCompact

Docs: [event](https://code.claude.com/docs/en/hooks#precompact) · [input](https://code.claude.com/docs/en/hooks#precompact-input)

**Fires:** before a compaction runs.

**Matcher → `trigger`:** `manual` (`/compact`), `auto` (auto-compact window reached, and idle compaction).

**Input:** `trigger`, `custom_instructions` (text passed to `/compact`, else `null`; always `null` for `auto`).

**Output:** exit 2 or top-level `decision: "block"` blocks compaction (manual: stderr shown to the user). `systemMessage`/`continue` discarded.

Blocking `auto` depends on why it fired: proactive (before the limit) → skipped, conversation continues uncompacted; recovering from a context-limit error the API already returned → that error surfaces and the request fails.

---

## PostCompact

Docs: [event](https://code.claude.com/docs/en/hooks#postcompact) · [input](https://code.claude.com/docs/en/hooks#postcompact-input)

**Fires:** after a compaction completes. Same matcher values as PreCompact.

**Input:** `trigger`, `compact_summary` (the generated summary).

**Output:** no decision control; `systemMessage`/`continue` discarded; exit 2 shows stderr to the user. Use to log the summary or update external state. To re-inject context after compaction, use SessionStart with matcher `compact`.

---

## PreModelSwitch

Docs: [event](https://code.claude.com/docs/en/hooks#premodelswitch) · [input](https://code.claude.com/docs/en/hooks#premodelswitch-input) · [decision control](https://code.claude.com/docs/en/hooks#premodelswitch-decision-control)

v2.1.251+.

**Fires:** before Claude Code applies a model switch that the user or a client requested: `/model <name>`, the `/model` picker, Option+P / Alt+P picker, Model in `/config`, turning on fast mode when it changes the model, and SDK/Remote Control `set_model` or a model change in `apply_flag_settings`. Not for switches Claude Code makes itself (automatic fallback, model restore on resume); those reach PostModelSwitch only.

**Matcher → canonical name of the target model**, ignoring `[1m]`. Aliases (`opus`), dated IDs and provider IDs (Bedrock) all resolve to one canonical name, so `claude-opus-5` covers every spelling. Exact (`claude-opus-5`), list (`claude-opus-4-6|claude-opus-5`) or regex (`.*opus.*`). If no canonical name can be derived (custom gateway model ID), every PreModelSwitch hook runs regardless of matcher: a blocking hook must also check `to_model` itself.

**Input:**

| Field | Notes |
|---|---|
| `from_model`, `to_model` | model IDs |
| `requested_model` | as requested (`opus`, a full ID) or `null` for the default |
| `source` | `command` (`/model <name>`, `/config`, fast mode), `picker`, `sdk` |
| `context_tokens` | tokens the next request re-sends (last main-conversation response's input + cache read + cache creation + output); `0` before the first response |
| `prompt_cache_warm` | whether the current model's cache is likely warm (the switch forfeits it) |
| `cache_ttl` | `5m` or `1h` |
| `estimated_cache_write_usd` | estimate of re-caching `context_tokens` on `to_model` at `cache_ttl` rate, excluding the response |
| `pricing` | `configured` (org rates), `catalog` (list price), `default` (unknown model, assumed rate) |

**Output (`hookSpecificOutput`):** `permissionDecision` `allow` (also skips the warm-cache confirmation), `deny`, or `ask`; `permissionDecisionReason` (deny → shown to the user or returned as the `set_model` error; ask → shown in the prompt). No `defer`, `updatedInput` or `additionalContext`. Exit 2 or top-level `decision: "block"` cancels. Precedence deny > ask > allow. `systemMessage` is shown regardless, so a cost-report hook can return just `{"systemMessage": "..."}` and exit 0.

`ask` only works for `/model` in an interactive session; everywhere else (`-p`, `/config`, `set_model`) it counts as refusal.

**Timeouts and errors:** default 30 s; a timeout **blocks** the switch. Other non-zero exits without valid JSON are non-blocking (the switch proceeds), unless the hook is configured to block on failure.

---

## PostModelSwitch

Docs: [event](https://code.claude.com/docs/en/hooks#postmodelswitch) · [input](https://code.claude.com/docs/en/hooks#postmodelswitch-input) · [decision control](https://code.claude.com/docs/en/hooks#postmodelswitch-decision-control)

v2.1.251+.

**Fires:** after the session's model changes for any reason: a requested switch, automatic fallback, a setting like `opusplan` entering/leaving plan mode, or model restore on resume. Not when a fallback-chain model serves a single turn (the session's model is unchanged).

**Matcher:** same rules as PreModelSwitch (canonical name of the new model).

**Input:** same fields as PreModelSwitch; `source` can also be `auto` (Claude Code's own change; `requested_model` is `null`) or `resume` (`requested_model` = the restored saved setting).

**Output:** can't block. Plain-text stdout on exit 0, or `hookSpecificOutput.additionalContext`, is delivered with the next request. If the hook hasn't finished within 5 s after the next prompt is sent, its output rides on the following request instead. Several switches before the next request → only the last target's output is delivered. Exit 2 shows stderr to the user.

Use for model-specific guidance (e.g. "on Opus, delegate implementation to subagents") without editing every CLAUDE.md. To read the model at session start, SessionStart's optional `model` is the only other source; there is no `$CLAUDE_MODEL`, and `$ANTHROPIC_MODEL` doesn't follow `/model`.
