# ✅ Closed Debt

> [!NOTE]
> The history of technical and maintenance debt that is no longer open: fixed, no longer applicable, or kept for good on purpose. Each entry holds the evidence that closes it. Entries arrive here from `pending-debt.md` with the same ID.

**Important:** a closed entry is a dated historical record. If a later change invalidates the closure, keep the original entry and open a new pending item that links back to it. The only field that changes afterwards is "Superseded by".

## 🚦 Outcomes

| Outcome | Meaning | Evidence it needs |
| --- | --- | --- |
| resolved | A fix aimed at this item was made and it works | A positive check and a negative check |
| obsolete | The condition no longer exists for another reason: a change not aimed at this item removed the code or changed the architecture, or the item was logged in error or duplicates another | A negative check, and what changed |
| accepted | The user decided to keep the condition for good | The accepted ADR that records the decision |

## 📚 Index

| Closed on | ID | Outcome | Closure | Superseded by |
| --- | --- | --- | --- | --- |
| 2026-11-13 | DEBT-002 | resolved | The cloud setup script pins every tool it installs | none |

## 🏁 Closed items

### DEBT-002 — The cloud setup script pins every tool it installs

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-11-13 |
| **Logged on** | 2026-11-13 |
| **Owner** | unassigned |

#### ❗ The problem

The `the-claude-factory` environment's setup script installed `typescript-language-server`, `bash-language-server` and `svelte-language-server` at `@latest`, ShellCheck and shfmt from webi with no version, and actionlint at `@latest`, so two snapshots built on different days could hold different tool versions and give different lint results on the same commit.

#### 🔧 The closure

The owner chose exact pins on 2026-11-13. The setup script, replaced through the environment tools the same day, installs `typescript-language-server@6.1.0`, `bash-language-server@5.8.1`, `svelte-language-server@0.18.6`, `shellcheck@v0.11.0` and `shfmt@v3.14.1` through webi, and `actionlint@v1.7.12` through `go install`.

The image ships its own ShellCheck 0.11.0 in `/nix/var/nix/profiles/default/bin`, which comes first on the session's `PATH`, so a webi pin alone did not decide which ShellCheck runs: a request for webi's 0.10.0 switched the webi link and left `shellcheck --version` at 0.11.0. The script therefore appends one marked line to `~/.bashrc` that puts `~/.local/bin` first, matching the owner's machine, and logs `shellcheck on PATH is not 0.11.0` when the version on `PATH` differs.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | Running the script from the checkout's parent, without its `~/.bashrc` step, exited 0 in 15 seconds; `npm ls -g` listed `bash-language-server@5.8.1`, `svelte-language-server@0.18.6` and `typescript-language-server@6.1.0`; the summary showed shfmt v3.14.1 and actionlint v1.7.12; webi's ShellCheck link pointed to `shellcheck-v0.11.0`. The `~/.bashrc` step, run twice in a temporary `HOME`, wrote one line and moved `~/.local/bin` ahead of a leading `/nix/x`. ShellCheck reported nothing on the script. |
| 🚫 **Negative:** the original failure or condition is gone | The script sent to the environment contains no `@latest` (count 0) and no unversioned webi URL. |

#### 🔗 Follow-up

- **Residual risk:** the `~/.bashrc` step was not run against this session's own `~/.bashrc` (a write there was blocked by the permission classifier), so its effect on `PATH` is confirmed only at the first fresh session; the setup script's ShellCheck warning shows it if it fails. Version bumps for these tools are manual, since Dependabot does not read the setup script.
- **Closed by:** the setup script replacement of 2026-11-13, under ADR_2026-11-13_cloud-dependencies-through-setup-script-and-npm-run-setup.
- **Related records:** ADR_2026-11-13_cloud-dependencies-through-setup-script-and-npm-run-setup, ADR_2026-11-13_python-3-15-default-and-pinned-in-cloud-setup.
- **Superseded by:** none

<!--
Entry format. Copy this block above this comment for each closed item and add its row to the Index.
Use the ID the item had in pending-debt.md. Delete these instructions from the copy.

### DEBT-NNN — {{Short closure title}}

| Field | Value |
| --- | --- |
| **Outcome** | {{resolved, obsolete or accepted}} |
| **Closed on** | {{YYYY-MM-DD}} |
| **Logged on** | {{YYYY-MM-DD, copied from the pending entry}} |
| **Owner** | {{Copied from the pending entry}} |

#### ❗ The problem

{{The original limitation, risk or follow-up, as it stood in the pending entry.}}

#### 🔧 The closure

{{resolved: the corrective change and the resulting state. obsolete: what changed and why the condition no longer applies, or that it was logged in error or duplicates DEBT-NNN. accepted: the ADR ID and the decision to keep the condition.}}

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | {{resolved: the fix works, with commands, tests or review. obsolete: "not applicable". accepted: the ADR ID with status accepted.}} |
| 🚫 **Negative:** the original failure or condition is gone | {{resolved or obsolete: it no longer reproduces or exists; showing that a new path works is not enough. accepted: "not applicable".}} |

#### 🔗 Follow-up

- **Residual risk:** {{Anything left over, or "none".}}
- **Closed by:** {{The ADR ID, commit or pull request that caused the closure, or "none".}}
- **Related records:** {{Links to issues, ADRs or PRs, or "none".}}
- **Superseded by:** {{The ID of a newer item when this closure no longer describes the current state, or "none".}}
-->
