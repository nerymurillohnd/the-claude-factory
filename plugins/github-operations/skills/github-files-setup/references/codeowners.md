# CODEOWNERS

A CODEOWNERS file names who is asked to review changes to each path. GitHub reads `CODEOWNERS` from `.github/`, the root or `docs/`, in that order, and uses the first it finds; each pull request uses the file on its base branch.

1. **Find the owners.** Ask the user who owns the repository and each area; never guess them from the commit history.
   - In a repository owned by an organization, name teams (`@<org>/<team>`) or named users; the organization itself (`@<org>`) is not a valid owner.
   - In a personal repository, name the owner (`@<user>`) and any collaborators the user names.
   - Every owner needs explicit write access to the repository, and a team must be visible. When the user cannot confirm it, read each proposed user's permission with `gh api repos/<owner>/<repo>/collaborators/<user>/permission --jq '{permission, role_name}'`, which counts every grant, teams and organization included: a `permission` of `write` or `admin` can own (GitHub reports the maintain role as `write`). For a team, read its permissions with `gh api -H 'Accept: application/vnd.github.v3.repository+json' orgs/<org>/teams/<team>/repos/<owner>/<repo> --jq .permissions`: without that header the call only answers whether the team has any access. `push`, `maintain` or `admin` set to `true` can own; otherwise ask the user. An owner without write access is silently skipped.
2. **Write the rules.** One line per path pattern, then its owners on the same line, separated by spaces:

   ```text
   # Default owners of everything not matched below.
   *                    @<org>/<maintainers-team>

   # Areas, from general to specific: the last matching line wins.
   /docs/               @<org>/<docs-team>
   /src/payments/       @<org>/<payments-team> @<user>

   # Protect this file itself.
   /.github/CODEOWNERS  @<org>/<maintainers-team>
   ```

   - Patterns follow `.gitignore` rules, except that `!` negation, `[ ]` ranges and `\#` escapes don't work. Paths are case sensitive.
   - The last matching line wins, so write general patterns first and specific ones after.
   - A pattern with no owner leaves that path without owners.
   - Keep the file under 3 MB; a larger file is not loaded.
3. **Warn about review rules.** When the base branch requires review from code owners (a branch protection rule or a ruleset), a pull request needs approval from one owner of each changed path, and code owners are not asked to review a draft until it is ready. A single owner on `*` can then block a solo maintainer's own pull requests: say so before the user turns that rule on.
4. **Check it after the merge.** GitHub skips each invalid line. Read the errors with `gh api "repos/<owner>/<repo>/codeowners/errors?ref=<default branch>"`, which must return an empty `errors` list, or ask the user to open the file on GitHub, which highlights them.
