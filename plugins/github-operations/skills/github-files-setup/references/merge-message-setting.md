# Merge message setting

GitHub has no repository file for merge commit messages: the default message of a squash or a merge commit is a repository setting. A setting affects everyone: read the current values, show the change, and apply it only after approval. It needs admin permission. No GitHub MCP tool changes it; use `gh api` REST, or give the user the path **Settings → General → Pull Requests**.

1. **Read the settings:** `gh api repos/<owner>/<repo> --jq '{allow_squash_merge, allow_merge_commit, allow_rebase_merge, squash_merge_commit_title, squash_merge_commit_message, merge_commit_title, merge_commit_message}'`.
2. **Read the convention:** the last 50 commit titles on the default branch (`git log --format=%s -50 <default branch>`) and the repository's `CONTRIBUTING`, `CLAUDE.md` or `AGENTS.md`. Note whether titles follow Conventional Commits (`type(scope): summary`) or plain sentences, and whether the repository squashes, merges or rebases. Follow what it does; never impose a format it doesn't use.
3. **Choose the default message with the user.** Show the options for each merge method the repository allows, with their trade-offs ([MERGE_TEMPLATE/merge-message.md](../assets/MERGE_TEMPLATE/merge-message.md) explains them):

   | Squash merge option | `squash_merge_commit_title` | `squash_merge_commit_message` |
   | :-- | :-- | :-- |
   | Default message: the commit's title and message for one commit; the PR title and the list of commits otherwise | `COMMIT_OR_PR_TITLE` | `COMMIT_MESSAGES` |
   | Pull request title | `PR_TITLE` | `BLANK` |
   | Pull request title and commit details | `PR_TITLE` | `COMMIT_MESSAGES` |
   | Pull request title and description | `PR_TITLE` | `PR_BODY` |

   For merge commits, `merge_commit_title` is `MERGE_MESSAGE` (the default, `Merge pull request #123 from <branch>`) or `PR_TITLE`, and `merge_commit_message` is `PR_TITLE`, `PR_BODY` or `BLANK`.
4. **Apply the approved choice.** Send each title with its message, because GitHub requires the title whenever the message is set:

   ```bash
   gh api --method PATCH repos/<owner>/<repo> \
     -f squash_merge_commit_title=<title value> -f squash_merge_commit_message=<message value>
   ```

   Change the merge commit pair the same way, only when the repository allows merge commits.
5. **Propose turning off the merge methods the repository does not use** (`allow_merge_commit`, `allow_rebase_merge`, `allow_squash_merge`, each `-F <key>=false`), as a separate approval.
6. **Read the settings again** and confirm they show the approved values.
