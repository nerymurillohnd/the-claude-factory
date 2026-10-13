# Learnings

Rules learned the hard way. Follow them; add one line per new lesson.

## Claude Code plugins

- Plugin names starting with `claude-`, `anthropic-`, `cc-plugin-` fail validation; `claude` as a whole word anywhere only warns. Marketplace name `the-claude-factory` is accepted.
- Skills with `disable-model-invocation: true` can't be run by Claude, and the Claude app's `/` and **+ → Skills** menus only list account skills — so in app/cloud sessions repo skills are usable only if Claude may invoke them. Our maintenance skills therefore omit that flag and say "Use only when Nery explicitly asks".
- In cloud sessions the environment's `skillOverrides` blocks Claude from invoking a skill named `verify`; run the gates directly there (commands in `.claude/CLAUDE.md`).
- Project skills appear in the `/` menu only in Claude Code opened on the repo (terminal, desktop Code tab, IDE).
- A project skill named `verify` replaces the bundled `/verify` and Claude Code runs it before each commit.
- Test install loops in an isolated config: `CLAUDE_CONFIG_DIR=$(mktemp -d) claude plugin marketplace add ./`.
- Reading a file inside an installed plugin (cache under `~/.claude/plugins/cache/`) is a read outside the working directory: in default mode it needs permission, from the main session and from subagents. Our plugin skills don't pre-approve it: users' settings decide.
- Hand a plugin agent its files as absolute paths in the delegation message (the skill body expands `${CLAUDE_SKILL_DIR}`) instead of relying on `skills:` preloading, whose name resolution for plugin skills is undocumented.
- Plugin `PostToolUse` hooks with `if: "Write(**/SKILL.md)"` fire when `skill-creator` writes a skill (it uses the Write tool) and inside `claude plugin eval` runs. Verified 2.1.296, 2026-10-11.
- In `claude plugin eval`, the agent can't write under `.claude/` even with `--allow-tools Write` (protected path, denied in dontAsk mode): eval prompts must target paths like `skills/<name>/`. Scaffold scripts run as the user and may write anywhere in the workspace.
- Self-audits never run out of findings: each pass surfaces finer edge cases. Fix only findings that change a verdict, findings or produced files; stop when no such finding remains.
- `claude plugin eval` only runs a granted Bash inside the OS sandbox: on Linux install `bubblewrap` and `socat` first (CI too), then grant `--allow-tools Bash`; a wildcard rule like `Bash(*script.py *)` did not match. A skill's own `allowed-tools` cannot widen an eval's grants.
- Eval fixtures that look hard are often easy for Sonnet: the first skill-diagnostics pilot passed 4 of 6 cases without the plugin. Calibrate differences against the baseline arm before trusting a case; reclassify a delta-0 case as a guardrail or rewrite it.
- Hook `if` and permission path rules are anchored: `**/SKILL.md` matches only at or under the session's cwd. Use `//**/SKILL.md` to match anywhere on disk (Windows paths normalize to `/c/...`, so `//**` covers every drive).
- A plugin hook started through a `python3` shebang shows a "hook error" notice on every matching tool call when `python3` is missing; a mode check inside the script can't silence it. Declare it in the README Requirements.
- The Agent Skills reserved words (`claude`, `anthropic`) only matter for uploads and the API; Claude Code instead refuses skill folders named `synced` and names in the `anthropic-skills` namespace.
- A plugin zip uploaded in the Claude app (**Customize** → **Plugins**) also reaches Claude Code as `<plugin>@synced`: a quick way to test the cached, synced path on Nery's Mac before release. Remove that copy after release so it doesn't duplicate the marketplace install.
- In a Cowork session of the Claude app, a plugin skill ran its Python 3 script by path and launched plugin agents (observed 2026-10-12, skill-diagnostics, from an uploaded zip). Still undocumented, so keep runtimes in README Requirements.
- A skill's `allowed-tools` grant ends at the user's next message: a skill that asks the user something mid-run must invoke itself again to get its pre-approvals back.
- Fixing audit findings can plant new ones ("and that ran" made the verdict rule ambiguous): re-run the audit on the fix before calling it done.
- On macOS, Linux and WSL the main session has no Glob or Grep (Claude uses embedded `bfs`/`ugrep` through Bash); a subagent that lists Glob/Grep and omits Bash gets them. Glob stops at 100 results and lists gitignored files; Grep skips them. Never make a skill depend on Glob for an inventory.
- Terminal sessions sync claude.ai plugins once, in the background, at startup; a session can start on the old synced copy until "Plugins changed. Run /reload-plugins" appears (docs: plugins/loading, synced plugins). On 2026-10-12 a terminal audit ran the old copy right after a re-upload. For synced tests, stamp the test zip with a unique pre-release version, wait for the notice and run `/reload-plugins`.
- Synced skills (`~/.claude/skills/synced/`) re-sync in a running terminal session, every ~40 min while no session is in use since 2.1.293 (was ~10 min); synced plugins (`<plugin>@synced`, `~/.claude/plugins/synced/`) only at startup. Local edits to either are overwritten. With a same-named plugin from a marketplace (or --plugin-dir), Claude Code loads that one and reports the synced copy as not loaded (docs: plugins/loading, Name conflicts) — verify such claims before writing them.
- Synced plugins in the terminal need Claude Code v2.1.273+ and a claude.ai sign-in (not an API key or token); `/plugin` can enable or disable `<name>@synced` but not update or uninstall it (that happens on claude.ai).
- Use `$ARGUMENTS` in a skill body: Claude Code appends an `ARGUMENTS:` line only when no placeholder receives the input.
- `context: fork` skills get no conversation history: wrong for skills that act on what was just discussed, like `audit` after a hook offer. (Subagents can spawn subagents up to three levels; docs: sub-agents, depth limit.)
- Verify every user-doc claim against the docs before writing it: "a duplicate install loads twice" was wrong (a same-named install wins over the synced copy).
- Following symlinks in an inventory: stay inside the skill (a link out is an external dependency, never read), and tell a duplicate path (alias to a listed folder) from a loop (link to an ancestor); otherwise coverage fixes create false "not determinable" verdicts and out-of-scope reads.
- Audit verdicts are not stable across runs: never treat one audit as proof; measure stability with repeated runs on a fixed fixture.
- Never suppress findings to tame an auditor: a rule like "report only what a model would plausibly get wrong" also hides real defects. Report everything, classify by impact and path (normal vs rare), and verify each finding against live official sources instead.
- WebFetch answers through a small model 100k characters at a time (observed 2026-10-12), and Bash output past ~30,000 characters reaches Claude only as a saved file plus a preview (docs: tools-reference, Output limits).
- `/skill-diagnostics:audit` typed in Nery's terminal runs the synced copy (`<plugin>@synced`), not the branch: audit the branch with `claude --plugin-dir plugins/skill-diagnostics`.
- WebFetch can't read GitHub commit history or rendered files (robots.txt / 403, and the CHANGELOG blob page has no content): treat GitHub sources as possibly unreachable and use the docs' own changelog pages instead.
- Make a verifier's "provisional" rule depend on what stayed unverified, not on any source being down; otherwise one always-blocked source makes every verdict provisional.
- Verify every fact an eval rubric asserts against the live docs, and dry-check fixtures with the plugin's own scripts: on 2026-10-12 this caught a rubric (and the plugin) claiming `${CLAUDE_SKILL_DIR}` breaks in an uploaded skill used in Cowork, which the docs contradict, and a false `name-missing` warning for Claude Code.
- An eval case earns its place only if Claude without the plugin, and without our session context, would get it wrong; eval runs are isolated (no CLAUDE.md, memory or other plugins), so the with-arm already answers "does it work without our context".
- A `claude plugin eval` trace (`out/trace.jsonl`, kept with `--keep-temp`) holds subagent tool calls too, each line tagged with `parent_tool_use_id`; a full Read is `"input":{"file_path":"…"}` with no offset or limit. Regex graders on `target: trace` can prove per-file full reads by agents (verified 2026-10-12).
- Plugin options can't be set in an eval run: only allowlisted and `EVAL_*` variables reach it, so `CLAUDE_PLUGIN_OPTION_*` stays unset and hooks run on their defaults.
- Local eval smoke tests follow the docs: `--case … --runs 1 --ablation none` (one arm, one run); the full two-arm, three-run suite belongs in CI.
- Instructions alone don't hold every time: a rule that must always run belongs in a hook (a `Stop` hook in the skill's `hooks` frontmatter works, and `${CLAUDE_PLUGIN_ROOT}` resolves there).
- In `claude -p` without grants, Claude invoking a skill by itself (the Skill tool) is denied; a prompt that starts with the slash command is not. Headless tests of natural triggering need `--allowedTools Skill`.
- `claude plugin eval` authenticates with `CLAUDE_CODE_OAUTH_TOKEN` (a `claude setup-token` subscription token) in CI: verified on the first full run, 2026-10-12.
- Re-running a GitHub Actions job reuses the run's original commit; to evaluate a fix, start a new run (draft then ready, or workflow_dispatch once the workflow is on `main`).
- Write report graders for content, not layout: the model nests a template line as a list ("- **Verification:**" then sub-bullets) and a same-line regex fails a correct report.
- `claude plugin eval` in CI keeps no traces (no `--keep-temp`), and the result JSON holds scores and grader explanations only: to see why a case failed, rerun it locally with `--keep-temp` and read `out/trace.jsonl`.
- Opening a PR that changes a `plugin.json` of a plugin with `evals/` starts `evals.yml` on Nery's plan; say so before opening such a PR.
- Squash-merging two PRs back to back cancels the first merge's Validate run on `main` (concurrency), so its Release is skipped; the next Validate's Release still tags every untagged version.
- `compgen -G "${dir}/*.md"` treats the whole path as a pattern: brackets or backslashes in the project path hide every file. Quote the directory and glob only the file name (`"${dir}"/[0-9]*.md` plus a `-f` check).
- The Claude app's plugin labels (claude.com/docs/plugins/overview): **Add** → **Add marketplace**, **Discover** → **Add**, the plugin's menu → **Remove**, **Check for updates**; not "Install" or "Uninstall".
- A copied (cached) install for local testing: a local marketplace whose entry uses `{"source":"git-subdir","url":"file:///abs/repo.git","path":"plugins/<name>"}`; a relative-path source loads in place instead. Isolate with `HOME=<tmp>` or `CLAUDE_CONFIG_DIR`.
- A plain YAML value holding a colon followed by a space breaks strict YAML ("mapping values are not allowed here"), yet `claude plugin validate --strict` passes it: check skill frontmatter with a strict parser (`uvx --with pyyaml`) after writing a description.
- A "free" `claude -p` load check stays free only with every credential source off: `env -u` the API key, auth token, OAuth token, `ANTHROPIC_PROFILE`, federation and every `CLAUDE_CODE_USE_*` provider variable, and check for an active Anthropic profile in `~/.config/anthropic`, which lives outside `CLAUDE_CONFIG_DIR` (docs: authentication, precedence).
- `CLAUDE_CODE_PLUGIN_CACHE_DIR` moves the whole plugins root (including `installed_plugins.json`) out of `CLAUDE_CONFIG_DIR`: unset it for an isolated install test.

