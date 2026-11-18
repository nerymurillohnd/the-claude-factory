# Phase 2: Scripts and hooks

Whether a step of the skill needs a script, an injected command or a hook, and where each lives.

## Script or instructions

Write a script when the step is deterministic, when the work you extracted shows the model rewriting the same helper each time, or when a small slip breaks it: an exact sequence, a strict format, a destructive operation. Keep a step as instructions when it needs judgment, such as choosing, wording or reviewing: a script only hides the judgment.

A command the model can type correctly from memory needs no script; write it in the body.

## Where the script lives

Choose by who must reach it, and where the skill travels:

- **Inside the skill folder** (`scripts/`): travels with the skill to every copy and upload. The default for a script one skill uses.
- **At the plugin level**, shared by several skills of one plugin: reached through the plugin root. The skill then works only inside its plugin.
- **In the plugin's `bin/`**: Claude Code puts it on the shell's PATH while the plugin is enabled, so the body calls the tool by name. Use it for a command-line tool several skills or the user call, and only for a plugin that never needs claude.ai or Cowork: neither installs a plugin that has a `bin/` folder.
- **In the user's project**: only for a project skill, or when the skill states the project must provide it.
- **Outside the plugin**: never. Installing a plugin copies only its own folder, so a path above the plugin root doesn't exist on users' machines.

Incorrect:

```text
my-plugin/skills/deploy/SKILL.md   →  Run `bash ../../../shared/deploy.sh`
~/.claude/skills/report/SKILL.md   →  Run `python3 ~/work/tools/build_report.py`
```

The first breaks after installation; the second works only on its author's machine.

## Injected commands

In Claude Code, an injected command runs when the skill loads and its output replaces it in the body. Use one to hand the model current data it would otherwise fetch first, such as the diff, the branch or open pull requests.

## Skill hooks

A hook in the skill's `hooks` field registers when the skill is invoked and runs for the rest of the session. Use one for a check that must hold on every event once the skill is active, such as validating each file the model writes. A check that must hold whether or not the skill was invoked belongs in the plugin's hooks or in settings instead.

- **Subagents**: the docs don't say whether a skill's hooks register when a subagent preloads the skill or runs it with `context: fork`. Put a check that must hold inside a subagent in that subagent's own `hooks` frontmatter, which runs while the subagent runs. A plugin's subagent ignores `hooks`, `mcpServers` and `permissionMode`, so a plugin puts such a check in its own hooks file, which applies to the whole session.
