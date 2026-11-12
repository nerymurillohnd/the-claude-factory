# Repository tooling

An optional extra: leave the repository its own copy of the two checks, so its maintainers can validate a form or sync labels after the setup, without this skill. It never replaces the checks the skill runs during the setup.

## Contents

- When to offer it
- What it writes
- Dependencies
- Limits

## When to offer it

Offer it at step 2, with the files you chose, only when the repository will keep editing these files: several maintainers, forms or labels that change often, or a label file it already keeps. Say why from what step 1 found. Skip it for a repository that is set up once and rarely touched, and say so.

## What it writes

| Source | Written in the repository as |
| :-- | :-- |
| `scripts/check-forms.py` and `scripts/labels-sync.py`, copied unchanged with the command in step 10 of `SKILL.md` | `.github/scripts/`, or the folder the repository keeps its own tooling in |
| The approved label list from step 8 | `.github/labels.json`, or the label file the repository already has |
| `assets/tooling/README.md`, with its placeholders filled: `<ISSUE_FORMS>` lists the issue forms, `config.yml` excluded; keep only the commands for files the repository has | `README.md` in the same folder as the scripts |

Copy the scripts, never retype or edit them: a copy that matches the plugin's file can be compared with a newer plugin version later.

## Dependencies

`check-forms.py` needs Python 3.12 or later with ruamel.yaml 0.19.1 and check-jsonschema 0.39.0; `labels-sync.py` needs only Python 3.12 or later and `gh`. Declare the two packages where the repository already declares development tools, and install nothing without the user's approval:

| The repository has | Declare them in |
| :-- | :-- |
| `uv.lock` | Its development group: `uv add --dev 'ruamel.yaml==0.19.1' 'check-jsonschema==0.39.0'` |
| `pyproject.toml` with `[dependency-groups]` | Its `dev` group, with those exact pins |
| `requirements-dev.txt` | That file, with those exact pins |
| No Python packaging | A `requirements.txt` next to the scripts, with those exact pins |

The tooling README tells maintainers to install them in a virtual environment, never into the system's Python, which many systems refuse.

## Limits

- The copies are a snapshot of this plugin's version: fixes in later versions don't reach them. The report names the version copied, and running this step again from a newer plugin version replaces the copies after a diff.
- A workflow that runs these checks on pull requests is outside this skill, which writes no workflows: tell the user it is possible, and leave it to them.
