# Repository audit of 2026-11-01: consolidated findings and their final state

## Source and method

- **Audited state:** `main` at 33e48f685f401e0a30e86f83cd103c5175281566, equal to `origin/main`, clean tree.
- **Input:** Nery's consolidated report of five audits (5 medium, 20 low, 6 informational findings and a list of what was not verified).
- **This pass:**
  - Three read-only agents checked what was still unverified: READMEs against code in two halves, and dangling objects with signatures.
  - A fourth agent derived each plugin's minimum Claude Code version from the official CHANGELOG.
  - The main session repeated every decisive check (CI logs, release notes, engine declarations, workflow logs, settings) and confirmed each "wrong claim" before fixing it.
- **Decisions:** Nery took them on 2026-11-01 before execution; they are listed with each finding.
- **Backup:** `~/Claude/backups/the-claude-factory/2026-11-01-audit/`, made before any change.
  - `all.bundle`, the whole repository, with `refs/repo-cleanup-backup/stash-0` and `refs/repo-cleanup-backup/lost-a57621d`.
  - `stash-0.patch` and `manifest.txt`, with the checksums and the restore commands.
  - It was verified with `git bundle verify`, and the rescue refs were removed afterwards.

## What was unverified, now verified

| Item | Result | Evidence |
| :-- | :-- | :-- |
| Logs of the 20-Oct runs | 39477911261 and 39472572712 failed the version-bump gate on the revert of #27. 39445956971 and 39445942223 failed a TypeScript hook test that later PRs fixed. 39474233609 and 39474033930 are Validate runs with no jobs. All are superseded. | `gh run view --log-failed`, `actions/runs/<id>/jobs` |
| The three failures of the removed Evals workflow | 40224316519, 38297567893 and 38246672629 ran their suites and wrote results; exit 1 came from the graders. No artifacts are left, so the failing cases cannot be recovered. c748041 removed the workflow, and DEBT-043 tracks its rebuild. | run logs; artifacts API empty |
| The 56 dangling blobs and the dangling commits | Nothing unique. Of the commits, 15 are on main, 17 on main as amended copies and 24 superseded; the blobs are replaced drafts. Unique content sits only in unreachable parents: the instruction-engineering evals, which Nery chose not to keep (ADR_2026-11-01_instruction-engineering-keeps-no-evals), and a57621d, which is kept in the backup bundle (DEBT-043). | patch-id, `cat-file`, `show --stat` |
| Minimum Claude Code versions | Each floor was derived from the features and fixes each plugin needs, and 13 changed (table below). Engine declarations back project-maintainer's 2.1.307. | `anthropics/claude-code` CHANGELOG; `index.d.ts` declarations; 915e71e |
| Signatures before 113b025 | Of 994 commits on main, 988 verify. Two are `unsigned` (9c6ae56 and b0c6474, from `/install-github-app`) and four `unknown_key` (c441921, f2854bc, e1dd69d and 27b61da). All 45 commits after 113b025 verify. | `gh api commits`; ADR_2026-11-01_unverified-history-commits-stay-unrewritten |
| `~/.claude/tasks` and caches | 130 directories of `.lock` and `.highwatermark` files (284 KB), which are Claude Code's task store and inert. The directories that answer Permission denied are not Nery's, and were left. | `find`, `du` |
| Whether each README matches its plugin | About 40 mismatches across the 21 plugins, all fixed (N-02). | three agent passes, each claim checked against the code line |

## Findings and final state

### Medium

