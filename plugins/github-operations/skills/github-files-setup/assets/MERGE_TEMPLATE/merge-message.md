# Merge message options

GitHub has no repository file for merge or squash commit messages. The default comes from a repository setting
(**Settings → General → Pull Requests**), where you pick one built-in format per merge method. Show the user these
trade-offs, so the default matches how the repository writes its history. Whoever merges can still edit the message.

| Option (squash merge) | What lands in history | Fits when | Watch out |
| :-- | :-- | :-- | :-- |
| Default message | One commit: its own title and message. Several: the PR title and the list of commit messages | Commits are already clean | Work-in-progress commits ("fix typo") land in history |
| Pull request title | The PR title only | Short history, the PR keeps the details | The why lives only on GitHub |
| Pull request title and commit details | The PR title and the list of commit messages | Each commit message explains its part | Same as the default when commits are messy |
| Pull request title and description | The PR title and the whole PR description | The description is short prose | The whole filled template lands in history: headings, checklists, HTML comments and empty sections. Keep the template short, or edit the message at merge time |

For merge commits the choices are the classic `Merge pull request #N from <branch>` title or the PR title, with
the PR title, the PR description or nothing as the message.

Whatever the default, the PR title becomes the commit title: it follows the repository's own convention, read from
its recent commit titles (Conventional Commits such as `fix(scope): summary`, or plain imperative sentences).
