---
type: llm
---

The skill has four planted problems for a claude.ai upload used in Cowork:
(a) `when_to_use` is not one of the six fields an upload accepts, so the upload fails with an error;
(b) `name` contains the reserved word `claude`, which uploads reject;
(c) the unquoted description contains a space followed by `#owner`, which YAML reads as a comment, cutting the description at that point;
(d) the `` !`date +%F` `` line does not run in Cowork (Claude Code replaces it with a placeholder there), so the due dates, which step 2 counts from it, have no date to start from.

(b) and (c) need only general knowledge; (a) and (d) need current platform facts.

PASS if the reply identifies both (a) and (d) as problems for this use.
FAIL if it misses either of them.
