# Phase 12: External verification and run history (steps)

## 12.1 External verification

Carried out by `docs-researcher` (`agents/docs-researcher.md` at the plugin root). It runs on every audit: the reviewers extract the claims their instructions make about tools, versions, and compatibility, and a false or outdated claim becomes a finding. A retry or a challenge round can return claims that the first batch never saw. Send them as a further batch before Phase 13, and validate the findings that its verdicts produce like any other new finding.

## 12.2 Optional run history (only if approved in Gate 1)

1. Compare the findings with the previous run by unit id (see Normalizing findings in SKILL.md) and classify each as new, resolved, persistent, reappeared, or recategorized. The same unit with another category is `recategorized`.
2. Record the run in the project index.
3. Leave a one-time notice for the next session; the user can disable it. (Unavailable until the plugin ships a session-start hook.)
