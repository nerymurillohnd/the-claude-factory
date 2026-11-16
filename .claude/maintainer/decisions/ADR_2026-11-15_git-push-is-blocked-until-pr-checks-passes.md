---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# A PreToolUse hook blocks every git push until pr-checks passes

## Scope

`.claude/hooks/pre-push-checks.sh` and its `PreToolUse` registration in `.claude/settings.json`, for pushes Claude runs through the Bash tool in this repository. Pushes made outside Claude Code, through the GitHub MCP tools or by `release.yml` are out of scope.

## Context and problem statement

The rules already said to keep the plugin dropdowns in step with the catalog and to run the checks before a commit. Even so, [nerymurillohnd/the-claude-factory#109](https://github.com/nerymurillohnd/the-claude-factory/pull/109) reached CI without the dropdowns. An instruction is a request, not a guarantee: the docs say to use a hook for what must hold every time ([features-overview, Hook vs Skill](https://code.claude.com/docs/en/features-overview#claude-md-vs-rules-vs-skills)). How can a branch that would fail `Checks` be kept from reaching GitHub?

## Decision drivers

- The check must run every time, without depending on Claude remembering it.
- A failing push must be stopped with the failed steps' own output, so the fix is immediate.
- Anything the gate can't judge must block, not let the push through.
- Bash commands that are not pushes must not pay for a full run.

## Considered options

- **A `PreToolUse` command hook on Bash, `if: Bash(git *)`, that runs `pr-checks.sh`**: chosen. `Bash(git push*)` was narrower but misses a push with global options such as `git -C <dir> push`.
- **A Git `pre-push` hook**: rejected, because the repository installs no Git hooks and they don't reach cloud sessions (refactor blueprint: husky and `.githooks/` were dropped).
- **Instructions only**: rejected, because they already existed and failed.

## Decision outcome

Chosen option: **a `PreToolUse` hook on Bash**, because it fires on every push Claude runs, in every session that loads the project settings, and blocks the call with exit 2.

### Consequences

- Good, because a push that would fail `Checks` is blocked before it leaves, with the failed steps' output.
- Good, because it fails closed on what may be a push: input that mentions `push` blocks when `jq` is missing, the input is not JSON or the script is missing, and `onFailure: "block"` covers a crash or a timeout of 900 s.
- Bad, because each push waits for the full run (about 73 s on a clean branch).
- Bad, because the hook starts for every git command, and the `if` filter also fires on any Bash command holding `$VAR`, `$()` or backticks ([hooks#bash-if-matching](https://code.claude.com/docs/en/hooks)). The script exits 0 at once when the input never mentions `push`, and otherwise unless the command is `git`, any global options, then `push`.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| A push is detected; `git status`, `git stash push` and a `grep` are not | Piped inputs with an empty project folder | 3 pushes exit 2; `git status`, `git stash push`, `git -C /x log`, a `grep` and non-JSON input without `push` exit 0; without `jq`, a push exits 2 and `git -C /x log` exits 0 | After a change to the pattern |
| A failing branch is blocked with its error, a passing one goes through | The exact handler command, with one form broken, then restored | Exit 2 with `plugin dropdown lacks work-lifecycle`; exit 0 | After a change to the script |
| It fires in a live session | `claude -p --debug-file` asking for a dry-run push, with one form broken | Claude reported the push blocked with the hook's reason | After a Claude Code upgrade that touches hooks |

## More information

- It runs the checks from ADR_2026-11-15_pr-checks-is-the-single-source-of-the-merge-gate, and it coexists with the guard of ADR_2026-11-15_quality-gates-guarded-by-ask-rules-and-a-pretooluse-ask-guard and with the `Bash(git push*)` ask rule. The owner still approves every push.
- The handler runs `bash` on the script by its path, so it doesn't depend on the script's mode (owner decision, 2026-11-15).
