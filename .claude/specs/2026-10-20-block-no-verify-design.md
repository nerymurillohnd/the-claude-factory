# block-no-verify: a guard against git bypass flags (design)

Date: 2026-10-20. Owner: Nery. Status: approved by Nery on 2026-10-20; D1 to D6 of section 10 decided as recommended. Nothing is built: no scaffold, no code, no gate run.

Plugin: `block-no-verify` 0.1.0, new, independent. Hooks rules: `.claude/rules/HOOKS_GATE.md`.

## 1. Goal

Claude runs git through the Bash tool, and a failing pre-commit or commit-msg hook invites a shortcut: `--no-verify`, `--no-gpg-sign`, or a `commit.gpgsign=false` override. Each one turns a quality or signing gate into a suggestion. The plugin denies those commands before they run and tells Claude to run the command without the bypass and fix the cause. It installs with one command and needs no per-project configuration.

For anyone who runs Claude Code on a repository with commit gates. Nery's own rule is the first case: commits and tags are SSH-signed and never unsigned.

## 2. Starting point (measured on 2026-10-20)

| Reference | Strong | Weak |
| :-- | :-- | :-- |
| `codex-essentials-legacy`, Codex skill 0.2.1 (public) | Stdlib Python parser: quote-aware split of command lists, wrapper stripping (`sudo env nice nohup timeout xargs command builtin noglob watch`), leading `VAR=`, case-insensitive `git`, falsy `commit.gpgsign` values (`false no off 0`), `-m` messages skipped, fails closed on unparseable input. An 11-section bash test with negative controls | Codex only; a skill that copies files, so no hook is active; no `-n` (`git commit -n` is `--no-verify`); no `bash -c`; no `git.exe`; no heredoc rule |
| `forestal-mt-plugins` (private) | A skill and a command that explain the problem | A regex over `$TOOL_INPUT` inside a `"hook"` object: not the documented contract (JSON on stdin, a `hooks` array); quoted message text trips it; wrappers, `-n` and `gpgsign=false` slip through |
| `claude-essentials` | `macos-shell-guard` is the model for a guard's README (Permissions, Limitations, fail behavior). Commit `a4e9bd3` shows the heredoc false positive for `git commit -F -` and four bypasses found in its first fix | Has no `block-no-verify`; the file that holds `guard-bash` was not found |
| `codex-essentials-deprecated`, `claude-essentials-deprecated` | | Not found by `gh` or the GitHub MCP (404), by search, or as local clones |

Decision: port the legacy parser and its tests to a Claude Code hook, and close the gaps in the right column.

## 3. Decisions

| Topic | Decision | Why |
| :-- | :-- | :-- |
| Name, version | `block-no-verify`, 0.1.0. Display name "Block No Verify", emoji 🛑 | Names what it does |
| Category | `security` | Guardrails |
| Independent or inside `github-operations` | Independent | `github-operations` needs a token and an MCP server; a guard must not require them |
| Components | One `PreToolUse` hook on Bash. No skill, agent, command or MCP | A plugin hook registers itself; the legacy skill existed only to copy files into Codex |
| Mechanism | Command hook: a Bash launcher plus a Python 3.9 module | Stable, documented hooks API; works in Cowork; no jq. A mod needs 2.1.287 or later and an API that "can change between releases" |
| Minimum Claude Code | 2.1.295, in the README badge and Requirements (`--min-claude-code`) | `onFailure` exists from that version |
| Surfaces | Claude Code: yes. Claude app: Cowork sessions only, not chat conversations | Hooks row of the compatibility matrix. Not declared Claude Code-only |
| Evals | None | Nery's decision, not requested |

## 4. Behavior

### 4.1 What is denied

A command is denied when a `git` invocation in it carries any of these.

