---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The plugin-tooling rule folds into CLAUDE.md, and what skills cover leaves both

## Scope

`.claude/rules/plugin-tooling.md`, the Plugin Tooling section of `.claude/CLAUDE.md`, and the rules for how a plugin is built that the rebuilt skills (`building-plugins`, `release-and-versioning`, `testing-plugins`) hold.

## Context and problem statement

Two files, both loaded in every session, stated the same rules:
- `.claude/rules/plugin-tooling.md`: portability, prerequisites in the README, Node lockfiles, `claude plugin validate --strict`, shebangs and executable bits, plugin Python, plugin script tests, evals only on request;
- `.claude/CLAUDE.md` → Plugin Tooling, which repeated most of them.

Most of these rules are now held by the rebuilt skills, and the rule file also ended in a stray, duplicate block. Where should each of these rules live?

## Decision drivers

- What a skill covers leaves the files that load in every session.
- One source per rule.
- CLAUDE.md holds only current rules that no skill holds.

## Considered options

- **Remove from both files what the skills cover, move what remains into CLAUDE.md → Plugin Tooling, and delete the rule file**: chosen.
- **Keep the rule file as the plugin-side source**: rejected, because it duplicated CLAUDE.md and the skills, and loaded in every session.

## Decision outcome

Chosen option: **fold the rule into CLAUDE.md and delete it**.

- **Removed from CLAUDE.md, because the skills hold them:** self-contained plugins, prerequisites, Node lockfiles, `validate --strict`, shebang and executable bit, and the line on an evals CI that no longer exists (commit cbd35bd).
- **Moved into CLAUDE.md → Plugin Tooling, because no skill holds them:** the platform targets, Windows support only when the README declares it, the plugin Python rules, and plugin script tests under `scripts/tests/<plugin>/`.
- **Deleted:** `.claude/rules/plugin-tooling.md`. The plugin review brief and `plugin-hooks-guidance` now point at CLAUDE.md (commit 2fcf271).

### Consequences

- Good, because each rule has one source, and sessions load fewer duplicate lines.
- Bad, because a rule now held only by a skill reaches a session only when that skill loads.

## More information

Decided by Nery on 2026-10-25 in this session ("elimina de `.claude/rules/plugin-tooling.md` lo cubierto. lo que no, agregarlo al CLAUDE.md y luego eliminar").
