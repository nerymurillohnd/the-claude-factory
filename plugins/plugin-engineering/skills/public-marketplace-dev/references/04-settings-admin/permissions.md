# Configure permissions

> This file explains how Claude Code decides what Claude may access and do: permission rules, permission modes, managed policies, and how hooks and mods interact with them.

## Contents

- [Permission system](#permission-system)
- [Manage permissions](#manage-permissions)
- [Permission modes](#permission-modes)
- [Permission rule syntax](#permission-rule-syntax)
  - [Match all uses of a tool](#match-all-uses-of-a-tool)
  - [Use specifiers for fine-grained control](#use-specifiers-for-fine-grained-control)
  - [Match by input parameter](#match-by-input-parameter)
  - [Wildcard patterns](#wildcard-patterns)
  - [Tool name wildcards](#tool-name-wildcards)
- [Tool-specific permission rules](#tool-specific-permission-rules)
  - [Bash](#bash)
    - [Compound commands](#compound-commands)
    - [Wrappers](#wrappers)
    - [Exec wrappers and `find` actions](#exec-wrappers-and-find-actions)
    - [What a Bash rule doesn't match](#what-a-bash-rule-doesnt-match)
    - [Read-only commands](#read-only-commands)
    - [Redirections](#redirections)
  - [PowerShell](#powershell)
  - [Read and Edit](#read-and-edit)
    - [What `Read` and `Edit` rules cover](#what-read-and-edit-rules-cover)
    - [`Write(path)`, `Glob(path)`, and `Grep(path)` rules don't match](#writepath-globpath-and-greppath-rules-dont-match)
    - [How path patterns match](#how-path-patterns-match)
    - [Special characters and `!` negation](#special-characters-and--negation)
  - [WebFetch](#webfetch)
    - [Allow or deny every fetch](#allow-or-deny-every-fetch)
  - [MCP](#mcp)
  - [Agent (subagents)](#agent-subagents)
- [Extend permissions with hooks](#extend-permissions-with-hooks)
  - [Precedence among rules, hooks, and mods](#precedence-among-rules-hooks-and-mods)
  - [Hook approvals in plan mode](#hook-approvals-in-plan-mode)
- [Project allow rules and workspace trust](#project-allow-rules-and-workspace-trust)
  - [What runs before you trust a folder](#what-runs-before-you-trust-a-folder)
- [Documentation References](#documentation-references)

## Permission system

Claude Code uses a tiered permission system to balance power and safety. The table shows, for each tool type, whether Manual mode asks the user before the action runs. The other [permission modes](#permission-modes) change which of these actions prompt. In auto mode a classifier reviews actions instead of the user; [how the classifier evaluates actions](https://code.claude.com/docs/en/permission-modes.md#how-the-classifier-evaluates-actions) lists which actions it sees.

| Tool type | Example | Approval required | "Yes, and don't ask again" behavior |
| :- | :- | :- | :- |
| Read-only | File reads, Grep | No, within the [working directory and additional directories](https://code.claude.com/docs/en/permissions#working-directories) | N/A |
| Bash commands | Shell execution | Yes, except a built-in set of [read-only commands](#read-only-commands) | Permanently per repository and command |
| File modification | Edit/write files | Yes | Until session end |
| Web fetch | WebFetch | Yes, except a built-in set of [preapproved documentation domains](https://code.claude.com/docs/en/tools-reference.md#webfetch-tool-behavior) | Permanently per repository and domain |
| Web search | WebSearch | Yes | Permanently per repository |

## Manage permissions

Use `/permissions` to view and manage Claude Code's tool permissions. The dialog lists every permission rule and the `settings.json` file each rule comes from. The dialog can be opened while Claude is working: when a rule is added or removed, Claude Code applies the change starting with Claude's next tool call in the same turn. Before v2.1.234, Claude Code queued the command until the turn finished.

There are three rule types:

* **Allow** rules let Claude Code use the specified tool without manual approval.
* **Ask** rules prompt for confirmation whenever Claude Code tries to use the specified tool.
* **Deny** rules prevent Claude Code from using the specified tool.

Claude Code evaluates rules in this order: deny, then ask, then allow. The first match in that order determines the outcome. Rule specificity doesn't change the order.

A broad deny rule like `Bash(aws *)` blocks every matching call, including calls that also match a narrower allow rule like `Bash(aws s3 ls)`. An allow rule can't carve an exception out of a deny rule. The same precedence applies between ask and allow: a matching ask rule prompts even when a more specific allow rule also matches the same call.

A deny rule behaves differently depending on whether it names a whole tool or scopes a pattern within one:

* A bare tool name like `Bash` removes the tool from Claude's context entirely, so Claude never sees it. When such a rule is added mid-session, Claude can't call the tool from its next tool call on; [Denying an entire tool](https://code.claude.com/docs/en/prompt-caching.md#denying-an-entire-tool) covers what happens to a definition Claude has already seen.
* A scoped rule like `Bash(rm *)` leaves the tool available and blocks matching calls when Claude attempts them.

> [!NOTE]
>
> Claude Code enforces permission rules; the model does not. Instructions in a prompt or `CLAUDE.md` shape what Claude tries to do, but they don't change what Claude Code allows. To grant or revoke access, use `/permissions`, the rules described here, a [permission mode](https://code.claude.com/docs/en/permission-modes.md), or a [PreToolUse hook](#extend-permissions-with-hooks).

## Permission modes

Claude Code supports several permission modes that control how it approves tool calls. Read [Permission modes](https://code.claude.com/docs/en/permission-modes.md) for when to use each one. To change the default permission mode for new sessions, set `defaultMode` in the [settings files](https://code.claude.com/docs/en/settings.md#where-settings-live). [Which mode a session starts in](https://code.claude.com/docs/en/permission-modes.md#which-mode-a-session-starts-in) covers the built-in default for each plan and what the VS Code extension reads.

| Mode | Description |
| :- | :- |
| `default` | Prompts for permission on first use of each tool. Labeled Manual in the CLI, the VS Code and JetBrains extensions, and the desktop app, and Claude Code accepts `manual` as an alias |
| `acceptEdits` | Automatically accepts file edits and common filesystem commands such as `mkdir`, `touch`, `mv`, and `cp` for paths in the working directory or `additionalDirectories` |
| `plan` | Claude reads files and runs read-only shell commands to explore but doesn't edit your source files; with [auto mode](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode) available, classifier-approved commands also run. Labeled Plan in the CLI and the VS Code extension |
| `auto` | Runs without routine prompts; before actions such as shell commands and network requests run, a background [classifier](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode) checks that they align with your request |
| `dontAsk` | Auto-denies every call that would otherwise prompt, though a [mod](https://code.claude.com/docs/en/plugins/mods/overview.md) you installed can still approve some of those calls. File reads in your working directories and other actions that need no approval still run, as do tools pre-approved via `/permissions` or `permissions.allow` rules. `AskUserQuestion`, MCP tools marked [`requiresUserInteraction`](https://code.claude.com/docs/en/mcp#require-approval-for-a-specific-tool), [reads from network paths](https://code.claude.com/docs/en/permissions#network-paths), and connector tools [your organization set to `ask`](https://code.claude.com/docs/en/mcp#organization-controls-on-connector-tools) in sessions where that setting reaches Claude Code are denied even if you've allowed them |
| `bypassPermissions` | Skips permission prompts, except for the [actions no mode auto-approves](https://code.claude.com/docs/en/permission-modes.md#actions-no-mode-auto-approves) |

## Permission rule syntax

Write a permission rule as `Tool` or `Tool(specifier)`. Parentheses inside the specifier are literal, so a command or path that contains them needs no escaping.

### Match all uses of a tool

To match all uses of a tool, write only the tool name, without parentheses:

| Rule | Effect |
| :- | :- |
| `Bash` | Matches all Bash commands |
| `WebFetch` | Matches all web fetch requests |
| `Read` | Matches all file reads |

`Bash(*)` is equivalent to `Bash` and matches all Bash commands. As a deny rule, both forms remove the tool from Claude's context.

The label shown for a tool in the transcript and the permission dialog can differ from its canonical name. For example, the tool labeled `Stop Task` in the transcript has the canonical name `TaskStop`. Permission rules and [hook matchers](https://code.claude.com/docs/en/hooks.md) don't match the label, so a rule written as `Stop Task` doesn't match. For deny and ask rules, a [startup warning](https://code.claude.com/docs/en/errors.md#matches-no-tool) reports the mismatch. Always use the canonical names listed in the [tools reference](https://code.claude.com/docs/en/tools-reference.md).

### Use specifiers for fine-grained control

To match specific uses of a tool, add a specifier in parentheses:

| Rule | Effect |
| :- | :- |
| `Bash(npm run build)` | Matches the exact command `npm run build` |
| `Read(./.env)` | Matches reading the `.env` file in the current directory |
| `WebFetch(domain:example.com)` | Matches fetch requests to example.com |

### Match by input parameter

Deny and ask rules can match a top-level input parameter on any built-in tool with `Tool(param:value)`.

To match a parameter on an MCP tool, pass a deny rule with [`--disallowedTools`](https://code.claude.com/docs/en/cli-reference#cli-flags). When Claude Code loads a settings file, it skips any `mcp__` rule that has parentheses. Claude Code lists the skipped rule in the invalid-settings dialog when an interactive session starts, and in [`claude doctor`](https://code.claude.com/docs/en/debug-your-config#check-resolved-settings) output.

A parameter rule matches when Claude calls the tool with that parameter set to that exact value. An allow rule for one parameter value wouldn't establish that the call is safe overall, so allow rules keep using each tool's own specifier syntax. Parameter matching works for any scalar parameter the tool accepts:

| Rule | Matches |
| :- | :- |
| `Agent(model:opus)` | Agent calls that request the Opus model tier |
| `Agent(isolation:worktree)` | Agent calls that request a git worktree |
| `Bash(run_in_background:true)` | Bash calls that run in the background |

Parameter matching follows these rules:

* The parameter name must be a direct field of the tool's input, such as `model` on the Agent tool. Fields nested inside an object or array are not matchable
* Each rule names one parameter. To gate on both `model` and `isolation`, write two rules, `Agent(model:opus)` and `Agent(isolation:worktree)`, rather than combining them in one rule
* The value supports `*` as a wildcard that matches any sequence of characters, so `Agent(isolation:*)` matches any explicit isolation value. Without `*` the match is exact
* A parameter the model omits is never matched, so `Agent(model:*)` doesn't match a call that leaves `model` unset
* The value is compared against the literal input Claude sends, before any normalization. `Agent(model:opus)` matches the alias `opus` but not a full model ID
* A `Skill(skill:<name>)` deny rule is the exception: it [matches the skill under any of its names](https://code.claude.com/docs/en/skills.md#restrict-claude’s-skill-access), such as its alias or display name
* To see the exact parameter names and values in each tool call, run with [`--verbose`](https://code.claude.com/docs/en/cli-reference)
* Whitespace around the colon is ignored

A tool's primary content field can't be matched this way: `command` for Bash and PowerShell, `file_path` for Read, Edit, and Write, `path` for Grep and Glob, `notebook_path` for NotebookEdit, and `url` for WebFetch. A rule like `Bash(command:rm *)` would be bypassable by a compound command, so Claude Code ignores it and emits a startup warning. Use `Bash(rm *)`, `Read(./path)`, or `WebFetch(domain:host)` instead.

### Wildcard patterns

A `*` in a Bash rule matches any text, including spaces, so one rule covers a family of commands. A rule with no `*` matches one exact command.

> [!WARNING]
>
> Put the `*` after the subcommand. In `git log --oneline main`, `git` is the program and `log` is the subcommand, the word that determines what the program does. Claude Code matches everything before the first `*` as written, so those words are what limit the rule: `Bash(git log *)` allows only `git log` commands, and `Bash(git *)` allows every git command. Claude Code [warns at startup](https://code.claude.com/docs/en/errors.md#has-a-wildcard-before-the-rest-of-the-command) about an allow rule with a `*` before the subcommand, such as `Bash(git * main)`.

To write a rule, write the command Claude should run without asking and replace the parts that vary with `*`. With the following configuration, Claude Code runs npm scripts and git commits without asking and refuses commands that begin with `git push`. A push written another way, such as `git -C . push`, isn't matched; see [what a Bash rule doesn't match](#what-a-bash-rule-doesnt-match).

```json theme={null}
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git commit *)"
    ],
    "deny": [
      "Bash(git push *)"
    ]
  }
}
```

A `*` can go anywhere in the rule: at the start, in the middle, or at the end. Each row shows a rule, commands it matches, and nearby commands it doesn't match:

| You write | Matches | Doesn't match |
| :- | :- | :- |
| `Bash(npm run build)` | `npm run build` | `npm run build --watch` |
| `Bash(npm run *)` | `npm run build`, `npm run test --watch`, `npm run` | `npm install` |
| `Bash(git log * main)` | `git log --oneline main`, `git log -5 main`, `git log --output=<file> main` | `git log main`, `git push origin main` |
| `Bash(git * main)` | `git merge main`, `git push origin main`, `git -c core.fsmonitor=<script> diff main` | `git log` |
| `Bash(* --version)` | `node --version`, `bash -c 'echo hi' --version` | `node -v` |
| `Bash(ls *)` | `ls -la`, `ls` | `lsof` |
| `Bash(ls*)` | `ls -la`, `lsof` | |
| `Bash(* --help *)` | `npm --help x` | `npm --help` |

Three matching rules produce those rows:

* **The `*` stands in for whatever text is in its place.** In `Bash(git * main)`, it stands in for the subcommand, so Claude Code matches every git subcommand and every option before it. That includes `-c`, which makes git run a program the command names. In `Bash(* --version)`, the `*` stands in for the program, so any program matches.
* **A `*` at the end, with a space before it, also matches the bare command.** `Bash(ls *)` matches `ls`, and `Bash(git log *)` matches `git log`. This holds only when the trailing `*` is the rule's only wildcard: `Bash(* --help *)` matches `npm --help x` but not `npm --help`.
* **The space before a trailing `*` is part of the rule.** `Bash(ls *)` requires a space after `ls`, so `lsof` doesn't match. `Bash(ls*)` has no space, so it matches `lsof` too.

The `:*` suffix is an equivalent way to write a trailing wildcard, so `Bash(ls:*)` matches the same commands as `Bash(ls *)`.

When the user selects "Yes, and don't ask again" for a command prefix, the permission dialog writes the space-separated form. The `:*` form is recognized only at the end of a pattern. In a pattern like `Bash(git:* push)`, the colon is treated as a literal character and won't match git commands.

### Tool name wildcards

Deny and ask rules also accept glob patterns in the tool-name position. The pattern must match the full tool name: `"*"` matches every tool, and `"mcp__*"` matches every MCP tool across all servers. A tool matched by a bare-name glob deny rule is removed from Claude's context, the same as with a bare tool name. The [`EndConversation`](https://code.claude.com/docs/en/tools-reference#endconversation-tool-behavior) exception applies here too: a glob deny can't remove it while any other tool remains, and a glob ask never prompts for it. This configuration denies every MCP tool:

```json theme={null}
{
  "permissions": {
    "deny": [
      "mcp__*"
    ]
  }
}
```

Allow rules accept tool-name globs only after a literal `mcp__<server>__` prefix. The server segment must be glob-free, so the rule names one specific configured server. `mcp__puppeteer__*` matches every tool from the `puppeteer` server, and `mcp__github__get_*` matches its `get_` tools. An unanchored allow glob such as `"*"`, `"B*"`, or `"mcp__*"` is skipped and doesn't auto-approve anything.

A deny or ask rule whose tool name matches no known tool produces a [startup warning](https://code.claude.com/docs/en/errors.md#matches-no-tool) to catch typos. Tool names containing `_` or `*` are exempt from this check, and so are the names of tools Claude Code has removed, such as `TaskOutput`.

## Tool-specific permission rules

### Bash

Bash rules match the whole command text, with `*` standing in for any text. [Wildcard patterns](#wildcard-patterns) shows which commands each rule shape matches and where to put the `*`. The subsections below cover how Claude Code matches compound commands and wrappers, which wrappers and `find` actions a prefix rule can't approve, what a rule doesn't match, read-only commands, and redirections.

#### Compound commands

> [!TIP]
>
> Claude Code is aware of shell operators, so a rule like `Bash(safe-cmd *)` doesn't permit the command `safe-cmd && other-cmd`. The recognized command separators are `&&`, `||`, `;`, `|`, `|&`, `&`, and newlines. A compound command runs without a prompt only when every subcommand is allowed, for example because the subcommand matches an allow rule or is a [read-only command](#read-only-commands).

Deny and ask rules apply when any subcommand matches them, including a command nested inside a subshell, a command substitution, or a control-flow body such as a `for` loop. An ask rule like `Bash(git clean *)` still prompts for `cd /tmp && git clean -f` or `echo "$(git clean -f)"`, even in [auto mode](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode).

When `&&` or `||` has nothing after it, such as in `npm test &&`, Claude Code treats the command as unparseable and doesn't split it into subcommands for allow-rule matching, so a rule such as `Bash(npm *)` doesn't approve it.

When the user approves a compound command with "Yes, and don't ask again", Claude Code saves a separate rule for each subcommand that requires approval, rather than a single rule for the full compound string. For example, approving `git status && npm test` saves a rule for `npm test`, so future `npm test` invocations are recognized regardless of what precedes the `&&`. A subcommand like `cd` into a directory outside the working directories generates its own Read rule for that path. Claude Code saves up to 5 rules for a single compound command.

#### Wrappers

Before matching Bash rules, Claude Code strips a fixed set of wrappers, so a rule like `Bash(npm test *)` also matches `timeout 30 npm test`. The stripped wrappers are `timeout`, `time`, `nice`, `nohup`, and `stdbuf`, plus the shell builtins `command` and `builtin`, and zsh's `noglob`. Each runs its argument as the actual command. Two related forms aren't stripped: the query form `command -v`, which looks up a command rather than running one, and zsh's `nocorrect`.

Claude Code also strips a leading assignment of certain known-safe environment variables, so `Bash(npm test *)` matches `NODE_ENV=test npm test`. An allow rule doesn't match past an assignment of any other variable. A deny or ask rule matches past any leading assignment, so `Bash(rm *)` in deny still matches `FOO=bar rm -rf tmp/`.

Bare `xargs` is also stripped, so `Bash(grep *)` matches `xargs grep pattern`. Stripping applies only when `xargs` has no flags: an invocation like `xargs -n1 grep pattern` is matched as an `xargs` command, so rules written for the inner command don't cover it.

This wrapper list is built in and not configurable. Development environment runners such as `direnv exec`, `devbox run`, `mise exec`, `npx`, and `docker exec` are not in the list. Because these tools execute their arguments as a command, a rule like `Bash(devbox run *)` matches whatever comes after `run`, including `devbox run rm -rf .`. To approve work inside an environment runner, write a specific rule that includes both the runner and the inner command, such as `Bash(devbox run npm test)`, with one rule per inner command to allow.

#### Exec wrappers and `find` actions

A prefix rule like `Bash(watch *)` or `Bash(find *)` can't auto-approve the following commands, so in Manual mode they prompt:

* **Exec wrappers**: such as `watch`, `setsid`, `ionice`, and `flock`
* **`find`**: with an action that runs commands, deletes files, or writes files, such as `-exec`, `-delete`, `-rm`, or `-fprint`, or with `-files0-from`, which takes the paths to search from a file

To approve a specific invocation that has no `*` in it, write an exact-match rule for the full command string, such as `Bash(find build -type f -delete)`.

When the command itself contains a `*`, as in `find . -name '*.tmp' -delete`, Claude Code reads the rule as a [wildcard pattern](#wildcard-patterns), not an exact match, so the command still prompts. Either approve it each time it prompts, or use a [PreToolUse hook](https://code.claude.com/docs/en/hooks.md#pretooluse-decision-control) that returns `"allow"` for it.

#### What a Bash rule doesn't match

A Bash rule matches the command text Claude writes, after Claude Code splits [compound commands](#compound-commands) and strips [wrappers](#wrappers). It doesn't match the same program invoked in a different form. A deny or ask rule therefore covers the invocation Claude usually produces; it is not a security boundary around the program. In `deny` or `ask`, these rules stop the first form and not the others:

| Rule | Stops | Doesn't stop |
| :- | :- | :- |
| `Bash(curl *)` | `curl https://example.com` | `/usr/bin/curl https://example.com`, `sh -c 'curl https://example.com'` |
| `Bash(rm *)` | `rm -rf build/` | `/bin/rm -rf build/`, `bash -c 'rm -rf build/'` |
| `Bash(git push *)` | `git push origin main` | `git -C . push origin main`, `git -c push.default=current push origin main`, `git 'push' origin main` |

The other rules and the permission mode decide the commands in the last column.

For filesystem and network enforcement that doesn't depend on the command text, use [sandboxing](https://code.claude.com/docs/en/sandboxing.md). To inspect the full command text with custom logic before it runs, use a [PreToolUse hook](#extend-permissions-with-hooks).

#### Read-only commands

Claude Code recognizes a built-in set of Bash commands as read-only and runs them without a permission prompt in every mode, except where [`permissions.blockReadsOutsideWorkingDirectories`](https://code.claude.com/docs/en/settings-reference#permissions-blockreadsoutsideworkingdirectories) changes that for paths outside the working directories. The set includes `ls`, `cat`, `echo`, `pwd`, `head`, `tail`, `grep`, `find`, `wc`, `which`, `diff`, `stat`, `du`, `cd`, and read-only forms of `git`. The set is not configurable; to require a prompt for one of these commands, add an `ask` or `deny` rule for it. In auto mode, these commands can also wait for the classifier's review; see [how the classifier evaluates actions](https://code.claude.com/docs/en/permission-modes.md#how-the-classifier-evaluates-actions).

A redirect such as `ls > out.txt` adds a check on the target. See [Redirections](#redirections).

Unquoted glob patterns are permitted for commands whose every flag is read-only, so `ls *.ts` and `wc -l src/*.py` run without a prompt.

In Manual mode, commands from this set still prompt in these cases:

* **Unquoted globs for commands with write-capable flags**: commands with write-capable or exec-capable flags, such as `find`, `sort`, `sed`, and `git`, prompt when an unquoted glob is present, because the glob could expand to a flag like `-delete`.
* **`docker` pointed at another daemon**: read-only forms of `docker` prompt when the command carries a flag that selects a different daemon, such as `-H`, `--context`, or Podman's `--url` and `--connection`.
* **`file` with path-opening flags**: `file` prompts when it passes `-m`/`--magic-file` or `-f`/`--files-from`, because those flags make `file` open the paths named in the flag's value.
* **`ps` that could print environment variables**: `ps` prompts when one of its arguments could act as the `e` option, such as in `ps auxe` or `ps aux -e`, because that option prints process environment variables. `ps aux` and `ps -ef` run without a prompt. The check on dashed forms such as `ps aux -e` requires Claude Code v2.1.290 or later.
* **Network paths on Windows**: a command whose arguments include a network (UNC) path, such as `\\server\share\file`, prompts because accessing a network path can send the user's Windows credentials to the host it names. The same check applies to [PowerShell tool](https://code.claude.com/docs/en/tools-reference.md#powershell-tool) commands.
* **Writes to special shell variables**: a command that sets, unsets, or loops over certain special shell variables, such as `PATH` or `IFS`, prompts even when the rest of the command is read-only.
* **Commands the analysis can't parse**: when Claude Code can't fully parse a command, it asks for approval instead of treating the command as read-only. Commands longer than 10,000 characters always prompt because they exceed what the analysis parses.

A `cd` into a path inside the working directory or an [additional directory](https://code.claude.com/docs/en/permissions#working-directories) is also read-only, and a compound command like `cd packages/api && ls` runs without a prompt when each part qualifies on its own. These combinations prompt even when each part is read-only:

* **`cd` with `git`**: prompts when the `cd` changes into a different directory, since running `git` in a new directory can execute that directory's hooks. A `cd` whose target resolves to the current working directory is a no-op and doesn't trigger the prompt.
* **`cd` with a redirect**: prompts when Claude Code can't determine which directory the redirect target resolves against after the `cd` runs. A command whose only redirect target is `/dev/null`, such as `cd app; grep -r pattern . 2>/dev/null`, doesn't prompt, because `/dev/null` doesn't depend on the working directory.

> [!WARNING]
>
> Bash permission patterns that try to constrain command arguments are fragile. For example, `Bash(curl http://github.com/ *)` intends to restrict curl to GitHub URLs, but doesn't match variations like:
>
> * Options before URL: `curl -X GET http://github.com/...`
> * Different protocol: `curl https://github.com/...`
> * Redirects: `curl -L http://short.example.com/xyz`, which redirects to GitHub
> * Variables: `URL=http://github.com && curl $URL`
>
> For more reliable URL filtering, use one of these approaches:
>
> * **Restrict Bash network tools**: use deny rules to stop `curl`, `wget`, and similar commands, then use the WebFetch tool with `WebFetch(domain:github.com)` permission for allowed domains. A deny rule doesn't match the same program by path or inside `sh -c`, so pair it with the [sandbox network allowlist](https://code.claude.com/docs/en/sandboxing.md#network-isolation) when the restriction must hold; see [what a Bash rule doesn't match](#what-a-bash-rule-doesnt-match)
> * **Use PreToolUse hooks**: implement a hook that validates URLs in Bash commands and blocks disallowed domains
> * **Add CLAUDE.md guidance**: describe the allowed curl patterns in `CLAUDE.md`. This shapes what Claude tries but doesn't enforce a boundary, so pair it with one of the options above
>
> Using WebFetch alone doesn't prevent network access. If Bash is allowed, Claude can still use `curl`, `wget`, or other tools to reach any URL.

#### Redirections

When a command redirects output or input, Claude Code checks the redirect target against the file rules as if Claude wrote or read that file directly:

* **Output redirects**: for `> file`, `>> file`, or `2> file`, the check covers the `Edit` allow and deny rules, [protected paths](https://code.claude.com/docs/en/permission-modes.md#protected-paths), and the [working directories](https://code.claude.com/docs/en/permissions#working-directories). A rule such as `Bash(git commit *)` allows the command, not the target. A target that starts with `~` or contains a glob character needs the user's approval.
* **Input redirects**: for `< file`, the check covers the `Read` allow and deny rules and the working directories. A target outside the working directories needs the user's approval unless an allow rule covers it. A target that contains a glob pattern, or a relative path that follows a `cd` in the same command, needs the user's approval even when an allow rule covers it. Claude Code checks input targets in v2.1.257 and later.

Targets with no file behind them aren't checked: `/dev/null`, file-descriptor forms such as `2>&1` and `<&3`, and here-docs and here-strings.

Claude Code also checks the files a `tee` command writes, including in a pipeline such as `make | tee build.log`. The check covers the `Edit` allow and deny rules, [protected paths](https://code.claude.com/docs/en/permission-modes.md#protected-paths), and the [working directories](https://code.claude.com/docs/en/permissions#working-directories). An allow rule such as `Bash(tee *)` doesn't cover a destination outside the working directories. Claude Code checks `tee` targets in v2.1.269 and later.

### PowerShell

PowerShell permission rules use the same shape as [Bash rules](#wildcard-patterns), and a bare `PowerShell` or `PowerShell(*)` matches every command. This configuration allows `Get-ChildItem` and `git commit` commands while blocking `Remove-Item`:

```json theme={null}
{
  "permissions": {
    "allow": [
      "PowerShell(Get-ChildItem *)",
      "PowerShell(git commit *)"
    ],
    "deny": [
      "PowerShell(Remove-Item *)"
    ]
  }
}
```

Claude Code canonicalizes common aliases before matching. A rule written for the cmdlet name also matches those aliases, so `PowerShell(Get-ChildItem *)` matches `gci`, `ls`, and `dir` as well. Matching is case-insensitive.

Claude Code parses the PowerShell AST and checks each command in a compound command independently. Pipeline operators `|`, statement separators `;`, and, on PowerShell 7+, the chain operators `&&` and `||` split a compound command into subcommands. A compound command runs without a prompt only when every subcommand is allowed, for example by matching an allow rule.

### Read and Edit

To block Claude's file tools from reading a file or directory, add a `Read` deny rule for its path, such as `Read(./.env)` or `Read(./secrets/**)`; [Exclude sensitive files](https://code.claude.com/docs/en/settings-reference.md#exclude-sensitive-files) has a paste-ready example. A `.claudeignore` file has no effect; when a project has one, move its entries into `Read` deny rules.

#### What `Read` and `Edit` rules cover

`Edit` rules apply to all built-in tools that edit files. Claude makes a best-effort attempt to apply `Read(path)` deny rules to all built-in tools that read files, like Grep and Glob. It makes the same attempt to apply `Read(path)` deny rules to `@file` mentions in prompts and to the selection and open-file context that a connected [IDE](https://code.claude.com/docs/en/vs-code.md#the-built-in-ide-mcp-server) shares with Claude.

A `Read(path)` deny rule also applies to image paths pasted into a prompt and to directories that are @-mentioned:

* **Image path**: when the user pastes an image's path or drags an image file into the prompt in the terminal and the rule matches that path, Claude Code doesn't attach the image. If the paste holds no other image, the path stays in the prompt as text.
* **Directory**: the [listing Claude receives](https://code.claude.com/docs/en/common-workflows.md#reference-files-and-directories) leaves out the file and directory names the rule matches.

Claude Code checks pasted image paths and directory listings in v2.1.290 and later.

A `Read` deny rule also blocks the [Edit and Write tools](https://code.claude.com/docs/en/errors.md#file-is-covered-by-a-read-deny-rule) on the same path, including creating a new file there. NotebookEdit isn't covered, so add an `Edit` deny rule for paths no tool may change. For the Write tool, the check requires Claude Code v2.1.228 or later.

> [!WARNING]
>
> Read and Edit deny rules apply to Claude's built-in file tools, to file commands Claude Code recognizes in Bash, such as `cat`, `head`, `tail`, `sed`, and `tee`, and to the targets of Bash [redirections](#redirections) such as `> file` and `< file`. They don't apply to a command that reads files without naming them, such as `grep -r pattern .` run from the directory that holds the file, or to arbitrary subprocesses that read or write files indirectly, like a Python or Node script that opens files itself. For OS-level enforcement that blocks all processes from accessing a path, [enable the sandbox](https://code.claude.com/docs/en/sandboxing.md).

#### `Write(path)`, `Glob(path)`, and `Grep(path)` rules don't match

Claude Code checks file permissions against `Edit(path)` and `Read(path)` rules. It accepts a rule with a path other than `*` for one of the tools below but never matches a read, search, or edit against it. For example, a `Grep(docs/**)` deny rule doesn't stop Grep from searching `docs`. Write the `Edit` or `Read` rule in its place:

* **`Write`, `NotebookEdit`, or legacy `MultiEdit`**: use `Edit(docs/**)` in place of `Write(docs/**)`.
* **`Glob` or `Grep`**: use `Read(docs/**)` in place of `Grep(docs/**)`. As an ask rule, `Read(docs/**)` prompts when Claude calls Grep or Glob on a matching path, but not when a search of a working directory above it returns matching files.

To match every use of one of these tools regardless of path, [write only the tool name](#match-all-uses-of-a-tool).

#### How path patterns match

Read and Edit rules both use [gitignore](https://git-scm.com/docs/gitignore) pattern syntax with four distinct pattern types:

| Pattern | Meaning | Example | Matches |
| - | - | - | - |
| `//path` | Absolute path from filesystem root | `Read(//Users/alice/secrets/**)` | `/Users/alice/secrets/**` |
| `~/path` | Path from home directory | `Read(~/Documents/*.pdf)` | `/Users/alice/Documents/*.pdf` |
| `/path` | Path relative to the settings source | `Edit(/src/**/*.ts)` | `<primary working directory>/src/**/*.ts` in project settings |
| `path` or `./path` | Path relative to current directory | `Read(*.env)` | `<cwd>/*.env` |

> [!WARNING]
>
> A pattern like `/Users/alice/file` isn't an absolute path. The single leading slash anchors at the settings source, not the filesystem root. Use `//Users/alice/file` for absolute paths.

##### Where a pattern anchors

A `/path` pattern anchors at a directory associated with the settings source that defines it, so the same rule matches different locations depending on which settings source holds it:

| Rule defined in | `/path` resolves to |
| :- | :- |
| Project settings at `.claude/settings.json` | `<primary working directory>/path` |
| Local settings at `.claude/settings.local.json` | `<primary working directory>/path` |
| User settings at `~/.claude/settings.json` | `~/.claude/path` |
| A file passed with `--settings <file>` | `<directory of file>/path` |
| CLI flags or session rules | `<primary working directory>/path` |

A rule added through `/permissions` follows the row for the settings file it is saved to.

Local settings rules anchor at the session's [primary working directory](https://code.claude.com/docs/en/permissions#working-directories), not at the repository root where Claude Code [stores the file](#permission-system). In a session started at the repository root, the two directories are the same; in a [worktree](https://code.claude.com/docs/en/worktrees.md) session, a shared rule such as `Edit(/src/**)` matches that worktree's own `src/` directory.

A deny rule such as `Read(/secrets/**)` in user settings blocks `~/.claude/secrets/**`, not a `secrets` directory in the project. To write a rule in user settings that applies inside every project, use a `//` absolute path or a `~/` home-relative path instead.

On Windows, paths are normalized to POSIX form before matching. `C:\Users\alice` becomes `/c/Users/alice`, so use `//c/**/.env` to match `.env` files anywhere on that drive. To match across all drives, use `//**/.env`.

Examples:

* `Edit(/docs/**)`: edits in `<primary working directory>/docs/`, not `/docs/` or `<primary working directory>/.claude/docs/`
* `Read(~/.zshrc)`: reads the home directory's `.zshrc`
* `Edit(//tmp/scratch.txt)`: edits the absolute path `/tmp/scratch.txt`
* `Read(src/**)`: as an allow rule, reads from `<current-directory>/src/` only; as a deny or ask rule, matches a `src` directory at any depth under the current directory

##### How deep a pattern matches

A rule only matches files under its anchor. Within that bound, matching depth depends on the pattern shape and, for single-segment directory patterns, on the rule type, as described below. Bare filenames follow gitignore semantics and match at any depth, so `Read(.env)` and `Read(**/.env)` are equivalent:

| Deny rule | Blocks | Does not block |
| - | - | - |
| `Read(.env)` or `Read(**/.env)` | any `.env` at or under the current directory | `.env` in a parent directory or another project |
| `Read(//**/.env)` | any `.env` anywhere on the filesystem | nothing; the rule is anchored at the filesystem root |

A relative pattern with a single directory segment, such as `src/**`, matches at different depths depending on the rule type:

* **Allow rules**: `Edit(src/**)` matches only `<cwd>/src` and the files under it. To allow a directory name at any depth, write `Edit(**/src/**)`.
* **Deny and ask rules**: `Read(secrets/**)` matches a directory named `secrets` at any depth under the current directory, so the rule also applies to nested copies.

Every other pattern shape matches at the same depth in every rule type: `Edit(/src/**)` and `Edit(src/components/**)` match only at their anchored location, while `Edit(**/src/**)` matches at any depth.

The following example shows each pattern shape against a project with a top-level `src/` directory and a nested copy under `vendor/`:

```text theme={null}
<current-directory>/
├── src/
│   └── app.ts
└── vendor/
    └── pkg/
        └── src/
            └── lib.js
```

| Rule | Matches `src/app.ts` | Matches `vendor/pkg/src/lib.js` |
| :- | :- | :- |
| `Edit(src/**)` as an allow rule | Yes | No |
| `Edit(src/**)` as a deny or ask rule | Yes | Yes |
| `Edit(/src/**)` in any rule type | Yes | No |
| `Edit(**/src/**)` in any rule type | Yes | Yes |

> [!NOTE]
>
> In gitignore patterns, `*` matches within a single path segment and can appear at any position in the pattern, while `**` matches across directories.

#### Special characters and `!` negation

When the user approves a file path with "Yes, and don't ask again", Claude Code escapes gitignore pattern characters in that path, such as `[`, `]`, and `*`, so the generated rule matches only the literal approved path. Hand-written rules aren't escaped.

Parentheses in a path need no escaping, so `Edit(./Finance (2024)/**)` matches the `Finance (2024)` folder as spelled.

A deny or ask rule whose path isn't usable as a gitignore pattern still guards that exact path. An allow rule with an unusable pattern doesn't approve anything.

A deny or ask pattern that starts with `!` is a gitignore negation. It carves the paths it matches out of the `path` or `./path` rules listed before it. In one settings file's `deny` list, `Read(*.env)` followed by `Read(!sample.env)` blocks every file whose name ends in `.env` at any depth, except files named `sample.env`. A `!` rule listed first carves nothing out.

The carve-out reaches only rules from the same source. A `Read(!.env)` in project settings or in `--disallowedTools` doesn't cancel a `Read(./.env)` deny from managed settings or any other settings file.

Two limits narrow what a `!` pattern can carve out:

* Claude Code reads a `!` pattern relative to the current directory even when `/`, `~/`, or `//` follows the `!`, so the pattern can't reach a rule anchored with one of those prefixes. `Read(!~/notes/public/**)` carves nothing out of `Read(~/notes/**)`.
* A carve-out can't reopen a file inside a directory that a rule blocks as a whole. With `Read(secrets/**)` and `Read(!secrets/public/**)`, Claude Code still blocks `secrets/public` along with the rest of `secrets`.

### WebFetch

WebFetch rules use a `domain:` prefix and match against the hostname of the requested URL. Matching is case-insensitive, supports `*` wildcards, and strips a trailing `.` from both the rule and the hostname, so `example.com.` and `example.com` are treated the same.

* `WebFetch(domain:example.com)` matches requests to `example.com` only. To also cover subdomains such as `api.example.com`, add a `WebFetch(domain:*.example.com)` rule
* `WebFetch(domain:*.example.com)` matches any subdomain at any depth, such as `api.example.com` or `a.b.example.com`, but not `example.com` itself
* `WebFetch(domain:*)` matches every domain. It isn't the same as a bare `WebFetch` rule; see [Allow or deny every fetch](#allow-or-deny-every-fetch)

In any position other than a leading `*.` or a bare `*`, the wildcard matches only the text between two dots. `WebFetch(domain:example.*)` matches `example.org`, where `*` becomes `org`, but not `example.evil.com`, where `*` would have to become `evil.com` and cross a dot. This keeps a trailing wildcard from matching domains an attacker could register.

Wildcards in `WebFetch` rules require Claude Code v2.1.172 or later to match fetches.

#### Allow or deny every fetch

A bare `WebFetch` rule is the tool name with no `domain:` part, such as `"deny": ["WebFetch"]`. Both it and `WebFetch(domain:*)` cover every URL, but Claude Code applies them differently: only the `domain:` form also adds its domain to the sandbox's [allowed or denied domain list](https://code.claude.com/docs/en/sandboxing.md#network-isolation). That linked section lists the wildcard forms the sandbox honors and the version that added bare `*`.

Each row shows what a rule does in the `allow` list and in the `deny` list:

| Rule | In `allow` | In `deny` |
| :- | :- | :- |
| `WebFetch` | Claude fetches without prompting you. Doesn't change which hosts sandboxed commands can reach. | Claude Code removes the `WebFetch` tool, so Claude can't fetch at all. Doesn't change which hosts sandboxed commands can reach. |
| `WebFetch(domain:*)` | Claude fetches without prompting you, and sandboxed commands can reach any host. | Claude Code keeps the tool and refuses each fetch, and sandboxed commands can't reach any host. |

To let Claude fetch freely while keeping the sandbox allowlist unchanged, use the bare form, as this `settings.json` does:

```json theme={null}
{
  "permissions": {
    "allow": ["WebFetch"]
  }
}
```

With this configuration, a request to fetch a page runs without a prompt. A request to run a [sandboxed](https://code.claude.com/docs/en/sandboxing.md) `curl` against a host outside the sandbox allowlist still prompts for that host, because the bare rule didn't add the host to the allowlist.

### MCP

To match every tool from an MCP server, write `mcp__<server>__*`. To match one tool, write its full name, `mcp__<server>__<tool>`.

* `mcp__puppeteer` matches any tool provided by the `puppeteer` server
* `mcp__puppeteer__*` uses wildcard syntax and also matches all tools from the `puppeteer` server
* `mcp__puppeteer__puppeteer_navigate` matches the `puppeteer_navigate` tool provided by the `puppeteer` server

For `<server>`, write the server's name the way it appears in that server's tool names. These cases show the rule to write for a name with special characters, a server from a plugin, and a name that contains `__` or ends in `_`:

* **Names with characters such as `.` or spaces**: those characters become `_`, so for a server configured as `my.server`, write `mcp__my_server__*`
* **Servers that a plugin provides**: `<server>` takes the [plugin-scoped form](https://code.claude.com/docs/en/mcp.md#plugin-provided-mcp-servers), so for the `database-tools` server in a plugin named `my-plugin`, write `mcp__plugin_my-plugin_database-tools__*`
* **A `<server>` that contains `__` or ends in `_`**: write the wildcard form, `mcp__<server>__*`, with the whole name. For a server named `reports__v2`, write `mcp__reports__v2__*`. The bare `mcp__reports__v2` and the shorter `mcp__reports` don't match its tools as allow rules, because Claude Code reads both as rules for a server named `reports`.

  As a deny or ask rule, though, each of those two names also covers every tool of the `reports__v2` server. To cover a server named `reports` alone, write one rule per tool in the `mcp__reports__<tool>` form, or rename one of the servers.

### Agent (subagents)

Use `Agent(AgentName)` rules to control which [subagents](https://code.claude.com/docs/en/sub-agents.md) Claude can use:

* `Agent(Explore)` matches the Explore subagent
* `Agent(Plan)` matches the Plan subagent
* `Agent(my-custom-agent)` matches a custom subagent named `my-custom-agent`

To disable specific agents, add these rules to the `deny` array in settings or pass them with the `--disallowedTools` CLI flag. To disable the Explore agent:

```json theme={null}
{
  "permissions": {
    "deny": ["Agent(Explore)"]
  }
}
```

## Extend permissions with hooks

[Claude Code hooks](https://code.claude.com/docs/en/hooks-guide.md) register custom shell commands that evaluate permissions at runtime. When Claude Code makes a tool call, PreToolUse hooks run before the permission prompt, for every tool except [`EndConversation`](https://code.claude.com/docs/en/tools-reference#endconversation-tool-behavior). The hook output can deny the tool call, force a prompt, or skip the prompt to let the call proceed.

### Precedence among rules, hooks, and mods

PreToolUse hook decisions don't bypass permission rules. Claude Code evaluates deny and ask rules regardless of what a PreToolUse hook returns: a matching deny rule blocks the call, and a matching ask rule still prompts even when the hook returned `"allow"` or `"ask"`. This preserves the deny-first precedence described in [Manage permissions](#manage-permissions), including deny rules set in managed settings.

That precedence covers hooks in settings files and in a plugin's `hooks/hooks.json`. An installed [mod](https://code.claude.com/docs/en/plugins/mods/overview.md) that handles the [`tool.check`](https://code.claude.com/docs/en/plugins/mods/events#approve-or-refuse-a-tool-call-before-the-user-is-asked) event gives its answer after the `PreToolUse` hooks have run. When [managed settings](https://code.claude.com/docs/en/settings.md#check-what-your-organization-enforces) are on the machine, or a Team or Enterprise [`/login`](https://code.claude.com/docs/en/authentication#authentication-precedence) is the session's credential, these outcomes stay in place by default when the mod approves a call:

* A call that a deny rule refuses stays refused, and the organization can change that.
* A call that an ask rule would prompt for still prompts the user.
* A call that a `PreToolUse` hook or [`permissions.blockReadsOutsideWorkingDirectories`](https://code.claude.com/docs/en/settings-reference#permissions-blockreadsoutsideworkingdirectories) would prompt for still prompts the user.
* A call that a `PreToolUse` hook blocked stays blocked, whichever settings file the hook comes from.
* A call that the [`--permission-prompt-tool`](https://code.claude.com/docs/en/cli-reference#cli-flags) or Agent SDK [`canUseTool` callback](https://code.claude.com/docs/en/agent-sdk/user-input#handle-tool-approval-requests) would be asked about is still put to that tool or callback.

When there are neither managed settings nor a Team or Enterprise `/login` as the session's credential, the mod can approve a call that a deny rule refuses or a `PreToolUse` hook blocked. A session that runs on an API key or a long-lived [`CLAUDE_CODE_OAUTH_TOKEN`](https://code.claude.com/docs/en/authentication#generate-a-long-lived-token) instead isn't using that login, even when that login is stored.

In that setup, the user isn't prompted when the mod approves a call that an ask rule, a `PreToolUse` hook, or `permissions.blockReadsOutsideWorkingDirectories` would prompt for. The `--permission-prompt-tool` or `canUseTool` callback isn't asked about a call the mod approves, either. Auto mode, plan mode, and `dontAsk` mode each add an outcome of their own in every setup:

* **[Auto mode](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode)**: a call the mod approves runs without a classifier check, except where the mod can't bypass the permission prompt tool or Agent SDK permission callback. There the classifier checks the call first.
* **[Plan mode](#hook-approvals-in-plan-mode)**: the mod can't approve a call that isn't read-only, such as a file edit or a shell command that writes.
* **[`dontAsk` mode](https://code.claude.com/docs/en/permission-modes#allow-only-pre-approved-tools-with-dontask-mode)**: the mod can approve a call that nothing but the mode would deny.

Read [Decide whether to trust a mod](https://code.claude.com/docs/en/plugins/mods/overview.md#decide-whether-to-trust-a-mod), or, for deployments with managed settings, [Manage mods for your organization](https://code.claude.com/docs/en/plugins/mods/admin.md#know-what-happens-by-default).

For a [tool that requires user interaction](https://code.claude.com/docs/en/permission-modes.md#actions-no-mode-auto-approves), such as `AskUserQuestion` or an MCP tool marked `requiresUserInteraction`, a mod's `tool.check` approval doesn't skip the prompt. This requires Claude Code v2.1.292 or later. MCP tools marked [`requiresUserInteraction`](https://code.claude.com/docs/en/mcp#require-approval-for-a-specific-tool) also still prompt when a hook returns `"allow"`, as do reads from [network paths](https://code.claude.com/docs/en/permissions#network-paths) and connector tools [your organization set to `ask`](https://code.claude.com/docs/en/mcp#organization-controls-on-connector-tools) in sessions where that setting reaches Claude Code.

A blocking hook also takes precedence over allow rules. A hook that exits with code 2 stops the tool call before permission rules are evaluated, so the block applies even when an allow rule would otherwise let the call proceed. To run all Bash commands without prompts except for a few that must be blocked, add `"Bash"` to the allow list and register a PreToolUse hook that rejects those specific commands. [Block edits to protected files](https://code.claude.com/docs/en/hooks-guide.md#block-edits-to-protected-files) has a hook script to adapt.

### Hook approvals in plan mode

In [plan mode](https://code.claude.com/docs/en/permission-modes.md#analyze-before-you-edit-with-plan-mode), apart from `ExitPlanMode`, a `PreToolUse` hook's `"allow"` has no effect on a file edit or another call that isn't read-only. The call gets the same prompt, block, or approval it would get with no hook, and Claude Code still applies any `updatedInput` the hook returns. If the hook answers [`ExitPlanMode`](https://code.claude.com/docs/en/hooks#allow-with-updatedinput) with `"allow"` and `updatedInput`, that tool still runs without a prompt.

In plan mode, a mod that handles `tool.check` also can't approve a file edit or another call that isn't read-only, though it can still block such a call. To lift this limit on hook and mod approvals, [approve the plan](https://code.claude.com/docs/en/permission-modes.md#review-and-approve-a-plan) or switch to another permission mode.

## Project allow rules and workspace trust

### What runs before you trust a folder

Each row is one kind of content a repository can supply. The columns are the two situations in which the user hasn't trusted the folder itself: the user trusted only a parent folder, or ran `claude -p` or the SDK there, which never shows the trust dialog. The parent-folder column doesn't apply inside a [nested repository](#project-allow-rules-and-workspace-trust): in an interactive session Claude Code shows the trust dialog for it, and a `claude -p` or SDK run there follows the `claude -p` column.

| What the repository supplies | You trusted only a parent folder | `claude -p` or the SDK, folder never trusted |
| :- | :- | :- |
| Frontmatter hooks in a project [subagent](https://code.claude.com/docs/en/sub-agents.md#hooks-in-subagent-frontmatter), a project [`@skills-dir` plugin](https://code.claude.com/docs/en/plugins/loading#plugins-shared-through-a-repository), and [`extraKnownMarketplaces`](https://code.claude.com/docs/en/settings-reference#extraknownmarketplaces) entries from the repository or an `--add-dir` directory | Not used, and no dialog is offered | Not used |

## Documentation References

- Source page: https://code.claude.com/docs/en/permissions (working directories, network paths and the rest of the full permissions page)
- https://code.claude.com/docs/en/settings-reference.md: every settings key, including the permission keys (permission settings), `permissions.blockReadsOutsideWorkingDirectories`, `extraKnownMarketplaces` and excluding sensitive files
- https://code.claude.com/docs/en/settings.md: where settings files live and how to check what an organization enforces
- https://code.claude.com/docs/en/permission-modes.md: each permission mode, the auto-mode classifier, protected paths, plan mode and actions no mode auto-approves
- https://code.claude.com/docs/en/hooks-guide.md: hooks guide, automating workflows and extending permission evaluation, including blocking edits to protected files
- https://code.claude.com/docs/en/hooks.md: hooks reference, PreToolUse decision control and `updatedInput`
- https://code.claude.com/docs/en/plugins/mods/overview.md: what mods are and how to decide whether to trust one
- https://code.claude.com/docs/en/plugins/mods/events: mod events, including `tool.check`
- https://code.claude.com/docs/en/plugins/mods/admin.md: managing mods for an organization and their default behavior
- https://code.claude.com/docs/en/plugins/loading: how plugins load, including `@skills-dir` plugins shared through a repository
- https://code.claude.com/docs/en/mcp.md: MCP servers, plugin-provided server naming, `requiresUserInteraction` and organization controls on connector tools
- https://code.claude.com/docs/en/tools-reference.md: canonical tool names, WebFetch preapproved domains, the PowerShell tool and `EndConversation`
- https://code.claude.com/docs/en/errors.md: startup warnings for rules that match no tool or have a misplaced wildcard, and the Read deny rule error
- https://code.claude.com/docs/en/sandboxing.md: OS-level sandboxing and network isolation allowlists
- https://code.claude.com/docs/en/cli-reference: CLI flags such as `--disallowedTools`, `--verbose` and `--permission-prompt-tool`
- https://code.claude.com/docs/en/debug-your-config: checking resolved settings with `claude doctor`
- https://code.claude.com/docs/en/prompt-caching.md: what happens when an entire tool is denied mid-session
- https://code.claude.com/docs/en/skills.md: restricting Claude's skill access
- https://code.claude.com/docs/en/sub-agents.md: subagents and hooks in subagent frontmatter
- https://code.claude.com/docs/en/authentication: authentication precedence and long-lived tokens
- https://code.claude.com/docs/en/agent-sdk/user-input: handling tool approval requests with `canUseTool`
- https://code.claude.com/docs/en/vs-code.md: the built-in IDE MCP server
- https://code.claude.com/docs/en/common-workflows.md: referencing files and directories in prompts
- https://code.claude.com/docs/en/worktrees.md: worktree sessions
- https://git-scm.com/docs/gitignore: gitignore pattern syntax used by Read and Edit rules
