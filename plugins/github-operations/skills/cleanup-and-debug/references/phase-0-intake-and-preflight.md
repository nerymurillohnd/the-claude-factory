# Phase 0: Intake and preflight

Establish what is being audited, with which tools and which access, before collecting anything. This phase is read-only.

## Repository

- Path, git dir and common dir.
- Remotes, with credentials redacted.
- Default branch and base branch.
- Clone type: bare, shallow, partial (promisor remotes) or sparse checkout.

## Repository format

- Ref storage: `files` or `reftable`, read with `git rev-parse --show-ref-format` ([git-init][git-init], [git-rev-parse][git-rev-parse]).
- Object format: SHA-1 or SHA-256, which sets the length of every object ID ([git-rev-parse `--show-object-format`][git-rev-parse]).

## Tooling and identity

- The git and gh versions in use, checked against the minimums the README declares. Mark a domain `BLOCKED` when the installed version lacks the command it needs.
- The GitHub identity and its permission on the repository: admin, write or read.

## Reachability and consent

Classify every audit domain:

- **Reachable:** read-only git, gh or public registry queries. Collected without asking.
- **Needs consent:** scans outside the repository. Ask the user once, with the exact roots and commands.
- **Not reachable:** behind a credential the audit must not read, or on someone else's machine or service.

Record every domain in the coverage ledger with one status (`checked`, `BLOCKED` with the call that failed, or `not reachable` with the reason). A refused consent scope is recorded too.

## Side-effect-free inventory

Run every inventory command so that it writes nothing:

- No optional locks. Plain `git status` refreshes and writes the index; `GIT_OPTIONAL_LOCKS=0` or `git --no-optional-locks` prevents it ([git-status: Background refresh][git-status], [git][git]).
- No lazy fetch in partial clones. `GIT_NO_LAZY_FETCH=1` stops Git from fetching missing objects from the promisor remote ([git][git]).

## Sources

Checked on 2026-11-04.

- [git][git]: `GIT_OPTIONAL_LOCKS`, `--no-optional-locks`, `GIT_NO_LAZY_FETCH`.
- [git-status][git-status]: "By default, `git status` will automatically refresh the index … and writing out the result."
- [git-rev-parse][git-rev-parse]: `--show-ref-format`, `--show-object-format`.
- [git-init][git-init]: `--ref-format=<format>`, with `files` (the default) and `reftable`.

[git]: https://git-scm.com/docs/git
[git-status]: https://git-scm.com/docs/git-status#_background_refresh
[git-rev-parse]: https://git-scm.com/docs/git-rev-parse
[git-init]: https://git-scm.com/docs/git-init
