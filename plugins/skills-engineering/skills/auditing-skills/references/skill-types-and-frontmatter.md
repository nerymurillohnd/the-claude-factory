# Frontmatter and structure by skill type

This file is a lookup, not a set of rules: it gathers, from the official sources, which frontmatter fields, names, arguments, body features and folder layouts each type of skill accepts, so you can check the skill in front of you against the type it is. The rules for judging what you find live in your own reference; this file gives you the facts those rules apply to. Every table reproduces an official table or is built from quoted sources, named under each heading. The sources were read in full on 2026-11-17, against Claude Code 2.1.326.

## Contents

- How to use this file
- 1. Identify the skill's type
- 2. Claude Code frontmatter fields
- 3. Agent Skills specification fields
- 4. Fields each distribution path accepts
- 5. Name rules by type
- 6. Command name by location
- 7. Same names across locations
- 8. Who can invoke, and what loads
- 9. Arguments and string substitutions
- 10. Body features by type
- 11. Layout by type
- 12. Skills consumed by subagents
- 13. Correct and incorrect examples by type
- 14. Where the sources disagree

## How to use this file

Read this whole file, through "Where the sources disagree", before you use any part of it: a row read alone can hide a condition another section states, such as a field Claude Code accepts but an upload rejects. Then identify every type the skill is (§1): one skill can be several at once, such as a plugin skill that is also uploaded to claude.ai. Check the skill against each type's rows, and treat a fact as applying only to the types and versions its row names. When a fact here and the current official source disagree, the source wins: report the disagreement with both texts.

## 1. Identify the skill's type

A skill's type is set by where it lives, how it is distributed and who consumes it. Record each that applies:

- **Claude Code location skills:** enterprise, personal, project, nested and additional-directory skills, each a `<skill-name>/SKILL.md` folder (§6, §11).
- **Plugin skills:** a folder in a plugin's `skills/` directory or in a path its manifest's `skills` key lists; or a single `SKILL.md` at the plugin root, when the plugin has no `skills/` directory and no `skills` manifest key.
- **Skill folder as a plugin:** a personal or project skill folder that also holds `.claude-plugin/plugin.json`, loaded as the plugin `<name>@skills-dir`.
- **Command file:** a Markdown file in `.claude/commands/`, the older format.
- **Synced skill:** a skill enabled on a claude.ai account and downloaded to `~/.claude/skills/synced/`, named `anthropic-skills:<name>`.
- **claude.ai upload:** a ZIP uploaded to a claude.ai account, used in chat and Cowork and synced to Claude Code.
- **Skills API:** a skill uploaded to a workspace with `/v1/skills` and used in the code execution container.
- **Managed Agents:** a custom or pre-built skill attached through an agent's `skills` array, or discovered in a mounted GitHub repository.
- **Agent SDK:** a filesystem skill discovered through `settingSources` and enabled with the `skills` option.
- **Consumed by a subagent:** a skill forked with `context: fork`, or preloaded through a subagent's `skills` field (§12).
- **Bundled skill:** a skill that ships with Claude Code, such as `/doctor` or `/code-review`. You never audit one; it matters only when the audited skill shares its name (§7).

## 2. Claude Code frontmatter fields

Source: code.claude.com/docs/en/skills, "Frontmatter reference". Claude Code reads the frontmatter only when the opening `---` is the file's first line. "All fields are optional. Only `description` is recommended." A field name must match exactly: "Claude Code ignores a field it doesn't recognize without reporting an error." Boolean fields accept `yes`, `no`, `on`, `off`, `1` and `0` in any case, besides `true` and `false`. If the YAML doesn't parse, "the skill still loads with no fields set". A command file accepts the same fields except `name` and `paths`.

