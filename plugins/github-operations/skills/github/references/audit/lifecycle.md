# Audit and cleanup lifecycle

Audit a repository completely, report it in plain language, and change nothing until the user approves twice. Run the commands in the references yourself, from your scratch folder. Nothing is installed and no script is written into the repository or onto the machine.

## Lifecycle

Create one task per step (TaskCreate) and complete them in order.

| # | Step | Read | Output | Gate |
| :-: | :-- | :-- | :-- | :-- |
| 0 | Intake: repository, remote, `gh` identity and permission, which scans outside the repository are allowed | `intake-local.md` | `context.md` | none |
| 1 | Audit, read-only: local Git, full history, objects, residue, GitHub, external links | `intake-local.md`, then `history.md`, `github.md`, `links.md` as the allowed scopes permit | files in the scratch folder | none |
| 2 | Inventory and classify; keep the coverage ledger | `intake-local.md` (Step 2) | `findings.md`, `coverage.md` | none |
| 3 | Report and recommendations | `report.md` | `report.md` | **Gate 1**: the user approves recommendation IDs |
| 4 | Implementation plan for the approved IDs only | `plan.md` | `plan.md` | **Gate 2**: the user approves action IDs |
| 5 | Backup (`A-01`, always) and revalidation | `execute.md` | backup folder | state drift stops the run |
| 6 | Execute, one action at a time, each with its pre-flight check | `execute.md`, plus `integrate.md` or `investigate.md` for those classes | statuses in `plan.md` | none |
| 7 | Validate with fresh read-only proof | `validate.md` | `validation.md` | none |
| 8 | Results report; the user decides about the backup | `validate.md` | `results.md` | none |

Read a reference when its step starts, not before. A reference that names another one (for example `execute.md` pointing to `integrate.md`) is read when that action class comes up.

## Invariants

- **Steps 0 to 3 change nothing.** No `fetch`, `gc`, `prune`, `clean` (except `-n`), checkout, stash or write of any kind in the repository. Run audit git commands as `GIT_OPTIONAL_LOCKS=0 git -C "<repo>" ...`.
- **Two gates.** An answer is approval only if the user chose explicitly and named the IDs. "Clean it up", silence, a timeout or an auto-closed question approve nothing; ask again. "Audit only" or a refusal ends the run with the report delivered.
- **A failed command is `BLOCKED`, never zero.** Every domain ends in the coverage ledger as `checked`, `BLOCKED`, `not reachable` or `declined`. The audit cannot prove that nothing else exists, so the report always carries the ledger.
- **Backup before anything else.** `A-01` is part of every approval: a bundle of every ref outside the repository, with a restore test and a checksum, plus patches and archives of uncommitted work. Secret-like files are never copied.
- **Prove before deleting.** Every deletion runs a containment check first (its commits are in the published base, or its content is, or it is in the backup with the user's explicit `backup-only` approval). Remote deletions also re-check the live SHA. Integrations are published before anything they make redundant is deleted.
- **No force.** No `--force`, `-f`, `+refspec`, `-D`, `reset --hard`, `clean -x`, `stash --all`, `stash branch` or `--no-verify`, except an action the user approved by name. History rewrites are never part of a bulk approval and happen only in a fresh mirror clone.
- **Fixes land through branches and pull requests,** never on the base, and pull requests are opened only when the user authorized them.
- **Security-sensitive external items are report-only:** deploy keys, tokens, secrets, installed apps, collaborator access. A secret that was ever committed is reported as exposed, by file name, with the instruction to rotate it; never print or open its content.
- **Never override the user's signing setup.** If signing is configured and unavailable, stop before committing.
- **Redact credentials** in every URL you show: `sed -E 's#(//)[^/@[:space:]]*@#\1***@#'`.

## Folders

- **Scratch folder:** your session scratchpad if the session names one, otherwise `mktemp -d "${TMPDIR:-/tmp}/repo-cleanup-XXXXXX"`. Outside the repository. Holds audit output, `findings.md`, `coverage.md`, `report.md` and `plan-draft.md`. Write outputs to files and read them in pieces; a context compaction then loses nothing.
- **Backup folder:** chosen by the user at Gate 1 (recommend `~/repo-cleanup-backups/<repo>-<date>`, absolute, never inside the repository). Holds the bundle, patches, archives, `manifest.txt`, `plan.md` with statuses, `validation.md` and `results.md`. Never deleted without the user's explicit yes.

## Style of the work

Tell the user in one line where the scratch folder is and what step you are on. Write the report for a person who may not know Git: explain a term the first time, lead with consequences, and keep commands and SHAs as evidence. Cite the raw output for every claim in `validation.md` and `results.md`. If a tool or command is not available, report it as `BLOCKED` and continue; do not install anything and do not write an alternate implementation.
