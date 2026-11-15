# Sources and freshness

**Snapshot:** checked against the official sources below on 2026-11-15, at Claude Code **v2.1.325**. Anything newer than v2.1.325 is outside this skill's references: check the live pages, the changelog and the installed CLI (step 1 of the skill).

**Authority:** the plugin evals page wins over these references; where the changelog and the page disagree, the changelog wins. `claude plugin eval --help` only confirms that a flag exists in the installed build.

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
| Publishing reports as artifacts, who can publish | <https://code.claude.com/docs/en/artifacts.md> |
| Installing a pinned Claude Code version | <https://code.claude.com/docs/en/setup.md> |
| `/claude-api` subcommands and their versions | <https://code.claude.com/docs/en/skills.md> |
| Success criteria and evaluations for Claude API apps | <https://platform.claude.com/docs/en/test-and-evaluate/develop-tests.md> |
| Skill authoring best practices | <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md> |
| Evaluating skills, optimizing descriptions | <https://agentskills.io/skill-creation/evaluating-skills>, <https://agentskills.io/skill-creation/optimizing-descriptions> |
| skill-creator plugin | <https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator> |

## Known gaps at the snapshot

- **`--disallow-tools` and the `disallowed_tools` case field** are in the changelog for v2.1.299 ("Added `--disallow-tools` and a `disallowed_tools` case field to `claude plugin eval`") and in `--help`, but the plugin evals page omits them. The changelog wins: they are valid.
- **The default judge.** The page says "the model Claude Code uses for background tasks"; `--help` names `haiku`. State the page's wording.
- **`--keep-temp`.** The page says it keeps every run's sandbox directory and prints its path; `--help` says it preserves scaffold directories. Follow the page.

## Version milestones

From the changelog:

| Version | Change |
| :-- | :-- |
| v2.1.269 | `claude plugin eval` and `claude plugin eval init` added |
| v2.1.283 | git 2.31 or later required when git is installed |
| v2.1.289 | A plugin installed from a local folder marketplace no longer shows a stale copy in `plugin eval` |
| v2.1.293 | Bash-granting runs on Macs with Docker Desktop are no longer refused |
| v2.1.299 | `--disallow-tools` and `disallowed_tools` added; a run that ends on an API error scores 0 ungraded and makes the suite exit 1 |
| v2.1.319 | Warnings no longer suggest `max: 0` for a tool that must not be called |
| v2.1.325 | `--output-dir ''` exits with an error instead of writing the report into the current folder |