| Field | Required | Description |
| :-- | :-- | :-- |
| `name` | No | Command name shown in the `/` menu. Defaults to the directory name. See How a skill gets its command name for how the field interacts with the name you type to invoke the skill. |
| `description` | Recommended | What the skill does and when to use it. Claude uses this to decide when to apply the skill. If omitted, uses the first non-empty line of the markdown content. Put the key use case first: the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill listing to reduce context usage. Angle brackets in the text show as `&lt;` and `&gt;`. |
| `when_to_use` | No | Additional context for when Claude should invoke the skill, such as trigger phrases or example requests. Appended to `description` in the skill listing and counts toward the 1,536-character cap. |
| `argument-hint` | No | Hint shown during autocomplete to indicate expected arguments. Example: `[issue-number]` or `[filename] [format]`. |
| `arguments` | No | Named positional arguments for `$name` substitution in the skill content. Accepts a space-separated string or a YAML list. Names map to argument positions in order. |
| `disable-model-invocation` | No | Set to `true` to prevent Claude from automatically loading this skill. Use for workflows you want to trigger manually with `/name`. Also prevents the skill from being preloaded into subagents and from running when a session-scoped scheduled task fires with the skill as its prompt. Default: `false`. |
| `user-invocable` | No | Set to `false` when only Claude should invoke the skill: Claude Code hides it from the `/` menu and doesn't run it when you type `/name`. Use for background knowledge users shouldn't invoke directly. Default: `true`. |
| `allowed-tools` | No | Tools Claude can use without asking permission during the turn that invokes this skill. The grant clears when you send your next message. Accepts a space- or comma-separated string, or a YAML list. See Pre-approve tools for a skill. |
| `disallowed-tools` | No | Tools removed from Claude's available pool while this skill is active. Use for autonomous skills that should never call certain tools, such as `AskUserQuestion` for a background loop. Accepts a space- or comma-separated string, or a YAML list. The restriction clears when you send your next message. Like deny rules, the field can't remove `EndConversation` while any other tool remains. |
| `model` | No | Model to use when this skill is active. The override applies for the rest of the current turn and isn't saved to settings. The session model resumes when you send your next prompt. Accepts the same values as `/model`, or `inherit` to keep the active model. A value excluded by your organization's `availableModels` allowlist isn't used, and the session keeps its current model. In auto mode, and in plan mode while the classifier reviews commands, a model that auto mode doesn't support also isn't used, and the session keeps its current model. With `context: fork`, the value sets the forked subagent's model instead, and an excluded value follows the same rules as a subagent model override. |
| `effort` | No | Effort level for the rest of the current turn. Overrides the session effort level, but not the `CLAUDE_CODE_EFFORT_LEVEL` environment variable. With `context: fork`, the value sets the forked subagent's effort level instead. When you omit it, the level comes from the effort resolution order. For a fork on another model, see Effort level of subagents and teammates. Options: `low`, `medium`, `high`, `xhigh`, `max`; available levels depend on the model. |
| `context` | No | Set to `fork` to run in a forked subagent context. See Run skills in a subagent. |
| `agent` | No | Which subagent type to use when `context: fork` is set. |
| `background` | No | Only applies with `context: fork`. Set to `false` to wait for the forked subagent's result in the turn that invoked the skill, instead of running it in the background. Default: `true`. |
| `hooks` | No | Hooks that Claude Code registers when the skill is invoked and keeps running for the rest of the session. See Hooks in skills and agents for the configuration format, the `once` option, and the limits on skill hooks. |
| `paths` | No | Glob patterns that limit when this skill is activated. Accepts a comma-separated string or a YAML list. When set, Claude loads the skill automatically only when working with files matching the patterns. Patterns are relative to Claude's current working directory, and files outside that directory don't match. Uses the same glob format as path-specific rules. |
| `shell` | No | Shell to use for `` !`command` `` and ` ```! ` blocks in this skill. Accepts `bash` (default) or `powershell`. Setting `powershell` runs inline shell commands via PowerShell when the PowerShell tool is enabled: it's on by default on Windows without Git Bash, on by default with Git Bash for claude.ai and Console accounts, and needs `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` in Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry sessions and on macOS, Linux, and WSL. Set it to `0` to turn the tool off. |
| `metadata` | No | Free-form YAML map for your own key-value data, such as entitlement or catalog fields, read by your own tooling from `SKILL.md`. Claude Code doesn't act on its contents, and drops a value that isn't a map. Don't reuse frontmatter field names such as `paths` as keys. |
| `license` | No | License covering the skill. Part of the Agent Skills spec; see Using skill frontmatter outside Claude Code. Claude Code accepts the field but doesn't act on it. |
| `compatibility` | No | Environment requirements for the skill, such as intended products or system prerequisites, as defined by the Agent Skills spec; see Using skill frontmatter outside Claude Code. Accepts a string of up to 500 characters. Claude Code accepts the field but doesn't act on it. |

## 3. Agent Skills specification fields

Source: agentskills.io/specification, "Frontmatter". These six fields are the open standard; every other field in §2 is a Claude Code extension.

| Field | Required | Constraints |
| :-- | :-- | :-- |
| `name` | Yes | Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen. |
| `description` | Yes | Max 1024 characters. Non-empty. Describes what the skill does and when to use it. |
| `license` | No | License name or reference to a bundled license file. |
| `compatibility` | No | Max 500 characters. Indicates environment requirements (intended product, system packages, network access, etc.). |
| `metadata` | No | Arbitrary key-value mapping for additional metadata (a map from string keys to string values). |
| `allowed-tools` | No | Space-separated string of pre-approved tools the skill may use. (Experimental) |

The specification adds for `name`: "Must not contain consecutive hyphens (`--`)" and "Must match the parent directory name". For `compatibility`: "Most skills do not need the `compatibility` field." For `allowed-tools`: "Support for this field may vary between agent implementations."

## 4. Fields each distribution path accepts

Source: code.claude.com/docs/en/skills, "Using skill frontmatter outside Claude Code".

| Distribution path | Frontmatter fields you can use |
| :-- | :-- |
| Claude Code skills at any level, including plugin skills | Every field in the table above |
| claude.ai skill uploads, the Skills API, and packaging with `package_skill.py` from anthropics/skills | `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` |

A field outside the six makes packaging or upload fail "with a hard error instead of ignoring the field":

```text
Unexpected key(s) in SKILL.md frontmatter: argument-hint. Allowed properties are: allowed-tools, compatibility, description, license, metadata, name
```

The Skills API and Managed Agents uploads add, per platform.claude.com/docs/en/build-with-claude/skills-guide ("Requirements") and the Agent Skills overview:

- `name`: "Maximum 64 characters, lowercase letters/numbers/hyphens only, no XML tags, no reserved words (`anthropic`, `claude`)".
- `description`: "Maximum 1,024 characters, non-empty, no XML tags".
- `SKILL.md` "at the upload root (or at the top of a single enclosing folder)"; total upload "under 30 MB (uncompressed)"; an optional `display_name` up to 255 characters, derived from `name` when omitted.

## 5. Name rules by type

- **Claude Code location skills:** `name` is optional and "Defaults to the directory name"; when set, it "sets the command that the `/` menu shows and that you type, unless another command already uses that name. The directory name also invokes the skill." Claude Code doesn't require `name` to match the folder (documented behavior), while the specification does (requirement of the spec), so a skill that also targets an upload or another client keeps them equal.
- **Plugin skills:** `name` "sets the last segment of the command and the plugin prefix stays in place". On v2.1.246 or later a `name` that already starts with the plugin's prefix isn't prefixed again; from v2.1.216 through v2.1.245 the prefix was doubled.
- **Plugin-root `SKILL.md`:** `name` supplies the whole final segment, falling back to the plugin directory name; set it, "because otherwise a marketplace install names the skill after its cache directory rather than your plugin" (code.claude.com/docs/en/plugins/components).
- **Command files:** no `name` field; the file name is the command.
- **Synced skills:** the account name, prefixed `anthropic-skills:`.
- **Uploads, Skills API, Managed Agents:** `name` is required with the limits in §3 and §4, including the reserved words `anthropic` and `claude`.
- **Agent SDK `skills` option:** each entry is an exact name; an empty name, parentheses, commas, control characters, padding whitespace, a bare `*` or a `:*` suffix are rejected before the process starts.
- **Reserved in Claude Code:** a folder named `synced` in any capitalization is skipped in the enterprise, personal and project locations; outside a plugin, a folder, frontmatter `name` or command file named `anthropic-skills` or starting with `anthropic-skills:` doesn't load.
- **Characters Claude Code refuses** in a command name or frontmatter `name`: zero-width spaces and control characters, private-use or unassigned characters, direction-changing characters, any blank other than one plain space between words, and `<` or `>`. Outside a plugin the folder then doesn't load; in a plugin's `skills/` folder name they become hyphens; in a frontmatter `name` the name doesn't show and doesn't invoke.

## 6. Command name by location

Source: code.claude.com/docs/en/skills, "How a skill gets its command name".

| Skill location | Command name source | Example |
| :-- | :-- | :-- |
| Skill directory under `~/.claude/skills/` or `.claude/skills/` | Frontmatter `name` or the directory name | `.claude/skills/deploy-staging/SKILL.md` → `/deploy-staging`, or `/deploy` with `name: deploy` |
| Nested `.claude/skills/` directory, when the directory name clashes with another skill | Subdirectory path relative to the working directory, then the skill directory name | `apps/web/.claude/skills/deploy/SKILL.md` → `/apps/web:deploy` |
| `.claude/skills/` in an added directory outside the project, when the skill directory name clashes with an enterprise, personal, or project skill, or one in a directory added earlier | The added directory's folder name, then the skill directory name. When two added directories share a folder name, the prefix starts with the parent folder's name. Requires v2.1.309 or later | `../cli/.claude/skills/verify/SKILL.md` with `--add-dir ../cli` → `/cli:verify`. With `--add-dir ../a/cli --add-dir ../b/cli`, a `verify` skill in each, and none elsewhere, the one in `../a/cli` → `/verify` and the other → `/b/cli:verify` |
| File under `.claude/commands/` | File name without extension | `.claude/commands/deploy.md` → `/deploy` |
| File in a subdirectory of `.claude/commands/` | Subdirectory path relative to `commands/` with each `/` replaced by `:`, then the file name without extension | `.claude/commands/frontend/component.md` → `/frontend:component` |
| Plugin `skills/` subdirectory | Frontmatter `name` or the directory name, namespaced by plugin | `my-plugin/skills/review/SKILL.md` → `/my-plugin:review`, or `/my-plugin:fancy` with `name: fancy` |
| Plugin root `SKILL.md` | Frontmatter `name`, with the plugin directory name as a fallback | `my-plugin/SKILL.md` with `name: review` → `/my-plugin:review`. See a single skill at the plugin root |
| Skill synced from claude.ai | The skill's name on your claude.ai account, prefixed with `anthropic-skills:` | Account skill `deploy` → `/anthropic-skills:deploy`, or `/deploy` while no other command uses that name |

Where each location loads (same page, "Choose where skills load"):

| Location | Path | Loads in |
| :-- | :-- | :-- |
| Enterprise | `.claude/skills/<skill-name>/SKILL.md` in the managed settings directory | All users on machines where your organization deploys it |
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | All your projects on this machine, but not Cowork or cloud sessions |
| Project | `.claude/skills/<skill-name>/SKILL.md` | Sessions in this repository, but not cloud threads in a project. Commit it so your team gets it too |
| Nested | `<subdir>/.claude/skills/<skill-name>/SKILL.md` | Sessions started in or below `<subdir>`, but not cloud threads in a project. Outside those threads, a session started above it loads the skill once Claude works on files there. See monorepos and subdirectories |
| Additional directory | `.claude/skills/<skill-name>/SKILL.md` in a directory you pass with `--add-dir` | That session. See directories outside the project |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | Wherever the plugin is enabled, as `/plugin-name:skill-name` |
| claude.ai account | Skills enabled for your claude.ai account | Cowork sessions, cloud sessions, and terminal sessions where you sign in with that account. See Skills synced from claude.ai |

## 7. Same names across locations

Source: code.claude.com/docs/en/skills, "Resolve skills that share a name".

| Same name in | Which one runs |
| :-- | :-- |
| Two of enterprise, personal, and project | Enterprise over personal, and personal over project. With `deploy` in both `~/.claude/skills/` and the project's `.claude/skills/`, `/deploy` runs the personal one |
| Any of those locations and a bundled skill | Your skill replaces the bundled command, but not its aliases. A project `code-review` skill replaces `/code-review`, and the bundled alias `/review` never runs your skill |
| Any of those locations and a built-in command | In a local terminal session, your skill replaces the built-in command, but not its aliases. A project `usage` skill replaces `/usage`, and the built-in alias `/cost` still runs the built-in command |
| A skill and a file in `.claude/commands/` | The skill |
| A project-root skill and a nested skill | Both load. See monorepos and subdirectories |
| An enterprise, personal, or project skill and a skill in an added directory outside the project | The enterprise, personal, or project skill, while the added directory's skill runs under a prefixed name. See run a same-named skill from an added directory |
| Two added directories outside the project | The skill from the directory added first, in `--add-dir` or `/add-dir` order. The other runs under a prefixed name |
| A plugin skill and a skill at any of the locations above | Both load, because plugin skills are namespaced as `/plugin-name:skill-name` |
| Any of the above and the short name of a skill synced from your claude.ai account | The other skill or command. The synced skill is then listed and runs only under its full name. See When a synced skill name matches another command |

## 8. Who can invoke, and what loads

Source: code.claude.com/docs/en/skills, "Control who invokes a skill".

| Frontmatter | You can invoke | Claude can invoke | When loaded into context |
| :-- | :-- | :-- | :-- |
| (default) | Yes | Yes | Description in context, full skill loads when invoked |
| `disable-model-invocation: true` | Yes | Not on its own | Description not in context, full skill loads when invoked |
| `user-invocable: false` | No | Yes | Description in context, full skill loads when invoked |

`disable-model-invocation: true` also "prevents the skill from being preloaded into subagents and from running when a session-scoped scheduled task fires with the skill as its prompt". After plain text, `/name` "gives Claude permission to run the skill but doesn't run it"; only at the start of the message does Claude Code run it directly.

## 9. Arguments and string substitutions

Source: code.claude.com/docs/en/skills, "Available string substitutions" and "Pass arguments to skills". These are Claude Code features: `arguments` and `argument-hint` are outside the specification's six fields (§4).

| Variable | Description |
| :-- | :-- |
| `$ARGUMENTS` | All arguments passed when invoking the skill. When no placeholder receives an argument, Claude Code appends them as `ARGUMENTS: <value>`. See Pass arguments to skills. |
| `$ARGUMENTS[N]` | Access a specific argument by 0-based index, such as `$ARGUMENTS[0]` for the first argument. |
| `$N` | Shorthand for `$ARGUMENTS[N]`, such as `$0` for the first argument or `$1` for the second. |
| `$name` | Named argument declared in the `arguments` frontmatter list. Names map to positions in order, so with `arguments: [issue, branch]` the placeholder `$issue` expands to the first argument and `$branch` to the second. |
| `${CLAUDE_SESSION_ID}` | The current session ID. Useful for logging, creating session-specific files, or correlating skill output with sessions. |
| `${CLAUDE_EFFORT}` | The current effort level: `low`, `medium`, `high`, `xhigh`, or `max`. Use this to adapt skill instructions to the active effort setting. |
| `${CLAUDE_SKILL_DIR}` | The directory containing the skill's `SKILL.md` file. For plugin skills, this is the skill's subdirectory within the plugin, not the plugin root. Use this in bash injection commands to reference scripts or files bundled with the skill, regardless of the current working directory. |
| `${CLAUDE_PROJECT_DIR}` | The project root directory. This is the same path hooks and MCP servers receive as `CLAUDE_PROJECT_DIR`. Use this to reference project-local scripts or files, such as `${CLAUDE_PROJECT_DIR}/.claude/hooks/helper.sh`, independent of where the skill is installed. |
| `${CLAUDE_PLUGIN_ROOT}` | The plugin's installation directory. Substituted only in plugin skills. Use this to reference scripts or files bundled anywhere in the plugin, including resources shared between the plugin's skills. See plugin environment variables. |
| `${CLAUDE_PLUGIN_DATA}` | The plugin's persistent data directory, which survives plugin updates. Substituted only in plugin skills. Use this to reference installed dependencies, generated files, or caches that must outlive an update. |

- With arguments but no placeholder that receives one, Claude Code appends `ARGUMENTS: <value>` to the content.
- An indexed placeholder with no argument stays literal; a named one with no argument expands to an empty string.
- Indexed arguments use shell-style quoting; `$ARGUMENTS` is the full string as typed.
- A literal `$` before a digit, `ARGUMENTS` or a declared name is escaped with one backslash, such as `\$1.00`; the escape doesn't stop `${CLAUDE_*}` substitution.
- `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PROJECT_DIR}` are substituted in the content and in `allowed-tools` Bash rules; `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` too, in plugin skills only.
- Stacked skills: at the terminal prompt, `/write-tests /fix-issue 123` loads both and passes `123` to each, up to the first skill plus five more; through the Agent SDK or `claude -p` only the first loads. Expansion stops at a forked skill or one whose arguments may start with another command.

## 10. Body features by type

- **Claude Code local sessions:** every body feature works: `!` commands and ` ```! ` blocks, `@` file references, string substitutions.
- **claude.ai chat and the API:** "Claude Code-only body features, such as dynamic context injection, don't function in claude.ai chat or through the API."
- **Synced skills in a cloud session:** the body behaves as a local skill's.
- **Synced skills in Cowork on the desktop:** as a local skill's, except every `!` command line becomes the `disableSkillShellExecution` placeholder.
- **Synced skills in a terminal or VS Code session:** `!` commands don't run, `@` references aren't attached, and `${CLAUDE_PROJECT_DIR}` and `${CLAUDE_SESSION_ID}` aren't substituted; all reach Claude as literal text (v2.1.228 or later).
- **Skills API and Managed Agents code execution:** "No network access", "No runtime package installation: Only pre-installed packages available", and "A fresh container is created unless you specify an existing container ID".
- **Frontmatter hooks:** under a `strictPluginOnlyCustomization` lock, "A skill keeps its frontmatter hooks under that lock only if it's a plugin skill, a bundled skill, or a skill in the managed settings directory" (code.claude.com/docs/en/hooks).

