# Verification gate

The orchestrator's last gate before the verdict: every finding is checked against the skill's files and against live official sources, and nothing reaches the report on a lens's word alone. Use whatever tools, skills and connections this session has to read files and fetch web pages.

## Contents

- Check each finding
- Recent official changes
- Send back what fails
- No live sources

## Check each finding

1. **Quote.** Read the cited lines yourself. The quote must match the file verbatim at that `file:line`; for something absent, confirm it is absent from every file of the skill.
2. **Official source.** When the finding states a rule, a limit, a field, a command or how a platform behaves, open the live official page that owns it and copy the sentence that supports it, with its URL. Ask fetch tools for verbatim quotes: a summary is not evidence. A finding about the skill's internal logic (one file contradicts another, a value has no source) needs no page: its evidence is the skill's own quotes.
3. **Focus.** The finding must be about the audited skill and answer its lens's question (conformance: rules and portability; executability: could a model run it without guessing).
4. **Classify:** verified; partly false (some of it is wrong); false; off-focus.

## Recent official changes

Check what changed in the last 15 days, counted back from today, in:

- Claude Code changelog: <https://code.claude.com/docs/en/changelog> (built from <https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md>) and the weekly digests at <https://code.claude.com/docs/en/whats-new>
- Claude apps release notes (Claude, Cowork): <https://support.claude.com/en/articles/12138966-release-notes>
- Agent Skills specification and best practices, which have no changelog: <https://agentskills.io/specification>, <https://agentskills.io/skill-creation/best-practices>, and the commit history of <https://github.com/anthropics/skills> (its `spec/` folder)

For each finding, note whether a recent change confirms it, changes it or makes it obsolete, and correct it.

## Send back what fails

- Send each partly false, false or off-focus finding back to the lens agent that produced it, with your evidence, and ask it to correct or withdraw it. Relaunch that agent with the same inputs plus the disputed findings when it can't be resumed.
- At most two rounds. What is still not verified after that: keep only the part you verified yourself, and list the rest under Coverage as refuted, with the reason.
- Add a finding the lenses missed only with the same evidence a lens would give.

## No live sources

When no page or changelog can be reached: keep the findings, mark each `not verified live`, and mark the verdict **provisional** with the reason.
