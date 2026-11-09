# Claude Code plugin docs vault (pruned)

This vault holds 64 official Claude and Claude Code documentation pages, downloaded on 2026-11-07 and pruned by removing whole lines. Every kept line is identical to the official page, except 74 links that pointed at a section removed from the same file: their target now points at that section on the live page. The pages keep only what applies to developing, testing, publishing and maintaining Claude Code plugins in a marketplace hosted in a public GitHub repository and installed by third parties on their own machines.

## How to use these files

- Start each file at its `Documentation Index` block: it gives the source URL and the sections the file still contains.
- Before concluding that something is undocumented, check `REMOVALS.md` in this folder: it lists every removed line range with its reason, and the passages kept under doubt.
- Treat this vault as a dated snapshot. For behavior or versions that may have changed, fetch the source URL from the file's index block; when the live page or the changelog differs from this vault, follow the live source.
- Links to another page of the docs are absolute URLs to the live site; some point at sections that this vault removed but the live page still has. `LINK-AUDIT.md` in this folder lists them, along with anchors already broken in the official pages.
- Seven files hold little content after pruning: `cli-hints.md`, `github-enterprise-server.md`, `sdk-hooks.md` and `support-chat-and-cowork.md` keep only their title, description and index; `troubleshoot-install.md` and `sdk-mcp.md` keep a few lines; `sdk-plugins.md` keeps the plugin directory layout. Load them only when their topic comes up.

## Scope of the pruning

Kept: plugin components and their formats, `plugin.json` and `marketplace.json`, plugin sources usable from a public GitHub marketplace (relative paths, `github`, `git-subdir`), versions, updates and tags, plugin commands, evals and validation, errors and troubleshooting, and managed settings that change whether a third party can add the marketplace or run its plugins.

Removed: Anthropic's official directory and its submission flow (`manifest-reference.md` keeps the directory listing fields so their validation warnings stay documented), private repositories and their credentials, non-GitHub hosts, self-hosted and GitHub Enterprise Server marketplaces, the `url`, `npm`, `archive` and `command` plugin sources (sentences that cover several sources still name them), local-folder or zip distribution, administrator deployment procedures, and content unrelated to plugins.

## Inventory

Sizes in KB (1 KB = 1,024 bytes), including each file's index block. The 64 pages total 2,199.1 KB and 31,078 lines (as of 2026-11-08). `REMOVALS.md` adds 178.0 KB and 1,842 lines.

### 01-plugins-core

- `anthropic-marketplaces.md`: 3.0 KB, 38 lines
- `cli-hints.md`: 0.4 KB, 11 lines
- `cli-reference.md`: 64.3 KB, 947 lines
- `code-intelligence.md`: 9.1 KB, 114 lines
- `components.md`: 40.6 KB, 714 lines
- `create-marketplace.md`: 16.1 KB, 248 lines
- `create.md`: 26.8 KB, 402 lines
- `dependencies.md`: 16.0 KB, 226 lines
- `host-marketplace.md`: 20.9 KB, 262 lines
- `install.md`: 28.6 KB, 363 lines
- `loading.md`: 34.8 KB, 353 lines
- `manifest-reference.md`: 43.6 KB, 741 lines
- `marketplace-reference.md`: 38.7 KB, 415 lines
- `measure.md`: 8.8 KB, 127 lines
- `org.md`: 25.8 KB, 268 lines
- `overview.md`: 16.7 KB, 142 lines
- `plugin-evals.md`: 64.6 KB, 797 lines
- `publish.md`: 12.7 KB, 158 lines
- `relevance.md`: 12.0 KB, 201 lines
- `security.md`: 13.4 KB, 162 lines
- `troubleshooting.md`: 92.6 KB, 1181 lines

### 02-mods

- `mod-admin.md`: 24.8 KB, 238 lines
- `mod-api.md`: 42.4 KB, 484 lines
- `mod-create.md`: 24.1 KB, 368 lines
- `mod-events.md`: 37.7 KB, 505 lines
- `mod-gallery.md`: 30.0 KB, 478 lines
- `mod-interface.md`: 53.0 KB, 933 lines
- `mod-overview.md`: 25.4 KB, 276 lines
- `mod-reference.md`: 51.9 KB, 481 lines
- `mod-test.md`: 24.6 KB, 366 lines
- `mod-troubleshoot.md`: 45.0 KB, 493 lines

### 03-components

- `channels-reference.md`: 45.0 KB, 805 lines
- `channels.md`: 13.8 KB, 178 lines
- `hooks-guide.md`: 66.7 KB, 1110 lines
- `hooks.md`: 278.3 KB, 4366 lines
- `mcp.md`: 115.0 KB, 1385 lines
- `model-config.md`: 11.7 KB, 130 lines
- `output-styles.md`: 12.7 KB, 158 lines
- `skills.md`: 75.6 KB, 995 lines
- `statusline.md`: 8.0 KB, 117 lines
- `sub-agents.md`: 64.3 KB, 839 lines
- `workflows.md`: 31.4 KB, 396 lines

### 04-settings-admin

- `env-vars.md`: 22.1 KB, 171 lines
- `github-enterprise-server.md`: 0.6 KB, 13 lines
- `managed-settings.md`: 7.0 KB, 56 lines
- `permissions.md`: 52.2 KB, 586 lines
- `server-managed-settings.md`: 3.3 KB, 36 lines
- `settings-reference.md`: 64.7 KB, 899 lines
- `settings.md`: 31.1 KB, 266 lines

### 05-cli-diagnostics

- `changelog.md`: 119.8 KB, 2550 lines
- `cli-reference.md`: 12.0 KB, 79 lines
- `debug-your-config.md`: 14.0 KB, 160 lines
- `errors.md`: 87.9 KB, 1036 lines
- `headless.md`: 16.2 KB, 195 lines
- `troubleshoot-install.md`: 1.2 KB, 23 lines

### 06-agent-sdk

- `sdk-hooks.md`: 0.5 KB, 13 lines
- `sdk-mcp.md`: 1.9 KB, 33 lines
- `sdk-plugins.md`: 1.9 KB, 42 lines
- `sdk-skills.md`: 10.1 KB, 118 lines

### 07-cross-platform-external

- `build.md`: 17.2 KB, 257 lines
- `platform-skills-best-practices.md`: 42.6 KB, 1235 lines
- `platform-skills-overview.md`: 14.7 KB, 255 lines
- `platform-support.md`: 7.0 KB, 68 lines
- `support-chat-and-cowork.md`: 0.7 KB, 16 lines
