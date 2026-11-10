# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

The project's conventions are in `.claude/rules/project-conventions.md`, a rule that loads in every session.

## What this repository is

A public Claude Code plugin marketplace. `.claude-plugin/marketplace.json` is the catalog; each entry points at a plugin under `plugins/`. Everything under `plugins/` is installed on other people's machines. Everything under `.claude/` exists to build and maintain the marketplace and is never distributed.

The repository is being rebuilt from a clean base. `.claude/architecture/refactor.md` maps the plugin lifecycle in 20 stages and names scripts, such as `scripts/release/bump-version.py`, that do not exist here: treat a script it names as absent until you have confirmed the file.

## Commands

There is no build step and no test suite.

- Validate one plugin: `claude plugin validate --strict plugins/<plugin>`
- Validate the catalog: `claude plugin validate --strict .`
- Validate the project agents' frontmatter: `claude plugin validate .claude/agents`
- Lint the governance scripts and hooks: `shellcheck --enable=all -x .claude/hooks/*.sh .claude/skills/documentation-governance/scripts/*.sh`

## How documentation is produced

A plugin's `README.md` and `CHANGELOG.md` are written by owning agents, not by the main session. The pieces, in the order they act:

1. `.claude/skills/documentation-governance/chains.json` is the single registry: which agent owns which document, and which chain of documents each event sets off. The skill, the hooks and the workflow all read it.
2. The scripts in `.claude/skills/documentation-governance/scripts/` hold the logic: `pending-chains.sh` derives pending chains from git with no stored state, and `check-document.sh` checks what a script can verify. The files in `.claude/hooks/` are only the triggers that call them on an event; nothing asks Claude or a writer agent to run a check.
3. The `documentation-governance` skill tells the main session how to launch the `documentation-chain` workflow with a chain's stages.
4. The workflow runs the owning agents in `.claude/agents/docs/` stage by stage, sends the result to `doc-reviewer`, and allows two correction rounds.
5. On each write, one hook denies a governed document to anyone but its owner and another blocks a document that fails the scripted checks; when a writer stops, its documents are checked again; before a turn ends, pending chains are reported.

To govern another document, add it to `chains.json`, give it an owning agent whose file is its full contract, and extend `check-document.sh` with what a script can verify about it. `.claude/architecture/documentation-governance-plan.md` records the design and the documents still to be brought in.

## Gotchas

- The governance scripts and hooks must run on the bash 3.2 that macOS ships, and they fail open: a missing `jq` or registry lets the action through.
- A workflow script in `.claude/workflows/` uses runtime globals and a top-level `return`, so a TypeScript or JavaScript checker reports errors on it that are not defects. Test it by running it with those globals stubbed.
- `.claude/templates/` and `.claude/references/` are source material being absorbed into the agents' contracts. Do not treat them as current instructions.
- Project memory is `.claude/memory/`. In a cloud session the configured memory path resolves outside the clone, so move a new memory file into `.claude/memory/` and add its line to `MEMORY.md` before committing.
