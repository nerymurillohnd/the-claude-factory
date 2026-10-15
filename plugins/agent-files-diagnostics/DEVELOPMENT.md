# Development record

This file records what is planned for the plugin and what has been verified. It is a development record. It is not an instruction for an audit run, and the skill does not load it.

Last updated: 2026-10-14. Claude Code 2.1.300.

## Scripts

The deterministic steps of the workflow are done by the coordinator by hand today: Phases 2, 4, 7, and 13.1, the symlink table that Phase 2 hands to `evidence-collector` (the agent enumerates with Glob but has no tool that reads a link), and the mechanical part of the Phase 10 coverage check. No script ships yet. The scripts below are part of the plugin and are to be developed. Each one is analyzed together with the agent it supports before it is built.

| Id | Script | Steps it serves | Status |
| :- | :- | :- | :- |
| S1 | `inventory` | Phase 2 baseline counts and symlink table; Phase 3 enumeration, Codex selection, and pointer resolution; part of Phases 7.1 and 7.2 | Prototype tested; to be developed |
| S2 | `protect` | Phase 4: masked working copies and hashes of the originals | Not started |
| S3 | `checks` | Phase 7: references, loading, duplicates, candidates for judgment | Not started |
| S4 | `integrity` | Phase 13.1: rehash, changes and disappearances, Git comparison | Not started |
| S5 | `coverage` | Phase 10: every assigned line reached a reviewer; cited lines and excerpts exist | Not started |
| S6 | `unit-ids` | Normalization: instruction units and stable identifiers | Not started |

### S1 `inventory`

**Origin.** A prototype written by the user (a Bash wrapper with embedded Python). It was run and tested against a fixture on 2026-10-14. Nothing from it is in the plugin yet.

**Consumer.** The coordinator runs it and hands its JSON to `evidence-collector`, which then does not enumerate files by hand. The agent keeps the judgment work: loading modes when the documentation is ambiguous, pointers written as prose, and unrecognized files.

#### Behaviors verified in the prototype, to preserve

| Behavior | Verified |
| :- | :- |
| Codex selection per folder: an empty override is skipped and `AGENTS.md` wins | Yes. It is step 3.3.4 of `evidence-collector` |
| An import inside a fenced code block is ignored | Yes |
| Resolves relative paths and links from the folder of the file, expands `~`, reports `exists` and `inside_root` | Yes. It covers "resolve paths and links" |
| Does not follow directory symlinks, and lists them | Yes |
| Writes only to a new directory and fails if it already exists | Yes. It matches "never overwrite" |
| Exit code 2 when there were errors | Yes |
| No execution, no network, read-only | Yes |

#### Gaps to close, found with the fixture

| Gap | What happened |
| :- | :- |
| Recognizes only `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, `AGENTS.override.md`, and the configured fallback names | Rules, agent definitions, memory files, and `loop.md` in the fixture were counted but not inventoried |
| Sees nothing outside the root | User level, managed policy, and ancestor directories are not inventoried. Those need approved boundaries (Gate 1) |
| No canonical identity | `AGENTS.md` as a symlink to `CLAUDE.md` appeared as two sources with the same six references |
| A quoted import is not distinguished | `"@docs/b.md"` was reported as an ordinary import (check 7.1.2) |
| Anchors are not checked | `docs/a.md#nope` reported `exists: true` (check 7.1.5) |
| False positive | `` `@docs/c.md` `` in inline code was reported as a path that includes the `@` |
| Pointers in prose are missed | "read the file docs/readme-note.md" was not detected. This stays with the agent |
| Frontmatter is detected by delimiters only | A rule with invalid YAML would pass unnoticed |
| No content hash | Phases 4 and 13.1 need one. It has only line and byte counts |
| One level only | An import inside an imported file is not followed |
| No exclusions | It walks `.git` and `node_modules` and records no exclusion list |

#### Conditions to adopt it in the plugin

- Code, comments, and report labels in English.
- Typed, with no suppressions. The prototype did not pass the user's gates: ruff reported dozens of findings (missing annotations and docstrings, `os.path` instead of `Path`, the complexity of `inspect_instruction`, and others) and basedpyright reported errors at the `references.append` call, because one dictionary holds values of different types. Those are fixed by restructuring (dataclasses or `TypedDict`, smaller functions), not by ignoring them.
- Run with `uv`, not a bare `python3`.
- Tests against a fixture that covers every case in the tables above.

#### Fixture cases the tests must cover

