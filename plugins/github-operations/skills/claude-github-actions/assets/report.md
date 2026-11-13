# <Route>: <owner>/<repo>

<!-- When the repository's owner and name can't be read, use the local folder's name followed by "(no remote)". -->

<!-- Keep every section, in this order. A section with nothing to show keeps its heading and says `none`. -->

**Result:** <n> critical · <n> high · <n> medium · <n> low · <n> questions — <one line: what was examined, and the cause or the main finding>
**Scope:** <workflows, runs or files examined> · checked <YYYY-MM-DD HH:MM UTC>
**Detection layers** (audit route; in the other routes write `not run: <route> route`): code scanning <run: n alerts on workflows | not set up | unavailable: reason | not inspected: reason> · zizmor <version | not installed | not run: reason> · actionlint <version | partial: <file> didn't parse | not installed | not run: reason>; <the repository silences some zizmor findings, when it does>
**Left for you:** <each decision or action only the user can take, questions included>, or `none`

## Fix first

<!-- Every critical and high finding, most severe first, each linked to its block, then the combined patch for each file it touches. -->

1. **<F-1>** <title> · <severity> · `<file>:<line>` → [Combined patch](#combined-patch), `<file>`, or → its own block, when it needs its own approval

## Evidence

<!-- Diagnosis and repair routes: one row per run. -->

| Run / attempt | Job / step | Commit | Log line or file:line | Sharp edge |
| :-- | :-- | :-- | :-- | :-- |
| <run id> / <n>, or `no run` | <job> / <step> | `<short SHA>` | "<exact line>" | SE-<nn>, or `none matched` |

<!-- Audit route: one row per finding. -->

| File:line | Check | Layers that saw it | claude-code-action commit the step runs |
| :-- | :-- | :-- | :-- |
| `<file>:<line>` | <W-nn, C-nn, layer, or scanner rule ID> | <code scanning, zizmor, actionlint, the audit's checks> | `<short SHA>` (<tag>), or `—` |

## Findings

<!-- Critical, high and medium findings, by severity, then file, then line. Diagnosis and repair routes: one block per cause, whatever its severity; Lower findings holds only findings that are not the diagnosed cause. -->

### <F-1>: <title>

- **Check:** <W-nn, C-nn, an auto-mode layer, a scanner's rule ID, or `none` for a diagnosed cause> · **Seen by:** <layers>
- **Where:** `<file>:<line>`; for a composite action or reusable workflow, the caller's and the callee's
- **Triggered when:** <what an attacker or a failure needs>
- **Impact:** <what happens> · **Severity:** <critical | high | medium | low>
- **Mode:** <effective mode before> → <after the patch>, for a claude-code-action step
- **Rests on unverified:** <an unverified fact the finding depends on, and what would settle it>, or `nothing`
- **Patch:**

  ```yaml
  <the exact replacement lines>
  ```

- **Approval:** <with the rest | its own, because it changes triggers, permissions, secrets or the mode>
- **Residual risk:** <what the patch leaves>, or `none`

## Hypotheses

<!-- Diagnosis route, when no sharp edge matched and no cause is proved: ranked, most likely first. Otherwise `none`. -->

| Rank | Hypothesis | Log line that supports it | Next check that would confirm it |
| :-- | :-- | :-- | :-- |
| 1 | <hypothesis> | "<exact line>" | <check> |

## Lower findings

| ID | Check | Where | What | Patch |
| :-- | :-- | :-- | :-- | :-- |
| <F-n> | <check> | `<file>:<line>` | <one line> | <one line, or see Combined patch> |

## Questions

| Fact | Why it couldn't be read | Checks it decides | Rating if the answer is the risky one | Answer that lowers it |
| :-- | :-- | :-- | :-- | :-- |
| <the missing fact> | <reason> | <W-nn, C-nn, layer…> | <severity> | <answer> |

## Observations

<!-- What matches no check and is not a finding, such as upstream keeping auto off for workflows with allowed_* lists. -->

- <observation>

## Combined patch

<!-- One block per file the patches touch: every finding's change merged, the mode frozen. A change that needs its own approval stays out, with its patch in its finding block. -->

`<file>` (findings <F-1, F-3…>):

```yaml
<the whole replacement for the jobs or steps it changes>
```

## Changes

| Change | Permissions, tools or authentication it adds or removes | Approved by the user |
| :-- | :-- | :-- |
| <patch or pull request> | <delta, including tools a plugin command grants> | <yes, when> |

## Version provenance

| Reference | Pinned as | Commit | Snapshot | Drift | Resolved with, when |
| :-- | :-- | :-- | :-- | :-- | :-- |
<!-- One row per distinct `uses:` string, listing every line it appears on. -->
| `anthropics/claude-code-action` | `<ref in the file>` (lines <n, m>) | `<full SHA>` | `<snapshot short SHA>` (<tag>) | <none | topics: …, read at the pin | not an upstream commit | unverified: reason> | <`git ls-remote` | "Set up job" log | MCP>, <YYYY-MM-DD> |
| `<owner>/<action>` | `<ref>` | `<full SHA>` | — | — | <how>, <YYYY-MM-DD> |

- **Unmapped changes:** <files changed between the snapshot and the pin that hold none of the skill's facts, and what they change>, or `none`, or `not checked (MCP only)`
- **Release notes read:** <tags>, or `none needed`
- **How each new tag was chosen:** <the pick pipeline, in the current major | a major jump the user approved>

## Validation

| Check | Result | Reason |
| :-- | :-- | :-- |
| <effective mode re-derived, each check on the patched files, auto-mode layers, actionlint, the next run on the default branch…> | <passed, failed, not run or blocked> | <why, for anything but passed> |
