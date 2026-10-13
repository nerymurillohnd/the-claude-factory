# LSP intelligence plugins: design (v2)

Date: 2026-10-13. Owner: Nery. Status: approved design, pending implementation plan.

Four public plugins for Claude Code users on macOS and Linux (Windows only through Git Bash): `python-lsp-intelligence`, `bash-lsp-intelligence`, `typescript7-lsp-intelligence` and the new `typescript6-lsp-intelligence`. This document replaces the committed 0.1.0 design and the uncommitted working-tree draft.

Design sources, in this order and nothing else: Claude Code Docs (`hooks`, `plugins/components`, `plugins/loading`, `plugins/manifest-reference`, `plugins/code-intelligence`, `skills`, `tools-reference`, `plugins/measure`, `best-practices`), agentskills.io (specification, best practices) and Claude Platform Docs (skill authoring best practices). Tool facts were measured on 2026-10-13 with Claude Code 2.1.296.

## 1. Goal and principles

Each plugin gives Claude three separate things for one language:

| Piece | Role | Rule |
| :-- | :-- | :-- |
| LSP server | Code intelligence tools. Claude prefers them over Grep, Glob and Bash when navigating code | `.lsp.json`; the user installs the binary (Python, Bash) or the plugin pins it (TypeScript) |
| Hook | The user's guarantee: after every edit Claude made, the edited file is formatted, linted and type-checked, and Claude can't move on past findings without seeing them | `PostToolUse`, scoped to the edited file, stderr + exit 2 |
| Skill | Teaches Claude how to work with that language's toolchain: LSP routing, trust checks, impact analysis, configuration, CLI, CI, IDE, installs, fixtures | Never mentions the hook |

Principles that decide every detail below:

- Only what Claude would get wrong without it. No explanations of what Python, LSP or `tsc` are.
- Efficiency: one script per plugin, no state, no session stamps, no shared engine, no `bin/`.
- Every requirement (tool, version, install command) is declared in the plugin README. Plugins install nothing except the TypeScript packages Claude Code installs itself from the plugin's lockfile.
- Hook runtime is one the plugin's users already have: Python 3 for the Python plugin, Node for the Bash plugin (bash-language-server is an npm package) and for both TypeScript plugins. No `jq`.
- Claude Code only (`metadata.surfaces: ["claude-code"]`): the Claude app and cloud sessions don't start language servers.

## 2. Verified facts the design depends on

