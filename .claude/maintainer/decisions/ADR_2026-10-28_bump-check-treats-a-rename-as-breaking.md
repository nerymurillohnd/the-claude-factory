---
status: accepted
date: 2026-10-28
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The bump check compares a renamed plugin with its old name and fails a rename shipped as a patch

## Scope

- In scope: `check-version-bump.py` in `.claude/skills/release-and-versioning/scripts/` and `.claude/skills/plugin-renames-and-removals/scripts/`, its tests in `scripts/testers/scripts.test.mjs`, and the texts that state what a rename means for its version: rule 3 and step 7 of the `plugin-renames-and-removals` skill, the major row and step 4 of the `release-and-versioning` skill, the renames stage in `.claude/CLAUDE.md`, and `docs/faq.md`.
- Out of scope: the level of `<target>` in a merge, which the check does not enforce; DEBT-002, the check's base ref after a revert.

## Context and problem statement

Nery reported on 2026-10-28 that the bump check did not detect renames. It skipped `plugins/<old>`, which no longer exists, and treated `plugins/<new>` as a new plugin, because `plugins/<new>/.claude-plugin/plugin.json` does not exist at the base. A renamed plugin therefore passed with no bump and no changelog entry, and users of the old name received the rename with no new version.

The `plugin-renames-and-removals` skill already said a rename is a breaking change, and the official docs support it. `renames` migrates only `enabledPlugins` and `pluginConfigs` ([host-marketplace](https://code.claude.com/docs/en/plugins/host-marketplace#migrate-users-with-a-renames-map)). The plugin's `name` namespaces its components ([loading](https://code.claude.com/docs/en/plugins/loading#entry-name-and-manifest-name)), and plugin MCP tools are named `mcp__plugin_<plugin>_<server>__<tool>`, the name permission rules and hook matchers use ([mcp](https://code.claude.com/docs/en/mcp#plugin-provided-mcp-servers)). Nothing enforced the rule, and several texts left it unclear: `.claude/CLAUDE.md` said to carry the change "without breaking existing installs", the `release-and-versioning` SemVer table left the plugin's own name out of its breaking cases, and `docs/faq.md` told users that only a major bump is breaking.

## Decision drivers

- A plugin change that reaches users must carry a new version and a changelog entry; a rename is such a change.
- Users must see a rename as breaking, because their commands, agent names, MCP tool names and the permission rules and hook matchers that name them stop matching.
- The rule lives in the file that owns it, and the other texts complement it without restating it.

## Considered options

- **Detect a rename from the `renames` entries HEAD adds and from the `plugin.json` moves git sees; compare with the old name's version; fail a patch step and a move without its `renames` entry**: chosen.
- **Detect a rename from the `renames` map only**: rejected because a rename whose `renames` entry was forgotten would still pass as a new plugin, and that entry is what migrates users.
- **Detect a rename from git's rename detection only**: rejected because a `plugin.json` rewritten past git's similarity threshold would not be seen as moved, while the `renames` entry is the authoritative statement of the rename.
- **Compare the version only, and accept a patch step for a rename**: rejected because a rename is breaking, and in this marketplace a breaking change bumps the minor in `0.x` and the major from `1.0.0` on.

## Decision outcome

Chosen option: **both detection paths, comparison with the old name, and a failing patch step**, because the check then catches the defect Nery reported, a forgotten `renames` entry and a rename under-versioned as a patch, and each text that touches renames states its own part once.

- `check-version-bump.py` reads the `renames` maps of `.claude-plugin/marketplace.json` at the base and at HEAD, and `git diff -M --name-status <base>...HEAD -- 'plugins/*/.claude-plugin/plugin.json'`. A renamed plugin is compared with `plugins/<old>/.claude-plugin/plugin.json` at the base. A patch step fails with the minor or major level to run instead, and a move git sees without its `renames` entry fails. The two skill copies stay identical.
- `plugin-renames-and-removals` owns the rule and its reasons (rule 3) and marks a rename's root changelog line `**Breaking:**` (step 7). `release-and-versioning` classifies a plugin rename or merge in its major row and points to the renames skill, and step 4 fixes one marker for a breaking bump. `.claude/CLAUDE.md` names both key jobs of the renames stage. `docs/faq.md` tells users how breaking changes are versioned and what a rename breaks.

### Consequences

- Good, because a renamed plugin can no longer reach users unbumped, under-versioned or without its `renames` entry.
- Good, because the root changelog has one marker for a breaking bump.
- Bad, because a removal and a new plugin in the same diff whose `plugin.json` files git pairs as a rename would fail as an unregistered move unless the removal's `renames` entry maps the old name to `null`, which the renames skill already requires.
- Bad, because the level of `<target>` in a merge is still not enforced: a merge that bumps `<target>` by a patch passes the check.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| A rename with no bump, with a patch bump, and without its `renames` entry fails; with a minor bump it passes | `node --test --test-name-pattern="rename\|moved" scripts/testers/scripts.test.mjs` | 2026-10-28: 4 of 4 pass; against the previous script, the three failing cases passed | Each change to either copy of the script |
| The two skill copies are identical | `node --test --test-name-pattern="skill copies" scripts/testers/scripts.test.mjs` | 2026-10-28: 2 of 2 pass | Each change to either copy of the script |
| The script lints and type-checks clean | `ruff check`, `ruff format --check` and `basedpyright` on the script | 2026-10-28: no findings | Each change to the script |

## More information

- Decided by Nery Samuel Murillo on 2026-10-28: he reported the defect, then approved the table of owners for the rule and asked for the work on the current branch.
- Commits: 39761b1 (the check and its tests), d0a5615 (the two skills), ea27b13 (`.claude/CLAUDE.md`), bd254c9 (`docs/faq.md`).
- Related: ADR_2026-10-28_skill-bump-copies-stay-identical, ADR_2026-10-18_breaking-changes-bump-minor-in-0x, DEBT-002.
