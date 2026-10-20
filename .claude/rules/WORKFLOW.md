# How to Work With Nery in This Project

## Rules by Task

Each section below applies to one kind of work. Follow the section for the task at hand before you start it.

### When Maintaining Plugins and Repo Documentation

- Read its README. Add what the change made missing and remove what it made obsolete.
- Summarize the change in its `CHANGELOG.md`. Each plugin changelog tells the full story of that plugin.
- The Version badge in a plugin README must stay dynamic, reading `version` from `plugin.json`. Never hardcode a version in it.
- The root `CHANGELOG.md` is a summary, never a copy of a plugin changelog.
- Changelogs follow Keep a Changelog 2.0.0. Write entries under `## [Unreleased]` as you work.
- User-facing language: what changed for the user, not implementation detail. Reference issues as `(#12)`.
- Mark breaking entries with a leading `**Breaking:**` inside their change type (they force a major bump, or a minor bump in `0.x`).
- Root `CHANGELOG.md` is grouped by date, newest first, with one line per plugin launch, version bump or substantial change under that day's heading: `- **plugin-name** 1.2.0 — one-line summary.`
- Create the `## YYYY-MM-DD` heading when it is missing, with `### Added`, `### Changed` and so on below it.

### When Writing Plugins

- When a plugin needs a specific version, tool, binary or program, list it as a prerequisite in its README, with how to install it and the applicable alternatives.
- When the new plugin overlaps an existing one by domain, weigh integrating it into that plugin against creating an independent one. Propose the choice to Nery.
- Whether a plugin has evals is Nery's decision.
- Read the Claude Code changelog for the installed version, the four before it and every newer one. Contrast what you find and apply it.
- Name skills and plugins for what the skill does, not how it is implemented.
- Keep the version in `plugin.json`. Never set `version` on a marketplace entry.
- Change `displayName` to relabel a plugin.
- After moving or creating files, delete `.DS_Store` files and orphaned cache directories.
- Ship a plugin's Node dependencies only with an npm or Bun lockfile; other lockfiles leave no `node_modules`.
- Do not set `hooks` in the frontmatter of a plugin agent: it is ignored. Declare the hook in the plugin's `hooks/hooks.json`.
- Scripts start with `#!/usr/bin/env <interpreter>` (no version), are committed as `100755`, and are called by path (`${CLAUDE_SKILL_DIR}` or `${CLAUDE_PLUGIN_ROOT}`).
- Network calls only when the plugin's purpose requires them and the README discloses them.

### When Versioning a Plugin

| Bump | When |
| :-- | :-- |
| **major** | Breaking: removed/renamed skill, agent or command; changed config keys; new required dependency; behavior users rely on changes |
| **minor** | New component, option or capability, backwards compatible |
| **patch** | Bug fix, prompt wording fix, performance, internal refactor with same behavior |

- `0.x` while a plugin is new; `1.0.0` only when Nery declares its interface stable.
- In `0.x`, a breaking change bumps the minor (`0.y.z` → `0.(y+1).0`) and its changelog entry keeps `**Breaking:**`. From `1.0.0` on, breaking means major.
- Never rename silently. Add `"renames": { "old": "new" }` (or `"old": null` for removal) to `marketplace.json` and note it in the root changelog.

### When Using GitHub

- Changes to plugin manifests, components and dependencies always go through a PR.
- Changes to maintainer documentation need no PR unless Nery explicitly asks for one.
- Check the failed jobs and the reviews of Claude and of third parties. Verify each finding.
- Repeat until everything is green and no more reviews, issues or failed jobs are found.
- Comment on each review and resolve it. A PR is not ready to merge before that.
- Always stop at ready to merge and tell Nery, then wait for the green light.

### When Writing Skills

- Description: what it does + when to use it, third person, ≤ ~500 characters, specific trigger phrases.
- Body: headers, numbered steps, bullets; under 500 lines and ~5,000 tokens. Follow [agentskills.io best practices](https://agentskills.io/skill-creation/best-practices):
  - Moderate detail: each line must be something the model would get wrong without it. The main path stays in `SKILL.md`; situational paths go to `references/` with a "read when …" trigger. Leave layout and rare cases to the model.
  - Prescriptive only where the task is fragile (exact commands, sequences, formats); elsewhere state the goal and why.
  - Defaults, not menus: one default with a short escape hatch.
  - A short input/output example; a template for output that must keep its shape.
- Word guidance that needs judgment for the whole task ("after every edit", not "once").
- Audit our own skills with `/skill-diagnostics:audit`, and re-audit after any rewrite: slimming can drop a load-bearing rule.
- In a file under `references/`, link with a path relative to that file, and only to templates: `[template](../assets/template.md)`.
- Never link from one reference to another. Keep references one level deep from `SKILL.md`.
- Project skill in `.claude/skills/`: use `${CLAUDE_PROJECT_DIR}/...`, such as `[rule](${CLAUDE_PROJECT_DIR}/.claude/rules/QUALITY_GATE.md)`.
- Skill inside a plugin: use `${CLAUDE_PLUGIN_ROOT}/...` for files of that plugin.
- Never reference a file outside the plugin from a plugin skill. The install does not copy it.
- Personal skill: use `${CLAUDE_SKILL_DIR}/...` for its own files.
- Skill synced from claude.ai: reference no file outside the skill.
- Never use `../` to leave the skill folder.

### When Writing User Docs

- READMEs sell: lead with the outcome and why to install, then teach. Never mention maintenance, `.claude/`, internal scripts, CI internals or how we work.
- English, second person, active voice, present tense. Short sentences.
- Benefit first, mechanics second.
- Emoji-prefixed `##` headings, one emoji per heading, consistent across docs (📥 install, 🔧 manage, 🧭 compatibility, 🩺 troubleshooting, ❓ FAQ, 🔄 update, 🗑️ uninstall, 📝 changelog, 📄 license).
- Badges in the hero only: shields.io, brand color `D97757`.
- Tables for comparisons, commands per surface, requirements and options.
- GitHub alerts (`> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`) — never two alerts back to back without text between.
- `<details>` for per-surface instructions and FAQs; the most common option `open`.
- **Bold** for UI labels exactly as shown in the app (`/plugin` → **Installed** → **Update now**). *Italics* for emphasis or terms.
- Relative links inside the repo; absolute `https://` links outside.
- Version-gated features state the minimum version (e.g. "v2.1.292+").
