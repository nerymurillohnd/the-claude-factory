# Check claude-code-action drift

The facts in [action-contract.md](action-contract.md) describe `anthropics/claude-code-action` at one verified commit, the snapshot below. A workflow can run any other commit, and upstream ships several releases a day. This page tells you, the same way every time, which facts hold for the commit a step runs.

Run it once per claude-code-action step a route touches, before you rely on any fact from `action-contract.md`.

**Contents**
- [Snapshot](#snapshot)
- [Source files](#source-files)
- [Find the commit a step runs](#find-the-commit-a-step-runs)
- [Pick the newest release](#pick-the-newest-release)
- [Compare with the snapshot](#compare-with-the-snapshot)
- [When the pin is older than the snapshot](#when-the-pin-is-older-than-the-snapshot)
- [A version bump is a patch](#a-version-bump-is-a-patch)
- [When nothing can be read](#when-nothing-can-be-read)

## Snapshot

| claude-code-action | Commit | Claude Code bundled | Agent SDK locked | GitHub MCP server image | zizmor | actionlint | Checked |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| v1.0.275 | `4d75e5f390ee76b2e09c1980ecc99ff3a2e088c8` | 2.1.323 | 0.3.323 | `ghcr.io/github/github-mcp-server:sha-23fa0dd` (v0.17.1) | 1.32.0 | 1.7.12 | 2026-11-13 |

Dated facts other references rely on, checked on 2026-11-13. Re-check one before you rely on it after its date:

- **`pull_request_target` default policy.** GitHub adds a default policy that blocks `pull_request_target` in public repositories that have no Actions event policy. It runs in evaluate mode now; enforcement for affected repositories begins on 2026-12-02.
- **`actions/checkout` credential layout, checked at v7.0.1 (`3d3c42e`).** v6.0.0 and later keep the token in a file under `$RUNNER_TEMP`, which the local `.git/config` includes through an `includeIf` entry. v5.0.1 and earlier, and the backports v5.1.0 and v4.4.0, keep it in the local `.git/config`. v7 and the backports refuse to check out a fork's code under `pull_request_target` or `workflow_run` unless `allow-unsafe-pr-checkout: true` is set.
- **GitHub-hosted runner labels.** `macos-14` was retired on 2026-11-02. `ubuntu-slim` has a 15-minute job limit.
- **`anthropics/claude-plugins-official`** publishes no version tags: pin it by commit.

## Source files

Every path that a `Sources:` line in `action-contract.md` names, with its blob at the snapshot. A changed blob makes the topics on its row unverified until you read the change. A path that isn't here holds none of the skill's facts.

| Path | Blob at the snapshot | Topics |
| :-- | :-- | :-- |
| `action.yml` | `1ad93d0dd466589dfdc703074e451cd95aab21fc` | [Inputs and outputs](action-contract.md#inputs-and-outputs), [Untrusted pull requests](action-contract.md#untrusted-pull-requests), [Git, branches and credentials](action-contract.md#git-branches-and-credentials), [GitHub token and the Claude App token](action-contract.md#github-token-and-the-claude-app-token), [Inference credentials](action-contract.md#inference-credentials), [Comments, reviews and structured output](action-contract.md#comments-reviews-and-structured-output), [Removed inputs](action-contract.md#removed-inputs), [Environment variables the action passes](action-contract.md#environment-variables-the-action-passes) |
| `base-action/action.yml` | `866689cc1b21a775b7bcc3b4480e18605cd33cc1` | [Inputs and outputs](action-contract.md#inputs-and-outputs), [Claude Code version, models and auto availability](action-contract.md#claude-code-version-models-and-auto-availability) |
| `base-action/package.json` | `223ac6b6f00fe5708551cbd1778f48427005d180` | [Claude Code version, models and auto availability](action-contract.md#claude-code-version-models-and-auto-availability) |
| `base-action/src/install-plugins.ts` | `0eb12e74472801d2c4685457f66bb2e28123b4f8` | [Plugins and marketplaces](action-contract.md#plugins-and-marketplaces) |
| `base-action/src/parse-sdk-options.ts` | `dc7c3c11c7a939f47d40f374d709b2bb399805e6` | [Permission mode](action-contract.md#permission-mode), [Tools the action grants and the MCP servers it starts](action-contract.md#tools-the-action-grants-and-the-mcp-servers-it-starts), [Claude Code version, models and auto availability](action-contract.md#claude-code-version-models-and-auto-availability), [Environment variables the action passes](action-contract.md#environment-variables-the-action-passes) |
| `base-action/src/run-claude-sdk.ts` | `1fd4d84427de2b99fdf21ae6a13797ffb0817c31` | [Permission mode](action-contract.md#permission-mode), [Claude Code version, models and auto availability](action-contract.md#claude-code-version-models-and-auto-availability) |
| `base-action/src/validate-env.ts` | `7fc17be9172a91228021015003579aa5935b16b2` | [Inference credentials](action-contract.md#inference-credentials) |
| `base-action/src/workload-identity.ts` | `79ebaf50e6649b100d8eb5e21681fb81f04f5b05` | [Inference credentials](action-contract.md#inference-credentials) |
| `src/create-prompt/index.ts` | `c43e9abf4f700b07e77fbf4fd50651d7a3465d91` | [Actor and text trust](action-contract.md#actor-and-text-trust) |
| `src/entrypoints/collect-inputs.ts` | `919e98394bd4606532a84821cba17012ed46096f` | [Inputs and outputs](action-contract.md#inputs-and-outputs) |
| `src/entrypoints/post-buffered-inline-comments.ts` | `9283baf65c652580e68a4652f7f4031e42c4b3c2` | [Comments, reviews and structured output](action-contract.md#comments-reviews-and-structured-output) |
| `src/entrypoints/run.ts` | `369767240f65e0aa4ad39c4d9d5f2e4c48980b31` | [Permission mode](action-contract.md#permission-mode), [Untrusted pull requests](action-contract.md#untrusted-pull-requests), [Configuration restored from the base branch](action-contract.md#configuration-restored-from-the-base-branch), [Session guard](action-contract.md#session-guard), [GitHub token and the Claude App token](action-contract.md#github-token-and-the-claude-app-token), [Comments, reviews and structured output](action-contract.md#comments-reviews-and-structured-output), [Claude Code version, models and auto availability](action-contract.md#claude-code-version-models-and-auto-availability) |
| `src/github/context.ts` | `9826b0cca0a6cd0d31144ee32c96a0180f735de5` | [Modes and triggers](action-contract.md#modes-and-triggers) |
| `src/github/data/fetcher.ts` | `fe68bbc2fe87902f1251487af29f8f94d0a935cb` | [Actor and text trust](action-contract.md#actor-and-text-trust) |
| `src/github/operations/branch.ts` | `bfd68ea765c8e1d16ab36d60b550168ce8f59170` | [Configuration restored from the base branch](action-contract.md#configuration-restored-from-the-base-branch), [Git, branches and credentials](action-contract.md#git-branches-and-credentials) |
| `src/github/operations/git-config.ts` | `446a3aac6c95095ac144e545ef63826fcae985db` | [Git, branches and credentials](action-contract.md#git-branches-and-credentials) |
| `src/github/operations/restore-config.ts` | `bdd55761fa50c5cea06c897c3e8624ce2348669f` | [Configuration restored from the base branch](action-contract.md#configuration-restored-from-the-base-branch) |
| `src/github/operations/session-guard.ts` | `a35cb08ba818f97d33348b45a1cf4644d7a5d9de` | [Session guard](action-contract.md#session-guard) |
| `src/github/token.ts` | `c5f03a28ecbd6271fbfacc56f7fbf2390d16633e` | [GitHub token and the Claude App token](action-contract.md#github-token-and-the-claude-app-token) |
| `src/github/validation/actor.ts` | `717705c3a17ab7deba45adcd0f25f7d2a8474fe8` | [Actor and text trust](action-contract.md#actor-and-text-trust) |
| `src/github/validation/permissions.ts` | `b3aa850fd10e3ee12e4b4bddd22718c447f5486d` | [Actor and text trust](action-contract.md#actor-and-text-trust) |
| `src/github/validation/trigger.ts` | `6065aad59ef95d4b23e13cf6576ea47e720b00f0` | [Modes and triggers](action-contract.md#modes-and-triggers), [Actor and text trust](action-contract.md#actor-and-text-trust) |
| `src/github/validation/untrusted-pr.ts` | `01650ea0b5019376549e0192ec602b70c7492107` | [Untrusted pull requests](action-contract.md#untrusted-pull-requests) |
| `src/mcp/install-mcp-server.ts` | `402617e421924e796cba4fa0b83401e91f943d0d` | [Tools the action grants and the MCP servers it starts](action-contract.md#tools-the-action-grants-and-the-mcp-servers-it-starts), [Comments, reviews and structured output](action-contract.md#comments-reviews-and-structured-output) |
| `src/modes/agent/index.ts` | `d402594e2fd877b45da3f2e592b56a429f2ff9f2` | [Permission mode](action-contract.md#permission-mode), [Tools the action grants and the MCP servers it starts](action-contract.md#tools-the-action-grants-and-the-mcp-servers-it-starts), [Git, branches and credentials](action-contract.md#git-branches-and-credentials) |
| `src/modes/detector.ts` | `46e1366513359e0df14159dcb99ac818a8040770` | [Modes and triggers](action-contract.md#modes-and-triggers), [Actor and text trust](action-contract.md#actor-and-text-trust) |
| `src/modes/permission-mode.ts` | `311101128bfc30e0fa097b4c9db8ea3990a2c7b5` | [Permission mode](action-contract.md#permission-mode) |
| `src/modes/tag/index.ts` | `accbe801e302e0a1b5aea9dc486e456235a81e38` | [Permission mode](action-contract.md#permission-mode), [Tools the action grants and the MCP servers it starts](action-contract.md#tools-the-action-grants-and-the-mcp-servers-it-starts) |
| `src/utils/branch-template.ts` | `f9fac933250546edf3d184b07d62b9397aaade1f` | [Git, branches and credentials](action-contract.md#git-branches-and-credentials) |
| `scripts/git-add.sh` | `e5bb92da6b92aa2cb01fd2306d74e5ba66f37ebf` | [Git, branches and credentials](action-contract.md#git-branches-and-credentials) |
| `scripts/git-commit.sh` | `6ed5647c3c4a35e35a656d8157b5126342022302` | [Git, branches and credentials](action-contract.md#git-branches-and-credentials) |
| `scripts/git-env.sh` | `9f01465ddfc5b7597692e2bcad50fa21966e75cd` | [Git, branches and credentials](action-contract.md#git-branches-and-credentials) |
| `scripts/git-push.sh` | `4421ccb66e215e009ac046e43007cb03ab3173ea` | [Git, branches and credentials](action-contract.md#git-branches-and-credentials) |
| `scripts/git-rm.sh` | `871b9a0c9a50529a3c854725044e8115a2d2d0a2` | [Git, branches and credentials](action-contract.md#git-branches-and-credentials) |
| `docs/security.md` | `0f27b281cad75fe9cc0f771843efba7a9d0046e9` | [Actor and text trust](action-contract.md#actor-and-text-trust), [Untrusted pull requests](action-contract.md#untrusted-pull-requests), [Environment variables the action passes](action-contract.md#environment-variables-the-action-passes) |

## Find the commit a step runs

1. **Find the step.** It is a `uses: anthropics/claude-code-action@<ref>` line. When a workflow calls a composite action (`uses: ./path` or `owner/repo/path@ref`) or a reusable workflow, open that file at the ref the caller pins and find the step there.
2. **Check the owner and name.** Any `uses:` other than `anthropics/claude-code-action` is not an upstream commit, even when the code looks the same. Report it as "not an upstream commit", count every fact for that step as unverified, and raise W-04 ([workflow-audit.md](workflow-audit.md#checks-every-workflow-gets)).
3. **Resolve the ref.**
   - A full 40-character SHA is the commit. Confirm that upstream has it: the fetch in [Compare with the snapshot](#compare-with-the-snapshot) fails with `fatal: remote error: upload-pack: not our ref <sha>` when it doesn't. Treat that answer exactly like step 2.
   - A tag or branch, such as `v1` or `v1.0.275`:

     ```
     git ls-remote https://github.com/anthropics/claude-code-action <ref> '<ref>^{}'
     ```

     When a line ending in `^{}` prints, its SHA is the commit: the other line is an annotated tag object, not a commit. When only one line prints, its SHA is the commit. When a branch and a tag both print, report both, and take the commit from a run's log (next bullet) if one exists. With MCP only, `list_tags` (or `list_branches` for a branch) gives the commit of each name.
   - A past run: the "Set up job" log of that job has the line `Download action repository 'anthropics/claude-code-action@<ref>' (SHA:<sha>)`. That SHA is what the run executed, whatever the ref points to now.
4. **A floating ref** (`v1`, `main`) runs whatever it points to when the job starts. Audit the commit it resolves to today, say so in Version provenance, and recommend a SHA pin (W-04).

## Pick the newest release

Use this when a patch pins or bumps the action. It needs git 2.18 or later and no clone. It keeps only exact `vX.Y.Z` tags, sorts them by version, and prints the newest with its commit, taking the `^{}` line for an annotated tag:

```
git ls-remote --tags --sort=-v:refname https://github.com/<owner>/<action> | awk '$2 ~ /^refs\/tags\/v[0-9]+\.[0-9]+\.[0-9]+(\^\{\})?$/ { t=$2; sub(/\^\{\}$/,"",t); if (!seen) { seen=t } if (t==seen) { sha=$1; if ($2 ~ /\^\{\}$/) peeled=$1 } } END { print seen, (peeled?peeled:sha) }'
```

- It prints a line such as `refs/tags/v1.0.275 4d75e5f390ee76b2e09c1980ecc99ff3a2e088c8`. Pin the commit and keep the tag as a comment: `uses: anthropics/claude-code-action@<commit> # v1.0.275`.
- Never take the last line of a plain `git ls-remote --tags`: its order is lexical, so it ends at `v1.0.99`.
- Stay in the pin's current major unless the user approves a jump. To keep the major, replace `v[0-9]+` in the pattern with the major, for example `v1`. A jump lists the breaking changes from the release notes as residual risk.
- With MCP only: `get_latest_release` gives the tag GitHub marks as latest, and `list_tags` gives its commit. Check that the tag is in the current major.

The same pipeline works for any action, for example `actions/checkout`.

## Compare with the snapshot

Do this for the commit from [Find the commit a step runs](#find-the-commit-a-step-runs) (`<pin>` below). `<snapshot>` is the commit in the Snapshot table. When the two are equal, every fact in `action-contract.md` holds; skip to Version provenance.

**With git** (Claude Code with a shell):

```
TMP=$(mktemp -d)
git init -q "$TMP" && git -C "$TMP" fetch -q --filter=blob:none --depth=1 https://github.com/anthropics/claude-code-action <snapshot> <pin>
git -C "$TMP" diff --name-only <snapshot> <pin> -- action.yml base-action/action.yml base-action/package.json base-action/src src scripts docs/security.md
```

The fetch downloads trees, not file contents, so it takes about a second. Read the list it prints:

- **Nothing printed:** every fact holds at the pin, whatever its version number.
- **A path in the Source files table:** the topics on its row are unverified. Read `git -C "$TMP" diff <snapshot> <pin> -- <path>`, then apply what the code at the pin says, not what `action-contract.md` says. Name each such topic in Version provenance.
- **A path not in the table:** an unmapped change. Read its diff and say in Version provenance whether it changes anything the route relies on.

Delete `$TMP` when you're done.

**With MCP only:** list each directory that holds a Source files path with `get_file_contents` at `sha: <pin>` (for example `src/modes`). Each entry carries its blob `sha`. A blob different from the table makes that row's topics unverified until you read the file at the pin. Unmapped changes can't be seen this way: say in Version provenance that they weren't checked.

**Release notes, either way.** Read every release between the snapshot and the pin (`get_release_by_tag` or `list_releases`, or the repository's Releases page). Breaking releases are titled `<version> (breaking changes)` and carry a `### ⚠️ Breaking changes` heading, but that label isn't guaranteed: v1.0.275 changed how the git wrappers treat `GIT_SSH_COMMAND` without it, and v1.0.274's notes don't mention its Claude Code bump. The notes are a second signal, never a replacement for the comparison. When no route can read them (no `gh`, MCP or web), say so in Version provenance and let the comparison decide.

## When the pin is older than the snapshot

Compare exactly as above: the diff shows what the snapshot added. Every topic on a changed row is described by the code at the pin, not by `action-contract.md`. These releases changed behavior the routes rely on:

| Release | What it added |
| :-- | :-- |
| v1.0.273 (breaking) | Auto mode by default, `restrict_untrusted_prs`, trust in the actor's own text only, the session guard, the credential helper with `allowed_bots`, the git wrappers, `issue-N` and `pr-N` branches for signed agent commits |
| v1.0.274 | Claude Code 2.1.323, which starts a session in Manual when auto is unavailable |
| v1.0.275 | Git wrappers that ignore the session's `GIT_*` variables, such as `GIT_SSH_COMMAND` |

A pin older than v1.0.273 misses security fixes: rate its staleness by W-04 in [workflow-audit.md](workflow-audit.md#checks-every-workflow-gets).

## A version bump is a patch

A patch that changes the pin changes what the step does. When the old and new commits straddle a breaking release:

1. List in the finding what changes, from the comparison and the release notes, for example "the step now runs in auto mode" or "pull requests from outside authors can no longer run `npm`".
2. Freeze the step's current effective mode in the same patch, by [Permission mode in patches](auth-and-permissions.md#permission-mode-in-patches).
3. Run every check in [Checks for steps that run claude-code-action](workflow-audit.md#checks-for-steps-that-run-claude-code-action) again on the bumped file, and validate by [Validate the patches](workflow-audit.md#validate-the-patches).

## When nothing can be read

When git, MCP and the network are all unavailable, or the pin can't be resolved:

- Every claude-code-action fact counts as unverified for that step.
- The checks that depend on them follow [When a check can't be decided](workflow-audit.md#when-a-check-cant-be-decided): one Questions row for the commit the step runs, naming every check it decides.
- A floating ref that can't be resolved counts as auto mode ([auto-mode-audit.md](auto-mode-audit.md#1-is-auto-mode-the-effective-mode)).
- On GitHub Enterprise Server, count these facts as unverified too: they were checked against github.com's action and github.com's behavior.
