# Debug your configuration

How to diagnose why CLAUDE.md, settings, hooks, MCP servers or skills aren't taking effect, using `/context`, `/doctor`, `/hooks` and `/mcp` to see what actually loaded.

When Claude ignores an instruction or a configured feature doesn't appear, the cause is usually one of three: the file didn't load, it loaded from a different location than expected, or another file overrode it. Inspect what Claude Code actually loaded to narrow down which one applies.

## Contents

- [See what loaded into context](#see-what-loaded-into-context)
- [Check resolved settings](#check-resolved-settings)
- [Check MCP servers](#check-mcp-servers)
- [Check hooks](#check-hooks)
- [Test against a clean configuration](#test-against-a-clean-configuration)
- [Check common causes](#check-common-causes)
- [Documentation References](#documentation-references)

## See what loaded into context

Run `/context` first. It shows everything occupying the context window for the current session, broken down by category: system prompt, system tools, MCP tools, custom subagents with the source each loaded from, memory files, skills, and conversation messages. Use it to confirm whether a `CLAUDE.md`, rules or skill descriptions are present at all. The skills section in `/context` also includes [bundled skills](https://code.claude.com/docs/en/skills.md#bundled-skills), which `/skills` doesn't list.

In [fullscreen mode](https://code.claude.com/docs/en/fullscreen.md), `/context` collapses the per-item breakdown; run `/context all` to expand it.

For detail on a specific category, follow up with the dedicated command:

| Command | Shows |
| :- | :- |
| `/skills` | Available skills from project, user, and plugin sources |
| `/hooks` | Active hook configurations |
| `/mcp` | Connected MCP servers and their status |
| `/doctor` | Setup checkup: installation health, invalid settings files, unused extensions, duplicate [subagent](https://code.claude.com/docs/en/sub-agents.md) names in the same directory, and checked-in `CLAUDE.md` content Claude can derive from the codebase, with proposed fixes |
| `/debug [issue]` | Enables debug logging for the session and prompts Claude to diagnose using the log output and settings paths |
| `/status` | Active settings sources, including whether managed settings are in effect |

## Check resolved settings

Settings merge across managed, user, project, and local scopes. Managed settings apply first when present. Among the rest, the closer scope overrides the broader one, in the order local, then project, then user. Some settings can also be set by command-line flags or [environment variables](https://code.claude.com/docs/en/env-vars.md), which act as another override layer. When a setting doesn't seem to apply, the configured value is usually being overridden by another scope or by an environment variable.

- To find invalid settings files, run `claude doctor` from the terminal. It prints read-only installation and settings diagnostics without starting a session.
- For a full checkup that also proposes fixes and asks before applying them, run [`/doctor`](https://code.claude.com/docs/en/commands#all-commands) inside a session.
- Run `/status` to see which settings sources are active, including whether managed settings are in effect.
- To determine which scope Claude Code uses for a given key, see [Settings precedence](https://code.claude.com/docs/en/settings.md#settings-precedence).

## Check MCP servers

Run `/mcp` to see every configured server, its connection status, and whether it has been approved for the current project. A server can be defined correctly and still provide no tools, for these common reasons:

* A server that fails to start shows as failed in `/mcp`. Relative file paths in `command` or `args` are a frequent cause, since they resolve against the directory Claude Code was launched from rather than the location of `.mcp.json`.
* A server that shows as connected but lists zero tools has started successfully but isn't returning a tool list. Select **Reconnect** from `/mcp`. If the count stays at zero, run `claude --debug=mcp` and read the server's stderr in the debug log at `~/.claude/debug/<session-id>.txt`.

For configuration locations and scope rules, see [MCP](https://code.claude.com/docs/en/mcp.md).

## Check hooks

Run `/hooks` to list every hook registered for the current session, grouped by event. If a defined hook doesn't appear, Claude Code didn't load it. Check for these causes:

* The `matcher` value is an array instead of a single string. Claude Code lists the entry as an invalid setting when an interactive session starts and in `claude doctor`. If the array is under `PreToolUse` or `PermissionRequest`, none of that file's other hooks load either.
* The hook is in a skill's frontmatter, and nobody (neither the user nor Claude) has invoked the skill yet in this session. Invoke the skill, then run `/hooks` again. If the hook still doesn't appear, check for other causes, such as [frontmatter that didn't parse](https://code.claude.com/docs/en/skills.md#skill-not-triggering) or one of the [limits on skill hooks](https://code.claude.com/docs/en/hooks.md#limits-on-skill-hooks).

If the hook appears but doesn't fire, the matcher is the usual cause. Check it for these mistakes:

* The `matcher` field is a single string that uses `|` to match multiple tool names, for example `"Edit|Write"`. A `,` separator is equivalent, so `"Edit,Write"` matches the same tools. Before v2.1.191, a comma fell through to regex evaluation and the matcher never matched, so use `|` on any version earlier than v2.1.191.
* A misspelled tool name produces a matcher that matches nothing, so the hook fails silently.

If `/hooks` shows the hook but it still does not fire, watch hook evaluation live: start a session with `claude --debug` and trigger the tool call. The debug log records each event, which matchers were checked, and the hook's exit code and output. See [Debug hooks](https://code.claude.com/docs/en/hooks.md#debug-hooks) for the log format and [hooks troubleshooting](https://code.claude.com/docs/en/hooks-guide.md#limitations-and-troubleshooting) for common failure patterns.

## Test against a clean configuration

Start with [`claude --safe-mode`](https://code.claude.com/docs/en/cli-reference#cli-flags), which launches a session with customizations disabled, including:

* `CLAUDE.md`
* Skills, plugins, and hooks
* MCP servers
* Custom commands and agents
* Custom output styles
* Custom keybindings

Authentication, model selection, built-in tools, and permissions work normally. If the problem disappears in safe mode, the cause is one of the disabled items. To find which, run the check for that item, such as [See what loaded into context](#see-what-loaded-into-context), [Check MCP servers](#check-mcp-servers), or [Check hooks](#check-hooks).

If the problem persists in safe mode, or the settings themselves are suspect, start a session with none of the user's own configuration and check whether the problem follows. Follow these steps.

**1. Create an empty directory and change into it**

In the shell, with no Claude Code session running, create the directory and move into it:

> [tab] Bash or Zsh
>
> ```bash theme={null}
> mkdir -p ~/claude-clean/empty && cd ~/claude-clean/empty
> ```

> [tab] PowerShell
>
> ```powershell theme={null}
> New-Item -ItemType Directory -Force "$HOME/claude-clean/empty" | Out-Null
> Set-Location "$HOME/claude-clean/empty"
> ```

**2. Start Claude Code with a clean configuration directory**

From the same shell, set [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/en/env-vars) to a fresh directory in place of `~/.claude`, and pass [`--setting-sources user`](https://code.claude.com/docs/en/cli-reference#cli-flags) to turn off project configuration such as `.claude/settings.json`, `CLAUDE.md`, and `.mcp.json`:

> [tab] Bash or Zsh
>
> The variable applies to this one launch.
>
> ```bash theme={null}
> CLAUDE_CONFIG_DIR=~/claude-clean/config claude --setting-sources user
> ```

> [tab] PowerShell
>
> The variable stays set for the rest of this PowerShell session, so later `claude` launches in the same window keep using the clean directory. To return to the usual directory, run `Remove-Item Env:CLAUDE_CONFIG_DIR` before the next launch.
>
> ```powershell theme={null}
> $env:CLAUDE_CONFIG_DIR = "$HOME/claude-clean/config"
> claude --setting-sources user
> ```

On the first launch, the first-run setup screens appear again, which confirms that the clean configuration directory is in effect. Managed settings still apply, and [connectors](https://code.claude.com/docs/en/mcp.md#use-mcp-servers-from-claude-ai) still load when logged in with a claude.ai account.

**3. Reproduce the problem**

Repeat what triggered the problem in the clean session, then act on the result:

* **Problem gone**: the cause is in the user or project configuration. Copy `~/.claude.json` and the files in `~/.claude` into `~/claude-clean/config` one at a time. If none brings the problem back, go to the project directory in the same shell and start Claude Code without `--setting-sources user`. In Bash or Zsh, run `CLAUDE_CONFIG_DIR=~/claude-clean/config claude`. In PowerShell, the variable is still set, so run `claude`.
* **Problem persists**: the cause is outside the user and project configuration. Run `/status` in the session to check for managed settings, check the shell for [environment variables](https://code.claude.com/docs/en/env-vars.md), then see [Troubleshooting](https://code.claude.com/docs/en/troubleshooting.md).

## Check common causes

Most configuration surprises trace back to a small set of location and syntax rules. Check these before assuming a bug:

| Symptom | Cause | Fix |
| :- | :- | :- |
| Hook never fires | `matcher` is a JSON array instead of a string | Use a single string with `\|` to match multiple tools, for example `"Edit\|Write"`. See [matcher patterns](https://code.claude.com/docs/en/hooks.md#matcher-patterns). |
| Hook never fires | `matcher` uses `,` as a separator on a version before v2.1.191 | Claude Code v2.1.191 or later treats `,` as a list separator like `\|`. Earlier versions evaluate a comma as a literal character, so `"Edit,Write"` matches nothing. Use `\|` instead, or upgrade Claude Code. |
| Hook never fires | `matcher` value is lowercase, for example `"bash"` | Matching is case-sensitive. Tool names are capitalized: `Bash`, `Edit`, `Write`, `Read`. |
| Hook never fires | Hooks are defined in a standalone file instead of `settings.json` | There is no standalone hooks file for project or user config. Define hooks under the `"hooks"` key in `settings.json`. Only [plugins](https://code.claude.com/docs/en/plugins/components.md#hooks) load a separate `hooks/hooks.json`. See [hook configuration](https://code.claude.com/docs/en/hooks.md). |
| Skill doesn't appear in `/skills` | Skill file is at `.claude/skills/name.md` instead of in a folder | Use a folder with `SKILL.md` inside: `.claude/skills/name/SKILL.md`. |
| Skill appears in `/skills` but Claude never invokes it | Skill has `disable-model-invocation: true` in its frontmatter, or its description doesn't match how you phrase the request | Check the badge in `/skills`: a "user-only" label means Claude won't trigger it on its own. See [skill invocation](https://code.claude.com/docs/en/skills.md). |
| MCP servers in `.mcp.json` never load | File is under `.claude/`, or its servers sit under a top-level `servers` key, as in VS Code's `mcp.json`, instead of `mcpServers` | Project MCP config goes at the repository root as `.mcp.json`, not inside `.claude/`, with servers under the `mcpServers` key. See [MCP configuration](https://code.claude.com/docs/en/mcp.md). |
| MCP server fails to start from some directories | `command` or `args` uses a relative file path | Use absolute paths for local scripts. Executables on your `PATH` like `npx` or `uvx` work as-is. |
| MCP server starts without expected environment variables | The server's config entry doesn't set them, and they aren't in the environment Claude Code passes to stdio servers: its own environment, minus the [variables it strips from subprocesses](https://code.claude.com/docs/en/monitoring-usage.md#administrator-configuration) | Set per-server `env` inside the server's `.mcp.json` entry, which doesn't depend on the launch environment or workspace trust. |

## Documentation References

- Source page: https://code.claude.com/docs/en/debug-your-config — the full configuration debugging guide.
- https://code.claude.com/docs/en/skills.md — skills, bundled skills, invocation, and why a skill does not trigger.
- https://code.claude.com/docs/en/fullscreen.md — fullscreen mode and how it changes `/context` output.
- https://code.claude.com/docs/en/sub-agents.md — subagents and where they are defined.
- https://code.claude.com/docs/en/env-vars.md — environment variables that override settings.
- https://code.claude.com/docs/en/env-vars — the same environment variables page, linked without `.md` for `CLAUDE_CONFIG_DIR`.
- https://code.claude.com/docs/en/commands — built-in commands, including `/doctor`.
- https://code.claude.com/docs/en/settings.md — settings scopes and settings precedence.
- https://code.claude.com/docs/en/mcp.md — MCP configuration locations, scope rules, approval, `/mcp` output and claude.ai connectors (also listed in the removed "Related resources" section).
- https://code.claude.com/docs/en/hooks.md — hooks reference: event names, payloads, matcher patterns, skill hook limits and `--debug` output format (also listed in the removed "Related resources" section).
- https://code.claude.com/docs/en/hooks-guide.md — hooks guide, limitations and troubleshooting.
- https://code.claude.com/docs/en/cli-reference — CLI flags such as `--safe-mode` and `--setting-sources`.
- https://code.claude.com/docs/en/troubleshooting.md — general troubleshooting for problems outside user and project configuration.
- https://code.claude.com/docs/en/plugins/components.md — plugin components, including plugin `hooks/hooks.json`.
- https://code.claude.com/docs/en/monitoring-usage.md — administrator configuration, including variables stripped from subprocesses.
