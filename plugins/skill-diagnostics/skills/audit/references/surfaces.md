# Where a skill runs

What changes for a skill on each surface. The conformance lens uses this to judge portability; the checker's `--target` option applies the same rules. Labels as in `fields.md`: **[req]**, **[rec]**, **[spec]**, **[default]**, **[observed]**.

Sources, checked 2026-10-11: [Claude Code skills](https://code.claude.com/docs/en/skills) (Where skills live, Skills in Cowork and cloud sessions, Using skill frontmatter outside Claude Code), [plugin platform support](https://claude.com/docs/plugins/platform-support), [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) (Runtime environment, Package dependencies).

## Contents

- Pick the target
- What each surface accepts
- How a skill reaches each surface
- Scripts and dependencies
- Portability findings

## Pick the target

The first row that matches wins.

| The skill is | Target | Checker option |
| :-- | :-- | :-- |
| A synced copy of an account skill (`~/.claude/skills/synced/`) | claude.ai upload; fixes are made on claude.ai, since a sync overwrites local edits | `--target upload` |
| Uploaded to claude.ai, or enabled on the account so it reaches Cowork and cloud sessions | claude.ai upload | `--target upload` |
| Inside a plugin (an ancestor folder holds `.claude-plugin/plugin.json`) | Claude Code and Cowork | `--target code` and `--target cowork`, one run each |
| Personal (`~/.claude/skills/`) or project (`.claude/skills/`) | Claude Code | `--target code` (default) |
| Sent through the Skills API | API | `--target api` |
| Anywhere else (a loose folder, a `skills/` folder outside `.claude/`) | Claude Code | `--target code`, stated as assumed |

Without `--target`, the three location rules in `SKILL.md` (Input → Target) decide; the other rows apply when the request names that surface. Say which targets you assumed. A plugin installs in both Claude Code and Cowork, so its skills are checked for both unless the request names one.

## What each surface accepts

| Feature | Claude Code | Cowork (plugin) | claude.ai upload | Skills API |
| :-- | :--: | :--: | :--: | :--: |
| All 20 frontmatter fields | ✅ | ✅ | ❌ hard error | ❌ hard error |
| Only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` | ✅ | ✅ | ✅ | ✅ |
| `description` over 1,024 characters | ⚠️ cut in the listing at 1,536 by default | ⚠️ | ❌ | ❌ |
| `anthropic` or `claude` in `name` | ✅ | ✅ | ❌ | ❌ |
| `!` dynamic-context lines | ✅ run at load | ⚠️ replaced by a placeholder | ❌ never run | ❌ never run |
| `${CLAUDE_*}` path variables | ✅ | ✅ | ⚠️ substituted where Claude Code runs it (Cowork, cloud and local sessions); not documented elsewhere | ⚠️ not documented |
| Bundled scripts | ✅ | ✅ | ✅ through the interpreter | ✅ no network |

- [req] Uploads and the Skills API fail with `Unexpected key(s) in SKILL.md frontmatter` for any field outside the six. A skill meant for both Claude Code and an upload keeps to the six fields, or ships two versions.
- [req] Synced skills: in a cloud session the body behaves like a local skill. In any other local Claude Code session, a synced skill does not run `!` lines, does not attach `@` files, and leaves `${CLAUDE_PROJECT_DIR}` and `${CLAUDE_SESSION_ID}` as literal text.
- [req] In a Cowork session on the desktop, Claude Code replaces every `!` line with a placeholder, for every skill.

## How a skill reaches each surface

- [req] Personal skills in `~/.claude/skills/` load only on that machine: not in Cowork, cloud sessions or routines.
- [req] Cowork sessions load the skills enabled on the claude.ai account (synced when the session starts) and the skills of installed plugins.
- [req] Cloud sessions also load project skills committed to the repository's `.claude/skills/`.
- [req] Enabling a personal skill on the claude.ai account is an upload: the upload rules apply.

## Scripts and dependencies

- [req] In Claude Code, commands run in the session's directory, never the skill's: call bundled scripts as `${CLAUDE_SKILL_DIR}/scripts/<file>`.
- [default] In Claude Code and Cowork, a script starts with `#!/usr/bin/env <interpreter>` (no version), is executable (committed as `100755`) and is called by its path; the user's first interpreter on `PATH` runs it. The skill's README lists the interpreter and minimum version under requirements.
- [default] For an upload or the API, call scripts through their interpreter with a path relative to the skill (`python3 scripts/<file>`): a zip upload can lose the executable bit, and the platform documentation shows only relative paths, never the path variables.
- [req] The Skills API has no network access and installs nothing at run time; claude.ai can install packages from npm and PyPI. Use only preinstalled packages for the API.
- [req] MCP tools are named `mcp__<server>__<tool>` in Claude Code (`mcp__plugin_<plugin>_<server>__<tool>` for a plugin's server); other clients use `Server:tool`.

## Portability findings

Report a portability problem only for a target the skill is meant for. Severity:

| Problem | Severity |
| :-- | :-- |
| A field, limit or feature the target rejects (upload or API) | high |
| A feature the target silently skips (a `!` line in Cowork, a path variable in a synced skill) that an instruction depends on | high |
| The same, when no instruction depends on it | low |
| A requirement the skill needs but does not state (interpreter, network, a tool on `PATH`) | medium |
