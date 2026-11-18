# Phase 5: Self-review and deliver

How to review the skill from the model's seat, run its checks and deliver it.

1. Walk each use case from the model's seat: from the description, through the body and the pointers it follows, to its result, naming what the model decides at each step. Rewrite wherever it would decide wrong.
2. Run the mechanical check: `claude plugin validate` on a plugin or skills folder where the Claude Code CLI exists; for an upload, check the skill against the rules for a skill that leaves Claude Code, which you applied in phase 2.
3. Copy this checklist and check the skill you write against it:

   ```text
   - [ ] Each use case walks to its result with no step where the model would decide wrong.
   - [ ] Each section prevents a failure you can name from a use case or a correction.
   - [ ] The description carries every use case's trigger words and the boundary with each sibling skill from phase 2, within every target's limit.
   - [ ] Every supporting file is linked from SKILL.md on its own line, with its verb and condition.
   - [ ] A search for each number, limit and rule finds it in one file only.
   - [ ] Every frontmatter key is accepted on every target surface.
   - [ ] Nothing in SKILL.md expands or runs by accident (see Gotchas in SKILL.md).
   - [ ] The body and every file meet the size and link rules in SKILL.md's Standing rules.
   ```

4. Fix each failed item and check it again. When an item can't be met, such as a check you can't run here, stop and list it in the report with the reason.
5. Report what you built and what each file holds, each decision and its reason, what you checked and how, what you couldn't check and why, and the assumptions still open. Never report a check you didn't run as passed.
6. Ask the requester how to proceed: keep the skill as it is, run the audit, build evals, or anything else they type. This step is mandatory every time a skill is delivered; never skip it or continue on your own.
