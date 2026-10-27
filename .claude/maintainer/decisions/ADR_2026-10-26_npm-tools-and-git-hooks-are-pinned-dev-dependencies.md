---
status: accepted
date: 2026-10-26
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-21_maintainer-only-root-package-json
superseded-by: none
---

# The npm tools and the git hooks are pinned devDependencies, run through npm scripts

## Scope

- In scope: the root `package.json` (devDependencies and scripts), `package-lock.json`, `.husky/`, the `package.json` rules of `scripts/check-repo.mjs`, the `--only` option of `scripts/gates.mjs`, `biome.json` → `$schema`, and `.claude/CLAUDE.md` → Maintainer Tooling.
- Out of scope: how CI installs its tools (ADR_2026-10-26_ci-installs-npm-tools-from-the-lockfile); the tools npm does not distribute (ruff, basedpyright, shfmt, ShellCheck, actionlint, the Claude Code CLI); plugin runtimes, which the root `package.json` never serves.

## Context and problem statement

ADR_2026-10-21_maintainer-only-root-package-json allowed only exact `@types/*` packages in the root `package.json`; every other tool ran as installed globally, by bare name. Biome's version then lived in three places by hand that had drifted (the maintainer's binary and `validate.yml` at 2.6.3, `.pre-commit-config.yaml` at 2.5.15), a Biome devDependency turned `main` red against that rule, and no git hook ran the gates. Nery ordered Husky ("instala husky"), installed it, set `.husky/pre-commit` to `npm test`, and asked to consolidate the maintenance scripts behind `package.json`. Asked for the standard practice regardless of the repository's rules, the answer was: the npm tools as exact devDependencies with a lockfile, npm scripts as the entry points, and git hooks from a devDependency that call the same scripts as CI. How should the repository hold its npm tools and git hooks?

## Decision drivers

- One version per npm tool for every clone, worktree and git hook, set by `package-lock.json`, updated through Dependabot's npm pull requests.
- One definition of each command: the gates of `scripts/gates.mjs` stay the only source; npm scripts select them.
- The root `package.json` stays maintainer tooling, never a plugin runtime.

## Considered options

- **Biome, TypeScript and Husky as exact devDependencies, every maintenance command an npm script, Husky hooks calling them**: chosen.
- **Git hooks without a package (`core.hooksPath` to a versioned folder set by the session hook)**: rejected because Husky does the same with a `prepare` script npm runs on every install, and Nery chose Husky.
- **Keep only the `@types/*` packages local** (ADR_2026-10-21_maintainer-only-root-package-json): rejected because the versions drifted by hand and no hook ran the gates.

## Decision outcome

Chosen option: **pinned devDependencies run through npm scripts, with Husky hooks**, because every local run then uses the lockfile's versions and every command is written once.

- devDependencies: `@biomejs/biome` 2.6.3, `typescript` 6.0.3, `husky` 9.1.7 and `@types/node` 26.6.5, each exact; `check-repo.mjs` refuses a version range and every auto-run script except `"prepare": "husky"`.
- npm scripts: `test`, `typecheck` (`:ts`, `:python`), `lint` (`:python`, `:js`, `:shell`), `format:check`, `check:repo`, `check:version-bump` and `generate:check` run `node scripts/gates.mjs --only <prefixes>`; `format` and `fix` write with each tool's config; `setup`, `labels:sync` and `version:bump` run their scripts.
- Husky: `.husky/pre-commit` runs `npm test`; `.husky/pre-push` runs `npm run gates`. `~/.config/husky/init.sh` loads nvm, uv's `~/.local/bin` and Homebrew, so hooks started from a GUI find the tools.
- `biome.json` reads its `$schema` from the installed package, which always matches its version.

### Consequences

- Good, because `npm run` and the git hooks use the same Biome and TypeScript on every clone, and a new release arrives as a reviewed pull request.
- Bad, because in this repository the npm tools no longer run by bare name from PATH as `~/.claude/ENVIRONMENT.md` says; `.claude/CLAUDE.md` states the exception, and the global binaries serve the editor.
- Bad, because the pre-commit hook runs the maintainer tests (about a minute) on every commit and does not lint: a lint error reaches a commit and the pre-push gates stop it.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Every npm script passes | `npm test`, `npm run typecheck`, `lint`, `format:check`, `check:repo`, `generate:check`, `check:version-bump` | Passed on 2026-10-26, each exit 0 | Each change to `package.json` or `scripts/gates.mjs` |
| The hooks run | Commits `0da35ed` to `fd2330a` each passed `npm test` through Husky; the first attempt failed until the gates stopped passing git's hook variables | Passed on 2026-10-26 | Each Husky major version |

## More information

- Decided by Nery on 2026-10-26: "instala husky", his `npm install --save-dev husky && npx husky init` and `.husky/pre-commit` set to `npm test`, the goal "consolidate and build the project maintenance scripts wired in the package.json", and the question "de no existir esas rules del repo: cuál es la buena práctica y lo que mejor aplica a este repo".
- `.pre-commit-config.yaml` is unused and stale; the `block-no-verify` hook refused its deletion from this session, so Nery deletes it.
- Related: ADR_2026-10-21_gates-run-from-one-script, ADR_2026-10-26_maintainer-tools-cover-the-whole-repository.
