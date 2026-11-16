# Repository files of a public plugin marketplace

The GitHub files around a public marketplace's catalog and plugins: what each one is for, where it lives and the rules GitHub applies to it. Facts come from GitHub Docs, read on 2026-11-16. A line marked **(pattern)** is a design choice for plugin marketplaces that no official page prescribes. For the catalog and the plugin folders, read `create-marketplace.md` and `manifest-reference.md`; for the workflows, `ci-cd.md`.

## Contents

- [Why these files matter for a marketplace](#why-these-files-matter-for-a-marketplace)
- [Issue forms](#issue-forms)
- [The template chooser](#the-template-chooser)
- [Labels](#labels)
- [Pull request template](#pull-request-template)
- [CODEOWNERS](#codeowners)
- [Dependabot](#dependabot)
- [Security policy and license](#security-policy-and-license)
- [Done when](#done-when)
- [Documentation References](#documentation-references)

## Why these files matter for a marketplace

People who install a plugin report problems from their own machines, and the maintainer can't see those machines. A report missing the plugin name, the Claude Code version (`claude --version`), the operating system or the surface (terminal, desktop, web, claude.ai, Cowork) can't be reproduced. The files below make each report arrive with what diagnosis needs, route changes to the people who own them, and keep the repository's own tooling current. They don't change what users install, but they decide whether the marketplace can be maintained.

Each file takes effect once it is on the default branch. Templates "are available to collaborators when they are merged into the repository's default branch". Labels and rulesets are repository settings, not files, and they take effect on GitHub as soon as they are created. So they need the owner's yes.

## Issue forms

- **Location**: `.github/ISSUE_TEMPLATE/<form-name>.yml`.
- **Required top-level keys**: `name` ("Must be unique from all other templates, including Markdown templates"), `description` and `body`.
- **Optional top-level keys**: `title`, `labels`, `assignees`, `type` and `projects`. A label named in `labels` that "does not already exist in the repository … will not be automatically added to the issue": create the labels first.
- **Body elements**: `markdown` (shown, not submitted), `textarea`, `input`, `dropdown`, `checkboxes` and `upload`. Each element except `markdown` takes an `id`, which uses only letters, digits, `-` and `_` and is unique in the form, plus `attributes` and `validations` (`required: true`).

**(pattern)** For a plugin marketplace, the bug form asks for:

- the plugin name, as a `dropdown` of the catalog's plugins, so reports can't name a plugin that doesn't exist;
- the plugin version;
- the output of `claude --version`;
- the operating system and shell;
- the surface;
- how the marketplace was added (`owner/repo`, URL or local path);
- the exact message, as a `textarea` with `render: shell`;
- the steps to reproduce it.

Keep the dropdown in step with the catalog: a plugin added to `marketplace.json` and missing from the form can't be reported.

## The template chooser

`.github/ISSUE_TEMPLATE/config.yml` controls what people see when they open an issue:

- `blank_issues_enabled: false`: contributors with Read or Triage roles see only the forms, while write access and above still see **Blank issue**, marked **Maintainers only**.
- `contact_links`: each entry has a `name`, a `url` and an `about`. Use them to send questions, security reports and support requests elsewhere.

## Labels

GitHub creates default labels, such as `bug` and `good first issue`, in every new repository. "Anyone with write access to a repository can create a label." Create them in the repository settings, with `gh label create <name> --color <hex> --description <text>` (https://cli.github.com/manual/gh_label_create), or through the REST API.

**(pattern)** For a marketplace, add a `plugin: <name>` label for each plugin, so issues and pull requests can be filtered per plugin. Keep the labels in step with the catalog and the issue forms. Keep the label set in a file in the repository, such as `.github/labels.json`, so it is reviewed like code and can be recreated, and apply it with a script or `gh`.

## Pull request template

- **One template**: `.github/pull_request_template.md`. Also accepted: the root `pull_request_template.md` or `docs/pull_request_template.md`.
- **Several templates**: put them under `.github/PULL_REQUEST_TEMPLATE/`, and choose one with the `template` query parameter.

**(pattern)** Make it ask which plugins changed, whether each one's `version` was bumped (with the version model), whether its CHANGELOG has an entry, and whether `claude plugin validate --strict` passed locally.

## CODEOWNERS

- **Location**: `.github/`, the root or `docs/`. GitHub uses "the first one it finds" in that order.
- **Size**: the file must be under 3 MB. Over that, it isn't loaded and no owner is requested.
- **Patterns**: they follow gitignore rules, and "the last matching pattern takes the most precedence".
- **Owners**: users or teams written `@username` or `@org/team-name`, each with explicit write access to the repository.
- **Branch**: each CODEOWNERS file covers only the branch it is on.

**(pattern)** Give each `plugins/<name>/` directory its owner, and the catalog (`.claude-plugin/`) and `.github/` the marketplace's maintainers. Code owners are requested for review on a pull request. Their review is a merge requirement only when a ruleset requires review from code owners.

## Dependabot

`.github/dependabot.yml` with `package-ecosystem: "github-actions"`, `directory: "/"` and a `schedule.interval` keeps the workflows' actions current. Add an entry for each other ecosystem the repository uses, such as `npm` or `pip` for maintainer scripts. `ci-cd.md`, "Harden every workflow", says why this matters for SHA-pinned actions.

## Security policy and license

- **`SECURITY.md`** states the supported versions and how to report a vulnerability privately (https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository). For a marketplace, which runs code on users' machines, give a private route rather than public issues, and link it from `config.yml`'s `contact_links` **(pattern)**.
- **A license file** at the root, and one in each plugin folder, because users receive only the plugin folder ("Fill in the metadata users see", `publish.md`; `license` in `manifest-reference.md`).

## Done when

- Every `.yml` under `.github/` parses, and each issue form has `name`, `description` and `body`, with unique `id`s.
- Every label a form or a workflow names exists, or is listed for the owner to create.
- The plugin dropdown, the per-plugin labels and the CODEOWNERS entries list the same plugins as `marketplace.json`.
- Each file that only takes effect on GitHub (labels, rulesets, enabling Dependabot) is listed in the report as waiting on the owner, until they confirm it.

## Documentation References

- Source page: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms
- https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema — form elements, keys and validations
- https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository — `config.yml` and the template chooser
- https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels — default labels, who can create labels
- https://cli.github.com/manual/gh_label_create — `gh label create`
- https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository — pull request templates
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners — CODEOWNERS
- https://docs.github.com/en/code-security/dependabot/working-with-dependabot/keeping-your-actions-up-to-date-with-dependabot — Dependabot for actions
- https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository — `SECURITY.md`
