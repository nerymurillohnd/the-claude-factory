---
name: public-marketplace-dev
description: Sets up, completes and audits the base architecture of a public Claude Code plugin marketplace hosted on GitHub - the repository layout, marketplace.json, each plugin folder and plugin.json, the version and release model, validation, the install instructions users follow, the CI workflows that validate and release, and the repository files (issue forms, labels, pull request template, CODEOWNERS, Dependabot, branch rules) - from the official docs, checked against the latest release notes. Use when someone wants to start a public plugin marketplace, turn a repository of plugins into one, add a plugin to the catalog, choose how plugins are versioned, tagged and released, write install and update instructions, set up its CI or GitHub files, or audit an existing marketplace against it. Not for writing a plugin's skills, agents, hooks, mods or MCP servers, for a plugin that fails to install or load (plugin-testing-and-debugging), or for renaming, retiring or removing a published plugin (migrating-plugins).
---

# Set up a public plugin marketplace on GitHub

You build, for the user, the base architecture of a public plugin marketplace: the repository people add with `claude plugin marketplace add owner/repo`. You decide its structure with the user, build it, and prove it works the way users receive it.

A marketplace is a contract with people you never see: once added, its name, its plugins' names, its version model and its release route live on their machines, and changing them means migrating every install. So decisions come first, each with its reason, and the repository is built to enforce them. The failures this prevents: a name that collides or must change, a version model that silently stops updates, a marketplace that validates locally but won't install from GitHub, CI that is missing or green while broken, install instructions that don't match what users must type, and a field written from memory that a release removed.

## Gotchas

Each gotcha gives the sign that it is in play.

- **The plugin installs from a local path but not from GitHub.** A local-path marketplace loads a relative-path plugin in place, like `--plugin-dir`, so it doesn't prove the copy users get ("In-place and copied plugins" in `loading.md`). The cause is usually a path that escapes the plugin directory, a symlink out of it, or a file left out of the commit.
- **Users never receive a new release.** Users get a new copy only when the computed version changes: `plugin.json` first, then the marketplace entry, then the commit SHA. A pinned `version` that wasn't bumped keeps everyone on the cached copy. Check that the version changed, and that it is set in one place only ("Release a new version" in `host-marketplace.md`).
- **Validation passes but a plugin's components are broken.** `claude plugin validate .` at the root reads the catalog. It doesn't open the listed plugins' skill, agent, command, hook or MCP files. Validate every plugin directory as well.
- **Users must update by hand.** Auto-update is off by default for third-party marketplaces, and no `marketplace.json` field turns it on. Say so in the install instructions, with the command to turn it on ("Keep plugins updated" in `install.md`).
- **A relative `source` fails to resolve.** It resolves only when Claude Code has the marketplace's files. A marketplace added as a `marketplace.json` URL fetches only that file ("Relative path plugin source" in `marketplace-reference.md`).
- **The copies here are a dated snapshot.** The pages were downloaded on 2026-11-07, and the GitHub references were read on 2026-11-16. Before you write a manifest or catalog field, read its live section with `references/reading-docs.md`. When the live page differs from a copy, follow the live page and tell the user.

## The target architecture

A complete public marketplace has these layers; each exists because a later layer, or a user, depends on it.

1. **Identity.** A marketplace `name` that is kebab-case, not reserved and unlikely to collide, plus `owner` and the GitHub `owner/repo` users add. Users key every plugin as `name@marketplace`, and two marketplaces with the same name can't coexist on a machine. Read "Reserved names" in `marketplace-reference.md`.
2. **Catalog.** `.claude-plugin/marketplace.json` at the repository root. It lists every plugin, with an entry `name` equal to the plugin's manifest `name`. Read `create-marketplace.md` and `marketplace-reference.md`.
3. **Plugins.** One self-contained folder per plugin, usually `plugins/<name>/`, holding `.claude-plugin/plugin.json`, components at their default locations, a `README.md` and a license. Nothing in it may reach outside the folder, because users receive only that folder. Read "Explore the plugin directory" in `components.md`, and `manifest-reference.md`. Writing the components themselves is outside this skill.
4. **Versions and releases.** One model per plugin, declared in one place. Either bump `version` in `plugin.json` on each release and tag it as `<name>--v<version>` with `claude plugin tag`, or leave `version` out and ship every commit. Add a `CHANGELOG.md` for each plugin. Read `host-marketplace.md` and `publish.md`.
5. **Validation.** `claude plugin validate --strict` passes on the root and on every plugin directory, and each plugin installs from the published GitHub source. Read `publish.md`, "Prepare your plugin for release".
6. **User instructions.** A root `README.md` with the add, install, update, auto-update and uninstall commands, using the real names. Read `install.md`, and `publish.md` "Tell users how to install".
7. **CI/CD.** A validate workflow on every pull request and every push, and a release workflow that tags only after validation passes. Both are hardened. Read `references/08-github-repository/ci-cd.md`.
8. **Repository files.** Issue forms with a template chooser, labels, a pull request template, CODEOWNERS, Dependabot, `SECURITY.md`, and branch rules that make CI a gate. Read `references/08-github-repository/repository-files.md`.

