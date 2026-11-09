---
name: public-marketplace-dev
description: Current knowledge, CLI commands and references from the official sources that teach Claude how to create, build, develop, structure, publish and maintain a public Claude Code plugin marketplace hosted on GitHub. Use when the user asks about or requests, or the task involves, designing or planning, creating, developing, structuring, versioning, tagging, auditing, troubleshooting and debugging, adding components or dependencies, releasing or distributing, and maintaining or answering questions about plugins in a Claude Code plugin marketplace served to third parties from a public GitHub repository. Use only for plugins that belong to such a marketplace or repository.
---

# Public marketplace development

The files in `references/` are copies of official pages from the Claude Code docs, the Claude plugin docs on claude.com, the Claude Platform docs and the Claude Help Center, pruned to what matters for plugins that a public GitHub marketplace serves to third parties, who install them on their own machines. One file, `official-source-validation.md`, is not a copy: it is the procedure this skill uses to check facts against the release notes. Answer and build from these files instead of from memory.

The work is done when every fact you state or write comes from one of these files or from its live source page, and every version-sensitive fact has passed the validation loop below.

## Standing rules

- These copies are a dated snapshot: the pages were downloaded on 2026-11-07, and the hooks files were checked against the release notes up to Claude Code 2.1.319 on 2026-11-09. When the live page or the release notes differ from a copy, follow the live source.
- Before you run, write or explain a plugin command (`claude plugin …`, `claude plugin marketplace …`, any `/plugin` form, `/reload-plugins`, `--plugin-dir` or `--plugin-url`), in a shell, a script, CI, a README or an answer, Step 6 included, invoke this plugin's `cli-commands-guide` skill with the Skill tool and follow it. Once it is loaded, don't invoke it again unless the conversation was compacted. If the skill is not available, read `https://code.claude.com/docs/en/plugins/cli-reference.md` instead.
- Start every reference file at its `## Contents` list, then read only the sections the task needs.
- The first entry of each file's `## Documentation References` section is its source page. Fetch it when a section is missing, thin or possibly outdated.
- A topic missing from these copies is not proof that it is undocumented: read the source page before you say so.
- This skill authorizes no change by itself. Reading the files and drafting change nothing; pushing, tagging, releasing or publishing a plugin still needs the user's request.

## Gotchas

- The pruning removed these topics on purpose: Anthropic's official directory and its submission flow (the manifest reference keeps the directory listing fields), private repositories and their credentials, hosts other than GitHub, self-hosted and GitHub Enterprise Server marketplaces, the `url`, `npm`, `archive` and `command` plugin sources, local-folder or zip distribution, and administrator deployment procedures. For any of them, read the source page.
- Two files are named `cli-reference.md`: the one in `01-plugins-core/` covers the plugin commands, the one in `05-cli-diagnostics/` the general `claude` command line.
- The exact flags, defaults, outputs and exit codes of the plugin commands are in this plugin's `cli-commands-guide` skill; the standing rules say when to load it. The plugin commands file points to it section by section, and names the official page to read when that skill is not available.
- The hooks page is split in two. [references/03-feature-references/hooks.md](references/03-feature-references/hooks.md) holds configuration, handlers, exit codes, JSON output, security and debugging, and opens with the things to know about hooks in plugins. [references/03-feature-references/hooks-events.md](references/03-feature-references/hooks-events.md) holds each event's matcher, input and decision control. Both are trimmed: a line marked **Key facts** replaces a removed example or section and keeps only what it held that is new.
- Links to other docs pages are absolute URLs to the live site, and some point at sections these copies removed. Follow them when the task needs that section.
- A line that starts with `> **View the image**` or `> **Read the example**` points to a file in `assets/`. Open it when the section needs what it shows. The index below names each asset with its page.
- Seven files keep little after pruning, and the index marks each one. For more on their topics, read the source page.

## Workflow

Copy this checklist and tick each item as you complete it:

```
Task Progress:
- [ ] Step 1: Pick the files for the task (the file index in this `SKILL.md`)
- [ ] Step 2: Read each file's `## Contents`, then the sections the task needs
- [ ] Step 3: Open every asset those sections point to
- [ ] Step 4: Draft the answer or the change from those sections
- [ ] Step 5: Validate each version-sensitive fact (`references/05-cli-diagnostics/official-source-validation.md`)
- [ ] Step 6: Validate the changed plugin or marketplace (run `claude plugin validate --strict <directory>`)
- [ ] Step 7: Deliver, citing the source page of each fact
```

**Step 1: Pick the files.** Find the task's topic in the file index and take every file whose condition matches. A task that touches several components needs the file for each side: a plugin hook needs the hooks files, the manifest reference and the platform support tables. The result is the list of files to read.

**Step 2: Read the sections.** Read each file's `## Contents` list, then the matching sections in full. The result is the passages the task rests on, each with its file and heading.

