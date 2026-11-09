# Skill audit: <skill name>

Skill: <absolute path>
Origin: <account | plugin | personal | project | loose>
Surfaces it reaches: <list>
Claude Code release: <version, or unknown>
Profile: <each profile question with its answer>

## Verdict

<pass | pass with warnings | fail | not determinable> · Provisional: <no | yes: the source that was tried and couldn't be reached>
Reason: <the verdict rule that matched, in one sentence>

## What ran

Scripts:
- check-metadata · <ran | couldn't run: <error>>
- check-structure · <ran | couldn't run: <error>>
- check-runtime · <ran | couldn't run: <error>>
- check-size · <ran | couldn't run: <error>>
- check-evals · <ran | couldn't run: <error>>

Agents: <each agent · complete | incomplete: <reason>>, or "inline in chat: no independent reviewers, cold executor or verifier ran"

Changelog read: <versions> · Unread: <versions, or none>

Reports saved: <the folder that holds `agents/` | missing: <which agents> | in chat: not saved>

Verdict recorded: <yes | no: the error | not in chat>, filled after the verdict is recorded

## Checklist

One row per item of `references/checklist.md`, in its order. The item's condition is in that file; don't copy it here.

| Item | Status | Findings or reason |
| --- | --- | --- |
| <ID> | <pass | fail | n/a | not assessed by this audit> | <finding IDs; for n/a, why the rule doesn't apply; for evals items, the evaluation that would assess it> |

## Findings

Order: high, then medium, then low. Write `No findings.` when there are none.

### High

#### <finding ID>
- Item: <checklist item ID>
- Location: <path relative to the skill>:<line or lines>, every location for a merged finding
- Evidence: "<verbatim quote>", or where the missing information is needed
- Fix: <one concrete change>
- Verifier: <upheld | downgraded from <severity> | not verified against the official source | proved by <script> | confirmed by the orchestrator> · <the official source or changelog entry it rests on, or the script check>

### Medium

<same fields>

### Low

<same fields>

## Accounting

Every finding ID of every agent report, the cold executor's points included, and every failed proved check and confirmed lead, once each. The count per agent matches its saved report.

| Finding | From | Outcome |
| --- | --- | --- |
| <ID in the agent report> | <agent name, script or orchestrator> | <kept as <ID> | merged into <ID> | withdrawn> |

## Withdrawn

<finding ID · the verifier's evidence>, or none
