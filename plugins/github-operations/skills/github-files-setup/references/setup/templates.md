# Set up a repository's templates, labels and settings

Contents: How the assets are used · Before any file · 1. PR templates · 2. Issue forms · 3. Discussion forms · 4. Labels · 5. Merge message setting · 6. Dependabot · 7. CODEOWNERS · 8. Land the setup

Create the GitHub files a repository lacks, written for that repository. The repository's own files win: never overwrite one.

## How the assets are used

`<skill-dir>/assets/` holds reference models, not files to copy as they are. For each kind of file:

1. Read the models of that kind.
2. Choose the ones that fit the repository: who contributes, what it ships, how it is tested and released.
3. Write the repository's own files from them: keep each model's structure and required fields, and replace every generic part with the repository's facts, such as its components, versions, environments, commands and labels.
4. Drop what does not apply, and add what the repository needs that no model covers.

## Before any file

1. Confirm a git repository (`git rev-parse --show-toplevel`) and read the owner and name from `git remote get-url origin`.
2. Read the visibility: `gh repo view --json isPrivate,visibility,hasDiscussionsEnabled,defaultBranchRef`.
3. Learn the repository: its `README`, `CONTRIBUTING`, `CLAUDE.md` or `AGENTS.md`, its manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod` and the like), its CI files, its release process, its existing labels and its recent issues and pull requests.
4. Create one branch off the default branch for the whole setup, such as `chore/repository-templates`. Never work on the default branch.
5. For each kind below, look for the repository's own files first. If any exist, stop for that kind: show the user what you would change as a diff, and ask.
6. Show the user the set of files you chose for each kind, and why, before you write them.

## 1. PR templates

1. Choose from the four models (`standard`, `bug-fix`, `hotfix`, `maintenance`) the ones the repository's kinds of change need. A small repository may need only `standard`.
2. Write each chosen template to `.github/PULL_REQUEST_TEMPLATE/`, with the repository's real checks in place of every `Project checks:` hint: the exact commands from its `CLAUDE.md`, `package.json` scripts, `Makefile` or CI files.
3. Write the default template to `.github/pull_request_template.md` too: that is the one GitHub opens, and a folder alone shows no chooser.
4. When a template changes later, change the default copy with it.
5. After the merge, open `https://github.com/<owner>/<repo>/compare` on a test branch, and again with `?template=<file>.md`, and confirm each template loads.

## 2. Issue forms

1. Choose the forms from who files issues and what they report. Ask the user when it is unclear who files issues.

| Model | Public repository (outside users) | Internal repository (one team) |
| :-- | :-: | :-: |
| `bug_report.yml` | yes | yes |
| `feature_request.yml` | yes | yes |
| `docs_issue.yml` | when it has user docs | when it has docs |
| `idea.yml` | yes | no |
| `question.yml` | when Discussions are off | no |
| `maintenance.yml` | no | yes |
| `incident.yml` | no | when it runs in production |
| `config.yml` | yes | yes |

2. Write the chosen forms to `.github/ISSUE_TEMPLATE/`, adapted to the repository: its components and versions as dropdown options, its environments, the logs it produces, and its own labels.
3. In `config.yml`, keep `blank_issues_enabled: false`, and add contact links only to places the repository really uses, such as its Discussions, docs or security policy.
4. Check the forms, fix every finding and check again until both pass:
   - `<skill-dir>/scripts/check-forms.py --kind issue .github/ISSUE_TEMPLATE/<form>.yml ...` on every form but `config.yml`;
   - `<skill-dir>/scripts/check-forms.py --kind issue-config .github/ISSUE_TEMPLATE/config.yml`.
5. Check by reading what the script cannot: `name` is unique across the forms, input labels are unique and not near-identical, and no label holds a blocked word such as "Password".
6. Check that every label in a form's `labels:` exists (section 4): GitHub skips a missing label without warning.
7. After the merge, confirm GitHub read `config.yml` with `gh api graphql -f query='query { repository(owner:"<owner>", name:"<repo>") { contactLinks { name url } } }'`, and ask the user to open `https://github.com/<owner>/<repo>/issues/new/choose` signed in.

Limits of issue forms:

- Forms are read from the default branch only.
- `required: true` is enforced only in public repositories.
- The GraphQL field `issueTemplates` does not list YAML forms: never use it to verify forms.
- `isBlankIssuesEnabled` describes the viewer: an admin sees `true` even when `config.yml` disables blank issues.
- A form's `type:` key needs issue types defined at organization level.

## 3. Discussion forms

1. Discussions must be on. When they are off, tell the user: enabling them is a repository setting and needs approval.
2. List the categories and slugs with MCP `list_discussion_categories`.
3. Choose a model for each category the repository uses:

| Category use | Model |
| :-- | :-- |
| Ideas still open, not ready to track | `ideas.yml` |
| "How do I…?" questions with no defect | `q-a.yml` |
| Sharing a setup or a result | `show-and-tell.yml` |
| Hard-to-reverse decisions to debate | `rfc.yml` |

4. Write each chosen form to `.github/DISCUSSION_TEMPLATE/`, adapted to the repository. The file name must equal the category slug.
5. Check them with `<skill-dir>/scripts/check-forms.py --kind discussion .github/DISCUSSION_TEMPLATE/*.yml`; fix every finding and run it again until it passes.
6. After the merge, ask the user to open `https://github.com/<owner>/<repo>/discussions/new/choose` signed in.

Limits of discussion forms:

- Forms are read from the default branch only, and `required: true` is enforced only in public repositories.
- Discussion forms have no polls.
- No mutation creates a category: a form whose category does not exist, such as `rfc`, needs the user to create it in **Settings → Discussions** first.

## 4. Labels

The forms and templates apply labels that must exist. The repository's labels win; `labels.json` is the model for a group of labels the repository lacks.

1. Run `<skill-dir>/scripts/labels-diff.py --repo <owner>/<repo> --labels <skill-dir>/assets/labels.json`. It prints the labels `missing`, `extra` and `different` as JSON.
2. From the missing labels, keep only the ones the forms and templates you wrote apply, and the groups the repository needs. Name them in the repository's existing style.
3. Show the user the labels to create. Creating or changing a label changes the repository: ask first.
4. After approval, create each one with `gh label create "<name>" --color <hex> --description "<text>"`. Leave existing labels as they are unless the user asks.
5. When the repository already has a label-sync file, update that file instead.
6. Read the labels again and confirm nothing approved is still missing.

## 5. Merge message setting

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

## 6. Dependabot

1. When `.github/dependabot.yml` is missing, write one from `<skill-dir>/assets/dependabot.yml`: keep its GitHub Actions entry when the repository has workflows.
2. Detect the repository's package ecosystems from its manifests and add one entry each, with the directory where each manifest lives, a schedule that fits the repository, and its own labels.
3. Validate it with `uvx check-jsonschema --builtin-schema vendor.dependabot .github/dependabot.yml`.

## 7. CODEOWNERS

When `.github/CODEOWNERS` is missing and the user wants one, write it from the repository's real owners: one line naming the owner (`* @<owner>`), plus a line per area when the user names its maintainers.

## 8. Land the setup

1. Commit with the repository's signing setup.
2. Ask the user before you push. Open the pull request with the `github-operations:auto-pr-lifecycle` skill, using the repository's new maintenance template when it has one.
3. Tell the user the templates and forms apply only after the PR merges into the default branch.
