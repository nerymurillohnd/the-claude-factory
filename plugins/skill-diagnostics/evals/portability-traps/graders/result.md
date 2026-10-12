---
type: llm
---

The skill has four planted upload problems:
(a) `when_to_use` is not one of the six fields an upload accepts, so the upload fails;
(b) `name` contains the reserved word `claude`, which uploads reject;
(c) the unquoted description contains a space followed by `#owner`, which strict YAML reads as a comment, cutting the description at that point;
(d) the body runs the script through the skill-directory variable and by its path, which does not work in an uploaded skill (the variable is not substituted there, and the script should be called through its interpreter).

PASS if the reply identifies at least three of (a), (b), (c), (d) as problems for the upload.
FAIL if it identifies fewer than three.
