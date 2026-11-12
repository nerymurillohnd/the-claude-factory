# Labels

Every file written in the earlier steps can name labels that must exist: the forms' and discussion forms' `labels:`, the labels the PR templates ask for, and `dependabot.yml`'s `labels`. GitHub skips a missing label without warning, and Dependabot ignores a missing custom label. The repository's labels win; `<skill-dir>/assets/labels.json` is the model for a group of labels the repository lacks.

1. Collect every label name the written files use.
2. Build the label list, as a JSON list of `{"name", "color", "description"}` objects:
   - Start from the repository's own label file when it has one (such as `.github/labels.json`), and keep its style.
   - Map onto GitHub's default labels before adding a new one. A new repository has `bug`, `documentation`, `duplicate`, `enhancement`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix` and `accessibility`, and `good first issue` feeds the repository's `/contribute` page.
   - Add, from the model, only the groups the repository needs and every label the collected names still miss. For a component group (`area: <component>`), take the components from the repository: its packages, plugins or services.
   - Write each color as 6 hex digits without `#`, and each description in 100 characters or fewer.
3. Compare the list with the repository: `python3 <skill-dir>/scripts/labels-sync.py --repo <owner>/<repo> --labels <list file>`. It prints `missing`, `different` and `extra` as JSON and changes nothing. Without `gh`, read the labels with the MCP `list_label` tool, save its output (all pages) and pass it as `--current <file>`.
4. Show the user the labels to create and to change. Creating or changing a label changes the repository: ask first, and keep only what the user approves in the list file.
5. After approval, apply the approved list:
   - With `gh`: `python3 <skill-dir>/scripts/labels-sync.py --repo <owner>/<repo> --labels <list file> --apply`. It creates the missing labels and updates the different ones, and never deletes or renames one.
   - Without `gh`: the MCP `label_write` tool, once per label (`method: create` or `update`).
   - When the repository keeps a label file, write the approved list there too, in the same pull request.
6. Run step 3 again: it must exit 0. Leave labels the repository has and the list lacks (`extra`) as they are, unless the user asks.
