# Project Conventions

Conventions that apply to the whole project. Each section groups the conventions on one subject; add a convention to the section it belongs to, or open a new section when none fits.

## Dates

- Release dates are written in UTC, as `YYYY-MM-DD`.
- A release is dated when it is published: the UTC day its tag and GitHub Release are created, never the day the bump is prepared.

## Platform support

- The repository and its plugins are built for macOS and Linux.
- Windows is supported only when a plugin, current or future, is meant to run there, and then only through Git Bash.

## Target surfaces

- Every plugin in this marketplace is built exclusively for Claude Code, for Claude, or for both.
- The two surfaces are named **Claude Code** and **Claude**, and no other surface name is used.

## Audience and distribution

- The marketplace is public and hosted in a public GitHub repository owned by a personal account, not an organization.
- Everything the marketplace distributes is built for third parties, to install on their own machines and in their own working environments, where they use Claude and Claude Code for their operations and projects.

## Project scopes

- The project has two scopes, which are never mixed:
  - **Maintainer scope:** the development, creation, publishing and upkeep of the project itself.
  - **Plugin scope:** what each plugin distributes to its users.
- A rule, tool or file of one scope does not apply to, or become a requirement of, the other.

## Ownership and contributions

- The project is developed and maintained by its owner, Nery, and Claude.
- Users contribute only by reporting issues; they do not open pull requests.
- Triaging, fixing, verifying, releasing and keeping the project current are the work of the owner and Claude alone.