**Step 3: Open the assets.** Open each `assets/` file that a section you read points to. The result is the layout or example the draft follows.

**Step 4: Draft.** Choose the branch that fits the task:
- Answering a question: write the answer from the passages.
- Creating or changing plugin or marketplace files: write the change from the passages and the examples.
- Auditing existing files: skip to the validation loop below and follow its audit rule.

The result is a draft with each fact traced to its file and section.

**Step 5: Validate the facts.** Run the validation loop below on every version-sensitive fact in the draft.

**Step 6: Validate the files.** Only when Step 4 changed plugin or marketplace files: run `claude plugin validate --strict <directory>` on each changed plugin directory and on the marketplace root. It passes when it exits `0` and prints `Validation passed`. On exit `1`, read each error and warning with its path, fix the file, and run it again. Exit `2` means the validator itself failed, such as on an unreadable path. Where the `claude` CLI isn't available, as in claude.ai chat, say that this step was skipped. For the flags and the `--json` report, read `plugin validate` in the `cli-commands-guide` skill, which the standing rules load before this run.

**Step 7: Deliver.** Give the result with the source page URL of each fact, and say which facts the release notes changed.

If Step 5 finds a fact that changed, was removed or can't be confirmed, return to Step 4. If Step 6 fails, return to Step 4.

### Validation loop

[references/05-cli-diagnostics/official-source-validation.md](references/05-cli-diagnostics/official-source-validation.md) is the validator. It sets which facts count as version-sensitive, the sources to read, which source wins, and how to read only the releases newer than these copies.

1. Draft the answer or the change (Step 4).
2. Check each version-sensitive fact against the sources in that file, following its `When to validate`, `Source precedence` and `Read a range of Claude Code releases` sections.
3. If a fact fails:
   - Note the fact, the status the file's `Procedure` gives it, and the release entry that shows it
   - Correct the draft from the newer source
   - Check every fact again
4. Only proceed when the sources that file names confirm every fact as current.

When you audit existing files instead of drafting, follow that file's `Procedure` and `Report format`, and change no file until the user decides.

## File index

Each file is listed with when to read it. Assets are listed under the page that points to them.

### Plugins

- [overview.md](references/01-plugins-core/overview.md): what a plugin is and when a plugin is needed instead of a standalone skill or MCP server.
  - [plugin-directory.png](assets/plugin-directory.png): how each file of a plugin directory maps to what it adds.
  - [plugins-model.png](assets/plugins-model.png): the path from a marketplace to a plugin to Claude Code loading its components.
- [create.md](references/01-plugins-core/create.md): to build a first plugin, test it without a marketplace, or convert a `.claude/` setup.
- [components.md](references/01-plugins-core/components.md): to add any component type to a plugin, with an example that validates for each.
  - [components-channel-example.json](assets/components-channel-example.json): the `plugin.json` that binds a channel.
- [manifest-reference.md](references/01-plugins-core/manifest-reference.md): every `plugin.json` field, path forms, and the `userConfig` and environment variable schemas.
  - [manifest-full-example.json](assets/manifest-full-example.json): a `plugin.json` that sets most fields.
  - [manifest-channel-example.json](assets/manifest-channel-example.json): a manifest that binds a channel to an MCP server.
- [dependencies.md](references/01-plugins-core/dependencies.md): to declare plugin dependencies with version ranges, and how they install, resolve and prune.
- [code-intelligence.md](references/01-plugins-core/code-intelligence.md): language server plugins and the LSP recommendation dialog.
- [create-marketplace.md](references/01-plugins-core/create-marketplace.md): to build a `marketplace.json` and test the marketplace locally.
- [marketplace-reference.md](references/01-plugins-core/marketplace-reference.md): every `marketplace.json` field, plugin entries, and the plugin and marketplace source objects.
- [host-marketplace.md](references/01-plugins-core/host-marketplace.md): to host a marketplace and release updates and renames without breaking installs.
- [publish.md](references/01-plugins-core/publish.md): to publish a plugin, the pre-release checklist, and how users get updates.
- [install.md](references/01-plugins-core/install.md): to write a marketplace's install, update and uninstall instructions and predict what users see.
- [cli-reference.md](references/01-plugins-core/cli-reference.md): the plugin commands, with pointers to the `cli-commands-guide` skill.
- [loading.md](references/01-plugins-core/loading.md): where a plugin loads from, which settings file decides it, and why an update changed nothing.
- [plugin-evals.md](references/01-plugins-core/plugin-evals.md): to write and run `claude plugin eval` cases, grade them, and gate CI on the score.
  - [plugin-eval-report.png](assets/plugin-eval-report.png): the layout of an eval report.
