# Session and workspace

This file teaches you how to recognize the session you write the skill in: its surface, its workspace and the capabilities it gives you, and what they let you save, run and test. It serves workflow steps 1.1, 1.2, 1.3 and 1.7, and step 2.4, where section 4 is settled for the location you choose.

## Contents

- How to use this file
- 1. Identify the surface and session
- 2. Identify the workspace
- 3. Identify the capabilities at hand
- 4. Derive the implications
- Verify and go deeper

## How to use this file

Read it at the start of phase 1, before you open or write a skill file.

Keep the two seats of the rule "Two seats" in `SKILL.md` apart: here you establish your own seat, and the questions about the target sessions come back at step 2.4.

Answer each question with evidence you can point to: your system prompt and tool list, an environment variable, the output of a command, or a file. When no evidence settles a question, record it as unknown. Ask the user only when the answer would change what you build or where you save it.

---

## 1. Identify the surface and session

The surface decides which skills load and which of their features run, so you identify it before anything else. Claude Code runs in the terminal, the IDE extensions, the desktop app, cloud sessions and the cloud threads of a Claude project. Claude.ai chat, Cowork and programs built on the Claude API or the Agent SDK are surfaces with their own rules for skills, which section 2 of `references/environment/skill-loading.md` lists. A file you write in a cloud session ends with its container unless you commit it and push it to the remote, because the next cloud session starts from a fresh clone. A non-interactive run (`claude -p`) and a cloud scheduled task, also called a routine, have no person to answer a question or a permission prompt.

Claude Code sets variables you can read from a shell:

- `CLAUDE_CODE_REMOTE` is set to `true` when Claude Code runs as a cloud session. `CLAUDE_CODE_REMOTE_SESSION_ID` holds the cloud session's ID.
- `CLAUDE_CODE_BRIDGE_SESSION_ID` is set while the session has an active Remote Control connection, in which Claude Code runs on the user's machine and a person follows it from claude.ai or a phone (v2.1.199 or later).

Ask yourself:

1. Am I in Claude Code, claude.ai chat, Cowork, or a program built on the Claude API or the Agent SDK, and what evidence says so?
2. Does this session run on the user's machine, in a cloud container, or in a cloud thread of a Claude project?
3. Can a person answer my questions and approve my tool calls during this run?
4. Which permission mode governs my tool calls, and which of my planned commands would stop on a prompt?
5. Is the Bash sandbox on, and which paths and network hosts does it let my commands reach?

Then:

- Read the variables with one command, for example `printf '%s\n' "remote=${CLAUDE_CODE_REMOTE:-unset}" "bridge=${CLAUDE_CODE_BRIDGE_SESSION_ID:+set}"`, and combine the result with what your system prompt states about the surface, the permission mode and the sandbox.
- Avoid inferring the surface from the operating system or the home directory alone: a Linux home directory belongs to cloud containers and to workstations alike.
- When no person can answer during the run, decide each open question from the sources, avoid the steps that need an approval you cannot get, and list both in your report.

## 2. Identify the workspace

The working directory decides which project skills, `CLAUDE.md` files and rules load, and where a relative path lands. Which `.claude/skills/` folders load from it, and when, is in section 1 of `references/environment/skill-loading.md`, which you apply at step 1.4; here you record what the workspace holds.

Ask yourself:

1. What is the working directory, and is it inside a git repository? Which repository, branch and worktree?
2. Does the repository hold `.claude/skills/` folders below its root, as a monorepo does?
3. Which directories were added to the session, and which of them hold a `.claude/skills/` folder?
4. Where will each file I create land, and will the sessions that need it look there?

Then:

- Before you choose where to save, list the `SKILL.md` files the workspace holds, outside `node_modules`; step 1.4 maps which of them your session loaded.
- When the working directory is not inside a git repository, record that there is no repository, branch or worktree.
- Write each save path as an absolute path: from the repository root for a file inside a repository, from the expanded home directory, the value of `$HOME`, for a personal skill, and from the working directory when there is no repository. A path relative to the working directory misses for a session started in a subdirectory or a worktree.

## 3. Identify the capabilities at hand

What you can verify depends on the tools this session gives you. Without a shell you cannot run `claude plugin validate`, a script's tests or a trigger test. Without network access you cannot read the current documentation. Without the `claude` CLI you cannot load the skill in a separate session to test it. The installed Claude Code version decides which features exist, since the documentation marks many features with a minimum version. MCP servers connected to the session appear in your tool list as tools named `mcp__<server>__<tool>`, and a documentation server or a GitHub server changes where you research and read.

Ask yourself:

1. Can I read and write files here, and in which directories? Can I run shell commands?
2. Is the `claude` CLI installed, and which version is it?
3. Can I reach the official documentation, through a documentation MCP server or the web?
4. Do I have subagent or task tools that start a fresh context, for the behavior tests of phase 7?
5. Which checks of phase 7 can I not run here?

