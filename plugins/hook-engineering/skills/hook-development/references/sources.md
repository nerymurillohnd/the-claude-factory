# Sources and version gates

Read before stating a rule as current, when the installed Claude Code is newer than the version below, or when a user asks where a rule comes from.

## Contents

- Freshness: releases lead, docs follow
- Which source wins
- Doc anchors
- Version gates
- Recent changelog entries that change hook behavior
- Re-verifying

## Freshness: releases lead, docs follow

Docs: [changelog](https://code.claude.com/docs/en/changelog) · [GitHub changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)

Claude Code ships a release every day or two, and the docs catch up later. A release can change or contradict what the docs say.

- **Docs baseline:** hooks reference page as read on 2026-10-20.
- **Changelog baseline: v2.1.305.** Every hook-related entry through that version has been reconciled into this skill. Facts that came from the changelog and weren't in the docs yet are tagged *(changelog vX.Y.Z)*.

Verified against the Claude Code docs and changelog on 2026-10-20, through **v2.1.305** (v2.1.305 from the [GitHub changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md), which listed it before the docs page). v2.1.305 has no hook configuration, input or output change and no prompt, agent or background hook change; its two hook entries are VS Code's "Running start-up hooks" status (in `events-session.md`) and a self-hosted runner fix that is not a Claude Code hook event.

The changelog script in `SKILL.md` reads the `CHANGELOG.md` in github.com/anthropics/claude-code. It prints the hook-related entries released after the baseline and tags those newer than the installed version. Run it with the installed version as the first argument to list what that version lacks.

## Which source wins

When sources disagree, trust them in this order:

1. Observed behavior on the installed version (payload replay, `claude --debug`, the user's own debug log).
2. Changelog entries newer than the docs, up to the installed version. The docs often lag releases by a day or more.
3. The docs page. The raw page (`<page URL>.md`) wins over the docs server's copy when they differ, and both win over a WebFetch summary.
4. This skill's references.
5. Memory.

Report every disagreement you find instead of silently picking one: say which source you followed, and when the docs and the changelog disagree for the user's version, give both and say which version each applies to.

## Doc anchors

All on <https://code.claude.com/docs/en/hooks>:

| Topic | Anchor |
| :-- | :-- |
| Hook input and output | `#hook-input-and-output` |
| Common input fields | `#common-input-fields` |
| Exit code output | `#exit-code-output` |
| Exit code 0 / 2 / other | `#exit-code-0`, `#exit-code-2`, `#other-exit-codes` |
| Timeouts | `#timeouts` |
| Background processes | `#hooks-that-start-a-background-process` |
| onFailure | `#block-the-action-when-a-hook-fails` |
| Windows without Git Bash | `#failed-hooks-on-windows-without-git-bash` |
| Exit code 2 per event | `#exit-code-2-behavior-per-event` |
| HTTP responses | `#http-response-handling` |
| JSON output | `#json-output` |
| terminalSequence | `#emit-terminal-notifications` |
| additionalContext | `#add-context-for-claude` |
| Decision control | `#decision-control` |
| Per-event input and output | `#hook-events`, then `#<event>-input` and `#<event>-decision-control` (or `-output`) |
| Debug log | `#debug-hooks` |

Every other heading in scope is in `docs-map.md`. Changelog: <https://code.claude.com/docs/en/changelog> (generated from <https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md>, which can list a release before the docs page does).

## Version gates

### Configuration

| Feature | Minimum |
| :-- | :-- |
| `onFailure` on command and http hooks | v2.1.295 |
| Prompt and agent hooks run at most 12 at once per event | v2.1.302 |
| Skill hooks capped at 1,024 hooks and 16,384 matcher characters per source per session | v2.1.304 |
| Agent hooks honor `model` aliases and fall back to the caller's model | v2.1.300 |
| A skill's own UserPromptSubmit frontmatter hook first runs on the prompt after the invoking one | v2.1.299 |
| `/plugin` notes plugin hooks left out over a duplicate plugin name | v2.1.296 |
| Plugin marketplace `command` sources (which `allowManagedHooksOnly` disables) | v2.1.229 |
| `allowManagedHooksOnly` blocks marketplace `headersHelper` commands | v2.1.238 |
| Project subagent frontmatter hooks wait for workspace trust | v2.1.218 |
| Shell-form plugin hooks stop substituting `${user_config.*}` | v2.1.207 |
| `$CLAUDE_CODE_BRIDGE_SESSION_ID` | v2.1.199 |
| StopFailure matcher `cloud_credential_error` | v2.1.267 |

### Input and output

| Feature | Minimum |
| :-- | :-- |
| Multi-line JSON response from an async hook | v2.1.295 |
| `Hooks:` duration lines in the debug log | v2.1.296 |
| `scratchpad_dir` input field | v2.1.257 |
| `mcp_server` input object on tool events | v2.1.274 |
| `SubagentHandback` report in `tool_input.message` | v2.1.271 |
| `agent_id` on TeammateIdle | v2.1.290 |
| SessionStart resume cost fields | v2.1.251 |
| PostToolUse `classifierContext` | v2.1.236 |
| WorktreeCreate path screening (`.`/`..`, symlinks) | v2.1.216 |
| Top-level `decision` honored on Elicitation/ElicitationResult again | v2.1.284 (ignored since v2.1.105) |

### Prompt, agent and background hooks

Behaviors the prompt, agent and background hook references rely on that depend on the Claude Code version (a row the tables above already hold appears here only when it adds detail):

| Version | Change |
| :-- | :-- |
| 2.1.218 | Project subagent frontmatter hooks require that folder's trust; they never run under `-p` |
| 2.1.287 | `asyncRewake` with a missing script is reported once instead of waking Claude repeatedly |
| 2.1.288 | Prompt hooks work behind gateways that reject structured outputs; `CLAUDE_CODE_DISABLE_STRUCTURED_OUTPUTS` added |
| 2.1.290 | Fixed an endless reply loop from a plugin's async Stop hook with an unquoted path containing a space |
| 2.1.294 | Prompt and agent hooks written as rules no longer allow what they should block; Stop and SubagentStop rule prompts judged better |

### Mods

Mods are on by default from v2.1.287 in the terminal and from v2.1.286 in the Desktop app (<https://code.claude.com/docs/en/plugins/mods/overview#turn-mods-on-or-off>); the admin page says v2.1.286 for both (<https://code.claude.com/docs/en/plugins/mods/admin>), a docs inconsistency recorded on 2026-10-20. A mod's `tool.check` approval doesn't skip the prompt for a tool that requires user interaction from v2.1.292 (<https://code.claude.com/docs/en/permissions#precedence-among-rules-hooks-and-mods>).

## Recent changelog entries that change hook behavior

- v2.1.304: skill hooks are capped per source per session (1,024 hooks, 16,384 matcher characters).
- v2.1.304: under a policy that allows hooks from plugins only, a skill used in the main conversation whose hooks are kept out no longer gets its `allowed-tools`.
- v2.1.304: fixed a skill's `once` hook also removing another skill's identical hook.
- v2.1.302: at most 12 prompt or agent hooks of one event run at a time.
- v2.1.300: fixed plugin WorktreeCreate and WorktreeRemove hooks not running with `--worktree`.
- v2.1.300: `updatedInput` from PreToolUse and PermissionRequest is validated like Claude's own input; unknown keys are dropped and input the tool rejects denies the call.
- v2.1.300: in Cowork cloud sessions, a `setMode` update in a PermissionRequest allow is ignored.
- v2.1.300: fixed agent hooks ignoring their `model`: aliases like `haiku` now resolve, a subagent's model no longer overrides it, and an unavailable model falls back to the caller's instead of allowing the action.
- v2.1.299: Windows: PreToolUse and PermissionRequest hooks that set no shell now fail closed when Git for Windows isn't installed.
- v2.1.299: UserPromptSubmit runs before a skill or custom command expands, so a block also stops the skill's embedded shell commands.
- v2.1.299: in Cowork cloud sessions under auto mode, a PermissionRequest hook can't approve shell commands or subagents.
- v2.1.290: fixed an endless loop when a plugin's async Stop hook passed an unquoted script path under a folder with a space.

## Re-verifying

These steps read sources; they never edit this plugin's files. Keeping the references current is the plugin maintainer's job.

1. `claude --version`.
2. If newer than the version above, read every changelog entry after v2.1.305 up to it (the changelog script in `SKILL.md` lists the ones that name `hook`, `matcher`, an event other than a bare `Stop`, or a hook field) and search them by hand for `settings` too.
3. Re-read the sections for the topic you are answering. Precedence when sources disagree: Which source wins, above. Say which source you followed and note the difference in your answer.
4. If you can't reach the docs, state the rule as "as of v2.1.305" and mark it unverified for newer versions. If a source can't be reached, say which, and mark every version-sensitive claim `unverified against live docs`.