Add these only when the user's case calls for them: dependencies between plugins (`dependencies.md`), `relevance` suggestions (`relevance.md`), release channels ("Run release channels" in `host-marketplace.md`), and evals in CI (`plugin-evals.md`).

## How to work

### 1. Understand the user's situation

Establish these points before deciding anything, because each one changes the architecture:

- **New or existing repository?** For an existing one, Step 2 finds what is there.
- **Which plugins, now and later?** A repository that will only ever hold one plugin can be its own marketplace, with `"source": "./"` ("Add the marketplace file to your repository" in `publish.md`). Several plugins, or plans for more, need `plugins/<name>/` entries.
- **Who installs, and on which surfaces?** Only Claude Code, or also Claude and Cowork? Some components and install paths don't work everywhere (`platform-support.md`, `build.md`).
- **Who maintains it?** One person or several decides CODEOWNERS, whether pull requests are required, and how strict the branch rules are.
- **How should releases reach users?** A controlled release with a version, a tag and a changelog, or every merged commit?

Find what the repository, `git remote -v` or the files can answer before asking. Ask the user only what is left, with your recommended answer and its reason.

### 2. Inspect what exists

Read the files and run `claude plugin validate` on what exists. Record each layer as present and correct, present but divergent (say what differs and which section shows it), or missing. Never overwrite a user's file to match the target. A divergence that changes what users receive, such as the version model, a name or a plugin's `source`, is the user's decision. Present it with its consequence and wait for their answer.

### 3. Decide, with the criteria

- **Version model.** Explicit `version` when users should get deliberate, documented releases: it gives tags, a changelog and holding users on a version. The commit SHA only when every push should ship: each merge then reaches users at their next update, and those plugins can't use `--strict`. Never set `version` in both `plugin.json` and the entry.
- **Plugin source.** Use a relative path (`./plugins/<name>`) for plugins in this repository: one clone, one history, one release route. Use `github` or `git-subdir` only for a plugin that lives in another repository, and accept that it is released from there.
- **Release automation.** Tag in CI after validation passes when more than one person merges, or when releases are frequent. Tag by hand with `claude plugin tag --dry-run`, then without `--dry-run`, when one maintainer releases rarely.
- **Branch rules.** Require pull requests and the validate check whenever anyone other than the owner can push, and also for a solo owner who wants CI to block a broken catalog before users read it.
- **Evals in CI.** Only for plugins that have suites, and only with the owner's agreement on cost, because each run bills their account.

When the docs don't settle a choice, it is the user's. Give the options with what each costs, recommend one, and record their answer in the report.

### 4. Build, layer by layer

Build in the order of the target architecture: each layer is checked or documented by the ones after it, so a layer built on an unchecked one hides its defect.

- Read a field's live section before writing it into `marketplace.json` or `plugin.json`, and follow the example manifests in `assets/`.
- Create each plugin's folder and manifest, not the skills or hooks inside: leave those to the user or to the skill for that component.
- Write the CI workflows and the repository files from the two `08-github-repository` references. Pin every action to a full commit SHA that you look up from the action's own repository. Never invent one.

### 5. Verify each layer

A layer is done only when its check passes. A file that exists is not proof.

- **Catalog and plugins**: `claude plugin validate --strict .` and `claude plugin validate --strict <plugin-dir>` for every plugin exit `0`. For a plugin on the commit-SHA model, run it without `--strict` and read every warning.
- **What users receive**: once the repository is pushed, run in an empty configuration:

  ```bash
  export CLAUDE_CONFIG_DIR="$(mktemp -d)"
  claude plugin marketplace add <owner>/<repo>
  claude plugin install <plugin>@<marketplace>
  claude plugin list --json
  ```

  The `installPath` must sit under the plugin cache, and `claude plugin details <plugin>` must list every component. Before the push, this check can't run: report it as waiting.
- **Versions**: `claude plugin tag <plugin-dir> --dry-run` names the expected tag, and `plugin.json` and the entry don't both set `version`.
- **Instructions**: every command in the README uses the real marketplace and plugin names. Run the add and install commands as written.
- **CI and repository files**: the "Done when" lists in `ci-cd.md` and `repository-files.md`.