- [measure.md](references/01-plugins-core/measure.md): a plugin's token cost, how to lower it, and whether people still use it.
- [troubleshooting.md](references/01-plugins-core/troubleshooting.md): to diagnose a plugin or marketplace error from its exact message.
- [security.md](references/01-plugins-core/security.md): what a plugin can do on a user's machine and how users review and remove one.
- [org.md](references/01-plugins-core/org.md): how organizations allowlist, block or require plugins through managed settings.
- [relevance.md](references/01-plugins-core/relevance.md): the `relevance` block that makes Claude Code suggest a plugin.
- [anthropic-marketplaces.md](references/01-plugins-core/anthropic-marketplaces.md): Anthropic's marketplaces and how a public GitHub one differs.
- [cli-hints.md](references/01-plugins-core/cli-hints.md): the `claude-code-hint` tag; title and source only.

### Mods

- [mod-overview.md](references/02-mods/mod-overview.md): what a mod is and how it compares with settings hooks, skills and MCP servers.
- [mod-create.md](references/02-mods/mod-create.md): to write a mod, with the reload and validate loop and type definitions.
- [mod-reference.md](references/02-mods/mod-reference.md): the complete reference for the hooks module, events, API methods, render sites, limits and commands.
- [mod-events.md](references/02-mods/mod-events.md): to observe, rewrite or answer tool calls, prompts, turns and settings reads.
- [mod-api.md](references/02-mods/mod-api.md): to add commands and tools, call a model, run timers, message sessions, and reach files and the network.
- [mod-interface.md](references/02-mods/mod-interface.md): to draw panes, bands, buttons and fields, and keep state between redraws.
  - [mods-screen-map.png](assets/mods-screen-map.png): where on the screen a mod can draw each surface.
  - [mods-heat-map.png](assets/mods-heat-map.png): the grid the example pane draws.
- [mod-gallery.md](references/02-mods/mod-gallery.md): each interface element with sample code.
  - Screenshots, one per element or state: [text](assets/mods-el-text-light.png), [markdown](assets/mods-el-markdown-light.png), [link](assets/mods-el-link-light.png), [code](assets/mods-el-code-light.png), [diff](assets/mods-el-diff-light.png), [box](assets/mods-el-box-light.png), [button](assets/mods-el-button-light.png), [focused plain button](assets/mods-el-button-plain-focused-light.png), [input](assets/mods-el-input-light.png), [focused input](assets/mods-el-input-focused-light.png), [input while typing](assets/mods-el-input-typed-light.png), [select](assets/mods-el-select-light.png), [open select](assets/mods-el-select-moved-light.png), [picked select](assets/mods-el-select-picked-light.png), [raster](assets/mods-el-raster-light.png).
- [mod-test.md](references/02-mods/mod-test.md): to write automated tests for a mod.
- [mod-troubleshoot.md](references/02-mods/mod-troubleshoot.md): why a mod does nothing, refusal messages and the debug log.
- [mod-admin.md](references/02-mods/mod-admin.md): what an organization's managed settings allow a published mod to do.

### Components a plugin ships

- [skills.md](references/03-feature-references/skills.md): to write, configure, invoke and ship skills and commands.
- [sub-agents.md](references/03-feature-references/sub-agents.md): to define subagents, including the rules for a plugin's `agents/` directory.
- [hooks.md](references/03-feature-references/hooks.md): to configure, write and debug hooks, above all plugin hooks.
  - [hooks-lifecycle.png](assets/hooks-lifecycle.png): the order in which every hook event fires in a session and inside the agentic loop.
  - [hook-resolution.png](assets/hook-resolution.png): how a matcher and an `if` condition decide whether a hook runs.
- [hooks-events.md](references/03-feature-references/hooks-events.md): when each hook event fires, its matcher, its input and its decision control.
- [hooks-guide.md](references/03-feature-references/hooks-guide.md): worked hooks for formatting, notifications, command checks and project rules.
- [mcp.md](references/03-feature-references/mcp.md): MCP servers, including plugin-provided ones, their scopes, authentication and limits.
- [channels.md](references/03-feature-references/channels.md): how channel plugins are installed, enabled, secured and tested.
- [channels-reference.md](references/03-feature-references/channels-reference.md): the channel contract an MCP server must follow.
  - [channel-architecture.png](assets/channel-architecture.png): how external systems, the channel server and Claude Code connect.
  - [channel-permission-relay.png](assets/channel-permission-relay.png): the message sequence of a permission relay.