Then:

- Run `claude --version` and record the version: phase 4 reads the changelog for it.
- Take the MCP servers from your tool list. Avoid `claude mcp list` for this, because it starts and health-checks each configured server.
- Write down each check of phase 7 you cannot run here, with the reason, and carry the list to your report.

## 4. Derive the implications

The environment comes down to three answers: where you can save the skill from this session, what you can test in it, and what you must report as not verified. The answers often differ from what the request assumes. A skill saved in a location the target surface does not read cannot be tested there by typing its name (section 2 of `references/environment/skill-loading.md`). A personal skill written in a cloud session lands in the container's `~/.claude/skills/`, which never reaches the user's machine. A skill meant for claude.ai or the Skills API can be built and packaged here, while the upload stays with the user.

A separate non-interactive run, `claude -p` started in the repository, with `--plugin-dir <plugin folder>` for a plugin skill, is a second session that can load the skill for trigger tests. No official page documents this run inside a cloud container. One such run, started in the repository inside a cloud thread of a Claude project on v2.1.326, was observed loading both the repository's project skills and the `--plugin-dir` plugin's skills, which the thread itself does not load; treat it as unconfirmed on other versions and confirm it each time with the check below. A managed `disableSideloadFlags` makes Claude Code reject `--plugin-dir` at startup and exit with an error that names the flag (v2.1.193 or later); on that error, report the tests that need the run as not verified. A `.claude/skills/` folder inside the plugin folder follows the v2.1.325 limit in section 1 of `references/environment/skill-loading.md`.

Ask yourself:

1. Which locations can be written from this session, and will a file there persist?
2. Can I load the skill, in this session or a separate one, to run the trigger and behavior tests?
3. What would the user need to run each check you listed at step 1.3 as not runnable here?

Then:

- Write down the three answers before phase 2, for each location this session can write and for the location the request names, if it names one. At step 2.4, settle them for the location you choose; phase 7 relies on them.
- Before you plan tests on a separate run, confirm it loads the skill: start it with `--output-format stream-json --verbose` and read the `skills` array of its `init` message. That array lists only user-invocable skills with a `description` or `when_to_use`, so for a skill with `user-invocable: false`, run a trigger prompt instead. When the skill is missing, report the tests that depend on the run as not verified.
- Claude Code picks up the `SKILL.md` text you add, edit or remove under `~/.claude/skills/`, the project's `.claude/skills/` or an added directory's `.claude/skills/` within the session, except in bare mode, but only in top-level skills directories that existed when the session started. A top-level skills directory you create during the session loads only after the user runs `/reload-skills`, and again after each later change there. For a skill folder that is also a plugin, changes to its `.mcp.json`, `agents/`, `output-styles/` and `hooks/` need `/reload-plugins`, apart from a mod's module file that reloads on its own. A plugin folder that is not inside a skills directory your session reads, and that you did not pass with `--plugin-dir` when the session started, does not load in your session, so test it in the separate run.
- For each check you listed at step 1.3 as not runnable here, write the session and the command the user would run it with, and carry both to the report of step 8.1.
- When the location you choose at step 2.4 cannot be written or tested from this session, tell the user before you build, and name the session that can.
- State the answers in plain terms. In this example the version, the surface and the run's result are illustrative values, and the three answers are the fixed part: "This is a cloud thread of a Claude project with Claude Code 2.1.326. The plugin folder can be written and validated here, and a `claude -p --plugin-dir` check run listed the skill, so trigger tests can run here. The terminal surface on the user's machine cannot be tested here and will be reported as not verified."

## Verify and go deeper

Read these pages to confirm a fact in this file against the current official guidance, or to go deeper than this file does.

- Claude Code docs, Skills: "Choose where skills load", "Load skills in monorepos and subdirectories", "Load skills from a directory outside the project", "Use skills in Cowork and cloud sessions", "Edit a skill during a session". https://code.claude.com/docs/en/skills
- Claude Code docs, Environment variables: `CLAUDE_CODE_BRIDGE_SESSION_ID`, `CLAUDE_CODE_REMOTE`, `CLAUDE_CODE_REMOTE_SESSION_ID`. https://code.claude.com/docs/en/env-vars
- Claude Code docs, Settings: `disableSideloadFlags`. https://code.claude.com/docs/en/settings-reference
- Claude Code docs, Cloud environments: "What carries over from your setup". https://code.claude.com/docs/en/cloud-environments
- Claude Code changelog, for the version you run and the releases since the docs were last updated. https://code.claude.com/docs/en/changelog
- Claude Platform docs, Agent Skills overview: "Where Skills work", "Runtime environment constraints". https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
