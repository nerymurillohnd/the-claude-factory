---
name: plugin-development
description: Use before writing, editing or scaffolding any file under plugins/<name>/, such as a component, manifest, script or README.
---

# Plugin development

Every plugin in this marketplace is installed by third parties whose setups are unknown, and nobody reviews it between this repo and them. This skill holds the rules for building one: what to cover, which files it ships, how each component is written and which facts to recall before touching it. It applies when you scaffold a plugin and on every later edit to its files.

## Role

Act as a plugin engineer who builds for strangers. You read the official docs before you write a component, you recall the verified facts of this project before you rely on a behavior, and you keep each part as simple as it can be while staying safe, stable and efficient in Claude Code.

## Rules

- Build for any user of the public marketplace, never for Forestal MT, Nery's machine or the tools he uses. His machine is a test bench, never a finding or a dependency: recall memory `plugins-are-for-third-parties`.
- Cover the plugin's whole domain in one install. Every component must earn its place with a user task no other component of the plugin covers; justify each choice on its own merits, never by citing another plugin of the marketplace.
- A required tool, dependency, account or integration never rules a plugin out: it becomes a prerequisite in the README, with how to install it and its alternatives.
- When Nery hands over his own version of a plugin file, edit his file in place and copy it into the plugin only after he reviews it and says so: recall memory `stage-external-plugin-files`.
- A new plugin starts from `node scripts/new-plugin.mjs`, which renders its files from `.claude/templates/plugin/` (`.claude/CLAUDE.md` → Plugin Documentation and Changelogs → Templates); `.claude/WORKFLOW.md` → Build lists the steps. This skill governs the build after that.
- Make network calls only when the plugin's purpose requires them, and disclose each one in the README.
- Never set `version` on a marketplace entry; `plugin.json` is the only source.

## Gotchas

- A plugin with a top-level `bin/` makes the Claude app refuse it (`check-repo.mjs` enforces this); put the code in a skill's `scripts/` or declare the plugin Claude Code-only.
- A plugin agent ignores `hooks`, `mcpServers`, `permissionMode` and `initialPrompt` in its frontmatter; hooks live in `hooks/hooks.json` and servers in `.mcp.json`.
- Keep `metadata` in `plugin.json` and `onFailure` on hooks even when the claude.ai sync warns about them: recall memory `claudeai-sync-warnings`.
- A Node dependency ships only with a text `bun.lock`, or an npm `package-lock.json` or `npm-shrinkwrap.json` with `lockfileVersion` 2 or 3; other lockfiles, `bun.lockb` included, leave no `node_modules`.

## Hand-offs

| When | Invoke with the Skill tool |
| :-- | :-- |
| The component you write is a hook | `plugin-hooks-guidance`, before you write it (step 4) |
| The component is an MCP server, or an agent that uses a server's tools | `plugin-mcp-guidance`, before you write it (step 4) |
| The change is written | `plugin-consistency`, always (step 7) |
| Nery says the change is ready to ship | `release-and-versioning` (step 8) |
| The work came from an issue or ends in a PR | `github-workflow` |

A skill you invoke hands back to you when it ends: continue at your next step. When a row names the skill that invoked you, hand back to it instead of invoking it, and never re-invoke it.

## Workflow

Tick each step as you finish it. Steps 3 to 5 apply once per component you add or change.

Progress:
- [ ] 1. **Scope**: the domain and the user task behind each component.
- [ ] 2. **Docs**: the official page for each component type.
- [ ] 3. **Recall**: the memories and doc sections those components depend on.
- [ ] 4. **Write**: files, manifest and components.
- [ ] 5. **Scripts**: conventions and network calls.
- [ ] 6. **Clean and try**: no leftovers, load it with `--plugin-dir`.
- [ ] 7. **Consistency**: invoke `plugin-consistency`.
- [ ] 8. **Release**: when Nery says it is ready to ship, invoke `release-and-versioning`.

## Step details

### 1. Scope

State the domain the plugin covers and, for each component, the user task it serves that no other component serves. Drop or merge a component that has no such task. Do this before writing, so every file you add already has a reason. For a component added to an existing plugin, say the task to Nery in your reply before you build; the full design brief is only for a new plugin.

### 2. Docs

Read the current official page for each component type you will write, in full, before you write it. Training data and project docs are starting points, not the authority.

