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

Record each domain's reachability in the coverage ledger. A refused consent scope is recorded as refused, with its roots.

## Done when

- [ ] The repository, its remotes (redacted), default branch and base branch are recorded.
- [ ] The clone type, ref storage and object format are recorded.
- [ ] The git and gh versions are recorded, and every domain they cannot serve is `BLOCKED`.
- [ ] The GitHub identity and its permission are recorded.
- [ ] Every audit domain has its reachability in the coverage ledger.
- [ ] The user answered the consent question, and the approved and refused roots are recorded.

## Sources

Checked on 2026-11-04.

- [git-rev-parse][git-rev-parse]: `--show-ref-format`, `--show-object-format`.
- [git-init][git-init]: `--ref-format=<format>`, with `files` (the default) and `reftable`.

[git-rev-parse]: https://git-scm.com/docs/git-rev-parse
[git-init]: https://git-scm.com/docs/git-init
