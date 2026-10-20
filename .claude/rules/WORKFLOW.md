# How to Work With Nery in This Project

## Rules by Task

Each section below applies to one kind of work. Follow the section for the task at hand before you start it.

### When Maintaining Plugins and Repo Documentation

- Read its README. Add what the change made missing and remove what it made obsolete.
- Summarize the change in its `CHANGELOG.md`. Each plugin changelog tells the full story of that plugin.
- The Version badge in a plugin README must stay dynamic, reading `version` from `plugin.json`. Never hardcode a version in it.
- The root `CHANGELOG.md` is a summary, never a copy of a plugin changelog.

### When Writing Plugins

- When a plugin needs a specific version, tool, binary or program, list it as a prerequisite in its README, with how to install it and the applicable alternatives.
- When the new plugin overlaps an existing one by domain, weigh integrating it into that plugin against creating an independent one. Propose the choice to Nery.
- Whether a plugin has evals is Nery's decision.
- Read the Claude Code changelog for the installed version, the four before it and every newer one. Contrast what you find and apply it.

### When Using GitHub

- Changes to plugin manifests, components and dependencies always go through a PR.
- Changes to maintainer documentation need no PR unless Nery explicitly asks for one.
- Check the failed jobs and the reviews of Claude and of third parties. Verify each finding.
- Repeat until everything is green and no more reviews, issues or failed jobs are found.
- Comment on each review and resolve it. A PR is not ready to merge before that.
- Always stop at ready to merge and tell Nery, then wait for the green light.

### When Writing Skills

- In a file under `references/`, link with a path relative to that file, and only to templates: `[template](../assets/template.md)`.
- Never link from one reference to another. Keep references one level deep from `SKILL.md`.
- Project skill in `.claude/skills/`: use `${CLAUDE_PROJECT_DIR}/...`, such as `[rule](${CLAUDE_PROJECT_DIR}/.claude/rules/QUALITY_GATE.md)`.
- Skill inside a plugin: use `${CLAUDE_PLUGIN_ROOT}/...` for files of that plugin.
- Never reference a file outside the plugin from a plugin skill. The install does not copy it.
- Personal skill: use `${CLAUDE_SKILL_DIR}/...` for its own files.
- Skill synced from claude.ai: reference no file outside the skill.
- Never use `../` to leave the skill folder.
