# Claude Code plugin docs vault (pruned)

This vault holds 63 official Claude and Claude Code documentation pages, downloaded on 2026-11-07 and pruned by removing whole lines, and one procedure written for the skill, `official-source-validation.md`, which replaced the pruned copy of the changelog on 2026-11-09. The pages keep only what applies to developing, testing, publishing and maintaining Claude Code plugins in a marketplace hosted in a public GitHub repository and installed by third parties on their own machines. They are the `references/` of the `public-marketplace-dev` skill, and their images and long JSON examples are in the skill's `assets/` folder.

- 51 pages are rewritten for Claude as their reader: a directive voice, a `## Contents` list of every heading, and a `## Documentation References` section at the end that starts with the source page. Their code blocks and tables are the official ones; `REMOVALS.md` records every other change.
- 12 pages, marked "not yet rewritten" below, keep the pruned official text: every kept line is identical to the official page, except links that pointed at a removed section of the same file, which now point at that section on the live page. They start with a `Documentation Index` block.

## How to use these files

- Start each file at its `## Contents` list, or at its `Documentation Index` block if it is not yet rewritten. The source URL is the first entry of `## Documentation References`, or the `Source:` line of the index block.
- Before concluding that something is undocumented, check `REMOVALS.md` in this folder: it lists every removed line range with its reason, and the passages kept under doubt.
- Treat this vault as a dated snapshot. For behavior or versions that may have changed, fetch the file's source URL; when the live page or the changelog differs from this vault, follow the live source.
- Links to another page of the docs are absolute URLs to the live site; some point at sections that this vault removed but the live page still has. `LINK-AUDIT.md` in this folder lists them, along with anchors already broken in the official pages.
- Seven files hold little content after pruning: `cli-hints.md`, `github-enterprise-server.md`, `sdk-hooks.md` and `support-chat-and-cowork.md` keep only their title, description and source; `troubleshoot-install.md` and `sdk-mcp.md` keep a few lines; `sdk-plugins.md` keeps the plugin directory layout. Load them only when their topic comes up.
- A line that starts with `> **View the image**` or `> **Read the example**` points to a file in the skill's `assets/` folder: open it when the section needs what it shows.

## Scope of the pruning

Kept: plugin components and their formats, `plugin.json` and `marketplace.json`, plugin sources usable from a public GitHub marketplace (relative paths, `github`, `git-subdir`), versions, updates and tags, plugin commands, evals and validation, errors and troubleshooting, and managed settings that change whether a third party can add the marketplace or run its plugins.

Removed: Anthropic's official directory and its submission flow (`manifest-reference.md` keeps the directory listing fields so their validation warnings stay documented), private repositories and their credentials, non-GitHub hosts, self-hosted and GitHub Enterprise Server marketplaces, the `url`, `npm`, `archive` and `command` plugin sources (sentences that cover several sources still name them), local-folder or zip distribution, administrator deployment procedures, and content unrelated to plugins.

## Inventory

Sizes in KB (1 KB = 1,024 bytes). The 64 files total 2,068.9 KB and 28,118 lines (as of 2026-11-09). The skill's `assets/` folder holds 29 PNG images and 3 JSON examples, 1,372.0 KB in total; each is listed under the page that points to it. `REMOVALS.md` adds 184.9 KB and 1,892 lines.

### 01-plugins-core

- `anthropic-marketplaces.md`: 3.0 KB, 38 lines
- `cli-hints.md`: 0.4 KB, 11 lines
- `cli-reference.md`: 29.6 KB, 365 lines
- `code-intelligence.md`: 9.1 KB, 114 lines
- `components.md`: 43.7 KB, 697 lines
  - asset `components-channel-example.json`: 0.5 KB
- `create-marketplace.md`: 16.1 KB, 248 lines
- `create.md`: 27.3 KB, 409 lines
- `dependencies.md`: 16.0 KB, 226 lines
- `host-marketplace.md`: 20.9 KB, 262 lines
- `install.md`: 28.8 KB, 365 lines
- `loading.md`: 35.2 KB, 357 lines
- `manifest-reference.md`: 44.8 KB, 692 lines
  - asset `manifest-full-example.json`: 1.4 KB
  - asset `manifest-channel-example.json`: 0.5 KB
- `marketplace-reference.md`: 38.9 KB, 419 lines
- `measure.md`: 8.8 KB, 127 lines
- `org.md`: 26.1 KB, 272 lines
- `overview.md`: 15.3 KB, 142 lines
  - asset `plugin-directory.png`: 64.3 KB
  - asset `plugins-model.png`: 40.5 KB
- `plugin-evals.md`: 67.6 KB, 800 lines
  - asset `plugin-eval-report.png`: 185.6 KB
- `publish.md`: 12.7 KB, 158 lines
- `relevance.md`: 12.1 KB, 204 lines
- `security.md`: 13.4 KB, 162 lines
- `troubleshooting.md`: 99.7 KB, 1198 lines

