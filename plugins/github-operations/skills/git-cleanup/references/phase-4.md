# Phase 4: Object Store, Provenance & Configuration Security

Use narrowly scoped read-only checks when ordinary refs do not explain a repository's history or disk size.

## Object Store Commands

```sh
git for-each-ref --format='%(refname) %(objecttype) %(objectname)' refs
git show-ref --head --dereference
git count-objects -vH
git fsck --full --strict --connectivity-only
# the next two print a path only: read the file if it exists
git rev-parse --git-path objects/info/alternates
git rev-parse --git-path packed-refs
```

## Provenance & Object Safety Rules

* **Ref Classification:** Logical refs may be loose or packed. Notes, replace refs, provider refs, and tool-created refs serve as provenance until explicitly classified.
* **Shared Object Stores:** Alternates files can make objects available from another object store.
* **Unreachable Objects:** Running `git fsck --unreachable --no-reflogs` may expose objects kept only by reflogs; this does **not** prove they are dispensable.
* **Deletion Verification:** Always correlate findings with refs, stashes, worktrees, and any retained bundle before proposing object deletion.
* **Non-Destructive Diagnosis:** Never edit `packed-refs`, prune, repack, or run `git gc` as a diagnostic response.

## Configuration & Secret Handling

* **Redaction:** Configuration inspection can expose private remote URLs or credential-helper settings.
* **Targeted Queries:** Query only explicitly relevant keys, redact sensitive values, and report provenance without printing credentials or private tokens.