| Fact | How verified |
| :-- | :-- |
| Claude Code consumes pushed diagnostics (`publishDiagnostics`) after edits; `.lsp.json` `diagnostics` defaults to `true` | docs: manifest-reference `lspServers`, tools-reference LSP tool behavior |
| TypeScript 7.0.2 (`latest` on npm) serves `tsc --lsp --stdio` with **pull diagnostics only**: no `publishDiagnostics` for the opened file, `textDocument/diagnostic` answers TS2322 | runtime probe |
| typescript-language-server 6.0.2 with TypeScript 6.0.3, basedpyright 1.40.2 and bash-language-server 5.8.1 push diagnostics; bash-language-server pushes ShellCheck findings (SC2086, SC2250 with `enable=all`) | runtime probe |
| typescript-language-server honors `initializationOptions.tsserver.path` (`$/typescriptVersion` reports `source: "user-setting"`) | runtime probe + README |
| Claude Code installs a plugin's `package.json` + `package-lock.json` when it caches the plugin: registry packages only, exact versions, `--ignore-scripts`, 60 s limit; not for in-place `--plugin-dir` loads | docs: plugins/loading, Node.js package dependencies |
| `typescript@7.0.2` with a lockfile installs in under 1 s (cached) and 30 MB; only the platform's native package lands | measured |
| One LSP server per extension; a second plugin claiming `.ts` is ignored with a warning in `/plugin` → **Errors** | docs: plugins/components |
| Hook output strings over 10,000 characters are saved to a file with a 2,000-character preview; `PostToolUse` exit 2 shows stderr to Claude; exec form (`args`) substitutes `${CLAUDE_PLUGIN_ROOT}` with no shell | docs: hooks |
| Exit codes: `ruff check --fix` 0 when nothing remains, 1 with remaining violations; `ruff format` 0; `basedpyright --warnings` 1 on findings; `shellcheck` 1 on findings and on an unsupported dialect (SC1071 for zsh); `shfmt -l` 1 when the file would change; `tsc` prints `--listFiles` paths and `file(line,col): error TSnnnn:` lines on stdout | measured |
| A plugin's always-on context cost is its skill names and descriptions; hooks cost nothing | docs: plugins/measure |
| Matchers made of letters and `\|` are exact lists (`Edit\|Write\|Bash`); any other character makes them a regex, so `Edit.*` would also catch `NotebookEdit` | docs: hooks, Matcher patterns |
| `if` holds exactly one permission rule per handler, anchors path patterns to the cwd, and can't see a shebang, so language filtering belongs in the script | docs: hooks, Common fields |
| A `PostToolUse` Bash input carries `tool_response.bashEditDiff.changedFiles` (absolute paths, at most 200) only when `bashEditDiffEnabled` is `true` in user or managed settings, or in auto and bypass modes; it's best effort and never lists git-ignored files. `duration_ms` is optional on both `PostToolUse` and `PostToolUseFailure` | docs: hooks (Bash, PostToolUseFailure), settings-reference |
| `PostToolUseFailure` fires for a Bash command that ran and exited non-zero; its input has `tool_input.command`, `error` and `duration_ms` but no `tool_response`, so no `bashEditDiff` | docs: hooks, PostToolUseFailure input |
| `PostToolBatch` exit 2 stops the agentic loop instead of returning findings to Claude, so it's unfit for a repair loop | docs: hooks, PostToolBatch decision control |
| A hook's JSON `systemMessage` is shown to the user; `PostToolUse` and `PostToolUseFailure` don't discard it | docs: hooks, JSON output and per-event sections |
| Config discovery: ruff uses the closest `pyproject.toml`/`ruff.toml` above the file, then the user-level config, then defaults, and lints `.ipynb` by default; ShellCheck reads the first `.shellcheckrc` from the script's directory upward, then `~/.shellcheckrc`, then XDG, plus `SHELLCHECK_OPTS`; shfmt reads `.editorconfig` from the file's directory upward; basedpyright's CLI reads its config from the **cwd** (a `pyrightconfig.json` in a subfolder is ignored when run from the parent: measured, strict errors became warnings) | ruff docs, ShellCheck manual, `shfmt -h`, measured |

## 3. Plugin layout

```text
plugins/<name>/
├── .claude-plugin/plugin.json      # name, displayName, version, description, author, homepage,
│                                   # repository, license, keywords, metadata.surfaces ["claude-code"]
├── .lsp.json
├── hooks/hooks.json
├── hooks/check.py | hooks/check.mjs
├── skills/<skill>/SKILL.md
├── skills/<skill>/references/toolchain.md
├── skills/<skill>/references/fixtures.md
├── skills/<skill>/references/fixtures/*.fixture
├── README.md · CHANGELOG.md · LICENSE
└── package.json + package-lock.json  # TypeScript plugins only
```

| Plugin | Skill name (kept from 0.1.0; new for TS6) | Hook runtime | Server |
| :-- | :-- | :-- | :-- |
| `python-lsp-intelligence` | `python-lsp-intelligence` | `python3` | `basedpyright-langserver --stdio` (user-installed) |
| `bash-lsp-intelligence` | `bash-lsp-intelligence` | `node` | `bash-language-server start` (user-installed) |
| `typescript7-lsp-intelligence` | `typescript7-lsp-intelligence` | `node` | `node ${CLAUDE_PLUGIN_ROOT}/node_modules/typescript/bin/tsc --lsp --stdio` (pinned 7.0.2) |
| `typescript6-lsp-intelligence` | `typescript6-lsp-intelligence` | `node` | `node ${CLAUDE_PLUGIN_ROOT}/node_modules/typescript-language-server/lib/cli.mjs --stdio`, `initializationOptions.tsserver.path` = `${CLAUDE_PLUGIN_ROOT}/node_modules/typescript/lib/tsserver.js` (pinned 6.0.3 + 6.0.2) |

