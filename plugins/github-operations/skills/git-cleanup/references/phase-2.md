# Phase 2: Path & Workspace Inventory

Examine untracked and ignored files to determine their safety before taking action.

## Inventory Commands

```sh
GIT_OPTIONAL_LOCKS=0 git status --short --branch --ignored
git diff --name-status
git diff --cached --name-status
git ls-files --others --ignored --exclude-standard
git check-ignore -v -- <path>
git ls-files --error-unmatch -- <path>
```

## Path Assessment Principles

* **Ignore Rule Purpose:** An ignore rule identifies *why* Git excludes a path, not who owns it or whether its contents can be safely regenerated.
* **Inspection Safety:** Inspect file sizes and repository documentation without opening unvetted ignored files.
* **Retention Policy:** Retain secrets, local configuration (`.env`, `.local`), lockfiles, user data, and caches with unknown rebuild costs.
* **Deletion Previews:**
  * `git clean -ndX` is strictly a deletion preview—it does not grant permission to clean.
  * **Do not substitute `-x`**, as it broadens deletion scope to include unignored, untracked files.
