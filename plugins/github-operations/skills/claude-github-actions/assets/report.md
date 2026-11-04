# <Route>: <owner>/<repo>

**Result:** <one line: what was examined and what was found or changed>
**Scope:** <workflows, runs or files examined> · checked <YYYY-MM-DD HH:MM UTC>
**Left for you:** <each decision or action only the user can take>, or `nothing`

## Evidence

| Run / attempt | Job / step | Commit | Log line or file:line | Sharp edge |
| :-- | :-- | :-- | :-- | :-- |
| <run id> / <n> | <job> / <step> | `<short SHA>` | "<exact line>" | SE-<nn>, or `none matched` |

## Findings

<!-- Audit route: one block per finding. Diagnosis and repair routes: one block per cause. -->

### <F-1>: <title>

- **Where:** `<file>:<line>`
- **Triggered when:** <what an attacker or a failure needs>
- **Impact:** <what happens> · **Severity:** <critical | high | medium | low>
- **Patch:**

  ```yaml
  <the exact replacement lines>
  ```

- **Residual risk:** <what the patch leaves>, or `none`

## Changes

| Change | Permissions, tools or authentication it adds or removes | Approved by the user |
| :-- | :-- | :-- |
| <patch or pull request> | <delta, including tools a plugin command grants> | <yes, when> |

## Version provenance

| Reference | Tag | Commit SHA | Resolved with, when |
| :-- | :-- | :-- | :-- |
| `<owner>/<action>` | `<vX.Y.Z>` | `<full SHA>` | `git ls-remote`, <YYYY-MM-DD> |

## Validation

| Check | Result | Reason |
| :-- | :-- | :-- |
| <actionlint, zizmor, the next run on the default branch…> | <passed, failed, not run or blocked> | <why, for anything but passed> |
