# Workflow

This file is the contract of the work on this project: each stage, the skill that owns it and its key jobs. The procedure of each stage lives in its skill; never copy it here. Depending on the context, resume the work from the stage it belongs to, and apply its skill to what is already built.

1. Management, Maintenance and Quality Gates
2. Marketplace Plugins

## Management, Maintenance and Quality Gates

1. Decision records
   - When: Nery makes an important decision.
   - Skill: `project-maintainer:write-records`.
   - Key jobs: write the ADR.
2. Pending and resolved tasks
   - When: an idea, task or conflict resolution cannot be carried out, or a logged item is withdrawn, completed or closed.
   - Skill: `project-maintainer:write-records`.
   - Key jobs: log the pending item; record its closure.
3. User documentation
   - When: the marketplace's own user documentation is written, updated or checked.
   - Skill: `maintaining-user-docs`.
   - Key jobs: keep the docs true to the current Claude Code release and the marketplace.
4. Issue handling and resolution
   - Skill: none yet; ask Nery.
   - Key jobs: label each issue only with the labels the repository already has.
5. Local quality gates
   - Skill: none yet; ask Nery.
6. Remote quality gates
   - Skill: none yet; ask Nery.

## Marketplace Plugins

1. Plugin design and planning
   - Skill: none yet; ask Nery.
2. Plugin creation
   - When: a plugin is created, scaffolded, written or fixed.
   - Skills: `building-plugins`; also `building-mods` when the plugin is a mod or contains one.
   - Key jobs:
     - Settle the identity with Nery: name, category (with `plugin-categories`), description, display name and surfaces.
     - Create the plugin and register it in the marketplace.
     - Write the components from the current official docs.
     - Make it public-ready: README, host disclosures, `LICENSE`, `CHANGELOG.md`, third-party notice when it applies.
     - Validate it.
3. Plugin categories
   - When: a new plugin needs its category, a plugin's category changes, a plugin gains or loses a mod, or `scripts/categories.json` changes.
   - Skill: `plugin-categories`.
   - Key jobs:
     - Give every plugin one category, chosen by its purpose.
     - Keep `scripts/categories.json` the only definition, and `metadata.category` the only place a plugin's category is set.
     - Regenerate the marketplace and the catalog after every change.
4. Plugin testing and evaluation
   - When: evals are requested, a ready plugin has MCP servers or MCP hooks, a mod is tested, or an install, load or marketplace error needs diagnosing.
   - Skills: `testing-plugins`; `testing-mods` for a mod's own tests and troubleshooting.
   - Key jobs:
     - Build and run eval suites, only when asked.
     - Run the live MCP checks once Nery says the plugin is ready.
     - Run a mod's own tests.
     - Diagnose install, load and marketplace errors.
5. Versioning and releases
   - When: a new plugin is published, or an existing plugin has changed.
   - Skill: `release-and-versioning`.
   - Key jobs:
     - Choose the version and write the release notes.
     - Check the release before the merge.
     - Confirm what users receive after the merge.
6. Plugin renames and removals
   - When: a plugin is to be renamed, merged into another, removed, retired or deprecated.
   - Skill: `plugin-renames-and-removals`.
   - Key jobs: carry the change without breaking existing installs.
