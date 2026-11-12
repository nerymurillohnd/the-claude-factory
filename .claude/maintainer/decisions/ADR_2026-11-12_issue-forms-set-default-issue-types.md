---
status: accepted
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Set GitHub's default issue types from the issue forms and keep the type labels

## Scope

The `type:` key of the forms in `.github/ISSUE_TEMPLATE/`, and the `type:` labels in `.github/labels.json`. Maintainer scope.

## Context and problem statement

GitHub made issue types generally available on repositories owned by personal accounts (changelog 2026-11-11). This repository already has the default types `Task`, `Bug` and `Feature` (REST `repos/nerymurillohnd/the-claude-factory/issue-types`). A form can set the type with its `type:` key. The `type:` labels classify issues and pull requests, and issue types do not exist on pull requests: `type: bug`, `type: enhancement` and `type: documentation` are on 22, 56 and 18 pull requests.

## Decision drivers

- Use GitHub's native field where it exists.
- Keep one classification that also covers pull requests.
- No account-wide change: custom issue types are defined for the whole account, across all its repositories.

## Considered options

- **Forms set the default types (bug report and docs issue → `Bug`; feature request and plugin idea → `Feature`; question → none), and the `type:` labels stay**: chosen.
- **Replace the `type:` labels with issue types**: rejected because pull requests cannot carry issue types.
- **Create custom types (Documentation, Question, Plugin idea)**: rejected because they would appear in every repository of the owner's account.
- **Ignore issue types**: rejected because the default types already exist and cost nothing to set.

## Decision outcome

Chosen option: **default issue types set by the forms, with the type labels kept**, because issues gain the native field while pull requests and changelogs keep using the labels.

### Consequences

- Good, because `check-jsonschema` 0.39.0 accepts the `type:` key in the issue forms.
- Bad, because an issue carries its kind twice: as a type and as a label.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| A new issue from a form gets its type | Open an issue from each form after the merge to `main` | Pending: forms apply after PR #104 merges | After the merge |

## More information

- Sources: GitHub changelog 2026-11-11, "Issue types and fields are available for personal accounts"; GitHub docs "Managing issue types in an organization" ("Default issue types are included in every organization and user account"); GitHub docs "Syntax for issue forms" (`type`).
- The owner asked on 2026-11-12 to research and settle issue types in this session instead of deferring them.
