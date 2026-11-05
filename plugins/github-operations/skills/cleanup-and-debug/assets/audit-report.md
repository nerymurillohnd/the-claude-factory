# Repository audit: <owner>/<repo>

**State:** <a plain-language summary of the repository's state, in two or three sentences>
**Audited:** base `<branch>` at `<full object ID>` · <YYYY-MM-DD>
**Your decision:** approve recommendations by their IDs, or answer "audit only"

## Findings

| ID | Class | Item | Evidence |
| :-- | :-- | :-- | :-- |
| F-1 | <class> | <branch, stash, run, alert…> | <command, full object ID, output file> |

## Recommendations

| ID | Covers | Action proposed | Risk | Can be undone |
| :-- | :-- | :-- | :-- | :-- |
| R-1 | F-1, F-3 | <what would be done> | <risk> | <yes / no, how> |

## Security-sensitive items (report-only)

| Item | Risk | How you change it |
| :-- | :-- | :-- |
| <deploy key, token, app, collaborator…> | <risk> | <where and how> |

## Secrets in published history

<!-- Only when found. Name each by file or key, never by value. -->
- <file or key> in `<commit>`: revoke or rotate it first; rewriting history does not remove it from clones, forks, cached views or pull requests.

## Questions for you

1. <question> — recommended: <answer>, because <reason>.

## Coverage

| Domain | Status (`checked`, `BLOCKED`, `not reachable`) | Call and error, or reason |
| :-- | :-- | :-- |
| <domain> | <status> | <detail> |
