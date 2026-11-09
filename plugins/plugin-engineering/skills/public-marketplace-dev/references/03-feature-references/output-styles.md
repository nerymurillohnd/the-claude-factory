# Output styles

> An output style changes Claude Code's role, tone, and response format, through a built-in style such as Concise or Explanatory or a custom style. This file covers how a style is selected, how to write a custom style (including the plugin-only `force-for-plugin` field), when another feature fits better, and how styles affect the system prompt and token usage.

## Contents

- [What an output style is](#what-an-output-style-is)
- [Change your output style](#change-your-output-style)
- [Create a custom output style](#create-a-custom-output-style)
  - [Frontmatter reference](#frontmatter-reference)
- [Choose between an output style and other features](#choose-between-an-output-style-and-other-features)
- [How output styles work](#how-output-styles-work)
- [Documentation References](#documentation-references)

## What an output style is

An output style is a set of instructions that sets Claude's role, tone, and response format for every response in a session. Claude Code includes four built-in styles besides its default, and users can write their own.

An output style changes the way Claude responds and works for a whole session, so the user does not repeat the request in each prompt. For example, a built-in style can make responses shorter, add an explanation of each change, or have Claude start work without asking routine questions. A custom style can also turn Claude into something other than a software engineer, such as a writing assistant or a data analyst.

* To write custom instructions, [create a custom output style](#create-a-custom-output-style).

> **Note:** An output style gives Claude instructions to follow. It does not guarantee that something always happens or never happens. Some needs fit a different feature:
>
> * For what Claude should know about the project, use [CLAUDE.md](https://code.claude.com/docs/en/memory.md).
> * For something that has to happen every time, such as formatting after each edit or blocking a command, use a [hook](https://code.claude.com/docs/en/hooks-guide.md).
> * For skills, subagents, and the other options, see [Choose between an output style and other features](#choose-between-an-output-style-and-other-features).

## Change your output style

A style is picked with the command, a menu, or a settings file. The command and both menus save the choice to `.claude/settings.local.json` at the [local project level](https://code.claude.com/docs/en/settings.md).

* **`/output-style` command**: run `/output-style <style>` to switch, for example `/output-style concise`. With no argument, the command lists the styles available and marks the current one.

  The command also works in [non-interactive mode](https://code.claude.com/docs/en/headless.md) and Agent SDK sessions, and from the mobile app or web via [Remote Control](https://code.claude.com/docs/en/remote-control.md#limitations), where only [built-in styles](https://code.claude.com/docs/en/output-styles#built-in-output-styles) can be listed and selected. Requires Claude Code v2.1.269 or later.
* **Terminal menu**: run `/config` and select **Output style** to pick a style from a menu.
* **VS Code extension**: open the [command menu](https://code.claude.com/docs/en/vs-code.md#use-the-prompt-box) with `/` and select **Output styles** to pick a style, including custom styles. Requires Claude Code v2.1.257 or later.
* **Desktop app**: set the `outputStyle` field in a settings file, for example `.claude/settings.local.json`, the file the terminal menu writes. Running `/config` there makes Claude Code [open **Settings > Code** or **Settings > Claude Code**](https://code.claude.com/docs/en/desktop.md#what’s-not-available-in-desktop) rather than a menu.

To set a style without the menu, edit the `outputStyle` field directly in a settings file:

```json theme={null}
{
  "outputStyle": "Explanatory"
}
```

Rules for the `outputStyle` value:

- The value is case-sensitive, so write the built-in names as `Proactive`, `Concise`, `Explanatory`, and `Learning`. A value that does not match a style name exactly, such as `explanatory`, gives the Default style. The `/output-style` command ignores case.
- To make a style the default across projects, set `outputStyle` in `~/.claude/settings.json`. A project's own settings files [take precedence](https://code.claude.com/docs/en/settings.md#settings-precedence) over that value.

When the style is switched mid-session, Claude uses the new style starting with the next message. For what that first message costs in prompt caching, see [Changing output style](https://code.claude.com/docs/en/prompt-caching.md#changing-output-style). Before v2.1.251, the new style applied only after running `/clear` or starting a new session.

## Create a custom output style

A custom output style is a Markdown file: frontmatter for metadata, then the instructions for Claude.

**1. Create a Markdown file**

Save it at one of three levels. The file name becomes the style name unless `name` is set in the frontmatter.

* User: `~/.claude/output-styles`
* Project: `.claude/output-styles`

Project output styles load from every `.claude/output-styles/` between the working directory and the repository root. When more than one of these nested directories defines a style with the same name, Claude Code uses the one closest to the working directory.

**2. Add frontmatter and instructions**

Decide whether to keep Claude Code's software engineering instructions. Set `keep-coding-instructions: true` when the style changes how Claude communicates but Claude should still code the same way. Leave it out if Claude will not be doing software engineering.

This example leads every explanation with a diagram while keeping Claude's coding behavior:

```markdown theme={null}
---
name: Diagrams first
description: Lead every explanation with a diagram
keep-coding-instructions: true
---

When explaining code, architecture, or data flow, start with a Mermaid diagram showing the structure, then explain in prose.

## Diagram conventions

Use `flowchart TD` for control flow and `sequenceDiagram` for request paths. Keep diagrams under 15 nodes.
```

**3. Switch to the style**

Run `/output-style <style>` in the terminal, or run `/config` and select the style under **Output style**. Claude uses the new style starting with the next message. In the terminal, Claude Code reads style files when it starts, so after creating or editing one during a running session, restart Claude Code to pick up the change.

[Plugins](https://code.claude.com/docs/en/plugins/manifest-reference.md) can also ship output styles in an `output-styles/` directory.

### Frontmatter reference

Configure an output style with YAML [frontmatter](https://code.claude.com/docs/en/glossary.md#frontmatter) between `---` markers at the top of the file. Parsing rules:

- All fields are optional, and field names use lowercase words separated by hyphens.
- A misspelled field is ignored without an error.
- If the YAML does not parse, the style still loads under its file name with no fields set; run `claude --debug` to see the parse error.

| Field | Required | Description |
| :- | :- | :- |
| `name` | No | Name of the output style, shown in the `/config` picker. Default: the file name |
| `description` | No | Description of the output style, shown in the `/config` picker |
| `keep-coding-instructions` | No | Set to `true` to keep Claude Code's section of built-in software engineering instructions, which only the full system prompt includes, alongside your style. See [How output styles work](#how-output-styles-work). Default: `false` |
| `force-for-plugin` | No | Plugin output styles only. Set to `true` to apply this style automatically whenever the plugin is enabled, without requiring users to select it. Overrides the user's `outputStyle` setting. If multiple enabled plugins set this, Claude Code uses the first one loaded. Default: `false` |

## Choose between an output style and other features

An output style applies to every response in a session. It is an instruction Claude follows, so nothing enforces it. When the need is narrower than every response, or has to happen without fail, another feature fits better.

This table matches each need to the feature that does it:

| You want | Use | Why it fits |
| :- | :- | :- |
| Every response in a certain voice, length, or format, or Claude in a different role | An output style | It applies to the whole session, and you switch styles with one command |
| Claude to know your project's conventions, commands, and structure | [CLAUDE.md](https://code.claude.com/docs/en/memory.md) | It holds what Claude should know about the codebase, and it stays loaded whichever style you pick |
| Instructions for one kind of task, such as a release checklist or a review procedure | A [skill](https://code.claude.com/docs/en/skills.md) | Claude loads it only when you invoke it or the task matches, so it doesn't shape unrelated responses |
| Something to happen every time without exception, such as formatting after each edit or blocking a command | A [hook](https://code.claude.com/docs/en/hooks-guide.md) | Claude Code runs a hook itself at a lifecycle event, so it doesn't depend on Claude following an instruction |
| A helper with its own instructions, model, and tools for a focused task | A [subagent](https://code.claude.com/docs/en/sub-agents.md) | It runs in a separate context with its own system prompt and returns a summary to your conversation |

These features combine. For example, use CLAUDE.md for what Claude should know, an output style for how it responds, and a hook for anything that has to be guaranteed. [Extend Claude Code](https://code.claude.com/docs/en/features-overview.md) compares the rest of the extension features.

## How output styles work

An output style changes the instructions Claude Code gives Claude.

* Claude Code sends the active style's instructions with every request.
* On the full system prompt, custom output styles leave out Claude Code's section of built-in software engineering instructions, such as how to scope changes, write comments, and verify work, unless `keep-coding-instructions` is set to `true`. The shorter system prompt does not include that section, so the field has no effect there. To rely on the field, set [`CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT`](https://code.claude.com/docs/en/env-vars#variables) to `0`, which selects the full prompt on any model.

Scope: output styles apply to the main conversation and to a [fork](https://code.claude.com/docs/en/sub-agents.md#fork-the-current-conversation), which inherits the parent's whole conversation and system prompt. Other [subagents run their own system prompt](https://code.claude.com/docs/en/sub-agents.md#what-loads-at-startup), so styles do not change how they respond.

Token usage depends on the style:

- A style's instructions add input tokens, though prompt caching reduces this cost after the first request in a session.
- The built-in Explanatory and Learning styles produce longer responses than Default by design, which increases output tokens. The Concise style does the opposite by instructing Claude to keep responses short by default.
- For custom styles, output token usage depends on what the instructions tell Claude to produce.

## Documentation References

- Source page: https://code.claude.com/docs/en/output-styles (full output styles guide, including the built-in styles)
- https://code.claude.com/docs/en/memory.md - CLAUDE.md for project knowledge
- https://code.claude.com/docs/en/hooks-guide.md - hooks for actions that must always happen
- https://code.claude.com/docs/en/settings.md - where the `outputStyle` field lives and how settings precedence works
- https://code.claude.com/docs/en/headless.md - non-interactive mode
- https://code.claude.com/docs/en/remote-control.md - Remote Control limitations
- https://code.claude.com/docs/en/vs-code.md - the VS Code extension's prompt box and command menu
- https://code.claude.com/docs/en/desktop.md - what is not available in the Desktop app
- https://code.claude.com/docs/en/prompt-caching.md - prompt caching cost of changing output style
- https://code.claude.com/docs/en/plugins/manifest-reference.md - shipping output styles in a plugin's `output-styles/` directory
- https://code.claude.com/docs/en/glossary.md - definition of frontmatter
- https://code.claude.com/docs/en/skills.md - skills for task-specific instructions
- https://code.claude.com/docs/en/sub-agents.md - subagents, forks, and what loads at startup
- https://code.claude.com/docs/en/features-overview.md - comparison of all extension features
- https://code.claude.com/docs/en/env-vars - `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT` and other environment variables
- https://code.claude.com/docs/en/plugins/overview.md - package and distribute output styles alongside skills, hooks, and agents
- https://code.claude.com/docs/en/debug-your-config.md - diagnose why an output style is not taking effect
