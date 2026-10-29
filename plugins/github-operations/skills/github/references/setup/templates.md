# Set up a repository's templates, labels and settings

Contents: Before any install · 1. PR templates · 2. Issue forms · 3. Discussion forms · 4. Labels · 5. Merge message setting · 6. Dependabot · 7. CODEOWNERS · 8. Land the setup

Install what a repository lacks, from `<skill-dir>/assets/`. The repository's own files win: never overwrite one.

## Before any install

1. Confirm a git repository (`git rev-parse --show-toplevel`) and read the owner and name from `git remote get-url origin`.
2. Read the visibility: `gh repo view --json isPrivate,visibility,hasDiscussionsEnabled,defaultBranchRef`.
3. Create one branch off the default branch for the whole setup, such as `chore/repository-templates`. Never work on the default branch.
4. For each kind below, look for the repository's own files first. If any exist, stop for that kind: show the user a diff and ask.
5. Replace every `<OWNER>/<REPO>` in each copied file with the real value.

## 1. PR templates

1. Copy the four templates to `.github/PULL_REQUEST_TEMPLATE/`.
2. Copy `standard.md` to `.github/pull_request_template.md` too: that is the default GitHub opens, and a folder alone shows no chooser.
3. Find the repository's real checks in its `CLAUDE.md`, `package.json` scripts, `Makefile` or CI files, and replace each `Project checks:` hint comment with the exact commands.
4. When a template changes later, change `standard.md` and the default copy together.
5. After the merge, open `https://github.com/<owner>/<repo>/compare` on a test branch, and again with `?template=bug-fix.md`, and confirm each template loads.

## 2. Issue forms

1. Choose the set. Ask the user when it is unclear who files issues.

| Form | Public set (outside users) | Internal set (one team) |
| :-- | :-: | :-: |
| `bug_report.yml` | yes | yes |
| `feature_request.yml` | yes | yes |
| `docs_issue.yml` | yes | yes |
| `idea.yml` | yes | no |
| `question.yml` | yes | no |
| `maintenance.yml` | no | yes |
| `incident.yml` | no | yes |
| `config.yml` | yes | yes |

2. Copy the chosen forms and `config.yml` to `.github/ISSUE_TEMPLATE/`.
3. In `config.yml`, delete the commented third-party link or fill it in, and keep `blank_issues_enabled: false`.
4. Check the forms, fix every finding and check again until both pass:
   - `<skill-dir>/scripts/check-forms.py --kind issue .github/ISSUE_TEMPLATE/<form>.yml ...` on every form but `config.yml`;
   - `<skill-dir>/scripts/check-forms.py --kind issue-config .github/ISSUE_TEMPLATE/config.yml`.
5. Check by reading what the script cannot: `name` is unique across the forms, input labels are unique and not near-identical, and no label holds a blocked word such as "Password".
6. Check that every label in a form's `labels:` exists (section 4): GitHub skips a missing label without warning.
7. After the merge, confirm GitHub read `config.yml` with `gh api graphql -f query='query { repository(owner:"<owner>", name:"<repo>") { contactLinks { name url } } }'`, and ask the user to open `https://github.com/<owner>/<repo>/issues/new/choose` signed in.

## 3. Discussion forms

1. Discussions must be on. When they are off, tell the user: enabling them is a repository setting and needs approval.
2. List the categories and slugs with MCP `list_discussion_categories`.
3. Copy only the forms whose category exists to `.github/DISCUSSION_TEMPLATE/`. The file name must equal the category slug: rename a copy when the repository uses another slug.
4. `rfc.yml` needs an `rfc` category, created by hand in **Settings → Discussions**.
5. Check them with `<skill-dir>/scripts/check-forms.py --kind discussion .github/DISCUSSION_TEMPLATE/*.yml`; fix every finding and run it again until it passes.
6. After the merge, ask the user to open `https://github.com/<owner>/<repo>/discussions/new/choose` signed in.

## 4. Labels

The forms and templates apply labels that must exist. The repository's labels win; `labels.json` seeds only a repository that has none for a group.

1. Run `<skill-dir>/scripts/labels-diff.py --repo <owner>/<repo> --labels <skill-dir>/assets/labels.json`. It prints the labels `missing`, `extra` and `different` as JSON.
2. Show the user the missing labels and the differences. Creating or changing a label changes the repository: ask first.
3. After approval, create each missing label with `gh label create "<name>" --color <hex> --description "<text>"`. Leave `extra` and `different` labels as they are unless the user asks.
4. When the repository already has a label-sync file, update that file instead.
5. Run the diff again and confirm nothing approved is still missing.

## 5. Merge message setting

A repository setting affects everyone: read the current values, show the change, and apply it only after approval.

1. Read: `gh api repos/<owner>/<repo> --jq '{squash_merge_commit_title, squash_merge_commit_message, merge_commit_title, merge_commit_message, allow_squash_merge, allow_merge_commit, allow_rebase_merge}'`.
2. Propose "Pull request title and description" as the default message:

   ```bash
   gh api -X PATCH repos/<owner>/<repo> \
     -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=PR_BODY \
     -f merge_commit_title=PR_TITLE -f merge_commit_message=PR_BODY
   ```

3. Propose turning off the merge methods the repository does not use.
4. Read the values back after the change.

## 6. Dependabot

1. When `.github/dependabot.yml` is missing, copy `<skill-dir>/assets/dependabot.yml`; it covers GitHub Actions.
2. Detect the repository's other package ecosystems from its manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod` and the like) and add one entry each, with the same schedule and labels.
3. Validate it with `uvx check-jsonschema --builtin-schema vendor.dependabot .github/dependabot.yml`.

## 7. CODEOWNERS

When `.github/CODEOWNERS` is missing and the user wants one, write one line naming the repository owner: `* @<owner>`.

## 8. Land the setup

1. Commit with the repository's signing setup; use the `maintenance` PR template.
2. Ask the user before you push or open the PR, then continue at `pr/start.md`.
3. Tell the user the templates and forms apply only after the PR merges into the default branch.
