---
status: accepted
date: 2026-11-06
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# DEBT-037, a maintainer hook that makes sessions load the Workflow skills, is withdrawn

## Scope

- In scope: DEBT-037 in `.claude/maintainer/technical-debt/pending-debt.md`, and its proposed `.claude/hooks/require-workflow-skill.py`.
- Out of scope: how sessions are made to use the project skills from now on; the project instructions already list which skill each area needs.

## Context and problem statement

DEBT-037 (logged 2026-10-27) recorded that the session that built `tailwind-development` skipped two project skills, `testing-plugins` and `plugin-hooks-guidance`, that the Workflow of `.claude/CLAUDE.md` assigned to its work. Its fix was a `PreToolUse` hook in `.claude/settings.json` that denies the first call in an area until the session loads that area's skill. Rechecked on `main` at b98db29 on 2026-11-06:

- `plugin-hooks-guidance` no longer exists; commit c4e57fc (2026-11-05) replaced it with `.claude/rules/plugins/plugins-claude-hooks.md`.
- `.claude/CLAUDE.md` has no Workflow section; the area-to-skill list now lives in the project instructions ("Skills").
- Project threads do not run `.claude/settings.json` hooks (`/mnt/project-files/audits/what-sessions-load-2026-11-06.md`, quoting `code.claude.com/docs/en/claude-projects`: hooks "Not run"), and all current work runs in project threads.

Does the item stay open, get rewritten, or go?

## Decision drivers

- The fix it tracked cannot work where the project works today, and two of the names it relies on are gone.
- Nery's decision on 2026-11-06: "Retirar deuda".

## Considered options

- **Withdraw the item, with no closed entry, per ADR_2026-10-28_withdrawn-debt-leaves-no-closed-entry**: chosen.
- **Rewrite it as a `PreToolUse` hook shipped in a private maintainer plugin, which does load in project threads**: proposed on 2026-11-06, not chosen.
- **Close it as obsolete and rely on the project instructions' skill list**: not chosen.

## Decision outcome

Chosen option: **withdraw DEBT-037 with no closed entry**, because Nery withdrew its subject. It leaves `pending-debt.md` without a `closed-debt.md` entry, as ADR_2026-10-28_withdrawn-debt-leaves-no-closed-entry sets for withdrawn items.

### Consequences

- Good, because the pending ledger no longer tracks a fix built on a deleted skill, a deleted section and a hook location that threads ignore.
- Bad, because nothing enforces that a session loads the skill an area needs; the project instructions only list them.
- Bad, because DEBT-037 appears in neither ledger; this ADR is its only trace.

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| A session skips a skill its area needs | Long sessions with many topics, as on 2026-10-27 | Checks or rules of that area are missed | The project instructions list the skill for each area; a new item can be logged on the next observed skip | Nery Samuel Murillo |
| The ID DEBT-037 is reused | Only if the highest ID in the ledgers falls below 037, which it does not (DEBT-048 is pending) | Two items with one ID | This ADR names DEBT-037 as taken | Nery Samuel Murillo |

## More information

- Related: ADR_2026-10-28_withdrawn-debt-leaves-no-closed-entry; DEBT-015 (closed as obsolete on 2026-11-06); DEBT-031, the separate user-facing reminder for the LSP intelligence plugins, stays open.
