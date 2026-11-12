# GitHub operations: specification for the maintainer skills

> [!NOTE]
> A living specification of the repository's GitHub collaboration setup: what exists, how it is operated, what each environment allows, and the traps already found. It is the source for the future maintainer skills (`.claude/skills/`) that handle issues, vulnerability reports, labels and merges. Decisions live in the ADRs, cited here by ID; this file does not repeat their reasoning.

**Scope:** maintainer scope. It covers this repository's own GitHub files, labels and settings, not what any plugin distributes. The `github-operations` plugin's skills, which set up such files for other repositories, are plugin scope.

**Last updated:** 2026-11-12, at commit `94e03fd` on `claude/repo-refactor-redesign-feqwzk`.

## 1. What exists

### Issue forms and templates

GitHub reads forms, `config.yml` and PR templates from the default branch only: everything below applies once PR #104 merges into `main`.

| File | Purpose | Labels applied | Issue type |
| --- | --- | --- | --- |
| `.github/ISSUE_TEMPLATE/bug_report.yml` | A plugin doesn't install, load or behave as documented | `type: bug`, `status: triage` | `Bug` |
| `.github/ISSUE_TEMPLATE/feature_request.yml` | Improve an existing plugin | `type: enhancement`, `status: triage` | `Feature` |
| `.github/ISSUE_TEMPLATE/plugin_idea.yml` | Propose a new plugin | `type: plugin-idea`, `status: triage` | `Feature` |
| `.github/ISSUE_TEMPLATE/docs_issue.yml` | A README or guide is wrong, unclear or missing | `type: documentation`, `area: docs`, `status: triage` | `Bug` |
| `.github/ISSUE_TEMPLATE/question.yml` | Usage or setup question | `type: question`, `status: triage` | none |
| `.github/ISSUE_TEMPLATE/config.yml` | Blank issues off; links to private vulnerability reporting, Anthropic's Claude Code tracker and the official plugin docs | — | — |
| `.github/VULNERABILITY_REPORT.yml` | The private vulnerability report form (replaces GitHub's default form) | none (advisories carry no labels) | — |

Fields that matter for triage:

- **Bug report:** plugin (dropdown), plugin version, Claude Code version, surfaces, OS (`macOS`, `Linux`, `Windows (Git Bash)`, `Other (not supported)`), what happened, expected, steps, regression (yes / never worked / unknown), last working version, impact (blocks with no workaround / blocks with workaround / annoying), diagnostics, optional upload (`.log,.txt,.json,.png,.jpg,.zip`), checklist.
- **Vulnerability report:** plugin (dropdown), plugin version, Claude Code version, surface (Claude Code, Claude), summary, proof of concept, impact, checklist (no secrets, not disclosed publicly).
- **A dropdown applies no label.** The `plugin: <name>` label is added by hand during triage, from the form's Plugin answer.

### Pull request templates

| File | When | Selected by |
| --- | --- | --- |
| `.github/pull_request_template.md` | Default; a copy of `PULL_REQUEST_TEMPLATE/standard.md` | Opens automatically |
| `.github/PULL_REQUEST_TEMPLATE/standard.md` | Features, refactors, security, tooling, releases | `?template=standard.md` |
| `.github/PULL_REQUEST_TEMPLATE/bug-fix.md` | A fix for a reported bug | `?template=bug-fix.md` on the compare URL |
| `.github/PULL_REQUEST_TEMPLATE/maintenance.md` | Docs, tests, dependencies, CI, chores with no change to what plugins do | `?template=maintenance.md` |

When `standard.md` changes, `pull_request_template.md` changes with it (`cmp` shows them equal).

### Labels

- **Fixed labels:** `.github/labels.json` (22 labels: `type:`, `status:`, `priority:`, `area:` and `accessibility`).
- **Plugin labels:** one `plugin: <name>` per entry of `.claude-plugin/marketplace.json`, color `EDEDED`, description "Issues about the <name> plugin". They are not written in `labels.json`.
- **Not managed:** GitHub's 9 default labels and the 4 retired plugin labels (`agent-context-audit`, `agent-files-diagnostics`, `git-hygiene`, `session-handoff`). The plan is to archive them; until that runs they stay selectable.
- **Lifecycle used in CONTRIBUTING.md:** `status: triage` → `status: needs-info` or `status: confirmed` → `status: in-progress` → `status: released` (with the release linked in the issue); or `status: duplicate`, `status: wontfix`, `status: upstream`.
- **Decision:** ADR_2026-11-12_labels-from-labels-json-and-the-catalog.

### Issue types

The repository has GitHub's default types `Task`, `Bug`, `Feature` (REST `repos/{owner}/{repo}/issue-types`). The forms set them. The `type:` labels stay, because pull requests have no issue type. Decision: ADR_2026-11-12_issue-forms-set-default-issue-types.

### Merge policy

- Pull request titles follow conventional commits: `type(scope): summary`, with scope the plugin name or the area (`marketplace`, `ci`, `docs`, `maintainer`).
- Squash only. The squash title is the PR title (`PR_TITLE`) and the body the branch's commit messages (`COMMIT_MESSAGES`).
- Decision: ADR_2026-11-12_conventional-titles-and-squash-only-merges.
- **Applied on GitHub:** not yet. Today all three methods are allowed and the squash title is `COMMIT_OR_PR_TITLE`.

### Security policy

- `SECURITY.md` sends reports to private vulnerability reporting (enabled; REST `private-vulnerability-reporting` returned `{"enabled":true}` on 2026-11-12).
- Targets in `SECURITY.md`: acknowledgement within 3 business days, assessment and severity within 7 days, fix for confirmed critical or high within about 14 days, then a published security advisory with optional credit.
- Out of scope per `SECURITY.md`: Claude Code, Claude and Anthropic services (to Anthropic's disclosure policy), and third-party services (to their owners).
- `CODEOWNERS`: `* @nerymurillohnd`.

### Dependabot

`.github/dependabot.yml` has entries for `github-actions`, `npm` and `uv`:
- **Cooldown:** 7 days, and 14 for majors where supported.
- **Grouped:** minor and patch updates.
- **Labels:** `area: ci` and `type: dependencies`.
- **Commit messages:** `include: scope`.

The maintainer Python tools are uv tools pinned in `tools:install`, which Dependabot does not read, so they are bumped by hand. Decisions: ADR_2026-11-12_dependabot-cooldown-and-groups and ADR_2026-11-12_maintainer-tools-as-pinned-uv-tools.

## 2. Commands

| Command | What it does | Writes to GitHub |
| --- | --- | --- |
| `npm run tools:install` | Installs ruff, basedpyright, zizmor and check-jsonschema at their pinned versions as uv tools | No |
| `npm run lint:github` | Schema-checks the forms, `VULNERABILITY_REPORT.yml`, `config.yml` and `dependabot.yml` (check-jsonschema 0.39.0 built-in schemas), then runs `scripts/check-github-files.py` | No |
| `npm run labels:sync` | Dry run of `scripts/sync-labels.py`: prints a JSON plan (`create`, `update`, `in_sync`, `not_managed`); exit 1 when changes are pending | No |
| `npm run labels:sync -- --apply` | Creates and updates labels; never deletes, renames or archives | Yes |
| `npm run check` | Maintainer lint, type checks and `claude plugin validate --strict` for every plugin and the marketplace | No |

`scripts/check-github-files.py` exits 1 when:
- a plugin dropdown does not list exactly the catalog's plugins in catalog order (the question form may add `None (marketplace question)`);
- a form or Dependabot names a label the repository does not define.

It exits 2 on unreadable input.

## 3. Procedures (the future skills' workflows)

### Add, rename or retire a plugin

1. Change `.claude-plugin/marketplace.json`.
2. Update the `plugin` dropdown in `bug_report.yml`, `feature_request.yml`, `question.yml` and `VULNERABILITY_REPORT.yml`, in catalog order.
3. `npm run lint:github` must pass.
4. `npm run labels:sync`, then `-- --apply` to create the new `plugin:` label.
5. A retired plugin's label is archived, not deleted.

### Triage a new issue

1. Read the form answers.
2. Add `plugin: <name>` from the Plugin answer.
3. Check the issue type the form set.
4. Reproduce, or ask for details with `status: needs-info`.
5. Confirmed: `status: confirmed` and a `priority:` label. The bug form's impact answer maps to priority: blocks with no workaround → `priority: high`; blocks with a workaround → `priority: medium`; annoying → `priority: low`. The owner confirms the priority.
6. A Claude Code bug goes to `status: upstream`, with a pointer to Anthropic's tracker.
7. Once the fix ships: `status: released`, and link the release in the issue.

The owner's rule (CLAUDE.md, Ownership and contributions): users only report; triage, fixes and releases are the owner's and Claude's work.

### Handle a private vulnerability report

1. Acknowledge within 3 business days, in the advisory's thread.
2. Assess severity within 7 days. Reproduce in an isolated environment from the plugin version reported.
3. Fix in a private fork of the advisory, or in a normal PR only after publication, since the advisory's private fork keeps the fix hidden. Not yet verified for this repository.
4. Release the fixed plugin version, publish the advisory, and credit the reporter if they wish.

Open: whether to request a CVE through GitHub, and the CWE requirement option of the report form. Neither is decided yet.

### Prepare a merge

1. Title in conventional commits.
2. The PR template's checks pass locally, with their output in the PR.
3. Labels applied.
4. Every review comment resolved.
5. Squash.

PR rules (CLAUDE.md, Pull requests): a change to a plugin's components needs a PR; changes outside `plugins/` do not, unless the owner asks.

## 4. Environments

| Environment | GitHub access | Notes |
| --- | --- | --- |
| Claude Code cloud session | `gh api` REST on `repos/<owner>/<repo>/...`; the GitHub MCP server | **GraphQL is blocked:** `gh label list`, `gh pr checks` and `gh repo view --json` fail with HTTP 403. **Paths outside the repository are blocked:** `users/...`, `user/...`, `repositories/<id>/...`. The auto-mode classifier refused a label write once; writes need the owner's explicit approval in the conversation. Bare `python3` is 3.13.18; the maintainer scripts use `.venv/bin/python` (3.15.2). |
| Owner's terminal | Full `gh` | Python is managed by uv and is on PATH. The tools run bare after `npm run tools:install`. |
| CI | Not configured | `.github/workflows/` holds only `release.yml`, whose `workflow_run` trigger names the deleted `Validate` workflow, so it runs only through `workflow_dispatch`. A maintainer workflow would run `npm ci`, `uv sync --locked` and `npm run tools:install`, then the npm checks. |

## 5. Traps already found

| Trap | Evidence | Handling |
| --- | --- | --- |
| `gh` fills `{owner}/{repo}` only in `gh api` paths, not in `--repo` | `gh label create --repo {owner}/{repo}` went to `repos/%7Bowner%7D/%7Brepo%7D` and got HTTP 403 | `sync-labels.py` resolves OWNER/NAME first (commit `94e03fd`) |
| GitHub skips a label a form names when the label does not exist, without a warning | GitHub docs, "Syntax for issue forms" | `check-github-files.py` rule (b) |
| A dropdown answer applies no label | GitHub form schema docs list no label key for dropdowns | Triage adds `plugin:` by hand |
| check-jsonschema 0.39.0 rejects `min_length` in `VULNERABILITY_REPORT.yml`, which GitHub documents | `Additional properties are not allowed ('min_length' was unexpected)` | `min_length` was dropped; revisit when the vendored schema adds it |
| If GitHub cannot parse a custom vulnerability form, it shows its default form silently | GitHub docs, "Configuring private vulnerability reporting for a repository" | Keep `lint:github` passing |
| `blank_issues_enabled: false` still shows "Blank issue (Maintainers only)" to users with write access | GitHub docs, "Configuring issue templates" | Expected; no action |
| Label archiving on personal-account repositories is not documented | GitHub REST labels docs and the 2026-08-27 changelog mention no account type | Probe one label before archiving the rest |
| Issue types exist only on issues, not on pull requests | ADR_2026-11-12_issue-forms-set-default-issue-types | Keep the `type:` labels |
| Biome reads `pyrightconfig.json` as strict JSON | Parse errors on comments in `scripts/pyrightconfig.json` | No comments in that file |

## 6. Candidate skills

These are proposals for the owner. None exists yet.

| Skill | Triggers | Does | Needs |
| --- | --- | --- | --- |
| `issue-triage` | A new or updated issue; "triage", "label this issue" | Reads the form answers, applies `plugin:` and the status, priority and area labels, checks the type, asks for missing details, links upstream bugs | REST or MCP issue write; label taxonomy (section 1); triage procedure (section 3) |
| `security-advisory-handling` | A private vulnerability report; "security report", "advisory" | Follows the `SECURITY.md` timeline, assesses severity, plans the fix and the advisory, drafts the acknowledgement for the owner to send | Advisory access (to verify in a cloud session); `SECURITY.md` targets |
| `github-files-maintenance` | A plugin added, renamed or retired; a form, label or template change | Runs the plugin-catalog procedure, `lint:github`, `labels:sync`, and keeps the default PR template equal to `standard.md` | npm scripts (section 2) |
| `merge-readiness` | "Is #N ready", "prepare the merge" | Checks the title format, the template's checks and output, labels and resolved threads; never merges without the owner | Merge policy (section 1) |

Each skill sends any outward action (a message to a reporter, a label write, a merge) to the owner first, as the owner's standing rules require.

## 7. Open items

| Item | State |
| --- | --- |
| Sync labels (`area: docs`), archive the 9 defaults and 4 retired labels, set `Bug` on issues #87 and #88, apply the merge settings | Proposed to the owner on 2026-11-12; not run |
| Change PR #104's title to conventional commits before the squash | Proposed: `refactor(maintainer): redesign the maintainer tooling and GitHub files` |
| Maintainer CI workflow, and `release.yml`'s orphaned trigger | Open |
| Confirm Dependabot's real title with `include: scope` (expected `chore(deps): …`) | Pending the first Dependabot PR |
| Confirm each PR template loads through `?template=` | After the merge to `main` |
