---
status: accepted
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Title pull requests with conventional commits and merge them only by squash

## Scope

Pull request titles, the PR templates in `.github/pull_request_template.md` and `.github/PULL_REQUEST_TEMPLATE/`, and the repository's merge settings on GitHub. Maintainer scope.

## Context and problem statement

`main` used conventional-commit titles, while this redesign wrote plain imperative titles ("Restore …"). The repository allowed merge commits, rebase and squash, and the squash title was `COMMIT_OR_PR_TITLE`, which takes the commit's title when a pull request has one commit. The history therefore had no single title format, and the merge method varied.

## Decision drivers

- One title format in the history, so releases and changelogs can be grouped by type and by plugin.
- One commit on `main` per pull request, titled by the reviewed pull request title.
- A squash body that keeps the branch's commit messages instead of copying the whole PR template.

## Considered options

- **Conventional-commit titles (`type(scope): summary`, with the plugin or area as scope), squash as the only merge method, squash title `PR_TITLE` and squash body `COMMIT_MESSAGES`**: chosen.
- **Plain imperative titles**: rejected because they state neither the type nor the plugin.
- **Squash body `PR_BODY`**: rejected because it copies the whole PR template into the history.
- **Keep merge commits and rebase allowed**: rejected because a rebase or merge commit brings work-in-progress commits and their titles onto `main`.

## Decision outcome

Chosen option: **conventional-commit titles with squash-only merges**, because every commit on `main` then carries a reviewed, typed and scoped title, and the body keeps the branch's own commit messages.

### Consequences

- Good, because each PR template tells the author the title format and that the squash uses it.
- Bad, because a pull request's title must be fixed before the merge when it does not follow the format.
- Bad, because branch commits keep whatever titles they had; only the squash title on `main` follows the format.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| GitHub allows only squash, with title `PR_TITLE` and body `COMMIT_MESSAGES` | `gh api repos/nerymurillohnd/the-claude-factory` (`allow_merge_commit`, `allow_rebase_merge`, `squash_merge_commit_title`, `squash_merge_commit_message`) | Pending: the settings change runs after the files are verified | After the change |
| The PR templates load | Open the compare page with `?template=bug-fix.md` and `?template=maintenance.md` | Pending: templates apply after the merge to `main` | After PR #104 merges |

## More information

- Sources: GitHub REST "Update a repository" (`squash_merge_commit_title` is "Required when using squash_merge_commit_message"; values `PR_TITLE`, `COMMIT_OR_PR_TITLE`, `PR_BODY`, `COMMIT_MESSAGES`, `BLANK`); GitHub docs "Configuring commit squashing for pull requests"; GitHub docs "Creating a pull request template for your repository".
- The owner decided this in this session, on 2026-11-12, after the github-operations github-files-setup evaluation.
