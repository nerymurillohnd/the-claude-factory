# Phase 5: Self-review

How to review the skill from the model's seat and run its checks before you deliver it.

1. Walk each use case from the model's seat: from the description, through the body and the pointers it follows, to its result, naming what the model decides at each step. Rewrite wherever it would decide wrong.
2. Run the mechanical checks:
   - `claude plugin validate [path]`, where `[path]` is the plugin or skills folder, wherever the Claude Code CLI exists.
   - The skill checks, with the command Phase 5 of `SKILL.md` gives: it prints one line per check, then `results: [folder]`. For each check with findings, read `[folder]/[check id].json` with the Read tool. Leave the folder in place: the plugin removes it when the session ends.
   - Fix every finding on a surface the skill reaches. A plugin skill reaches Claude and Claude Code through its plugin, so fix its `claude-code` findings, and its `open-spec` and `upload` findings only when the skill is also distributed on its own, as an upload or for agents outside Claude. A field such as `argument-hint` is valid in a plugin skill even though `non-spec-key` reports it.
   - The skill pre-approves this command only in the turn that invoked it, so Claude Code may ask the user to approve it here: say that it runs the plugin's checks, which write their results only to the plugin's own data folder. Where `python3` isn't found, use `python`; where neither runs, or the command says Python is older than 3.12, list the skill checks as not run in the report.
3. Copy this checklist and check the skill you write against it:

   ```text
   - [ ] Each section prevents a failure you can name from a use case or a correction.
   - [ ] Every fact the skill states about its domain comes from a primary source, at the version or edition its users rely on.
   - [ ] The description carries every use case's trigger words and the boundary with each sibling skill from phase 2, within every target's limit.
   - [ ] Every supporting file is linked from SKILL.md on its own line, with its verb and condition.
   - [ ] A search for each number, limit and rule finds it in one file only.
   - [ ] Every frontmatter key is accepted on every target surface.
   - [ ] Every shown command that installs or runs a package pins its version, every placeholder is explained, every bundled script is listed in SKILL.md with its purpose, and no path variable sits in a reference file.
   - [ ] Nothing in SKILL.md expands or runs by accident (see Gotchas in SKILL.md).
   - [ ] The body and every file meet the size and link rules of standard 5, Progressive disclosure, in this skill's `SKILL.md`.
   ```

4. Fix each failed item and check it again. After 3 rounds, or when the same item fails again after a fix, treat it as unmet. When an item can't be met, such as a check you can't run here, leave it unmet and list it in the report with the reason.

## Exit

Every checklist item and check passes, or each one that can't is listed with its reason for the report. Then return to the step list in `SKILL.md`, and go on with the next file or step.
