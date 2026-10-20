# Map of the official docs

Read before citing, checking or re-verifying any fact about prompt, agent or background hooks, hook security, PowerShell hooks or hook debugging. It says where each fact lives in the official source and how to fetch it.

> Precedence: the changelog and the user's own debug log win over the docs for released behavior; the docs win over this map; this map wins over memory. When the docs and the changelog disagree for the user's version, report both and say which version each applies to.

## Contents

- How to use this map
- Retrieve a section's exact text
- Read the changelog for a version range
- Hooks reference: prompt and agent hooks
- Hooks reference: events that accept prompt and agent hooks
- Hooks reference: background hooks
- Hooks reference: security, PowerShell, debugging
- Hooks reference: supporting sections
- Hooks guide
- Other pages
- Out of scope: where to point

## How to use this map

- Each row gives the **header exactly as it appears in the source**, with its Markdown level, and the **URL with its anchor**. Cite the URL; search the source for the header.
- **Verified by** says how the anchor was confirmed on 2026-10-20 (Claude Code 2.1.305):
  - `link`: an official docs page links to that exact anchor.
  - `search`: the official docs search returns that exact URL for the section.
  - `slug`: derived from the header by the same rule as the verified anchors around it. Confirm it the first time you cite it.
- Anchors keep some punctuation: `/hooks` in a header becomes `%2F` in one page's link and stays `/` in another's search result. Copy anchors from this map; never rebuild them by hand.
- When a header in this map is no longer found in the source, the section was renamed or removed. Say so, search the page for the topic, cite what you find, and flag the map entry as stale in your report.

## Retrieve a section's exact text

Prefer raw Markdown over summaries. Each page serves raw Markdown at its URL plus `.md`, such as <https://code.claude.com/docs/en/hooks.md>.

1. **Shell (default, exact text):** fetch the page once and cut the section by its exact header. The section ends at the next header of the same or a higher level:

   ```bash
   curl -sS https://code.claude.com/docs/en/hooks.md |
     awk -v h='### Response schema' '
       $0 == h { p = 1; n = index(h, " ") - 1; print; next }
       p && /^#+ / { m = index($0, " ") - 1; if (m <= n) exit }
       p'
   ```

2. **Claude Code Docs MCP (main session, when connected):** read `/en/hooks.mdx` with the filesystem tool, for example `rg -n -F '### Response schema' /en/hooks.mdx` and then `sed -n '<line>,<line+60>p' /en/hooks.mdx`. Its index can be incomplete: if a header from this map is missing there, use the search tool, whose `Link` field gives the live anchor, or the shell route.
3. **WebFetch (last resort):** it returns a model's summary, not the source. Use it only to locate a section, never to quote a field, default or version. Mark anything that rests on it `unverified against live docs`.

If none of the three reaches the docs, say so and mark every version-sensitive claim `unverified against live docs`.

## Read the changelog for a version range

The docs describe the latest release and often lag it by a release; fixes and behavior changes often appear only in the changelog.

| Source | URL | Use |
| :-- | :-- | :-- |
| Raw changelog (newest first, `## <version>` headers) | <https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md> | Primary. Updated with each release |
| Docs changelog page | <https://code.claude.com/docs/en/changelog> | Cross-check; can trail the raw file by a release |

List the hook entries of every release newer than the user's version (replace `2.1.294` with the version `claude --version` prints). Those changes are not in the user's build; the docs may already describe them:

```bash
curl -sS https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md |
  awk -v stop='2.1.294' '/^## /{ v = $2; if (v == stop) exit } v' |
  grep -i -E 'hook|asyncRewake|ARGUMENTS|continueOnBlock|stop_hook|disableAllHooks|trust'
```

Read each matching line in its release, then apply the precedence rule above.

## Hooks reference: prompt and agent hooks

