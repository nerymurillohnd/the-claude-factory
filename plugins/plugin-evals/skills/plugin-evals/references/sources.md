# Sources and freshness

**Snapshot:** written from the official sources below on 2026-10-14, against Claude Code **v2.1.299**. Anything newer than v2.1.299 is outside this skill's references: check the installed CLI, the live pages and the changelog (step 1 of the skill).

## Read these live

Every page has a raw Markdown version at the same address ending in `.md`. Read the raw text: summaries drop flags.

- **Plugin evals guide:** <https://code.claude.com/docs/en/plugin-evals.md>
- **`plugin eval` and `plugin eval init` commands:** <https://code.claude.com/docs/en/plugins/cli-reference.md> (sections `plugin eval` and `plugin eval init`)
- **Changelog:** <https://code.claude.com/docs/en/changelog.md>. Search it for `plugin eval`, `eval init` and the flag in question.
- **Weekly summaries:** <https://code.claude.com/docs/en/whats-new/index.md>
- **Index of every page:** <https://code.claude.com/docs/llms.txt>

## Related pages

| Topic | Page |
| :-- | :-- |
| Skills, triggering, the `description`, evaluating a skill | <https://code.claude.com/docs/en/skills.md> |
| Manifest fields (`experimental.evals`) | <https://code.claude.com/docs/en/plugins/manifest-reference.md> |
| Components and their names (skills, agents, hooks, MCP) | <https://code.claude.com/docs/en/plugins/components.md> |
| In-place and copied plugins, `@skills-dir`, name conflicts | <https://code.claude.com/docs/en/plugins/loading.md> |
| Building and validating a plugin | <https://code.claude.com/docs/en/plugins/create.md> |
| Publishing (the release checklist runs the suite) | <https://code.claude.com/docs/en/plugins/publish.md> |
| Context cost of a plugin | <https://code.claude.com/docs/en/plugins/measure.md> |
| Troubleshooting plugins | <https://code.claude.com/docs/en/plugins/troubleshooting.md> |
| Headless `claude -p`, stream-json, `system/init` | <https://code.claude.com/docs/en/headless.md> |
| OS sandbox prerequisites | <https://code.claude.com/docs/en/sandboxing.md> |
| Permission rule syntax for grants | <https://code.claude.com/docs/en/permissions.md> |
| Credentials for CI | <https://code.claude.com/docs/en/authentication.md> |
| Cost estimates | <https://code.claude.com/docs/en/costs.md> |
| Hooks and subagents, when cases exercise them | <https://code.claude.com/docs/en/hooks.md>, <https://code.claude.com/docs/en/sub-agents.md> |
| MCP servers in plugins | <https://code.claude.com/docs/en/mcp.md> |
| Errors | <https://code.claude.com/docs/en/errors.md> |
| Skill authoring best practices | <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md> |
| Evaluating skills, optimizing descriptions | <https://agentskills.io/skill-creation/evaluating-skills>, <https://agentskills.io/skill-creation/optimizing-descriptions> |
| skill-creator plugin | <https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator> |

## Known gaps between the CLI and the docs at the snapshot

These are the reasons the skill checks `--help` first.

- **`--disallow-tools` and the `disallowed_tools` case field** shipped in v2.1.299 and appear in `claude plugin eval --help`. The plugin-evals page didn't list them yet.
- **The default judge.** `--help` named `haiku`; the docs say "the model for background tasks".
- **`--keep-temp`.** `--help` says it preserves scaffold directories; the docs say it keeps every run's sandbox directory.

## Version milestones

| Version | Change |
| :-- | :-- |
| v2.1.269 | `claude plugin eval` and `claude plugin eval init` added |
| v2.1.283 | git 2.31 or later required when git is installed |
| v2.1.289 | A plugin installed from a local folder marketplace no longer shows a stale copy in `plugin eval` |
| v2.1.293 | Bash-granting runs on Macs with Docker Desktop are no longer refused |
| v2.1.299 | `--disallow-tools` and `disallowed_tools` added; a run that ends on an API error scores 0 ungraded and makes the suite exit 1 |
