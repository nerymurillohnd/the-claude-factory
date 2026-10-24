# Skill Triggers

Every time one of these cases arises, invoke the skill with the Skill tool before you act, and follow it to its last step. The skill holds the full procedure; do not work from a memory of it.

| Every time you ... | Invoke |
| :-- | :-- |
| Scaffold, create, edit or remove a plugin file (a component, a script, `plugin.json`, `LICENSE`, `NOTICE.txt`, the README or the CHANGELOG), or receive one from Nery in his own version | `plugin-development` |
| Write or review a plugin hook, its script, its launcher, its tests or the README text about what it blocks | `plugin-hooks-guidance` |
| Add or edit an MCP server, its `userConfig`, or an agent that uses its tools | `plugin-mcp-guidance` |
| Change a plugin, the root `README.md` or `CHANGELOG.md`, `docs/`, `marketplace.json`, a template, a community file or a pinned version; and, over the whole repo, before a release or on a drift or freshness check | `plugin-consistency` |
| Bump, rename, remove or release a plugin, or decide which version a change carries | `release-and-versioning` |
| Handle an issue, commit, branch, push, PR, review comment, failed job, Dependabot alert, or a request for CI work | `github-workflow` |

- To invoke is to start a skill with the Skill tool. A skill that ends hands back to the one that invoked it and never re-invokes its caller; each skill lists its own hand-offs in a section of that name.
- When two apply to one change, `github-workflow` governs every push, PR and merge, `release-and-versioning` governs versions and tags, and `plugin-consistency` always runs last before a change is called ready.
- Whatever the skill, confirm before you claim, verify each review finding against the files and the docs before acting on it, never post, label, close, push, open a PR, merge, tag or publish without Nery's order, and report the raw output of every check.
- Pair every project skill in `.claude/skills/` with a row in this table.