- A `PostToolUse` hook's `systemMessage` reaches the user; in `claude -p --output-format stream-json` it arrives as `{"type":"system","subtype":"informational","content":"PostToolUse:Edit says: …","level":"notice"}` (verified 2026-10-13 with python-lsp-intelligence 0.2.0).
- TypeScript 7.0.2's native server (`tsc --lsp --stdio`) serves pull diagnostics only: `publishDiagnostics` never carries the file's errors, so Claude Code shows no `Found N new diagnostic issues` for it; typescript-language-server 6.0.2, basedpyright 1.40.2 and bash-language-server 5.8.1 push them (LSP probes, 2026-10-13).
- Claude Code installs a plugin's `package.json` + `package-lock.json` into the cache on `claude plugin install` from a git-subdir source (`node_modules/typescript/bin/tsc` present in `cache/<mp>/<plugin>/<version>/`); an in-place `--plugin-dir` load gets no install, run `npm ci --ignore-scripts` there.
- basedpyright's CLI reads `pyrightconfig.json`/`pyproject.toml` from the cwd only, never from the checked file upward; pass `-p <config>` to apply a subproject's config. `ruff check --show-settings <file>` prints `Settings path:` for the config it resolved and no such line when none applies.
- Node's `resolve()` keeps `/var/...` while `process.cwd()` reports `/private/var/...` on macOS: canonicalize with `realpathSync` before comparing paths from a hook event with the project or with `tsc --listFiles` output.
- `claude plugin validate --strict` and the Claude app's packager accept `package.json` and `package-lock.json` at the plugin root; `check-repo.mjs` ignores the local `node_modules` because it lists files with `git ls-files -co --exclude-standard`.
- Measuring skill triggering headless needs `--output-format stream-json --verbose` and a grep on `"name":"Skill","input":{"skill":"<plugin>:…"`; `--output-format json` holds only the result, so every prompt reads 0.
- A bare "Rename X to Y" prompt with no language cue does not trigger a language skill on the first turn (Claude greps first); prompts that name the tool, the error code or the file type trigger it 3/3 (2026-10-13).
- `git commit -F msg -- <paths>` commits only those paths; a plain `git commit` after `git add <path>` also sweeps whatever another session left staged in the same checkout (on 2026-10-13 that put an uncommitted plugin draft on `main`, reverted in `606988a`). Run `git status --short` before every commit.