| ID | Final state | Evidence |
| :-- | :-- | :-- |
| M-01 claude-review red on Dependabot PRs | **Fixed.** The report's cause was wrong. #75 was green only because the action skipped itself on a PR that changes its workflow; 1.0.264 and 1.0.265 change nothing about bots; and Dependabot runs get no Actions secrets, so the OAuth token is empty there. The job now skips Dependabot's PRs, and #76 shows `claude-review` SKIPPED. 7854162 had re-pinned the workflows against the accepted ADR; the new ADR records that choice. | db33556; ADR_2026-11-01_claude-workflows-pin-by-sha-and-skip-dependabot |
| M-02 unique work in stash@{0} | **Backed up and logged.** The stash is kept, by Nery's choice. | backup bundle; DEBT-044 |
| M-03 root CHANGELOG missing **Breaking:** | **Fixed** on six lines, plus github-operations 0.3.0, which is not breaking and lost the mark. | c622de0; #78 |
| M-04 Hooks rows against the matrix | **Fixed.** The matrix gains a note on hooks that run a program, and the four LSP READMEs use the matrix cell, each naming the programs its hooks need. The report misquoted the two TypeScript rows. | 861e3bd; #78 |
| M-05 release depends on a retired skill | **Fixed.** The live scripts moved to `scripts/release/`, the unused copies and their identity test were removed, and the script rules name the new folder. | e36afa5, 0245a63; ADR_2026-11-01_release-scripts-live-in-scripts-release |

### Low

| ID | Final state | Evidence |
| :-- | :-- | :-- |
| B-01 release body of github-operations--v0.1.0 | **Fixed** after #78 merged (e2fc64a), from its final 0.1.0 section; `releases` now compares each Release body with its section. | `gh release edit`; 0e002f5 |
| B-02 unverified commits | **Recorded, not rewritten.** | ADR_2026-11-01_unverified-history-commits-stay-unrewritten |
| B-03 dangling objects | **No action:** nothing unique, no `gc`. | see above |
| B-04 `.git/lost-found` | **Removed.** `git fsck --connectivity-only` is clean and HEAD is unchanged. | — |
| B-05 Actions defaults | **Fixed.** `default_workflow_permissions` is `read` and `sha_pinning_required` is `true`. All four workflows declare permissions and pin every action by SHA. | `gh api …/actions/permissions[/workflow]` |
| B-06 changelog dates | **Convention set:** a heading takes the tag's UTC day, and old dates stay as they are. | 0e002f5 (`releases`) |
| B-07 Breaking marks in plugin changelogs | **Fixed:** python-lsp 0.2.0 (`python3`, removed runner), bash-lsp 0.2.0 (removed runner), github-operations 0.3.0 (mark dropped) and 0.1.0 (`python3` stated). | #78 |
| B-08 prompt-writer line in the wrong version | **Fixed.** The explicit start (breaking) and the checklist moved to 0.1.1. | #78 |
| B-09 "eight issue forms" | **Fixed:** seven, plus `config.yml`. | #78 |
| B-10 `### Restored` | **Folded into Changed**, without the commit reference. | #78 |
| B-11 missing period | **Fixed.** | c622de0 |
| B-12 thin 0.1.0 entries | **Expanded** for instruction-engineering and macos-grep-guard. | #78 |
| B-13 icon and `privacyPolicyUrl` | **No action:** Claude Code ignores them, and they matter only for a listing in Anthropic's directory (`/en/plugins/manifest-reference` → Directory listing fields). | docs |
| B-14 one-word keywords | **Fixed** for both plugins. | #78 |
| B-15 `${user_config.*}` in a local MCP server | **No action:** the matrix row for a local MCP server already covers it. | `docs/compatibility.md` |
| B-16 marketplace tags without a `renames` entry | **No action:** they are the marketplace's own tags, and `renames` maps plugins only. | — |
| B-17 blocked job 37b37c09 | **Nery's action:** resume or discard it from the fleet view. | `~/.claude/jobs/37b37c09/state.json` |
| B-18 Claude.app started during the audit | **Nery's action:** confirm he opened it. | — |
| B-19 stale socket and roster | **Removed:** `/private/tmp/cc-socks/4619.sock` and `~/.claude/daemon/roster.json` (pid 61648 gone). `~/.claude/security` was not touched. | `ps -p` |
| B-20 ignored residue | **No action:** nothing ships. | — |

### Informational

I-01 to I-06 need no action. I-05 was not a duplicate: the second entry is a project-scope install for another project.

### New in this pass

