# Check claude-code-action drift

The facts in [action-contract.md](action-contract.md) describe `anthropics/claude-code-action` at one verified commit, the snapshot below. A workflow can run any other commit, and upstream ships several releases a day. This page tells you, the same way every time, which facts hold for the commit a step runs.

Run it once per claude-code-action step a route touches, before you rely on any fact from `action-contract.md`.

**Contents**
- [Snapshot](#snapshot)
- [Facts to look up live](#facts-to-look-up-live)
- [Source files](#source-files)
- [Find the commit a step runs](#find-the-commit-a-step-runs)
- [Pick the newest release](#pick-the-newest-release)
- [Pinning policy](#pinning-policy)
- [Compare with the snapshot](#compare-with-the-snapshot)
- [When the pin is older than the snapshot](#when-the-pin-is-older-than-the-snapshot)
- [A version bump is a patch](#a-version-bump-is-a-patch)
- [When nothing can be read](#when-nothing-can-be-read)

## Snapshot

The baseline: the one commit of `anthropics/claude-code-action` whose behavior `action-contract.md` and `sharp-edges.md` were verified against, read from its source. It is not the newest release, and it doesn't need to be: [Compare with the snapshot](#compare-with-the-snapshot) tells you which facts still hold at the commit a step runs, and sends you to the code for the rest.

| claude-code-action | Commit | Claude Code bundled | Agent SDK locked | GitHub MCP server image |
| :-- | :-- | :-- | :-- | :-- |
| v1.0.275 | `4d75e5f390ee76b2e09c1980ecc99ff3a2e088c8` | 2.1.323 | 0.3.323 | `ghcr.io/github/github-mcp-server:sha-23fa0dd` (v0.17.1) |

## Facts to look up live

This skill holds no versions, dates or lists that change outside the baseline. Look each of these up when a step depends on it, from the source named, and record what you found and where in the report's Version provenance or Observations:

- **The tools' versions and behavior.** Record `zizmor --version`, `actionlint -version` and the `gh actions-lock` version `gh extension list` shows. When a step on these pages disagrees with the installed version's `--help` or its release notes ([zizmor](https://docs.zizmor.sh/release-notes/), [actionlint](https://github.com/rhysd/actionlint/blob/main/CHANGELOG.md), [gh-actions-lock](https://github.com/github/gh-actions-lock/releases)), the installed version wins.
- **Where lockfiles and `$/` exist.** Both are github.com and GHE.com features ([Workflow dependency lockfiles](https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles)). On GitHub Enterprise Server, treat the instance as having neither unless its own documentation, for the instance's version, has a lockfile page.
- **The `pull_request_target` default rule.** Whether GitHub enforces it yet, on which repositories, and what a blocked attempt looks like: [Default policy for `pull_request_target`](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target#default-policy-for-pull_request_target) and the [GitHub changelog](https://github.blog/changelog/label/actions/). Say in the finding what the page said on the day you read it.
- **`actions/checkout` and fork checkouts.** Whether the version a workflow pins refuses a fork's checkout by default: read that tag's `action.yml`. A version that declares `allow-unsafe-pr-checkout` refuses unless it is set to `true`; one that doesn't declare it checks out whatever it is told.

  ```bash
  if a=$(gh api -H 'Accept: application/vnd.github.raw' 'repos/actions/checkout/contents/action.yml?ref=[tag]'); then printf '%s\n' "$a" | grep -cE '^  allow-unsafe-pr-checkout:' || true; else echo "read: failed"; fi
  ```

  `[tag]` is the tag the workflow pins. `1` or more means it refuses by default; `0` means it doesn't; `read: failed` means nothing was decided. With MCP only, read the same file with `get_file_contents` at that `ref`. The credential layout is in [Git, branches and credentials](action-contract.md#git-branches-and-credentials).
- **Runner labels and limits.** Read GitHub's [runner table](https://docs.github.com/en/actions/reference/runners/github-hosted-runners#supported-runners-and-hardware-resources) and [Actions limits](https://docs.github.com/en/actions/reference/limits) on the day of the audit, never a label or a limit from memory.
- **Version tags of a marketplace or action.** Before pinning one by tag, list its tags:

  ```bash
  GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git ls-remote --tags [repository URL]; echo "ls-remote exit: $?"
  ```

  A repository with no `vX.Y.Z` tags, with exit 0, is pinned by commit; any other exit means nothing was read.
- **Claude Code's models.** The default model per provider and the models that support auto mode change with each model release: read [Default model behavior](https://code.claude.com/docs/en/model-config#default-model-behavior) and [Eliminate permission prompts with auto mode](https://code.claude.com/docs/en/permission-modes#eliminate-permission-prompts-with-auto-mode) before a finding rests on them.

## Source files

Every path that a `Sources:` line in `action-contract.md` names, and the `package.json` and `bun.lock` files the action installs its dependencies from, with its blob at the snapshot. A changed blob makes the topics on its row unverified until you read the change. A changed path that isn't here is an unmapped change: read its diff.

| Path | Blob at the snapshot | Topics |
| :-- | :-- | :-- |
| `action.yml` | `1ad93d0dd466589dfdc703074e451cd95aab21fc` | [Inputs and outputs](action-contract.md#inputs-and-outputs), [Untrusted pull requests](action-contract.md#untrusted-pull-requests), [Git, branches and credentials](action-contract.md#git-branches-and-credentials), [GitHub token and the Claude App token](action-contract.md#github-token-and-the-claude-app-token), [Inference credentials](action-contract.md#inference-credentials), [Comments, reviews and structured output](action-contract.md#comments-reviews-and-structured-output), [Removed inputs](action-contract.md#removed-inputs), [Environment variables the action passes](action-contract.md#environment-variables-the-action-passes) |
| `base-action/action.yml` | `866689cc1b21a775b7bcc3b4480e18605cd33cc1` | [Inputs and outputs](action-contract.md#inputs-and-outputs), [Claude Code version, models and auto availability](action-contract.md#claude-code-version-models-and-auto-availability) |
| `base-action/package.json` | `223ac6b6f00fe5708551cbd1778f48427005d180` | [Claude Code version, models and auto availability](action-contract.md#claude-code-version-models-and-auto-availability) |
| `package.json` | `681b0cdf5b4c5bcad2a72450d55534b505ab0370` | Claude Code version, models and auto availability, in `action-contract.md` |
| `bun.lock` | `17309d1a506e4be6190c796651c3eac1df470eba` | Claude Code version, models and auto availability, in `action-contract.md` |
| `base-action/bun.lock` | `aeb45a61768a1b9a09be179d7d2aa28765acca73` | Claude Code version, models and auto availability, in `action-contract.md` |
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
| `src/modes/agent/parse-tools.ts` | `5cccb1c021340f6c34728b9dcf4390c488bb60dc` | [Tools the action grants and the MCP servers it starts](action-contract.md#tools-the-action-grants-and-the-mcp-servers-it-starts), [Untrusted pull requests](action-contract.md#untrusted-pull-requests) |
| `src/github/operations/comments/create-initial.ts` | `1243035b759cffdab97e609f7fa934955277afe2` | [Comments, reviews and structured output](action-contract.md#comments-reviews-and-structured-output) |
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

1. **Find the step.** It is a `uses: anthropics/claude-code-action@<ref>` line. When a workflow calls a remote composite action (`owner/repo/path@ref`) or a reusable workflow, open that file at the ref the caller pins and find the step there. A local `uses: ./path` has no ref: GitHub runs the file as the job's workspace holds it when the step runs, so audit that copy; when the job checked out a pull request's head before it, that copy is the head's (W-02 under `pull_request_target`).
2. **Check the owner and name.** Any `uses:` other than `anthropics/claude-code-action` is not an upstream commit, even when the code looks the same. Report it as "not an upstream commit", count every fact for that step as unverified, and raise W-04 ([workflow-audit.md](workflow-audit.md#checks-every-workflow-gets)).
3. **Resolve the ref.**
   - In a workflow onboarded to `.github/workflows/actions.lock` (its path is a key under `workflows:`), the step runs the locked commit, whatever the ref points to now. Read it from the entry under `dependencies:` whose key is the `uses:` string, such as `'anthropics/claude-code-action@v1.0.275'`: its `commit` field, without the `sha1-` prefix the format writes. Then check that commit as a full SHA, next bullet. A `uses:` with no entry fails the job at run time (W-04).
   - A full 40-character SHA is the commit. A successful fetch doesn't prove it is upstream's: GitHub also serves the heads of pull requests anyone can open. It is an upstream commit only when it is on the default branch's history or a release tag points to it. In one shell call:

     ```bash
     export GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never
     TMP=$(mktemp -d) || exit 1; echo "tmp: $TMP"
     git init -q "$TMP" && git -C "$TMP" fetch -q --filter=blob:none https://github.com/anthropics/claude-code-action refs/heads/main:refs/remotes/upstream/main && echo "fetch: ok" || echo "fetch: failed"
     git -C "$TMP" merge-base --is-ancestor [sha] upstream/main 2>"$TMP/mb.err"; echo "on main: $?"; grep -m1 'fatal:' "$TMP/mb.err"
     git ls-remote --tags https://github.com/anthropics/claude-code-action > "$TMP/tags" && echo "tags: ok" || echo "tags: failed"
     awk -v s=[sha] '$1 == s && $2 ~ /\^\{\}$/ { t=$2; sub(/\^\{\}$/,"",t); print "release tag: " t; next } $1 == s { lt[$2]=1 } $2 ~ /\^\{\}$/ { p=$2; sub(/\^\{\}$/,"",p); peeled[p]=1 } END { for (t in lt) if (t in peeled) print "tag object, not a commit: " t; else print "release tag (lightweight): " t }' "$TMP/tags"
     ```

     `[sha]` is the full 40-character SHA. The first line keeps git from waiting on a credential prompt nobody can answer. Read the result in this order:

     - `fetch: failed` or `tags: failed`: nothing was decided, so never read it as "not an upstream commit". Check the commit with MCP (`list_tags`, and `list_commits` on `main` with `sha` set to the commit), or follow [When nothing can be read](#when-nothing-can-be-read).
     - A `tag object, not a commit:` line: W-04's annotated-tag case, even with `on main: 0`, because `merge-base` resolves the tag to its commit.
     - `on main: 0`, a `release tag:` line or a `release tag (lightweight):` line: upstream.
     - `on main: 1`, or `on main: 128` with a `fatal:` line that says `not our ref`, and no tag line: not an upstream commit, because GitHub serves no such commit or upstream's history doesn't hold it. Treat it exactly like step 2.
     - `on main: 128` with any other `fatal:` line, such as `unable to access`: git couldn't reach GitHub to test the commit, so nothing was decided. Follow [When nothing can be read](#when-nothing-can-be-read).

     Delete the folder before you leave this step with `rm -rf [tmp]`, where `[tmp]` is the literal path after `tmp:`: a variable doesn't survive between calls, and the comparison below makes its own folder.
   - A tag or branch, such as `v1` or `v1.0.275`:

     ```bash
     export GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never
     git ls-remote --exit-code https://github.com/anthropics/claude-code-action [ref] '[ref]^{}'; echo "ls-remote exit: $?"
     ```

     `[ref]` is the tag or branch the `uses:` line names. `ls-remote exit: 2` means upstream has no such ref, so the step fails when it runs (W-04); 128 means nothing was read: follow [When nothing can be read](#when-nothing-can-be-read). When a line ending in `^{}` prints, its SHA is the commit: the other line is an annotated tag object, not a commit. When only one line prints, its SHA is the commit. When a branch and a tag both print, report both, and take the commit from a run's log (next bullet) if one exists. With MCP only, `list_tags` (or `list_branches` for a branch) gives the commit of each name.
   - A past run: the "Set up job" log of that job has the line `Download action repository 'anthropics/claude-code-action@<ref>' (SHA:<sha>)`. That SHA is what the run executed, whatever the ref points to now.
4. **A floating ref** (`v1`, `main`) in a workflow the lockfile doesn't list runs whatever it points to when the job starts. Audit the commit it resolves to today, say so in Version provenance, and recommend the pin the [Pinning policy](#pinning-policy) gives (W-04).

## Pick the newest release

Use this when a patch pins or bumps the action. It needs git 2.18 or later and no clone. It keeps only exact `vX.Y.Z` tags, sorts them by version, and prints the newest with its commit, taking the `^{}` line for an annotated tag:

```bash
export GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never
TMP=$(mktemp -d) || exit 1; echo "tmp: $TMP"
git ls-remote --tags --sort=-v:refname https://github.com/[owner]/[action] > "$TMP/tags"; echo "ls-remote exit: $?"
awk -v major=[major] '$2 ~ ("^refs/tags/v" major "\\.[0-9]+\\.[0-9]+(\\^\\{\\})?$") { t=$2; sub(/\^\{\}$/,"",t); if (!seen) { seen=t } if (t==seen) { sha=$1; if ($2 ~ /\^\{\}$/) peeled=$1 } } END { if (!seen) exit 1; print seen, (peeled?peeled:sha) }' "$TMP/tags"; echo "pick exit: $?"
```

`[owner]/[action]` is the action's repository, and `[major]` is the pin's current major, such as `1`; write `[0-9]+` only after the user approves a jump. Delete the folder with `rm -rf [tmp]`, where `[tmp]` is the literal path after `tmp:`.

- It prints a line such as `refs/tags/v1.0.275 4d75e5f390ee76b2e09c1980ecc99ff3a2e088c8`. Write the pin as the [Pinning policy](#pinning-policy) says: the tag, `uses: anthropics/claude-code-action@v1.0.275`, in a workflow the lockfile lists; otherwise the commit with the tag as a comment, `uses: anthropics/claude-code-action@<commit> # v1.0.275`.
- An `ls-remote exit:` other than 0 means git couldn't read the tags: for a private action, read them with `gh api repos/[owner]/[action]/tags --paginate` or MCP `list_tags`. `ls-remote exit: 0` with `pick exit: 1` means the action has no `vX.Y.Z` tag in that major: pin the commit the user names, or ask. Pin only when both are 0.
- Never take the last line of a plain `git ls-remote --tags`: its order is lexical, so it ends at `v1.0.99`.
- Stay in the pin's current major unless the user approves a jump. A jump lists the breaking changes from the release notes as residual risk.
- With MCP only: `get_latest_release` gives the tag GitHub marks as latest, and `list_tags` gives its commit. Check that the tag is in the current major.

The same pipeline works for any action, for example `actions/checkout`.

## Pinning policy

Every `uses:` a patch adds or changes follows this policy. A repository's lockfile, `.github/workflows/actions.lock`, records the commit each action reference of an onboarded workflow resolves to, transitive ones included, with the source repository's numeric IDs, and GitHub runs that commit even after the tag moves. GitHub says the lockfile supersedes SHA pinning for the workflows it covers, and under it a bare SHA draws the `sha-as-ref` warning and gets no Dependabot alerts, which GitHub raises only for version refs. A workflow is onboarded when its path is a key under the lockfile's `workflows:`.

1. Write each line as its case says:

   | The `uses:` line | Write |
   | :-- | :-- |
   | A step in a workflow the lockfile lists | The full release tag from the pick pipeline, no comment: `uses: actions/checkout@v7.0.1`. Then regenerate the lockfile, step 2 |
   | An action in the same repository, in a workflow the lockfile lists | `$/<path>`, no `@ref`: a `./` path runs whatever the workspace holds, the lockfile never follows it, and the actions it uses fail at run time without entries. Not on GitHub Enterprise Server |
   | An action with no `vX.Y.Z` release tag, in a workflow the lockfile lists | The commit with a comment saying it has no release tag: `gh actions-lock` reports it as `sha-as-ref`, which is no finding here |
   | A reusable workflow from another repository (`jobs.<id>.uses`) | The commit with the tag as a comment: the lockfile doesn't cover these calls |
   | A step of an `action.yml` or `action.yaml` | The commit with the tag as a comment: a composite action carries no lockfile of its own, and the repositories that call it don't have yours |
   | A step in a workflow the lockfile doesn't list, or in a repository without a lockfile | The commit with the tag as a comment. Adopting the lockfile is a separate recommendation (W-04) with its own approval, never part of a patch, because onboarding changes how the allowed-actions policy matches and breaks `./` actions that use remote ones |
   | Any `uses:` on GitHub Enterprise Server | The commit with the tag as a comment: GHES has neither lockfiles nor `$/` |
   | A container image (`docker://`, `container:`, `services:`) | A digest, `@sha256:<digest>`: the lockfile doesn't lock images |

   Never write a branch or a partial tag such as `v1`: in an onboarded workflow it keeps running its locked commit after the ref moves, and a lockfile change that moves it back to an older commit goes undetected.
2. When the patch touches a workflow the lockfile lists, regenerate the lockfile only after the user approves the patch, on the approved branch, once the workflow files are written (step 7 of the audit route). While you build and validate the patch, never run the extension: the patch names the regeneration it needs, `gh actions-lock` and the workflow files.
   1. Check that `gh extension list` shows `github/gh-actions-lock`, and read `gh actions-lock --help` before the first run: the installed version's flags win over this page. When the extension isn't there, hold the patch for that workflow, and give the user the patch and these commands to run on the branch after applying it:

      ```bash
      gh extension install github/gh-actions-lock --pin [release tag]
      gh actions-lock [workflow file]
      ```

      `[release tag]` is the newest tag on the extension's releases page, and `[workflow file]` is each changed workflow, such as `.github/workflows/ci.yml`. Without the entry the job fails at run time with `lockfile missing pin for [action]@[ref]`.
   2. Run `gh actions-lock <workflow file>...; echo "gh actions-lock exit: $?"` with every changed workflow, never with no path: a run with no path scans every workflow under `.github/workflows/` and onboards the ones the lockfile doesn't list, which no patch may do. When the patch deletes a workflow, its leftover entry is only a `stale-workflow` warning: list the pruning run, `gh actions-lock` with no path, under "Left for you".
   3. Read the exit code on the last line: 0 means the lockfile was written; 1 means findings block it and nothing was written; 2 means the tool failed. On 1 or 2, report its output and hold the patch. The trailing `echo` keeps a long report whole, because the Bash tool cuts the output of a command that exits non-zero to about 10,000 characters.
   4. Review the whole diff the run left, workflows and lockfile together: the extension also narrows a partial tag such as `v4` to a full release tag in the workflows it locks. A workflow line that differs from the checked patch goes back through [Validate the patches](workflow-audit.md#validate-the-patches). A changed `owner_id` or `repo_id` means another repository now stands behind the name: stop and report it. Every changed or new `commit` is new code the workflow will run: list each one (action, old commit, new commit, direct or transitive) in Version provenance, show the list to the user, and land only after they confirm it.
3. Never edit `actions.lock` by hand or delete it to clear an error, never pass `--accept-moved`, and pass `--relock` or `--migrate-local-actions` only with the user's approval: the first moves refs to new commits, the second rewrites `./` references across the repository.

## Compare with the snapshot

Do this for the commit from [Find the commit a step runs](#find-the-commit-a-step-runs) (`[pin]` below). `[snapshot]` is the commit in the Snapshot table. When the two are equal, every fact in `action-contract.md` holds; skip to Version provenance.

**With git** (Claude Code with a shell):

```bash
export GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never
TMP=$(mktemp -d) || exit 1; echo "tmp: $TMP"
git init -q "$TMP" && git -C "$TMP" fetch -q --filter=blob:none --depth=1 https://github.com/anthropics/claude-code-action [snapshot] [pin] && git -C "$TMP" diff --name-only [snapshot] [pin] -- action.yml package.json bun.lock base-action/action.yml base-action/package.json base-action/bun.lock base-action/src src scripts docs/security.md && echo "compare: ok" || echo "compare: failed"
```

Run these three lines in one shell call. A variable doesn't survive between calls, so write the path after `tmp:`, as a literal path, in every later command, the cleanup included.

The fetch downloads trees, not file contents, so it takes about a second. Read what it prints:

- **`compare: failed`:** nothing was compared, whatever else printed. Use the MCP route below when a GitHub MCP server answers; otherwise follow [When nothing can be read](#when-nothing-can-be-read).
- **Nothing printed before `compare: ok`:** every fact holds at the pin, whatever its version number. On GitHub Enterprise Server the Drift result is still `unverified: GHES`: the instance's copy of the action and its behavior weren't checked.
- **A path in the Source files table:** the topics on its row are unverified. Read `git -C [tmp] diff [snapshot] [pin] -- [path]`, then apply what the code at the pin says, not what `action-contract.md` says. Name each such topic in Version provenance.
- **A path not in the table:** an unmapped change. Read its diff and say in Version provenance whether it changes anything the route relies on.

Delete that folder with `rm -rf [tmp]` when you're done.

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
- On GitHub Enterprise Server, count these facts as unverified too: they were checked against github.com's action and github.com's behavior. Read the instance with `gh` and `GH_HOST` set to its host name.
