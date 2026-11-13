---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# skill-lint never lists `.git/`, `node_modules/` or `.venv/` inside a skill

## Scope

File discovery in `scripts/validators/skill_lint/discover.py` (`PRUNED_DIRS`, `_list_files`) and the CO-12 orphan rule. Maintainer scope.

## Context and problem statement

skill-lint listed every file under a skill folder with `rglob`, so it entered `.git`, `node_modules` and `.venv`, and read whole binaries. A vendored dependency tree would make every one of its files a CO-12 orphan and slow every run. The code review of 2026-11-12 reported it.

## Decision drivers

- Findings the owner can act on, not hundreds of orphans from one vendored tree.
- A run that stays fast on any skill.

## Considered options

- **Prune the three folders from the listing and add them to the CO-12 exemptions in the spec**: chosen.
- **Keep them listed as CO-12 orphans, but read no file over 1 MiB**: rejected because it keeps the flood of orphans.

## Decision outcome

Chosen option: **prune them**, because a vendored tree is not content the skill references, and listing it buries the real findings. Files over 1 MiB elsewhere are still listed but not read.

### Consequences

- Good, because CO-12 reports only the skill's own files.
- Bad, because a skill that ships a vendored dependency tree is not flagged; no rule covers that.

## More information

- Recorded in the spec's CO-12 row and Discovery section. Implemented in commit 8775d17, with the test `test_vendored_folders_pruned`.
- The owner decided this on 2026-11-12, when approving the review-fix plan.
