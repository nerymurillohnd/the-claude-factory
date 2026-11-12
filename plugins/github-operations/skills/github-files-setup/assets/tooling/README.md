# Repository checks

Two scripts that keep this repository's GitHub files valid. They were copied from the github-operations plugin, version <PLUGIN_VERSION>.

- `check-forms.py` checks the issue forms, the issue template chooser, the discussion forms and `dependabot.yml` against GitHub's schemas and form rules.
- `labels-sync.py` compares `<LABEL_FILE>` with the repository's labels on GitHub, and with `--apply` creates and updates them. It never deletes a label.

## Requirements

- Python 3.12 or later.
- For `check-forms.py`: ruamel.yaml 0.19.1 and check-jsonschema 0.39.0, declared in `<DEPENDENCY_FILE>`. Install them in a virtual environment, not in the system's Python:

  ```bash
  <INSTALL_COMMAND>
  ```

- For `labels-sync.py`: the GitHub CLI (`gh`), signed in.

## Run them

From the repository's root:

```bash
<PYTHON> <SCRIPTS_PATH>/check-forms.py --kind issue <ISSUE_FORMS>
<PYTHON> <SCRIPTS_PATH>/check-forms.py --kind issue-config .github/ISSUE_TEMPLATE/config.yml
<PYTHON> <SCRIPTS_PATH>/check-forms.py --kind discussion .github/DISCUSSION_TEMPLATE/*.yml
<PYTHON> <SCRIPTS_PATH>/check-forms.py --kind dependabot .github/dependabot.yml
<PYTHON> <SCRIPTS_PATH>/labels-sync.py --dry-run --repo <OWNER>/<REPO> --labels <LABEL_FILE>
```

Each script lists its options and exit codes with `--help`. Exit 0 means it ran, with its result and a summary; exit 2 means it could not run, with the reason.
