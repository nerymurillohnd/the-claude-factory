# Persisting a correction: choosing the mechanism by severity and resistance

Use this when the user reports that Claude keeps doing something wrong, asks to "make sure this doesn't happen again", "persist this", "document this so you stop doing X", or when an audit finds a line that has obviously been fought over (capitals, repetition, "NEVER EVER"). The goal is the lightest mechanism that will actually hold, chosen from evidence, not the reflex of appending another line.

Hook and permission details were checked against the hooks, permissions and settings reference pages on 2026-10-28; re-check them before handing over a configuration snippet.

## 1. Diagnose why the current setup failed

Before choosing a fix, find out what Claude saw when it misbehaved. Read the effective set (checker inventory, `--match` on the files involved) and answer:

| Cause | How to tell | Fix direction |
| :-- | :-- | :-- |
| **Absent** | No instruction covers it anywhere | Add one, in the right home |
| **Not loaded at that moment** | It lives in a scoped rule whose `paths` didn't match, a nested CLAUDE.md not yet loaded, the wrong scope (user file in another machine, CLAUDE.local.md in another worktree), a rule with broken frontmatter, an import that doesn't resolve | Fix scope or timing; this is the most common cause of "it ignores my rule" |
| **Buried** | Long always-on file, the line sits among discoverable or irrelevant content | Shorten the set; restructure |
| **Vague** | No trigger, no concrete action, no artifact ("be careful with migrations") | Rewrite concretely |
| **Contradicted** | Another file, user scope, or the repo itself says otherwise | Resolve the pair |
| **Competes with built-in guidance** | Commit and PR habits (format, attribution, co-author lines) come from Claude Code's own instructions | Set `attribution`, or turn off the built-in git instructions with `includeGitInstructions: false` (this also drops the git status snapshot), then state the team rule once in prose |
| **Needs enforcement by nature** | Zero exceptions, high cost, the model judged "this case is different" | Hook or permission rule |

State the diagnosis in the reply. It is the part of the answer the user cannot get from a generic "I added it to CLAUDE.md".

## 2. Weigh severity and resistance

- **Severity**: what one more occurrence costs. Low (style, wording, preference), medium (rework, noisy diffs, broken local state), high (data loss, irreversible operations, security or secret exposure, shared or production state, money, compliance).
- **Resistance**: how the behavior has responded to instructions. First occurrence; repeated without any instruction; repeated despite a clear, loaded instruction (2–3 times is strong evidence the model is weighing it as a guideline); repeated despite emphasis.
- **Exceptions**: can the right behavior legitimately differ case by case? If yes, it stays a guideline Claude judges. If no, it is a candidate for enforcement.
- **Detectable signal**: does the bad action show up in a tool call you can match (a tool name, a file path, a Bash command pattern, the end of a turn)? Enforcement needs one.

## 3. The ladder

Pick the lowest rung that fits; say why the rungs below are not enough.

1. **Clarify in place** (low severity, first or second occurrence, instruction absent, vague or buried): one concrete line in the correct file (root CLAUDE.md for repo-wide, scoped rule for one area, CLAUDE.local.md or user scope for personal). Fix the cause found in step 1.
2. **Fix scope and timing** (instruction exists but did not load when needed): move it, make it always-on, add a pointer line, repair frontmatter or globs. Adding a second copy elsewhere is not a fix.
3. **Turn a procedure into a skill** (the misbehavior is skipping or reordering steps of a multi-step task): see procedures-to-skills.md.
4. **Enforce deterministically** (high severity, or repeated despite a clear loaded instruction, no legitimate exceptions, and a detectable signal):
   - Block an action before it runs: `PreToolUse` hook (`command` hook exits 2, or returns `permissionDecision: "deny"`), filtered with `matcher` (tool name) and optionally `if` (one permission-rule pattern such as `"Bash(git push *)"`). `if` is best-effort: it only reduces how often the hook starts, so the script must check the condition itself; for a plain allow or deny of a tool or path, prefer `permissions.deny`.
   - Deny access to tools or paths outright: `permissions.deny` (`Edit(...)` for writes, `Read(...)` for reads, `Bash(...)` for commands). Rules match tool calls, not scripts that open files themselves; the sandbox covers that.
   - Require a check before Claude finishes: `Stop` hook (exit 2 keeps Claude working; guard against loops with `stop_hook_active`).
   - Repair after the fact (formatting, generated files): `PostToolUse` hook; it cannot block, the tool already ran.
   - Inject context Claude keeps missing at the start: `SessionStart` or `UserPromptSubmit` hooks add their stdout to context. Prefer fixing the instruction files first.
5. **Outside Claude Code** (must hold for every person and tool): CI checks, branch protection, pre-commit hooks in the repository.

Emphasis is never a rung. Adding IMPORTANT, capitals or repetition makes current models over-apply the line and does not create enforcement.

## 4. What to deliver

- The diagnosis (step 1) and the severity and resistance reading (step 2), in two or three sentences.
- The change to instruction files you made or propose: usually one plain line that also tells Claude what to do instead, in the right home; or the scope fix.
- When enforcement is warranted, a recommendation, not an installation, unless the user asked for it: which event, matcher and `if` filter, what condition blocks, what message Claude gets, which settings file (`.claude/settings.json` for the team, `.claude/settings.local.json` or `~/.claude/settings.json` for one person; path patterns in user settings need `//` or `~/` anchors), and how to test it. Settings and hooks run for everyone who trusts the folder; creating them is the user's call.
- When the user said "remember this": Claude Code saves such requests to auto memory by default, which is personal and machine-local. If the correction should hold for the team or survive on other machines, it belongs in the instruction files or configuration; say which you used.

Example recommendation, after Claude edited an applied migration twice despite a rule:

```text
Diagnosis: the rule lives in .claude/rules/data/migrations.md scoped to "db/**/*.sql", so it loads only
after a migration is opened; Claude decided to "fix" the old migration before reading it, and the rule
arrived too late. Severity high (shared schema history), resistance high (twice, rule present).
Change made: pointer line in CLAUDE.md ("Applied migrations in db/migrations/ are immutable; add a new one").
Recommended, not applied: PreToolUse command hook, matcher "Edit|Write", whose script reads
tool_input.file_path and exits 2 when the file is under db/migrations/ and already tracked in git
(stderr: "Applied migration: create a new migration instead"). A deny rule would also block creating
new migrations, so it is the wrong tool here.
```
