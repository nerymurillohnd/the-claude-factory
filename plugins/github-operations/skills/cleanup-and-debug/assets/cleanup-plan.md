# Cleanup plan: <owner>/<repo>

**Approved at gate 1:** <R-IDs>
**Backup first:** a bundle of every ref, outside the repository, proven to restore before any action runs
**Your decision:** approve actions by their IDs; anything not approved does not run

<!-- One block per action, in class order. -->

### A-1: <short title>

- **Implements:** <R-ID> · **Class:** <class>
- **Commands:**

  ```bash
  <exact commands, with full object IDs>
  ```

- **Containment check:** <the read-only check that must pass right before it runs>
- **Backup coverage:** <what in the bundle restores it>
- **Rollback:** <exact steps>, or `irreversible: <why>`
- **Validation criterion:** <the read-only command and the exact result that prove it worked>
