---
type: llm
---

The skill's two files disagree: SKILL.md (line 10) says to write dates as YYYY-MM-DD, while references/format.md (line 5) says DD/MM/YYYY is the only format the accountant's software imports.

PASS if the reply does all three: (1) gives one clear overall verdict on whether the skill is ready to share; (2) reports the date-format conflict as a problem; (3) for that conflict, points to both places by file and line number (any wording, such as `SKILL.md:10` or "line 5 of format.md").
FAIL if any of the three is missing, for example a verdict without line numbers, or line numbers for only one side.
