# Form rules

The rules GitHub applies to issue forms, the issue template chooser and discussion forms, as a checklist. When `check-forms.py` can't run, check each written file against this page by reading it, and record the check as done by hand. The script checks every rule below except three, which you always check by reading: a form name against Markdown templates and files outside the run, that each label exists, and that each contact link's page exists.

Sources, read on 12 November 2026: GitHub's [Syntax for issue forms](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms), [Syntax for GitHub's form schema](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema), [Common validation errors when creating issue forms](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/common-validation-errors-when-creating-issue-forms), [Syntax for discussion category forms](https://docs.github.com/en/discussions/managing-discussions-for-your-community/syntax-for-discussion-category-forms) and [Configuring issue templates for your repository](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository).

## Contents

- Top level
- Body
- Values that YAML reads as something else
- Options
- Labels and placeholders
- config.yml

## Top level

- An issue form has `name`, `description` and `body`, all three required. It may also have `title`, `labels`, `assignees`, `type` and `projects`, and no other key.
- `name` is unique among all the repository's templates, Markdown templates included. Compare it with every file in `.github/ISSUE_TEMPLATE/`, not only the ones you wrote. A name of 3 characters or fewer hides the form.
- A discussion form takes only `title`, `labels` and `body`: no `name` and no `description`.

## Body

- `body` is not empty and holds at least one field that is not `markdown`.
- Each field has a `type`: `markdown`, `textarea`, `input`, `dropdown`, `checkboxes` or `upload`.
- Each `id` is unique in the form and uses only letters, digits, `-` and `_`. A `markdown` field has no `id`.
- Each field that takes input has a `label`, and the labels are unique.
- Labels must not be too similar. A field without an `id` is referenced by its label made into a slug: accents become plain letters, then lower case, and every run of characters other than letters, digits, `-` and `_` becomes one `-`. Two fields whose references match, or a reference that matches another field's `id`, are refused. Fix it by rewording one label or giving one of the two fields an `id`.
- Checkbox option labels are unique among the options of their field, and differ from the labels of other fields that have no `id`: an `id` on the clashing field also resolves it.
- The `label` of an `input` or `textarea` holds no forbidden word, such as "password".
- `validations` takes only the keys of the field's type:
  - `required` for every type but `markdown`;
  - `min_length` only for `input` and `textarea`;
  - `accept` only for `upload`.
- A string attribute is never empty or only spaces: when the field doesn't need it, delete the key.

## Values that YAML reads as something else

GitHub reads forms as YAML 1.1. An unquoted value in this list becomes a boolean, not text: `y`, `Y`, `yes`, `Yes`, `YES`, `n`, `N`, `no`, `No`, `NO`, `true`, `True`, `TRUE`, `false`, `False`, `FALSE`, `on`, `On`, `ON`, `off`, `Off` and `OFF`. An unquoted number, such as `1.3`, becomes a number.

- In every text value (`name`, `description`, `title`, `id`, `label`, `placeholder`, `value`, `assignees`, each option and each label name), quote such a value: `"Yes"`, `"1.3"`.
- `required` and `multiple` are booleans: write `true` or `false`.

## Options

- A `dropdown` or `checkboxes` field's options are not empty and are all distinct.
- A `dropdown` option is never "None": GitHub reserves it for no choice. With `default` set, "n/a" is refused too.

## Labels and placeholders

- The form's `labels:` names each label once, compared without regard to case. Every label it names must exist in the repository, or GitHub skips it without warning: the labels step creates them.
- No upper-case placeholder such as `<OWNER>` or `<FAQ_PATH>` is left. Lower-case prompts in a `title`, such as `<short summary>`, stay.

## config.yml

- `blank_issues_enabled` is `true` or `false`.
- Each entry of `contact_links` has `name`, `url` and `about`, and its URL points to a page that exists.
