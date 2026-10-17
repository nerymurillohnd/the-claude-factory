---
paths:
  - "plugins/**"
---

# Plugin Gate

- This file wins over any other rule in the project when they conflict.

## Plugins

- Build plugins exclusively for Claude, to distribute them to third parties from a public repository or a public marketplace.
- Make every plugin and its scripts portable. Never depend on what is installed on Nery's machine.
- Target macOS and Linux. Support Windows only through Git Bash.
- When a plugin needs a specific version, tool, binary or program, list it as a prerequisite in its README, with how to install it and the applicable alternatives.

## New Plugins

- Review the existing plugins first.
- When the new plugin overlaps an existing one by domain, weigh integrating it into that plugin against creating an independent one. Propose the choice to Nery.

## Evals

- Whether a plugin has evals is Nery's decision.
- When Nery asks for evals for a plugin, do not work from memory.
- Load the applicable skills and use the Claude Code Docs MCP tools.
- Read the Claude Code changelog for the installed version, the four before it and every newer one. Contrast what you find and apply it.
- Never invent. Never assume.
- CI runs the evals only for plugins that have an `evals/` folder and that changed.

## Versioning

- Use SemVer: `MAJOR.MINOR.PATCH`.
- Bump major for a breaking change: a removed or renamed skill, agent or command, changed config keys, a new required dependency, or a change in behavior users rely on.
- Bump minor for a new component, option or capability that stays backwards compatible.
- Bump patch for a bug fix, a wording fix, performance, or an internal refactor with the same behavior.
- Stay on `0.x` while a plugin is new. Release `1.0.0` when its interface is stable.