## 11. Layout by type

- **Any skill (specification):** a directory with `SKILL.md` required, and optional `scripts/`, `references/`, `assets/` "and any additional files or directories".
- **Claude Code locations:** `<location>/.claude/skills/<skill-name>/SKILL.md`, or `~/.claude/skills/<skill-name>/SKILL.md` for personal (§6). An enterprise, personal or project entry may be a symlink to a folder elsewhere.
- **Plugin:** `<plugin>/skills/<skill-name>/SKILL.md`; extra folders through the manifest's `skills` key, which "add to the default `skills/` scan rather than replacing it"; or one `SKILL.md` at the plugin root when there is no `skills/` folder and no `skills` key.
- **Skill folder as a plugin:** a personal or project skill folder plus `.claude-plugin/plugin.json`, with its own agents, hooks and MCP servers; in a project it needs the workspace trust dialog, and an administrator can block it.
- **claude.ai upload:** a ZIP whose root entry is the skill folder, with the folder name matching the skill's name. Correct: `my-skill.zip` holding `my-skill/SKILL.md`. Incorrect: files placed directly at the ZIP root (support.claude.com, "How to create custom Skills").
- **Skills API:** `SKILL.md` at the upload root or at the top of a single enclosing folder; under 30 MB uncompressed; up to 20 skills per request.
- **Managed Agents repository discovery:** exactly `.claude/skills/<skill-name>/SKILL.md`, "one directory level deep at the repository root", read with the agent's `read` tool; an agent with `read` disabled doesn't load repository skills. Up to 500 skills per session.
- **Agent SDK:** "Skills must be created as filesystem artifacts (`.claude/skills/<name>/SKILL.md`)"; "The SDK does not have a programmatic API for registering skills."

