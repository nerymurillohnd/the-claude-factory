---
paths:
  - "plugins/**"
  - ".github/workflows/**"
---

# Plugin scope

Conventions for the plugins this marketplace distributes. The split between the maintainer scope and the plugin scope is set in `.claude/CLAUDE.md` (Project scopes).

## Design

- Each plugin covers its purpose completely, end to end, so users find everything that goal needs in one place.
- A plugin earns its place by being more complete and more reliable for its purpose than the official and public alternatives.
- Each plugin is designed only from what it must do and solve for its users, never by copying another plugin.

## Safety

- Every action a plugin takes on a user's machine is treated as high risk, and the least invasive design wins.
- Any doubt about user safety goes to the owner before anything ships.

## License and version

- Every plugin is MIT-licensed, versioned on its own and documented in its own README.
- A plugin's version lives only in its `plugin.json`; its `CHANGELOG.md`, its git tags and its GitHub Releases always agree with that version.

## Target surfaces

- Every plugin in this marketplace is built exclusively for Claude Code, for Claude, or for both.
- When a component does not work everywhere in Claude, the plugin's compatibility notes state where it works, for example only where Claude runs tasks on the user's computer.

## Platform support

- Windows is supported only when a plugin, current or future, is meant to run there, and then only through Git Bash.
- Each plugin's README states its Windows support.

## Portability and prerequisites

- Every plugin created and published here runs on its own on a user's machine. It never depends on the tools, software, configuration or versions installed on the owner's terminal or machine.
- Code is always written to be portable.
- Every tool, software, integration or dependency a plugin needs to run, and every specific or minimum version it requires, is declared as a prerequisite in the Prerequisites section of that plugin's README.

## Pull requests inside `plugins/`

- A change that creates or edits a plugin's components, dependencies or configuration always goes through a pull request. Skill, agent and command files are components, even though they are Markdown.
- A change limited to a plugin's general documentation, which alters neither the plugin's behavior nor what users have installed on their machines, needs no pull request, unless the owner asks for one.

## Evals

- Whether a plugin has evals is the owner's decision. Claude may suggest adding them to a plugin, and says when and why.
- When the owner decides a plugin gets evals, Claude discusses every eval case with the owner before writing it, and never creates cases on its own.
- A plugin with evals runs a reduced smoke suite locally, through the official testing modes.
- In CI, the full eval suite of a plugin runs the first time, and afterwards only when a plugin that has evals changes in a way that needs a pull request. Every other run skips the eval workflow.
