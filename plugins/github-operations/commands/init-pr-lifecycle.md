---
description: Takes the current pull request from the stage it is in to merge-ready with the auto-pr-lifecycle skill, asking before each push and before the merge.
argument-hint: "[PR number or URL]"
disable-model-invocation: true
---

Take this pull request through its lifecycle, from where it stands to the merge.

1. Find the pull request (the one in the arguments, or the current branch's) and the stage it is in: not opened, checks running, failing, under review, ready, or merged.
2. Load the `github-operations:auto-pr-lifecycle` skill and follow it from that stage.
3. When the tracker reports problems, launch the fixer and wait for its results.
4. Tell the user what was fixed and ask whether to push.
5. After the push, track again. Repeat steps 3 to 5 until nothing is left to fix.
6. Launch the finalizer and wait for its verdict.
7. When everything is resolved, tell the user and ask for the merge approval.
