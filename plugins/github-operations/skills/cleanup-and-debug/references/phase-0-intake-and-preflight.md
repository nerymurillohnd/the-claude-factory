# Phase 0: Intake and preflight

- Repository: path, git dir, common dir, remotes (credentials redacted), default branch and base branch.
- Clone type: bare, shallow, partial (promisor remotes), sparse checkout.
- Repository format:
  - ref storage (`files` or `reftable`);
  - object format (SHA-1 or SHA-256), which sets the object ID length.
- Tooling: git and gh versions against the declared minimums. A domain whose command the installed version lacks is marked BLOCKED.
- GitHub identity, and its permission on the repository (admin, write or read). Every call the identity cannot make goes to the coverage ledger.
- Reachability of each domain:
  - reachable;
  - needs consent (scans outside the repository);
  - not reachable.
- The user approves the scans outside the repository once, with their exact roots.
- Every inventory command runs without side effects: no optional locks and no lazy fetch.
