# Audit and harden workflow files

The checks the audit runs in layer 3 of [detection-layers.md](detection-layers.md), how to judge each one, and how to turn findings into patches. For every check this page says what to look for, when it is a finding and when it isn't, how severe it is, what the patch is, and why. Each check also names the zizmor audit and the CodeQL rule that overlap it, or "none".

**Contents**
- [Scope and inputs](#scope-and-inputs) · [Order of the audit](#order-of-the-audit) · [Severity scale](#severity-scale) · [When a check can't be decided](#when-a-check-cant-be-decided)
- [Checks every workflow gets](#checks-every-workflow-gets): W-01 to W-13
- [Checks for steps that run claude-code-action](#checks-for-steps-that-run-claude-code-action): C-01 to C-17
- [Build the patches](#build-the-patches) · [Validate the patches](#validate-the-patches) · [Each finding](#each-finding)

## Scope and inputs

Read, and record what you couldn't:

- **Files.** Every file under `.github/workflows/`, every composite action (`action.yml` or `action.yaml` anywhere in the repository) and every reusable workflow the files call, at the ref the caller pins.
- **The default branch's copy.** Comment, issue and schedule events run the workflow file on the default branch, so audit that copy too when the working tree is on another branch: `git show origin/<default>:.github/workflows/<file>`, or `get_file_contents` with `ref` set to the default branch.
- **The Actions policy:** `gh api repos/<owner>/<repo>/actions/permissions` and `gh api repos/<owner>/<repo>/actions/permissions/workflow` (the default token permission).
- **The rules on the default branch:** `gh api repos/<owner>/<repo>/rules/branches/<default branch>`.
- **Secret and variable names at every level** (names only, never values): `gh secret list`, `gh secret list --env <environment>` for each environment a job uses, `gh secret list --app dependabot`, `gh secret list --org <org>` when readable, and `gh variable list`.
- **Runners**, when readable: `gh api repos/<owner>/<repo>/actions/runners` needs admin access; the job's `GITHUB_TOKEN` can't list runners.
- **The commit each claude-code-action step runs:** [version-drift.md](version-drift.md#find-the-commit-a-step-runs).

When one of these can't be read, decide the checks that need it by [When a check can't be decided](#when-a-check-cant-be-decided). This audit reads files and settings; the state of runs, artifacts, caches and runners belongs to the repository audit.

## Order of the audit

Cover every file, in this order, so the riskiest are read first even if the work stops early:

1. Workflows with a claude-code-action step, including those that reach one through a composite action or a reusable workflow.
2. Workflows on triggers outsiders can reach: `pull_request_target`, `issue_comment`, `issues`, `discussion`, `discussion_comment`, `workflow_run`, `pull_request_review` and `pull_request_review_comment`.
3. Workflows that hold secrets or a write token.
4. The rest.

A claude-code-action step inside a composite action or a reusable workflow is audited where its inputs are written: the C-checks read the caller's `with:` values and the callee's defaults together, and the finding names both files.

## Severity scale

Rate every finding by two questions: who can trigger it, and what they get. Use this scale for every check, including scanner results that match no check:

| Severity | Who can trigger it, and what they get |
| :-- | :-- |
| critical | Any GitHub user, with no maintainer action, gets code execution in a job that holds secrets or a token that can write to the repository |
| high | Any GitHub user gets code execution without secrets or write access; or a collaborator, or one maintainer action such as a label or an approval, gets secrets or write access; or a security control is silently gone |
| medium | A protection layer is missing that would limit the damage of another flaw; or a misconfiguration blocks merges or runs |
| low | Hygiene and cost: no direct path to harm |

How to apply it:

- **Count only what the trigger adds.** A collaborator who can already push to the default branch gains nothing from a workflow they can start; rate by what the workflow gives beyond the actor's own access.
- **GitHub's fork model is not a finding.** A fork's `pull_request` run on a GitHub-hosted runner, with a read-only token and no secrets, is the protection working.
- **The scale wins.** A check's own rating assumes the usual case; when the scale gives another rating for a given workflow, use the scale's and say why.
- **Auto-mode layers** are rated by the table in [auto-mode-audit.md](auto-mode-audit.md#4-rate-and-report), which applies this scale.

## When a check can't be decided

Sometimes a check needs a fact you can't read: the default token permission, an organization secret, the network of a self-hosted runner, the commit a floating ref ran, the inputs a third-party action really needs. Then:

1. **Name the missing fact** and why you couldn't read it.
2. **Ask only when the answer changes a rating.** If every possible answer gives the same rating, decide the check and say why.
3. **One Questions row per missing fact**, not per check: the fact, every check it decides, the rating if the answer is the risky one, and the answer that would lower it. An unreadable Actions policy is one row, however many `uses:` lines it decides.
4. **A certain finding with an uncertain severity** is still a finding: report it at the severity of the risky answer, and add the Questions row with the answer that would lower it. Only a check whose finding itself depends on the missing fact is a question instead.
5. **Count questions apart.** The report's Result line gives findings by severity and questions as their own number. A question is never a finding and never a pass.
6. When the user is present and one answer settles a row, ask them; otherwise leave the row for the report.

## Checks every workflow gets

### W-01. Expressions expanded into a shell or script

- **Look for:** `${{ }}` inside `run:`, or inside `script:` of `actions/github-script`.
- **A finding when** the expression carries a value an outside actor can influence: `github.event.*` fields (issue and pull request titles and bodies, comment bodies, branch and label names), `github.head_ref`, step or job outputs that came from such text, and `structured_output`. A quoted assignment is no exception ([trust-boundaries.md](trust-boundaries.md#shell-injection-is-not-prompt-injection)).
- **Not a finding when** the value is fixed by the repository or the run: `github.repository`, `github.sha`, `github.run_id`, `matrix` values written in the file, or `inputs` of a `workflow_dispatch` only people with write access can start (then rate it low).
- **Severity:** by the scale. Usually critical on `issues`, `issue_comment` or `pull_request_target` jobs that hold secrets or a write token.
- **Patch:** pass the value through `env:` and read `"$NAME"` in the script. Write the script as a block scalar (`run: |`), so no `: ` or ` #` in it changes how the file parses (W-12).
- **Why:** the expression is pasted into the script before the shell parses it, so the text becomes code.
- **Scanners:** zizmor `template-injection`; CodeQL `actions/code-injection/*`.

### W-02. A pull request's code run with the base's privileges

- **Look for:** `pull_request_target` or `workflow_run` jobs that check out the pull request's head into the workspace (`ref:` naming the head branch or `head.sha`, or `repository:` naming the fork), or that build, test or run it; `actions/checkout` with `allow-unsafe-pr-checkout: true`; a claude-code-action step with `track_progress` under `pull_request_target`, which checks out the head itself ([trust-boundaries.md](trust-boundaries.md#fork-dependabot-and-pull_request_target-designs)).
- **Not a finding when** the job checks out only the base, or fetches the head outside the workspace and runs nothing from it, as the design in trust-boundaries.md describes.
- **Severity:** critical.
- **Patch:** that design, or move the job to `pull_request`. Name in the finding GitHub's new default policy for `pull_request_target` in public repositories (its date is in [the Snapshot](version-drift.md#snapshot)) and that `actions/checkout` v7 refuses a fork's checkout under these triggers unless `allow-unsafe-pr-checkout: true` is set.
- **Why:** these triggers run with the base repository's secrets and write token, whatever the approval settings, while the head is code anyone can submit.
- **Scanners:** zizmor `dangerous-triggers` flags the trigger; its `dangerous-checkout`, which would flag `allow-unsafe-pr-checkout`, is documented for a zizmor release newer than the Snapshot's, so only this check covers that input. CodeQL `actions/untrusted-checkout/*`.

### W-03. Token permissions wider than the job uses

- **Look for:** no workflow-level `permissions:`; `write-all` or `read-all`; a job write scope nothing in the job uses; `id-token: write` without OIDC.
- **How to decide "unused":** a write scope is used when a step pushes (`git push`, an action that commits), writes through `gh` or the API, posts through a tool the agent is granted, or calls an action whose documentation needs that scope. A claude-code-action step without `github_token` runs on the Claude App token, not the job's: a job write scope kept only for it is unused, except `id-token: write`, which the App token's exchange needs. When you can't tell from the file or the action's documentation, it is a Questions row.
- **Not a finding when** workflow-level `permissions:` is absent but the repository's default token permission is read-only: rate that low, as hygiene.
- **Severity:** `write-all`, or an absent block under a write default, is high when a trigger outsiders reach runs the job, and medium otherwise. One unused write scope: medium.
- **Patch:** `permissions: {}` at workflow level, and each job's scopes set to exactly what it uses.
- **Why:** every injected or mistaken step acts with the whole token.
- **Scanners:** zizmor `excessive-permissions`; CodeQL `actions/missing-workflow-permissions`.

### W-04. Actions not pinned to an upstream commit, or pinned stale

- **Look for:**
  - `uses:` with a tag or branch instead of a full 40-character commit SHA;
  - a SHA that is an annotated tag's object rather than its commit ([Find the commit a step runs](version-drift.md#find-the-commit-a-step-runs));
  - a `uses:` whose owner or name isn't the action's upstream, or a SHA upstream doesn't have ("not an upstream commit");
  - a version comment that doesn't match the SHA;
  - a stale pin: its tag is older than the newest release in its major ([Pick the newest release](version-drift.md#pick-the-newest-release)).
- **Not a finding when** the `uses:` is a local path (`./...`) or a Docker image pinned by digest. A workflow covered by a workflow dependency lockfile (`.github/workflows/actions.lock`, made with `gh actions-lock`) needs no SHA pins: GitHub says the lockfile supersedes SHA pinning [unverified: whether the lockfile is generally available or a preview]. Reusable workflows called at job level still need pins.
- **Severity:**
  - a tag or branch, or not an upstream commit: high when the job holds secrets or a write token, medium otherwise;
  - a stale pin: low, or medium when it misses a security release: claude-code-action below v1.0.273; `actions/checkout` below v7 in a `pull_request_target` or `workflow_run` job;
  - a wrong version comment: low.
- **Patch:** pin to the commit the pick pipeline prints, with the tag as a comment. Bumping claude-code-action across a breaking release is a patch with its own impact ([A version bump is a patch](version-drift.md#a-version-bump-is-a-patch)). To keep pins current, hand a `github-actions` Dependabot entry to `github-operations:github-files-setup`; Dependabot raises no security alerts for actions pinned to a SHA.
- **Why:** a tag or branch can be moved to new code after the review, and a fork's commit is code upstream never reviewed.
- **Scanners:** zizmor `unpinned-uses`, `ref-version-mismatch`, and offline-skipped `impostor-commit` and `ref-confusion`; staleness none.

### W-05. Checkout credentials left on disk

- **Look for:** `actions/checkout` without `persist-credentials: false`.
- **Not a finding when** a later step in the same job pushes with those credentials. A claude-code-action step doesn't count: it pushes with its own token, never checkout's ([Git, branches and credentials](action-contract.md#git-branches-and-credentials)).
- **Severity,** in this order:
  1. Low when the job's `GITHUB_TOKEN` has no write scope on the repository, whatever runs later (`id-token: write` doesn't count: checkout doesn't store it).
  2. Otherwise medium when a later step runs code the workflow didn't write (dependencies, the pull request's code, or an agent the credential reaches) or uploads the workspace as an artifact. A claude-code-action step's agent reaches it only with checkout v6 or later: the action removes the credential of earlier versions before Claude starts. Resolve a floating checkout ref to its version first.
  3. Low otherwise.
- **Patch:** `persist-credentials: false`. On a claude-code-action job, state its cost from [Costs of each change](auth-and-permissions.md#costs-of-each-change).
- **Why:** checkout's token stays readable for every later step: in the local `.git/config` up to checkout v5, and in a separate file that `.git/config` includes from v6 on. claude-code-action doesn't remove the v6 form.
- **Scanners:** zizmor `artipacked`.

### W-06. Secrets exposed or passed wholesale

- **Look for:** `secrets: inherit`; a secret echoed, or `set -x`, `env` or `printenv` in a step that holds one; `ACTIONS_STEP_DEBUG` set as a variable or secret.
- **Severity:** a printed secret: high. `secrets: inherit` to a workflow outside the repository: high; inside it: medium. `ACTIONS_STEP_DEBUG`: medium.
- **Patch:** pass each secret by name; remove the printing and the debug setting.
- **Why:** logs of public repositories are public, and masking misses transformed values.
- **Scanners:** zizmor `secrets-inherit`; the others none.

### W-07. Deployment credentials reachable from untrusted events

- **Look for:** deployment or publishing secrets, environments or OIDC roles in a workflow that `issues`, `issue_comment`, `pull_request_target` or `workflow_run` can start, or in the same job as an agent or an untrusted build.
- **Severity:** critical when an outside actor can reach the step that holds them; high otherwise.
- **Patch:** a separate workflow or job for deployment, gated by an environment with required reviewers.
- **Why:** one injection in the triggering job would carry the deployment keys.
- **Scanners:** zizmor `dangerous-triggers` and, under the auditor persona, `secrets-outside-env`.

### W-08. No time limit, no cancelling of superseded runs

- **Look for:** jobs without `timeout-minutes` (the default is 360 minutes); workflows that comment, review or label without a `concurrency` group that cancels runs a newer event supersedes.
- **Severity:** for a job that runs an agent, the rating of layer E in [auto-mode-audit.md](auto-mode-audit.md#4-rate-and-report): medium when outsiders can start it, low when only collaborators can. Low for every other job. Report it once, as W-08, even when layer E applies.
- **Patch:** `timeout-minutes` sized to the job; `concurrency: { group: <workflow>-<issue or PR number>, cancel-in-progress: true }`.
- **Why:** a stuck or looping job burns minutes and can post for hours.
- **Scanners:** zizmor `concurrency-limits` (pedantic persona only); timeouts none.

### W-09. Required checks that skip

- **Look for:** a workflow whose job is a required check (from the rules read in [Scope and inputs](#scope-and-inputs)) and that has `paths`, `branches` or a commit-message filter at workflow level, or a job-level `if:` that can skip the required job; a required job skipped because a job it `needs` failed; a required check behind a merge queue in a workflow without `merge_group`.
- **Not applicable** to workflows that can't feed a pull request's required check: checks from `issues`, `issue_comment`, `schedule` and other events outside `push`, `pull_request`, `pull_request_review`, `pull_request_target`, `deployment`, `deployment_status` and `merge_group` are never evaluated for a pull request. A required check fed only by them never passes: report that as the finding instead.
- **Severity:** a workflow-level filter: medium, because the check never reports and blocks the merge. A job-level `if:` or a failed `needs`: high when the check guards security or tests, medium otherwise, because GitHub reports the skipped job as `Success` and the requirement is bypassed.
- **Patch:** move the filter into a step; add a job that always runs (`if: always()` with `needs`) and reports the result; add `merge_group` to the triggers.
- **Why:** GitHub treats a skipped job as passing and a workflow that never started as pending.
- **Scanners:** none.

### W-10. References to things that no longer exist

- **Look for:**
  - branches in `on:` filters (`git ls-remote --heads`);
  - secrets the repository doesn't have, at every level read in [Scope and inputs](#scope-and-inputs);
  - files under `paths:` or used by steps, and scripts named in a script-caps value;
  - `runs-on` labels: compare GitHub-hosted labels with GitHub's current runner table, read live (for example `macos-14`, retired: see [the Snapshot](version-drift.md#snapshot)); compare self-hosted and larger-runner labels with the runners list, which needs admin access.
- **When it can't be decided:** organization and environment secrets and self-hosted labels may not be readable. Each is a Questions row, not a missing reference.
- **Severity:** low; medium when the missing piece is a required check's or a deployment's, or when a `runs-on` label matches no runner. Such a job waits in the queue and, for self-hosted routing, ends after 24 hours; GitHub's pages describe that end as failed in one place and cancelled in another, so report whichever the run shows.
- **Patch:** fix or remove the reference; for a retired label, the nearest newer label of the same OS and architecture in GitHub's table, not a `-latest` label, which moves on its own.
- **Scanners:** none. actionlint checks labels against its own list, which can lag GitHub's.

### W-11. Actions the repository's policy doesn't allow

- **Look for:** `uses:` outside the allowed-actions policy read in [Scope and inputs](#scope-and-inputs).
- **Severity:** medium, because the workflow fails when it runs.
- **Patch:** a permitted equivalent, or tell the user the policy needs their change.
- **Scanners:** none (zizmor `forbidden-uses` reads its own configuration, not the repository's policy).

### W-12. The file parses and is a valid workflow

- **Look for, in this order:**
  1. actionlint's parse errors, when it is installed.
  2. Runs of the workflow with zero jobs and conclusion `failure`, or conclusion `startup_failure`: GitHub creates a failed run for every commit while a workflow file is invalid.
  3. Reading the file: a plain (unquoted) value containing `: `; tabs in indentation; duplicate keys, compared without case (`my-job` and `MY-JOB` collide); an `if:` value that starts with `!` and isn't quoted or wrapped in `${{ }}`; a `job_id` that doesn't start with a letter or `_` or holds other than letters, digits, `-` and `_`; a file over 500 KB, which starts no runs.
- **Also look for silent truncation:** ` #` inside an unquoted value starts a comment, so `run: echo a #b` runs `echo a`. Rate it by what the cut text did.
- **Severity:** medium: the workflow doesn't run, which blocks merges or leaves a job undone.
- **Patch:** one patch per file that fixes the parse error and carries every other finding in that file, because every one of them becomes live when the file runs again.
- **Why:** an invalid file runs nothing, and its other checks were never exercised.
- **Scanners:** actionlint reports the parse error, then stops checking that file; zizmor fails to read it too.

### W-13. Workflow-command injection through printed text

- **Look for:** steps that print text an outsider controls to stdout or stderr: event bodies, files from a pull request, test or tool output on a pull request's code, an agent's answer, a downloaded artifact.
- **How the runner reads it:** a line that starts with `::` after leading spaces is a workflow command, and `##[command]` is one anywhere in a line, on stdout and stderr alike. Live commands include `add-mask`, `stop-commands`, the annotation commands, `group` and `debug`; `set-output` and `save-state` are deprecated but still processed; `set-env` and `add-path` work only with `ACTIONS_ALLOW_UNSECURE_COMMANDS`.
- **Severity:** high when a forged output or state can reach a later `run:` or a deciding `if:`, or when `ACTIONS_ALLOW_UNSECURE_COMMANDS` is set; low otherwise (forged annotations or masks).
- **Patch:** write the text to a file instead of printing it; or print it between `::stop-commands::<random token>` and `::<random token>::`; and never set `ACTIONS_ALLOW_UNSECURE_COMMANDS`.
- **Why:** the runner can't tell a step's own commands from text it echoes.
- **Scanners:** none in zizmor; in CodeQL only an experimental query.

## Checks for steps that run claude-code-action

Before these, run [the drift check](version-drift.md#compare-with-the-snapshot) for the step, and read [action-contract.md](action-contract.md), [auth-and-permissions.md](auth-and-permissions.md) and [sharp-edges.md](sharp-edges.md). Every fact these checks use is a topic of action-contract.md, as it holds at the step's pin. When the step's effective mode is auto (C-13), also run every layer of [auto-mode-audit.md](auto-mode-audit.md). No zizmor audit or CodeQL rule covers these checks.

| ID | Look for | Severity and why | Patch |
| :-- | :-- | :-- | :-- |
| C-01 | Inputs the `action.yml` at the pin doesn't declare ([Removed inputs](action-contract.md#removed-inputs); SE-14) | High for a dropped `disallowed_tools` or `experimental_allowed_domains`, because the control is silently gone; low for others, which are ignored | Its replacement in `claude_args` |
| C-02 | On comment or review events, a `prompt` without a job-level `if:` that matches the trigger phrase, or without the event's action limited to `created`, either by `types: [created]` under `on:` or by `github.event.action == 'created'` in the `if:` (agent mode starts on edited and deleted comments: [Actor and text trust](action-contract.md#actor-and-text-trust)); `issues` triggers without a job-level `if:` (SE-04) | Medium for comment events: every comment, edit or deletion starts the agent and spends credits, and an edit can turn someone else's text into a run. Low for `issues`: every issue event starts a runner | A job-level `if:` on the trigger phrase, the event action and, where it matters, the comment's author |
| C-03 | `*` in `allowed_bots` or `allowed_non_write_users`; bot events without `allowed_bots` or a bot filter (SE-02) | High for `*` in `allowed_bots`, and in `allowed_non_write_users` when `github_token` is set: anyone, or any bot, reaches the agent and its token. Medium for `*` in `allowed_non_write_users` without `github_token`: the bypass is inert, but one patch (C-04) would open it to everyone. Low for a missing filter | Name the bots and users. This keeps the lists non-empty, so the mode doesn't change |
| C-04 | `allowed_non_write_users` without `github_token` (SE-03) | Medium: the bypass does nothing, so the listed users can't start runs; the list still keeps the step out of auto, with the scrub and the credential helper | The user's choice, so the report shows both options and applies neither until the user picks one: add `github_token`, never while the list holds `*` (resolve C-03 first); or remove the list, with the frozen mode and the scrub set explicitly. Both rows are in [Costs of each change](auth-and-permissions.md#costs-of-each-change) |
| C-05 | `track_progress` on an event or action it doesn't support (SE-05); `use_sticky_comment` with `github_token` or a custom App (SE-06) | Medium for `track_progress`: the step fails red. Low for the sticky comment, which stops sticking | Remove `track_progress` from those events, or narrow the triggers; for the sticky comment, as SE-06 says |
| C-06 | CI tools expected without `actions: read` in the job's `permissions:`, or on events that aren't pull requests (SE-07) | Low | Add the scope to the job, or remove the expectation |
| C-07 | `structured_output` used without `--json-schema` or an empty guard (SE-01); and anywhere in `run:` through `${{ }}` (W-01) | Low for the guard; the interpolation is W-01 | Add the schema and the guard |
| C-08 | An inline-comment review without the tool in `--allowedTools`, or with only a bare `mcp__github` in tag mode (SE-08); a prompt asking to post with no posting tool in acceptEdits or Manual (SE-13); a review whose profile isn't `anthropic_api_key` (SE-16) | Low: the review posts nothing, or posts unclassified | Grant the named tool; or use an API key input |
| C-09 | A scheduled Claude workflow last edited by a bot not in `allowed_bots` (SE-02); any `allowed_bots` entry on a public repository (SE-03) | Medium for the public-repository case; low otherwise | As each entry says |
| C-10 | More than one inference profile, a static key beside the federation IDs, or a profile without its variables or `id-token: write` (SE-17) | Medium: the step fails before Claude starts, or federation is silently unused | One profile, with what it needs ([auth-and-permissions.md](auth-and-permissions.md#inference-credentials-which-profile)) |
| C-11 | `mcp__github` or `mcp__github__*` in `--allowedTools`; or a step that can start the GitHub MCP server without `--disallowedTools` denying the approval, merge and branch-write class ([trust-boundaries.md](trust-boundaries.md#approval-merge-and-branch-write-tools)) | High: an injected agent could approve, merge or push. Under auto an allow list doesn't stop the other tools; only the deny rules do | Name the tools needed; deny the whole class, read from the pinned server ([Tools the action grants](action-contract.md#tools-the-action-grants-and-the-mcp-servers-it-starts)) |
| C-12 | `bypassPermissions` in the `settings` input or `claude_args` (`--permission-mode bypassPermissions`, or its equals form); `--dangerously-skip-permissions`; `--allow-dangerously-skip-permissions` | Critical when the workflow is open to outsiders as [auto-mode-audit.md](auto-mode-audit.md#2-who-can-start-the-run) defines it; high otherwise: every call no deny rule covers runs unchecked | Remove it, and write explicitly the mode the step gets without it, from [Permission mode](action-contract.md#permission-mode). This finding is the mode change: state the mode before and after |
| C-13 | Auto is the step's effective mode, derived by [auto-mode-audit.md](auto-mode-audit.md#1-is-auto-mode-the-effective-mode) from the pin and the step's settings. An unresolved floating ref counts as auto | Run auto-mode-audit.md; its table rates each missing layer | Its patches |
| C-14 | `--model` with an ID not resolved live; `show_full_output: true` or `--debug` on a public repository | High for the output settings, which publish the agent's full transcript in public logs; low for the model | Remove them; resolve the model ID live |
| C-15 | A marketplace passed as a URL instead of a pinned local checkout, or Anthropic's plugins through the `claude-code-plugins` redirect instead of `claude-plugins-official` ([Plugins and marketplaces](action-contract.md#plugins-and-marketplaces)) | Medium: each run takes upstream's newest code | A local checkout at a resolved commit |
| C-16 | A pull request's head passed with `--add-dir` without neutralizing its `.claude/` ([trust-boundaries.md](trust-boundaries.md#fork-dependabot-and-pull_request_target-designs)); an OAuth token passed through `anthropic_api_key` | High for `--add-dir`: the pull request's skills and agents load; low for the token, which belongs in `claude_code_oauth_token` | As trust-boundaries.md says; move the token |
| C-17 | `restrict_untrusted_prs: false` on a step that pull request events from outside authors reach ([Untrusted pull requests](action-contract.md#untrusted-pull-requests)) | High: a security control is silently gone, and the pull request's own scripts can run in the agent's job | Remove the input, so the default applies. To read CI results on outside pull requests, use the documented path in the same topic |

## Build the patches

Build one set of patches for all findings, not one patch per finding:

1. **One replacement block per step or job**, merging every finding's change to it, and one combined patch per file.
2. **W-12 first.** A file that doesn't parse gets one patch that fixes it and carries every other finding in that file.
3. **Order:** never add `github_token` while `allowed_non_write_users` holds `*`; resolve C-03 first.
4. **Side effects:** for each change, find its row in [Costs of each change](auth-and-permissions.md#costs-of-each-change) and carry what its last column says.
5. **Freeze the mode** of every claude-code-action step the patch touches, by [Permission mode in patches](auth-and-permissions.md#permission-mode-in-patches). Hold back the patches that need a frozen mode the audit couldn't determine.
6. **Separate approvals.** A change to what starts the workflow (`on:` events or `types:`), to its permissions or secrets, or to the permission mode is its own item in the report, approved on its own.
7. **Pins.** Every new or changed `uses:` is pinned by [Pick the newest release](version-drift.md#pick-the-newest-release).

## Validate the patches

Before you show the patches to the user, check them on the patched files:

1. **Re-derive the effective mode** of every claude-code-action step the patches touch, from [Permission mode](action-contract.md#permission-mode). The mode after must equal the mode before, unless the user approved a change.
2. **Run the W and C checks again on what the patches change.** A patch can raise a finding of its own, for example a bump that crosses a breaking release ([A version bump is a patch](version-drift.md#a-version-bump-is-a-patch)).
3. **Auto mode:** when a patch makes a step's mode auto that wasn't auto before, run [auto-mode-audit.md](auto-mode-audit.md) on that step. In the audit route, also confirm that every layer patch is in place.
4. **Parse the files:** actionlint when installed; otherwise read them again for W-12.
5. **Stay in the route.** In the diagnosis and repair routes, something this check notices on lines the patches don't touch isn't a finding of that route: put it in Observations and offer the audit route.

Apply the patches only after the user approves them, on a branch, and land the change through `github-operations:auto-pr-lifecycle`. When the applied files differ from the checked patches, check them again.

## Each finding

- The check ID (W-xx, C-xx, an auto-mode layer, or the scanner's rule ID) and every layer that saw it. C-13 isn't a finding of its own: the missing auto-mode layers it leads to are. Two checks that apply to the same lines, such as C-11 and layer B, are two findings; their patches merge into one block.
- File and line; for a composite action or reusable workflow, both the caller's and the callee's.
- What an attacker or a failure needs to trigger it.
- Its impact and severity by the scale above.
- For a claude-code-action step, the effective mode before and after the patch.
- The exact patch: the replacement lines, with every new `uses:` resolved and pinned.
- The risk left after the patch.

**Order in the report:** critical, high and medium findings as blocks, by severity, then file, then line; low findings as one table; questions in their own table. "Fix first" lists every critical and high finding with the combined patch for each file.

## Verify against

- GitHub, secure use of Actions: https://docs.github.com/en/actions/reference/security/secure-use
- GitHub, workflow syntax: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- GitHub, workflow commands: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands
- GitHub, GitHub-hosted runners: https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- GitHub, conditions and required checks: https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions and https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks
- zizmor audits: https://docs.zizmor.sh/audits/
- CodeQL queries for Actions: https://codeql.github.com/codeql-query-help/actions/
