# Merge message setting

GitHub has no repository file for merge commit messages: the default message of a squash or a merge commit is a repository setting. A setting affects everyone: read the current values, show the change, and apply it only after approval. It needs admin permission. No GitHub MCP tool changes it; use `gh api` REST, or give the user the path **Settings → General → Pull Requests**.

1. **Read the settings:** the merge fields come with the repository read at step 1 ([github-access.md](github-access.md#operations)). Also read the rules that apply to the default branch: `gh api repos/<owner>/<repo>/rules/branches/<default branch>` lists every active ruleset rule, and a `pull_request` rule's `allowed_merge_methods` or a `required_linear_history` rule limits the methods a pull request can use. Classic branch protection can require linear history too (`gh api repos/<owner>/<repo>/branches/<default branch>/protection`, which answers 404 when the branch has none).
2. **Read the convention:** the last 50 commit titles on the default branch (`git log --format=%s -50 <default branch>`) and the repository's `CONTRIBUTING`, `CLAUDE.md` or `AGENTS.md`. Note whether titles follow Conventional Commits (`type(scope): summary`) or plain sentences, and whether the repository squashes, merges or rebases. Follow what it does; never impose a format it doesn't use.
3. **Choose the default message with the user.** Show the options for each merge method the repository allows, with their trade-offs, so the default matches how the repository writes its history. Whoever merges can still edit the message.

   | Squash merge option | What lands in history | Fits when | Watch out | `squash_merge_commit_title` | `squash_merge_commit_message` |
   | :-- | :-- | :-- | :-- | :-- | :-- |
   | Default message | One commit: its own title and message. Several: the PR title and the list of commit messages | Commits are already clean | Work-in-progress commits ("fix typo") land in history | `COMMIT_OR_PR_TITLE` | `COMMIT_MESSAGES` |
   | Pull request title | The PR title only | Short history, the PR keeps the details | The why lives only on GitHub | `PR_TITLE` | `BLANK` |
   | Pull request title and commit details | The PR title and the list of commit messages | Each commit message explains its part | Same as the default when commits are messy | `PR_TITLE` | `COMMIT_MESSAGES` |
   | Pull request title and description | The PR title and the whole PR description | The description is short prose | The whole filled template lands in history: headings, checklists, HTML comments and empty sections. Keep the template short, or edit the message at merge time | `PR_TITLE` | `PR_BODY` |

   | Merge commit option | What lands in history | `merge_commit_title` | `merge_commit_message` |
   | :-- | :-- | :-- | :-- |
   | Default message | `Merge pull request #123 from <branch>`, then the PR title | `MERGE_MESSAGE` | `PR_TITLE` |
   | Pull request title | The PR title only | `PR_TITLE` | `BLANK` |
   | Pull request title and description | The PR title and the whole PR description | `PR_TITLE` | `PR_BODY` |

   These are the three options GitHub's settings page offers. Send only these pairs.
4. **Apply the approved choice.** Send each title with its message, because GitHub requires the title whenever the message is set:

   ```bash
   gh api --method PATCH repos/<owner>/<repo> \
     -f squash_merge_commit_title=<title value> -f squash_merge_commit_message=<message value>
   ```

   Change the merge commit pair the same way, only when the repository allows merge commits.
5. **Propose turning off the merge methods the repository does not use** (`allow_merge_commit`, `allow_rebase_merge`, `allow_squash_merge`, each `-F <key>=false`), as a separate approval. Keep on at least one method that every `allowed_merge_methods` from step 1 lists, and squash or rebase merging when linear history is required: GitHub blocks a merge when the repository disabled the method a rule requires.
6. **Read the settings again** and confirm they show the approved values.
