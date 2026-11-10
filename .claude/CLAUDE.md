# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@architecture/project-conventions.md

## What this repository is

A public Claude Code plugin marketplace. `.claude-plugin/marketplace.json` is the catalog; each entry points at a plugin under `plugins/`. Everything under `plugins/` is installed on other people's machines. Everything under `.claude/` exists to build and maintain the marketplace and is never distributed.

The repository is being rebuilt from a clean base. `.claude/architecture/refactor.md` maps the plugin lifecycle in 20 stages and names scripts, such as `scripts/release/bump-version.py`, that do not exist here: treat a script it names as absent until you have confirmed the file.

## Commands

There is no build step and no test suite.

- Validate one plugin: `claude plugin validate --strict plugins/<plugin>`
- Validate the catalog: `claude plugin validate --strict .`
- Validate the project agents' frontmatter: `claude plugin validate .claude/agents`
- Check a governed document: `.claude/hooks/docs-check.sh plugins/<plugin>/README.md`
- List documentation chains the working tree has set off: `.claude/hooks/docs-pending.sh`
- Lint the hook scripts: `shellcheck --enable=all -x .claude/hooks/*.sh`

## How documentation is produced

A plugin's `README.md` and `CHANGELOG.md` are written by owning agents, not by the main session. The pieces, in the order they act:

1. `.claude/skills/documentation-governance/chains.json` is the single registry: which agent owns which document, and which chain of documents each event sets off. The skill, the hooks and the workflow all read it.
2. `.claude/hooks/docs-pending.sh` derives pending chains from git, with no stored state, and reports them after a change to a plugin and before a turn ends.
3. The `documentation-governance` skill tells the main session how to launch the `documentation-chain` workflow with a chain's stages.
4. The workflow runs the owning agents in `.claude/agents/docs/` stage by stage, sends the result to `doc-reviewer`, and allows two correction rounds.
5. `.claude/hooks/docs-owner-gate.sh` denies a write to a governed document from anyone but its owner, and `docs-check.sh` blocks a document that fails the scripted checks.

To govern another document, add it to `chains.json`, give it an owning agent whose file is its full contract, and extend `docs-check.sh` with what a script can verify about it. `.claude/architecture/documentation-governance-plan.md` records the design and the documents still to be brought in.

## Gotchas

- The hook scripts must run on the bash 3.2 that macOS ships, and they fail open: a missing `jq` or registry lets the action through.
- A workflow script in `.claude/workflows/` uses runtime globals and a top-level `return`, so a TypeScript or JavaScript checker reports errors on it that are not defects. Test it by running it with those globals stubbed.
- `.claude/templates/` and `.claude/references/` are source material being absorbed into the agents' contracts. Do not treat them as current instructions.
- Project memory is `.claude/memory/`. In a cloud session the configured memory path resolves outside the clone, so move a new memory file into `.claude/memory/` and add its line to `MEMORY.md` before committing.