| Header in source | URL | Settles | Verified by |
| :-- | :-- | :-- | :-- |
| `## Prompt-based hooks` | <https://code.claude.com/docs/en/hooks#prompt-based-hooks> | Which events take which hook types | link |
| `### How prompt-based hooks work` | <https://code.claude.com/docs/en/hooks#how-prompt-based-hooks-work> | Single model call; default model | search |
| `### Prompt hook configuration` | <https://code.claude.com/docs/en/hooks#prompt-hook-configuration> | `prompt`, `$ARGUMENTS`, `model`, `timeout`, `continueOnBlock` | link |
| `### Response schema` | <https://code.claude.com/docs/en/hooks#response-schema> | `ok`, `reason`, `impossible`; what `ok: false` does per event | link |
| `### Check multiple conditions before stopping` | <https://code.claude.com/docs/en/hooks#check-multiple-conditions-before-stopping> | Multi-condition Stop example | search |
| `## Agent-based hooks` | <https://code.claude.com/docs/en/hooks#agent-based-hooks> | Experimental status; events | link |
| `### How agent hooks work` | <https://code.claude.com/docs/en/hooks#how-agent-hooks-work> | Up to 50 turns; example tools; block handling | search |
| `### Agent hook configuration` | <https://code.claude.com/docs/en/hooks#agent-hook-configuration> | 60 s default; no `continueOnBlock`, no `impossible` | link |
| `#### Prompt and agent hook fields` | <https://code.claude.com/docs/en/hooks#prompt-and-agent-hook-fields> | `\$` escaping in `prompt` | link |
| `#### Common fields` | <https://code.claude.com/docs/en/hooks#common-fields> | `if`, `timeout` defaults, `statusMessage`, `once` | link |
| `### Hook handler fields` | <https://code.claude.com/docs/en/hooks#hook-handler-fields> | Parallel runs; 12-at-once limit; duplicate handlers | link |
| `### Hooks in skills and agents` | <https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents> | Lifetime of frontmatter hooks; `Stop` → `SubagentStop` | link |

## Hooks reference: events that accept prompt and agent hooks

Each event has an overview section and an input section. The input section lists the fields a prompt can point at through `$ARGUMENTS`.

| Event | Overview header · URL | Input header · URL | Verified by |
| :-- | :-- | :-- | :-- |
| PreToolUse | `### PreToolUse` · <https://code.claude.com/docs/en/hooks#pretooluse> | `#### PreToolUse input` · <https://code.claude.com/docs/en/hooks#pretooluse-input> | link · link |
| PostToolUse | `### PostToolUse` · <https://code.claude.com/docs/en/hooks#posttooluse> | `#### PostToolUse input` · <https://code.claude.com/docs/en/hooks#posttooluse-input> | link · slug |
| PostToolUseFailure | `### PostToolUseFailure` · <https://code.claude.com/docs/en/hooks#posttoolusefailure> | `#### PostToolUseFailure input` · <https://code.claude.com/docs/en/hooks#posttoolusefailure-input> | link · slug |
| PostToolBatch | `### PostToolBatch` · <https://code.claude.com/docs/en/hooks#posttoolbatch> | `#### PostToolBatch input` · <https://code.claude.com/docs/en/hooks#posttoolbatch-input> | link · slug |
| PermissionDenied | `### PermissionDenied` · <https://code.claude.com/docs/en/hooks#permissiondenied> | `#### PermissionDenied input` · <https://code.claude.com/docs/en/hooks#permissiondenied-input> | link · slug |
| PermissionRequest (prompt only) | `### PermissionRequest` · <https://code.claude.com/docs/en/hooks#permissionrequest> | `#### PermissionRequest input` · <https://code.claude.com/docs/en/hooks#permissionrequest-input> | link · link |
| UserPromptSubmit | `### UserPromptSubmit` · <https://code.claude.com/docs/en/hooks#userpromptsubmit> | `#### UserPromptSubmit input` · <https://code.claude.com/docs/en/hooks#userpromptsubmit-input> | link · slug |
| UserPromptExpansion | `### UserPromptExpansion` · <https://code.claude.com/docs/en/hooks#userpromptexpansion> | `#### UserPromptExpansion input` · <https://code.claude.com/docs/en/hooks#userpromptexpansion-input> | link · slug |
| Stop | `### Stop` · <https://code.claude.com/docs/en/hooks#stop> | `#### Stop input` · <https://code.claude.com/docs/en/hooks#stop-input> | link · link |
| SubagentStop | `### SubagentStop` · <https://code.claude.com/docs/en/hooks#subagentstop> | `#### SubagentStop input` · <https://code.claude.com/docs/en/hooks#subagentstop-input> | link · slug |
| TaskCreated | `### TaskCreated` · <https://code.claude.com/docs/en/hooks#taskcreated> | `#### TaskCreated input` · <https://code.claude.com/docs/en/hooks#taskcreated-input> | link · slug |
| TaskCompleted | `### TaskCompleted` · <https://code.claude.com/docs/en/hooks#taskcompleted> | `#### TaskCompleted input` · <https://code.claude.com/docs/en/hooks#taskcompleted-input> | link · slug |
| TeammateIdle | `### TeammateIdle` · <https://code.claude.com/docs/en/hooks#teammateidle> | `#### TeammateIdle input` · <https://code.claude.com/docs/en/hooks#teammateidle-input> | link · slug |
| Fields every event sends | `### Common input fields` · <https://code.claude.com/docs/en/hooks#common-input-fields> | — | link |
| All events, one per section | `## Hook events` · <https://code.claude.com/docs/en/hooks#hook-events> | — | link |

