# How to run this project, stage by stage

The commands of each lifecycle stage. It lists only Claude Code commands and the npm scripts in `package.json`. Under a stage, the **Docs** line comes first: it names the skill that writes the documents the stage creates or edits, and the event or step to follow; write each document from its procedure and template in the `docs-maintenance` skill, never from memory. Run the mechanical checks yourself. Commands marked "user side" are what users run; they go in READMEs and docs.

## Phase A — Marketplace setup (one time)

### 1. Planning and design

- `claude --version` — the installed Claude Code version; check it before relying on a version-gated flag.
- `claude plugin --help`, `claude plugin <subcommand> --help` — the subcommands and options the installed binary has; they win over the docs.

### 2. Marketplace scaffolding

- **Docs:** With the `docs-maintenance` skill, event Repository foundation: the root `README.md`, the root `LICENSE` and `SECURITY.md`.
- `claude plugin validate .` — validates `marketplace.json` from the marketplace root.
- `npm run validate` — `claude plugin validate --strict` on every `plugins/*/`, then on the marketplace root, then `validate:claude` and `validate:mods`.

### 3. Repository governance

- **Docs:** With the `docs-maintenance` skill, events Repository foundation and The owner changes a policy: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md` and `PRIVACY.md`.
- `npm run tools:install` — installs the pinned uv tools: ruff, basedpyright, zizmor and check-jsonschema.
- `npm run lint` — every linter: `lint:js`, `lint:python`, `lint:shell`, `lint:workflows` and `lint:github`.
- `npm run lint:workflows` — actionlint and zizmor on the GitHub Actions workflows.
- `npm run lint:github` — issue forms, the issue config and `dependabot.yml` against their schemas, then the form dropdowns and labels against the catalog.
- `npm run labels:sync` — syncs the GitHub labels from `.github/labels.json` and the catalog; it changes GitHub.
- `npm run test:scripts` — the unittest suite of the maintainer scripts in `scripts/testers/`.
- `npm run check` — `lint`, `typecheck`, `check:consistency` and `validate` in that order.
- `claude plugin validate <path> --strict --json` — fails on warnings and gives a machine-readable report.
- `claude plugin test [dir]` — runs a mod's tests; it needs no sign-in or network.

### 4. Plugin scaffolding

- **Docs:** With the `docs-maintenance` skill, event New plugin: the plugin's `LICENSE`, its `CHANGELOG.md`, its `NOTICE.txt` when it bundles third-party material, its `README.md` (written in full by the `plugin-readme-writer` subagent), its catalog row in the root `README.md` and `PRIVACY.md`. Its first version comes from the `plugin-versioning` skill.
- No command. `claude plugin init` writes only to `~/.claude/skills/<name>/`, so it doesn't create a plugin in this repository.

## Phase B — Plugin development (per plugin)

### 5. Component authoring

- **Docs:** The `plugin-versioning` skill (step 5) writes the plugin's `CHANGELOG.md` notes and `README.md` changes with the `docs-maintenance` skill; that skill's events Third-party material changes and Data handling changes cover `NOTICE.txt` and `PRIVACY.md`.
- `claude --plugin-dir <plugin-dir>` — loads the plugin being edited for one session.
- `/reload-plugins` — applies on-disk edits in a running session.
- `/reload-plugins --force` — applies a reload that adds or removes a plugin MCP server or the `LSP` tool.
- `claude --plugin-dir <plugin-dir> plugin details <name>` — the plugin's components and projected token cost.
- `npm run lint:skills` — checks every skill (`plugins/*/skills/*/SKILL.md` and `.claude/skills/*/SKILL.md`) with skill-lint. It changes no file and exits 0 with no error, 1 on an error (or on a warning with `--strict`), and 2 on a usage error.
- `npm run lint:skills -- <skill folder>` — checks one skill; pass `--only CO,SC`, `--strict`, `--manifest` or `--json` after `--` to narrow or reshape the report.
- Report each defect `lint:skills` finds to the owner, one question per rule id, and fix it or record it as debt only after the owner decides.
- `npm run lint:js` — Biome on the JavaScript, TypeScript, JSON, Markdown and YAML files.
- `npm run lint:python` — ruff lint and format check.
- `npm run lint:shell` — ShellCheck and the shfmt check on every shell script.
- `npm run typecheck` — `typecheck:ts`, then `typecheck:python`.
- `npm run typecheck:ts` — `tsc` on the TypeScript.
- `npm run typecheck:python` — basedpyright on plugin Python, then on maintainer Python in `scripts/`.
- `npm run fix` — rewrites files: Biome fixes, ruff fixes and format, shfmt.
- `npm run format` — rewrites files: Biome, ruff and shfmt formatting only.
- `npm run icons:render [-- <plugin>...]` — rewrites each plugin's `.claude-plugin/icon.png` from `scripts/generators/plugin-icons/<plugin>.svg`; needs Playwright's Chromium, ImageMagick and the JetBrains Mono font.

### 6. Dependencies and relevance

- `/reload-plugins` — installs missing dependencies and reports the ones it resolved.
- `claude plugin prune [--scope <scope>] [--dry-run]` — removes auto-installed dependencies no plugin needs.
- `claude plugin validate .` — checks each entry's `relevance` block.

### 7. Marketplace registration

- **Docs:** With the `docs-maintenance` skill, event New plugin: the plugin's catalog row in the root `README.md`.
- `claude plugin validate .` — flags duplicate names, `..` paths and version mismatches between an entry and its `plugin.json`.
- `npm run check:consistency` — what `validate` doesn't check across files: names, `renames`, `forceRemoveDeletedPlugins`, changelog headings against tags, README placeholders, length, badge and commands, the root catalog rows, each plugin's icon and its SVG source, and its listing URLs; `-- --offline` skips the tag check.

### 8. Validation

- `claude plugin validate <path>` — validates `marketplace.json` when the folder has one, otherwise `plugin.json`, with its skills, agents and commands.
- `claude plugin validate <path> --strict` — warnings become errors.
- `claude plugin validate <path> --json` — one JSON report, with the same exit codes.
- `claude plugin validate <plugin-dir> --profile directory` — adds the portability checks for a plugin directory.
- `/plugin validate <path>` — the same report inside a session.
- `npm run validate` — `--strict` on every plugin, then on the marketplace root, `.claude` and each mod's tests.
- `npm run validate:claude` — `claude plugin validate --strict .claude`: this repository's own skills, agents and commands.
- `npm run validate:mods` — `claude plugin test` on every plugin with `tests/*.test.ts(x)`.
- `npm run validate:portable` — `--profile directory --strict` on every plugin; outside `validate` while DEBT-003 is open.
- `npm run validate:hooks-catch` — lists each mod gating hook without `.catch`, from `validate --json`; outside `validate` while DEBT-003 is open.
- `npm run check` — every lint, type check and validation.

### 9. Local testing

- `claude --plugin-dir <plugin-dir> plugin list` — shows the plugin loaded as `<name>@inline`.
- `claude --plugin-url <url>` — loads a plugin `.zip` from a URL for one session.
- `claude plugin marketplace add <local-path>` — adds the local marketplace.
- `claude plugin install <plugin>@<marketplace> --scope user|project|local` — installs the plugin at that scope.
- `claude plugin install <plugin> --marketplace <source>` — adds the marketplace and installs in one step.
- `claude plugin install <plugin>@<marketplace> --config <key=value>` — sets a `userConfig` option at install.
- `claude plugin configure <plugin>@<marketplace>` — shows the plugin's options and which are unset.
- `claude plugin enable|disable <plugin> [--scope <scope>]` — turns an installed plugin on or off.
- `claude plugin list --json` — each install with its path, errors and notes.
- `/plugin`, `/plugin manage` — the Discover and Installed tabs inside a session.
- `claude plugin test [dir]` — runs a mod's `*.test.ts(x)` tests.
- `npm run check:install -- --from local <plugin>...` — adds this checkout as a marketplace in a throwaway configuration, installs each plugin, then runs `list --json`, `details`, `validate --strict` and, for a mod, `test` on the installed copy.

### 10. Evaluation

- `claude plugin eval init [name]` — interview that writes an eval suite, from the plugin root; only after the owner approves each case.
- `claude plugin eval <plugin-dir>` — runs every case with and without the plugin; it bills the owner's usage.
- `claude plugin eval <plugin-dir> --case <case> --runs 1 --ablation none --no-publish` — one quick case. Without `--no-publish`, `eval` publishes its HTML report to claude.ai; `--max-cost-usd <usd>` caps the run's spend.

### 11. Documentation

- **Docs:** With the `docs-maintenance` skill, events A small fix and Audit or review: `plugins/<plugin>/README.md`, the root `README.md` and its catalog; a released plugin's change goes through the `plugin-versioning` skill.
- `claude plugin validate <plugin-dir>` — prints an `Advice` block when the README has no install-from-marketplace line; it never changes the exit code.

## Phase C — Release cycle (per version)

### 12. CHANGELOG update

- **Docs:** The `plugin-releases` skill (step 4 and Withdraw a version) writes `plugins/<plugin>/CHANGELOG.md` and the root `CHANGELOG.md` with the `docs-maintenance` skill.
- `npm run release:changelog -- <plugin> [--date YYYY-MM-DD]` — dates `## [Unreleased]` as the version in `plugin.json`, today in UTC by default, and writes the link references; it never writes the notes.

### 13. Versioning and bumping

- **Docs:** The `plugin-versioning` and `plugin-releases` skills write the version's changelog section, the release line in the root `CHANGELOG.md`, the plugin's `README.md` and the catalog row with the `docs-maintenance` skill.
- `claude plugin validate .` — reports an entry version that differs from its `plugin.json`.
- `npm run release:status` — plugins whose version differs from `origin/main`, versions on `origin/main` with no tag, non-semver versions (exit 1) and declared dependencies; run `git fetch origin main` first.
- `npm run release:status -- --next <plugin> --level major|minor|patch` — the next version from the one on `origin/main`.

### 14. Tagging

- `claude plugin tag <plugin-dir> --dry-run` — prints the `<plugin>--v<version>` tag it would create, without creating it.
- `claude plugin tag <plugin-dir>` — creates the annotated tag.
- `claude plugin tag <plugin-dir> --push` — creates and pushes the tag; only with the owner's authorization.
- `/plugin tag <plugin-dir> [--dry-run] [--push] [--force]` — the session form.
- `npm run release:notes -- <plugin> [--tag]` — the GitHub Release body `release.yml` publishes, or with `--tag` the tag name from `plugin.json`.

### 15. Publishing and distribution

- `claude plugin marketplace add nerymurillohnd/the-claude-factory` — user side: adds the marketplace.
- `claude plugin install <plugin>@the-claude-factory` — user side: installs a plugin.
- `claude plugin install <plugin> --marketplace nerymurillohnd/the-claude-factory` — user side: both in one step.
- `npm run check:install -- --from <ref> <plugin>...` — the same install check as stage 9, from `nerymurillohnd/the-claude-factory#<ref>` on GitHub: what users receive from that branch.

### 16. Update delivery

- `claude plugin marketplace update [name]` — user side: refreshes the listings; installed plugins keep their versions.
- `claude plugin update <plugin> [--scope <scope>]` — user side: installs the new version.
- `/reload-plugins` — user side: loads it into a running session.

## Phase D — Operations (ongoing)

### 17. Monitoring and measurement

- `claude plugin details <name>` — projected token cost per plugin.
- `claude plugin list --json --data-size [plugin]` — the size of each plugin's saved data.
- `/plugin stats` — the Stats tab, with `/skill-doctor`.

### 18. Maintenance

- **Docs:** With the `docs-maintenance` skill, events Audit or review and The owner changes a policy: each document from its procedure.
- `claude --version`, `claude plugin <subcommand> --help` — detect CLI changes after an upgrade.
- `claude plugin validate <path> --strict`, `claude plugin eval <plugin-dir>` — regression checks; the eval bills usage.
- `HOME=<tmp> claude plugin init <name> --with skills agents hooks mcp lsp` — the official scaffold, for comparison only, in an isolated `HOME`; delete the folder afterwards.
- `npm run labels:sync` — after adding a plugin, which needs its `plugin: <name>` label.
- `npm run lint:skills` — after a Claude Code upgrade, and after the docs a skill-lint rule cites change.

### 19. Catalog changes

- **Docs:** The `plugin-catalog-changes` skill writes the changelogs, the root catalog, the renamed plugin's `README.md` and `PRIVACY.md` with the `docs-maintenance` skill.
- `claude plugin validate .` — after editing `renames` or entries.
- `claude plugin uninstall <plugin> [--scope <scope>] [--keep-data] [--prune]` — user side: from the last scope it deletes the plugin's options, secrets and data unless `--keep-data` is passed.
- `claude plugin marketplace remove <name>` — user side: uninstalls every plugin from that marketplace and deletes their options, secrets and data.

### 20. Troubleshooting

- `claude plugin validate <path> --json` — the full validation report.
- `claude plugin list --json` — each plugin's `installPath`, errors and notes.
- `claude plugin marketplace list --json` — each marketplace's `installLocation`.
- `/plugin list --enabled|--disabled` — the plugins by state, inside a session.
- `claude plugin details <name>` — what the plugin loaded.
- `claude plugin restore-set-aside <name@marketplace>` — gives back the options and secrets set aside when a managed marketplace replaced a plugin's source; `--discard` deletes them for good.
- `/plugin` (Errors tab), the `/reload-plugins` summary — load errors inside a session.
