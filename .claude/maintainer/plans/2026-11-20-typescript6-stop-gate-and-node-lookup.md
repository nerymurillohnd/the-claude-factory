# Plan: typescript6-lsp-intelligence — hard gate on edited-file type errors, and Node found on any install

Status: presented to the owner on 2026-11-20, not approved. Tracked as DEBT-012. Research by two `work-lifecycle:planning-researcher` agents (2026-11-20, Claude Code 2.1.329); facts re-checked against the hooks reference and hooks guide read in full.

## Context

The rebuilt hook (released in typescript6-lsp-intelligence 0.5.0: `hooks/tsc-check.sh`, `hooks/tsc-classify.awk`, PostToolUse Edit|Write + Bash, PostToolBatch, UserPromptSubmit `--new-turn`) **informs** Claude of errors but does not **prevent** it from advancing, and it only finds Node on the inherited PATH. The owner requires both: Claude must not move on while files it edited have type errors, and the hook must find Node whatever way the user installed it, on macOS and Linux — official features first, manual code only where none exists.

## Verified facts that drive the design

- Only `Stop` / `SubagentStop` keep Claude working in the same turn: exit 2 "Prevents Claude from stopping, continues the conversation"; `decision: "block"` + `reason` "Tells Claude why it should continue" (hooks#stop-decision-control). The 8-block cap "resets each time Claude calls a tool" (hooks#stop-input), so a fixing loop is never capped; `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` (env-vars).
- `onFailure` "has no effect" on Stop/SubagentStop (hooks#block-the-action-when-a-hook-fails): a Stop gate must fail closed by itself.
- PostToolUse cannot block ("Shows stderr to Claude; the tool already ran"); PostToolBatch block "stops the agentic loop" (ends the turn). Today `onFailure: "block"` on PostToolBatch ends the turn on a crash or timeout.
- `UserPromptSubmit` also fires on scheduled tasks, background-subagent reports and cross-session messages (hooks#userpromptsubmit): resetting the list there can drop outstanding errors.
- `bashEditDiff` is recorded only in auto/bypassPermissions or with `bashEditDiffEnabled` (user/managed settings only), and is "best effort … not to enforce a policy" (hooks#bash). The official guide's answer for Bash edits: "list modified and untracked files with `git status --porcelain`" (hooks-guide#filter-hooks-with-matchers).
- Hooks "inherit the parent environment" and run `sh -c`; rc files are sourced only for the Bash tool; plugin `bin/` and `CLAUDE_ENV_FILE` reach only the Bash tool. Official remedy for `node: command not found`: put node on the PATH Claude Code starts with (plugins/troubleshooting); Desktop reads the login shell's exports at launch (desktop). Official per-plugin user value: `userConfig` (type `file` allowed) → `CLAUDE_PLUGIN_OPTION_<KEY>` in hook processes (plugins/manifest-reference).
- Prior art (2026): Stop-hook tsc gates (SShadowS/DevOpsWorker, doemefu/furchert-ch, iamfakeguru/agent-md — the last never short-circuits on `stop_hook_active`); node lookup chains in Claude Code plugin hooks (thn-inc/claude-tweaks honours `NVM_DIR`/`FNM_DIR`/`alias/default`; meganemura/steerhook; alibaba/loongsuite-pilot); lefthook checks an override variable, then PATH, then known paths.

## Design

### 1. Gate: Stop and SubagentStop (new)

- `hooks.json`: `Stop` and `SubagentStop` command hooks running the same `tsc-check.sh`, timeout 120.
- The script, on these events, re-checks the ledger (§3) for this key (`session-agent`, `main` for Stop). Errors in ledger files → `{"decision":"block","reason":"<issue list + skill line>"}`, exit 0. No `stop_hook_active` short-circuit: the cap resets on every tool call, so Claude keeps fixing; a stalled loop ends after 8 blocks with Claude Code's own warning.
- Fail closed by hand (onFailure is ignored here): the ERR trap and every "could not verify" path print `decision: "block"` with the reason, on Stop/SubagentStop only.
- A blind run (no `Check time`), a missing or not-6 compiler, or Node not found on Stop: always block with the reason. No markers of our own: Claude Code's native cap ends the turn after 8 consecutive blocks with no tool call in between (owner decision, 2026-11-20), so a machine without tsc never traps a session.
- SubagentStop with an empty ledger (internal agents, agents that edited nothing) → allow silently.

### 2. Keep the per-call and per-batch checks, change one flag

- PostToolUse Edit|Write and Bash: unchanged (exit 2 feedback per call).
- PostToolBatch: `additionalContext` only; set `onFailure` to `"continue"` so a crash surfaces as a hook error instead of ending the turn — Stop is the gate.

### 3. Ledger: cleared by verification, not by prompts

- `${CLAUDE_PLUGIN_DATA}/turns/<key>.list`: files Claude changed and that are not yet verified clean. A run removes a file from the list only when tsc type-checked it (Check time present, file in `--listFiles`) and reported no error in it.
- Remove the UserPromptSubmit `--new-turn` handler (it fires on non-user turns). Keep the instructions `cat` handler. Stale entries still age out after 7 days; deleted files drop out.
- Bash edits: use `bashEditDiff.changedFiles` when present; otherwise, in a git work tree, compare `git status --porcelain=v1 -z` plus `git hash-object` of its TS/JS entries against the snapshot saved by the previous run for the key. A `SessionStart` command hook (new, `--snapshot`) saves the first baseline, so pre-existing user changes are never attributed to Claude. Outside git and without bashEditDiff, Bash edits are not seen; the user message says so once per session.

### 4. Node lookup (first that runs `node --version`)

1. `CLAUDE_PLUGIN_OPTION_NODE_PATH`: new optional `userConfig` option `node_path` (type `file`, title "Path to node", not required).
2. `command -v node` (inherited PATH).
3. Version managers, honouring each tool's variable (sources: each tool's docs/source, read 2026-11-20):
   - Volta `${VOLTA_HOME:-$HOME/.volta}/bin/node` (self-contained shim).
   - nodenv `${NODENV_ROOT:-$HOME/.nodenv}/shims/node` (self-contained shim).
   - mise `${MISE_DATA_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/mise}/shims/node` (symlink to mise; Task 0 checks the auto-install side effect).
   - fnm `<base>/aliases/default/bin/node`, base in fnm's own order: `$FNM_DIR`, `${XDG_DATA_HOME:-$HOME/.local/share}/fnm`, `$HOME/.fnm`, macOS `$HOME/Library/Application Support/fnm`.
   - nvm: in a subshell, `NVM_DIR` default per its README (`$XDG_CONFIG_HOME/nvm` or `$HOME/.nvm`), `. "$NVM_DIR/nvm.sh" --no-use` then `nvm which default` (Task 0 checks it under Bash 3.2 and `set -u`).
   - asdf `${ASDF_DATA_DIR:-$HOME/.asdf}/shims/node` only when `asdf` resolves (its shims `exec asdf exec`).
   - n `${N_PREFIX:-/usr/local}/bin/node`, `$HOME/n/bin/node` (n-install).
4. System prefixes: `/opt/homebrew/bin`, `/usr/local/bin` (nodejs.org pkg, Intel Homebrew), `/home/linuxbrew/.linuxbrew/bin`, `/usr/bin`, `/snap/bin`.

- The found node's folder is prepended to `PATH` for the run, so `node_modules/.bin/tsc` (`#!/usr/bin/env node`) and pnpm `sh` shims work.
- Not found: systemMessage naming every place checked and the fixes (start Claude Code from a terminal where `command -v node` works; Desktop: shell profile + restart; or set the plugin option). On Stop: blocks with the same text, bounded by the native 8-block cap.

## File map

| Path | Change |
| :-- | :-- |
| `plugins/typescript6-lsp-intelligence/hooks/tsc-check.sh` | Stop/SubagentStop gate, ledger by verification, git-snapshot fallback, node lookup |
| `plugins/typescript6-lsp-intelligence/hooks/hooks.json` | add Stop + SubagentStop + SessionStart `--snapshot`; PostToolBatch `onFailure: "continue"`; drop `--new-turn` handler |
| `plugins/typescript6-lsp-intelligence/.claude-plugin/plugin.json` | `userConfig.node_path` |
| `plugins/typescript6-lsp-intelligence/tests/tsc-check.test.mjs` | new cases (below) |
| `plugins/typescript6-lsp-intelligence/CHANGELOG.md` | `[Unreleased]` entries |

## Tasks

- **Task 0 (probes, go/no-go):** (a) `claude -p --plugin-dir` scratch: a Stop block keeps Claude fixing until clean; ends after 8 blocks without tool calls; (b) SubagentStop block keeps a subagent working, internal agents unaffected; (c) `userConfig` optional `file` left blank: no prompt block, variable unset/empty; (d) nvm.sh `--no-use` + `nvm which default` under Bash 3.2-compatible options in a subshell (install nvm in a scratch HOME); (e) mise shim with `env -i` (auto-install off/on); (f) `git status --porcelain -z` snapshot diff detects a `sed -i` edit and ignores pre-existing user changes.
- **Task 1 (tests first, red):** Stop blocks with errors / allows clean / fails closed on crash / blocks on missing tsc, blind run and missing Node; SubagentStop empty ledger allows; ledger keeps an unfixed file across prompts and drops it when clean; Bash edit found via git snapshot without bashEditDiff; node found via each layout in a fake HOME with PATH lacking node (option path, Volta, nodenv, mise, fnm XDG/legacy/macOS, nvm alias default, n, system prefix) and via none → message listing checked paths.
- **Task 2:** implement §1–§4; shfmt, shellcheck, `bash -n`; tests green.
- **Task 3:** hooks.json, plugin.json, CHANGELOG; `claude plugin validate --strict`; `npm run test:plugins`; `check:consistency`; local commit.
- **Task 4:** live check with `claude -p --plugin-dir` (Haiku): an edit leaving a type error → Claude is held by Stop until it fixes it.

## Verification

```bash
shellcheck plugins/typescript6-lsp-intelligence/hooks/tsc-check.sh && bash -n plugins/typescript6-lsp-intelligence/hooks/tsc-check.sh
node --test plugins/typescript6-lsp-intelligence/tests/tsc-check.test.mjs
claude plugin validate --strict plugins/typescript6-lsp-intelligence
npm run test:plugins
```

## Not covered

User interrupts and API errors (Stop does not fire: hooks#stop); a user raising or disabling the block cap; Bash edits outside git without bashEditDiff; the LSP server (`typescript-language-server`) has the same PATH dependency; Windows.
