# agent-files-diagnostics: workflow-based design (2026-10-15)

Design record of the rebuild of `agent-files-diagnostics` on dynamic workflows, from Nery's
specification "Evidence-Based Instruction and Memory Audit Plugin" (2026-10-15). It replaces the
14-phase, prompt-only design of 2026-10-14 and the script-driven `agent-context-audit` branch,
from which it takes the deterministic engine.

## Decisions

| Decision | Why |
| :-- | :-- |
| Scope: the Markdown that Claude Code and Codex load as instructions and memory (`CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, `AGENTS.override.md`, rules, auto memory, subagent memory, subagent definitions, output styles, `loop.md`, Codex memories, and the Markdown they import). Configuration (settings, hooks, MCP, Codex config) is consulted as evidence of what loads, never audited; skills, commands and plugins are counted, never reviewed | Nery, 2026-10-15: the branch had over-designed into settings and MCP |
| Execution mechanism: two plugin workflows (`audit-domains`, `review-and-verify`) coordinating four read-only plugin agents; the main session is the coordinator and the accountable reviewer; deterministic stages are a Python package driven by the skill between the workflows | The specification (section 1); workflows cannot take user input mid-run and have no filesystem, so validation and the coordinator's own inspection sit between them |
| Results flow through Claude Code's workflow journal (`~/.claude/projects/<project>/<session>/subagents/workflows/<run>/`): `accept` reads each agent's structured result from `journal.jsonl` and proves coverage from the agent transcripts (`agent-<id>.jsonl`) | Keeps the coordinator's context free of the agents' output; the transcript is the only proof that every line reached an agent |
| No substitution when workflows are unavailable: the skill stops and says so | The specification (section 1) |
| Domains fixed by file type: A Codex files and every `AGENTS.md`, B the `CLAUDE.md` family, C rules, D memory, E extensions; one package per domain, split only by size | The specification (sections 1 and 3): ownership never overlaps |
| Four per-source fields: loading (`automatic`, `conditional`, `on-demand`, `unknown`), consumption (`verified`, `documented-not-observed`, `unverified`), availability (`complete`, `truncated`, `inaccessible`, `opaque`), applicability (`applicable`, `excluded`, `superseded`, `unresolved`); consumption is never `verified` because the audit observes no session | The specification (section 3) |
| Two identities per unit: the text identity (hash of the normalized text) and the occurrence identity (hash of path and text, numbered on repeats); finding IDs use the occurrence | The specification (section 3) |
| The coordinator inspects every reported finding itself and records `ok` or a rejection in `checked.json`; an uninspected finding makes the run `partial` | The specification (section 7) |
| Workflow scripts are excluded from Biome (`!!plugins/*/workflows`) | They use the top-level `return` the workflow runtime provides, which no JavaScript parser accepts; a unit test checks that the schemas embedded in them equal the JSON schemas the Python validator uses |
| Claude Code only, minimum 2.1.300 (the version the run was tested on); workflows do not load in the Claude app | `cross-surface-compatibility.md` matrix |

## Facts verified (Claude Code docs MCP, 2026-10-15)

| Fact | Source |
| :-- | :-- |
| A plugin ships workflows in `workflows/`; a plugin workflow runs as `/<plugin>:<meta.name>`; the `workflows` manifest field replaces the default scan | `/en/workflows.mdx:220,222`; `/en/plugins/components.mdx:547`; `/en/plugins/manifest-reference.mdx:151` |
| Workflows on all paid plans and API access; Pro turns them on in `/config`; `disableWorkflows`, `CLAUDE_CODE_DISABLE_WORKFLOWS` turn them off | `/en/workflows.mdx:6,483-487`; `/en/settings-reference.mdx:660,668` |
| No mid-run user input; the script has no filesystem, shell or module access; `Date.now()`, `Math.random()`, `new Date()` throw | `/en/workflows.mdx:330,358-360` |
| `schema` is checked before the agent starts and the output is validated with five attempts; `agent()` resolves to `null` on a stop or an unrecoverable error and `pipeline()`/`parallel()` keep the `null` | `/en/workflows.mdx:311,315,317` |
| 16 concurrent agents by default (`CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS`, 2.1.269+); 4,096 items per call; 1,000 agents per run; workflow agents sit outside the 20-subagent Agent-tool cap | `/en/workflows.mdx:361,363,364`; `/en/sub-agents.mdx:1056` |
| Workflow agents use the session's permission rules; plugin agents ignore `permissionMode`, `hooks`, `mcpServers`; `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` covers workflow agents | `/en/workflows.mdx:192`; `/en/sub-agents.mdx:235,394` |
| Workflows run in the CLI, Desktop, IDE, `claude -p` and the SDK; results are saved under `~/.claude/projects/` and a same-session `resumeFromRunId` replays them | `/en/workflows.mdx:338,393,479`; `/en/agent-sdk/typescript.mdx:3264` |
| Subagent transcripts are kept 30 days by default; a plugin agent whose frontmatter fails to parse loads with every field ignored and the description `Agent from <plugin> plugin` | `/en/sub-agents.mdx:1125`; `/en/plugins/components.mdx:737` |

## Facts verified by experiment (2026-10-15, Claude Code 2.1.300)

A throwaway plugin with one agent (`model: claude-sonnet-5-5`, `effort: low`, `tools: Read, Grep, Glob`, `omitClaudeMd: true`) and one workflow calling `agent(prompt, {agentType: 'probe-plugin:probe-agent', schema})` next to a `general-purpose` control, run with `claude -p "/probe-plugin:probe" --plugin-dir`:

| Property | Plugin agent | Control | Evidence |
| :-- | :-- | :-- | :-- |
| `tools` | Read, Grep, Glob (+ StructuredOutput); "no Write tool" | Bash, Edit, Write, MCP tools; wrote a file | journal results and transcripts |
| `omitClaudeMd` | no `CLAUDE.md` attachment; marker not seen | attachment with `CLAUDE.md`; marker seen | transcripts |
| `model` | `claude-sonnet-5-5` on every API request | `claude-haiku-5-5` (the session's) | transcripts |
| `effort` | `low` | `medium` | transcripts |

Cost $0.03, 7 seconds. The journal records `{"type":"started","label","agentId"}` and `{"type":"result","agentId","result"}` per agent; a `Read` tool result in a transcript is `N<TAB>text` lines.

## Not documented, handled by design

- How the Workflow tool's `name` addresses a plugin workflow: the skill uses `agent-files-diagnostics:<name>`; the isolated run checks it.
- Whether `SubagentStart` hooks fire for workflow agents; per-agent token counts in the tool result (the script sums them from transcripts instead).
- A wall-clock limit for a run: none; only stall restarts (five at most per agent).
