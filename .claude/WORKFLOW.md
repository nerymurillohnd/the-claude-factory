# Workflow

The stages of work in this repository, in order. Each step names the skill, rule or file that governs it; the instructions live there, never here. Skills are in `.claude/skills/`, rules in `.claude/rules/`. A line that says "Recall memory `<name>`" points to a verified fact or a past correction: read `<name>.md` in `.claude/memory/` before you act on that step.

## 1. Intake
1. Triage the issue, request or failed job → `github-workflow` step 1.
2. Confirm it against the code and the live docs → `github-workflow` step 2.
3. Draft the reply and labels for Nery's approval → `github-workflow` step 3.

## 2. Design (new plugin only, on Nery's explicit request)
1. Write the design brief and agree it with Nery → `plugin-design.md` → Design brief.

## 3. Build
1. Branch off `origin/main` → `github-workflow` step 4.
2. Scaffold a new plugin with `new-plugin.mjs` → `plugin-design.md` → While building.
3. Build or change the components → `plugin-development`; a hook → `plugin-hooks-guidance`; an MCP server or agent tools → `plugin-mcp-guidance`.
4. Write each skill → `skill-authoring.md`.
5. Write the README and other user docs → `user-docs.md`.
6. Write evals, only when Nery requests them → `evals.md`.
7. Fill the plugin CHANGELOG (`## [0.1.0]` → `### Added` for a new plugin) and the root `CHANGELOG.md` line → `release-and-versioning`.
8. Check each edited file as you go → `CLAUDE.md` → Quality gates → After editing a file.

## 4. Verify
1. Stop and tell Nery the plugin is built; run the closing checks only once he says it is ready → `plugin-design.md` → Closing checks.
2. Review the plugin with a read-only subagent → `.claude/templates/plugin-review-brief.md`; verify and apply its findings → `CLAUDE.md` → Quality gates.
3. Run every gate → `CLAUDE.md` → Quality gates → Before every push.

## 5. Consistency
1. Make the plugin, READMEs, CHANGELOGs, manifests and docs agree, last before calling a change ready → `plugin-consistency`.

## 6. Version
1. Choose and apply the bump → `release-and-versioning`.

## 7. Ship (each action only on Nery's order)
1. Push and open the PR → `github-workflow` step 5.
2. Carry failed jobs and reviews until nothing is open → `github-workflow` step 6.
3. Report ready to merge and wait for Nery's merge → `github-workflow` step 7.

## 8. Release and close out
1. Confirm the tag and the GitHub Release → `release-and-versioning`.
2. Create the `plugin: <name>` label after a new plugin's first push → `plugin-design.md` → Closing checks.
3. Close the fixed issues with Nery's approval → `github-workflow` step 8.
