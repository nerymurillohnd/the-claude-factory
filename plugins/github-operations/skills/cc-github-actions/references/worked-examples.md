# Worked examples

One example per route: the input, an excerpt of the report in [the template's](../assets/report.md) format, and the rule that decided each value. They fix the format and the severity bar; they are not checklists. Values in `<angle brackets>` stand for what the real run reads.

## Diagnose: a comment that started no run

**Input.** "Claude didn't respond to my comment on issue #12." The default branch's `.github/workflows/claude.yml` starts:

```yaml
on:
  issue_comment:
    types: [edited]
```

`gh run list --event issue_comment --created '>=<time of the comment>'` prints nothing, and `gh workflow list --all` shows the workflow `active`.

**Report excerpt.**

> **Result:** 0 critical · 0 high · 1 medium · 0 low · 0 questions — no run: the trigger's `types` exclude new comments
>
> | Run / attempt | Job / step | Commit | Log line or file:line | Sharp edge |
> | :-- | :-- | :-- | :-- | :-- |
> | `no run` | — | — | `.github/workflows/claude.yml:3` `types: [edited]` | `none matched` |
>
> ### F-1: The workflow runs only on edited comments
> - **Check:** `none` (a diagnosed cause) · **Seen by:** the diagnosis
> - **Where:** `.github/workflows/claude.yml:3`
> - **Severity:** medium · **Mode:** auto → auto (the patch doesn't touch the step)
> - **Approval:** its own, because it changes triggers
> - **Patch:**
>
> ```yaml
> on:
>   issue_comment:
>     types: [created, edited]
> ```
>
> **Observations:** the job has no job-level `if:`, so every comment starts a runner; the audit route covers it.

**Why each value.**
- "no run" and the cause: [step 2](claude-step-diagnosis.md#2-when-there-is-no-run), check 1, which comes before the workflow's state.
- `none matched`: [step 4](claude-step-diagnosis.md#4-match-the-catalog) found no sharp edge, so the report says so instead of forcing one.
- Medium: [the scale](workflow-audit.md#severity-scale), "a misconfiguration blocks merges or runs".
- The patch adds the missing action and keeps `edited`: the smallest change that makes a new comment start the run ([step 2](claude-step-diagnosis.md#2-when-there-is-no-run)). The missing job-level `if:` is an Observation, not part of the fix.
- Its own approval: a change to what starts the workflow ([Build the patches](workflow-audit.md#build-the-patches), item 6).

## Audit: an implicit-auto mention workflow

**Input.** A public repository's only workflow:

```yaml
on:
  issue_comment:
    types: [created]
permissions:
  contents: read
  id-token: write
jobs:
  claude:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<commit> # <tag>
        with:
          persist-credentials: false
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          claude_args: --allowedTools "mcp__github__*"
```

`v1` resolves to the Snapshot's commit, so the drift check finds nothing changed.

**Report excerpt.**

> **Fix first**
> 1. **F-1** The GitHub MCP server is granted whole · high · `claude.yml:18` (C-11) → Combined patch
> 2. **F-2** Nothing denies the network tools · high · `claude.yml:18` (auto-mode layer B) → Combined patch
> 3. **F-3** The action follows a moving tag · high · `claude.yml:15` (W-04) → Combined patch
> 4. **F-4** The agent runs on the Claude App token, which the job's permissions don't limit · high · `claude.yml:15` (auto-mode layer A) → its own block, its own approval
> 5. **F-5** Tag mode checks out pull request heads, whose nested configuration loads · high · `claude.yml:9` (auto-mode layer F) → its own block, its own approval
>
> ### F-1: The GitHub MCP server is granted whole
> - **Check:** C-11 · **Seen by:** the audit's checks
> - **Where:** `.github/workflows/claude.yml:18`
> - **Severity:** high · **Mode:** auto → auto
> - **Patch:** in the combined patch below · **Approval:** with the rest
>
> **Lower findings:** none. **Medium:** F-6 layer C (no script caps), F-7 W-08 (no time limit or cancelling).
> **Questions:** which GitHub tools the task uses (C-11); the runner's network (layer D).
>
> **Combined patch,** `.github/workflows/claude.yml`:
>
> ```yaml
> jobs:
>   claude:
>     if: contains(github.event.comment.body, '@claude')
>     runs-on: ubuntu-latest
>     timeout-minutes: 30
>     concurrency:
>       group: claude-${{ github.event.issue.number }}
>       cancel-in-progress: true
>     steps:
>       - uses: actions/checkout@<commit> # <tag>
>         with:
>           persist-credentials: false
>       - uses: anthropics/claude-code-action@<commit from the pick pipeline> # <tag>
>         with:
>           anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
>           claude_args: |
>             --permission-mode auto
>             --disallowedTools "WebFetch,WebSearch,Monitor,<every approval, merge and branch-write tool of the pinned server, as mcp__github__<name>>"
> ```

**Why each value.**
- Mode auto before: a tag run on v1.0.273 or later with no exclusion ([Permission mode](action-contract.md#permission-mode)). `--permission-mode auto` is written to freeze it ([Permission mode in patches](auth-and-permissions.md#permission-mode-in-patches)), so after is auto too, and the check of the patches confirms each layer patch on the patched file.
- C-11 and layer B are two findings with one patch block ([Each finding](workflow-audit.md#each-finding)). The workflow shows no GitHub tool the task uses, so the patch grants none and asks ([C-11](workflow-audit.md#checks-for-steps-that-run-claude-code-action)); the deny list is the hard block under auto.
- W-04 high: a moving tag in a job that holds a secret. W-08 medium: layer E's row for an agent job outsiders reach. Layer C medium: nothing caps the agent's writes ([the rating table](auto-mode-audit.md#4-rate-and-report)).
- Layers A and F high, each its own approval: A adds `github_token` and job scopes, at the costs in [Costs of each change](auth-and-permissions.md#costs-of-each-change) (Claude's pushes then start no CI); F adds `if: ${{ !github.event.issue.pull_request }}`, which changes when the job runs. Both stay out of the combined patch until the user decides.
- No `--tools` and no deny on `Edit` or `Write`: a tag workflow that changes code needs them ([Costs of each change](auth-and-permissions.md#costs-of-each-change)).

## Repair: a job waiting for a runner that doesn't exist

**Input.** "CI on main is stuck." The latest run of `build.yml` on the default branch has job `test-macos` `queued` for three hours, with `runs-on: macos-14`.

**Report excerpt.**

> **Result:** 0 critical · 0 high · 1 medium · 0 low · 0 questions — `test-macos` waits for a retired runner label
>
> | Run / attempt | Job / step | Commit | Log line or file:line | Sharp edge |
> | :-- | :-- | :-- | :-- | :-- |
> | <run id> / 1 | test-macos / — | `<short SHA>` | `build.yml:<line>` `runs-on: macos-14`; queued since <time> | `none matched` |
>
> ### F-1: A runner label GitHub retired
> - **Check:** W-10 · **Seen by:** the repair route
> - **Where:** `.github/workflows/build.yml:<line>`
> - **Severity:** medium · **Approval:** with the rest
> - **Patch:**
>
> ```yaml
>     runs-on: macos-15
> ```
>
> | Check | Result | Reason |
> | :-- | :-- | :-- |
> | The next run of `build.yml` on the default branch | not run | waits for the fix to land |

**Why each value.**
- A finding, not a wait: GitHub documents no queue limit for GitHub-hosted runners, so a long queue sends you to the runner table ([ci-repair.md](ci-repair.md), section 1, step 3), where the label matches no runner (W-10).
- W-10 medium: a `runs-on` label that matches no runner ([W-10](workflow-audit.md#checks-every-workflow-gets)); the retirement is a dated fact in [the Snapshot](version-drift.md#snapshot).
- `macos-15`: the nearest newer label of the same OS and architecture in GitHub's table, so the fewest things change. Not `macos-latest`, which moves on its own.
- The fix lands through a pull request, and the repair is done only when the next run on the default branch passes.