### 02-mods

- `mod-admin.md`: 25.1 KB, 238 lines
- `mod-api.md`: 42.4 KB, 484 lines
- `mod-create.md`: 24.1 KB, 368 lines
- `mod-events.md`: 37.7 KB, 505 lines; not yet rewritten
- `mod-gallery.md`: 25.1 KB, 478 lines
  - asset `mods-el-text-light.png`: 9.5 KB
  - asset `mods-el-markdown-light.png`: 8.4 KB
  - asset `mods-el-link-light.png`: 4.2 KB
  - asset `mods-el-code-light.png`: 6.1 KB
  - asset `mods-el-diff-light.png`: 7.8 KB
  - asset `mods-el-box-light.png`: 4.8 KB
  - asset `mods-el-button-light.png`: 3.8 KB
  - asset `mods-el-button-plain-focused-light.png`: 3.8 KB
  - asset `mods-el-input-light.png`: 3.5 KB
  - asset `mods-el-input-focused-light.png`: 4.2 KB
  - asset `mods-el-input-typed-light.png`: 3.1 KB
  - asset `mods-el-select-light.png`: 2.9 KB
  - asset `mods-el-select-moved-light.png`: 5.1 KB
  - asset `mods-el-select-picked-light.png`: 2.5 KB
  - asset `mods-el-raster-light.png`: 1.9 KB
- `mod-interface.md`: 53.3 KB, 937 lines; not yet rewritten
  - asset `mods-screen-map.png`: 36.6 KB
  - asset `mods-heat-map.png`: 1.8 KB
- `mod-overview.md`: 25.4 KB, 276 lines
- `mod-reference.md`: 51.9 KB, 481 lines
- `mod-test.md`: 24.6 KB, 366 lines
- `mod-troubleshoot.md`: 45.1 KB, 493 lines

### 03-feature-references

- `channels-reference.md`: 45.4 KB, 809 lines; not yet rewritten
  - asset `channel-architecture.png`: 41.7 KB
  - asset `channel-permission-relay.png`: 34.1 KB
- `channels.md`: 13.8 KB, 178 lines
- `hooks-guide.md`: 66.7 KB, 1110 lines; not yet rewritten
- `hooks.md`: 278.6 KB, 4370 lines; not yet rewritten
  - asset `hooks-lifecycle.png`: 165.0 KB
  - asset `hook-resolution.png`: 51.8 KB
- `mcp.md`: 115.0 KB, 1385 lines; not yet rewritten
- `model-config.md`: 11.8 KB, 130 lines
- `output-styles.md`: 12.7 KB, 158 lines
- `skills.md`: 75.6 KB, 995 lines; not yet rewritten
- `statusline.md`: 8.0 KB, 117 lines
- `sub-agents.md`: 64.3 KB, 839 lines; not yet rewritten
- `workflows.md`: 31.4 KB, 396 lines

### 04-settings-admin

- `env-vars.md`: 22.1 KB, 171 lines
- `github-enterprise-server.md`: 0.6 KB, 13 lines
- `managed-settings.md`: 7.0 KB, 56 lines
- `permissions.md`: 52.2 KB, 586 lines; not yet rewritten
- `server-managed-settings.md`: 3.3 KB, 36 lines
- `settings-reference.md`: 64.7 KB, 899 lines; not yet rewritten
- `settings.md`: 31.1 KB, 266 lines

### 05-cli-diagnostics

- `official-source-validation.md`: 11.5 KB, 169 lines; how to validate version-sensitive claims against the official release notes and read only the releases that matter
- `cli-reference.md`: 12.0 KB, 79 lines
- `debug-your-config.md`: 14.0 KB, 160 lines
- `errors.md`: 87.9 KB, 1036 lines; not yet rewritten
- `headless.md`: 16.4 KB, 198 lines
- `troubleshoot-install.md`: 1.2 KB, 23 lines

### 06-agent-sdk

- `sdk-hooks.md`: 0.5 KB, 13 lines
- `sdk-mcp.md`: 1.9 KB, 33 lines
- `sdk-plugins.md`: 1.9 KB, 42 lines
- `sdk-skills.md`: 10.1 KB, 118 lines

### 07-cross-platform-external

- `build.md`: 17.2 KB, 257 lines
- `platform-skills-best-practices.md`: 43.2 KB, 1241 lines; not yet rewritten
  - asset `agent-skills-simple-file.png`: 93.7 KB
  - asset `agent-skills-bundling-content.png`: 210.1 KB
  - asset `agent-skills-executable-scripts.png`: 130.1 KB
- `platform-skills-overview.md`: 15.1 KB, 259 lines
  - asset `agent-skills-architecture.png`: 126.0 KB
  - asset `agent-skills-context-window.png`: 116.5 KB
- `platform-support.md`: 7.0 KB, 68 lines
- `support-chat-and-cowork.md`: 0.7 KB, 16 lines
