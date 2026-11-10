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
  - **Claude** is the unified chat and Cowork experience. Anthropic merged Cowork and chat into one Claude on 2026-09-16 ("Starting today, Claude Cowork and chat are merging into one Claude", https://claude.com/blog/cowork-is-now-claude; https://support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude).
  - **Claude Code** remains a separate product; the merge did not include it ("The model picker and the "Code" tab are where they were", same help article).
- The merge is rolling out gradually, and some accounts still show separate Chat and Cowork options, so a plugin's compatibility notes still state where in Claude a component works, for example only where Claude runs tasks on the user's computer.

## Audience and distribution

- The marketplace is public and hosted in a public GitHub repository owned by a personal account, not an organization.
- Everything the marketplace distributes is built for third parties, to install on their own machines and in their own working environments, where they use Claude and Claude Code for their operations and projects.

## Responsibility and verification

- Everything this project publishes reaches third parties: their machines, their projects and their operations with Claude. It can help them, or it can damage, break, block or complicate their work. The consequences are real, for those users and for the owner, as author and as a person.
- The owner and Claude share that responsibility, in every session and every change.
- Every decision, implementation and published change rests on validation and evidence: the current official documentation and its latest applicable changes, with the argument that ties them to the decision.
- Assuming, taking something for granted, acting on what is believed to be true, or fixing things by trial and error is a serious defect, and is not allowed.
- Nothing is published until it is confirmed to be actionable, executable, not deprecated, aligned with current best practices and the official documentation, and built on the best current Claude features available for its purpose.

## Project scopes

- The project has two scopes, which are never mixed:
  - **Maintainer scope:** the development, creation, publishing and upkeep of the project itself.
  - **Plugin scope:** what each plugin distributes to its users.
- A rule, tool or file of one scope does not apply to, or become a requirement of, the other.

## Pull requests

- A pull request is opened only at the owner's request. When a change needs one under these rules, Claude asks the owner for permission before opening it.
- Changes outside `plugins/` need no pull request, unless the owner asks for one.
- Inside `plugins/`:
  - A change that creates or edits a plugin's components, dependencies or configuration always goes through a pull request. Skill, agent and command files are components, even though they are Markdown.
  - A change limited to a plugin's general documentation, which alters neither the plugin's behavior nor what users have installed on their machines, needs no pull request, unless the owner asks for one.

## Evals

- Whether a plugin has evals is the owner's decision. Claude may suggest adding them to a plugin, and says when and why.
- A plugin with evals runs a reduced smoke suite locally, through the official testing modes.
- In CI, the full eval suite of a plugin runs the first time, and afterwards only when a plugin that has evals changes in a way that needs a pull request. Every other run skips the eval workflow.

## Ownership and contributions

- The project is developed and maintained by its owner, Nery, and Claude.
- Users contribute only by reporting issues; they do not open pull requests.
- Triaging, fixing, verifying, releasing and keeping the project current are the work of the owner and Claude alone.
