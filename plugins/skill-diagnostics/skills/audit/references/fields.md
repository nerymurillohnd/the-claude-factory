# Skill fields and load-time behavior

Facts the conformance lens checks a skill against. Each line is labelled: **[req]** documented behavior, **[rec]** official recommendation, **[spec]** Agent Skills specification, **[default]** this plugin's recommended default (an alternative is acceptable when the skill states why), **[observed]** seen in testing but not documented.

Sources, checked 2026-10-11: [Claude Code skills](https://code.claude.com/docs/en/skills), [settings reference](https://code.claude.com/docs/en/settings-reference), [Agent Skills specification](https://agentskills.io/specification), [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [best practices for skill creators](https://agentskills.io/skill-creation/best-practices) (checked 2026-10-12). When a live page disagrees with this file, the live page wins: report the difference.

## Contents

- Frontmatter syntax
- Field reference
- Name
- Description
- Arguments and substitutions
- Body and loading
- Invocation control

## Frontmatter syntax

- [req] Claude Code reads frontmatter only when line 1 is `---`. Without it, the whole file is body text and the skill has no description.
- [req] Field names must match exactly; an unknown or misspelled field is ignored without any error (`disable_model_invocation` does nothing).
- [req] Boolean fields accept `true`/`false`, `yes`/`no`, `on`/`off`, `1`/`0`, in any letter case (Claude Code 2.1.218+).
- [spec] Other tools parse frontmatter as strict YAML. An unquoted value containing a colon followed by a space is invalid there; an unquoted value containing a space followed by `#` is cut at the `#`, because YAML reads the rest as a comment; a value starting with `[` or `{` becomes a list or a map.
- [default] Write `description` as one plain, unquoted line. Reword a sentence instead of quoting it (`Use when the user asks …`, not `Use when: …`). Quote only a value that cannot be reworded.

## Field reference

| Field | What it does in Claude Code |
| :-- | :-- |
| `name` | Name shown in the `/` menu; defaults to the directory name |
| `description` | What the skill does and when to use it; Claude decides from it. Missing: the first non-empty body line is used |
| `when_to_use` | Extra trigger phrases, appended to `description` in the listing |
| `argument-hint` | Autocomplete hint such as `[issue-number]` |
| `arguments` | Named positional arguments for `$name` placeholders (space-separated string or list) |
| `disable-model-invocation` | `true`: only the user can start the skill |
| `user-invocable` | `false`: only Claude can start it; hidden from the `/` menu |
| `allowed-tools` | Tools pre-approved for the turn that invokes the skill; the grant clears at the user's next message |
| `disallowed-tools` | Tools removed while the skill is active |
| `model` | Model for the rest of the current turn (`inherit` keeps the session's) |
| `effort` | `low`, `medium`, `high`, `xhigh` or `max` while the skill is active |
| `context` | `fork` runs the skill in a subagent |
| `agent` | Subagent type used with `context: fork` |
| `background` | With `context: fork`: `false` waits for the result in the invoking turn; default `true` (2.1.218+) |
| `hooks` | Hooks registered when the skill is invoked, kept for the rest of the session |
| `paths` | Globs that limit automatic activation to matching files |
| `shell` | `bash` (default) or `powershell` for dynamic-context commands |
| `metadata` | Free-form map for your own tooling; a value that is not a map is dropped |
| `license`, `compatibility` | Agent Skills fields Claude Code accepts and ignores; `compatibility` holds up to 500 characters |

All 20 fields are optional in Claude Code [req]. Set `name` and `description` anyway [default]: uploads and the specification require both, and the description is what makes the skill trigger.

## Name

- [spec] 1–64 characters; lowercase letters, digits and hyphens; no hyphen at the start or end; no two hyphens in a row; equal to the directory name.
- [req] claude.ai uploads and the Skills API also reject the words `anthropic` and `claude` in `name`. Claude Code accepts them: report it only for an upload or API target.
- [req] Claude Code never loads a skill whose directory is named `synced` (any capitalization), or whose directory or `name` is `anthropic-skills` or starts with `anthropic-skills:`; both are reserved for skills synced from claude.ai.
- [rec] Prefer a name that says the activity (`processing-invoices`) over a vague one (`helper`, `utils`).

## Description

- [rec] Third person, present tense: it is read as part of Claude's system prompt. "Formats invoices", not "I can format invoices".
- [rec] Say what the skill does, then when to use it, with the words a user would actually type.
- [req] Claude Code shows `description` + `when_to_use` in the skill listing and cuts the combined text at `skillListingMaxDescChars` characters (default 1,536; users can raise or lower it). Put the key use case first.
- [req] When the listing as a whole is over its budget (about 1% of the context window), Claude Code drops whole descriptions, starting with the least-used skills.
- [spec] Uploads and the Skills API reject a description over 1,024 characters or one containing angle-bracket tags.
- [default] Do not summarize the procedure in the description: Claude may follow the summary and never read the body.

## Arguments and substitutions

Claude Code replaces these in `SKILL.md` before Claude reads it [req]:

| Token | Becomes |
| :-- | :-- |
| `$ARGUMENTS` | Everything typed after the skill name |
| `$ARGUMENTS[N]`, `$N` | One argument, counted from 0 |
| `$name` | The argument named in `arguments` at that position |
| `${CLAUDE_SKILL_DIR}` | The directory holding this `SKILL.md` |
| `${CLAUDE_PROJECT_DIR}` | The project root |
| `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` | Plugin directory and its persistent data directory (plugin skills only) |
| `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}` | Session id; current effort level |

- [req] With no placeholder in the body, Claude Code appends the arguments as a final `ARGUMENTS: <value>` line.
- [req] Substitution happens everywhere in the body, code blocks included. A literal `$1.00` must be written `\$1.00`.
- [req] The path variables are also substituted in Bash rules of `allowed-tools`, so a bundled script can run without a prompt.
- [req] Built-in read-only commands (`ls`, `cat`, `head`, `grep`, `find`, `wc`, `diff`, `stat` and others) run without a prompt in every mode, so a skill needs no `allowed-tools` entry for them; they still prompt with an unquoted glob when the command has write-capable flags (`find`), or for paths a user's `blockReadsOutsideWorkingDirectories` covers ([permissions](https://code.claude.com/docs/en/permissions), Read-only commands).
- [observed] They are substituted in `Read(...)` rules too: `Read(/${CLAUDE_SKILL_DIR}/**)` lets the skill, and subagents it launches in the same turn, read the skill's own files without a prompt (Claude Code 2.1.296).
- [req] The variables are text substitutions, not environment variables: commands run through the Bash tool do not see them.

## Body and loading

- [req] The rendered skill enters the conversation once and stays; Claude Code does not re-read the file. Write rules that apply for the whole task, not one-time steps.
- [req] After auto-compaction, Claude Code re-attaches each invoked skill's first 5,000 tokens (25,000 for all skills together). Critical rules belong near the top.
- [rec] Keep the body under 500 lines; move detail to files that `SKILL.md` links with when to read them.
- [spec] Aim for under about 5,000 tokens of body.
- [rec] Link every supporting file from `SKILL.md`, one level deep; a reference that links to another may be read only partially. Open references longer than 100 lines with a contents list.
- [req] A line starting with `!` and a backticked command (or a block opened with three backticks and `!`) runs before Claude reads the skill; its output replaces the line. A non-zero exit, or a permission result other than allow outside auto mode, aborts the whole skill.

## Invocation control

| Want | Set | Effect [req] |
| :-- | :-- | :-- |
| Claude and the user can start it | nothing | Description listed; body loads when invoked |
| Only the user | `disable-model-invocation: true` | Description not listed; cannot be preloaded into a subagent or run by a scheduled task |
| Only Claude | `user-invocable: false` | Hidden from the `/` menu; typing `/name` does not run it |

- [req] Setting both `disable-model-invocation: true` and `user-invocable: false` leaves nobody able to run the skill.
- [req] A plugin skill runs as `/<plugin>:<skill>`.