| ID | Final state | Evidence |
| :-- | :-- | :-- |
| N-01 an ADR pointed at evals that do not exist | **Corrected:** instruction-engineering keeps no evals. | ADR_2026-11-01_instruction-engineering-keeps-no-evals |
| N-02 about 40 README mismatches | **Fixed.** Notable ones: block-no-verify's "only blocks" answer, notebooks in python-lsp, the dead `#-requirements` link in the TypeScript hooks, prompt-writer's undisclosed `Stop` hook, and missing "What this plugin runs and sends" sections. | d5853ef; #78 |
| N-03 floors not backed by evidence | **Fixed** with the rule Nery set: the lowest version that runs the plugin without friction. | `building-plugins` → `references/readme-style.md`; table below |
| N-04 code defects found while fixing | **Fixed with tests:** the TypeScript 7 removed-option message, the `ts-lifecycle` pre-approval (against the rule that plugins never pre-approve tools), the `GIT_EXEC_PATH` denial message, and `detectComponents` missing hooks in skill frontmatter. | #78 |

## Releases and pull requests

- [#78](https://github.com/nerymurillohnd/the-claude-factory/pull/78) merged as e2fc64a. Validate and Release succeeded, and Release tagged exactly the eight versions: bash-lsp-intelligence 0.2.6, python-lsp-intelligence 0.3.1, typescript6-lsp-intelligence 0.3.2, typescript7-lsp-intelligence 0.4.2, github-operations 0.5.1, prompt-writer 0.2.2, macos-grep-guard 0.1.2 and instruction-engineering 0.1.1. Each installs from `main` at that version, and each Always-on figure is unchanged.
- [#76](https://github.com/nerymurillohnd/the-claude-factory/pull/76) (setup-uv 10.3.3) merged as 20215bd; [#75](https://github.com/nerymurillohnd/the-claude-factory/pull/75) (claude-code-action 1.0.265) merged after it, as be10847. On both, `claude-review` was skipped.
- [#77](https://github.com/nerymurillohnd/the-claude-factory/pull/77) (TypeScript 7.0.2) was closed by Dependabot once the major-version ignore landed, with a comment saying why.
- After #78, nine Release bodies differ from their corrected changelog sections: github-operations 0.3.0, 0.4.0 and 0.5.0, prompt-writer 0.1.1 and 0.2.0, python-lsp-intelligence 0.2.0, bash-lsp-intelligence 0.2.0, instruction-engineering 0.1.0 and macos-grep-guard 0.1.0. Editing a Release body is public content, so it waits for Nery's go-ahead.

## Minimum Claude Code versions

| Plugin | Before | After | What sets it |
| :-- | :-- | :-- | :-- |
| bash-lsp-intelligence, python-lsp-intelligence, svelte-development | 2.1.292, 2.1.292, 2.1.303 | 2.1.288 | language-server requests time out instead of hanging |
| block-no-verify, github-operations | 2.1.295 | 2.1.314 | Bash hooks also check Monitor commands |
| file-tree-pane, model-trace | 2.1.299 | 2.1.299 | `Text` weights and sizes draw |
| tool-ledger | 2.1.295 | 2.1.299 | the panel draws |
| hook-engineering | 2.1.292 | 2.1.222 | `metadata` in the manifest |
| instruction-engineering | 2.1.271 | 2.1.271 | `omitClaudeMd` |
| skill-diagnostics | 2.1.176 | 2.1.271 | `omitClaudeMd` |
| macos-grep-guard | 2.1.287 (2.1.286 Desktop) | 2.1.292 | `tool.call` sees repaired arguments |
| mods-engineering | 2.1.292 | 2.1.295 | the type-file behavior the skill teaches |
| plugin-evals, plugin-test-bench | 2.1.269, 2.1.293 | 2.1.299 | an API error fails a run |
| project-maintainer | 2.1.307 | 2.1.307 | a mod's ask reaches a person (engine declarations) |
| prompt-writer | 2.1.292 | 2.1.294 | hooks written as instructions block |
| tailwind-development | 2.1.292 | 2.1.281 | MCP-tool hooks wait for their server |
| turn-meter, typescript6-lsp-intelligence, typescript7-lsp-intelligence | 2.1.295 | 2.1.295 | `$.ui.notify`; `onFailure` |

### Unverified

- No build older than 2.1.312 is on disk, so no floor was run live.
- tailwind-development's 2.1.281 relies on a fix that names "PreToolUse and similar" events; that it covers PostToolUse is an inference.
