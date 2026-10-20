# block-no-verify: a guard against git bypass flags (design)

Date: 2026-10-20. Owner: Nery. Status: approved, implementation replaced on 2026-10-20 (section 3). Supersedes the first draft of this spec, which described a Python parser.

Plugin: `block-no-verify` 0.1.0, new, independent. Hooks rules: `.claude/rules/HOOKS_GATE.md`.

## 1. Goal

Claude runs git through its shell tools, and a failing pre-commit or commit-msg hook invites a shortcut: `--no-verify`, `--no-gpg-sign`, or a `commit.gpgsign=false` override. Each one turns a quality or signing gate into a suggestion. The plugin denies those commands before they run and tells Claude to run the command without the bypass and fix the cause. It installs with one command and needs no per-project configuration.

For anyone who runs Claude Code on a repository with commit gates. Nery's own rule is the first case: commits and tags are SSH-signed and never unsigned.

## 2. Starting point

| Reference | What it gave |
| :-- | :-- |
| `codex-essentials-legacy`, Codex skill 0.2.1 | A small Python parser and a bash test with negative controls. Good for the idea, too narrow for what Claude writes |
| `forestal-mt-plugins` | A regex over `$TOOL_INPUT` in a `"hook"` object: not the documented hook contract |
| `claude-essentials`, skill `block-no-verify` 0.1.3 | A standalone Bash and `jq` handler of about 1600 lines, written and tested earlier by Nery. It denies 66 of the 73 cases an independent reviewer tried to bypass it with, lets harmless heredocs through, and costs about 27 ms per call inside a session |

## 3. Decisions

| Topic | Decision | Why |
| :-- | :-- | :-- |
| Name, version, category | `block-no-verify`, 0.1.0, `security`, display name "Block No Verify", emoji 🛑 | Names what it does |
| Independent or inside `github-operations` | Independent | `github-operations` needs a token and an MCP server; a guard must not require them |
| Components | One `PreToolUse` hook on Bash and PowerShell. No skill, agent, command or MCP | A plugin hook registers itself |
| Mechanism | A Bash handler that reads the payload with `jq`, taken from the earlier skill and registered through `hooks/hooks.json` | It already existed, was tested, and covers far more than the Python port; one language, no interpreter to check, about a third of the time per call |
| Minimum Claude Code | 2.1.295, in the README badge and Requirements | `onFailure` exists from that version |
| Surfaces | Claude Code: yes. Claude app: Cowork sessions only, not chat conversations | Hooks row of the compatibility matrix. Not declared Claude Code-only |
| Evals | None | Nery's decision, not requested |

What changed, and why. The first implementation was a Python port of the Codex parser. Two independent reviews of it found two kinds of fault: shell syntax that hides git (`(git …)`, `if`, `exec`, `$(git …)`) and harmless heredocs that it denied. A rewrite into a one-pass shell scanner followed, doubled the code, and was dropped before any commit. Nery replaced the hook with the handler from the earlier skill, which already did what the reviews asked for. The Python module, its tests and its launcher are gone.

## 4. Behavior

The behavior is what `.github/scripts/tests/block-no-verify/by_path.sh` checks and the README tables describe. In short:

- **Denied:** a git command that runs with `--no-verify` (or an abbreviation git accepts), `-n` in `commit` and `am`, `--no-gpg-sign`, or `commit.gpgsign` or `tag.gpgsign` set to a value git reads as false; `git config` on the signing keys; `core.hooksPath` pointing away from the repository; `HUSKY=0`; `GIT_CONFIG_*`; an inline alias that carries a bypass. Through `sudo`, `env`, `time`, `exec`, subshells, brace groups, `if` and loops, `$(…)`, backticks, `$'…'`, `bash -c`, `eval`, and heredocs that a shell runs.
- **Allowed:** text that only mentions a flag, `-n` in `push`, `merge`, `pull` and `cherry-pick`, heredocs that only write text, and Claude's `git commit -m "$(cat <<'EOF' …)"` form.
- **Answer:** exit 2, one JSON deny object on stdout, the reason on stderr. Claude is told to run the command without the bypass and to fix the hook failure. A payload or command it cannot read is denied with the reason. Without `jq`, a command that could involve git is denied and says why; everything else passes.

Not covered, and listed under Limitations in the README: comma brace lists (`{git,} commit -n`), options between `bash -c` and its script (`bash -c -- '…'`), `xargs git` fed by a heredoc, `source <(…)`, values that come from outside the command, commands a person types in a terminal, and sessions where hooks are turned off.

## 5. Components

```text
plugins/block-no-verify/
  .claude-plugin/plugin.json      name, displayName, version 0.1.0, keywords
  hooks/hooks.json                PreToolUse, matcher Bash|PowerShell, bash "${CLAUDE_PLUGIN_ROOT}/hooks/block-no-verify.sh", onFailure block
  hooks/block-no-verify.sh        the handler, 100755
  README.md  CHANGELOG.md  LICENSE
.github/scripts/tests/block-no-verify/
  by_path.sh                      runs the handler by path under env -i and checks the contract
```

## 6. Requirements

| Tool | Minimum | Install | Why |
| :-- | :-- | :-- | :-- |
| Claude Code | 2.1.295 | the official installer | `onFailure` |
| bash | 3.2 | included in macOS, Linux and Git Bash | runs the handler |
| jq | 1.6 | included in macOS; the package manager on Linux; `winget install jqlang.jq` on Windows | reads the payload |
| git | any, optional | | the handler reads aliases with `git config --get` |

macOS and Linux; Windows only through Git Bash.

## 7. Verification

| What | How |
| :-- | :-- |
| The contract and the behavior | `by_path.sh`: 41 bypasses denied, 21 harmless commands passed, the PowerShell tool, calls without a command, unreadable input, no `jq`, a 20 KB command. Run on Linux, macOS and Windows by CI |
| The test can fail | A handler that always allows, and one that denies with exit 1, each fail it |
| Gates | The Quality Gate's pre-push list |
| Live, `claude -p --plugin-dir plugins/block-no-verify` | A bypass is denied and the repository does not change; a plain commit reaches git's own hook; the same under `bypassPermissions`; a subshell form; the attempt made by a subagent; Claude's heredoc commit form passes and keeps its message; 26 to 39 ms per call |
| Manifest | `claude plugin validate --strict` |
| Review | `plugin-reviewer`; every confirmed finding fixed |
| Claude app | A Cowork session: the hook denies; a chat conversation: the README says it does not run |

## 8. Release

The plugin PR carries the `0.1.0` bump, the `[Unreleased]` notes, `catalog.mjs` and the root `CHANGELOG.md` line, the label `plugin: block-no-verify` from `sync-labels.mjs`, and `Refs #n` only. A push to `plugins/` needs Nery's approval. Merge, then verify the tag and GitHub Release (`RELEASES.md`).

## 9. Out of scope

Server-side enforcement, branch protection and CI checks; blocking `--force`; rewriting a command instead of denying it, which would stop it matching the user's permission rules.
