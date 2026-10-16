# GitHub Gate

- Changes to plugin manifests, components and dependencies always go through a PR.
- Changes to maintainer documentation need no PR unless Nery explicitly asks for one.
- Every PR carries labels. Always read `gh label list` and apply the ones that fit the changes.
- Pushes of changes outside `plugins/` are authorized. Pushes of changes in `plugins/` need Nery's approval.
- Always stage work after edits.
- Commits are allowed. Commit the work before ending the turn.
- Sign every commit and give it a descriptive message of the changes, following the user-level guidelines.

## Reviewing a PR

- Check the failed jobs and the reviews of Claude and of third parties. Verify each finding.
- Fix the root cause, commit and push again. A push to a plugin PR needs Nery's approval.
- Repeat until everything is green and no more reviews, issues or failed jobs are found.
- Comment on each review and resolve it. A PR is not ready to merge before that.
- Always stop at ready to merge and tell Nery, then wait for the green light.
