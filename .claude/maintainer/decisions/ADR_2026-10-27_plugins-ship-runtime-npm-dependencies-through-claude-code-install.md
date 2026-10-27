---
status: accepted
date: 2026-10-27
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Plugins ship runtime npm dependencies through Claude Code's dependency install

## Scope

- In scope: a plugin under `plugins/<name>/` whose code needs npm packages at runtime. It declares them in its own `package.json` and `package-lock.json` at the plugin root. First case: `tailwind-development` 0.2.0, whose MCP server needs `@modelcontextprotocol/server`, `@tailwindcss/language-server` and `vscode-jsonrpc`.
- In scope, maintainer side: `npm run setup` (`.claude/hooks/repo-setup.sh`) installs each such plugin's packages in the clone, and `scripts/tsconfig.plugins.json` excludes `plugins/*/node_modules`.
- Out of scope: the root `package.json`, which stays maintainer tooling only (ADR_2026-10-26_npm-tools-and-git-hooks-are-pinned-dev-dependencies); Python dependencies; plugins that need no packages.

## Context and problem statement

`tailwind-development` 0.2.0 runs the Tailwind CSS language server inside a plugin MCP server (spec `.claude/specs/2026-10-27-tailwind-development-diagnostics-mcp-design.md`). Its code needs three npm packages on every user's machine, whose environment the marketplace cannot see. How does a plugin of this marketplace get runtime npm packages to its users?

Claude Code installs a plugin's Node packages when it caches the plugin, if the plugin root holds a `package.json` and a supported lockfile ([plugins/loading](https://code.claude.com/docs/en/plugins/loading), "Node.js package dependencies"). The install allows registry packages only, pinned exactly in the lockfile, over `https`. It runs `--ignore-scripts`, applies no `overrides`, and stops after 60 seconds. A plugin loaded with `--plugin-dir` or in place from a local marketplace gets no install.

## Decision drivers

- Users install from a public marketplace; nothing reviews a plugin between the push and their install.
- Every file a plugin ships, and every package version it installs, must be reviewable in the repository.
- Least invasive design: nothing installed globally on the user's machine, no install scripts run.
- The plugin must work with only what its README declares (Node and npm on `PATH`).

## Considered options

- **A plugin-root `package.json` and `package-lock.json` (lockfile version 3, exact pins, registry packages), installed by Claude Code**: chosen.
- **An MCPB bundle with `node_modules` inside**: rejected. It would be an opaque zip of about 10 MB in the repository that no diff can review, and its settings would live in the bundle's own `user_config`, apart from the plugin's `userConfig`. It stays the fallback if Cowork proves not to run the dependency install.
- **README prerequisites the user installs globally (`npm install -g …`)**: rejected. It touches the user's global environment, leaves the versions to the user, and adds a manual step to every install and update.
- **Hand-written code in place of the packages**: rejected for the MCP protocol, where the SDK serves both revisions Claude Code speaks (2026-07-28 and the 2025 handshake); a hand-written server would have to reimplement both.

## Decision outcome

Chosen option: **a plugin-root `package.json` and `package-lock.json` installed by Claude Code**. It uses the documented install path, keeps every version pinned and reviewable, runs no package code at install, and writes nothing outside the plugin's cached copy.

A plugin `package.json` is `"private": true` and lists only `dependencies`, each an exact version. Prefer packages with few or no transitive dependencies and versions published at least two weeks earlier. The plugin README names every package downloaded at install, the npm registry as its source, and the Node minimum their `engines` fields set.

### Consequences

- Good, because users get exactly the versions the lockfile pins, with no global install and no install scripts.
- Good, because a dependency change shows in the pull request as a lockfile diff.
- Bad, because every install and update downloads from the npm registry: a restricted network, or an install longer than 60 seconds, leaves the plugin without its packages. `/plugin` and `claude plugin list` then show a note, and the README says so.
- Bad, because `--plugin-dir` runs skip the install: local testing needs `npm ci --ignore-scripts` in the plugin folder first.
- Bad, because the maintainer environment now holds plugin `node_modules`, which the gates must exclude. Node resolves imports by walking up the folders, so a test or type check can pass on a package from the root `node_modules` that users never receive. A plugin's imports must therefore resolve from its own `node_modules`.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Claude Code installs the packages into the cached copy | `release-and-versioning` step 8.5: HTTPS install from the branch, then `node_modules` is present and `claude plugin list` shows no dependency note | pending | Each release of a plugin with a `package.json` |
| The install runs in Cowork | A Cowork session on the user's computer with the plugin installed | pending, unverified | Before the README claims Cowork support for the MCP server |
| Lockfile meets the install's rules | `lockfileVersion` 3, every `resolved` on `https://registry.npmjs.org`, integrity present, no `overrides`, same dependencies in both files | pending (tailwind-development 0.2.0) | Every dependency change |

## More information

- ADR_2026-10-21_maintainer-only-root-package-json already left a plugin's own `package.json` allowed "when the plugin's architecture needs it"; this record makes it a practice, with its rules.
- Decided by Nery on 2026-10-27, when he approved the tailwind-development diagnostics MCP spec and its plan.
