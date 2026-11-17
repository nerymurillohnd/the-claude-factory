# Session and workspace

This file teaches you how to recognize the session you write the skill in: its surface, its workspace and the capabilities it gives you, and what they let you save, run and test. It serves workflow steps 1.1, 1.2, 1.3 and 1.7. Each section gives the facts, why they matter for the skill you write, the questions to answer, and what to do with the answers.

## Contents

- How to use this file
- 1. Identify the surface and session
- 2. Identify the workspace
- 3. Identify the capabilities at hand
- 4. Derive the implications
- Verify and go deeper

## How to use this file

Read it at the start of phase 1, before you open or write a skill file.

Work from two seats and keep them apart. Your seat is the session you write in, which decides what you can read, run, save and test now. The model's seat is each session where it will load the skill, which decides what the skill can rely on. A fact you observe in your session holds for your session only: the user's sessions can load other skills, run other policies and lack the tools you have.

Answer each question with evidence you can point to: your system prompt and tool list, an environment variable, the output of a command, or a file. When no evidence settles a question, record it as unknown. Ask the user only when the answer would change what you build or where you save it.

---

## 1. Identify the surface and session

The surface decides which skills load and which of their features run, so you identify it before anything else. Claude Code runs in the terminal, the IDE extensions, the desktop app, cloud sessions and the cloud threads of a Claude project. Claude.ai chat, Cowork and programs built on the Claude API or the Agent SDK are surfaces with their own rules for skills, which section 2 of `skill-loading.md` lists. A cloud session starts from a fresh clone of the repository, so it holds nothing installed only on the user's machine, and a file you leave uncommitted ends with the container. A non-interactive run, a scheduled task and a routine have no person to answer a question or a permission prompt.

Claude Code sets variables you can read from a shell:

- `CLAUDE_CODE_REMOTE` is `true` in a cloud session, and never `true` on a local machine. `CLAUDE_CODE_REMOTE_SESSION_ID` holds the cloud session's ID.
- `CLAUDE_CODE_BRIDGE_SESSION_ID` is set while the session has an active Remote Control connection, in which Claude Code runs on the user's machine and a person follows it from claude.ai or a phone (v2.1.199 or later).
- `CLAUDECODE` is `1` in subprocesses Claude Code spawns, and IDE extensions also set it in their integrated terminals. `CLAUDE_CODE_CHILD_SESSION` is `1` only when Claude Code itself launched the subprocess (v2.1.172 or later).

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

The working directory decides which project skills, `CLAUDE.md` files and rules load, and where a relative path lands. Claude Code loads project skills from `.claude/skills/` in the start directory and in each parent directory up to the repository root. In a linked git worktree it stops at the worktree root, and from v2.1.277, when the worktree has no `.claude/skills` at its root, it loads the main checkout's project skills instead. A `.claude/skills/` folder below the start directory loads only the first time Claude reads or edits a file in that subdirectory. A `paths` glob in a skill matches only files inside the working directory. A directory added with `--add-dir` or `/add-dir` contributes its `.claude/skills/`, `.claude/commands/` and `.claude/agents/`, while the `permissions.additionalDirectories` setting grants file access and loads none of them.

Ask yourself:

1. What is the working directory, and is it inside a git repository? Which repository, branch and worktree?
2. Does the repository hold `.claude/skills/` folders below its root, as a monorepo does?
3. Which directories were added to the session, and which of them hold a `.claude/skills/` folder?
4. Where will each file I create land, and will the sessions that need it look there?

Then:

- Run `pwd`, `git rev-parse --show-toplevel`, `git branch --show-current` and `git worktree list` before you choose where to save.
- List the skills the workspace holds with `find "$(git rev-parse --show-toplevel)" -name SKILL.md -not -path '*/node_modules/*'`, and note which of them your session loaded at startup.
- Write every save path from the repository root, never from the working directory, so a session started in a subdirectory or a worktree finds the file.

## 3. Identify the capabilities at hand

What you can verify depends on the tools this session gives you. Without a shell you cannot run `claude plugin validate`, a script's tests or a trigger test. Without network access you cannot read the current documentation. Without the `claude` CLI you cannot load the skill in a separate session to test it. The installed Claude Code version decides which features exist, since the documentation marks many features with a minimum version. MCP servers connected to the session appear in your tool list as tools named `mcp__<server>__<tool>`, and a documentation server or a GitHub server changes where you research and read. A check you cannot run here ends as not verified, never as passed.

Ask yourself:

1. Can I read and write files here, and in which directories? Can I run shell commands?
2. Is the `claude` CLI installed, and which version is it?
3. Can I reach the official documentation, through a documentation MCP server or the web?
4. Do I have subagent or task tools that start a fresh context, for the behavior tests of phase 7?
5. Which checks of phase 7 can I not run here?

Then:

- Run `claude --version` and record the version: phase 4 reads the release notes from it.
- Take the MCP servers from your tool list. Avoid `claude mcp list` for this, because it starts and health-checks each configured server.
- Write down each check of phase 7 you cannot run here, with the reason, and carry the list to your report.

## 4. Derive the implications

The environment comes down to three answers: where you can save the skill from this session, what you can test in it, and what you must report as not verified. The answers often differ from what the request assumes. A skill saved in a repository's `.claude/skills/` does not load in a cloud thread of a Claude project, so typing its name there cannot test it, while a non-interactive `claude -p` run started inside the repository is a separate session that loads it. A personal skill written in a cloud session lands in the container's `~/.claude/skills/`, which never reaches the user's machine. A skill meant for claude.ai or the Skills API can be built and packaged here, while the upload stays with the user.

Ask yourself:

1. Can the location the skill needs be written from this session, and will the file persist?
2. Can I load the skill, in this session or a separate one, to run the trigger and behavior tests?
3. Which checks will end as not verified, and what would the user need to run them?

Then:

- Write down the three answers before phase 2; step 2.4 and phase 7 rely on them.
- When the location the skill needs cannot be written or tested from this session, tell the user before you build, and name the session that can.
- State the answers in plain terms, for example: "This is a cloud thread of a Claude project with Claude Code 2.1.326. The plugin folder can be written and validated here, and a `claude -p --plugin-dir` run can load the skill for trigger tests. The terminal surface on the user's machine cannot be tested here and will be reported as not verified."

## Verify and go deeper

Read these pages to confirm a fact in this file against the current official guidance, or to go deeper than this file does.

- Claude Code docs, Skills: "Choose where skills load", "Load skills in monorepos and subdirectories", "Load skills from a directory outside the project", "Use skills in Cowork and cloud sessions". https://code.claude.com/docs/en/skills
- Claude Code docs, Environment variables: `CLAUDECODE`, `CLAUDE_CODE_CHILD_SESSION`, `CLAUDE_CODE_BRIDGE_SESSION_ID`, `CLAUDE_CODE_REMOTE`, `CLAUDE_CODE_REMOTE_SESSION_ID`. https://code.claude.com/docs/en/env-vars
- Claude Code docs, Cloud environments: "What carries over from your setup". https://code.claude.com/docs/en/cloud-environments
- Claude Platform docs, Agent Skills overview: "Where Skills work", "Runtime environment constraints". https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
