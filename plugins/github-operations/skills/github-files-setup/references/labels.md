# Labels

The files the setup writes name labels that must exist: the forms' and discussion forms' `labels:`, the labels the PR templates ask for, and `dependabot.yml`'s `labels`. GitHub skips a missing label without warning, and Dependabot ignores a missing custom label. The repository's labels win; `assets/labels.json` is the model for a group of labels the repository lacks.

## Decide the names (step 2)

Before any file is written, decide the label names the files will use, so the forms and the label list agree:

1. Use the repository's own label when one has the meaning, in its existing style.
2. Otherwise use GitHub's default label when one has the meaning: a new repository has `bug`, `documentation`, `duplicate`, `enhancement`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix` and `accessibility`, and `good first issue` feeds the repository's `/contribute` page.
3. Otherwise take the name from `assets/labels.json`, such as `status: triage` or `type: maintenance`.
4. For a component group (`area: <component>`), take the components from the repository: its packages, plugins or services.
5. When the repository has or wants an issue triage automation (a workflow, a cloud scheduled task or a stale-issue bot), use the exact lifecycle label names it applies. Anthropic's own triage applies `needs-info` and `needs-repro`; the model's `status: needs-info` and `status: needs-repro` fit a triage written in this repository's own style. A label never closes an issue by itself: closing after a timeout needs a separate closer, such as a stale-issue workflow, so promise it only when the repository has one.

## Create them (step 8)

1. Collect every label name the written files use.
2. Write the label list as a JSON list of `{"name", "color", "description"}` objects: each color as 6 hex digits without `#`, each description in 100 characters or fewer. When the repository keeps a label file (such as `.github/labels.json`), the list is that file, updated. Otherwise write the list outside the repository, in a scratch folder, so it stays out of the pull request.
3. Compare the list with the repository: `labels-sync.py --dry-run`, with the command in the Scripts table of `SKILL.md`. Its `summary` gives the missing, different and extra counts, and it changes nothing. Without `gh`, read the labels with the MCP `list_label` tool, save its output (all pages) and pass it as `--current <file>`.
4. Show the user the labels to create and to change. Creating or changing a label changes the repository: ask first, and keep only what the user approves in the list.
5. For each label the user declines that a written file still names: remove it from that file and run the file's check again, or, if the user wants the file as it is, list it under **Left for you** in the report.
6. After approval, apply the approved list:
   - With `gh`: the same `labels-sync.py` command with `--apply` in place of `--dry-run`. It creates the missing labels and updates the different ones, and never deletes or renames one. It asks for permission, because it writes to GitHub.
   - Without `gh`: the MCP `label_write` tool, once per label (`method: create` or `update`).
7. Run `labels-sync.py --dry-run` again: its summary must read `0 missing, 0 different`. Leave the labels the repository has and the list lacks (`extra_count`) as they are, unless the user asks.
