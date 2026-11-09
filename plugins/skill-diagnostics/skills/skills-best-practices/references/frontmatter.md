# Frontmatter

The fields of `SKILL.md` frontmatter on each surface, how they parse, and the combinations that disable a skill.

## Contents

- [Fields by surface](#fields-by-surface)
- [The name](#the-name)
- [How Claude Code reads frontmatter](#how-claude-code-reads-frontmatter)
- [Strict YAML traps](#strict-yaml-traps)
- [Combinations that disable a skill](#combinations-that-disable-a-skill)

## Fields by surface

Only the six fields of the open standard work on every surface; Claude Code accepts more, and claude.ai uploads, the Skills API and `package_skill.py` reject any other field with a hard error ("Unexpected key(s) in SKILL.md frontmatter") \[CC\]. Enabling a personal skill on your claude.ai account is such an upload \[CC\].

| Field | Open standard \[AS\] | Claude API / claude.ai \[PL\]\[CC\] | Claude Code \[CC\] |
| --- | --- | --- | --- |
| `name` | Required. 1–64 chars, `a-z`, `0-9`, `-`; no leading, trailing or double hyphen; must match the folder name | Required. Max 64 chars, lowercase letters, numbers and hyphens; no XML tags; no reserved words `anthropic` or `claude` | Optional; defaults to the folder name and sets the `/` command. Folders named `synced` or `anthropic-skills` don't load; names with `<`, `>`, control or zero-width characters are refused |
| `description` | Required. 1–1,024 chars; what it does and when to use it, with keywords | Required. Non-empty, max 1,024 chars, no XML tags | Recommended. If missing, the first body line is used. `description` + `when_to_use` are cut at 1,536 chars in the listing; `<` and `>` show as `&lt;` `&gt;` |
| `license` | Optional, short | Allowed | Accepted, not acted on |
| `compatibility` | Optional, max 500 chars; only for real environment requirements | Allowed | Accepted, not acted on |
| `metadata` | Optional string-to-string map; use unique keys | Allowed | Free-form map for your own tooling; a value that isn't a map is dropped; don't reuse field names such as `paths` as keys |
| `allowed-tools` | Optional, space-separated, experimental | Allowed | Pre-approves the listed tools for the invoking turn only; does not restrict other tools |
| `when_to_use` | — | Rejected | Extra trigger text appended to the description |
| `argument-hint`, `arguments` | — | Rejected | Autocomplete hint; named positional arguments |
| `disable-model-invocation`, `user-invocable` | — | Rejected | Who may invoke the skill (see [claude-code-features.md](claude-code-features.md#invocation-control)) |
| `disallowed-tools` | — | Rejected | Removes tools while the skill is active |
| `model`, `effort` | — | Rejected | Model or effort for the rest of the turn |
| `context`, `agent`, `background` | — | Rejected | Run in a forked subagent |
| `hooks` | — | Rejected | Hooks registered when the skill is invoked |
| `paths` | — | Rejected | Glob patterns that limit automatic activation |
| `shell` | — | Rejected | `bash` (default) or `powershell` for injected commands |

## The name

The open standard requires `name` and says it must match the folder \[AS\]; the Platform requires it and forbids `anthropic` and `claude` \[PL\]; Claude Code makes it optional, defaults it to the folder name, lets it differ from the folder, and reserves the folder names `synced` and `anthropic-skills` \[CC\]. To pass every surface, match the folder name and avoid every reserved word.

## How Claude Code reads frontmatter

In Claude Code, frontmatter is read only when `---` is the file's first line, an unknown field is ignored silently, and YAML that doesn't parse loads the skill with no fields set \[CC\]. Check it with `claude plugin validate <dir>` \[CC\] or `skills-ref validate ./my-skill` \[AS\].

## Strict YAML traps

Claude Code reads more than strict YAML parsers do, and uploads, the API and other clients use strict ones \[SD\] `spec`. Quote or reword a plain value that:

- contains a colon followed by a space (`Use when: …` breaks; write `Use when the user …`);
- contains a space followed by `#`, which strict YAML reads as the start of a comment;
- starts with `[`, `{` or another YAML indicator, which turns it into a list or a map;
- reads as a boolean or null (`yes`, `no`, `on`, `off`, `null`).

**One plain line.** Write `description` as one plain line, and reword a sentence rather than quote it `default`.

## Combinations that disable a skill

\[CC\] `req`:

- **Nobody can run it.** `disable-model-invocation: true` with `user-invocable: false` leaves nobody able to run it: the first stops Claude, the second stops the user.
- **No preloading and no scheduled task.** `disable-model-invocation: true` also stops the skill from being preloaded into subagents and from running when a session-scoped scheduled task fires with it as its prompt, so don't set it on a skill an agent or a scheduled task needs.
- **`paths` on a skill Claude may not start.** `paths` limits only automatic activation, so it does nothing on a skill Claude may not start `default` \[SD\].
