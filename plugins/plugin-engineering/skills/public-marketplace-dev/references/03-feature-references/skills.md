# Extend Claude with skills

How to write, configure, invoke, evaluate and ship Claude Code skills (`SKILL.md`), including the custom commands merged into skills, with a focus on skills that a plugin distributes.

## Contents

- [Getting started](#getting-started)
  - [Create your first skill](#create-your-first-skill)
- [Choose where skills load](#choose-where-skills-load)
  - [Resolve skills that share a name](#resolve-skills-that-share-a-name)
  - [Remove a skill](#remove-a-skill)
- [Configure skills](#configure-skills)
  - [Types of skill content](#types-of-skill-content)
  - [Frontmatter reference](#frontmatter-reference)
    - [Using skill frontmatter outside Claude Code](#using-skill-frontmatter-outside-claude-code)
    - [How a skill gets its command name](#how-a-skill-gets-its-command-name)
    - [Characters a skill name can't hold](#characters-a-skill-name-cant-hold)
    - [Available string substitutions](#available-string-substitutions)
  - [Add supporting files](#add-supporting-files)
  - [Control who invokes a skill](#control-who-invokes-a-skill)
    - [Where you write the skill's name](#where-you-write-the-skills-name)
  - [Skill content lifecycle](#skill-content-lifecycle)
  - [Pre-approve tools for a skill](#pre-approve-tools-for-a-skill)
    - [When managed settings lock hooks to plugins](#when-managed-settings-lock-hooks-to-plugins)
    - [When only managed permission rules apply](#when-only-managed-permission-rules-apply)
  - [Pass arguments to skills](#pass-arguments-to-skills)
    - [Stack several skills in one message](#stack-several-skills-in-one-message)
- [Advanced patterns](#advanced-patterns)
  - [Inject dynamic context](#inject-dynamic-context)
    - [How injected commands run](#how-injected-commands-run)
    - [When an injected command fails](#when-an-injected-command-fails)
    - [When no shell command was run](#when-no-shell-command-was-run)
    - [Permission checks on injected commands](#permission-checks-on-injected-commands)
  - [Run skills in a subagent](#run-skills-in-a-subagent)
    - [Example: Research skill using Explore agent](#example-research-skill-using-explore-agent)
  - [Restrict Claude's skill access](#restrict-claudes-skill-access)
  - [Override skill visibility from settings](#override-skill-visibility-from-settings)
- [Evaluate and iterate on a skill](#evaluate-and-iterate-on-a-skill)
  - [Run evals with skill-creator](#run-evals-with-skill-creator)
- [Share skills](#share-skills)
  - [Generate visual output](#generate-visual-output)
- [Troubleshooting](#troubleshooting)
  - [Skill not triggering](#skill-not-triggering)
  - [Skill triggers too often](#skill-triggers-too-often)
  - [Claude stops following a skill](#claude-stops-following-a-skill)
  - [Skill descriptions are cut short](#skill-descriptions-are-cut-short)
  - [Angle brackets in a skill description show as `&lt;` and `&gt;`](#angle-brackets-in-a-skill-description-show-as-lt-and-gt)
- [Documentation References](#documentation-references)

A skill is a `SKILL.md` file of instructions that Claude adds to its toolkit. Claude loads a skill when it is relevant, and the user can invoke one directly with `/skill-name`.

Write a skill when the same instructions, checklist or multi-step procedure keeps being pasted into chat, or when a section of CLAUDE.md has grown into a procedure rather than a fact. Unlike CLAUDE.md content, a skill's body loads only when the skill is used, so long reference material costs almost nothing until it is needed.

> **Note:** For built-in commands like `/help` and `/compact`, and bundled skills like `/debug` and `/code-review`, see the [commands reference](https://code.claude.com/docs/en/commands.md).
>
> **Custom commands have been merged into skills.** A file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy` and work the same way. Existing `.claude/commands/` files keep working. Skills add optional features: a directory for supporting files, frontmatter to [control whether the user or Claude invokes them](#control-who-invokes-a-skill), and the ability for Claude to load them automatically when relevant.

Claude Code skills follow the [Agent Skills](https://agentskills.io) open standard, which works across multiple AI tools. Claude Code extends the standard with features such as [invocation control](#control-who-invokes-a-skill), [subagent execution](#run-skills-in-a-subagent) and [dynamic context injection](#inject-dynamic-context). [Using skill frontmatter outside Claude Code](#using-skill-frontmatter-outside-claude-code) lists which frontmatter fields belong to the standard and which are Claude Code extensions.

## Getting started

### Create your first skill

This example builds a skill that summarizes the uncommitted changes in a git repository and flags anything risky. It pulls the live diff into the prompt before Claude reads it, so the response rests on the actual working tree rather than on what Claude can guess from open files. Claude loads the skill automatically when the user asks about their changes, and the user can also invoke it directly with `/summarize-changes`.

**1. Create the skill directory**

Create a directory for the skill in the personal skills folder. Personal skills are available across all of the user's projects.

```bash theme={null}
mkdir -p ~/.claude/skills/summarize-changes
```

**2. Write SKILL.md**

Every skill needs a `SKILL.md` file with two parts: YAML frontmatter between `---` markers that tells Claude when to use the skill, and Markdown content with the instructions Claude follows when the skill runs. The directory name, or the frontmatter `name` when one is set, becomes the command the user types, and the `description` helps Claude decide when to load the skill automatically.

Save this to `~/.claude/skills/summarize-changes/SKILL.md`:

```yaml theme={null}
---
description: Summarizes uncommitted changes and flags anything risky. Use when the user asks what changed, wants a commit message, or asks to review their diff.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any risks you notice such as missing error handling, hardcoded values, or tests that need updating. If the diff is empty, say there are no uncommitted changes.
```

The `` !`git diff HEAD` `` line uses [dynamic context injection](#inject-dynamic-context): Claude Code runs the command and replaces the line with its output before Claude sees the skill content, so the instructions arrive with the current diff already inlined.

**3. Test the skill**

Open a git project, make a small edit to any file, and start Claude Code by running `claude`. Test the skill in two ways.

**Let Claude invoke it automatically** by asking something that matches the description:

```text theme={null}
What did I change?
```

**Or invoke it directly** with the skill name:

```text theme={null}
/summarize-changes
```

Either way, the expected response is a short summary of the edit and a list of risks.

## Choose where skills load

Where a skill is saved decides which sessions load it. A skill under the home directory loads in every project; a skill committed to a repository is shared with everyone who works there; a skill distributed through a plugin or managed settings reaches a whole team. This copy lists only the plugin location; the other locations are on the [source page](https://code.claude.com/docs/en/skills).

| Location | Path | Loads in |
| :- | :- | :- |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | Wherever the [plugin](https://code.claude.com/docs/en/plugins/overview.md) is enabled, as `/plugin-name:skill-name` |

### Resolve skills that share a name

When two skills share a directory or file name, the source of each one decides which one `/name` runs. For a name set by the frontmatter `name` field, see [How a skill gets its command name](#how-a-skill-gets-its-command-name).

| Same name in | Which one runs |
| :- | :- |
| A plugin skill and a skill at any of the locations above | Both load, because plugin skills are namespaced as `/plugin-name:skill-name` |

### Remove a skill

How to remove a skill depends on its source:

* **Plugin skill**: disable or uninstall the plugin that provides it, from the `/plugin` menu or with `/plugin uninstall <plugin-name>@<marketplace-name>`. Claude Code unloads the plugin's skills when [the change applies](https://code.claude.com/docs/en/plugins/cli-reference.md#reload-plugins) or at the next restart.

## Configure skills

Configure a skill through the YAML frontmatter at the top of `SKILL.md` and the Markdown content that follows it.

### Types of skill content

A skill file can contain any instructions. Decide first how the skill will be invoked, because that decides what to include:

**Reference content** adds knowledge Claude applies to the current work: conventions, patterns, style guides, domain knowledge. This content runs inline, so Claude uses it alongside the conversation context.

```yaml theme={null}
---
name: api-conventions
description: API design patterns for this codebase
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats
- Include request validation
```

**Task content** gives Claude step-by-step instructions for a specific action, such as a deployment, a commit or code generation. The user often wants to invoke these directly with `/skill-name` rather than let Claude decide when to run them. Add `disable-model-invocation: true` to keep Claude from triggering such a skill automatically. The example below also sets `context: fork`, which runs the skill in its own subagent context; see [Run skills in a subagent](#run-skills-in-a-subagent).

```yaml theme={null}
---
name: deploy
description: Deploy the application to production
context: fork
disable-model-invocation: true
---

Deploy the application:
1. Run the test suite
2. Build the application
3. Push to the deployment target
```

Keep the body concise. Once a skill loads, its content [stays in context across turns](#skill-content-lifecycle), so every line is a recurring token cost. State what to do rather than narrating how or why, and apply the same conciseness test as for [CLAUDE.md content](https://code.claude.com/docs/en/best-practices.md#keep-claude-md-short).

### Frontmatter reference

Configure a skill with YAML [frontmatter](https://code.claude.com/docs/en/glossary.md#frontmatter) between `---` markers at the top of `SKILL.md`, and write the skill's instructions as Markdown after the closing `---`. Field names use lowercase words separated by hyphens, except `when_to_use`. A [command file](#choose-where-skills-load) in `.claude/commands/` accepts the same fields except `name` and `paths`. This example sets four fields:

```yaml theme={null}
---
name: my-skill
description: What this skill does
disable-model-invocation: true
allowed-tools: Read Grep
---

Your skill instructions here...
```

All fields are optional. Only `description` is recommended, so Claude knows when to use the skill. Spell each field name exactly as the table does, hyphens included: Claude Code ignores a field it doesn't recognize and reports no error. Boolean fields accept `yes`, `no`, `on`, `off`, `1` and `0` in any letter case, in addition to `true` and `false`.

Put the opening `---` on the file's first line: Claude Code reads the frontmatter only then, and otherwise treats the whole file, `---` markers included, as skill content. If the YAML between the markers doesn't parse, the skill still loads with no fields set; see [Skill not triggering](#skill-not-triggering) to find and fix the error.

| Field | Required | Description |
| :- | :- | :- |
| `name` | No | Command name shown in the `/` menu. Defaults to the directory name. See [How a skill gets its command name](#how-a-skill-gets-its-command-name) for how the field interacts with the name you type to invoke the skill. |
| `description` | Recommended | What the skill does and when to use it. Claude uses this to decide when to apply the skill. If omitted, uses the first non-empty line of the markdown content. Put the key use case first: the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill listing to reduce context usage. Angle brackets in the text [show as `&lt;` and `&gt;`](#angle-brackets-in-a-skill-description-show-as-lt-and-gt). |
| `when_to_use` | No | Additional context for when Claude should invoke the skill, such as trigger phrases or example requests. Appended to `description` in the skill listing and counts toward the 1,536-character cap. |
| `argument-hint` | No | Hint shown during autocomplete to indicate expected arguments. Example: `[issue-number]` or `[filename] [format]`. |
| `arguments` | No | Named positional arguments for [`$name` substitution](#available-string-substitutions) in the skill content. Accepts a space-separated string or a YAML list. Names map to argument positions in order. |
| `disable-model-invocation` | No | Set to `true` to prevent Claude from automatically loading this skill. Use for workflows you want to trigger manually with `/name`. Also prevents the skill from being [preloaded into subagents](https://code.claude.com/docs/en/sub-agents.md#preload-skills-into-subagents) and from running when a [session-scoped scheduled task](https://code.claude.com/docs/en/scheduled-tasks.md) fires with the skill as its prompt. Default: `false`. |
| `user-invocable` | No | Set to `false` when only Claude should invoke the skill: Claude Code hides it from the `/` menu and doesn't run it when you type `/name`. Use for background knowledge users shouldn't invoke directly. Default: `true`. |
| `allowed-tools` | No | Tools Claude can use without asking permission during the turn that invokes this skill. The grant clears when you send your next message. Accepts a space- or comma-separated string, or a YAML list. See [Pre-approve tools for a skill](#pre-approve-tools-for-a-skill). |
| `disallowed-tools` | No | Tools removed from Claude's available pool while this skill is active. Use for autonomous skills that should never call certain tools, such as `AskUserQuestion` for a background loop. Accepts a space- or comma-separated string, or a YAML list. The restriction clears when you send your next message. Like deny rules, the field can't remove [`EndConversation`](https://code.claude.com/docs/en/tools-reference#endconversation-tool-behavior) while any other tool remains. |
| `model` | No | Model to use when this skill is active. The override applies for the rest of the current turn and isn't saved to settings. The session model resumes when you send your next prompt. Accepts the same values as [`/model`](https://code.claude.com/docs/en/model-config), or `inherit` to keep the active model. A value excluded by your organization's [`availableModels`](https://code.claude.com/docs/en/model-config#restrict-model-selection) allowlist isn't used, and the session keeps its current model. In [auto mode](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode), and in [plan mode while the classifier reviews commands](https://code.claude.com/docs/en/permission-modes.md#analyze-before-you-edit-with-plan-mode), a model that auto mode doesn't support also isn't used, and the session keeps its current model. With `context: fork`, the value sets the [forked subagent's model](#run-skills-in-a-subagent) instead, and an excluded value follows the [same rules as a subagent model override](https://code.claude.com/docs/en/model-config.md#restrict-model-selection). |
| `effort` | No | [Effort level](https://code.claude.com/docs/en/model-config.md#adjust-effort-level) for the rest of the current turn. Overrides the session effort level, but not the [`CLAUDE_CODE_EFFORT_LEVEL`](https://code.claude.com/docs/en/env-vars#variables) environment variable. With `context: fork`, the value sets the forked subagent's effort level instead. When you omit it, the level comes from the [effort resolution order](https://code.claude.com/docs/en/model-config.md#adjust-effort-level). For a fork on another model, see [Effort level of subagents and teammates](https://code.claude.com/docs/en/model-config.md#effort-level-of-subagents-and-teammates). Options: `low`, `medium`, `high`, `xhigh`, `max`; available levels depend on the model. |
| `context` | No | Set to `fork` to run in a forked subagent context. See [Run skills in a subagent](#run-skills-in-a-subagent). |
| `agent` | No | Which subagent type to use when `context: fork` is set. |
| `background` | No | Only applies with `context: fork`. Set to `false` to wait for the forked subagent's result in the turn that invoked the skill, instead of [running it in the background](#run-skills-in-a-subagent). Default: `true`. |
| `hooks` | No | Hooks that Claude Code registers when the skill is invoked and keeps running for the rest of the session. See [Hooks in skills and agents](https://code.claude.com/docs/en/hooks.md#hooks-in-skills-and-agents) for the configuration format, the `once` option, and the [limits on skill hooks](https://code.claude.com/docs/en/hooks.md#limits-on-skill-hooks). |
| `paths` | No | Glob patterns that limit when this skill is activated. Accepts a comma-separated string or a YAML list. When set, Claude loads the skill automatically only when working with files matching the patterns. Patterns are relative to Claude's current working directory, and files outside that directory don't match. Uses the same glob format as [path-specific rules](https://code.claude.com/docs/en/memory.md#path-specific-rules). |
| `shell` | No | Shell to use for `` !`command` `` and ` ```! ` blocks in this skill. Accepts `bash` (default) or `powershell`. Setting `powershell` runs inline shell commands via PowerShell when the [PowerShell tool](https://code.claude.com/docs/en/tools-reference.md#powershell-tool) is enabled: it's on by default on Windows without Git Bash, on by default with Git Bash for claude.ai and Console accounts, and needs `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` in Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry sessions and on macOS, Linux, and WSL. Set it to `0` to turn the tool off. |
| `metadata` | No | Free-form YAML map for your own key-value data, such as entitlement or catalog fields, read by your own tooling from `SKILL.md`. Claude Code doesn't act on its contents, and drops a value that isn't a map. Don't reuse frontmatter field names such as `paths` as keys. |
| `license` | No | License covering the skill. Part of the [Agent Skills](https://agentskills.io) spec; see [Using skill frontmatter outside Claude Code](#using-skill-frontmatter-outside-claude-code). Claude Code accepts the field but doesn't act on it. |
| `compatibility` | No | Environment requirements for the skill, such as intended products or system prerequisites, as defined by the [Agent Skills](https://agentskills.io) spec; see [Using skill frontmatter outside Claude Code](#using-skill-frontmatter-outside-claude-code). Accepts a string of up to 500 characters. Claude Code accepts the field but doesn't act on it. |

#### Using skill frontmatter outside Claude Code

Claude Code accepts every field in the table above. Outside Claude Code, only the fields in the [Agent Skills](https://agentskills.io) spec are usable:

| Distribution path | Frontmatter fields you can use |
| :- | :- |
| Claude Code skills at [any level](#choose-where-skills-load), including [plugin](https://code.claude.com/docs/en/plugins/overview.md) skills | Every field in the table above |
| claude.ai skill uploads, the Skills API, and packaging with `package_skill.py` from [anthropics/skills](https://github.com/anthropics/skills) | `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` |

Enabling a personal skill for a claude.ai account, for example to use it in [Cowork and cloud sessions](https://code.claude.com/docs/en/skills#skills-in-cowork-and-cloud-sessions) and scheduled tasks, uploads it to claude.ai. The same rules apply to that upload.

If the frontmatter includes any field the spec doesn't allow, packaging or upload fails with a hard error instead of ignoring the field:

```
Unexpected key(s) in SKILL.md frontmatter: argument-hint. Allowed properties are: allowed-tools, compatibility, description, license, metadata, name
```

To avoid the unexpected-key error above, restrict the frontmatter to the spec's six fields. The [Agent Skills spec](https://agentskills.io) and the [Skills API requirements](https://docs.claude.com/en/api/skills-guide) define everything else those paths validate. Claude Code-only body features, such as [dynamic context injection](#inject-dynamic-context), don't function in claude.ai chat or through the API. Claude Code accepts all six fields, so frontmatter that follows the spec loads in Claude Code without changes.

#### How a skill gets its command name

The command that invokes a skill comes from where the skill file lives and, for skill directories and plugin skills, from the frontmatter `name` field. In a personal or project skill directory, `name` sets the command that the `/` menu shows and that the user types, unless another command already uses that name. The directory name also invokes the skill. In a plugin skill, `name` sets the last segment of the command and the plugin prefix stays in place.

The table below shows where the command name comes from for each layout:

| Skill location | Command name source | Example |
| :- | :- | :- |
| Plugin `skills/` subdirectory | Frontmatter `name` or the directory name, namespaced by plugin | `my-plugin/skills/review/SKILL.md` → `/my-plugin:review`, or `/my-plugin:fancy` with `name: fancy` |
| Plugin root `SKILL.md` | Frontmatter `name`, with the plugin directory name as a fallback | `my-plugin/SKILL.md` with `name: review` → `/my-plugin:review`. See [a single skill at the plugin root](https://code.claude.com/docs/en/plugins/components.md#skills) |

In a plugin skill, the frontmatter `name` replaces the directory name in the last segment of the command, so `my-plugin/skills/review/SKILL.md` with `name: fancy` becomes `/my-plugin:fancy`. The bare `/fancy` also invokes the skill unless another command already uses that name. If the `name` already starts with the plugin's own prefix, Claude Code v2.1.246 or later doesn't add the prefix again. For example, `name: my-plugin:fancy` still becomes `/my-plugin:fancy`. From v2.1.216 through v2.1.245, Claude Code doubled the prefix when the `name` already carried it.

In [non-interactive sessions](https://code.claude.com/docs/en/headless.md), the names `help` and `feedback` aren't reserved for their terminal-only built-in commands, so a plugin skill with one of those names keeps its bare command there. Every other terminal-only built-in's name, such as `/login`, stays reserved even though the command can't run in those sessions.

For a plugin-root `SKILL.md`, there is no skill directory to take the name from, so `name` supplies the whole final segment. Without a `name` field, Claude Code falls back to the plugin's directory name.

#### Characters a skill name can't hold

When a skill or custom command is missing from the `/` menu, or the menu doesn't show a skill's frontmatter `name`, check the name. Claude Code refuses a command name or a frontmatter `name` that contains characters such as these:

* A zero-width space or a control character
* A private-use or unassigned character, such as a glyph from an icon font
* A character that changes the direction of the text around it
* A blank other than one plain space between words, such as a no-break space, two spaces in a row, or a space at the start or end
* `<` or `>`

A custom command or skill doesn't load when Claude Code refuses its directory or file name. Rename that folder or file to remove the characters. A skill still loads when these characters are only in a plugin skill folder's name or in its frontmatter `name`:

* **Folder in a plugin's `skills/` directory or its manifest's [`skills` paths](https://code.claude.com/docs/en/plugins/components#skills)**: the folder needs no rename. These characters become hyphens in the skill's command name, so type the command with the hyphens.
* **Frontmatter `name`**: the `/` menu doesn't show the `name` value and typing it doesn't invoke the skill. Edit the `name:` line to remove the characters.

To find out which name Claude Code refused, start it with [`claude --debug`](https://code.claude.com/docs/en/cli-reference#cli-flags) from the shell and search the [debug log](https://code.claude.com/docs/en/debug-your-config.md) for `[names]`. In an interactive session, a [startup notice](https://code.claude.com/docs/en/errors.md#skill-or-command-name-refused) also reports that names were refused. After a rename or a `name:` edit, restart the session, unless the file is in a directory Claude Code [watches for changes](https://code.claude.com/docs/en/skills#live-change-detection).

#### Available string substitutions

Claude Code substitutes these placeholders with dynamic values in the skill content:

| Variable | Description |
| :- | :- |
| `$ARGUMENTS` | All arguments passed when invoking the skill. When no placeholder receives an argument, Claude Code appends them as `ARGUMENTS: <value>`. See [Pass arguments to skills](#pass-arguments-to-skills). |
| `$ARGUMENTS[N]` | Access a specific argument by 0-based index, such as `$ARGUMENTS[0]` for the first argument. |
| `$N` | Shorthand for `$ARGUMENTS[N]`, such as `$0` for the first argument or `$1` for the second. |
| `$name` | Named argument declared in the [`arguments`](#frontmatter-reference) frontmatter list. Names map to positions in order, so with `arguments: [issue, branch]` the placeholder `$issue` expands to the first argument and `$branch` to the second. |
| `${CLAUDE_SESSION_ID}` | The current session ID. Useful for logging, creating session-specific files, or correlating skill output with sessions. |
| `${CLAUDE_EFFORT}` | The current effort level: `low`, `medium`, `high`, `xhigh`, or `max`. Use this to adapt skill instructions to the active effort setting. |
| `${CLAUDE_SKILL_DIR}` | The directory containing the skill's `SKILL.md` file. For plugin skills, this is the skill's subdirectory within the plugin, not the plugin root. Use this in bash injection commands to reference scripts or files bundled with the skill, regardless of the current working directory. |
| `${CLAUDE_PROJECT_DIR}` | The project root directory. This is the same path [hooks](https://code.claude.com/docs/en/hooks.md#reference-scripts-by-path) and MCP servers receive as `CLAUDE_PROJECT_DIR`. Use this to reference project-local scripts or files, such as `${CLAUDE_PROJECT_DIR}/.claude/hooks/helper.sh`, independent of where the skill is installed. |
| `${CLAUDE_PLUGIN_ROOT}` | The plugin's installation directory. Substituted only in plugin skills. Use this to reference scripts or files bundled anywhere in the plugin, including resources shared between the plugin's skills. See [plugin environment variables](https://code.claude.com/docs/en/plugins/manifest-reference.md#environment-variables). |
| `${CLAUDE_PLUGIN_DATA}` | The plugin's [persistent data directory](https://code.claude.com/docs/en/plugins/components.md#path-variables-and-persistent-data), which survives plugin updates. Substituted only in plugin skills. Use this to reference installed dependencies, generated files, or caches that must outlive an update. |

Claude Code substitutes `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PROJECT_DIR}` in two places: the skill's markdown content, and Bash rules in the [`allowed-tools`](#frontmatter-reference) frontmatter. In a plugin skill, Claude Code substitutes `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` in the same two places. To let a skill run a bundled script without a permission prompt, use the same variable in both places, as this skill does:

```yaml theme={null}
---
name: render-chart
description: Render a chart from a CSV file
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)
---

Run `${CLAUDE_SKILL_DIR}/scripts/render.sh <csv-file>` to render the chart.
```

If this skill is installed at `~/.claude/skills/render-chart/`, both occurrences of `${CLAUDE_SKILL_DIR}` expand to that directory. The `allowed-tools` rule then matches the exact command the skill body tells Claude to run, so the script runs without prompting.

Indexed arguments use shell-style quoting, so wrap multi-word values in quotes to pass them as a single argument. For example, `/my-skill "hello world" second` makes `$0` expand to `hello world` and `$1` to `second`. The `$ARGUMENTS` placeholder always expands to the full argument string as typed.

An indexed placeholder with no corresponding argument, such as `$2` when only one argument was passed, stays in the content unchanged. A named placeholder from the [`arguments`](#frontmatter-reference) frontmatter with no matching argument expands to an empty string.

When an argument value itself contains text such as `$1` or `$ARGUMENTS`, Claude Code inserts it as literal text and doesn't expand it. For example, when a skill's body contains `Summarize $0` and the user runs `/summarize "$ARGUMENTS from yesterday"`, Claude receives `Summarize $ARGUMENTS from yesterday`. Claude Code still replaces `${CLAUDE_*}` variables such as `${CLAUDE_SKILL_DIR}` after it inserts the arguments.

To include a literal `$` before a digit, `ARGUMENTS`, or a declared argument name, such as `$1.00` in prose, escape it with a backslash: `\$1.00`. A backslash before any other `$` is left unchanged. Only a single backslash directly before the token escapes it. A doubled backslash such as `\\$1` leaves both backslashes in place, and `$1` still expands to the argument value. The backslash escape covers only these argument placeholders. A backslash doesn't prevent substitution of a `${CLAUDE_*}` variable where the variable applies.

**Example using substitutions:**

```yaml theme={null}
---
name: session-logger
description: Log activity for this session
---

Log the following to logs/${CLAUDE_SESSION_ID}.log:

$ARGUMENTS
```

### Add supporting files

A skill can include multiple files in its directory. This keeps `SKILL.md` focused on the essentials while Claude reads detailed reference material only when needed, so large reference docs, API specifications or example collections don't load into context every time the skill runs.

```text theme={null}
my-skill/
├── SKILL.md (required - overview and navigation)
├── reference.md (detailed API docs - loaded when needed)
├── examples.md (usage examples - loaded when needed)
└── scripts/
    └── helper.py (utility script - executed, not loaded)
```

Reference supporting files from `SKILL.md` so Claude knows what each file contains and when to load it:

```markdown theme={null}
## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
```

> **Tip:** Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files.

### Control who invokes a skill

By default, both the user and Claude can invoke any skill: the user types `/skill-name` to invoke it directly, and Claude loads it automatically when it is relevant to the conversation. Two frontmatter fields restrict this:

* **`disable-model-invocation: true`**: Claude can't invoke the skill on its own. Use it for workflows that have side effects or whose timing the user wants to control, such as `/commit`, `/deploy` or `/send-slack-message`. Claude must not decide to deploy because the code looks ready.

* **`user-invocable: false`**: only Claude can invoke the skill. Use it for background knowledge that isn't actionable as a command. For example, a `legacy-system-context` skill explains how an old system works: Claude should know this when relevant, but `/legacy-system-context` isn't a meaningful action for users to take.

This example creates a deploy skill. With `disable-model-invocation: true` set, Claude can't run the skill automatically:

```yaml theme={null}
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
---

Deploy $ARGUMENTS to production:

1. Run the test suite
2. Build the application
3. Push to the deployment target
4. Verify the deployment succeeded
```

If Claude tries anyway, Claude Code blocks the call and instructs Claude not to reproduce the deploy steps another way, so Claude then suggests that the user run `/deploy` themselves.

How the two fields affect invocation and context loading:

| Frontmatter | You can invoke | Claude can invoke | When loaded into context |
| :- | :- | :- | :- |
| (default) | Yes | Yes | Description always in context, full skill loads when invoked |
| `disable-model-invocation: true` | Yes | Not on its own | Description not in context, full skill loads when invoked |
| `user-invocable: false` | No | Yes | Description always in context, full skill loads when invoked |

> **Note:** In a regular session, skill descriptions are loaded into context so Claude knows what's available, but full skill content only loads when invoked. [Subagents with preloaded skills](https://code.claude.com/docs/en/sub-agents.md#preload-skills-into-subagents) work differently: the full skill content is injected at startup.

#### Where you write the skill's name

To run a skill directly, the user puts its name at the start of the message. After plain text, the name gives Claude permission to run the skill but doesn't run it:

| Where | Example | What happens |
| :- | :- | :- |
| At the start of your message | `/deploy staging` | Claude Code runs the skill directly |
| After plain text, as a separate word with no punctuation attached | `go ahead and /deploy to staging` | Nothing runs directly. The name counts as your permission for that message: Claude can run the skill while it responds, and judges from your wording whether you asked it to |

To write about the skill without permitting a run, leave off the slash.

### Skill content lifecycle

When the user or Claude invokes a skill, the rendered `SKILL.md` content enters the conversation as a single message and stays there across later turns. This persistence applies to the skill's instructions, not its permissions: an [`allowed-tools`](#pre-approve-tools-for-a-skill) grant clears when the user sends the next message. Claude Code does not re-read the skill file on later turns, so write guidance that must apply throughout a task as standing instructions rather than one-time steps.

When Claude re-invokes a skill whose rendered content is identical to the copy already in context, Claude Code adds a short note that the skill is already loaded rather than a second copy of the content. When the rendered content differs, because the arguments changed or a [dynamic context](#inject-dynamic-context) command produced new output, Claude Code appends the full content again.

[Auto-compaction](https://code.claude.com/docs/en/how-claude-code-works.md#when-context-fills-up) carries invoked skills forward within a token budget. When the conversation is summarized to free context, Claude Code re-attaches the most recent invocation of each skill after the summary, keeping the first 5,000 tokens of each. Re-attached skills share a combined budget of 25,000 tokens. Claude Code fills this budget starting from the most recently invoked skill, so older skills can be dropped entirely after compaction when many skills were invoked in one session.

If Claude stops following a skill partway through a session, see [Claude stops following a skill](#claude-stops-following-a-skill).

### Pre-approve tools for a skill

The `allowed-tools` field grants permission for the listed tools during the turn that invokes the skill, so Claude can use them without prompting the user for approval. The grant clears when the user sends the next message, even though the skill content [stays in context](#skill-content-lifecycle); invoking the skill again re-applies it for that turn. The field does not restrict which tools are available: every tool remains callable, and the user's [permission settings](https://code.claude.com/docs/en/permissions.md) still govern tools that are not listed. To pre-approve tools for the whole session rather than a single turn, add allow rules to those permission settings instead.

This skill lets Claude run git commands without per-use approval whenever the skill is invoked:

```yaml theme={null}
---
name: commit
description: Stage and commit the current changes
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---
```

To remove tools from Claude's available pool while a skill is active, list them in `disallowed-tools` in the skill's frontmatter. The restriction clears when the user sends the next message. Like deny rules, the field can't remove [`EndConversation`](https://code.claude.com/docs/en/tools-reference#endconversation-tool-behavior) while any other tool remains. To block tools across all skills and prompts, add deny rules in the [permission settings](https://code.claude.com/docs/en/permissions.md).

#### When managed settings lock hooks to plugins

When an organization's managed settings list `hooks` in `strictPluginOnlyCustomization`, a personal or project skill whose frontmatter declares `hooks` loses its `allowed-tools` pre-approval, apart from the [skills that keep it](https://code.claude.com/docs/en/settings-reference.md#strictpluginonlycustomization-hooks).

* **Check**: type `/status` in a Claude Code session. If `/status` shows [`Enterprise managed settings`](https://code.claude.com/docs/en/settings#check-what-your-organization-enforces), ask the administrator whether `strictPluginOnlyCustomization` lists `hooks`.
* **Fix**: remove `hooks` from the skill's frontmatter, because its hooks don't run under that setting. To keep them, [move the skill into a plugin](https://code.claude.com/docs/en/hooks.md#limits-on-skill-hooks) installed from a marketplace.

#### When only managed permission rules apply

When an organization sets `allowManagedPermissionRulesOnly` in managed settings, Claude Code ignores `allowed-tools` in project and personal skills and in the [other sources the setting's entry lists](https://code.claude.com/docs/en/settings-reference.md#allowmanagedpermissionrulesonly). This requires Claude Code v2.1.282 or later.

The tools an affected skill lists go through the organization's managed rules and the normal permission prompt instead. Run `/status` to list each skill whose `allowed-tools` Claude Code has ignored so far in the session. An injected command in the skill that no managed rule allows follows [Permission checks on injected commands](#permission-checks-on-injected-commands).

### Pass arguments to skills

Both the user and Claude can pass arguments when invoking a skill. The skill content receives them through the `$ARGUMENTS` placeholder.

This skill fixes a GitHub issue by number. Claude Code replaces the `$ARGUMENTS` placeholder with whatever follows the skill name:

```yaml theme={null}
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

1. Read the issue description
2. Understand the requirements
3. Implement the fix
4. Write tests
5. Create a commit
```

Running `/fix-issue 123` sends Claude "Fix GitHub issue 123 following our coding standards..."

When a skill is invoked with arguments but no placeholder in the skill's content receives one, Claude Code appends `ARGUMENTS: <your input>` to the end of the skill content so Claude still sees what the user typed. A placeholder is `$ARGUMENTS`, an indexed form such as `$1`, or a named argument. An indexed placeholder with no argument at its position stays as literal text and doesn't count as receiving one. A named placeholder counts even when its position has no argument, because it expands to an empty string.

To access individual arguments by position, use `$ARGUMENTS[N]` or the shorter `$N`:

```yaml theme={null}
---
name: migrate-component
description: Migrate a component from one language to another
---

Migrate the $ARGUMENTS[0] component from $ARGUMENTS[1] to $ARGUMENTS[2].
Preserve all existing behavior and tests.
```

Running `/migrate-component SearchBar JavaScript TypeScript` replaces `$ARGUMENTS[0]` with `SearchBar`, `$ARGUMENTS[1]` with `JavaScript`, and `$ARGUMENTS[2]` with `TypeScript`. The same skill using the `$N` shorthand:

```yaml theme={null}
---
name: migrate-component
description: Migrate a component from one language to another
---

Migrate the $0 component from $1 to $2.
Preserve all existing behavior and tests.
```

#### Stack several skills in one message

At the Claude Code prompt in the terminal, the user can stack several skills at the start of one message. Through the Agent SDK or `claude -p`, Claude Code loads only the first skill, with the rest of the line as its arguments. At the terminal prompt, typing `/write-tests /fix-issue 123` loads both skills and passes the trailing text `123` as `$ARGUMENTS` to each of them.

Claude Code expands the first skill plus up to five more stacked after it. Expansion stops at the first token that isn't an inline user-invocable skill. When the stack contains a skill that runs as a [forked subagent](#run-skills-in-a-subagent), such as [`/code-review`](https://code.claude.com/docs/en/code-review-local), or one whose arguments may start with another command, such as `/loop`, expansion ends there. That token and everything after it become the argument text for every expanded skill.

## Advanced patterns

### Inject dynamic context

The `` !`<command>` `` syntax runs shell commands before the skill content is sent to Claude. The command output replaces the placeholder, so Claude receives actual data, not the command itself. Claude Code doesn't run these commands on the user's machine when the skill is [synced from the user's claude.ai account](https://code.claude.com/docs/en/skills#how-claude-code-handles-the-body-of-a-synced-skill). This restriction requires Claude Code v2.1.228 or later.

This skill summarizes a pull request by fetching live PR data with the GitHub CLI. The `` !`gh pr diff` `` and other commands run first, and their output is inserted into the prompt:

```yaml theme={null}
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

Substitution runs once over the original file. Command output is inserted as plain text and is not re-scanned for further `` !`<command>` `` placeholders, so a command cannot emit a placeholder for a later pass to expand.

The inline form is only recognized when `!` appears at the start of a line or immediately after whitespace. If `!` follows another character, as in `` KEY=!`cmd` ``, the placeholder is left as literal text and the command does not run.

For multi-line commands, use a fenced code block opened with ` ```! ` instead of the inline form:

````markdown theme={null}
## Environment
```!
node --version
git status --short
```
````

To disable this behavior for skills and custom commands from user, project, plugin or [additional-directory](https://code.claude.com/docs/en/skills#skills-from-additional-directories) sources, set `"disableSkillShellExecution": true` in [settings](https://code.claude.com/docs/en/settings.md). Each command is then replaced with `[shell command execution disabled by policy]` instead of being run. Bundled and managed skills are not affected. This setting is most useful in [managed settings](https://code.claude.com/docs/en/managed-settings.md), where users cannot override it.

> **Tip:** To request deeper reasoning when a skill runs, include `ultrathink` anywhere in the skill content. See [Use ultrathink for one-off deep reasoning](https://code.claude.com/docs/en/model-config.md#use-ultrathink-for-one-off-deep-reasoning).

#### How injected commands run

Claude Code picks the tool that runs a skill's injected commands from the `shell` key in the skill's frontmatter and the environment. Every combination runs the commands through the Bash tool or the PowerShell tool, except one that fails the invocation outright:

* `shell: powershell`, with the [PowerShell tool](https://code.claude.com/docs/en/tools-reference.md#powershell-tool) enabled: the commands run through the PowerShell tool.
* `shell: bash` when bash isn't available: the invocation fails before any command runs. This happens on Windows without Git Bash. Claude Code shows ``Skill <name> requires bash (`shell: bash` in frontmatter) but Git Bash was not found``.
* Any other combination: the commands run through the Bash tool when bash is available. When it isn't, they run through the PowerShell tool.

Either tool runs the commands the same way it runs Claude's own shell commands. They share the working directory, timeout, and output handling:

* **Working directory**: Claude Code runs each command in the session shell's current working directory. That directory moves when Claude runs `cd`. Use [`${CLAUDE_SKILL_DIR}` or `${CLAUDE_PROJECT_DIR}`](#available-string-substitutions) in paths that must resolve the same way every time.
* **stderr**: with the default `bash` shell, Claude Code merges stderr into stdout. Anything the command writes to stderr appears in the injected text.
* **Timeout**: each command runs under the Bash tool's default 2-minute [timeout](https://code.claude.com/docs/en/tools-reference.md#timeout-and-output-limits). When the Bash tool [moves a timed-out command to the background](https://code.claude.com/docs/en/tools-reference.md#foreground-commands-that-move-to-the-background), the skill still renders. The injected text reports the move and names the background task and the file collecting the command's output. When the command is one the Bash tool never auto-backgrounds, Claude Code kills it at the timeout. That failure [aborts the invocation](#when-an-injected-command-fails).
* **Output size**: output past the Bash tool's inline ceiling arrives as a file path plus a short preview, not truncated text. [Output limits](https://code.claude.com/docs/en/tools-reference.md#output-limits) covers the ceiling and how to adjust each boundary.

The PowerShell tool applies the same timeout, backgrounding, and output-ceiling behavior to the commands it runs. See the [PowerShell tool](https://code.claude.com/docs/en/tools-reference.md#powershell-tool) section for its specifics.

#### When an injected command fails

A failed command aborts the entire skill invocation, not just its own placeholder. Claude never sees the skill content for that invocation. The abort shows `Shell command failed for pattern "..."`. The error message includes the command's output.

With the default `bash` shell, any non-zero exit code counts as a failure. One carveout applies: Claude Code treats exit code 1 from [search and comparison commands](https://code.claude.com/docs/en/tools-reference.md#output-limits) as a normal result and injects their output. Exit codes of 2 or higher fail even for those commands.

Which commands get the carveout depends on the shell:

* Default `bash` shell: the commands listed under [Output limits](https://code.claude.com/docs/en/tools-reference.md#output-limits)
* `shell: powershell`, when the PowerShell tool is enabled: a [different set](https://code.claude.com/docs/en/tools-reference.md#exit-code-1-from-searches-and-git-diff-in-powershell) that includes `grep` and `git diff` but not `find` or `diff`

With the default `bash` shell, append `|| true` to any other command that is expected to exit non-zero. A check script that exits 1 when it finds problems is one example.

#### When no shell command was run

`No shell command in <name> was run` means one of its shell commands contains a character the tool doesn't accept. To find and remove the character, see the [error reference](https://code.claude.com/docs/en/errors.md#no-shell-command-was-run).

#### Permission checks on injected commands

Injected commands never prompt for permission while the skill renders. Claude Code first checks each one against the user's [permission rules](https://code.claude.com/docs/en/permissions.md). A command a deny rule matches aborts the invocation with `Shell command permission check failed for pattern "..."`.

Outside [auto mode](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode), when a command's permission check returns anything other than allow, Claude Code aborts the invocation with the same error. This includes a rule that would normally ask the user. To keep an unmatched command from aborting here, pre-approve it with [`allowed-tools`](#pre-approve-tools-for-a-skill). If the organization restricts permission rules to managed settings, see [When only managed permission rules apply](#when-only-managed-permission-rules-apply). Deny and ask rules still override `allowed-tools`. See [Manage permissions](https://code.claude.com/docs/en/permissions.md#manage-permissions).

In auto mode, a command that would otherwise need the user's approval doesn't abort the invocation. The skill loads with an instruction telling Claude to run the command first, and Claude's own call then goes through [auto mode's usual checks](https://code.claude.com/docs/en/permission-modes.md#how-the-classifier-evaluates-actions). The invocation still aborts in a [forked skill](#run-skills-in-a-subagent) that sets `agent`, and in a session where Claude doesn't have the [shell tool that runs injected commands](#how-injected-commands-run).

### Run skills in a subagent

To run a skill in isolation, add `context: fork` to its frontmatter. Claude Code starts a new subagent of the type set in the `agent` field and gives it the skill content as its prompt. The subagent doesn't see the conversation history, so the skill's instructions must stand on their own.

> **Note:** Despite the name, a skill with `context: fork` doesn't run in a [fork of the current conversation](https://code.claude.com/docs/en/sub-agents.md#fork-the-current-conversation), which would hand the subagent everything discussed so far. When the task depends on that history, fork the conversation instead of using `context: fork`.

The forked subagent runs in the [background](https://code.claude.com/docs/en/sub-agents.md#run-subagents-in-foreground-or-background): the user keeps working while it runs, and its result arrives in the conversation when it completes. To wait for the result in the turn that invoked the skill instead, set `background: false` in the frontmatter.

Claude Code also waits for the result, even when the skill doesn't set `background: false`, in cases like these:

* In non-interactive mode, with the `-p` flag or the Agent SDK
* When [`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`](https://code.claude.com/docs/en/env-vars) is set to `1`, which also turns off other background task features
* When a forked skill is invoked while an earlier invocation of the same skill is still running
* When a [session-scoped scheduled task](https://code.claude.com/docs/en/scheduled-tasks.md) fires with the skill as its prompt

When an agent in a [dynamic workflow](https://code.claude.com/docs/en/workflows.md) invokes a forked skill, that agent waits for and receives the result, even when the skill doesn't set `background: false`. Before v2.1.295, when the skill ran in the background, that agent didn't wait for it, and the skill's result arrived in the main conversation instead of reaching the agent.

A backgrounded fork also runs with the [narrower tool set that applies to background subagents](https://code.claude.com/docs/en/sub-agents.md#run-subagents-in-foreground-or-background): the skill's subagent is a regular agent type, so the exemption for subagents that fork the conversation doesn't cover it. If the skill's steps depend on a tool outside that set, set `background: false` to keep the full tool set.

A forked skill that runs in the background applies its edits outside the session's [checkpoints](https://code.claude.com/docs/en/checkpointing.md#subagent-edits-not-restored). After one, `/rewind` restores only the files Claude had already edited in the conversation. The skill's edits to other files stay, so use git to revert them.

> **Warning:** `context: fork` only makes sense for skills with explicit instructions. If a skill contains guidelines like "use these API conventions" without a task, the subagent receives the guidelines but no actionable prompt, and returns without meaningful output.

Skills and [subagents](https://code.claude.com/docs/en/sub-agents.md) work together in two directions:

| Approach | System prompt | Task | Also loads |
| :- | :- | :- | :- |
| Skill with `context: fork` | From agent type | SKILL.md content | CLAUDE.md, per the agent's [startup context](https://code.claude.com/docs/en/sub-agents.md#what-loads-at-startup) |
| Subagent with `skills` field | Subagent's markdown body | Claude's delegation message | Preloaded skills + CLAUDE.md, per the subagent's [startup context](https://code.claude.com/docs/en/sub-agents.md#what-loads-at-startup) |

With `context: fork`, write the task in the skill and pick an agent type to execute it. The built-in Explore and Plan agents [start without CLAUDE.md and git status](https://code.claude.com/docs/en/sub-agents.md#what-loads-at-startup) to keep their context small, so put everything the task needs in the SKILL.md. A forked skill using `agent: Explore` starts with that content and the agent's own system prompt, and none of the user's CLAUDE.md files.

For the inverse, a custom subagent that uses skills as reference material, see [Subagents](https://code.claude.com/docs/en/sub-agents.md#preload-skills-into-subagents).

#### Example: Research skill using Explore agent

This skill runs research in a forked Explore agent. The skill content becomes the task, and the agent provides read-only tools optimized for codebase exploration:

```yaml theme={null}
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

When this skill runs:

1. A new isolated context is created
2. The subagent receives the skill content as its prompt (the "Research \$ARGUMENTS thoroughly" instructions)
3. The `agent` field determines the execution environment (model, tools, and permissions)
4. The subagent summarizes its results and returns them to the main conversation when it finishes

The `agent` field specifies which subagent configuration to use: a built-in agent (`Explore`, `Plan`, `general-purpose`) or any custom subagent from `.claude/agents/`. When the field is omitted, Claude Code uses `general-purpose`.

### Restrict Claude's skill access

By default, Claude can invoke any skill that doesn't have `disable-model-invocation: true` set. Skills that define [`allowed-tools`](#pre-approve-tools-for-a-skill) grant Claude access to those tools without per-use approval during the turn that invokes the skill; the grant clears when the user sends the next message. The [permission settings](https://code.claude.com/docs/en/permissions.md) still govern baseline approval behavior for all other tools. A few built-in commands are also available through the Skill tool, including `/init` and `/security-review`. Other built-in commands such as `/compact` are not.

Control which skills Claude can invoke in three ways:

**Disable all skills** by denying the Skill tool in `/permissions`:

```text theme={null}
# Add to deny rules:
Skill
```

**Allow or deny specific skills** using [permission rules](https://code.claude.com/docs/en/permissions.md):

```text theme={null}
# Allow only specific skills
Skill(commit)
Skill(review-pr *)

# Deny specific skills
Skill(deploy *)
```

Permission syntax: `Skill(name)` for exact match, `Skill(name *)` for prefix match with any arguments.

The table shows what a `deny` rule blocks beyond the name written in it, by the kind of name in the rule.

| Your `deny` rule names | Example rule | Claude Code also blocks |
| :- | :- | :- |
| A skill in the [parameter form](https://code.claude.com/docs/en/permissions.md#match-by-input-parameter) | `Skill(skill:deploy)` | The skill whichever of its names Claude calls it by, including its alias and display name |

**Hide individual skills** by adding `disable-model-invocation: true` to their frontmatter. This removes the skill from Claude's context entirely.

> **Note:** With `user-invocable: false`, the user can't invoke the skill, but Claude still can. To keep Claude from invoking it through the Skill tool, set `disable-model-invocation: true`.

### Override skill visibility from settings

`skillOverrides` doesn't affect plugin skills. Manage plugin skills through `/plugin` instead.

## Evaluate and iterate on a skill

A skill that triggers shows that Claude found it, not that it did what was intended. To know a skill works, measure two things separately: whether Claude invokes it on the prompts it should, and whether the output matches the expectation when it does.

Check both with a baseline comparison. Collect a few realistic prompts, run each one in a fresh session with the skill available and again with it turned off, and compare the results. Use a fresh session because leftover context from authoring the skill masks gaps in the written instructions.

How to turn the skill off for the second run depends on its source:

* **Skill that a plugin provides**: `skillOverrides` doesn't apply to plugin skills. Use [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals#the-no-plugin-baseline) instead, which repeats each run with no plugin loaded.

Two tools automate the baseline comparison. For a skill that ships in a [plugin](https://code.claude.com/docs/en/plugins/overview.md), [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals) runs each prompt in an isolated session with and without the plugin, scores it with graders that the author defines or that it writes, and exits non-zero below a threshold, so CI can gate on it. For iterating on a single skill inside a Claude Code conversation, the skill-creator plugin below runs a similar loop with its own `evals/evals.json` format. The two formats aren't interchangeable.

### Run evals with skill-creator

The [`skill-creator` plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator) automates the comparison loop inside Claude Code. In the VS Code extension or the desktop app, install it from the official marketplace by following [Install a plugin](https://code.claude.com/docs/en/plugins/install.md#install-a-plugin). In a terminal, start Claude Code by running `claude`, then enter this at its prompt:

```text theme={null}
/plugin install skill-creator@claude-plugins-official
```

If the install fails, act on the message Claude Code reports:

* `Marketplace "claude-plugins-official" not found`: add the marketplace with `/plugin marketplace add anthropics/claude-plugins-official`, then retry the install.
* `Plugin "<name>" not found in marketplace "claude-plugins-official"`: the local copy of the marketplace catalog may be out of date. Refresh it with `/plugin marketplace update claude-plugins-official`, then retry the install. If the retry prints the same message, see [Plugin not found in marketplace](https://code.claude.com/docs/en/plugins/troubleshooting.md#plugin-not-found-in-marketplace).

If the install summary reports `Run /reload-plugins to apply.`, Claude Code then runs that reload itself. If the reload warns that the next message would re-read the conversation, run `/reload-plugins --force` to make the plugin's skills available in the current session. Then ask Claude to evaluate an existing skill, for example `evaluate my summarize-changes skill with skill-creator`. The plugin guides the writing of test cases and runs the loop:

* **Test cases**: stores prompts, input files, and expected behavior in `evals/evals.json` inside the skill directory
* **Isolated runs**: spawns a [subagent](https://code.claude.com/docs/en/sub-agents.md) per test case so each run starts with a clean context, and records token count and duration
* **Grading**: checks each assertion against the output and writes pass or fail with evidence to `grading.json`
* **Benchmark**: aggregates pass rate, time, and tokens for with-skill versus without-skill into `benchmark.json`, to compare the pass-rate improvement against the token and time overhead
* **Version comparison**: runs a blind A/B between two versions of the skill, to confirm an edit is an improvement before committing it
* **Description tuning**: generates should-trigger and should-not-trigger prompts, measures the hit rate, and proposes description edits when the skill activates on the wrong requests
* **Review viewer**: opens an HTML report for inspecting each output and recording qualitative feedback that the next iteration reads

For the eval file format and the full iteration workflow, see [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills) on agentskills.io. For background on the benchmark and comparison modes, see the [skill-creator announcement](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills).

## Share skills

Distribute skills at the scope that fits the audience. For a plugin:

* **Plugins**: create a `skills/` directory in the [plugin](https://code.claude.com/docs/en/plugins/overview.md)

### Generate visual output

A skill can bundle and run scripts in any language, giving Claude capabilities beyond what a single prompt allows. One pattern is generating visual output: interactive HTML files that open in the browser for exploring data, debugging or creating reports.

This example creates a codebase explorer: an interactive tree view in which the user expands and collapses directories, sees file sizes at a glance, and identifies file types by color.

Create the skill directory:

```bash theme={null}
mkdir -p ~/.claude/skills/codebase-visualizer/scripts
```

Save this to `~/.claude/skills/codebase-visualizer/SKILL.md`. The description tells Claude when to activate this skill, and the instructions tell Claude to run the bundled script. The script path uses [`${CLAUDE_SKILL_DIR}`](#available-string-substitutions) so it resolves correctly whether the skill is installed at the personal, project, or plugin level:

````yaml theme={null}
---
name: codebase-visualizer
description: Generate an interactive collapsible tree visualization of your codebase. Use when exploring a new repo, understanding project structure, or identifying large files.
allowed-tools: Bash(python3 *)
---

# Codebase Visualizer

Generate an interactive HTML tree view that shows your project's file structure with collapsible directories.

## Usage

Run the visualization script from your project root:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/visualize.py .
```

This creates `codebase-map.html` in the current directory and opens it in your default browser.

## What the visualization shows

- **Collapsible directories**: Click folders to expand/collapse
- **File sizes**: Displayed next to each file
- **Colors**: Different colors for different file types
- **Directory totals**: Shows aggregate size of each folder
````

Save this to `~/.claude/skills/codebase-visualizer/scripts/visualize.py`. This script scans a directory tree and generates a self-contained HTML file with:

* A **summary sidebar** showing file count, directory count, total size, and number of file types
* A **bar chart** breaking down the codebase by file type (top 8 by size)
* A **collapsible tree** whose directories expand and collapse, with color-coded file type indicators

The script requires Python 3 but uses only built-in libraries, so there are no packages to install:

```python expandable theme={null}
#!/usr/bin/env python3
"""Generate an interactive collapsible tree visualization of a codebase."""

import json
import sys
import webbrowser
from html import escape
from pathlib import Path
from collections import Counter

IGNORE = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}

def scan(path: Path, stats: dict) -> dict:
    result = {"name": path.name, "children": [], "size": 0}
    try:
        for item in sorted(path.iterdir()):
            if item.name in IGNORE or item.name.startswith('.'):
                continue
            if item.is_file():
                size = item.stat().st_size
                ext = item.suffix.lower() or '(no ext)'
                result["children"].append({"name": item.name, "size": size, "ext": ext})
                result["size"] += size
                stats["files"] += 1
                stats["extensions"][ext] += 1
                stats["ext_sizes"][ext] += size
            elif item.is_dir():
                stats["dirs"] += 1
                child = scan(item, stats)
                if child["children"]:
                    result["children"].append(child)
                    result["size"] += child["size"]
    except PermissionError:
        pass
    return result

def generate_html(data: dict, stats: dict, output: Path) -> None:
    ext_sizes = stats["ext_sizes"]
    total_size = sum(ext_sizes.values()) or 1
    sorted_exts = sorted(ext_sizes.items(), key=lambda x: -x[1])[:8]
    colors = {
        '.js': '#f7df1e', '.ts': '#3178c6', '.py': '#3776ab', '.go': '#00add8',
        '.rs': '#dea584', '.rb': '#cc342d', '.css': '#264de4', '.html': '#e34c26',
        '.json': '#6b7280', '.md': '#083fa1', '.yaml': '#cb171e', '.yml': '#cb171e',
        '.mdx': '#083fa1', '.tsx': '#3178c6', '.jsx': '#61dafb', '.sh': '#4eaa25',
    }
    lang_bars = "".join(
        f'<div class="bar-row"><span class="bar-label">{ext}</span>'
        f'<div class="bar" style="width:{(size/total_size)*100}%;background:{colors.get(ext,"#6b7280")}"></div>'
        f'<span class="bar-pct">{(size/total_size)*100:.1f}%</span></div>'
        for ext, size in sorted_exts
    )
    def fmt(b):
        if b < 1024: return f"{b} B"
        if b < 1048576: return f"{b/1024:.1f} KB"
        return f"{b/1048576:.1f} MB"

    html = f'''<!DOCTYPE html>
<html><head>
  <meta charset="utf-8"><title>Codebase Explorer</title>
  <style>
    body {{ font: 14px/1.5 system-ui, sans-serif; margin: 0; background: #1a1a2e; color: #eee; }}
    .container {{ display: flex; height: 100vh; }}
    .sidebar {{ width: 280px; background: #252542; padding: 20px; border-right: 1px solid #3d3d5c; overflow-y: auto; flex-shrink: 0; }}
    .main {{ flex: 1; padding: 20px; overflow-y: auto; }}
    h1 {{ margin: 0 0 10px 0; font-size: 18px; }}
    h2 {{ margin: 20px 0 10px 0; font-size: 14px; color: #888; text-transform: uppercase; }}
    .stat {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #3d3d5c; }}
    .stat-value {{ font-weight: bold; }}
    .bar-row {{ display: flex; align-items: center; margin: 6px 0; }}
    .bar-label {{ width: 55px; font-size: 12px; color: #aaa; }}
    .bar {{ height: 18px; border-radius: 3px; }}
    .bar-pct {{ margin-left: 8px; font-size: 12px; color: #666; }}
    .tree {{ list-style: none; padding-left: 20px; }}
    details {{ cursor: pointer; }}
    summary {{ padding: 4px 8px; border-radius: 4px; }}
    summary:hover {{ background: #2d2d44; }}
    .folder {{ color: #ffd700; }}
    .file {{ display: flex; align-items: center; padding: 4px 8px; border-radius: 4px; }}
    .file:hover {{ background: #2d2d44; }}
    .size {{ color: #888; margin-left: auto; font-size: 12px; }}
    .dot {{ width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; }}
  </style>
</head><body>
  <div class="container">
    <div class="sidebar">
      <h1>📊 Summary</h1>
      <div class="stat"><span>Files</span><span class="stat-value">{stats["files"]:,}</span></div>
      <div class="stat"><span>Directories</span><span class="stat-value">{stats["dirs"]:,}</span></div>
      <div class="stat"><span>Total size</span><span class="stat-value">{fmt(data["size"])}</span></div>
      <div class="stat"><span>File types</span><span class="stat-value">{len(stats["extensions"])}</span></div>
      <h2>By file type</h2>
      {lang_bars}
    </div>
    <div class="main">
      <h1>📁 {escape(data["name"])}</h1>
      <ul class="tree" id="root"></ul>
    </div>
  </div>
  <script>
    const data = {json.dumps(data)};
    const colors = {json.dumps(colors)};
    function fmt(b) {{ if (b < 1024) return b + ' B'; if (b < 1048576) return (b/1024).toFixed(1) + ' KB'; return (b/1048576).toFixed(1) + ' MB'; }}
    function esc(s) {{ return s.replace(/[&<>"']/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[c])); }}
    function render(node, parent) {{
      if (node.children) {{
        const det = document.createElement('details');
        det.open = parent === document.getElementById('root');
        det.innerHTML = `<summary><span class="folder">📁 ${{esc(node.name)}}</span><span class="size">${{fmt(node.size)}}</span></summary>`;
        const ul = document.createElement('ul'); ul.className = 'tree';
        node.children.sort((a,b) => (b.children?1:0)-(a.children?1:0) || a.name.localeCompare(b.name));
        node.children.forEach(c => render(c, ul));
        det.appendChild(ul);
        const li = document.createElement('li'); li.appendChild(det); parent.appendChild(li);
      }} else {{
        const li = document.createElement('li'); li.className = 'file';
        li.innerHTML = `<span class="dot" style="background:${{colors[node.ext]||'#6b7280'}}"></span>${{esc(node.name)}}<span class="size">${{fmt(node.size)}}</span>`;
        parent.appendChild(li);
      }}
    }}
    data.children.forEach(c => render(c, document.getElementById('root')));
  </script>
</body></html>'''
    output.write_text(html)

if __name__ == '__main__':
    target = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
    stats = {"files": 0, "dirs": 0, "extensions": Counter(), "ext_sizes": Counter()}
    data = scan(target, stats)
    out = Path('codebase-map.html')
    generate_html(data, stats, out)
    print(f'Generated {out.absolute()}')
    webbrowser.open(f'file://{out.absolute()}')
```

To test, open Claude Code in any project and ask "Visualize this codebase." Claude runs the script, which prints the generated file's path, such as `Generated /path/to/codebase-map.html`, and opens it in the browser. In a headless environment where no browser opens, the printed path confirms the script succeeded.

This pattern works for any visual output: dependency graphs, test coverage reports, API documentation, or database schema visualizations. The bundled script does the work while Claude handles orchestration.

## Troubleshooting

### Skill not triggering

When Claude doesn't use a skill when expected:

1. Check that the description includes keywords users would naturally say
2. Verify that the skill appears in `What skills are available?`
3. Rephrase the request to match the description more closely
4. Invoke it directly with `/skill-name` if the skill is user-invocable
5. If `/skill-name` isn't recognized either, check whether Claude Code [refused the skill's name](#characters-a-skill-name-cant-hold)
6. If the skill sets `paths`, check that the files Claude reads, edits or writes are inside Claude's current working directory. The skill doesn't activate for files outside it, such as those in a sibling git worktree, even one added with `/add-dir`. To have the skill activate for those files, start Claude Code in that worktree or [move the session there with `/cd`](https://code.claude.com/docs/en/permissions#move-the-session-to-another-directory).

If the frontmatter YAML is malformed, Claude Code loads the skill body with empty metadata, so `/skill-name` still works but Claude can't match against the `description`. Run with `--debug` to see the parse error.

If the skill ships in a plugin, measure how often it triggers across realistic prompts rather than checking one prompt at a time: write an eval case with a [`tool_used: Skill` grader](https://code.claude.com/docs/en/plugin-evals#create-your-first-eval-suite) and run it with `claude plugin eval` after each description change.

To find `SKILL.md` files whose frontmatter doesn't parse, run [`claude plugin validate`](https://code.claude.com/docs/en/plugins/cli-reference#validate-a-directory) on the skills directory, for example `claude plugin validate .claude/skills` for project skills or `claude plugin validate ~/.claude/skills` for personal skills. Requires Claude Code v2.1.233 or later.

### Skill triggers too often

When Claude uses a skill when it isn't wanted:

1. Make the description more specific
2. Add `disable-model-invocation: true` if only manual invocation is wanted

### Claude stops following a skill

When Claude follows a skill in its first response and stops following it later, start with whichever of these cases matches:

* **Claude skipped a rule that must hold every time**: move the rule into a [hook](https://code.claude.com/docs/en/hooks-guide.md). Claude Code runs a hook every time its event occurs, such as before each file edit, whether or not Claude is following the skill. To keep the rule with the skill, define the hook in the skill's [`hooks` frontmatter](https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents). That hook applies from the time the skill is invoked until the session ends.
* **Claude skipped guidance it should apply with judgment**: word the guidance so it applies to the whole task, for example "Run the tests after every edit" rather than "Run the tests". Claude Code adds the skill's content to the conversation when the skill is invoked and [doesn't re-read the file](#skill-content-lifecycle) on later turns.
* **The conversation was compacted**: invoke the skill again to restore its full content. After [compaction](https://code.claude.com/docs/en/how-claude-code-works.md#when-context-fills-up), Claude Code [can keep only the start of an invoked skill](#skill-content-lifecycle), so put the most important instructions near the top of `SKILL.md`.

### Skill descriptions are cut short

Claude Code loads a listing of skill names and descriptions into context so Claude knows what's available. The listing always contains every skill name, but when there are many skills, Claude Code drops some descriptions to fit the listing's character budget, which removes the keywords Claude needs to match a request. The budget scales at 1% of the model's context window. When the listing overflows, Claude Code drops descriptions starting with the least-invoked skills, so the most-used skills keep their full text.

Run `/doctor` for an estimate of the listing's context cost and its biggest contributors. To find skills worth turning off, run [`/skill-doctor`](https://code.claude.com/docs/en/skills#find-unused-skills). When the listing exceeds its budget, Claude Code also writes a warning to the debug log, visible with [`--debug`](https://code.claude.com/docs/en/cli-reference#cli-flags).

The Skills row in `/context` reports the size of the listing after the budget is applied, so it matches what the model receives. Before v2.1.196, the row counted the full text of every description and could show a value several times larger than the configured budget.

To raise the budget, set the [`skillListingBudgetFraction`](https://code.claude.com/docs/en/settings-reference#skilllistingbudgetfraction) setting (for example, `0.02` = 2%) or the `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable to a fixed character count. To free budget for other skills, set low-priority entries to `"name-only"` in [`skillOverrides`](#override-skill-visibility-from-settings) so they list without a description. Also trim the `description` and `when_to_use` text at the source: put the key use case first, since each entry's combined text is capped at 1,536 characters regardless of budget. The cap is configurable with [`skillListingMaxDescChars`](https://code.claude.com/docs/en/settings-reference#skilllistingmaxdescchars).

### Angle brackets in a skill description show as `&lt;` and `&gt;`

Claude Code displays `<` and `>` in the `description` and `when_to_use` fields as `&lt;` and `&gt;`. To show a placeholder such as `<branch>`, use square brackets or [`argument-hint`](#frontmatter-reference):

* **Square brackets**: replace `<branch>` with `[branch]`, which displays as typed
* **`argument-hint`**: move the placeholder to a new `argument-hint: <branch>` line. It shows after the command name. If the skill is also uploaded to claude.ai or the Skills API, first [check whether `argument-hint` is accepted there](#using-skill-frontmatter-outside-claude-code).

## Documentation References

- Source page: https://code.claude.com/docs/en/skills (the full skills page, including the skill locations, live change detection, additional directories, Cowork and cloud sessions, synced skills, `skillOverrides` and `/skill-doctor`, which this copy omits)
- https://code.claude.com/docs/en/commands.md - built-in commands and bundled skills
- https://code.claude.com/docs/en/plugins/overview.md - packaging and distributing skills in a plugin
- https://code.claude.com/docs/en/plugins/components.md - plugin skills, a single skill at the plugin root, path variables and persistent data
- https://code.claude.com/docs/en/plugins/manifest-reference.md - plugin manifest and plugin environment variables
- https://code.claude.com/docs/en/plugins/cli-reference.md - reloading plugins and `claude plugin validate`
- https://code.claude.com/docs/en/plugins/install.md - installing a plugin
- https://code.claude.com/docs/en/plugins/troubleshooting.md - plugin not found in marketplace
- https://code.claude.com/docs/en/plugin-evals - `claude plugin eval`, graders and the no-plugin baseline
- https://code.claude.com/docs/en/sub-agents.md - subagents, preloaded skills, background subagents, startup context, forking the conversation
- https://code.claude.com/docs/en/hooks.md - hooks reference, hooks in skills and agents, limits on skill hooks
- https://code.claude.com/docs/en/hooks-guide.md - guide to writing hooks
- https://code.claude.com/docs/en/permissions.md - permission rules, `Skill(...)` rules, parameter form, moving the session with `/cd`
- https://code.claude.com/docs/en/permission-modes.md - auto mode, plan mode and the classifier
- https://code.claude.com/docs/en/settings.md - settings files and checking what an organization enforces
- https://code.claude.com/docs/en/settings-reference.md - `strictPluginOnlyCustomization`, `allowManagedPermissionRulesOnly`, `skillListingBudgetFraction`, `skillListingMaxDescChars`
- https://code.claude.com/docs/en/managed-settings.md - managed settings
- https://code.claude.com/docs/en/tools-reference.md - PowerShell tool, Bash timeout, backgrounding, output limits, `EndConversation`
- https://code.claude.com/docs/en/model-config.md - `/model` values, `availableModels`, effort levels, ultrathink
- https://code.claude.com/docs/en/env-vars - environment variables such as `CLAUDE_CODE_EFFORT_LEVEL` and `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`
- https://code.claude.com/docs/en/cli-reference - CLI flags such as `--debug`
- https://code.claude.com/docs/en/debug-your-config.md - diagnosing why a skill isn't appearing or triggering, the debug log
- https://code.claude.com/docs/en/errors.md - refused skill or command names, "No shell command was run"
- https://code.claude.com/docs/en/headless.md - non-interactive sessions
- https://code.claude.com/docs/en/scheduled-tasks.md - session-scoped scheduled tasks
- https://code.claude.com/docs/en/workflows.md - dynamic workflows
- https://code.claude.com/docs/en/checkpointing.md - checkpoints and subagent edits that are not restored
- https://code.claude.com/docs/en/how-claude-code-works.md - what happens when context fills up (compaction)
- https://code.claude.com/docs/en/memory.md - path-specific rules
- https://code.claude.com/docs/en/best-practices.md - keeping CLAUDE.md short
- https://code.claude.com/docs/en/glossary.md - frontmatter definition
- https://code.claude.com/docs/en/code-review-local - the `/code-review` skill
- https://agentskills.io - the Agent Skills open standard and spec
- https://agentskills.io/skill-creation/evaluating-skills - the eval file format and iteration workflow
- https://docs.claude.com/en/api/skills-guide - Skills API requirements
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices - skill authoring best practices across Claude products
- https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator - the `skill-creator` plugin
- https://github.com/anthropics/skills - Anthropic's skills repository with `package_skill.py`
- https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills - announcement of skill-creator's benchmark and comparison modes