| Component | Read |
| :-- | :-- |
| Plugin layout and every component type | `/en/plugins/components`, `/en/plugins/manifest-reference` |
| Skills | `/en/skills` |
| Agents | `/en/sub-agents` |
| Hooks | `/en/hooks`, `/en/hooks-guide` |
| MCP servers | `/en/mcp` |
| LSP servers | `/en/plugins/code-intelligence` |
| Output styles, themes, monitors, `bin/` | `/en/output-styles` and the matching sections of `/en/plugins/components` |
| Mods | `/en/plugins/mods/overview`, `create`, `reference`, `test` |
| Dependencies and loading | `/en/plugins/dependencies`, `/en/plugins/loading` |

Open them through the Claude Code Docs MCP tools, which serve `/en/plugins/components` at `/en/plugins/components.mdx`. The MCP copy can lack headings the live page has: when a heading is missing or a decision rests on exact wording, read the raw page at `https://code.claude.com/docs/en/<page>.md`.

### 3. Recall

Read these before you write or rely on the behavior they describe:

| When you work on | Read first |
| :-- | :-- |
| An agent | Memory `agent-file-rules`; also `/en/sub-agents` → "Preload skills into subagents" before relying on `skills:` in its frontmatter |
| `userConfig` options | `/en/plugins/manifest-reference` → "User configuration" (install, update and synced copies) |
| An MCP server | The `plugin-mcp-guidance` skill (step 4 invokes it), which holds the Claude app and header rules |
| A mod | `/en/plugins/mods/reference` and `/en/plugins/mods/test` (`register.ts`, static validation, tests, type declarations), `/en/plugins/mods/events`, and `.claude/rules/mods.md`, which lists the sources and the verified lessons. The declarations the engine writes for the installed build win over any docs page when they disagree, as the docs themselves say, and `.claude/CLAUDE.md` → Maintainer and Plugin Scopes → Plugin Tooling |
| A script a skill or agent runs | `/en/skills` → "Available string substitutions" (the path variables are substituted only in `SKILL.md` and agent bodies, never in `references/` or the Bash environment) |

Evals and user docs have their own rules in `.claude/rules/`: `evals.md` and `user-docs.md`. Read the one that matches before you write.

### 4. Write

Files every plugin ships:

- `LICENSE`, `CHANGELOG.md` and `README.md`.
- `NOTICE.txt` only when the plugin bundles, derives from or wires in third-party material: the plugin's copyright and license, then each third-party source with its repository, version or commit, license and the files derived from it.

Manifest:

- Keep `version` in `plugin.json`, at `0.1.0` for the first release, and add `keywords`. Change `displayName` to relabel a plugin; never rename it.
- Name each skill for what it does, not how it is implemented.
- Declare hooks in `hooks/hooks.json`.
- Give the plugin its own `package.json` or Python environment only when its architecture needs one, because its complexity must justify every dependency. Set it up the way the current plugins reference says.

If a component is a hook, invoke `plugin-hooks-guidance` before you write it; if it is an MCP server, or an agent that uses a server's tools, invoke `plugin-mcp-guidance`. Check each component against the page you read in step 2 and the memory from step 3 before you move to the next.

### 5. Scripts

- Start with `#!/usr/bin/env <interpreter>` with no version, commit as `100755`, and call the script by path through `CLAUDE_PLUGIN_ROOT` or `CLAUDE_SKILL_DIR`, each wrapped as `${…}` in the command (this file cannot spell them out: Claude Code would replace them with this machine's paths when the skill loads). Write that command in the plugin's `SKILL.md` or agent body, never in a `references/` file, where the variable arrives unsubstituted.
- Write the README disclosure of each network call at the same time as the call, so the two cannot drift apart.

### 6. Clean and try

After moving or creating files, delete `.DS_Store` files and orphaned cache directories. Exercise what you built with `claude --plugin-dir plugins/<name>`; that flag is only for building and testing. Nery installs the marketplace and the plugin like any other user when he uses it for his own work.

### 7. Consistency

Invoke the `plugin-consistency` skill with the Skill tool, unless it invoked you. It checks that the README, CHANGELOGs, manifests and docs agree with what you built, and it runs the repo's scripts.

### 8. Release

Skip this step while Nery is still shaping the plugin. When he says the change is ready to ship, and `release-and-versioning` has not already bumped this change, invoke it with the Skill tool for the level, the notes and the bump (its steps 1 to 4); it hands back here, and `github-workflow` takes the push and the PR. Verifying the release comes after the merge.