| Bypass | Applies to |
| :-- | :-- |
| `--no-verify` | any subcommand: `commit`, `push`, `merge`, `rebase`, `am` and the rest |
| `-n` | `commit` and `am` only, including clusters such as `-nm "x"` and `-anm`. In `push` it is `--dry-run`, in `merge`, `pull` and `rebase` it is `--no-stat`, in `cherry-pick` and `revert` it is `--no-commit` (git 2.56.0 `-h`) |
| `--no-gpg-sign` | any subcommand |
| `-c commit.gpgsign=<falsy>`, `-c tag.gpgsign=<falsy>`, `--config` and the `=` forms | the global option; falsy is `false`, `no`, `off`, `0`, any case |

The same words are checked in these routes:

- Chained commands (`&&`, `||`, `;`, `|`, newline) and each wrapper in the legacy list, alone or stacked.
- Leading `VAR=value` assignments.
- A `git` named in any case, by path (`/usr/bin/git`) or as `git.exe`.
- Global options before the subcommand (`-C <dir>`, `-c k=v`, `--git-dir`, `--work-tree`, `--namespace`, `--no-pager`); the first word after them is the subcommand.
- Quote-spliced names such as `g"i"t`: the filter runs on lexed words, never on raw text (`HOOKS_GATE.md`).
- `bash`, `sh`, `zsh`, `dash` and `ksh` with a `-c` cluster (`-c`, `-lc`, `-ec`): the next word is parsed as a command, to a depth of 3. Deeper nesting is denied as too deep to inspect.
- `eval "<string>"`: its arguments, joined by spaces, are parsed as a command, with the same depth limit.

### 4.2 What is allowed

- Every other git command, and every non-git command.
- Words inside a message: `-m "docs: explain --no-verify"`, `-m` clusters whose value starts with `n` (`-mn` is `-m` with the value `n`).
- A heredoc body is data only when the line is one plain `git commit` or `git tag` reading its message with `-F -`: balanced quotes, no separator, no comment mark, no `-c` option. In any other command the body lines are checked as commands, so `bash <<EOF` and `cat <<EOF | bash` stay denied. This is the rule that `claude-essentials` reached after its first fix let four bypasses through.

### 4.3 Not covered

Each item goes under Limitations in the README.

- `core.hooksPath`, environment switches such as `HUSKY=0`, git aliases, scripts that run git, `eval`, variables and command substitution that build the command.
- Commands a person types in their own terminal.
- The PowerShell tool, when `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` turns it on.
- Sessions with `allowManagedHooksOnly` or `disableAllHooks`.

### 4.4 The answer

When denied, the hook prints one JSON object and exits 0: `hookSpecificOutput` with `hookEventName` `PreToolUse`, `permissionDecision` `deny`, and a reason that names the bypass found and says to run the command without it and fix the hook failure instead. A command that passes prints nothing and exits 0. Unreadable input, a non-object payload or a lexing failure also deny, with the reason stated.

## 5. Components

```text
plugins/block-no-verify/
  .claude-plugin/plugin.json      name, displayName, version 0.1.0, keywords (no version-floor field)
  hooks/hooks.json                the hook below
  hooks/block-no-verify.sh        launcher, 100755
  hooks/block_no_verify.py        parser and answer, Python 3.9, typed
  README.md  CHANGELOG.md  LICENSE
.github/scripts/tests/block-no-verify/
  test_block_no_verify.py         unittest: the legacy cases plus the new ones
  by_path.sh                      runs the launcher by path, as Claude Code does
```

```json
{
  "description": "Denies git commands that skip commit hooks or signing",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/block-no-verify.sh\"",
            "timeout": 10,
            "onFailure": "block"
          }
        ]
      }
    ]
  }
}
```

No `if`, no `statusMessage`. The launcher looks for `python3` and checks it is 3.9 or later. When it is missing or older, it prints `systemMessage` and `additionalContext` that say the guard is inactive and how to install Python, and exits 0. Otherwise it runs the module with the same stdin. The module imports only the standard library and prints nothing but its one JSON object.

