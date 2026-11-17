# Environment

How to find out where you are working, what that lets you save, run and test, and what already exists that the new skill must fit with.

## Contents

- Recognize your surface
- Your session versus the target
- Inventory what exists
- Working with no one to answer

## Recognize your surface

Check, don't assume. The surface decides where you can save the skill and what you can verify:

- **Claude Code on the requester's machine** (terminal, IDE, desktop app): you have a shell and the file system. You can write the skill where it will live, run its scripts, validate it with `claude plugin validate`, and start fresh sessions to test it. Run `claude --version` to know which features apply.
- **Claude Code cloud session or project thread**: a fresh container with the repository cloned. You can write and test inside the repository; personal skills on the requester's machine don't exist here, and anything not committed and pushed is lost when the session ends. In a project's cloud thread, repository skills don't load at all.
- **Cowork**: account skills from claude.ai; injected commands don't run.
- **claude.ai chat with code execution**: you can write files in the sandbox and package a zip for the requester to upload; you can't install it into their account yourself.
- **No shell or file tools**: you can only write the content into your reply. Give the requester each file's path and full content, and the steps to install it.

Signs to check: which tools you have (a shell, file read and write, subagents, web access), the working directory, whether it is a git repository (`git rev-parse --show-toplevel`), and whether `.claude/` or `.claude-plugin/plugin.json` exist.

## Your session versus the target

Where you write the skill is often not where it will run. Keep the two apart:

- A check here proves what it ran against: this Claude Code version, this operating system, these installed tools, this network. It proves nothing about the target surface.
- A skill for claude.ai or the API can't be loaded and tested in Claude Code as it will run there: no substitutions, no injected commands, a different runtime. Validate its fields and structure here, and test the behavior on the target, or list that test as not run.
- A plugin skill runs from the plugin cache once installed, not from its source folder. Test it loaded with `--plugin-dir` and, before release, installed from its marketplace.

Report each check with where it ran, and each one that couldn't run here with the reason.

## Inventory what exists

Before designing, find what the new skill could duplicate, contradict or rely on:

1. The skills already listed in your context, with their descriptions.
2. Skill folders: `.claude/skills/` in the project and its parents, `~/.claude/skills/`, and the plugin's `skills/` if you are in one.
3. Instructions that may conflict: `CLAUDE.md` files and `.claude/rules/`.
4. Subagents in `.claude/agents/` and the plugin's `agents/`.
5. Hooks the skill may interact with: the `hooks` key of the settings files, and the plugin's `hooks/hooks.json`.
6. MCP servers the skill could use: their names from `.mcp.json` or the plugin manifest.

Read names, descriptions and structure; read a whole file only when the new skill must fit with it. Never read the values of settings that hold credentials, environment files or keys: name them, and leave their values unread.

For each match, decide: extend the existing skill instead of writing a new one, set a boundary in both descriptions, or rely on it as a component. A new skill that duplicates an existing one makes the model choose between them at random.

## Working with no one to answer

In an unattended run (a scheduled task, a background agent, a `-p` run) no one can answer a question:

- Take the reading of the request that the sources and the existing files support best.
- Record each assumption you made in place of an answer.
- Don't take any irreversible or outward-facing step that needed the requester's approval; leave it for them.
- Deliver the skill with a report that lists the assumptions, the decisions that would have needed approval, and what remains open.
