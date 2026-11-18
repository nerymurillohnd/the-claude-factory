# Frontmatter and description

This file teaches you how to audit a skill's frontmatter, its name and its description: whether the frontmatter parses and every field in it is valid and right for the skill's purpose on each surface it targets, whether the name is valid and says what the skill does, and whether the description routes Claude to the skill for the requests it serves and away from everything else. Each section gives you the principle, why it matters, and what to do when you audit.

## Contents

- How to use this file
  - Before auditing: establish the context
  - Then, audit area by area
- 1. Frontmatter structure and parsing
  - 1.1 Where the block must be
  - 1.2 What happens when the YAML doesn't parse
  - 1.3 YAML values that break or change type
  - 1.4 Strings, lists and maps: the shape each field takes
  - 1.5 Field names and unknown keys
- 2. Fields: validity and fit
  - 2.1 Identify the target surfaces first
  - 2.2 Required fields per target
  - 2.3 Who may invoke the skill: `disable-model-invocation` and `user-invocable`
  - 2.4 `allowed-tools` and `disallowed-tools`
  - 2.5 Input at invocation: `argument-hint` and `arguments`
  - 2.6 `model` and `effort`
  - 2.7 `paths`
  - 2.8 `shell`
  - 2.9 `hooks`
  - 2.10 `context`, `agent`, `background`: valid values
  - 2.11 `license`, `compatibility`, `metadata`
- 3. The name
  - 3.1 Whether to write `name`, and the directory match
  - 3.2 Format rules
  - 3.3 Reserved names
  - 3.4 Naming quality and consistency
- 4. The description
  - 4.1 The description is the router
  - 4.2 What it must say: the capabilities and the user's intent
  - 4.3 Point of view
  - 4.4 Wording users actually type
  - 4.5 Scope boundaries for plausible near-misses
  - 4.6 Vague versus specific
  - 4.7 XML tags and angle brackets
  - 4.8 `when_to_use`
  - 4.9 Descriptions across a set of skills
- 5. Activation and trigger tests
  - 5.1 What automatic activation depends on
  - 5.2 Whether the skill targets tasks Claude needs it for
  - 5.3 What kind of test the skill ships
  - 5.4 Judging the queries
  - 5.5 Judging how the tests were run and used
  - 5.6 Recommending trigger tests when none ship
- Classifying findings
- Improvement opportunities
- Delivering the report

## How to use this file

Read this whole file, through its final section, "Delivering the report", before you judge anything. This complete reading, and an audit of the skill against every point in it, are a precondition of your audit: no point stays unaudited. Keep to the file's order: establish the context, then audit the frontmatter (§1, §2), the name (§3), the description (§4) and activation (§5), then classify what you found.

Audit from the seat of a Claude that has only this skill's name and description in front of it, among every other skill it can see, and has to decide whether to load it; and then from the seat of the surface that reads the frontmatter. Ask at each point whether that Claude would load the skill for the wrong request, miss it for the right one, or whether the surface would reject the skill, ignore a field, or apply a setting the author didn't mean.

The prompt you receive states what the orchestrating model's scripts already checked, such as whether the frontmatter parses, the fields it holds and their values, and the structural validator's output. Take those results as verified and judge what they mean for the skill. When a mechanical result a point needs is missing, record it under Checklist exceptions as blocked and judge everything else by reading. You never run, test, measure or upload anything, and never run the skill: where only a run or an upload would settle a point, name that check.

### Before auditing: establish the context

What is valid and what routes well depend on the skill in front of you, so settle these four points first.

1. **Where the skill lives and which surfaces serve it.** A personal, project, plugin or managed skill in Claude Code; a skill uploaded to claude.ai, enabled on a claude.ai account or sent to the Skills API; or a skill meant for other Agent Skills clients. This decides which fields are valid (§2.1) and which name rules apply (§3).
2. **How the skill gets invoked.** By Claude on its own, by the user with `/name`, or only one of the two (§2.3). A skill Claude can't invoke routes nothing through its description (§4.1, §5.1).
3. **What the skill is for**, from its body and every file it points to: the jobs it does, the inputs it takes and the output it gives. You judge the name and the description against this, not against what they claim.
4. **Its siblings.** The other skills in the same plugin or folder, whose descriptions compete with this one for the same requests (§4.9).

### Then, audit area by area

Audit what the skill has and what it should have, with the same care for each: finding what its purpose needs and the frontmatter or description lacks, or a stronger version of what it has, is as much your job as finding a defect. For every field, the name, the description and its trigger tests, give exactly one of these outcomes:

- **Present and optimal.** Valid on every target and right for the skill's purpose. Record no finding.
- **Present but wrong or excess.** Invalid on a target, set against the skill's purpose, misleading Claude's choice, or not needed. Record it as a defect, classify it (see "Classifying findings"), and say whether it must be deleted, rewritten or moved.
- **Present, right, but improvable.** It works, but a stronger version from this file would route or serve the skill better. Record it as an improvement opportunity, with the exact replacement written out.
- **Absent, and the skill needs it.** Record it as an improvement opportunity, or as a defect where a target requires it: write out the exact field, name or description text, and cite the point of this file it rests on.
- **Absent, and the skill doesn't need it.** Record no finding. Never recommend a field, a boundary or a test by default.

Work only from what is written in the skill. If you have no line to point to, you have no finding; for a missing field or clause, point to where it belongs.

---

## 1. Frontmatter structure and parsing

### 1.1 Where the block must be

A `SKILL.md` is YAML frontmatter between two `---` lines, followed by the Markdown body. Claude Code reads frontmatter only when the opening `---` is the file's first line. Anything above it, even one blank line or a heading, makes Claude Code treat the whole file as body text, with the `---` markers and every field included. No field then applies, and the description never reaches the listing. Other clients look for the opening `---` at the start of the file too.

When you audit:
- Flag any content before the opening `---`: text, a title, a comment or a blank line.
- Flag a block with no closing `---`, or a closing `---` that comes after body text.
- Flag a block that sits anywhere other than the top of the file, such as a second block lower down or one inside a code fence. Only a block that opens on line 1 is frontmatter.

### 1.2 What happens when the YAML doesn't parse

A parse failure fails silently, and differently on each surface:
- **Claude Code** loads the skill with no fields set. `/skill-name` still runs the body, but Claude has no `description` to match, so the skill never triggers on its own, and every other field (`disable-model-invocation`, `allowed-tools`, `hooks`…) is lost as well. Because the command still works, a broken block can go unnoticed.
- **Other Agent Skills clients** are told to skip a skill whose YAML is completely unparseable. Some first retry a value that holds a colon after wrapping it in quotes; others don't.
- **Uploads** (claude.ai, the Skills API, `package_skill.py`) validate against the spec.

