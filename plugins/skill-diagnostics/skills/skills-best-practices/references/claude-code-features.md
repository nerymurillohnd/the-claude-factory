# Claude Code features

Invocation control, substitutions, pre-approved tools, dynamic context, forked subagents and hooks in a skill. These work only in Claude Code, not in claude.ai chat or the API \[CC\].

## Contents

- [Invocation control](#invocation-control)
- [Substitutions and pre-approved tools](#substitutions-and-pre-approved-tools)
- [Dynamic context](#dynamic-context)
- [Forked subagents](#forked-subagents)
- [Hooks in a skill](#hooks-in-a-skill)
- [Other behaviors](#other-behaviors)

## Invocation control

**Two kinds of content** \[CC\]: reference content (conventions, domain knowledge) runs inline beside the conversation; task content (deploy, commit) is usually invoked by the user with `/name` and often sets `disable-model-invocation: true`.

| Frontmatter | You can invoke | Claude can invoke | Description in context |
| --- | --- | --- | --- |
| (default) | Yes | Yes | Always |
| `disable-model-invocation: true` | Yes | No | No |
| `user-invocable: false` | No | Yes | Always |

**Which setting to use.** Use `disable-model-invocation: true` for side effects or timing you control (`/commit`, `/deploy`); `user-invocable: false` for background knowledge that isn't a meaningful command \[CC\]. The combinations that disable a skill are in [frontmatter.md](frontmatter.md#combinations-that-disable-a-skill).

## Substitutions and pre-approved tools

**Substitutions** \[CC\]: `$ARGUMENTS`, `$ARGUMENTS[N]` or `$N`, named `$name` from `arguments`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, and in plugin skills `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}`. If no placeholder receives the arguments, Claude Code appends `ARGUMENTS: <value>`. Escape a literal `$1` as `\$1`.

- **Escaping a literal `$`.** Substitution runs everywhere in the body, code blocks included. A literal `$` before a digit, before `ARGUMENTS`, or before a declared argument name needs one backslash directly before it: `\$1.00`, `\$ARGUMENTS`, and `\$issue` when `arguments` declares `issue` \[CC\] `req`. A doubled backslash doesn't escape (`\\$1` still expands), a backslash before any other `$` stays as written, and the backslash doesn't stop a `${CLAUDE_*}` variable from being substituted \[CC\].
- **Argument values are inserted as text.** An argument value that itself contains `$1` or `$ARGUMENTS` is inserted as literal text; `${CLAUDE_*}` variables are still replaced after the arguments are inserted \[CC\].
- **Argument name limits.** Only the first 64 names declared in `arguments`, each up to 64 characters, are filled in \[CL\] (2.1.301; not on the skills page) `req`.
- **Use every declared argument.** Every name declared in `arguments` appears as `$name` in the body \[SD\] `req`.
- **Where the path placeholders are substituted.** Claude Code substitutes `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PROJECT_DIR}` "in two places: the skill's markdown content, and Bash rules in the `allowed-tools` frontmatter. In a plugin skill, Claude Code substitutes `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` in the same two places" \[CC\] `req`. A file the skill links to (a reference, an asset) isn't substituted: Claude reads it with the placeholder as literal text \[SD\] `observed` (Claude Code 2.1.319, 2026-11-09), and "the variables aren't present in the environment of commands Claude runs through the Bash tool" \[CC\], so a command copied from there fails or prompts. Write every command that uses one of these placeholders in `SKILL.md`, and in a reference point to `SKILL.md` for it `req`.
- **Text substitutions, not environment variables.** The `${CLAUDE_*}` variables are text substitutions in the skill, not environment variables: a command the Bash tool runs doesn't see them unless the text passed them in \[SD\] `default`.

**Pre-approve a bundled script** by using the same variable in the body and in `allowed-tools` \[CC\].

- **Match the whole command line.** `Bash()` rules "match the whole command line" \[CP\], so the pattern repeats the command form the body uses `req`. With the default form ([scripts.md](scripts.md#how-to-call-a-script)), the body runs `python3 ${CLAUDE_SKILL_DIR}/scripts/render.py` and the rule is `allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/render.py *)` `default`; a shell script uses `bash` in both places. A skill that runs a script directly, by its shebang and executable bit, needs the direct pattern, as in the skills page's example: `Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)` \[CC\].
- **Scope of the grant.** The grant lasts one turn, isn't gated by workspace trust, and is ignored under `allowManagedPermissionRulesOnly` \[CC\].
- **Name the exact command.** A bare `allowed-tools: Bash` pre-approves every shell command for that turn \[SD\] `rec`.

## Dynamic context

**Dynamic context** \[CC\]: a line that starts with `!` followed by a backticked command, or a fenced block opened with three backticks and `!`, runs before Claude sees the skill and inlines the output. Any failure aborts the whole invocation (exit 1 from search commands excepted; append `|| true` to checks that exit non-zero). Commands are checked against permission rules and abort instead of prompting outside auto mode. They don't run for skills synced from claude.ai on the user's machine, and `disableSkillShellExecution` turns them off.

- **`UserPromptSubmit` runs first.** `UserPromptSubmit` hooks run before a skill expands, so a hook that blocks the prompt also stops the skill's `!` commands; a skill's own frontmatter `UserPromptSubmit` hook first runs on the prompt after the one that invokes the skill \[CL\] (2.1.299; not found on the hooks or skills page) `req`.
- **Never put an argument placeholder inside a `!` command.** The argument is substituted into the command as text before the shell runs it, so a user argument such as `$(echo INJECTED)` executes \[SD\] `observed` (Claude Code 2.1.296, 2026-10-12). Run the command without the argument, then hand the argument to Claude in prose: `Find the commits that match: $ARGUMENTS`.

## Forked subagents

**Forked subagent** \[CC\]: `context: fork` (+ `agent: Explore | Plan | general-purpose | <custom>`) runs the skill as the prompt of an isolated subagent that doesn't see the conversation, in the background by default (`background: false` waits). Use it only for skills with an explicit task; guideline-only content returns nothing useful. Background forks get a narrower tool set and their edits aren't covered by `/rewind`.

- **Forks on Explore or Plan.** The built-in Explore and Plan agents start without CLAUDE.md and git status, so a fork on them writes every rule its task needs in `SKILL.md` \[CC\] `req`.

## Hooks in a skill

A skill's `hooks` frontmatter registers its hooks when the skill is invoked and keeps them for the rest of the session; before the first invocation they don't exist \[CC\]. `once: true` removes a hook after its first successful run \[CC\].

- **Paths.** Hook commands resolve `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}`; `${CLAUDE_SKILL_DIR}` is not among them, so a plugin skill reaches its own script through the plugin root \[CC\] `req`. A plugin hook reaches a script through `${CLAUDE_PLUGIN_ROOT}` `default`.
- **Quoting.** Prefer exec form (`args`) for any hook that references a path placeholder; in shell form, wrap each placeholder in double quotes \[CC\] `req`.
- **`onFailure: "block"`** makes a `command` or `http` hook block the action when it can't start, times out or fails; it has no effect on `Stop`, `SubagentStop`, `TaskCompleted` and `TeammateIdle` hooks \[CC\] `req`.
- **Managed lock.** Under the managed setting `strictPluginOnlyCustomization` with `hooks`, frontmatter hooks run only in plugin skills, bundled skills and managed skills, and a personal or project skill whose frontmatter declares `hooks` also loses its `allowed-tools` pre-approval \[CC\] (2.1.304).
- **Hook limit.** The skills of one source (the project, the personal skills folder, each plugin) can register at most 1,024 hooks per session, whose matchers total at most 16,384 characters; a skill past the limit runs without any of its frontmatter hooks \[CC\] (2.1.304) `req`.
- **Other surfaces.** Uploads and the Skills API reject the `hooks` field ([frontmatter.md](frontmatter.md#fields-by-surface)), and chat ignores plugin hooks ([surfaces.md](surfaces.md#plugin-components-by-surface)).

## Other behaviors

\[CC\]:

- **`paths`** limits automatic activation to matching files in the working directory.
- **Live edits.** Skill folders are watched for live edits; a new top-level skills folder needs `/reload-skills`.
- **Typing the skill name** after plain text only permits Claude to run it.