Removed from every plugin: `bin/`, `scripts/`, `session-stamp.sh`, `verify-fixtures.sh`, `fixtures.json`, the six-reference layout (`controls`, `operations`, `verification`, `diagnostics-and-repair`, `*-navigation`, `sources`). Removed from the repo: `.github/scripts/quality-gate/` and its test (commit `02ecabe`, unused).

## 4. Hook

### 4.1 Registration

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node",
            "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/check.mjs"],
            "timeout": 120,
            "statusMessage": "tsc on the changed files' projects"
          }
        ]
      }
    ],
    "PostToolUseFailure": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node",
            "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/check.mjs"],
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

Python: `"command": "python3"`, `"args": ["${CLAUDE_PLUGIN_ROOT}/hooks/check.py"]`, `PostToolUse` matcher `Edit|Write|NotebookEdit|Bash`, timeout 60. Bash plugin: `node`, `check.mjs`, timeout 60. Matchers stay exact lists (letters and `|` only). Exec form, so paths with spaces need no quoting and nothing goes through a shell. `PostToolUseFailure` on `Bash` exists because a command that writes files and then exits non-zero fires that event instead of `PostToolUse`.

### 4.2 Common behavior

1. Read the JSON on stdin. Anything unreadable: exit 0 silently (the tool already ran; a hook bug must not spam the user).
2. Build the candidate list from `tool_name`:
   - `Edit`, `Write`: `tool_input.file_path`. `NotebookEdit`: `tool_input.notebook_path`.
   - `Bash` (both events): `tool_response.bashEditDiff.changedFiles` when present. Otherwise, files under the project modified since `now − duration_ms − 2 s` (a fixed 30 s window when `duration_ms` is absent). In a git work tree: `git ls-files -z --modified --others --exclude-standard` filtered by mtime. Elsewhere: a walk bounded to the project that prunes `.git`, `node_modules`, `.venv`, `venv`, `dist`, `build` and cache folders. The project is `CLAUDE_PROJECT_DIR`, else `cwd`; the scan never goes above it. A read-only command yields no candidates and exits 0 in milliseconds.
3. Keep the candidates that belong to the language (table below); exit 0 with no output when none do. Files under `node_modules/`, `.venv/`, `venv/`, `site-packages/` are dropped.
4. Run the chain on **those files only** (TypeScript: once per distinct `tsconfig.json`, since one `tsc` run checks the whole program). Python and Bash check at most 20 files per hook run; the rest are listed on stderr as "not checked; run the toolchain on them" and the run exits 2.
5. **The user's configuration wins; the plugin's defaults apply only when there is none.** Each tool runs the way it runs from a terminal, from the session's cwd, with the file path as argument and no policy flags, so it resolves its own configuration natively (nearest config above the file, then the user's global one). Only when that search finds nothing does the hook add the plugin's default flags listed in 4.3. The hook never creates, edits or overrides a config file, never sets an interpreter or environment, and never fails silently.
6. Outcomes (the user always sees that the hook ran on a file of its language):
   - Clean, files unchanged: exit 0 and print `{"systemMessage":"<plugin>: <tools> passed · <files>"}`.
   - Clean, formatter rewrote a file: exit 0 and print the same `systemMessage` plus `{"hookSpecificOutput":{"hookEventName":"<event>","additionalContext":"<tool> reformatted <files>; re-read them before the next edit."}}` in one JSON object, with the event name taken from the input.
   - Findings: print them to stderr, one line per diagnostic as the tool prints it (`path:line:col code message`), then one closing line `Fix these findings in <files> before continuing; do not suppress them.`, and exit 2.
   - Tool missing, crashed, or timed out inside the script: stderr `<tool> is not installed or failed, so <file> was not checked. Install it: <install command>.` and exit 2.
   - Non-language files: exit 0 with no output, so the hook is invisible on every other edit.
7. Cap stderr at 9,000 characters, cutting whole lines and ending with `… N more diagnostics`, so Claude always sees the report inline (Claude Code saves longer output to a file it never asks Claude to read).

