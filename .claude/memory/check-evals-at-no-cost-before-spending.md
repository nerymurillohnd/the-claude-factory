---
name: check-evals-at-no-cost-before-spending
description: Run every no-cost eval check before the first run that spends; a smoke run is the last check, not the first
metadata:
  type: feedback
---

Before any `claude plugin eval` run that spends, run every check that costs nothing and fix what it finds: `claude plugin validate --strict`, each fixture by hand, each grader against a real or hand-written trace, the commands and templates the skill under test teaches, and every suite loaded with `--max-cost-usd 0` and the run's real flags (observed on 2.1.325 to stop as partial before the first run; the docs say only that the ceiling is checked before each run starts).

**Why:** on 2026-11-15 the first writing-hooks smoke runs failed on causes a no-cost check finds: a `plugins` entry the CLI refuses, a missing Bash sandbox, graders that matched the skill's own text. The owner asked why a smoke run came first; the evals rule named only the smoke run, and the testing skill listed the no-cost load check last, under CI.

**How to apply:** follow step 4 of "Evals in brief" in `plugin-engineering:plugin-testing-and-debugging` and the evals rule; ask for a paid run only after every no-cost check passes, and say which ones ran.