## 6. Requirements

| Tool | Minimum | Install | Why |
| :-- | :-- | :-- | :-- |
| Claude Code | 2.1.295 | the official installer | `onFailure` |
| python3 | 3.9 | the OS package manager, `uv python install`, python.org | runs the parser |
| git | any | not needed by the plugin itself | the commands it inspects are git's |

macOS and Linux; Windows only through Git Bash.

## 7. Verification plan

Run after the plugin is built, not while designing.

| What | How |
| :-- | :-- |
| Rules | `test_block_no_verify.py`: the 11 legacy sections, plus `-n` on `commit` and `am`, clusters, `-mn`, `git -C`, `git.exe`, `g"i"t`, `bash -c` at depth 1, 3 and 4, the heredoc cases and the four bypass lines of `claude-essentials`, and fail-closed input |
| The tests can fail | Break each rule on purpose (drop the `-n` rule, drop recursion, widen the heredoc rule) and confirm the matching test fails for that reason |
| By path | `by_path.sh` under `env -i` with an empty `HOME` and a minimal `PATH`; the launcher keeps mode 100755; with `python3` hidden from `PATH`, the notice appears and nothing blocks |
| Gates | The Quality Gate's pre-push list, reported as a table |
| Live, `claude --plugin-dir plugins/block-no-verify` | In a scratch repository: `git commit --no-verify` is denied and Claude retries without it; a plain commit passes; the call from a subagent is denied; both `default` and `bypassPermissions` modes; `sudo git commit --no-verify` denied; the added time per Bash call measured |
| Manifest | `claude plugin validate --strict` on the plugin |
| Review | `plugin-reviewer`; every confirmed finding fixed |
| Claude app | A Cowork session: the hook denies; a chat conversation: the README says it does not run |

## 8. Release

The plugin PR carries the `0.1.0` bump, the `[Unreleased]` notes, `catalog.mjs` and the root `CHANGELOG.md` line, the label `plugin: block-no-verify` from `sync-labels.mjs`, and `Refs #n` only. A push to `plugins/` needs Nery's approval. Merge, then verify the tag and GitHub Release (`RELEASES.md`).

One rule blocks the scaffold: `.claude/CLAUDE.md` forbids a new plugin while a released one lacks its Claude app check, and `svelte-development` 0.1.0 has none. Nery decides before step 2 of `/new-plugin`: wait, or record an exception.

## 9. Out of scope

Server-side enforcement, branch protection, CI checks, and a PowerShell parser. Blocking `--force`. Rewriting a command instead of denying it, which would stop it matching the user's permission rules.

## 10. For Nery's review

| # | Question | Decided (Nery, 2026-10-20) |
| :-: | :-- | :-- |
| D1 | Also deny `-c tag.gpgsign=<falsy>`? It is the same function and covers unsigned tags | Yes |
| D2 | Deny `-c core.hooksPath=…`, which turns hooks off by pointing elsewhere? | No in 0.1.0: legitimate setups exist; listed as a limitation, revisit later |
| D3 | Parse `eval "<string>"` like `bash -c`? | Yes: the recursion exists already |
| D4 | With no `python3`: visible notice and no block (the repo rule), or block every command? | The notice. Blocking would break Claude's shell for the user |
| D5 | Category `security` or `testing` | `security` |
| D6 | Emoji 🛑 | Kept |

## 11. Risks

| Risk | Impact | Mitigation |
| :-- | :-- | :-- |
| The parser misses a route Claude finds | A bypass passes | Section 4.3 states what it does not cover; the tests grow with each report; `if` is not used |
| The parser denies a harmless command | Friction | Negative controls in the tests; the reason names the exact flag found |
| `python3` is absent or older | Guard inactive | The launcher says so on every call; the README lists the prerequisite |
| An update changes the hooks contract | Hook stops working | `onFailure: "block"` makes it loud; the live test reruns after each Claude Code bump |
