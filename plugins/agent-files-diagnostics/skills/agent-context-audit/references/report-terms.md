# Report terms

What each term in an Agent Context Audit report means, for answering the user's questions about it.

## Run status

| Status | Exit code | Meaning |
| :-- | :-- | :-- |
| `complete` | 0 | Every in-scope source was read line by line, every finding was checked, and nothing needs fixing. |
| `complete-with-findings` | 1 | The same full coverage, with findings to review. |
| `partial` | 2 | Something was not covered: a package failed, skipped lines or returned output that failed validation, the review did not finish, a finding was not inspected by the coordinator, or a file or the git state changed during the run. The findings shown passed validation, but the list is not complete. |
| `failure` | 3 | No valid report: an internal error stopped the run, a workflow left no journal, or the report could not be written. |
| `cannot-run` | 4 | A requirement is missing (Python 3.9+, the `claude` CLI 2.1.300+, a POSIX system, dynamic workflows); nothing ran. |

Integrity: every audited file must have the same hash before and after the run, and the git working tree and `HEAD` must be unchanged. The agents can only read, so a difference means someone edited the project during the run, and the run is `partial`.

## Sources

- **Loaded by**: how each tool loads the file: `always` (every session), `conditional` (when a matching path is touched or a condition holds), `on-demand` (when invoked or delegated to), `config` (configuration consulted as evidence), `truncated` (only the first part loads), `shadowed` (another file wins), `excluded` (skipped by a `claudeMdExcludes` pattern), `dead` (never loaded), `not-loaded`.
- **Loading**: the summary of the above: `automatic`, `conditional`, `on-demand` or `unknown`.
- **Consumption**: whether the file was seen to load: `verified` (observed in a session), `documented-not-observed` (the documentation says it loads; this audit observes no session, so this is the usual value) or `unverified` (no documented loader).
- **Availability**: how much of the text the audit could read: `complete`, `truncated`, `inaccessible` or `opaque` (only a subset is audited, such as the MCP part of `~/.claude.json`).
- **Applicability**: `applicable` (it governs something today), `excluded` (a pattern turns it off), `superseded` (another file wins or nothing reads it) or `unresolved`.
- **Evidence only**: managed policy files, third-party folders and configuration (settings, hooks, MCP servers, Codex config). They support findings but are never reported, because the user cannot change them or they are not instructions.
- **Out of scope**: skills, commands and plugin components: listed and counted, never reviewed.

## Findings

- **ID** `ACA-<CAT>-<unit>`: the category code and a hash of the file's display path and the instruction's normalized text. The same instruction keeps its ID across runs, so the change since the last run shows new, resolved and persisting findings. Editing the instruction's wording gives it a new ID.
- **Category**: `false` (a claim the evidence contradicts), `wrong` (a bad command, path, flag, key or version), `obsolete` (deprecated or renamed), `dead` (never loaded, or a broken reference), `ambiguous`, `duplicated`, `overlapping`, `misplaced` (wrong file, scope or tool), `contradictory`, `redundant-with-defaults` (the agent already does it or derives it), `non-conformant` (against the official guidance for that file type).
- **Severity**: `high` (the agent acts wrongly on a normal path, or a file is lost), `medium` (likely confusion, conflicting guidance, real context cost), `low` (polish).
- **Confidence**: `high` (mechanical or quoted evidence), `medium` (strong inference), `low` (judgment only).
- **Conflicts with**: what makes it a finding: another file and lines, a fact in the repository, an official doc, or a documented default (`DEF-…`). Every finding names at least one.
- **Evidence level** (for `redundant-with-defaults`): `a` the repository makes it derivable, `b` the official docs document it as default behavior, `c` judgment only (never proposed for removal).
- **Disposition**: `keep`, `remove`, `merge` (into the file named as target), `move` (to the target), `revise` (with the replacement shown) or `investigate`. Nothing is applied: every disposition is a recommendation.
- **Origin**: `deterministic` (a mechanical check), `auditor:<package>` (a domain auditor) or `reconciler` (a cross-domain finding).
- **Status**: `final` (holds), `open` (two positions stayed unresolved; both are shown), `dismissed` (dropped after the review or the coordinator's inspection; listed under Limitations).
- **Verification**: `independent verifier confirmed`, `refuted` or `unverified`, and `coordinator ok`, a rejection reason, or `not inspected`.

## External claims

Statements about third-party tools or versions that neither the repository nor the bundled knowledge can settle. Each carries a verdict (`confirmed`, `outdated`, `contradicted`, `inconclusive` or `unverified`) and, when checked, the URL, the version or date checked and the quote. An `outdated` or `contradicted` verdict becomes an `obsolete` or `false` finding on the instruction that made the claim.

## Usage

Token counts per agent, summed from each agent's transcript. Cost in money is not available to the audit; the run counts toward the plan's usage limits, which `/usage` shows.
