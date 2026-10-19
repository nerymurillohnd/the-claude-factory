# Phase 3: Submodules, Subtrees & Large Storage Inventory

Audit embedded dependencies, nested repositories, and object pointers before conducting branch operations or file purges.

## Inspection Commands

```sh
git submodule status --recursive
git config --file .gitmodules --get-regexp 'submodule\..*\.path'
git submodule foreach --recursive 'GIT_OPTIONAL_LOCKS=0 git status --short'
git log --grep="git-subtree-dir" --oneline -n 5
git lfs ls-files --size
```

## Submodule & Storage Safety Rules

* **Nested Boundaries:** A submodule is an independent repository bound to an exact recorded commit in the parent tree. Never run path cleaning (`git clean`) or recursive resets across submodule boundaries without auditing inner repositories.
* **Detached Submodule Heads:** Submodules typically check out detached HEADs. Before running `git submodule update` or discarding submodule diffs, check if changes inside the submodule checkout contain unpushed local commits or dirty edits.
* **De-init and Pruning Safeguards:** Running `git submodule deinit` or manually removing directories under `.git/modules/` can destroy uncommitted work or unpushed branches inside nested object stores. Always confirm local commit parity inside `.git/modules/<name>` before proposing submodule de-registration.
* **Subtrees:** Identify subtree prefixes and squashed subtree merge commits. Do not rebase, rewrite, or detach subtrees without preserving original upstream commit metadata.
* **Large File Pointers (LFS):** Differentiate between small Git pointer files and the actual large object payloads. Deleting untracked files or modifying `.gitattributes` without checking `git lfs` status can break pointer resolution across historical trees.