Declared limits: `bashEditDiff` is the precise path and the README recommends `bashEditDiffEnabled: true` as an optional improvement, never a requirement; the mtime fallback can include a file another process touched in the window, and both paths miss git-ignored files and anything written by processes outside Claude Code (`FileChanged` watches literal names only, so it doesn't help). `PostToolBatch` was rejected: its exit 2 stops the loop instead of handing findings to Claude.

### 4.3 Per-language chain

| Plugin | Covered files | With the user's config (found natively) | Plugin defaults (no config found) |
| :-- | :-- | :-- | :-- |
| Bash | `.sh`, `.bash`, and extensionless files whose shebang runs `sh` or `bash` (directly or via `env`). `.zsh` or a zsh shebang: exit 0 with `additionalContext` "ShellCheck doesn't support zsh; <file> was not checked" | `shfmt -w <file>` (reads `.editorconfig`), then `shellcheck <file>` on the formatted content (reads `.shellcheckrc` and `SHELLCHECK_OPTS`) | `shfmt -i 2 -ci -bn -w <file>` when no `.editorconfig` exists from the file's directory upward (shfmt ignores EditorConfig once any formatting flag is given, so the flags are added only in that case), then `shellcheck -o all -S style -x -a -P SCRIPTDIR <file>` (every optional check, style severity, follow and check sourced files, resolve `source` paths from the script's directory). "No config" means no `.shellcheckrc`/`shellcheckrc` from the script's directory upward, none in `$HOME` or XDG, and `SHELLCHECK_OPTS` unset |
| Python | `.py`, `.pyi`, `.pyw`; `.ipynb` runs ruff only | `ruff check --fix <file>`, `ruff format <file>` (ruff finds its own config), then `basedpyright -p <nearest pyrightconfig.json or pyproject.toml above the file> <file>` (basedpyright's CLI only looks in the cwd, so `-p` is how its native discovery reaches the file's project) | `ruff check --fix <file>`, `ruff format <file>`, `basedpyright <file>` (basedpyright's built-in `recommended` mode). `--outputjson` is used internally to read diagnostics; the user sees the text form |
| TypeScript 6 / 7 | `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs`, `.cjs` | Plugin's own `tsc --noEmit --listFiles --pretty false -p <nearest tsconfig.json above the file>`. Errors in the edited file first and complete; errors in other files of the program after them (breakage the edit may have caused). If the edited file is absent from `--listFiles`: `additionalContext` "<file> is not part of <tsconfig>'s program; add it to include or files" | Plugin's own `tsc --noEmit <file>` with the compiler's defaults |

Decisions behind the table:

- TypeScript hooks run only the compiler. Formatters and linters (Biome, Prettier, ESLint) belong to the project, and the plugin never imposes one; the skill teaches Claude to run the project's own.
- TypeScript 7's native server gives Claude no diagnostics after edits (pull-only), so the hook is the only source of type errors in that plugin. TypeScript 6's server pushes per-file diagnostics; the hook adds whole-program breakage.
- No PEP 723 environment preparation, no `uv sync`, no interpreter substitution: basedpyright reports what it sees, and the skill teaches `--pythonpath "$(uv python find --script <file>)"` for scripts.
- No invented strictness profile for TypeScript: the project's `tsconfig.json` is the policy. The skill explains how to raise it.
- Every default flag above is the tool's own documented option; the hook never writes a config file to apply them.

## 5. LSP configuration

Unchanged keys: `extensionToLanguage` per language, `startupTimeout` 30000, `maxRestarts` 3, `restartOnCrash` true, `diagnostics` true. Bash keeps `env.GLOB_PATTERN` so `.claude/` and `.github/` scripts are indexed.

TypeScript packaging:

- `typescript7-lsp-intelligence/package.json`: `{"private": true, "dependencies": {"typescript": "7.0.2"}}` + `package-lock.json` (lockfileVersion 3). The lockfile pins the 20 platform packages; npm installs the matching one.
- `typescript6-lsp-intelligence/package.json`: `typescript` `6.0.3`, `typescript-language-server` `6.0.2` + lockfile.
- Both `.lsp.json` and both hooks use `node` plus the path under `${CLAUDE_PLUGIN_ROOT}/node_modules`, never a global `tsc`, so the user's global TypeScript stays untouched and the two plugins never share a compiler.
- README states: enable only one of the two TypeScript plugins (one server per extension); the automatic install needs `npm` on `PATH`; with `--plugin-dir` run `npm ci` in the plugin folder first.

## 6. Skills

### 6.1 Rules

- `SKILL.md` under 200 lines, most important content first (after compaction only the start may survive). References one level deep, each with a "read when" trigger.
- Description: third person, what it does + when, trigger phrases a user would type, under 500 characters. Triggering is measured with several realistic prompts before release.
- Never mentions the hook. Formatting and checking are taught as commands Claude runs on purpose.
- Nothing time-sensitive: tool versions live in the README Requirements, not in the skill.

### 6.2 `SKILL.md` structure (same skeleton in the four)

1. **Principle.** LSP and Grep are complementary: LSP owns questions about code structure; Grep owns questions about text. Route each question to its owner; use both before changing or deleting code.
2. **Roles table.** Where is X defined → `goToDefinition`; who uses X → `findReferences`; type or signature → `hover`; what a file contains → `documentSymbol` before reading it whole; where is X, file unknown → `workspaceSymbol` (always pass `query`); who calls X / what X calls → `prepareCallHierarchy` → `incomingCalls` / `outgoingCalls`; implementations → `goToImplementation`; where a word appears as text (docs, comments, strings, config, scripts) → Grep; safe to delete or rename → both. Required parameters for every operation: `filePath` absolute, `line` 1-based, `character` 1-based.
3. **Positions.** `character` counts UTF-16 code units (an emoji before the symbol counts 2). Raw LSP data is 0-based: add 1 to both.
4. **Trusting a result.** When a result is empty, shows only the definition, or will justify an edit or deletion: position (`hover` at the same spot shows the symbol; "No hover information" means wrong position or no server, never "no usages"), warm-up (repeat until two consecutive results match, max 3), scope (only the working directory is indexed; outside it results are stable and incomplete), freshness (changes made by Bash, git, codegen or formatters may never reach the index: Grep/Read those files), blind spots (below). Only after all five does "no references" mean none. Never delete code on LSP evidence alone.
5. **Blind spots.** Strings and reflection; entry points and config (package scripts, YAML, JSON, TOML, `.env`); framework injection (fixtures, decorators, registries, routes); shell scripts, CI, Makefiles, Dockerfiles; docs, comments, templates.
6. **Language gotchas** (verified on fixtures; each looks complete and is wrong):
   - Python: aliases aren't followed (`from m import f as g`: `findReferences` on `f` lists the import line, not the calls to `g`; run it on `g` too). PEP 723 scripts show false `reportMissingImports` and cascading `reportUnknown*` in the server, which can't see the script's uv environment: check such a script with basedpyright and `--pythonpath "$(uv python find --script <file>)"`.
   - Bash: functions match by name (two unrelated same-named functions share one `findReferences` list, so it over-reports and is never a rename set); extensionless scripts are never indexed; `prepareCallHierarchy` is unsupported.
   - TypeScript (both): only loaded projects are searched (callers in another `tsconfig` project or in a file no `tsconfig` includes are missing and the result is stable across repeats: `hover` one file of each other project first, then re-run `findReferences`); `.astro`, `.svelte`, `.vue`, `.mdx` are invisible (Grep them before any rename or deletion); aliases are followed. TS7 only: the server reports no diagnostics after edits, so run `tsc --noEmit -p <tsconfig>` yourself after a change. TS6: per-edit diagnostics cover the edited file only; a caller broken elsewhere surfaces only in `tsc`.
   - All: `ruff format` and `shfmt -w` rewrite in place; re-read a file after running them and before the next edit.
7. **Impact analysis checklist** (rename, signature change, deletion), copied into working notes: `findReferences` on the definition with the five trust checks (the must-change list); the language-specific steps above; Grep the blind spots (textual mentions listed as optional; any dynamic use blocks a deletion); after the change, run the language's checks (`references/toolchain.md`) and fix what they report.
8. **Diagnostics.** After each Edit/Write the server pushes its diagnostics for the edited file into context (not TS7): fix them as they appear, don't wait.
9. **Pointers.** `references/toolchain.md`: read when configuring, installing, or running the tools by hand, or wiring CI or an IDE. `references/fixtures.md`: read when a check passes code it should flag, or to prove the toolchain works in a project.

### 6.3 References

`toolchain.md` per language: how each tool finds its configuration, the exact CLI invocations for one file and for a project, how to raise strictness in the project's own config, where the project's formatter and linter run (TypeScript), IDE and CI notes, install commands. `fixtures.md` + `fixtures/`: minimal `.fixture` files with one known defect each (clean control, format change, lint finding, type error, references target) and the exact commands plus expected codes, run in a temporary folder next to the project so its configuration applies.

## 7. Hook error handling and limits

| Situation | Behavior |
| :-- | :-- |
| Non-language file, or a Bash command that changed nothing | exit 0, silent |
| Language file, clean | exit 0 with a `systemMessage` naming the tools that passed and the files |
| No user config for a tool | the plugin's default flags from 4.3; never a generated config file |
| Bash command that changed more than 20 language files (Python, Bash) | first 20 checked; the rest listed on stderr as not checked; exit 2 |
| Tool missing | exit 2, one-line stderr with the install command from the README |
| Tool exits with an unexpected code or no parsable output | exit 2, stderr with the raw tail (bounded) and "<file> was not checked" |
| Hook `timeout` reached | Claude Code cancels the hook and shows nothing; the README documents the 60 s / 120 s budgets and that TypeScript 7 is the fast option for large programs |
| Output over 9,000 characters | cut by lines with a count of omitted diagnostics |
| Formatter rewrote the file | `additionalContext` tells Claude to re-read |

## 8. Testing

- Unit tests per hook script in `.github/scripts/tests/`: `lsp-hooks.test.mjs` (Node hooks: Bash, TS6, TS7) and `test_python_check.py` (Python hook), driven by the same fixture files the skills ship. Cases: non-language file, clean file, finding, format rewrite, missing tool (`PATH` emptied), unsupported dialect, no `tsconfig.json`, edited file outside the program, oversized output, Bash input with `bashEditDiff`, Bash input without it (mtime window, git and non-git project, read-only command), `PostToolUseFailure` input, more than 20 changed files. They run in `/verify` and in `validate.yml` (Python suite on the existing matrix).
- `claude plugin validate --strict` on the four plugins (`validate-claude.sh`).
- `/test-installed-plugin <name>` for each: copied install from a git source, load check, and for the TypeScript plugins proof that `node_modules` arrived in the cache and the server starts.
- Skill triggering measured with several realistic prompts (trigger rate), no full eval suite unless Nery decides otherwise.

## 9. Documentation, versions, release

- README per plugin from `.claude/templates/plugin/README.md`: Requirements with exact install commands (`uv tool install basedpyright`, `uv tool install ruff`; `npm install -g bash-language-server`, `brew install shellcheck shfmt` and the Linux equivalents; Node 18+ and npm for the TypeScript plugins), "Claude Code only" and why, Compatibility rows for Skills, Hooks and LSP server, FAQ entries for the known failure modes (binary not on `PATH`, both TypeScript plugins enabled, cloud sessions).
- Versions: Python, Bash, TS7 → 0.2.0 (`Added` hook, `Changed` skill, `Removed` control runner); TS6 → 0.1.0; marketplace minor bump at release time.
- Branch `feat/lsp-intelligence-v2`, draft PR, merge at release. The current working-tree draft is discarded first (`git checkout -- plugins && git clean -fd plugins/`), and the quality-gate engine is deleted in the same branch.

## 10. Out of scope

Stop hooks, session stamps, transcript reading, repair budgets, `bin/` commands, shared engines, `PostToolBatch`, Windows PowerShell (Windows only through Git Bash), PEP 723 environment management, plugin-owned TypeScript strictness profiles, evals suites.

## 11. Scope reminders

- Third-party users and developers on macOS and Linux; Windows only through Git Bash.
- Results and efficiency first; no over-engineering.
- Every required tool, binary or version goes in the README with its install steps.
- Skills never mention hooks; they teach the toolchain and put LSP operations first (operations table, `filePath`/`line`/`character` 1-based, gotchas, five trust checks, Grep blind spots, impact checklist).