## GitHub

- Issue-form query parameters prefill **text inputs** only, so the `plugin` field is an `input`, not a dropdown.
- Issue-form labels that don't exist in the repo are silently dropped — run `sync-labels.mjs` after adding labels or plugins.
- "Pull requests → Collaborators only" exists natively since 2026-02 (Settings → General → Features).
- The `release.yml` workflow is triggered by `workflow_run` after Validate on `main`; never tag by hand.
- A plugin registered in `marketplace.json` on `main` is live: users can install it from the branch and `release.yml` tags its version. Build new plugins on a `feat/<name>` branch with a draft PR and merge only at release.

## Tooling

- `node --test <dir>` fails on Node ≥ 22 — pass a glob: `node --test ".github/scripts/tests/*.test.mjs"`.
- GitHub heading anchors keep the emoji variation selector (U+FE0F) and start with `-` for emoji headings (`#-catalog`); markdownlint MD051 checks them, and `catalog.mjs` `anchor()` mirrors that.
- Nested code fences inside a markdown example: use `~~~` for the outer fence.
- Don't write literal double-brace placeholders in template comments — `check-repo.mjs` flags them.
- A `.gitignore` fix never untracks committed files: after widening a pattern, `git rm -r --cached` what it now covers (plugin eval results once shipped this way).
- A Bash command that exits non-zero counts as a failed tool call (`PostToolUseFailure`, not `PostToolUse`), and a failed command's output is cut to ~10,000 characters with no file path: a script Claude reads should exit 0 and report errors in its output. `FileChanged` only watches literal filenames in the cwd and can't pass context to Claude.
- The device shell's delete permission does not survive between turns: re-request it before git commands on Nery's Mac, then clear the `.lock` files the failed command left.
- The repo's only ruff config is the root `ruff.toml` (Nery's strict config: `ALL`, 100 columns, no `target-version`, ruff ≥0.16.10); CI pins ruff in `validate.yml`. Python 3.9 is guarded by mypy `--python-version 3.9` and the 3.9 test matrix, not by ruff.
- The lsp-intelligence Python gate runs `ruff format` after every edit with whatever config ruff discovers: keep one config at the root, or edits get reformatted to another style.
- Moving files from a cloud session to Nery's Mac: tar in the cloud → `device_commit_files` → extract with the device shell.
- A Node "is this the main module" check must `realpathSync(process.argv[1])`: `import.meta.url` is the real path, and macOS temp folders sit under the `/var` → `/private/var` link. Unresolved, `check-repo.mjs` ran nothing and exited 0 in the script tests on the Mac only (CI on Linux stayed green).
- Nery's shell sets `SHELLCHECK_OPTS=-o all -S style`, so local `actionlint` reports style findings that CI (default shellcheck) doesn't.
- The github-ops hook can't parse a Bash command that mixes a heredoc with `git`: write the message to a file in one call, then `git commit -F <file>` alone.
- Biome exits 0 on warnings: gates need `--error-on-warnings` (info never fails). Probe a rule's severity with `--only=<group/rule>` and read the exit code.
- Biome globs in `overrides` are relative to the config: `*.test.js` matches the root only; write `**/*.test.{js,mjs,ts}`. In `files.includes` a folder is `!!**/dist`; elsewhere `!**/dist/**`.
- Never set Biome `json.parser.allowComments: true` repo-wide: it lets a comment into a `.json` manifest that `JSON.parse` rejects (`.jsonc` already allows comments).
- Biome's `noExplicitAny`, `noImplicitAnyLet` and `noEvolvingTypes` don't fire in `.mjs`; `noMagicNumbers` does. `useBlockStatements`' fix is unsafe: apply with `--only=style/useBlockStatements --write --unsafe`, then rerun the script tests.
- `tsc` neither expands CLI globs nor reads a tsconfig when files are passed: use `tsc -p <dir>`. zsh `**` skips dot folders, so name `.github/` explicitly.
- TypeScript 6 `types` defaults to `[]` and only `node_modules/@types` upward from the tsconfig resolves; removed options pass as `false` but fail as `true` (TS5102) and are unknown in TS 7 (TS5023); `showConfig` is CLI-only (TS6266).
- markdownlint-cli2 lints untracked files unless its config sets `"gitignore": true` (`.git/info/exclude` alone doesn't stop it): local plans and scratch workspaces go in `.gitignore`, and the config skips them, so a local run lints what CI lints.
