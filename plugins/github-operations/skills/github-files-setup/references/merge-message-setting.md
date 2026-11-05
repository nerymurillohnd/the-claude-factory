# Merge message setting

A repository setting affects everyone: read the current values, show the change, and apply it only after approval.

1. Read: `gh api repos/<owner>/<repo> --jq '{squash_merge_commit_title, squash_merge_commit_message, merge_commit_title, merge_commit_message, allow_squash_merge, allow_merge_commit, allow_rebase_merge}'`.
2. Propose "Pull request title and description" as the default message, so the merge message follows the PR template:

   ```bash
   gh api -X PATCH repos/<owner>/<repo> \
     -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=PR_BODY \
     -f merge_commit_title=PR_TITLE -f merge_commit_message=PR_BODY
   ```

3. Propose turning off the merge methods the repository does not use.
4. Read the values back after the change.
