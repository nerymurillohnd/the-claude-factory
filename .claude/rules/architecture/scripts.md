---
paths:
  - "scripts/**"
  - "/typings/**"
---

# Maintainer scripts

- Put each maintainer script in one of the four folders of `scripts/`, by what it does:
  - `checks/`: a read-only check of the repository or of what it links to, the runners that sequence checks (`pre-commit-gate.sh`, `pr-checks.sh`, `plugins.sh`), and `install-git-hooks.sh`, which `prepare` runs to turn the pre-commit gate on.
  - `release/`: versions, release notes, changelogs, tags and the install check.
  - `generators/`: a script run on demand that writes repository files or GitHub state.
  - `tests/`: the tests, mirroring the folder under test (`tests/checks/skill_lint/` tests `checks/skill_lint/`), in `test_*.py` files written with `unittest`, never pytest.
- Ask the owner before adding a fifth folder. Keep the data a script reads beside it, as `generators/plugin-icons/` and `checks/live-urls.ignore` are.
- Treat `scripts/` as one Python package: import its modules absolutely (`from scripts.checks.skill_lint.model import Finding`), and give each package folder an `__init__.py` with a one-line docstring.
- Write Python modules without a shebang or executable bit: they run only through `python -m`. Give shell scripts and `plugin-icons.mjs` a shebang and mode 100755.
- Take the repository root from `scripts.REPO_ROOT`, never from a count of parent folders.
- Write new logic that parses files in Python, and keep shell for the Git hook, CI glue, loops over plugins and short pipelines of CLI tools, as `live-urls.sh` and `check-install.sh` are.
- Add each member of an untyped dependency a script uses to its stubs in `typings/<package>/`, as `typings/ruamel/yaml/` holds ruamel.yaml's.
