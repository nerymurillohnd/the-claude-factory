---
type: llm
focus: last_message
---

PASS if the reply says a project thread loads from the repository only its `CLAUDE.md` files and rules, so the repository's `.claude/skills/` triage skill, its `.claude/settings.json` hooks and the plugins it enables are not loaded there, and points to the documented replacements: add the formatter plugin in Project settings > Plugins (it loads into new threads), turn the triage skill on for the claude.ai account, or run the thread on the user's computer.
FAIL if the reply treats the missing skill or hook as a bug in the plugin or skill files to fix in the repository, or claims to have run and fixed the hook.
Formatting, headings and wording do not decide the verdict.
