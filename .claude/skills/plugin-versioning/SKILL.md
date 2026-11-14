---
name: plugin-versioning
description: Sets or changes the version of a plugin in this marketplace, with its changelog notes and checks. Use whenever a plugin under plugins/ changed and needs a version bump, a new plugin needs its first version, someone asks which semver level a change takes, or a change relies on a newer Claude Code release, even if they only say "bump it" or "does this need a new version".
---

# Plugin versioning

Every plugin here is a relative-path entry (`./plugins/<plugin>`) in a git-hosted marketplace. Users receive a change only when the plugin's version string changes, so a missed bump means users never get the change, and a version set in the wrong place silently wins over the right one.

## How Claude Code reads the version (official)

From code.claude.com/docs/en/plugins/host-marketplace (Release a new version), loading (How Claude Code computes the version) and manifest-reference (`version`):

- The version comes from `version` in `plugin.json` first, then from the marketplace entry. With neither set, a relative-path plugin in a git-hosted marketplace uses the commit SHA.
- With `version` set, commits pushed without changing it don't reach users: `claude plugin update` prints `<name> is already at the latest version (<version>)`.
- Set `version` only in `plugin.json`. If the marketplace entry also sets one, Claude Code uses `plugin.json` without warning and `claude plugin validate` reports `Entry declares version "<a>" but <path>/plugin.json says "<b>"`.
- `version` is not checked against semver. This project requires semver anyway (below).

## Steps

1. **Identify the case.**
   - New plugin: its first version is `0.1.0`. Go to step 4.
   - Only the plugin's `README.md`, `CHANGELOG.md`, `LICENSE`, `NOTICE.txt`, `tests/`, `*.test.ts(x)` or `evals/` changed: no bump. Stop.
   - Only `.claude-plugin/marketplace.json` changed: no plugin bump. Stop; a rename or removal goes through the `plugin-catalog-changes` skill.
   - Anything else in `plugins/<plugin>/` changed: bump. Continue.
2. **Choose the level** from the diff against `origin/main`; when a change mixes levels, take the highest.
   - Major: a removed or renamed skill, agent, command or plugin; changed configuration keys; a new mandatory dependency; changed behavior users rely on.
   - Minor: a new backward-compatible component, option or capability, or a higher `engines["claude-code"]` floor.
   - Patch: a bug fix, prompt wording, a performance improvement, or a refactor with the same behavior.
   - In `0.x`, a breaking change bumps Minor. Moving from `0.x` to `1.0.0` needs the owner's authorization, because it promises users a stable interface.
3. **Check dependents**, because a plugin that depends on this one through a version range stops resolving if the new version falls outside it:
   ```bash
   npm run release:status
   ```
   Each `dependent: <plugin> needs <name> <range>` line is a declared dependency, from `plugin.json` or the marketplace entry, with its range as written (`any` for a bare name). Keep the new version inside every range that names this plugin, or change the dependent in the same pull request.
4. **Set the minimum Claude Code version** when the change relies on a Claude Code feature, through `engines["claude-code"]` in `plugin.json`: outside its range the plugin is not installed, updated or loaded, and install and update pick the newest version that fits (see Version notes). Set it to `">=<lowest version that has the feature>"`, make the README's minimum Claude Code version say the same, and record the change under `### Changed`.
5. **Write the notes** with the `docs-maintenance` skill, under `## [Unreleased]` in `plugins/<plugin>/CHANGELOG.md`: one entry per user-visible change, its type (Added, Changed, Deprecated, Removed, Fixed or Security) and `**Breaking:**` where it breaks something. When the change alters what the plugin's README describes, such as its components, commands, prerequisites or minimum Claude Code version, update the README with the same skill. For a new plugin, run that skill's "New plugin" event instead.
6. **Set the new version** in `plugins/<plugin>/.claude-plugin/plugin.json` to what this prints, after `git fetch origin main`, with `<level>` the one chosen in step 2:
   ```bash
   npm run release:status -- --next <plugin> --level <level>
   ```
   It raises that field of the version on `origin/main` by one and resets the fields after it to `0` (Minor: `0.3.2` becomes `0.4.0`); a plugin not on `origin/main` yet gets `0.1.0`.
7. **Verify**, and show the raw output:
   - `npm run release:status` exits 0: it lists the plugin as `changed: <plugin> <old> -> <new>` and exits 1 on a version that is not semver, which the validator doesn't check (it accepts `1.0`)
   - `claude plugin validate --strict plugins/<plugin>` exits 0
   - `claude plugin validate --strict .` exits 0
   - `claude plugin validate --profile directory --strict plugins/<plugin>` exits 0: the plugin directory's portability checks (README, license, privacy URL, system files)
   - for a mod, meaning the plugin has `tests/*.test.ts(x)`: `claude plugin test plugins/<plugin>` exits 0
   - `npm run check:consistency` exits 0: names, changelog, README and catalog agree
   - `claude plugin tag plugins/<plugin> --dry-run` prints `<plugin>--v<new version>`. Commit the change first: it exits 1 while any file under the plugin is uncommitted.
   - the plugin installs and loads from a local marketplace, the official pre-release check. The script runs it in a throwaway configuration, never your own: a user can't have two marketplaces with the same name, so adding this checkout to your real configuration collides with an installed `the-claude-factory`. From the repository root:
     ```bash
     npm run check:install -- --from local <plugin>
     ```
     It exits 0 when `claude plugin list --json` shows the plugin with no `errors`, `claude plugin details` lists its components, and `claude plugin validate --strict` (and `claude plugin test` for a mod) pass on the installed copy. Check that the printed version is the new one.
   - when the plugin has evals and the owner approves the run, the local smoke run passes: `claude plugin eval plugins/<plugin> --case <case> --runs 1 --ablation none --no-publish`, where `<case>` is the case the owner approves, by its name in the plugin's eval suite. `--no-publish` keeps the HTML report local; without it `eval` publishes the report to claude.ai. `.claude/rules/plugins/evals.md` (Run) limits local runs to a reduced suite, and every run bills the owner's usage.
8. **Open the pull request** for the change, with the owner's authorization; component changes inside `plugins/` always go through one. The version heading, its date and the changelog links are written at release time by the `plugin-releases` skill, not here.

## Conventions this skill adds to the official docs

Semver levels, Keep a Changelog and the no-bump cases are this project's conventions, not Claude Code requirements. Keep them unless the owner changes them.

## Version notes

Checked on 2026-11-13, with Claude Code 2.1.323: `engines["claude-code"]` is in the Claude Code changelog for 2.1.323 and `claude plugin validate` accepts it, but the plugin docs don't describe it yet. Recheck the manifest reference before relying on more than step 4 states.
