# Report terms

What each term in an Agent Context Audit report means, for answering the user's questions about it.

## Run status

| Status | Exit code | Meaning |
| :-- | :-- | :-- |
| `complete` | 0 | Every in-scope source was read line by line and every check ran; nothing to fix. |
| `complete-with-findings` | 1 | The same full coverage, with findings to review. |
| `partial` | 2 | Something was not covered: a worker failed, skipped lines or returned output that failed validation, reconciliation did not finish, or a file or the git state changed during the run. The findings shown passed validation, but the list is not complete. |
| `failure` | 3 | No valid report: an internal error stopped the run, or the report could not be written. |
| `cannot-run` | 4 | A requirement is missing (Python 3.9+, the `claude` CLI 2.1.300+, a POSIX system); nothing ran. |

Integrity: every audited file must have the same hash before and after the run, and the git working tree and `HEAD` must be unchanged. The auditors can only read, so a difference means someone edited the project during the run, and the run is `partial`.

## Sources

- **Load mode**: how the agent loads the file: `always` (every session), `conditional` (when a matching path is touched), `on-demand` (when invoked), `config` (settings and hooks), `truncated` (only the first part loads), `shadowed` (another file wins), `dead` (never loaded), `not-loaded`.
- **Evidence-only sources**: managed policy and plugin-provided components. They support findings but are never reported, because the user can't change them.
- **Out of scope**: files the audit lists but does not analyze, with the reason.

## Findings

- **ID** `ACA-<CAT>-<unit>`: the category code and a hash of the file's display path and the instruction's normalized text. The same instruction keeps its ID across runs, so the change since the last run shows new, resolved and persisting findings. Editing the instruction's wording gives it a new ID.
- **Category**: `false` (a claim the evidence contradicts), `wrong` (a bad command, path, flag, key or version), `obsolete` (deprecated or renamed), `dead` (never loaded, or a broken reference), `ambiguous`, `duplicated`, `overlapping`, `misplaced` (wrong file, scope or tool), `contradictory`, `redundant-with-defaults` (the agent already does it or derives it), `non-conformant` (against the official guidance for that file type).
- **Severity**: `high` (the agent acts wrongly on a normal path, or a file is lost), `medium` (likely confusion, conflicting guidance, real context cost), `low` (polish).
- **Confidence**: `high` (mechanical or quoted evidence), `medium` (strong inference), `low` (judgment only).
- **Conflicts with**: what makes it a finding: another file and lines, a fact in the repository, an official doc, or a documented default (`DEF-…`). Every finding names at least one.
- **Evidence level** (for `redundant-with-defaults`): `a` the repository makes it derivable, `b` the official docs document it as default behavior, `c` judgment only (never proposed for removal).
- **Origin**: `deterministic` findings come from the script's own checks; `auditor` findings come from a domain auditor and passed validation.

## Dispositions

`keep`, `remove`, `merge` (with the text to merge into), `move` (with the destination), `revise` (with a proposed replacement), `investigate` (a person must decide). Replacements are proposals; the audit never applies them.

## Review outcome

- **Final**: the reconciler accepted the finding, possibly after a challenge.
- **Open**: the reviewers disagreed after the challenge rounds; both positions are listed, and the user decides.
- **Dismissed**: rejected during reconciliation, listed apart with the reason.

## External claims

Statements about third-party tools, libraries or versions that neither the repository nor the bundled docs can settle. Each has an ID `ACA-EXT-<unit>` and a verdict: `unverified` (not checked), `confirmed`, `outdated`, `contradicted` or `inconclusive`, with sources when checked online.
