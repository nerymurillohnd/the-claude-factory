---
name: plugin-development
description: Use before writing, editing or scaffolding any file of a plugin folder under plugins/, such as a component, manifest, script or README.
---

# Plugin development

Every plugin in this marketplace is installed by third parties whose setups are unknown, and nobody reviews it between this repo and them. This skill holds the rules for building one: what to cover, how a plugin starts and which facts to recall before touching it. It applies when you scaffold a plugin and on every later edit to its files.

## Role

Act as a plugin engineer who builds for strangers. You read the official docs before you write a component, you recall the verified facts of this project before you rely on a behavior, and you keep each part as simple as it can be while staying safe, stable and efficient in Claude Code.

## Rules

- Cover the plugin's whole domain in one install. Every component must earn its place with a user task no other component of the plugin covers; justify each choice on its own merits, never by citing another plugin of the marketplace.
- When Nery hands over his own version of a plugin file, edit his file in place and copy it into the plugin only after he reviews it and says so: recall memory `stage-external-plugin-files`.

## Gotchas

- Keep `metadata` in `plugin.json` and `onFailure` on hooks even when the claude.ai sync warns about them: recall memory `claudeai-sync-warnings`.

## Hand-offs

| When | Invoke with the Skill tool |
| :-- | :-- |
| The component you write is a hook | `plugin-hooks-guidance`, before you write it (step 3) |
| The component is an MCP server, or an agent that uses a server's tools | `plugin-mcp-guidance`, before you write it (step 3) |
| The change is written | `plugin-consistency`, always (step 5) |

A skill you invoke hands back to you when it ends: continue at your next step. When a row names the skill that invoked you, hand back to it instead of invoking it, and never re-invoke it.

## Workflow

Tick each step as you finish it. Steps 2 and 3 apply once per component you add or change.

Progress:
- [ ] 1. **Scope**: the domain and the user task behind each component.
- [ ] 2. **Recall**: the memories and rules those components depend on.
- [ ] 3. **Write**: manifest and components.
- [ ] 4. **Try**: load it with `--plugin-dir`.
- [ ] 5. **Consistency**: invoke `plugin-consistency`.

## Step details

### 1. Scope

State the domain the plugin covers and, for each component, the user task it serves that no other component serves. Drop or merge a component that has no such task. Do this before writing, so every file you add already has a reason. For a component added to an existing plugin, say the task to Nery in your reply before you build; the full design brief is only for a new plugin.

### 2. Recall

Read these before you write or rely on the behavior they describe:

| When you work on | Read first |
| :-- | :-- |
| An agent | Memory `agent-file-rules`; also `/en/sub-agents` → "Preload skills into subagents" before relying on `skills:` in its frontmatter |
| An MCP server | The `plugin-mcp-guidance` skill (step 3 invokes it), which holds the Claude app and header rules |

### 3. Write

Manifest:

- Name each skill for what it does, not how it is implemented.
- Give the plugin its own `package.json` or Python environment only when its architecture needs one, because its complexity must justify every dependency. Set it up the way the current plugins reference says.

If a component is a hook, invoke `plugin-hooks-guidance` before you write it; if it is an MCP server, or an agent that uses a server's tools, invoke `plugin-mcp-guidance`. Check each component against the official page for its type and the memory from step 2 before you move to the next.

### 4. Try

Exercise what you built with `claude --plugin-dir plugins/<name>`; that flag is only for building and testing. Nery installs the marketplace and the plugin like any other user when he uses it for his own work.

### 5. Consistency

Invoke the `plugin-consistency` skill with the Skill tool, unless it invoked you. It checks that the README and the manifest agree with what you built, and it runs the repo's scripts.
