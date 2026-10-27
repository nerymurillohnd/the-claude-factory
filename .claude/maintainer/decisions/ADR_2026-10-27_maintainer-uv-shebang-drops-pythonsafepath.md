---
status: accepted
date: 2026-10-27
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-24_maintainer-python-shebang-follows-its-dependencies
superseded-by: none
---

# Maintainer scripts with dependencies use the plain uv shebang, without `PYTHONSAFEPATH=1`

## Scope

- In scope: the shebang of every maintainer Python script with third-party dependencies (today `scripts/validators/lsp-json-schema.py`, `marketplace-json-schema.py`, `mcp-json-schema.py`, `plugin-json-schema.py`, `skill-names-consistency.py` and `scripts/tests/run_pytest.py`), and `UV_SHEBANG` in `scripts/gates.mjs`, which recognises it. The rest of ADR_2026-10-24_maintainer-python-shebang-follows-its-dependencies carries forward: a standard-library script starts with `#!/usr/bin/env python3`; a script with dependencies declares `requires-python = "==3.15.*"` and its `dependencies` in PEP 723 inline metadata, is executable and runs by path.
- Out of scope: plugin scripts, which keep `#!/usr/bin/env python3`; the uv policy in CI (`UV_PYTHON_PREFERENCE=only-managed`, `UV_PYTHON_DOWNLOADS=manual`).

## Context and problem statement

ADR_2026-10-24_maintainer-python-shebang-follows-its-dependencies kept `#!/usr/bin/env -S PYTHONSAFEPATH=1 uv run --script` for scripts with dependencies. `PYTHONSAFEPATH=1` keeps the script's folder off `sys.path`, so a `json.py` beside the script cannot replace the standard `json` module; ADR_2026-10-24_maintainer-python-entry-points-use-a-uv-shebang measured that shadowing without it. Nery changed the six scripts to `#!/usr/bin/env -S uv run --script`, the form uv's guide and `~/.claude/ENVIRONMENT.md` show and `.claude/rules/hooks-and-scripts.md` already states. Should the shebang keep `PYTHONSAFEPATH=1`?

## Decision drivers

- One shebang form across the machine's projects, its environment file and this repository's rules.
- The folders these scripts live in hold only maintainer files that Nery and Claude Code write, under review before each commit.

## Considered options

- **`#!/usr/bin/env -S uv run --script`**: chosen.
- **Keep `#!/usr/bin/env -S PYTHONSAFEPATH=1 uv run --script`**: rejected by Nery, who accepted the shadowing risk.

## Decision outcome

Chosen option: **the plain uv shebang**, because it matches the form used everywhere else on this machine, and Nery accepts the risk that a module-named file beside a script shadows a standard module.

### Consequences

- Good, because the shebang now matches `~/.claude/ENVIRONMENT.md` and `.claude/rules/hooks-and-scripts.md`.
- Bad, because a file such as `json.py` placed in `scripts/validators/` or `scripts/tests/` would be imported in place of the standard module when one of these scripts runs.

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| A file beside a script shadows a standard module | A module-named `.py` file is added to `scripts/validators/` or `scripts/tests/` | The validator or the test runner imports the wrong code, in CI too | Review new files in those folders before each commit | Nery Samuel Murillo |

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The six scripts run under the new shebang, and the gates recognise it | `node scripts/gates.mjs --only ruff-,basedpyright-,validator:` and `npm test` | 2026-10-27: every validator, `pytest-scripts` and `basedpyright-maintainer` pass | Each new PEP 723 script |

## More information

- Decided by Nery on 2026-10-27, after being asked to confirm the change given the shadowing risk.
- ADR_2026-10-24_maintainer-python-entry-points-use-a-uv-shebang was already superseded by ADR_2026-10-24_maintainer-python-shebang-follows-its-dependencies, which this record replaces.