A symlink `AGENTS.md` to `CLAUDE.md`; an empty `AGENTS.override.md`; a quoted import; an import in inline code; an import in a fenced block; a link to a missing file; a link with a missing anchor; a pointer written as prose; a rule with invalid frontmatter; an agent definition; a memory index; a `loop.md`; a directory symlink; a pointer to a non-Markdown helper that names a Markdown file.

#### Open design questions

- How the output reaches the agents: whole JSON, or excerpts per package.
- The exclusion list, and where it is recorded.
- The hash algorithm, shared with S2 and S4 so that the hashes are comparable. Until the scripts exist, the coordinator uses `shasum -a 256` (`sha256sum` where `shasum` is missing) and names the command in the report.
- Whether S1 scans the user and managed levels, which depends on the boundaries approved at Gate 1.

## Facts verified on 2026-10-14

Claude Code 2.1.300. Claude Code facts come from the Claude Code docs MCP; Codex facts from `learn.chatgpt.com` and the `openai/codex` releases page.

| Fact | Source and quote | Used in |
| :- | :- | :- |
| Imports recurse to a maximum of four hops | `memory`: "Imported files can recursively import other files, with a maximum depth of four hops." | The Gate 1 depth proposal (one hop more, so the first import too deep to load is recorded) |
| `omitClaudeMd` needs Claude Code 2.1.271 | `sub-agents`, frontmatter table: "Requires Claude Code v2.1.271 or later" | The minimum version in `01_PREREQUISITES.md` and Gate 1 |
| A subagent that lists `Grep` or `Glob` and leaves out `Bash` gets them back | `tools-reference`, Glob tool behavior: "A subagent lists `Glob` or `Grep` in its `tools` field and leaves out `Bash`. The listed tools come back for that subagent only" | The `tools: Read, Grep, Glob` lists of the agents work on macOS and Linux, where the main session has neither tool |
| Grep skips gitignored files; Glob does not | `tools-reference`: "Grep respects `.gitignore`, so gitignored files are skipped"; "Glob doesn't respect `.gitignore` by default" | Collector rule 16, reviewer rule 10, and the enumeration advice in Deterministic steps |
| `TaskStop` stops a running background task by ID | `tools-reference`: "Stops a running background task by ID." | The time limit in Limits to declare |
| Codex memories are off by default, switched on by the `memories` feature flag, and `memories.use_memories` (default `true`) decides whether they are injected | `customization/memories`: "Local Codex memories are off by default."; `config-reference`: "`memories.use_memories`: When `false`, Codex skips injecting existing memories into future sessions. Defaults to `true`." | Collector item 3.3.5 |
| Codex AGENTS.md discovery: override, then `AGENTS.md`, then fallback names, one file per directory | `agent-configuration/agents-md`: "checks for `AGENTS.override.md`, then `AGENTS.md`, then any fallback names" | Collector item 3.3.4 |
| Codex documentation lives on `learn.chatgpt.com`; `developers.openai.com/codex/...` redirects there | Redirect observed for `guides/agents-md` (308) | The admitted domains and `06_OFFICIAL_PAGES.md` |

Not documented: how a subagent result reports usage. The costs page describes a plan-usage breakdown by subagent share in `/usage`, and nothing per run, so section 12 of the report says `unavailable` unless the harness shows the figures.

## Review of 2026-10-14: items C1 to C20

A consolidated review of the skill by three reviewers raised 20 items. Each was checked against the files, and each held. Dispositions:

