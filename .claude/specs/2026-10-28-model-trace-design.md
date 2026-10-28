# model-trace: design

Status: approved by Nery on 2026-10-28, scope narrowed the same day to "only what Claude uses"; built and checked on Claude Code 2.1.312.

## Goal

A mod that shows, live, each skill, agent, MCP server, plugin, hook and web tool (WebSearch, WebFetch) Claude uses in the session: the name, how many times, and the exact local time of each use. A capability appears the first time it is used and its count grows with each use. Names and counts only: never tool rows, commands, arguments or prompts. Export to Markdown or HTML.

Not shown: what is available and never used (dropped by Nery on 2026-10-28). Claude Code's own `/skill-doctor`, `/doctor`, `/usage` and the Not used recently header of `/plugin` cover unused capabilities and their cost; the README points to them.

## Identity

- Name `model-trace`, display name "Model Trace", command `/model-trace [md | html]`.
- Category `mods`; Claude Code only (mods draw in the terminal, the Desktop Code tab and the VS Code extension; they don't load in Cowork or chat).
- Session only: `$.state`, which `/clear`, `/resume` and `/branch` reset. Nothing persists except what the user exports.
- Minimum Claude Code v2.1.299 (`Text` `weight`, `skill.prompt` `source` and `pluginName`); tested with v2.1.312.

## Signals

| Category | Counted from |
| :-- | :-- |
| Skills | The `Skill` tool call (`tool.call`), once it ran. A `skill.prompt` raised inside that call only names the skill's origin. A `skill.prompt` outside any Skill call (a `/skill` the user typed, a subagent's preloaded skill) counts on its own |
| Agents | `agent.spawn` that started (no `deny`), resumes skipped: `subagentType`, `provider.plugin` |
| MCP servers | `tool.call` of `mcp__<server>__<tool>` that ran; server only. `plugin_<plugin>_<server>` names a plugin's server; `claude_ai_<Name>` a claude.ai connector |
| Web | `tool.call` of `WebSearch` and `WebFetch` that ran, subagent calls included |
| Plugins | A roll-up: the uses of each plugin's skills, agents and MCP servers. Left out of the totals |
| Hooks | Settings hooks of every `$.settings.read({ source })` layer, named by `statusMessage`, else the file name of the program they run, else their type; counted when `classic.<Event>` fires and the matcher selects the fire, per the hooks docs' matcher rules and match fields. An `if` condition is not evaluated: the row says its count is an upper bound. Hook output that reached Claude (`session.append` origin `hook`), by event: shown, left out of the totals |

A call refused by a permission rule, a hook or another mod is not a use.

Settings hooks fire before `session.start` (`SessionStart`, `InstructionsLoaded`), so they are read on the first fire, not at session start.

Totals count each use once: Plugins and hook output rows are excluded, since they regroup or repeat uses other rows count.

## Limits a mod can't get past

- Which plugin's `hooks/hooks.json` hook ran is not visible to a mod; plugin hooks show only as hook output by event.
- Where the built-in guard loads (managed settings, or a Team or Enterprise login), a user's mod gets no `classic.*`, `skill.prompt` or `session.append{door=hook-context}` events: skills still count through the Skill tool, with the origin read from the name, while hooks and the origin of a typed `/skill` are missing.

## Behavior

- Every hook observes only: it calls `next(e)`, records, and returns `next`'s result. Recording is wrapped so a failure never changes a call; each hook has a `.catch` that returns `next(e)`, which replays a result already reached.
- `/model-trace` opens a pane with `focus` and `closeOnEscape`, and returns nothing Claude reads; where no pane draws (`claude -p`), it answers a text summary. `/model-trace md|html` writes the report.
- After `/clear`, `/resume` or `/branch`, `classic.SessionStart` with that source dates the new trace.
- Optional status line (`statusLine`, default off, because Claude Code prefixes every mod's status line with a warning sign).
- Pane: header (capabilities, uses, since); sections in a fixed order, each with its rows in first-use order; row = name, origin, `×N`, last time; pressing a row shows every time; eight rows per section, then "+ N more". Footer: plain buttons with hotkeys `m` Save .md, `h` Save .html, `c` Copy Markdown.
- Export: `$.fs.write` to `exportDir` (default `~/Downloads`, `~` from `HOME`), `model-trace-<YYYYMMDD-HHMMSS>.md|html`; the folder must exist. The HTML is self-contained (inline CSS, light and dark, no script, no external resource).

## Out of scope

History across sessions; token or cost figures; unused capabilities; tool rows and arguments.