- [output-styles.md](references/03-feature-references/output-styles.md): custom output styles, including the plugin-only `force-for-plugin` field.
- [statusline.md](references/03-feature-references/statusline.md): the `subagentStatusLine` setting a plugin can ship a default for.
- [model-config.md](references/03-feature-references/model-config.md): when a skill, command or subagent sets `model` or `effort`.
- [workflows.md](references/03-feature-references/workflows.md): dynamic workflows, including how a plugin distributes one.

### Settings and permissions

- [settings.md](references/04-settings-admin/settings.md): settings scopes and which value wins.
- [settings-reference.md](references/04-settings-admin/settings-reference.md): the `settings.json` keys that bear on plugins.
- [permissions.md](references/04-settings-admin/permissions.md): permission rules and modes, and how hooks and mods interact with them.
- [env-vars.md](references/04-settings-admin/env-vars.md): the environment variables relevant to building and distributing plugins.
- [managed-settings.md](references/04-settings-admin/managed-settings.md): the managed-only keys that control permissions, plugins and delivery.
- [server-managed-settings.md](references/04-settings-admin/server-managed-settings.md): when a `claude plugin` command can't show the approval dialog.
- [github-enterprise-server.md](references/04-settings-admin/github-enterprise-server.md): GitHub Enterprise Server; title and source only.

### CLI, diagnostics and validation

- [official-source-validation.md](references/05-cli-diagnostics/official-source-validation.md): the validator for Step 5, and for any audit of version-sensitive claims.
- [cli-reference.md](references/05-cli-diagnostics/cli-reference.md): the general `claude` commands and flags.
- [debug-your-config.md](references/05-cli-diagnostics/debug-your-config.md): why settings, hooks, MCP servers or skills aren't taking effect.
- [errors.md](references/05-cli-diagnostics/errors.md): to look up a runtime error message and its fix.
- [headless.md](references/05-cli-diagnostics/headless.md): to run Claude Code programmatically from the CLI, Python or TypeScript.
- [troubleshoot-install.md](references/05-cli-diagnostics/troubleshoot-install.md): removing stored plugin sensitive values and MCP server logins; a few lines only.

### Agent SDK

- [sdk-skills.md](references/06-agent-sdk/sdk-skills.md): which skills an Agent SDK session can invoke, and how sessions discover skills.
- [sdk-plugins.md](references/06-agent-sdk/sdk-plugins.md): the plugin directory layout and the fix for plugin skills that don't appear in the SDK; little else.
- [sdk-mcp.md](references/06-agent-sdk/sdk-mcp.md): how SDK sessions allow and name MCP tools; a few lines only.
- [sdk-hooks.md](references/06-agent-sdk/sdk-hooks.md): hooks in the Agent SDK; title and source only.

### Claude app, Cowork and Agent Skills

- [platform-support.md](references/07-cross-platform-external/platform-support.md): which components and install paths work in claude.ai chat, Cowork and Claude Code.
- [build.md](references/07-cross-platform-external/build.md): the plugin folder as every Claude app reads it, and testing on each app.
- [platform-skills-overview.md](references/07-cross-platform-external/platform-skills-overview.md): how Agent Skills load across Claude products.
  - [agent-skills-architecture.png](assets/agent-skills-architecture.png): where skills live in the agent's file system, next to its configuration.
  - [agent-skills-context-window.png](assets/agent-skills-context-window.png): how skill metadata and content load into the context window in stages.
- [platform-skills-best-practices.md](references/07-cross-platform-external/platform-skills-best-practices.md): how to write a skill Claude finds and uses well.
  - [agent-skills-simple-file.png](assets/agent-skills-simple-file.png): the structure of a basic `SKILL.md` file.
  - [agent-skills-bundling-content.png](assets/agent-skills-bundling-content.png): how a skill bundles reference files that Claude loads only when needed.
  - [agent-skills-executable-scripts.png](assets/agent-skills-executable-scripts.png): how a skill bundles scripts that Claude runs without loading them.
- [support-chat-and-cowork.md](references/07-cross-platform-external/support-chat-and-cowork.md): Cowork and chat as one Claude; title and source only.