When a check fails, fix the cause it names, then run every check again: a fix in one layer can break another.

### 6. Report

Give each layer's state before and after with the evidence (command and output), each decision with its reason, where each fact came from (live page, dated copy or changelog only), every check you couldn't run and why, and what waits on the user: the push, the first CI run, rulesets, labels created on GitHub.

## Stop and confirm

Creating the repository, pushing, creating tags or releases, creating labels or rulesets through the API, and changing a published name, `source` or version model reach GitHub or users, so each needs the user's explicit yes to that named action. A deadline or a general go-ahead doesn't replace that yes, because these steps can't be taken back from users' machines. Name the action and its target, ask once, and wait. Everything else in this skill (reading, drafting files, running `claude plugin validate`) changes nothing outside the working tree.

## Keep the facts current

- At the start of every task, invoke this plugin's `cli-commands-guide` skill with the Skill tool and follow it: it holds the exact form of every plugin command this skill runs or writes into instructions and workflows. If it isn't available, read `https://code.claude.com/docs/en/plugins/cli-reference.md`.
- After the conversation is compacted, invoke this skill and `cli-commands-guide` again: compaction keeps only the start of each.
- Before writing a new plugin, adding a manifest or catalog key, or relying on what `claude plugin validate --strict` accepts, run the procedure in `references/05-cli-diagnostics/official-source-validation.md`, from the copies' baseline release to the newest one. A `> **Live page**` note in a copy names a section that is known to be out of date.
- A topic missing from these copies isn't proof that it is undocumented: read the source page before you say so.

## References

Each reference opens with `## Contents`; its `## Documentation References` names its source page first.

- `references/01-plugins-core/overview.md`: plugins and marketplaces; images `assets/plugin-directory.png` and `assets/plugins-model.png`.
- `references/01-plugins-core/create.md`: a first plugin, tested without a marketplace.
- `references/01-plugins-core/create-marketplace.md`: `marketplace.json`, entry rules, plugin sources, local tests.
- `references/01-plugins-core/marketplace-reference.md`: every catalog field, reserved names, sources.
- `references/01-plugins-core/manifest-reference.md`: every `plugin.json` field and path rule; examples `assets/manifest-full-example.json` and `assets/manifest-channel-example.json`.
- `references/01-plugins-core/components.md`: the plugin layout, in "Explore the plugin directory" only; example `assets/components-channel-example.json`.
- `references/01-plugins-core/dependencies.md`: dependencies between plugins.
- `references/01-plugins-core/host-marketplace.md`: hosting, auto-update, releases, holding a version, release channels.
- `references/01-plugins-core/publish.md`: the pre-release checklist and the install instructions for users.
- `references/01-plugins-core/install.md`: what users run and see.
- `references/01-plugins-core/loading.md`: where installs load from, versions and updates.
- `references/01-plugins-core/cli-reference.md`: plugin commands, pointing to `cli-commands-guide`.
- `references/01-plugins-core/troubleshooting.md`: the errors users report, by stage.
- `references/01-plugins-core/security.md`: what an installed plugin can do, and how users review it.
- `references/01-plugins-core/anthropic-marketplaces.md`: how a public marketplace differs from Anthropic's.
- `references/01-plugins-core/org.md`: how organizations allow or block marketplaces.
- `references/01-plugins-core/relevance.md`: optional `relevance` suggestions.
- `references/01-plugins-core/plugin-evals.md`: evals and CI; image `assets/plugin-eval-report.png`.
- `references/04-settings-admin/settings.md` and `references/04-settings-admin/settings-reference.md`: scopes, and `extraKnownMarketplaces` for a repository.
- `references/04-settings-admin/managed-settings.md`: managed keys that restrict which marketplaces users add.
- `references/04-settings-admin/env-vars.md`: environment variables, including `CLAUDE_CONFIG_DIR`.
- `references/07-cross-platform-external/platform-support.md` and `references/07-cross-platform-external/build.md`: what works in Claude Code, Claude and Cowork.
- `references/08-github-repository/ci-cd.md`: Claude Code in CI, the validate and release workflows, hardening, gating the merge.
- `references/08-github-repository/repository-files.md`: issue forms, labels, pull request template, CODEOWNERS, Dependabot, `SECURITY.md`, licenses.
- `references/05-cli-diagnostics/official-source-validation.md`: sources, precedence, reading only the newer releases.
- `references/reading-docs.md`: reading a live section, and what to do when a download fails.
