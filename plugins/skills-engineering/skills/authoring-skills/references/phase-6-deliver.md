# Phase 6: Deliver

How to hand the skill to the requester and ask how to proceed.

## Contents

- Report
- Gotchas
- The question
- Act on the answer

## Report

Report what you built and what each file holds, each decision and its reason, what you checked and how, what you couldn't check and why, and the assumptions still open. Never report a check you didn't run as passed.

## Gotchas

- An AskUserQuestion call holds 1 to 4 questions, each with 2 to 4 options and a header of up to 12 characters. The tool always adds an "Other" choice where the requester types free text.
- A question that times out submits the options already selected. Treat it here as unanswered even so: list the options in your reply and stop until the requester answers.
- Without the tool, ask the same question in the reply, list the same options, and stop until the requester answers.

## The question

Ask it every time a skill is finished; never skip it or continue on your own. Leave out the audit option when `skills-engineering:auditing-skills` isn't among your available skills. Name the evals by the skill type you identified in phase 2.

```text
Question: The skill [name] is finished and self-reviewed. How do you want to proceed? You can choose more than one, or type anything else under Other.
Header: Next step
Multiple selection: yes
Options:
- Keep it as is (Recommended): The skill is done as delivered.
- Run the audit: Load auditing-skills and run its full battery of reviewer agents on the skill.
- Build evals: [Plugin evals, run with claude plugin eval. | Evals for skills, run in clean subagents.]
```

## Act on the answer

- Keep it as is, alone: the skill is done.
- Run the audit, build evals, or both, with or without Keep it as is: go to phase 7 with what they chose.
- Text under Other: do what the requester wrote. When it changed the skill, run phase 5 again, report what changed, then ask again.

Exit: the requester keeps the skill as it is, or chose phase 7.