So a skill that "works when I type `/name`" proves nothing about its frontmatter.

When you audit:
- Read the block as a strict YAML parser would. Flag every construct in 1.3 that breaks parsing or changes a value's type.
- When you can't be certain the block parses, say so and name the check that settles it: `claude plugin validate <skills-dir or plugin-dir>` for Claude Code, which reports each `SKILL.md` whose frontmatter fails to parse, or `skills-ref validate <skill-dir>` for the spec. `claude --debug` shows Claude Code's parse error.
- Never take "the skill runs with `/name`" as evidence that its fields were read.

### 1.3 YAML values that break or change type

Most frontmatter values are plain unquoted strings, and YAML gives some characters in them structural meaning. Only some parsers, Claude Code's among them, tolerate the result. A value can parse cleanly and still have the wrong type, so a field that should hold a string ends up holding a list or a number.

When you audit:
- Flag an unquoted value that contains a colon followed by a space, such as `description: Use when: the user asks…`. It is invalid YAML. Claude Code has loaded such values since a fix, but another client may skip the skill. Recommend double quotes, or a YAML block scalar for a long value.
- Flag an unquoted value that opens with `[`, such as `argument-hint: [issue-number]`. YAML reads it as a list, not a string, and Claude Code coerces it back to a string only because of a crash fix. Recommend quoting it: `argument-hint: "[issue-number]"`.
- Flag a value that YAML reads as a number or a boolean when the field needs a string, such as `name: 3000` or a `metadata` value like `version: 1.0`. Recommend quoting it (`version: "1.0"`, as the spec's own example does).
- Flag a `description` written as a YAML list or map. It must be a single string.
- Accept the spelling of a boolean field (`disable-model-invocation`, `user-invocable`, `background`) when it is `true`, `false`, `yes`, `no`, `on`, `off`, `1` or `0`, in any letter case. Claude Code accepts all of these.

Recognize the difference:
- `description: Reviews diffs. Triggers include: commits, PRs` is a colon inside an unquoted value, and strict parsers reject it.
- `description: "Reviews diffs. Triggers include: commits, PRs"` parses everywhere.

### 1.4 Strings, lists and maps: the shape each field takes

Each field expects one shape, and that shape can depend on the surface. Claude Code accepts more shapes than the spec does, so frontmatter that is valid in Claude Code can still be wrong for a portable skill.

When you audit:
- Check each field's shape against where the skill runs:
  - `allowed-tools`: the spec defines it as a space-separated string. Claude Code also accepts a comma-separated string or a YAML list.
  - `disallowed-tools`: a space- or comma-separated string, or a YAML list (Claude Code only).
  - `arguments`: a space-separated string or a YAML list (Claude Code only).
  - `paths`: a comma-separated string or a YAML list (Claude Code only).
  - `metadata`: a map. The spec defines it as string keys to string values. Claude Code drops a value that isn't a map.
  - Every other field is a single scalar.
- Flag a YAML list in `allowed-tools` on a skill that is uploaded or meant for other clients. The spec defines only the string form.
- Flag `metadata` written as a string or a list. Claude Code discards it, and the spec requires a map.

### 1.5 Field names and unknown keys

A field name must match the documented spelling exactly. Field names are lowercase words joined by hyphens, with one exception: `when_to_use`. An unknown key is silently ignored by Claude Code, so a misspelled `disable-model-invocaton` or a `user_invocable` loads without error and has no effect. The same key fails an upload outright: claude.ai uploads, the Skills API and `package_skill.py` reject any key outside the spec's six fields with `Unexpected key(s) in SKILL.md frontmatter`.

When you audit:
- Compare every key against the field list in section 2. Flag any key that is misspelled, written in the wrong case or in snake_case (except `when_to_use`), or undocumented. State the effect: in Claude Code the intended setting does nothing; on an upload target, the upload fails.
- Flag custom data placed as a top-level key, such as `author`, `version`, `tags`, or the `dependencies` field the help-center article lists. Recommend moving it under `metadata`, which the spec provides for properties it doesn't define. Package requirements go in `compatibility` or in the body.
- Flag a key under `metadata` that reuses a frontmatter field name, such as `metadata: { paths: … }`. Claude Code's documentation forbids it, and Claude Code doesn't act on anything under `metadata`, so the setting has no effect there.

## 2. Fields: validity and fit

### 2.1 Identify the target surfaces first

Whether a field is valid depends on where the skill will be served. Claude Code, at every level including plugins, accepts every field in this section. claude.ai uploads, the Skills API and `package_skill.py` accept only the six fields the Agent Skills spec defines: `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`. Any other key makes packaging or upload fail. Enabling a personal Claude Code skill for a claude.ai account, for Cowork, cloud sessions or scheduled tasks, is an upload too, so the same six-field rule applies. Other Agent Skills clients implement the spec, where `allowed-tools` is experimental and its support varies.

These fields exist only in Claude Code: `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths` and `shell`. A command file in `.claude/commands/` takes the same fields except `name` and `paths`.

Before you judge the skill's type, read `skill-types-and-frontmatter.md`, in this skill's `references/` folder, whole: it lists, from the official sources, every frontmatter field, name rule, argument, body feature and folder layout by type of skill, and a row read alone can hide a condition another section states.

When you audit:
- Determine the target before judging any field. The skill's location tells you: a plugin's `skills/`, or a `.claude/skills/` folder, means Claude Code. Packaging instructions, a ZIP, an API upload or a claude.ai or Cowork mention means an upload target. If you can't tell and the answer changes a finding, say which finding depends on it.
- On a skill for any upload target, flag every Claude Code-only field as an error: the upload fails. Recommend either removing it, or keeping a separate Claude Code copy if the skill needs that behavior.
- On a Claude Code-only skill, accept the Claude Code fields. If the skill would be valuable elsewhere and uses none of them, note that it is portable as written.
- Flag `paths` and `name` in a `.claude/commands/` file. Neither applies there.

### 2.2 Required fields per target

| Target | `name` | `description` |
| :-- | :-- | :-- |
| Agent Skills spec, claude.ai upload, Skills API | Required | Required, non-empty |
| Claude Code | Optional; defaults to the directory name | Recommended; if absent, Claude Code uses the first non-empty line of the body |

When you audit:
- On a portable or uploaded skill, flag a missing `name` or a missing or empty `description` as an error. Other clients are told to skip a skill that has no description.
- On a Claude Code skill, flag a missing `description` as absent and needed. It is the one field Claude Code recommends, because Claude uses it to decide when to apply the skill. The fallback, the body's first line, was written as an instruction, not as a description of when to use the skill.

### 2.3 Who may invoke the skill: `disable-model-invocation` and `user-invocable`

By default both the user (with `/name`) and Claude can start any skill. Each field closes one door:
- **`disable-model-invocation: true`** stops Claude from starting the skill on its own. The skill's description leaves Claude's context, and if Claude tries to invoke it, Claude Code blocks the call unless the user's message names `/name`. Use it for skills with side effects, or whose timing the user owns: commit, deploy, publish, send a message. You don't want Claude deploying because the code looks ready. Default `false`.
- **`user-invocable: false`** hides the skill from the `/` menu, and typing `/name` doesn't run it. Claude can still invoke it. Use it for background knowledge that makes no sense as a command, such as how a legacy system works. Default `true`.

When you audit:
- Ask whether the skill changes anything outside the conversation (files pushed, messages sent, deployments, releases, money or data moved), or whether the user needs to choose the moment. If it does and `disable-model-invocation: true` is absent, report it as absent and needed.
- Flag `disable-model-invocation: true` on a skill whose value is that Claude applies it when relevant: reference knowledge, conventions, read-only analysis. It makes such a skill unreachable unless the user remembers to type it.
- Also flag `disable-model-invocation: true` when the skill is meant to run as the prompt of a session-scoped scheduled task, because it doesn't run there. Flag it as well on a personal or project skill named `verify` or `simplify` that should run before each commit, because Claude Code then doesn't tell Claude to run it.
- Recommend `user-invocable: false` for pure background knowledge that the `/` menu offers as a command. Flag it on a skill a user would reasonably want to start.
- Flag `user-invocable: false` that is used to keep Claude from running a dangerous skill. It doesn't do that: only `disable-model-invocation: true` stops Claude.
- Flag a skill that sets both `disable-model-invocation: true` and `user-invocable: false`. Neither the user nor Claude can start it in the usual way. INFERENCE from the documented effect of each field.

Recognize the difference:
- A `deploy` skill with no invocation fields lets Claude decide to deploy. It needs `disable-model-invocation: true`.
- A `legacy-billing-context` skill with `user-invocable: false` stays available to Claude whenever billing code comes up.

### 2.4 `allowed-tools` and `disallowed-tools`

`allowed-tools` lists tools Claude may use without a permission prompt while it runs the skill. It is the only spec field that touches tools, and the spec marks it experimental. Its syntax is a list of permission rules: a bare tool name (`Read`), or a tool with a specifier (`Bash(git add *)`). In a Bash rule, `Bash(git:*)`, the spec's example form, is equivalent to `Bash(git *)` in Claude Code, but only when `:*` ends the pattern. In `Bash(git:* push)` the colon is literal. `disallowed-tools` (Claude Code only) removes tools from Claude's pool while the skill is active. It suits autonomous skills that must never call a tool, such as `AskUserQuestion` in a background loop. It cannot remove `EndConversation` while any other tool remains.

When you audit:
- Check each entry's syntax: a tool name, optionally followed by one parenthesized specifier. Flag unbalanced parentheses, unknown tool names, and a `:*` placed mid-pattern.
- Check that the separator matches the surface (1.4). On a portable skill, recommend the spec's space-separated string.
- Compare the list with what the body actually runs. Flag each entry for a tool or command the body never uses. Recommend an entry for each command the body runs that would otherwise stop for approval.
- Flag a grant that reaches beyond what the body runs, such as a bare `Bash` when the body runs two git commands: it pre-approves commands the skill never needs. Recommend the narrowest rule that covers each command.
- Flag `disallowed-tools` used only to express a preference. Recommend saying it in the body instead, and keeping the field for tools whose use would break the skill's purpose.

### 2.5 Input at invocation: `argument-hint` and `arguments`

Both fields are Claude Code only. `argument-hint` is the hint autocomplete shows after the command, such as `[issue-number]` or `[filename] [format]`. `arguments` declares names for positional arguments, so the body can write `$issue` instead of `$0`. It takes a space-separated string or a YAML list, and names map to positions in order. A declared name with no matching argument expands to an empty string. If no placeholder in the body receives the input, Claude Code appends `ARGUMENTS: <value>` to the content, so a skill can take input without any placeholder.

When you audit:
- If the body uses `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N` or a named placeholder and the skill is user-invocable, recommend an `argument-hint` that shows what to type.
- Flag `argument-hint` or `arguments` on a skill that takes no input.
- Flag a `$name` placeholder in the body that `arguments` doesn't declare. The documentation defines substitution only for declared names. Also flag a declared name the body never uses.
- Check that the order of `arguments` matches the order the `argument-hint` shows. INFERENCE: both describe the same positions.
- Quote an `argument-hint` that starts with `[` (1.3).

### 2.6 `model` and `effort`

Both are Claude Code only, and both apply to the rest of the turn that invokes the skill. With `context: fork`, they set the forked subagent's model and effort instead.
- `model` accepts the values `/model` accepts, or `inherit`. A model the organization's `availableModels` excludes isn't used, and neither is one that auto mode doesn't support while auto mode or the plan-mode classifier is active. In those cases the session keeps its model.
- `effort` accepts `low`, `medium`, `high`, `xhigh` or `max`, and which levels are available depends on the model. It doesn't override the `CLAUDE_CODE_EFFORT_LEVEL` environment variable.

When you audit:
- Flag an `effort` value outside the five levels. Flag a `model` value that isn't `inherit` or a recognizable `/model` value.
- Ask what in the skill's task requires a different model or effort than the session's. The documentation gives no criterion for when to set them. Accept a stated reason, such as a demanding analysis or a mechanical task. Flag a value with no reason the reader can see as excess, because it silently overrides the user's own choice for that turn. INFERENCE from the documented override behavior.
- On a skill distributed to other users, note that `model` may not be honored: their organization's allowlist or auto mode can refuse the value. The skill must still work on the session's model.

### 2.7 `paths`

`paths` (Claude Code only) takes glob patterns, as a comma-separated string or a YAML list, in the same format as path-specific rules. When it is set, Claude loads the skill automatically only while working with files that match. Patterns are relative to Claude's current working directory, so files outside that directory never match, including files in a sibling worktree.

When you audit:
- Recommend `paths` for a skill that is relevant only to one area or file type of a repository, such as migrations, a frontend package or `*.tf` files.
- Flag `paths` on a skill whose tasks don't involve files that match, or that are often done outside the working directory. Claude then never loads it automatically.
- Check that the glob syntax is valid, and that patterns are written relative to the working directory, not as absolute paths.

### 2.8 `shell`

`shell` (Claude Code only) selects the shell for the skill's `` !`command` `` and ` ```! ` blocks. It takes `bash` (the default) or `powershell`. `powershell` takes effect only where the PowerShell tool is enabled. An explicit `shell: bash` fails the invocation where bash is unavailable, as on Windows without Git Bash. In every other case, the commands run through bash when it is available and through PowerShell when it isn't.

When you audit:
- Flag `shell` on a skill with no `!` command blocks. It has no effect.
- Recommend `shell: powershell` only when the blocks are PowerShell syntax.
- Flag an explicit `shell: bash` when the commands would run under either shell. It turns the fallback on Windows without Git Bash into a hard failure. Accept it when the commands need bash and failing early is the intent. INFERENCE: the documentation separates the failing case from all others, and its error message names `shell: bash` in frontmatter.

### 2.9 `hooks`

`hooks` (Claude Code only) registers hooks, in the same configuration format as settings files, when the skill is invoked. They then keep running for the rest of the session, on later turns too. `once: true` on a hook, which is honored only in skill frontmatter, removes it after its first successful run.

When you audit:
- Flag a hook written as if it ends with the skill's task. It keeps running for the rest of the session, and `once: true`, which removes it after its first successful run, is the only documented way to stop it sooner.
- Check the structure: event name, then a list of `matcher` and `hooks` entries, each with a `type`, as in settings.

### 2.10 `context`, `agent`, `background`: valid values

These three are Claude Code only. `context` takes one value, `fork`. `agent` names the subagent type for a fork: `Explore`, `Plan`, `general-purpose` (the default) or a custom agent from `.claude/agents/`. `background` is a boolean that defaults to `true`.

When you audit:
- Flag a `context` value other than `fork`.
- Flag `agent` or `background` without `context: fork`. Both apply only to a fork, so either one is excess there.
- Flag an `agent` value that names no built-in type and no agent you can find in `.claude/agents/` or in the plugin.

### 2.11 `license`, `compatibility`, `metadata`

These are spec fields, valid on every surface. Claude Code accepts them and doesn't act on them, so each serves people or tools, not behavior.
- `license`: a license name or the name of a bundled license file, kept short (`Apache-2.0`, `Proprietary. LICENSE.txt has complete terms`).
- `compatibility`: environment requirements, such as the intended product, system packages or network access (`Requires git, docker, jq, and access to the internet`). It has a length limit. Most skills don't need it.
- `metadata`: a map of string keys to string values for properties the spec doesn't define, such as `author` and `version`. Clients and your own tooling read it.

When you audit:
- Recommend `license` on a skill distributed to others under terms. Check that the named file exists in the skill when it names one. INFERENCE: the spec defines the field but not when it is needed.
- Recommend `compatibility` when the skill truly needs something its environments may lack: a Claude Code-only feature, a binary on `PATH`, network access. That includes Skills API containers, which have no network access and no package installation at run time. Flag it when it restates what every environment has, or when it carries instructions that belong in the body.
- Flag `metadata` that is not a string-to-string map (1.3, 1.4). Recommend reasonably unique key names. Flag `metadata` that nothing reads as excess.

## 3. The name

### 3.1 Whether to write `name`, and the directory match

The spec and every upload surface require `name`. The spec, claude.ai packaging and the help center all require it to match the skill's directory name. Claude Code makes `name` optional and defaults to the directory name. In a personal or project skill, a `name` that differs from the folder sets the command shown in the `/` menu, and the folder name still invokes the skill. Since v2.1.290, the listing shows both names. In a plugin, `name` replaces the last segment of `/plugin:name`. The Skills API no longer requires a top-level folder named after the skill, but each new version's `name` must equal the skill's existing name.

When you audit:
- On a skill for the spec or claude.ai, flag a missing `name` and any mismatch with the directory as an error.
- On a Claude Code skill without `name`, recommend writing it equal to the folder name. It costs nothing and keeps the skill valid for upload, since Claude Code accepts all six spec fields.
- Flag a Claude Code `name` that differs from its folder unless the difference is deliberate: a different command than the folder, accepted knowingly as non-portable. Otherwise the skill answers to two names, and an upload fails.
- On a Skills API skill, flag a `name` change between versions.

### 3.2 Format rules

The spec sets the strictest format:
- Lowercase letters `a-z`, digits `0-9` and hyphens only.
- No hyphen at the start or end, and no `--`.
- A maximum length.

The platform pages and the Skills API add: no XML tags, and no reserved words `anthropic` or `claude`. Claude Code's documentation states no lowercase rule. It refuses a `name` or folder name that contains a zero-width space or control character, a private-use or unassigned character, a character that changes text direction, `<` or `>`, or any blank other than one plain space between words. A refused frontmatter `name` is ignored: the `/` menu doesn't show it and typing it doesn't invoke the skill. A refused folder name stops a non-plugin skill from loading. In a plugin's `skills/` folder, those characters become hyphens in the command name.

When you audit:
- Check the name against the spec's format whatever the target. A name that meets it is valid everywhere. Flag uppercase letters, underscores, spaces, dots and leading, trailing or doubled hyphens.
- Flag any character in the refused list as an error on every surface.
- Flag `anthropic` or `claude` anywhere in the name of a skill that is or may be uploaded to claude.ai or the Skills API. Upload rejects it, even though Claude Code loads it.

Recognize the difference:
- `processing-pdfs` is valid on every surface.
- `Processing_PDFs`, `pdf--tools` and `claude-pdf-helper` each fail the spec or an upload. The last one still loads in Claude Code.

### 3.3 Reserved names

Claude Code reserves the name `anthropic-skills`, and every name in that namespace such as `anthropic-skills:pdf`, for skills synced from claude.ai. A skill folder, a frontmatter `name` or a command file with such a name doesn't load outside a plugin. Claude Code also skips a skill folder named `synced`, in any capitalization, in the enterprise, personal and project locations. The spec and API reserve `anthropic` and `claude` as words (3.2).

When you audit:
- Flag a non-plugin skill whose folder or `name` is `anthropic-skills` or starts with `anthropic-skills:`. It doesn't load.
- Flag a skill folder named `synced` in any capitalization.

### 3.4 Naming quality and consistency

Claude reads the name alongside the description when it decides whether to trigger a skill, and in Claude Code the user types the name as a command. A name should therefore say what the skill does. The platform suggests the gerund, verb + -ing (`processing-pdfs`, `analyzing-spreadsheets`). Noun phrases (`pdf-processing`) and action forms (`process-pdfs`) are acceptable alternatives. Avoid vague names (`helper`, `utils`, `tools`), names so generic they could fit anything (`documents`, `data`, `files`), and naming patterns that change within one collection.

When you audit:
- Flag a vague or generic name. Recommend one that names the activity and its object, drawn from what the skill does.
- Flag a name that promises something different from what the description and body do. Claude uses both when deciding.
- When the skill belongs to a set (a plugin, a skills folder), compare its form with its siblings' forms. Flag the odd one out, such as `pdf-processing` beside `analyzing-spreadsheets` and `managing-databases`, and recommend the pattern the set already uses. Don't impose the gerund on a set that consistently uses another accepted form.
- Treat the gerund as a recommendation, never as a validity rule. Report a non-gerund name that is clear and consistent as present and optimal.

---

## 4. The description

### 4.1 The description is the router

Before Claude decides whether to load a skill, it has only the skill's name and description. The body, its references and its scripts reach Claude only after that decision. Claude matches the user's request against the descriptions of every skill it can see, possibly a hundred or more, and picks the ones that fit. So the description is a router, not a summary or a title. If it doesn't match the request, a skill with an excellent body never runs. If it matches the wrong requests, its instructions load where they don't belong. A skill that installs and loads proves nothing about how it routes.

When you audit:

- Read the description without the body and ask: from this text alone, would Claude pick the skill for the tasks the body serves and pass it over for everything else? Judge it on that question only.
- Flag use conditions that appear only in the body, such as a "When to apply" section with no matching conditions in the description: present but wrong. Claude reads that section only after it has already chosen the skill. Recommend moving the conditions into the description.
- When the skill sets `disable-model-invocation: true`, the description is not in Claude's context and routes nothing. Don't fault it for missing triggers. Judge it only as the text a user reads when picking the command.
- Where only a run can settle whether the description routes correctly, name the check: realistic requests that should and should not load the skill, each run in a fresh session.

### 4.2 What it must say: the capabilities and the user's intent

The description must say what the skill does and when to use it. The "what" names concrete capabilities: the operations, inputs and outputs. The "when" describes situations as the user's goal, not as the skill's internal mechanics. Claude needs the "what" to tell this skill apart from its neighbors, and the "when" to know that the current request calls for it. Implementation details such as libraries, script names, internal steps and runtime prerequisites match nothing a user asks for, and they take the place of the intents that should trigger the skill.

When you audit:

- Flag a description that states capabilities or a topic but no condition of use: present but wrong. Both the standard and the platform require what and when.
- Flag a description that states only a condition, such as "Use when working with data", with no capabilities: present but wrong. Claude can't tell which of several data skills it is.
- Flag implementation mechanics that fill the description in place of intents: present but wrong. Recommend moving them to the body, and environment requirements to `compatibility`.
- Don't impose one template or order. A description can open with "Use when…" or with the capabilities, and can end with a "Not for…" clause or have none. It meets the sources when what and when are both there and clear.

Recognize the difference:

- Mechanics: `Runs scripts/fill.py with pypdf to write values into AcroForm fields.`
- Intent: `Fills in PDF forms from data the user provides. Use when the user wants to complete, populate or answer a PDF form or application.`

### 4.3 Point of view

Write the description in the third person. It is injected into the system prompt, and a point of view that shifts there can cause discovery problems: a description written as "I can…" or "You can use this to…" speaks in a voice that doesn't match the rest of the prompt.

When you audit:

- Flag first person ("I can help…", "We provide…") and second person addressed to the user ("You can use this to…"): present but wrong. Recommend the third-person form ("Processes…", "Generates…").
- Don't flag a "Use when…" or "Use this skill when…" clause. The platform's own examples use it, and the Agent Skills guidance recommends that imperative framing because Claude is deciding whether to act. It is compatible with a third-person "what".
- Don't flag a capability list in the bare verb form ("Extract text and tables…") as a change of point of view. The platform's own examples use it.

Recognize the difference:

- Consistent: `Processes Excel files and generates reports.`
- Shifted: `I can help you process Excel files.` or `You can use this to process Excel files.`

### 4.4 Wording users actually type

Claude compares the user's words with the description's words. A description written in the author's vocabulary, with internal terms, coined names or abstract categories, misses requests phrased the way people actually ask. It needs the terms a request for the task would contain: file types and extensions, product and tool names, everyday verbs. It also needs the contexts where the user describes the need without naming the domain at all ("my boss wants a chart from this data file"), listed explicitly. The opposite mistake is overfitting: copying exact phrases from particular test requests makes the description fit those phrasings and miss new ones. The fix is the general category those phrases share.

When you audit:

- For each job the body does, ask what a user would type to get it, then check that the description holds those terms or their category. Flag missing user terms as absent and needed, for example a description that says "tabular data" for users who say "spreadsheet", "CSV" or ".xlsx".
- Flag descriptions built on the author's own terms (project codenames, the skill's coined names, internal process labels) that users wouldn't type: present but improvable.
- Ask whether the skill serves requests that never name its domain. If it does and the description doesn't cover them (for example, "even if they don't mention CSV or analysis"), flag absent and needed.
- Accept short quoted trigger phrases that many users would type for the skill's job, such as `asks for "design specs" or "component documentation"`: the official guide shows them in its good examples. Flag phrases copied from particular test requests or one-off prompts: present but improvable, because they are overfit and miss new phrasings. Recommend the category they represent.
- Where only a run can show whether real phrasing triggers the skill, name the check: requests that describe the need without naming the domain.

