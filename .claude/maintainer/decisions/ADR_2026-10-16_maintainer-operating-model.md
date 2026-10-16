---
status: accepted
date: 2026-10-16
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# Maintainer operating model: gate rules, push authority, release and records

## Scope

Applies to how Nery and Claude maintain The Claude Factory: `.claude/CLAUDE.md`, `.claude/rules/`, `.claude/skills/`, `.claude/hooks/` and `.claude/maintainer/`, plus the PR and release flow for plugins. It does not change what any plugin ships.

## Context and problem statement

`.claude/CLAUDE.md` had grown to 183 lines and repeated rules that now live in separate files. Three read-only audits found 37 contradictions between `CLAUDE.md`, the rules and the skills, grouped in about 20 topics: push authority, when gates run, a release flow that pushed to `main` while plugin changes must go through a PR, memory files that did not exist, and links in skills. How should the maintainer instructions be organized so each rule is stated once and the flow is consistent?

## Decision drivers

- Each rule lives in one place.
- Plugin changes always go through a PR and are released only after the merge.
- What must always hold is enforced by a hook, not left to an instruction.
- Cloud sessions see the instructions they need.
- Few moving parts to maintain.

## Considered options

- **Gate rules in `.claude/rules/` plus skills, with one push hook**: chosen.
- **Every push needs Nery's approval** (the previous `CLAUDE.md` position): rejected because the review loop and the maintainer docs would need an approval for each push.
- **Gates before every commit**: rejected because the work is committed at the end of every turn, so the full gate set would run each turn.
- **A separate release commit pushed to `main`**: rejected because it contradicts "plugin changes always go through a PR".
- **Four memory files (`project-state`, `environment`, `learnings`, `session-log`)**: rejected because they do not exist and the learnings already moved to the two `MEMORY.md` files.
- **Keep `.claude/rules/` in `.gitignore`**: rejected because skills and cloud sessions need the rules in the repository.

The rejection reasons come from the audit findings and from the options offered to Nery, who chose among them.

## Decision outcome

Chosen option: **gate rules in `.claude/rules/` plus skills, with one push hook**, because it keeps each rule in one file and enforces the release precondition mechanically.

1. **Authority.** Pushes of changes outside `plugins/` are authorized. Pushes of changes in `plugins/` need Nery's approval. Work is staged after every edit and committed before the turn ends.
2. **Gates.** Per-file checks run after each edit, and the full command list runs before every push. Both live in `QUALITY_GATE`. The `verify` skill is removed.
3. **Release.** The `release` skill is removed. A plugin PR carries its own version bump, and after the merge the release is verified at once (`RELEASES`). Fixed issues are referenced with `Refs #n`, never `Closes #n`.
4. **Version bump hook.** `.claude/hooks/version-bump-gate.sh` denies a `git push` while a plugin changed since `origin/main` has no bump.
5. **Memory.** `MEMORY.md` indexes one topic file per fact. Every reference to `project-state`, `session-log`, `environment` and `learnings` is removed.
6. **Records.** Decisions and technical debt are kept in `.claude/maintainer/decisions/` and `.claude/maintainer/technical-debt/`, through the `project-records` skill.
7. **Rules.** `.claude/rules/` is tracked again. Rules exist for quality, GitHub, maintenance, releases, plugins and skills; the plugin and skill rules are path-scoped.
8. **`CLAUDE.md`.** Duplicated and obsolete lines were removed, and new conventions were added for subagents, workflows and hooks.

### Consequences

- Good, because each rule has one owner and the audits' contradictions are gone.
- Good, because a plugin push without a version bump is blocked before it reaches CI.
- Good, because the cloud sees the rules, since they are tracked.
- Bad, because the gate commands now live only in a rule, not in `CLAUDE.md`.
- Bad, because `PLUGIN_GATE` and `SKILL_GATE` load only when Claude touches matching files.

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| `PLUGIN_GATE` is not loaded when Nery asks for evals or a new plugin, because that starts before any file under `plugins/` is read | Possible | The evals protocol and its precedence clause do not apply | Split the rule into an unscoped part and a path-scoped part (proposed, not decided) | Nery |
| The `tsc` gate is red, so the push steps cannot finish | Present today | Blocks every push | Decide what to do with `.github/scripts/tsconfig.json`, then fix the errors | Nery |

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The hook denies an unbumped plugin push and lets a bumped one through | `node --test ".github/scripts/tests/*.test.mjs"` | Passed, 78 of 78, on 2026-10-16 | When the hook or `check-version-bump.mjs` changes |
| Every link in the skills resolves | A script over `.claude/skills/**/*.md` | Passed, 20 links and none broken, on 2026-10-16 | When a skill changes |
| `bash-lsp-intelligence` and `python-lsp-intelligence` get a version bump | `node .github/scripts/check-version-bump.mjs origin/main` | Pending: both are still at their old version | Before the next push |

## More information

Commits that carry this decision, all local on `feat/github-operations`: `84afdae`, `2518045`, `082303f`, `4ea7a07`, `befb306`, `23b394d`, `ef70c07`, `8b54ea8`, `19be27f` and `6e02d50`.

Open items that follow from it: the bump levels of the two LSP plugins, a bump for `github-operations`, the `tsc` baseline, the split of `PLUGIN_GATE`, and CI evals that start only when a `plugin.json` changes.
