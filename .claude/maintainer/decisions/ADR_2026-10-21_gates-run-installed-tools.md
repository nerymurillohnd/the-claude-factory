---
status: accepted
date: 2026-10-21
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The gates run the tools installed on the machine by bare name, never through `npx` or `uvx`

## Scope

- In scope: every gate of `scripts/gates.mjs` that ran `npx --yes <pkg>@<version>` or `uvx` (TypeScript, Biome, ruff, mypy), the install steps of `.github/workflows/validate.yml`, `.pre-commit-config.yaml`, `.claude/CLAUDE.md` → Stack and Commands, and the message of `check-repo.mjs` for a non-type devDependency.
- Out of scope: the tools that already ran by bare name (basedpyright, ShellCheck, shfmt, actionlint, `claude`), and plugins, which never depend on the maintainer's machine.

## Context and problem statement

After the CI split, each gate that ran through `npx` with a cold npm cache took about 300 s, and the `Validate` workflow went from about 30 s to about 10 minutes. A direct `npx --yes @biomejs/biome@2.5.15 --version` with an empty cache reproduced it locally (302 s, no output); the cause was not found. The same tools were already installed on the maintainer's machine at the pinned versions: the Homebrew `biome` checked 71 files in 62 ms. How should the gates start their tools?

## Decision drivers

- Nery, 2026-10-21: "si algo está instalado en mi máquina, ÚSALO."
- No download or registry call between a gate and its tool.
- One way to run each tool, the same locally and in CI.

## Considered options

- **Run each tool by bare name; CI installs the pins first**: chosen.
- **Add the CLIs to the root `devDependencies` so `npx` finds them locally**: not chosen; it duplicates the pins and widens the maintainer-only `package.json`.
- **Keep `npx` and find the cause of the stall**: not chosen; the tools are installed, so the download is unneeded.

## Decision outcome

Chosen option: **bare names**. `gatesFor` no longer reads the pins: `loadPins` and the missing-pin test are gone, and a test fails any gate whose command is `npx` or `uvx`. In CI, the `policy` job installs TypeScript with `npm install --global`, the `python` job installs ruff, mypy and basedpyright with `uv tool install`, and the `lint` job installs Biome with `npm install --global`, each at the pin of the `env` block. Locally, a missing tool is installed from its source (nvm global, uv, Homebrew).

This replaces the `npx` and `uvx` parts of ADR_2026-10-21_maintainer-only-root-package-json and the pin reading of ADR_2026-10-21_gates-run-from-one-script; the rest of both records stands.

### Consequences

- Good, because no gate downloads anything, so the cold-cache stall cannot happen.
- Bad, because a local run uses whatever version is installed: a version that differs from the CI pin passes locally without warning. Today `claude` is 2.1.307 locally and 2.1.304 in CI.
- Bad, because a missing tool now fails the gate with "<cmd> is not on PATH" instead of being fetched.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| No gate runs through `npx` or `uvx` | `scripts/tests/gates.test.mjs` → "every gate runs the installed tool, never npx or uvx" | Passed on 2026-10-21; with one gate set back to `npx` on purpose, it failed naming `biome-plugins` | Each push |
| Every gate passes with the installed tools | `npm run gates` | See the commit that made the change | Each push |
| CI installs what each group runs | `validate.yml` on the branch's first push | Pending | First push |

## More information

Nery gave the rule on 2026-10-21 after running `biome check --write`, `tsc`, `ruff` and `basedpyright` by bare name in the repository.
