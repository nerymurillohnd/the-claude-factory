---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Set forceRemoveDeletedPlugins so a retired plugin uninstalls from users' machines

## Scope

The top-level `forceRemoveDeletedPlugins` field of `.claude-plugin/marketplace.json`, and every later removal or deprecation of a plugin from this marketplace. The `renames` map and how renames migrate users are out of scope.

## Context and problem statement

Claude Code has no deprecation state: the official way to retire a plugin is to remove its entry, map its name to `null` in `renames`, and optionally set `forceRemoveDeletedPlugins` (code.claude.com/docs/en/plugins/host-marketplace, Work around what a marketplace can't do; read 2026-11-13). Without the field, a removed plugin stays installed on users' machines and reports `Plugin "<name>" not found in marketplace` each time a session loads it. With it, Claude Code uninstalls at each session start every installed plugin that is neither listed nor renamed, from the user, project and local scopes, and flags it in `/plugin` as `Removed from marketplace`; plugins installed only by managed settings stay (host-marketplace, Uninstall removed plugins from users' machines).

## Decision drivers

- A retired plugin should stop running on users' machines, not linger as an error.
- Removal is the only deprecation path Claude Code offers.

## Considered options

- **Set `"forceRemoveDeletedPlugins": true` for the marketplace**: chosen.
- **Leave it unset**: rejected, because each retired plugin would stay installed and report an error at every session start.

## Decision outcome

Chosen option: **set `forceRemoveDeletedPlugins` to `true`**, because it is the documented way to take a retired plugin off users' machines, and the owner decided it on 2026-11-13.

### Consequences

- Good, because a removed plugin uninstalls at the next session start instead of failing to load.
- Bad, because the field applies to every later removal, with no per-plugin choice.
- Neutral, because the docs don't say whether this uninstall also deletes the plugin's saved options, secrets and data, as `claude plugin uninstall` does from the last scope.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The field is set | `jq '.forceRemoveDeletedPlugins' .claude-plugin/marketplace.json` | `true` (2026-11-13) | Before each removal |
| The marketplace stays valid | `claude plugin validate --strict .` | `Validation passed`, exit 0 (2026-11-13) | After each `marketplace.json` change |
| A removed plugin uninstalls at session start | Retire a plugin, then start a session in a configuration that had it installed | Pending | First removal after 2026-11-13 |

## More information

- The `plugin-catalog-changes` skill states the field and checks it before a removal.
- The field reaches users once this branch merges into `main`.