## Hooks reference: background hooks

| Header in source | URL | Settles | Verified by |
| :-- | :-- | :-- | :-- |
| `## Run hooks in the background` | <https://code.claude.com/docs/en/hooks#run-hooks-in-the-background> | Async hooks cannot block or decide | link |
| `### Configure an async hook` | <https://code.claude.com/docs/en/hooks#configure-an-async-hook> | `async` is command-only; `timeout` not enforced; `-p` teardown | search |
| `### How async hooks execute` | <https://code.claude.com/docs/en/hooks#how-async-hooks-execute> | Delivered fields; stdout rules; dropped fields; verbose notices | link |
| `### Run tests after file changes` | <https://code.claude.com/docs/en/hooks#run-tests-after-file-changes> | Worked example | search |
| `### Limitations` | <https://code.claude.com/docs/en/hooks#limitations> | Next-turn delivery; `asyncRewake` exit 2 wakes Claude | search |
| `#### Command hook fields` | <https://code.claude.com/docs/en/hooks#command-hook-fields> | `async`, `asyncRewake`, `shell` field definitions | link |
| `#### Hooks that start a background process` | <https://code.claude.com/docs/en/hooks#hooks-that-start-a-background-process> | A synchronous hook that leaves a process running | link |

## Hooks reference: security, PowerShell, debugging

| Header in source | URL | Settles | Verified by |
| :-- | :-- | :-- | :-- |
| `## Security considerations` | <https://code.claude.com/docs/en/hooks#security-considerations> | Section entry point | link |
| `### Disclaimer` | <https://code.claude.com/docs/en/hooks#disclaimer> | Full-user-permission warning | search |
| `### Workspace trust` | <https://code.claude.com/docs/en/hooks#workspace-trust> | Interactive vs `-p`/SDK trust; mitigations | link |
| `### Security best practices` | <https://code.claude.com/docs/en/hooks#security-best-practices> | Validate, quote, traversal, absolute paths, sensitive files | search |
| `## Windows PowerShell tool` | <https://code.claude.com/docs/en/hooks#windows-powershell-tool> | `shell: "powershell"`; placeholder rewriting; bare `$CLAUDE_PROJECT_DIR` | link |
| `## Debug hooks` | <https://code.claude.com/docs/en/hooks#debug-hooks> | Debug log paths; `Hooks:` lines; verbose level | link |

## Hooks reference: supporting sections

| Header in source | URL | Settles | Verified by |
| :-- | :-- | :-- | :-- |
| `##### Exec form and shell form` | <https://code.claude.com/docs/en/hooks#exec-form-and-shell-form> | `args` vs shell; quoting placeholders | link |
| `### Reference scripts by path` | <https://code.claude.com/docs/en/hooks#reference-scripts-by-path> | `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`; worktrees and `cwd` | link |
| ``### The `/hooks` menu`` | <https://code.claude.com/docs/en/hooks#the-%2Fhooks-menu> | Read-only list with sources | link |
| `### Disable or remove hooks` | <https://code.claude.com/docs/en/hooks#disable-or-remove-hooks> | `disableAllHooks` precedence; `--settings` override | link |
| `<h4 id="bash-if-matching">` (rendered "How `if` patterns match Bash commands") | <https://code.claude.com/docs/en/hooks#bash-if-matching> | `if` is best-effort | link |

## Hooks guide

