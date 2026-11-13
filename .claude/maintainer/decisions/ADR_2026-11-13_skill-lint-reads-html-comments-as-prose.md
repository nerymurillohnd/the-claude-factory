---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# skill-lint reads HTML comment content as prose only

## Scope

The Markdown scan in `scripts/validators/skill_lint/markdown.py` and the rules that read its links, headings, anchors, fences and prose (CO-07, CO-08, CO-11). Maintainer scope.

## Context and problem statement

skill-lint took links, headings, anchors and fences inside `<!-- ... -->` as real, so `<!-- see [old](gone.md) -->` gave a false CO-07 error. GitHub does not render comments, but Claude reads the raw SKILL.md and sees them. Several github-operations assets use comments (`report.md`, `audit-report.md`, the pull request templates).

## Decision drivers

- No false CO-07 or CO-08 from text that is not a link where it renders.
- Keep checking what Claude does read, such as time-sensitive wording.

## Considered options

- **No links, headings, anchors or fences come from comment content; its text stays in prose, so CO-11 still checks it**: chosen.
- **Ignore comment content for every rule**: rejected because Claude reads it, so CO-11 should still see it.
- **Keep checking links inside comments**: rejected because a comment link is not a link on GitHub, and template instructions in comments would give false errors.

## Decision outcome

Chosen option: **comments are prose only**, because it removes the false link errors and keeps the time-sensitive check on text Claude reads. A `<!--` inside inline code opens no comment.

### Consequences

- Good, because comment links in templates no longer fail CO-07.
- Bad, because a broken link that only Claude reads inside a comment is not reported.

## More information

- Recorded in the spec's CO-07 row. Implemented in commit 49de02e, with the tests in `CommentTest` (`test_markdown.py`).
- The owner decided this on 2026-11-12, when approving the review-fix plan.
