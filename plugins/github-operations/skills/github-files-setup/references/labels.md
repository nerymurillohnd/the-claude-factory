# Labels

MCP tools are named `mcp__<server>__<tool>`; find `<server>` as [github-access.md](github-access.md#order-of-routes) says.

The files the setup writes name labels that must exist: the forms' and discussion forms' `labels:`, the labels the PR templates ask for, and `dependabot.yml`'s `labels`. GitHub skips a missing label without warning, and Dependabot ignores a missing custom label. The repository's labels win; `assets/labels.json` is the model for a group of labels the repository lacks.

## Decide the names (step 2)

Before any file is written, decide the label names the files will use, so the forms and the label list agree:

1. Use the repository's own label when one has the meaning, in its existing style.
2. Otherwise use one of GitHub's default labels when one has the meaning ([Current behavior](#current-behavior-checked-on-2026-11-12-verify-before-relying-on-it) lists them). `good first issue` feeds the repository's `/contribute` page.
3. Otherwise take the name from `assets/labels.json`, such as `status: triage` or `type: maintenance`.
4. For a component group (`area: <component>`), take the components from the repository: its packages, plugins or services.
5. When the repository has or wants an issue triage automation (a workflow, a cloud scheduled task or a stale-issue bot), use the exact lifecycle label names it applies; [Current behavior](#current-behavior-checked-on-2026-11-12-verify-before-relying-on-it) names Anthropic's. The model's `status: needs-info` and `status: needs-repro` fit a triage written in this repository's own style. A label never closes an issue by itself: closing after a timeout needs a separate closer, such as a stale-issue workflow, so promise it only when the repository has one.

## Create them (step 8)

1. Collect every label name the written files use.
2. Write the label list as a JSON list of `{"name", "color", "description"}` objects: each color as 6 hex digits without `#`, each description in 100 characters or fewer. For a label the repository already has, leave out a field to keep its current value; a label to create needs its color. Names are compared without regard to case, as GitHub does: `Bug` and `bug` are one label. When the repository keeps a label file (such as `.github/labels.json`), the list is that file, updated. When the user accepted repository tooling, the list becomes the repository's label file ([tooling.md](tooling.md)). Otherwise write the list outside the repository, in a scratch folder, so it stays out of the pull request.
3. Compare the list with the repository: `labels-sync.py --dry-run`, with the command in the Scripts section of `SKILL.md`. Its `summary` gives the missing, different, extra and archived counts, and it changes nothing; each item under `different` names the fields that change. A label that differs only in the case of its name is listed under `case_only` and left as it is: rename it in GitHub by hand when the user wants the new case. A label to create without a color is listed under `missing_color`: give it one before `--apply`. Without `gh`, read the labels with the MCP tool `mcp__<server>__list_label`, page after page with `after` until `pageInfo.hasNextPage` is false, save the pages as one JSON list of page objects or one page per line, and pass the file as `--current <file>`. The script refuses a file whose last page says more pages follow.
4. Show the user the labels to create and to change. Creating or changing a label changes the repository: ask first, and keep only what the user approves in the list.
5. For each label the user declines:
   - A label to create that a written file still names: remove it from that file and run the file's check again, or, if the user wants the file as it is, list it under **Left for you** in the report.
   - A change to a label the repository already has: drop the changed fields from the list, so the repository's values stay. The label exists, so the files that name it stay as they are.
6. After approval, apply the approved list:
   - With `gh`: the same `labels-sync.py` command with `--apply` in place of `--dry-run`. It creates the missing labels and updates the different ones, never renames or deletes one, and refuses to run while a label to create has no color. It asks for permission, because it writes to GitHub. When it exits 2, some labels may already be written: read `created` and `updated` in its output and the reason on stderr, fix the cause, then run `--dry-run` and `--apply` again; each run works out what is left.
   - Without `gh`: the MCP tool `mcp__<server>__label_write`, once per label (`method: create` or `update`).
7. Run `labels-sync.py --dry-run` again, without `gh` on a fresh read of `list_label`: its summary must read `0 missing, 0 different`. A label the repository archived counts as present, but nobody can pick it: tell the user to unarchive the ones a file names. Only the `gh` route reports archived labels: the MCP `list_label` output does not say which are archived. Leave the labels the repository has and the list lacks (`extra_count`) as they are, unless the user asks.

## Current behavior (checked on 2026-11-12; verify before relying on it)

- A new repository has GitHub's default labels: `bug`, `documentation`, `duplicate`, `enhancement`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix` and `accessibility`.
- Anthropic's own issue triage applies `needs-info` and `needs-repro`. Its command applies only labels that already exist (a missing one is skipped, not reported), exactly one of `bug`, `enhancement`, `question`, `invalid` or `duplicate` on a new issue, and, when a person comments, removes `stale` and `autoclose` if the issue has them.