| Header in source | URL | Settles | Verified by |
| :-- | :-- | :-- | :-- |
| `## Prompt-based hooks` | <https://code.claude.com/docs/en/hooks-guide#prompt-based-hooks> | Guide view of prompt hooks | link |
| `## Agent-based hooks` | <https://code.claude.com/docs/en/hooks-guide#agent-based-hooks> | When to pick agent over prompt | link |
| `## Limitations and troubleshooting` | <https://code.claude.com/docs/en/hooks-guide#limitations-and-troubleshooting> | Entry point for symptoms | link (header text not confirmed) |
| `### Limitations` | <https://code.claude.com/docs/en/hooks-guide#limitations> | Timeouts by type; Stop vs StopFailure | link |
| `### Hooks and permission modes` | <https://code.claude.com/docs/en/hooks-guide#hooks-and-permission-modes> | A hook's deny holds in every mode | search |
| `### Hook not firing` | <https://code.claude.com/docs/en/hooks-guide#hook-not-firing> | First checks | search |
| `### Hook error in output` | <https://code.claude.com/docs/en/hooks-guide#hook-error-in-output> | Piping sample JSON; parse vs validation errors | search |
| ``### `/hooks` shows no hooks configured`` | <https://code.claude.com/docs/en/hooks-guide#/hooks-shows-no-hooks-configured> | Reload, JSON validity, `allowManagedHooksOnly` | search |
| `### Stop hook hits the block cap` | <https://code.claude.com/docs/en/hooks-guide#stop-hook-hits-the-block-cap> | 8-block cap; `stop_hook_active`; `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` | link |
| `### Hook JSON has no effect` | <https://code.claude.com/docs/en/hooks-guide#hook-json-has-no-effect> | Output not starting with `{`; misplaced fields | link |
| `#### Shell profile output before the JSON` | <https://code.claude.com/docs/en/hooks-guide#shell-profile-output-before-the-json> | Profile `echo` breaking JSON | link |
| `#### Fields at the wrong level` | <https://code.claude.com/docs/en/hooks-guide#fields-at-the-wrong-level> | `unrecognized keys` log line | link |
| `### Check what a hook did` | <https://code.claude.com/docs/en/hooks-guide#check-what-a-hook-did> | Transcript view; `/debug` mid-session | link |

## Other pages

| Header in source | URL | Settles | Verified by |
| :-- | :-- | :-- | :-- |
| `## Project allow rules and workspace trust` | <https://code.claude.com/docs/en/permissions#project-allow-rules-and-workspace-trust> | What the trust dialog covers | link |
| `### What runs before you trust a folder` | <https://code.claude.com/docs/en/permissions#what-runs-before-you-trust-a-folder> | Per-content trust table; `-p` mitigations; `hasTrustDialogAccepted` | link |
| `### Precedence among rules, hooks, and mods` | <https://code.claude.com/docs/en/permissions#precedence-among-rules-hooks-and-mods> | Hook allow vs deny/ask rules | link |
| `#### Hooks in subagent frontmatter` | <https://code.claude.com/docs/en/sub-agents#hooks-in-subagent-frontmatter> | Project subagent hooks need folder trust; never under `-p` | link |
| `<h3 id="supported-frontmatter-fields">` (rendered "Frontmatter reference") | <https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields> | Plugin subagents ignore `hooks` | link |
| `#### Preload skills into subagents` | <https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents> | `skills` frontmatter | link |
| `### Start faster with bare mode` | <https://code.claude.com/docs/en/headless#start-faster-with-bare-mode> | What `--bare` skips | link |
| `## Check hooks` | <https://code.claude.com/docs/en/debug-your-config#check-hooks> | `/hooks` first, then the debug log | search |
| `<h3 id="hook-needs-quotes-around-a-path-with-a-space">` (rendered "Hook needs quotes around a path with a space") | <https://code.claude.com/docs/en/errors#hook-needs-quotes-around-a-path-with-a-space> | `asyncRewake` shell-form path with a space | search |

## Out of scope: where to point

Link these in a **Not covered** line; do not assess them.

| Topic | Header in source | URL |
| :-- | :-- | :-- |
| Command-hook decisions per event | `#### Decision control` | <https://code.claude.com/docs/en/hooks#decision-control> |
| Exit codes | `### Exit code output` | <https://code.claude.com/docs/en/hooks#exit-code-output> |
| JSON output fields | `### JSON output` | <https://code.claude.com/docs/en/hooks#json-output> |
| Matchers | `### Matcher patterns` | <https://code.claude.com/docs/en/hooks#matcher-patterns> |
| HTTP hooks | `#### HTTP hook fields` | <https://code.claude.com/docs/en/hooks#http-hook-fields> |
| MCP tool hooks | `#### MCP tool hook fields` | <https://code.claude.com/docs/en/hooks#mcp-tool-hook-fields> |
| `onFailure` | `#### Block the action when a hook fails` | <https://code.claude.com/docs/en/hooks#block-the-action-when-a-hook-fails> |
| Permission rules | `## Permission rule syntax` | <https://code.claude.com/docs/en/permissions#permission-rule-syntax> |