## 12. Skills consumed by subagents

Source: code.claude.com/docs/en/skills, "Run skills in a subagent", and code.claude.com/docs/en/sub-agents, "Preload skills into subagents".

| Approach | System prompt | Task | Also loads |
| :-- | :-- | :-- | :-- |
| Skill with `context: fork` | From agent type | SKILL.md content | CLAUDE.md, per the agent's startup context |
| Subagent with `skills` field | Subagent's markdown body | Claude's delegation message | Preloaded skills + CLAUDE.md, per the subagent's startup context |

- **Forked (`context: fork`):** the subagent of the `agent` type gets the skill content as its prompt and "doesn't see your conversation history". It runs in the background unless `background: false`, and a backgrounded fork has the narrower background tool set. `model` and `effort` set the fork's model and effort. A skill with guidelines but no task "returns without meaningful output".
- **Preloaded (`skills` field):** "The full content of each listed skill is injected into the subagent's context at startup, up to the first 32 distinct names in the list." A skill with `disable-model-invocation: true` can't be preloaded. A missing or disabled skill is skipped with a warning only in the debug log. Unlisted project, user and plugin skills stay reachable through the Skill tool unless `Skill` is left out of `tools` or added to `disallowedTools`.

## 13. Correct and incorrect examples by type

- **A skill that is uploaded to claude.ai or used through the API.**
  - Incorrect: `argument-hint: "[issue]"` or `context: fork` in its frontmatter: the upload fails with "Unexpected key(s) in SKILL.md frontmatter".
  - Correct: only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`; Claude Code-only fields kept in a separate Claude Code copy, or left out.
- **A skill that is uploaded or follows the specification.**
  - Incorrect: `name: PDF-Processing`, `name: -pdf`, `name: pdf--processing`, `name: claude-helper`, or a folder `pdf-tools/` with `name: pdf-processing`.
  - Correct: `name: pdf-processing` in the folder `pdf-processing/`.
- **A plugin-root `SKILL.md`.**
  - Incorrect: no `name`: a marketplace install names the skill after its cache directory.
  - Correct: `name: review` in `my-plugin/SKILL.md`, invoked as `/my-plugin:review`.
- **A plugin skill whose `name` repeats the prefix.**
  - Version-dependent: `name: my-plugin:fancy` becomes `/my-plugin:fancy` on v2.1.246 or later, and `/my-plugin:my-plugin:fancy` on v2.1.216 through v2.1.245.
- **A command file.**
  - Incorrect: `name:` or `paths:` in `.claude/commands/deploy.md`: neither is read.
  - Correct: the file name sets the command; move it to `.claude/skills/deploy/SKILL.md` to use `name`, `paths` or supporting files.
- **A skill meant for subagent preloading.**
  - Incorrect: `disable-model-invocation: true`: it can't be preloaded, and the agent starts without it.
  - Correct: model invocation left on, with `user-invocable: false` when only Claude should use it.
- **A forked skill.**
  - Incorrect: `context: fork` on reference content such as "use these API conventions": the subagent has no task.
  - Correct: `context: fork` with an explicit task, an `agent` type that has the tools the task needs, and `background: false` when a step needs a tool outside the background set.
- **A skill that relies on body features.**
  - Incorrect: a step that depends on `` !`git diff` `` output in a skill also used in claude.ai chat, or synced to a terminal session, where the line reaches Claude as literal text.
  - Correct (inference): the step tells Claude to run the command itself where injection doesn't run, or the skill targets only the surfaces that run it.
- **A personal skill meant for cloud sessions or Cowork.**
  - Incorrect: kept only in `~/.claude/skills/`: those sessions don't read it, and a cloud scheduled task reports it not found.
  - Correct: enabled on the claude.ai account, or, for cloud sessions other than project threads, committed to the repository's `.claude/skills/`.
- **A skill discovered from a repository by Managed Agents.**
  - Incorrect: `.claude/skills/tools/pdf/SKILL.md`, two levels deep, or a skill in a subdirectory's `.claude/skills/`.
  - Correct: `.claude/skills/pdf/SKILL.md` at the repository root.

## 14. Where the sources disagree

- **claude.ai description limit and a `dependencies` field.** support.claude.com, "How to create custom Skills", says the description has a "200 characters maximum" and lists an optional field "dependencies: Software packages required by your skill". code.claude.com/docs/en/skills says claude.ai uploads accept only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`, and that any other field fails the upload with a hard error; the specification and the platform pages give the description 1,024 characters. Judge an upload by the developer documentation's six fields and 1,024 characters, and report the support article's text as a disagreement, with both quotes, whenever a skill relies on it.
- **`name` matching the folder.** Required by the specification; not required by Claude Code, where the directory name and `name` both invoke the skill (§5).
- **The support article's example `name: Brand Guidelines`** has a capital letter and a space, which the specification and the platform requirements reject; follow the requirements.