| Item | Disposition | Where |
| :- | :- | :- |
| C1 Official page list undefined | Fixed: a reference file with the topics and the verified URLs; Gate 1 asks approval; the researcher handles moved pages | `references/06_OFFICIAL_PAGES.md`, `docs-researcher.md` |
| C2 Codex absent; minimum versions | Fixed: Claude Code minimum 2.1.271; Codex has no minimum; `not installed` is a valid answer; "dormant" removed | `01_PREREQUISITES.md`, `docs-researcher.md`, `evidence-collector.md` |
| C3 Gate 1 omits parameters | Fixed: Gate 1 lists every item the file says to propose, and the agent count moved to Phase 8 | `SKILL.md`, Gate 1 |
| C4 Tools, hash, cost source | Fixed: tools and `shasum -a 256` named; usage comes from the harness or is `unavailable` | `SKILL.md`, Deterministic steps and Report conventions; `14_REPORT.md` |
| C5 Reference 10 cites missing items | Fixed: maps items 1 to 12 of the verifier | `10_COVERAGE_AND_VALIDATION.md` |
| C6 Managed `CLAUDE.md` | Fixed, a decision to confirm: evidence only, as in the original prompt; reviewers receive it to cite, nobody reviews it | `SKILL.md` Scope, all agents |
| C7 Next-session notice | Fixed: removed from the Gate 1 list | `SKILL.md`, Gate 1 |
| C8 Domains fixed or adjustable | Fixed another way: domains stay fixed and a package may hold several | `SKILL.md` Scope, `08_AUDIT_PLANNING.md`, `instruction-reviewer.md` |
| C9 Several pointers; collector vocabulary | Fixed: tie-break by order A to E; the collector uses A to E | `SKILL.md` Scope, `evidence-collector.md` 3.4 |
| C10 Isolation note in reference 09 | Fixed: points to Limits to declare | `09_INDEPENDENT_DOMAIN_REVIEW.md` |
| C11 Severity | Fixed: three levels and three confidence levels; the coordinator sets the final severity in Phase 11 | `SKILL.md`, `instruction-reviewer.md` |
| C12 Phase 7 thresholds | Fixed: exact duplicates are mechanical; the rest are candidates; undocumented thresholds are chosen, approved at Gate 1, and reported | `07_MECHANICAL_CHECKS.md`, `SKILL.md` |
| C13 `dead` against `non-conformant`; excluded files | Fixed: a cut file is `dead` only; an excluded file is `not loaded` and raises no finding | `SKILL.md`, `07_MECHANICAL_CHECKS.md` |
| C14 Pointer depth | Fixed: one rule, helpers count as a hop, default one hop beyond the documented import depth | `SKILL.md` Scope, `evidence-collector.md` |
| C15 Narrower request; "This prompt" | Fixed: the user may narrow, never widen; wording changed | `SKILL.md` |
| C16 Out-of-scope requests; "next phase" | Fixed: one paragraph, and Gate 3 wording | `SKILL.md` |
| C17 Phase 11 findings unvalidated | Fixed: `audit-verifier` runs again, on the new findings only | `SKILL.md`, `audit-verifier.md`, `11_CROSS_DOMAIN_RECONCILIATION.md` |
| C18 13.2 checks a report that does not exist | Fixed: the verifier checks the agent reports; Phase 14 checks the finished report | `audit-verifier.md`, `14_REPORT.md` |
| C19 Pre-flight against sequential fallback | Fixed: one behavior, with the lost independence declared | `SKILL.md`, Pre-flight and Limits |
| C20 Writes missing from the list | Fixed: hash table, run-state file, and scripts added; a record of writes kept | `SKILL.md`, Write boundary and Run state |

Added beyond the review: the gitignore rule for Grep (collector rule 16, reviewer rule 10), and the exact Codex memory keys in collector item 3.3.5.

## Second review of 2026-10-14: items C4 to C17 and S1 to S6

A second consolidated review arrived with some rows cut off in transit, so each row was judged by the evidence lines it cites. Several items were already closed by the first round. Dispositions:

