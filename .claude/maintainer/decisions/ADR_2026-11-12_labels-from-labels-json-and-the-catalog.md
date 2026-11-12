---
status: accepted
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Define labels in labels.json and the plugin catalog, sync them by script and archive the rest

## Scope

`.github/labels.json`, `scripts/sync-labels.py`, `scripts/check-github-files.py`, the plugin dropdowns of the issue forms and of `.github/VULNERABILITY_REPORT.yml`, and the repository's labels on GitHub. Maintainer scope.

## Context and problem statement

`.github/labels.json` held 20 fixed labels. The 22 `plugin: <name>` labels existed only on GitHub; on `main`, `scripts/sync-labels.mjs` generated them from `.claude-plugin/marketplace.json`. GitHub also had its 9 default labels (bug, documentation, duplicate, enhancement, good first issue, help wanted, invalid, question, wontfix), which duplicate the `type:` and `status:` labels, plus 4 labels of retired plugins used by 6 merged pull requests. The forms asked for the plugin as free text, and a form dropdown applies no label.

## Decision drivers

- Each plugin declared in one place.
- No label that a form or Dependabot applies may be missing, because GitHub skips a missing label silently.
- History kept on old pull requests.
- Reading labels through REST, because GraphQL (`gh label list`) is blocked in Claude Code cloud sessions.

## Considered options

- **Fixed labels in `labels.json`; `plugin:` labels and form dropdowns derived from `marketplace.json`; `scripts/sync-labels.py` creates and updates them and never deletes; `scripts/check-github-files.py` fails when a dropdown or an applied label drifts; the 9 defaults and the 4 retired labels archived**: chosen.
- **All 22 `plugin:` labels written by hand in `labels.json`**: rejected because each new or retired plugin would need edits in three places.
- **Delete the 9 default labels**: rejected in favor of archiving, which keeps them on the 3 pull requests that use them and can be undone. Deleting stays the fallback if the API refuses to archive.
- **Keep the retired plugin labels selectable**: rejected because they could still be applied.

## Decision outcome

Chosen option: **labels.json plus the catalog, synced by script, with unused labels archived**, because it keeps one source per label, catches drift offline in `npm run lint:github`, and keeps history.

### Consequences

- Good, because adding a plugin to `marketplace.json` makes `check-github-files.py` fail until the dropdowns list it, and `npm run labels:sync` creates its label.
- Good, because `sync-labels.py` reads through `gh api` (REST) and writes with `gh label create --force`, which use REST.
- Bad, because the labels on GitHub change only when someone runs `npm run labels:sync -- --apply`.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The check catches drift | `npm run lint:github` on a scratch copy with a removed plugin, an unknown plugin, a wrong order and a missing label | Passed on 2026-11-12 (exit 1 with one finding each; exit 2 on invalid JSON) | Each change to the script |
| The dry run matches GitHub | `npm run labels:sync` | Passed on 2026-11-12: 1 to create (`area: docs`), 43 in sync, 13 not managed | Before each `--apply` |
| The labels on GitHub match the wanted set | `npm run labels:sync -- --apply`, then `npm run labels:sync` | Passed on 2026-11-12: `area: docs` created; the dry run then exited 0 with 44 in sync | Each change to `labels.json` or the catalog |
| The 9 defaults and the 4 retired labels are archived | `archived_at` in `gh api repos/nerymurillohnd/the-claude-factory/labels` | Passed on 2026-11-12: 13 archived through `PATCH …/labels/{name}` with `archived=true` (the personal account supports it), 44 active | After the change |

## More information

- Sources: GitHub REST "Labels" (`archived`: "Archived labels cannot be added to issues or pull requests"); GitHub changelog 2026-08-27, "Label archiving is generally available"; GitHub docs "Syntax for issue forms" (`labels`: "If a label does not already exist in the repository, it will not be automatically added to the issue"); cli/cli `pkg/cmd/label` (`create.go`, `edit.go`, `delete.go` use REST; `list.go` uses GraphQL).
- The skill-side tool, github-operations' `labels-sync.py`, is plugin scope and is not used as maintainer tooling.
- The owner decided this in this session, on 2026-11-12.
