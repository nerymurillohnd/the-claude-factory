# Subagent frontmatter hooks

Read this in step 5 when the hook belongs to one project or user subagent and must run only while it works.

## Role

You write hooks that live and die with one subagent, scoped to what it does.

## Knowledge

- Lifetime: they run only while that subagent runs and are removed when it finishes. They also run when the agent is the main session through `--agent` or the `agent` setting, beside the settings hooks.
- `Stop` in a subagent's frontmatter runs as `SubagentStop`.
- Every hook event is supported; `PreToolUse`, `PostToolUse` and `Stop` are the usual ones.
- Settings and plugin hooks also fire inside every subagent, with `agent_id` and `agent_type` in the input: a frontmatter hook is needed only when the hook must not run elsewhere.
- Trust: a project subagent's frontmatter hooks run only after the user accepts the workspace trust dialog for the folder the agent file came from. Trusting a parent folder is not enough, and a `-p` session doesn't count. Until then the subagent runs without them, and the debug log says how to trust the folder. User subagents in `~/.claude/agents/` and agents passed with `--agents` are exempt; an `--add-dir` folder needs its own trust.
- `once` is ignored here.
- Docs: `### Define hooks for subagents` in `sub-agents`, `### Hooks in skills and agents` in `hooks`, and `### What runs before you trust a folder` in `permissions`.

## Gotchas

- A plugin agent ignores `hooks` in its frontmatter: use `references/location-subagent-events.md` or the plugin's `hooks/hooks.json` instead.
- Managed `allowManagedHooksOnly` blocks hooks declared in agent frontmatter.
- A hook tested in a `-p` run in an untrusted project never fires, which looks like a broken hook.

## Rules

- Reference a project agent's scripts through `${CLAUDE_PROJECT_DIR}`, and a user agent's through `$HOME` in shell form.
- Tell the user a project agent's hooks need the folder trusted, and how to confirm it in the debug log.

## Structure

- File: the agent's Markdown file in `.claude/agents/` or `~/.claude/agents/`, under `hooks` in the frontmatter.
- Template: `assets/subagent-frontmatter.md`.
