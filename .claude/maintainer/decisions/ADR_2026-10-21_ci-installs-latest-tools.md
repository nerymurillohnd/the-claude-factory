---
status: accepted
date: 2026-10-21
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# CI installs the latest release of every tool; only TypeScript stays pinned, to 6.0.3

## Scope

- In scope: the `env` block and the install steps of `.github/workflows/validate.yml` and `.github/workflows/evals.yml`, the session-start hook `.claude/hooks/checkout.sh`, `.claude/CLAUDE.md` and the `plugin-consistency` skill.
- Out of scope: the GitHub Actions themselves, which stay pinned by commit SHA and are updated by Dependabot; the Node version from `.nvmrc` and `@types/node` in the lockfile; the versions a plugin pins for its own users, such as the TypeScript in `typescript6-lsp-intelligence/package.json`; and the `rev` fields of `.pre-commit-config.yaml`, which pre-commit requires and no git hook runs.

## Context and problem statement

Since ADR_2026-10-21_gates-run-installed-tools, the gates run the tools installed on the maintainer's machine by bare name, while CI installed them at pins in `validate.yml`. A local run therefore used versions CI did not: Claude Code was 2.1.307 locally and 2.1.304 in CI. The pins also had to be reviewed and bumped by hand, since Dependabot does not track tools installed with `npm -g` or `uv tool install`. Should CI keep the pins?

## Decision drivers

- CI checks with the tools the maintainer uses, which he keeps at their latest release.
- No hand-maintained version list.
- TypeScript 7 breaks the maintainer's other projects, so his machine stays on 6.0.3 (Nery, 2026-10-21).

## Considered options

- **Install the latest of every tool in CI, TypeScript excepted**: chosen.
- **Keep every pin**: rejected, because CI and the machine drift apart between manual bumps.
- **Remove every pin, TypeScript included**: rejected, because CI would run TypeScript 7.0.2 while the machine runs 6.0.3.

## Decision outcome

Chosen option: **latest everywhere but TypeScript**, by Nery's decision on 2026-10-21. `TYPESCRIPT_VERSION: "6.0.3"` is the only pin left. Claude Code, Biome and TypeScript install with `npm install --global`; ruff, mypy and basedpyright with `uv tool install`; uv itself through `setup-uv` with no `version` and no cache; ShellCheck from apt; shfmt and actionlint as the latest GitHub release binary, checked against the sha256 digest GitHub records for the asset, so the step fails when the asset or the digest is missing or does not match.

On the same day the maintainer's machine was brought to the latest of each: mypy went from 1.20.2 to 2.4.0 (0 issues on `scripts/` and `plugins/`), and Biome from 2.5.15 to 2.6.2 through its official installer, with `biome.json` migrated to the 2.6.2 schema (`biome migrate --write`).

### Consequences

- Good, because CI and the maintainer's machine run the same versions while he keeps his tools current.
- Good, because no pin needs a manual bump, and the session-start hook no longer compares the local `claude` with a pin.
- Bad, because a new release of any tool can turn CI red with no change in the repository; the fix then lands in the repository, never as a new pin.
- Bad, because a run is reproducible only on the day it ran: the job log is the record of which versions it used.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Only `TYPESCRIPT_VERSION` is pinned | `git grep -n "_VERSION" .github` | Only `TYPESCRIPT_VERSION` in `validate.yml`, on 2026-10-21 | Each change to a workflow |
| The shfmt and actionlint steps install the latest release and reject a bad digest | The step logic run locally on 2026-10-21 with `shasum -a 256 -c` in place of GNU `sha256sum --check --strict` | shfmt and actionlint: OK, Linux ELF binaries; a wrong digest: FAILED | First push |
| Every gate passes with the latest tools | `validate.yml` on the branch's first push | Pending | First push |

## More information

This replaces the "CI installs them at the pins" part of ADR_2026-10-21_gates-run-installed-tools, and its consequence about a local version that differs from the CI pin; the rest of that record stands.