| Item | Disposition | Where |
| :- | :- | :- |
| C4 Domains fixed or adjustable; several parents | Closed in round 1 (C8, C9). Added the example of an `AGENTS.md` that a `CLAUDE.md` imports: it stays in A | `SKILL.md` Scope, `instruction-reviewer.md` |
| C5 Managed `CLAUDE.md` | Closed in round 1 (C6) | |
| C6 Writes missing from the boundary | Closed in round 1 (C20) | |
| C7 Severity | Closed in round 1 (C11) | |
| C8 Reference 10 | Closed in round 1 (C5) | |
| C9 Deterministic phases without method | Fixed: masking patterns, a definition of each unit, and Phase 7 reads the masked copies. The hash was closed in round 1 | `04_CONTENT_PROTECTION.md`, `07_MECHANICAL_CHECKS.md`, `SKILL.md` Deterministic steps |
| C10 Requests in the approval message; narrowed scope | Fixed: one run audits one repository, a narrowing is applied, a widening is declined, and the status carries `narrowed` | `SKILL.md` Gate 2 and Scope, `14_REPORT.md` |
| C11 Phase 11 ownership and format | Fixed: what a dispute is, the answer format, the ban on consuming findings lifted for that message, and adjusted findings revalidated | `SKILL.md`, `11_CROSS_DOMAIN_RECONCILIATION.md`, `instruction-reviewer.md` |
| C12 Identical units | Fixed: the sentence in `SKILL.md` now says same context. Reference 07 was closed in round 1 | `SKILL.md` |
| C13 Changed source | Fixed: one rule. A changed source makes the audit partial and its findings are revalidated; stale findings also make it partial; a git change alone does not | `13_INTEGRITY_AND_FINAL_VERIFICATION.md` |
| C14 Pointer depth against import depth | Fixed: the two depths are independent; the plan decides how far to look and the documented limit decides whether an import loads | `SKILL.md` Scope, `evidence-collector.md` 3.1.6 |
| C15 Provisional identifier | Fixed: the unit identifier uses the text, not a line number, and leaves the category out, so a recategorized finding keeps its unit. A finding is `<unit id>#<category>` | `SKILL.md` Normalizing findings, `12_EXTERNAL_VERIFICATION_AND_RUN_HISTORY.md` |
| C16 "This specification", "this prompt" | Fixed: Gate 1 names the user's request, the workflow, and the plan. The mapping to the original prompt moved here | `SKILL.md`, this file |
| C17 Trigger says "clean up" | Fixed: the description says the skill only reports, and Gate 1 says it too | `SKILL.md` |
| S1 Claims carry repository content | Fixed: the coordinator cuts each claim to four fields and rewrites any sentence with a private detail; reviewers write claims without private detail; the researcher ignores extra fields | `SKILL.md`, `instruction-reviewer.md`, `docs-researcher.md` |
| S2 13.2 verifies a report that does not exist | Closed in round 1 (C18) | |
| S3 Late claims skip external verification | Fixed: a further 12.1 batch before Phase 13 | `SKILL.md` Order of execution, `12_EXTERNAL_VERIFICATION_AND_RUN_HISTORY.md` |
| S4 Reviewer compares against files it does not receive | Fixed: reference copies of the other sources, the whole inventory, and no repository root | `SKILL.md` Delegation messages, `instruction-reviewer.md` |
| S5 Pre-flight failure | Closed in round 1 (C19) | |
| S6 Symlinks with Read, Grep, and Glob | Fixed: Phase 2 records a symlink table and the collector requires it; the note in the Scripts section was wrong and is corrected | `02_BASELINE_SNAPSHOT.md`, `evidence-collector.md` |

The masking patterns were run once with `perl -pe` on a scratch fixture of 18 lines that is not in the plugin. The line count stayed the same, branch names and prose were untouched, and the run found two defects that are now fixed in the text: a closing quote eaten by the `Authorization` value, and a quoted value that went unmasked. The GitHub prefixes and the AWS `AKIA` and `ASIA` prefixes were checked against their official pages on 2026-10-14; the lengths in the patterns are conservative minimums, not documented sizes. Script S2 will carry the real tests.

## Mapping from the original prompt

The skill started as a 457-line prompt. Changes that a reader of the original needs to know:

- Categories: `incorrect` became `wrong`; `duplicate` became `duplicated`; `ineffective loading or truncation risk` became `dead`; `stale memory` became `obsolete`; `inappropriate memory` became `misplaced`; `ambiguous or unverifiable` became `ambiguous`; `redundant with runtime defaults` and `readily discoverable from the repository` became `redundant-with-defaults`; `non-conforming` became `non-conformant`. `unsupported` has no category: a claim nobody can support is a claim to verify.
- Phase 12.1 always runs; the original ran it only on request.
- The network exception in the write boundary now includes GitHub and package registries.
- The first person became "the user".
- Gate 2 "isolated sessions" became background subagents with their own context, at the user's cost; Phase 9 "isolated" became "each in its own context".
- Step 7.4 (configuration) was removed and 7.5 was renumbered; configuration is now loading evidence only.
- Step 14.3 offers to retry the claims that stayed inconclusive.

## Other open work

- Check frontmatter with a YAML parser as well as with `claude plugin validate --strict`. On 2026-10-14 the validator passed a `description` that held a colon followed by a space, which a strict parser (Ruby's Psych) rejected.
- `maxTurns` for the reviewers. The value is the user's decision.
- A hook that guards `WebFetch` for `docs-researcher`. It needs the approved list of admitted domains.
- An isolated installation test of the plugin, with a throwaway configuration directory.
- A decision about the existing `agent-context-audit` plugin in the factory: replace it, or coexist.
- A marketplace entry, a README, a LICENSE, and a CHANGELOG.
- A session-start hook, which the next-session notice of Phase 12.2 needs.
- Confirm whether the Codex memory files are Markdown.