Recognize the difference:

- Author's terms only: `Analyzes tabular datasets.`
- User's terms and unnamed-domain requests: `Analyzes CSV and tabular data files: computes summary statistics, adds derived columns, generates charts and cleans messy data. Use when the user has a CSV, TSV or Excel file and wants to explore, transform or visualize the data, even if they don't mention "CSV" or "analysis".`

### 4.5 Scope boundaries for plausible near-misses

A near-miss is a request that shares keywords or concepts with the skill but needs something else: a different operation, a different format or another skill. A description that is only broad will catch near-misses, so Claude loads instructions that don't fit the task. When a plausible near-miss exists, the description has to separate it, either by sharpening what the skill does or by stating what it doesn't do and where its boundary with the neighboring capability lies. A boundary against requests nobody would confuse with the skill changes no routing decision.

When you audit:

- Build the plausible near-misses from the description's own keywords: requests that use its nouns but need a different action, a different format or another skill's job. Ask whether the description, read alone, keeps each one out.
- Flag absent and needed when a plausible near-miss exists and nothing in the description separates it, neither a sharper what and when nor an explicit exclusion.
- Flag excess when an exclusion names tasks that share no keyword or concept with the skill. It separates nothing.
- When the near-miss belongs to a known neighboring skill, recommend a boundary that states the neighbor's territory in the user's terms, not only a "Not for…" on one keyword.
- Flag an exclusion that copies the wording of one particular request: present but improvable, because it is overfit. Recommend the category of request it stands for.

Recognize the difference (for a CSV analysis skill):

- Needed: `Not for editing Excel formulas or loading CSV rows into a database.` Both share "spreadsheet" or "CSV" with the skill.
- Excess: `Not for writing Fibonacci functions or checking the weather.` Nothing in them could be confused with the skill.

### 4.6 Vague versus specific

A vague description fails both ways. If it is too narrow or abstract, the skill doesn't trigger when it should. If it is too broad, the skill triggers when it shouldn't and competes with unrelated skills. A specific description names concrete operations and inputs and the situations that call for them, so Claude can match it to a request and tell it apart from other skills. Specific doesn't mean stuffed with keywords. It means every claim is concrete and matches what the body actually does.

When you audit:

- Flag a description that names only a domain or a generic verb ("Helps with documents", "Processes data", "Does stuff with files"): present but wrong.
- Ask whether the same words could describe a different skill. If they could, the description is too vague to route.
- Compare the description's scope with the body's. Flag a description that promises jobs the body doesn't do: present but wrong, because Claude will load the skill for tasks it can't serve. Flag a body that handles jobs the description never mentions: absent and needed, because Claude will never route those requests to it.
- Flag claims to a whole domain when the skill covers only part of it ("Handles all spreadsheet work" for a skill that only analyzes CSV files): present but wrong.

Recognize the difference:

- Vague: `Helps with PDFs.`
- Specific: `Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.`

### 4.7 XML tags and angle brackets

On claude.ai, in the Skills API and in the platform's field requirements, a description cannot contain XML tags. Enabling a personal skill for a claude.ai account is an upload, so the same requirement applies to skills meant for Cowork and cloud sessions. Claude Code accepts angle brackets but escapes them: `<` and `>` in `description` and `when_to_use` show as `&lt;` and `&gt;`, so the text can't imitate Claude Code's internal formatting. A placeholder written as `<branch>` therefore reaches Claude as `&lt;branch&gt;` in Claude Code, and on the other surfaces it reads as a tag the description is not allowed to hold.

When you audit:

- Flag any XML-style tag, an angle-bracket placeholder (`<file>`, `<branch>`) included, in the description of a skill that is uploaded to claude.ai, sent to the Skills API or enabled on a claude.ai account: present but wrong.
- In a skill served only by Claude Code, flag an angle-bracket placeholder in `description` or `when_to_use` as present but improvable, because Claude reads it escaped. On any surface, recommend square brackets (`[branch]`), which show as typed, or plain words ("a branch name").
- For a skill served only by Claude Code that takes arguments, `argument-hint` is the other place for a placeholder. Never recommend it for a skill served anywhere else (2.1).
- Flag symbols built from angle brackets, such as arrows (`->`, `=>`) or comparisons (`<`, `>`): present but improvable, because Claude Code escapes them too. Recommend writing them in words.

Recognize the difference:

- Escaped or rejected: `Use when the user asks to deploy <branch> to staging.`
- Shows as written: `Use when the user asks to deploy a branch to staging.` or `Use when the user asks to deploy [branch] to staging.`

### 4.8 `when_to_use`

`when_to_use` is a Claude Code field for additional context on when Claude should invoke the skill, such as trigger phrases or example requests. Claude Code appends it to the description in the skill listing, so Claude reads the two as one text. It is a Claude Code-only field (2.1), and the only frontmatter field spelled with underscores (1.5).

When you audit:

- On a skill served anywhere besides Claude Code (claude.ai, the Skills API, a claude.ai account for Cowork or cloud sessions, other Agent Skills clients), flag `when_to_use` as present but wrong. Recommend moving its content into `description`, because on those surfaces the triggers have to be in the description.
- On a skill served only by Claude Code, rate `when_to_use` present and optimal when it holds trigger phrases or example requests that would otherwise crowd the description and bury what the skill does. Rate it absent and not needed when the description already carries the conditions clearly. Don't recommend it for its own sake.
- Flag a misspelled key (`when-to-use`, `whenToUse`, `when_to_Use`): present but wrong. Claude Code ignores it silently, so its triggers never reach Claude.
- Flag text repeated in both fields as excess, and conditions in one field that contradict the other as present but wrong.

### 4.9 Descriptions across a set of skills

Claude chooses among every description it can see, so a skill's description has to be judged against its siblings in the same plugin or set, not on its own. Skills compose: Claude can use several in one task, and that is intended when each does a different part of the work. It is a defect when two descriptions claim the same request for different or conflicting work. Then Claude picks one of them unpredictably, or loads both and gets conflicting instructions. A skill scoped too broadly also becomes hard to activate precisely, and its description pulls in requests that belong to narrower siblings. Each description has to make its own territory recognizable and mark the border where a sibling is the plausible near-miss.

When you audit:

- Read all sibling descriptions side by side before you rate any one of them.
- For each pair, ask which request both would claim. If one request fits both and the skills would do different or conflicting work with it, flag both descriptions as present but wrong. Recommend that each state what separates it (the input, the stage of the work, the target, the outcome), with a boundary that sends the other request to its sibling.
- Don't flag overlap between skills meant to load together for one task, such as a brand-guidelines skill and a document-creation skill. Each does a different part of the work.
- Flag an umbrella description that covers its siblings' territory ("Use for any work on X" beside narrower X skills): present but wrong. It takes their requests.
- Flag sibling descriptions that restate the plugin's overall purpose instead of their own job: present but wrong. The plugin name can't separate them either: Claude Code adds it to every sibling's description alike.
- Where only a run can settle which sibling loads, name the check: each sibling's near-misses run with every sibling installed, recording which skill loads.

Recognize the difference (two skills in one GitHub plugin):

- Competing: both say `Use when the user asks for a code review.`
- Separated: one says `Reviews an open pull request on GitHub, its checks and review threads. Use when the user names a PR or asks why one is blocked.` The other says `Reviews the uncommitted changes in the working tree before a commit. Use when the user asks to check their diff or local changes. Not for pull requests already on GitHub.`

---

## 5. Activation and trigger tests

### 5.1 What automatic activation depends on

Before a skill loads, Claude has only its `name` and `description`; when a request matches the description, Claude reads the full `SKILL.md`. That match is the whole of automatic activation, so the only evidence that it works is a request Claude was not told to route, followed by Claude loading the skill on its own. Two fields change what can be tested: with `disable-model-invocation: true` the description is not in Claude's context and Claude cannot invoke the skill on its own, so there is no automatic activation to test; with `paths` set, Claude loads the skill automatically only while working with files that match the patterns inside its current working directory, so a request without such files cannot trigger it whatever the description says. Activation also proves only that Claude found the skill, not that the skill did what was intended: activation and output quality are measured separately.

When you audit:

- Judge every activation claim the skill or its documentation makes ("triggers on…", "Claude uses this when…") against this model, and flag a claim that rests on typing `/name`, on the skill appearing in a list, or on it installing cleanly: none of these shows Claude choosing the skill.
- Flag trigger tests for automatic activation on a skill with `disable-model-invocation: true`; they can only fail, or pass for the wrong reason.
- For a skill with `paths`, ask whether each should-trigger test gives Claude a matching file to work with, and flag one that does not.
- Flag a test set or a claim that treats "the skill triggered" as "the skill works", or "the output was good" as "the skill triggered".

Recognize the difference:

- Not evidence: "Tested: `/pdf-forms` runs and fills the sample form."
- Evidence: "In a fresh session, 'can you fill in the W-9 in ~/Downloads with my details from the last invoice' loaded `pdf-forms` in 3 of 3 runs."

### 5.2 Whether the skill targets tasks Claude needs it for

Claude consults skills for tasks that need knowledge or capabilities beyond what it handles alone. A simple, one-step request it can do with its basic tools, such as "read this PDF", may not trigger a skill even when the description matches it perfectly. Descriptions make the difference on tasks that involve specialized knowledge: an unfamiliar API, a domain-specific workflow, an uncommon format. A skill whose description aims at what Claude already does unaided will trigger unreliably, and if Claude handles the whole task well without it, the skill may add nothing. Scope matters too: a skill scoped too broadly is hard to activate precisely, and one scoped too narrowly forces several skills to load for one task.

When you audit:

- Ask what the skill gives Claude that it lacks for the tasks the description names. If the description leads with or consists of simple one-step requests, flag it as present but improvable and recommend wording that names the harder tasks the skill exists for: the specific API, workflow, format or project convention.
- Flag a skill whose description names only tasks Claude does well alone and whose purpose adds nothing to them; recommend that its value be shown by a run with and without the skill before it ships.
- Flag a description that spans several unrelated jobs (for example querying a database and administering it), because it cannot be activated precisely; recommend splitting it into coherent units, each with its own description.
- Do not count a should-trigger test that fails on a simple one-step request as proof that the description is wrong; judge the description on the requests that need the skill's knowledge.

### 5.3 What kind of test the skill ships

Three formats appear next to skills, and only some of their cases test activation. Trigger-query sets (for example `eval_queries.json`) pair a realistic `query` with `should_trigger: true` or `false`; a run passes when the skill was or was not loaded as labeled. Output evals in skill-creator's `evals/evals.json` (`prompt`, `expected_output`, `files`, `assertions`) test what the skill produces, and their runs hand the agent the skill, so they say nothing about whether Claude would choose it. Plugin eval suites for `claude plugin eval` (a case directory holding `prompt.md` and `graders/*.md`, or `case.yaml`) test activation only through a `tool_used` grader on the `Skill` tool. skill-creator and `claude plugin eval` do not read each other's files.

When you audit:

- Identify the format from the files before judging anything, and flag any file that mixes the formats' fields, because neither tool reads the other's cases.
- Flag a skill that offers output evals alone as evidence of activation; record activation tests as absent and judge under 5.6 whether they are needed.
- In a plugin eval case meant to test activation, flag it when no grader has `type: tool_used` with `tool: Skill`.
- In a plugin eval case, flag an `allowed_tools` list that lacks `Skill`: a run allows only the read-only tools the case lists, so Claude cannot invoke any skill, every should-trigger case fails and every should-not-trigger case passes without testing anything.
- Flag a case with no grader at all; it fails to load.

### 5.4 Judging the queries

A trigger test is only as good as its queries. Should-trigger queries test whether the description covers the skill's scope; they earn their place when the skill would help but the link is not obvious from the wording, because a query that asks for exactly what the skill does triggers with almost any description. Should-not-trigger queries test precision; the valuable ones are near-misses that share keywords or concepts with the skill but need something else, while obviously unrelated queries test nothing. Real requests carry file paths, personal context, specific names and values, casual wording and typos; generic queries do not exercise the description the way real use will.

When you audit:

- Flag a set that has only should-trigger or only should-not-trigger queries, and one heavily lopsided; the reference set is about 20 queries, 8 to 10 of each.
- Check that should-trigger queries vary in phrasing (formal, casual, with typos or abbreviations), in explicitness (some name the domain, others only describe the need), in detail (terse and context-heavy) and in complexity (single steps and the skill's task buried in a longer chain). Flag a set where every query uses the description's own keywords.
- Flag should-not-trigger queries with no keyword or concept overlap with the skill, and recommend near-misses in their place: requests from the adjacent capabilities the description must be told apart from.
- Flag a query that names the skill or starts with `/name`; it tests direct invocation, not the description.
- Flag a query too vague to test anything ("process this data") and recommend a realistic rewrite with a path, context and specifics.
- Check each label: flag a should-trigger query that is really a simple one-step task Claude handles alone (per 5.2), and a should-not-trigger query that the skill's own purpose covers.

### 5.5 Judging how the tests were run and used

Triggering is nondeterministic: the same query can trigger on one run and not the next. A trustworthy result runs each query several times (three is the usual starting point) and judges its trigger rate against a threshold (0.5 by default): above it for should-trigger, below it for should-not-trigger. `claude plugin eval` runs each case three times by default, and a single run is noisy. When the description was tuned against the queries, the queries also become a trap: wording fitted to them can pass them and fail new requests. The guard is a train set (about 60%) that drives changes and a validation set (about 40%), with a proportional mix of both labels, kept fixed and used only to pick the best iteration, which may not be the last one. Fixes must address the category of request a failure represents, never copy its words.

When you audit:

- Flag a trigger result or pass claim based on one run per query, including `runs: 1` in a plugin eval case or a `--runs 1` result offered as final.
- If the description was tuned, ask whether the queries were split into train and validation sets; flag a tuned description with no held-out queries, and recommend 5 to 10 fresh mixed queries as a final check.
- Compare the description's wording with the queries': flag distinctive words, file names, column names or phrases that appear in a query and in the description but not in the skill's real scope, as overfitting, and recommend the general category they stand for.
- In a plugin eval suite, check that the `tool_used` grader's `input_match` matches the name Claude invokes the skill by, with the optional `plugin-name:` prefix (for example `'"skill"\s*:\s*"(?:[\w-]+:)?pdf-forms"'`); flag a pattern that names another skill or only one of the two forms.
- In a plugin eval suite, flag a should-not-trigger case whose `Skill` grader lacks `min: 0`, `max: 0` and `arm: both`. In a two-arm run, `tool_used` graders on `Skill` are excluded from the score unless `arm: both` is set, so without it the check does not count.
- Flag a should-trigger plugin eval case judged only by `Δ`: its `Skill` grader is a pass/fail indicator outside the score, so read the indicator, and recommend pairing it with one grader on the result.
- Ask whether each run started in a fresh session; leftover context from writing the skill masks gaps.
- If the skill targets several models, ask whether the tests ran on each of them, because how a skill performs depends on the model.
- Where only a run would settle whether the description triggers (a near-miss you cannot call by reading), name the run: the query, the expected label, and three runs.

### 5.6 Recommending trigger tests when none ship

A skill that relies on Claude choosing it needs trigger tests; the sources treat the description as the one text that decides activation and give no way to confirm it except running realistic requests. A skill Claude cannot invoke on its own does not. When tests are needed and absent, recommend them as complete files written from the skill's purpose and description, so the author can run them unchanged.

When you audit:

- Record trigger tests as absent and not needed when `disable-model-invocation: true` is set. Record them as absent and needed when Claude can invoke the skill (the default, and with `user-invocable: false`), and raise their priority when the skill has close neighbors that share its keywords or a broad description.
- Recommend the format that matches how the skill ships: a plugin eval suite for a skill in a plugin, a trigger-query file for a standalone skill.
- Write the queries yourself: 8 to 10 should-trigger, varied along the four axes in 5.4 and at least half of them not naming the domain; 8 to 10 should-not-trigger near-misses drawn from the adjacent capabilities, each realistic per 5.4. If the description will be tuned, also propose the train and validation split.
- For a skill with `paths`, include a matching file in every should-trigger case (in a plugin eval case, through a `case.yaml` `context.scaffold_script`, which runs only with `--scaffold`).
- Name the check that settles each: three runs per query, trigger rate against 0.5.

For a standalone skill, recommend `eval_queries.json`, each entry in this shape:

```json
[
  { "query": "<realistic request the skill should handle, not naming the skill>", "should_trigger": true },
  { "query": "<near-miss that shares the skill's keywords but needs something else>", "should_trigger": false }
]
```

For a plugin skill, recommend one case directory per query. A should-trigger case:

`evals/<case-name>/prompt.md`

```markdown
---
allowed_tools: [Read, Glob, Grep, Skill]
---

<realistic request, with the context the task needs; the workspace starts empty>
```

`evals/<case-name>/graders/skill-fired.md`

```markdown
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?<skill-name>"'
---
```

`evals/<case-name>/graders/result.md`

```markdown
---
type: llm
---

PASS if <what a correct result contains, from the skill's purpose>.
FAIL if <what a wrong or missing result looks like>.
```

A should-not-trigger case uses the same `prompt.md` shape with the near-miss request, and this grader:

`evals/<case-name>/graders/skill-not-fired.md`

```markdown
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?<skill-name>"'
min: 0
max: 0
arm: both
---
```

---

## Classifying findings

Give every finding four things: the exact file and line(s) in the skill under audit, or where a missing field or clause belongs; the point in this file it violates or falls short of; why it is a defect, stated as its consequence on a named surface or on Claude's choice of the skill; and a specific fix, written out, with the reason it's the right one.

Classify each defect into one of four levels by its actual consequence. The examples anchor each level; a finding that doesn't match one verbatim still gets the level its own consequence earns.

- **Critical.** The skill is rejected, doesn't load, or can never be chosen on a target it is meant for. For example: frontmatter that doesn't open on line 1; a Claude Code-only field in a skill that is uploaded; a reserved or refused name; a missing `description` on an upload target; frontmatter that doesn't parse.
- **High.** The skill loads, but Claude chooses it wrongly, or a field does the opposite of what the author meant. For example: a side-effect skill with no `disable-model-invocation: true`; `user-invocable: false` relied on to keep Claude away; a description with no condition of use, or one that claims a sibling's requests; use conditions only in the body; a misspelled field that silently does nothing; a trigger test that can't fail.
- **Medium.** Valid and routed, but less precise or less consistent than it should be. For example: a description in the author's terms instead of the user's; a needed near-miss boundary that is missing, or one that separates nothing; a field set with no reason the skill shows; a name that breaks its set's pattern; a trigger set without near-misses or judged on one run.
- **Low.** A minor weakness with no real consequence. For example: an unquoted value that every parser the skill meets accepts; a vague but harmless `metadata` key.

Tie-breaks:

- If a finding fits two levels, the higher level wins.
- A field, boundary or test the skill doesn't need is Medium at most, unless it makes the skill act wrongly.
- A surface the skill doesn't target gets no finding. A possible target, one the skill might reach without naming it, gets Medium at most.
- When the consequence differs by target, set the severity of the most affected target, and name each affected target with its consequence in the finding.
- When several defects share one root cause, report the root cause once and list every location.
- Never invent impact, never inflate a severity to make the report look decisive, and never lower one because Claude might choose correctly anyway.

## Improvement opportunities

Separate improvement opportunities from defects: an opportunity is something the skill's purpose needs and its frontmatter, name or description lacks, or something that works and a stronger version from this file would improve, such as user wording the description misses, a boundary for a near-miss, a clearer name, or trigger tests the skill should ship. Report every one that genuinely applies to this skill; this section may stay empty only when nothing does. For each one, give what exists now (or that it is absent, and where it belongs), the exact text written out in full, and why it is better for this skill.

This file gives you the criteria, the context to establish, and the severity model. The gotchas and the verification checklist live in your own instructions, and the report template lives in this skill's `assets/` folder, so they aren't repeated here.

## Delivering the report

Deliver every defect and improvement opportunity in the shared findings template, `assets/audit-report.md` in this skill. Fill one defect block per defect, with every field, and keep the template's structure exactly. Defects with one root cause are one defect: give its first location in File and Lines, and list every other location, as `path:lines`, in Finding.
