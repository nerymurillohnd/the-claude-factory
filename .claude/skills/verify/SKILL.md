---
name: verify
description: Checks this repository's work before a commit - pending documentation chains, plugin and catalog validation, and script linting. Run it right before each commit that changes a plugin, the catalog, an agent, a hook or a script.
allowed-tools: Bash(.claude/skills/documentation-governance/scripts/pending-chains.sh) Bash(claude plugin validate *) Bash(shellcheck *) Bash(git status *) Bash(git diff *)
---

# Verify before a commit

Run each step that applies to the files about to be committed. Report every command with its result. A step that fails stops the commit: fix the cause, then run the step again.

1. List the files about to be committed:

```bash
git status --short
```

2. A change to a plugin is not ready to commit while its documents are behind. List the pending documentation chains:

```bash
.claude/skills/documentation-governance/scripts/pending-chains.sh
```

   Each line is `<chain> <plugin>`. For each one, load the `documentation-governance` skill and run the chain, then commit the plugin's change and its documents together. No output means nothing is pending.

3. For each plugin with changed files, and for the catalog when `.claude-plugin/marketplace.json` changed:

```bash
claude plugin validate --strict plugins/<plugin>
claude plugin validate --strict .
```

4. When a file under `.claude/agents/` changed:

```bash
claude plugin validate .claude/agents
```

5. When a script under `.claude/hooks/` or `.claude/skills/documentation-governance/scripts/` changed:

```bash
shellcheck --enable=all -x .claude/hooks/*.sh .claude/skills/documentation-governance/scripts/*.sh
```

Say plainly which steps ran, which did not apply, and which failed.
