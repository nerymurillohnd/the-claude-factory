# Audit: `github-operations:github-files-setup` against GitHub's documentation

- **Date:** 2026-11-10
- **Scope:** `plugins/github-operations/skills/github-files-setup/`: `SKILL.md`, its 6 references, its 21 assets and 2 scripts, and the setup lines of `plugins/github-operations/README.md`.
- **Sources:**
  - `github/docs` at `f309096`. Pages missing from that checkout were fetched raw from `github/docs` `main` on 2026-11-10.
  - `github/rest-api-description` (REST OpenAPI) and the GitHub GraphQL schema.
  - `check-jsonschema` 0.39.0.
- **Method:** a read-only subagent wrote the report. Claude spot-checked four findings on disk: the `idea.yml` link, the CODEOWNERS line, `dependabot.md` naming only `.yml`, and the missing SECURITY.md.
- **Status:** open. To address after the maintainer refactor.

## Contents

- 1. Factual errors or outdated statements
- 2. Gaps
- 3. Weaknesses in procedure
- 4. Internal inconsistencies
- Prioritized list
- Unverified

## 1. Factual errors or outdated statements

| Item | Skill evidence | Official source | Sev | Change |
| :-- | :-- | :-- | :-- | :-- |
| `* @<owner>` CODEOWNERS line is invalid when the owner is an organization | SKILL.md:119 | about-code-owners.md:64 ("`@username` or `@org/team-name` … must have explicit `write` access"); :79 (an invalid line is skipped); :81 (no owner is assigned when the user or team doesn't exist or lacks access) | High | For an org-owned repo (`gh repo view --json isInOrganization`), require an `@org/team` or named users with write access. Validate with `gh api "repos/<o>/<r>/codeowners/errors?ref=<branch>"` |
| The PR "chooser" gotcha is misleading: there is never a chooser, only the `?template=` query | SKILL.md:75; pr-templates.md:5 | creating-a-pull-request-template:18; using-query-parameters-to-create-a-pull-request (`template`) | Medium | Say so; publish `compare/<base>...<head>?quick_pull=1&template=<file>.md` links |
| The PR-template verification URL is incomplete | pr-templates.md:7 | the same query-parameter page; invalid parameters return 404 | Low | Use `compare/<default>...<branch>?quick_pull=1&template=<file>.md` |
| PR template lookup ignores case, `.txt`, and the fact that a `.github/` copy shadows the root or `docs/` copy | SKILL.md:47, :51 | about-issue-and-pull-request-templates:144; creating-a-default-community-health-file:27-31 | Medium | Search case-insensitively; move an existing copy instead of adding a second one |
| The Dependabot step ignores `.github/dependabot.yaml` | dependabot.md:3,5 (contradicts SKILL.md:56) | about-the-dependabot-yml-file ("`.yml` or `.yaml`") | Medium | Check both names |
| `check-forms.py` rejects the documented `min_length` key (tested) | issue-forms.md:58-61; check-forms.py:55-59 | syntax-for-githubs-form-schema:135,179 (`min_length`) | Medium | Allow this known schema false positive, or document it |
| The "None" rule is broader than the docs, and `n/a` is missed | check-forms.py:61,178 | syntax-for-githubs-form-schema:210 (with `default`, no "None" or "n/a" option) | Low | Flag both, case-insensitively, when `default` is set |
| The merge asset calls the REST merge endpoint "unverified" | MERGE_TEMPLATE/merge-message.md:53-54 | REST `PUT /repos/{o}/{r}/pulls/{n}/merge` (`commit_title`, `commit_message`, `sha`, `merge_method`) | Low | State it as fact |
| Signing section: incomplete and partly unsupported | merge-message.md:50-52 | reusable rebase_and_merge_verification ("added … without commit signature verification") | Low | Add that rebase-merge commits are unsigned; present required signatures as the repository's own policy, not a GitHub rule |

Verified correct, keep:

- Forms are read from the default branch.
- `required` is enforced only in public repositories.
- A missing label is skipped.
- A discussion form's file name equals the category slug.
- There is no `createDiscussionCategory` mutation.
- The `isBlankIssuesEnabled` semantics.
- `type` needs organization issue types.
- CODEOWNERS lookup order: `.github/`, root, `docs/`.
- The squash and merge commit message enums.

## 2. Gaps

| Item | Official source | Sev | Change |
| :-- | :-- | :-- | :-- |
| Account-level `<owner>/.github` defaults, and the rule that a local form drops every inherited one | creating-a-default-community-health-file:21,35,73 | High | In step 1, read `gh api repos/<owner>/.github/contents/.github`; warn before writing any form; offer to target the `.github` repository itself |
| SECURITY.md is never written, yet config.yml and bug_report.yml route security reports to it | add-security-policy ("supported versions … how to report") | High | Add a model and a step |
| Private vulnerability reporting: assets link `/security/advisories/new` without checking that it is enabled | report-privately ("only … where this feature is enabled"); REST `GET/PUT /repos/{o}/{r}/private-vulnerability-reporting` | High | Check it first; propose enabling it as an approved setting change; for private or internal repos, link SECURITY.md or a real contact |
| `.github/VULNERABILITY_REPORT.yml` / `.yaml` | configure-for-a-repository (issue-form syntax; a broken form falls back to the default without notice) | Medium | Optional model, validated as an issue form |
| SUPPORT.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, although the description promises "ready for contributors" | adding-support-resources; setting-guidelines; adding-a-code-of-conduct | Medium | Write them, or narrow the description and list them under "Left for you" |
| LICENSE | creating-a-default-community-health-file:80 (no default license); adding-a-license | Low | Detect and report; never choose a license |
| FUNDING.yml, ACCESSIBILITY.md | displaying-a-sponsor-button; adding-an-accessibility-page | Low | Optional |
| Community Standards check | about-community-profiles; REST `GET /repos/{o}/{r}/community/profile` | Medium | Read it after the merge (public repos) |
| Issue form features: `type`, `projects`, `assignees`, `upload`, `min_length`, dropdown `default`/`multiple`, `id` rules, URL prefill | syntax-for-issue-forms:152-156; form schema `id`; creating-an-issue (query prefill) | Medium | Check `gh api orgs/<org>/issue-types` and prefer `type:` over a type label; warn that renaming an `id` breaks prefill links |
| `name` must be over 3 characters; chooser order is alphanumeric, YAML before Markdown | configuring-issue-templates:57,101-105 | Low | Add both rules, with optional numeric prefixes |
| `blank_issues_enabled: false` still shows **Blank issue** to users with write access, as **Maintainers only** | configuring-issue-templates:72 | Low | Say so, so the owner's own check is not misread |
| Labels: GitHub's default set, `good first issue` and `help wanted`, the 100-character description limit, color without `#` | managing-labels; REST labels | Medium | Map onto the default labels instead of duplicating them; check lengths |
| Dependabot beyond version entries: security updates and alerts state, `groups`, `cooldown`, `multi-ecosystem-groups`, `open-pull-requests-limit`, `registries`, intervals | about-the-dependabot-yml-file; Dependabot options reference | Medium | Read the alerts state; offer groups and cooldown; ask before private registries, which need secrets; route reviewers through CODEOWNERS |
| CODEOWNERS rules: last match wins, case-sensitive paths, unsupported `!`/`[ ]`/`\#`, the 3 MB limit, self-protection, not requested on drafts | about-code-owners:22,52,58-62,77,95-98,168 | Medium | Write a reference; warn that a single-owner `*` line plus "Require review from Code Owners" can block a solo maintainer |
| Rulesets and branch protection | reusable rulesets-alternative | Low | Name as out of scope, or under "Left for you" |
| Discussion forms as account-wide defaults | creating-a-default-community-health-file:69,93 | Low | Mention it |

## 3. Weaknesses in procedure

| Item | Evidence | Sev | Change |
| :-- | :-- | :-- | :-- |
| The labels Dependabot and the PR templates apply are never created, because labels run at step 6 and Dependabot at step 8; Dependabot silently ignores a missing label | SKILL.md:100-102; labels.md:2; assets/dependabot.yml:9-11; hotfix.md:34 | Medium | Collect labels from every file written, then create them |
| Unreplaced `<OWNER>/<REPO>` placeholders and hard-coded `tree/main/docs` paths pass validation (tested) | config.yml:6,9; bug_report.yml:18; feature_request.yml:13; idea.yml:13; question.yml:12; docs_issue.yml:14 | Medium | A check-forms rule for `<[A-Z_]+>`; check every repository link against the default branch and real paths |
| Contact and form links point to features that may be off (Discussions, private vulnerability reporting) | config.yml:9; question.yml; bug_report.yml:18 | Medium | Gate each link on the real state: `gh repo view --json contactLinks,isSecurityPolicyEnabled,securityPolicyUrl,hasIssuesEnabled,viewerPermission` |
| `labels-diff.py` after creation fails whenever only some labels were approved | SKILL.md:87 | Low | Diff against the approved list |
| No permission check before setting changes | merge-message-setting.md:5-14; labels.md:4-5 | Low | Read `viewerPermission` in step 1 |
| A `PR_BODY` merge message copies the whole filled template into history | merge-message-setting.md:6-11 vs merge-message.md:34-35 | Medium | Make the trade-off explicit; offer `COMMIT_MESSAGES` or `BLANK` |
| Validation errors GitHub reports that could be scripted: unique labels, near-identical labels, forbidden words | issue-forms.md:62 | Low | Add them to check-forms.py |
| No check after the merge for CODEOWNERS, Dependabot or the community profile | SKILL.md:137 | Low | Add all three to the closing report |

## 4. Internal inconsistencies

| Item | Evidence | Sev | Fix |
| :-- | :-- | :-- | :-- |
| Broken cross-link (verified) | assets/ISSUE_TEMPLATE/idea.yml:13 links `feature-request.yml`; the file is `feature_request.yml` | Medium | Correct the name |
| `feature_request.yml` always links `idea.yml`, which internal repositories do not get | feature_request.yml:13 vs issue-forms.md:21 | Medium | Make the link conditional |
| config.yml is recommended for internal repos, but its models assume a public repo with private vulnerability reporting and Discussions | issue-forms.md:25 vs config.yml:5-10 | Medium | See section 2 |
| Squash-only convention vs both merge settings | merge-message.md:10 vs merge-message-setting.md:9-11 | Low | Align them |
| `.yaml` listed in SKILL.md but ignored in dependabot.md (verified) | SKILL.md:56 vs dependabot.md:3,5 | Medium | See section 1 |
| The Contents entry names a heading that doesn't exist | SKILL.md:18 vs :89 | Low | Rename one of them |
| The README omits the third `uv` run (the Dependabot schema check) | README.md:534-535 | Low | Mention it |

## Prioritized list

1. SECURITY.md, plus a check and enable step for private vulnerability reporting before any advisories link; no such link in private repositories.
2. A correct, validated CODEOWNERS: team or user owners, a write-access check, the errors API, self-protection.
3. Detection of the account's `.github` repository, with the warning about losing inherited forms.
4. Label creation that covers `dependabot.yml` and the PR templates (fix the step order).
5. check-forms fixes: the `min_length` false positive, placeholders, duplicate and similar labels, forbidden words, `None`/`n/a` with `default`.
6. The `idea.yml` link and the conditional feature→idea link.
7. Dependabot: security updates and alerts state, groups, cooldown, `.yaml`.
8. CONTRIBUTING, SUPPORT, CODE_OF_CONDUCT, VULNERABILITY_REPORT.yml, FUNDING, ACCESSIBILITY and LICENSE: written, or reported under "Left for you".
9. PR templates: the `?template=` access model with no chooser, case-insensitive lookup, precedence.
10. Issue types, `projects`, prefill-stable `id`s, `name` length and chooser order.
11. The merge-message trade-off, and a community profile check after the merge.

## Unverified

- That issues and discussions created through the API or `gh` skip the forms (SKILL.md:78, issue-forms.md:74): no doc page states it.
- What `/security/advisories/new` shows when private vulnerability reporting is off.
- Whether GitHub accepts `.yaml` issue or discussion forms, and `config.yaml`.
- What Dependabot does when both `dependabot.yml` and `dependabot.yaml` exist.
- Whether the 3-day default Dependabot cooldown is live on github.com.
- The label name length limit.
- The default Q&A and Show and tell category slugs.
- The CODEOWNERS errors view and the Dependabot error view in the UI.
- No live `gh api` run against a real repository; the plugin's other skills were not reviewed.
