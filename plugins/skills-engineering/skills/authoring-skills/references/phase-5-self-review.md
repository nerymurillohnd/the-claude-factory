# Phase 5: Self-review

How to review the skill from the model's seat and run its checks before you deliver it.

1. Walk each use case from the model's seat: from the description, through the body and the pointers it follows, to its result, naming what the model decides at each step. Rewrite wherever it would decide wrong.
2. Run the mechanical check: `claude plugin validate [path]`, where `[path]` is the plugin or skills folder, wherever the Claude Code CLI exists; for an upload, check the skill against the rules for a skill that leaves Claude Code, which Phase 2 describes.
3. Copy this checklist and check the skill you write against it:

   ```text
   - [ ] Each section prevents a failure you can name from a use case or a correction.
   - [ ] The description carries every use case's trigger words and the boundary with each sibling skill from phase 2, within every target's limit.
   - [ ] Every supporting file is linked from SKILL.md on its own line, with its verb and condition.
   - [ ] A search for each number, limit and rule finds it in one file only.
   - [ ] Every frontmatter key is accepted on every target surface.
   - [ ] Every shown command pins its versions and explains its placeholders, every bundled script is listed in SKILL.md with its purpose, and no path variable sits in a reference file.
   - [ ] Nothing in SKILL.md expands or runs by accident (see Gotchas in SKILL.md).
   - [ ] The body and every file meet the size and link rules of standard 5, Progressive disclosure, in this skill's `SKILL.md`.
   ```

4. Fix each failed item and check it again. After 3 rounds, or when the same item fails again after a fix, treat it as unmet. When an item can't be met, such as a check you can't run here, leave it unmet and list it in the report with the reason.

Exit: every checklist item and check passes, or each one that can't is listed with its reason for the report.
