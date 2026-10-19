# Stage 2: User-Facing Audit Report & Recommendation Gate (MANDATORY HALT)

* **Execution Boundary:** The agent must synthesize discovery findings into the mandatory reviewable audit report below and **halt execution immediately**.
* **Communication Principles:**
  * **Plain-Language Summary First:** Lead with a conversational summary explaining what was audited, whether immediate risks were found, what matters most, and what remains untouched without action.
  * **Explain Git Terms:** Demystify Git jargon on first use (e.g., "worktree: separate checkout directories sharing one repo", "reflog: local ledger of commit head movements").
  * **Commands/OIDs as Evidence Only:** Raw commands and Object IDs (OIDs) serve solely as supporting citations, never as the standalone explanation or conclusion. Never ask the user to infer intent from a raw command list.
  * **Stable Finding IDs (F1, F2, …):** Every identified issue or candidate receives a persistent ID, detailing practical impact, evidence, confidence, and consequences if left alone.
  * **Granular Recommendation IDs (R1, R2, …):** Every proposed action receives a concrete ID with its intended outcome, target, risk, command, and reversibility.
* **Hard Stop & Approval Request:** Complete the audit in full before proposing actions. A generic request like "clean it up" does **not** authorize execution. Conclude with a clear, itemized approval prompt (e.g., *"Please specify which recommendations you authorize, for example: 'Approve R1 and R3; retain R2'."*).

## Mandatory Audit Report Template

```markdown
### Repository Cleanup Audit Report

**Summary:**
[Plain-language executive summary of the repository state: what was audited, primary risks discovered, and confirmation that all changes remain paused pending authorization.]

**Scope & Baseline:**
- Inspected Checkout: `<worktree path>` on branch `<branch>` at commit `<short-sha>`
- Timestamp: `<iso-timestamp>`
- Limits & Exclusions: [State what was not inspected, e.g., remote PR approval states, ignored contents not opened for privacy]

---

### Audit Findings

- **[F1] Stale Local Branch: `<branch-name>`**
  - *What it is:* A local branch merged into `<base>` but not yet deleted.
  - *Practical Effect:* Clutters branch listings; harmless to history but increases cognitive load.
  - *Supporting Evidence:* Verified merged via `git merge-base --is-ancestor` into commit `<oid>`.
  - *Confidence & Inaction Impact:* High confidence. If left alone, repository size is unchanged, but branches list stays noisy.

- **[F2] Abandoned Worktree Registration: `<path>`**
  - *What it is:* A registered linked worktree whose folder on disk no longer exists.
  - *Practical Effect:* Blocks branch reuse and shows warnings during Git worktree queries.
  - *Supporting Evidence:* Detected missing from filesystem during `git worktree list --porcelain`.
  - *Confidence & Inaction Impact:* High confidence. If left alone, Git metadata remains stale.

- **[F3] Retained Local Configuration / Cache: `<path/>`**
  - *Status:* Retained for safety (matches ignore rule, rebuild cost unverified).

---

### Recommendations Awaiting Approval

| ID | Finding Ref | Target | Proposed Action | Risk | Reversibility / Recovery Path |
|---|---|---|---|---|---|
| **R1** | F1 | `branch: <name>` | Delete verified merged local branch | Low | Reversible via rollback ref `refs/backup/<date>-<name>` |
| **R2** | F2 | `worktree: <path>` | Prune stale worktree administrative registration | Low | Administrative metadata only; recreate with `git worktree add` |
| **R3** | F3 | `cache: <path/>` | Remove generated build cache (`git clean -fdX -- <path/>`, previewed with `git clean -ndX`) | Medium | Irreversible without rebuild; confirm rebuild tooling is ready |

---

*Decision Request:*
Please review the recommendations above and specify which items to execute (e.g., **"Approve R1 and R2; reject R3"**). No files or branches will be modified until you confirm.
```
