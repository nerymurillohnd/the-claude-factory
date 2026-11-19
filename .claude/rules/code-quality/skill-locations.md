---
paths:
  - "**/skills/**"
---
# Where skills load

Choose where a skill lives by the sessions that must load it. The table follows https://code.claude.com/docs/en/skills#choose-where-skills-load; check that section when a row may have changed.

| Location | Loads in |
| :-- | :-- |
| Managed settings directory, `.claude/skills/<name>/` | Every session on the machines where the organization deploys it |
| `~/.claude/skills/<name>/` | Claude Code sessions on the user's machine only; never claude.ai, Cowork or cloud sessions |
| A repository's `.claude/skills/<name>/` | Every Claude Code session in that repository, local or cloud, except Claude project threads |
| `<subdir>/.claude/skills/<name>/` in a repository | The same sessions, once Claude works on files in `<subdir>` or the session starts there |
| `.claude/skills/<name>/` in a directory added with `--add-dir` | That session |
| A plugin's `skills/<name>/`, or `SKILL.md` at its root, installed from a marketplace into the plugin cache | Sessions on the machine where the plugin is installed and enabled; cloud sessions don't install the plugins a repository declares |
| The user's claude.ai account, alone or in a plugin turned on there | claude.ai, Cowork, cloud sessions, project threads, and Claude Code on the user's machine unless the session doesn't sign in with that account or `syncClaudeAiSkills` or `syncClaudeAiPlugins` is `false` |
