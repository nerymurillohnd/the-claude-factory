# Learnings

Rules learned the hard way. Follow them; add one line per new lesson.

## Claude Code plugins

- `claude plugin validate --strict` warns on an empty `plugins` array — `validate-claude.sh` drops `--strict` for the marketplace only while the catalog is empty.
- Plugin names starting with `claude-`, `anthropic-`, `cc-plugin-` fail validation; `claude` as a whole word anywhere only warns. Marketplace name `the-claude-factory` is accepted.
- Skills with `disable-model-invocation: true` can't be run by Claude, and the Claude app's `/` and **+ → Skills** menus only list account skills — so in app/cloud sessions repo skills are usable only if Claude may invoke them. Our maintenance skills therefore omit that flag and say "Use only when Nery explicitly asks".
- In cloud sessions the environment's `skillOverrides` blocks Claude from invoking a skill named `verify`; run the gates directly there (commands in `.claude/CLAUDE.md`).
- Project skills appear in the `/` menu only in Claude Code opened on the repo (terminal, desktop Code tab, IDE).
- A project skill named `verify` replaces the bundled `/verify` and Claude Code runs it before each commit.
- Test install loops in an isolated config: `CLAUDE_CONFIG_DIR=$(mktemp -d) claude plugin marketplace add ./`.
- Reading a file inside an installed plugin (cache under `~/.claude/plugins/cache/`) is a read outside the working directory: in default mode it needs permission, from the main session and from subagents. Pre-approve a skill's own files with `allowed-tools: Read(/${CLAUDE_SKILL_DIR}/**)` (the leading `/` makes the expanded path absolute, `//…`); the grant also covers subagents launched in that turn. Observed on 2.1.296, 2026-10-11 — the docs only promise substitution in Bash rules, so re-check it with `/docs-drift-check`.
- Hand a plugin agent its files as absolute paths in the delegation message (the skill body expands `${CLAUDE_SKILL_DIR}`) instead of relying on `skills:` preloading, whose name resolution for plugin skills is undocumented; verified working with the Read grant above.
- Plugin `PostToolUse` hooks with `if: "Write(**/SKILL.md)"` fire when `skill-creator` writes a skill (it uses the Write tool) and inside `claude plugin eval` runs. Verified 2.1.296, 2026-10-11.
- In `claude plugin eval`, the agent can't write under `.claude/` even with `--allow-tools Write` (protected path, denied in dontAsk mode): eval prompts must target paths like `skills/<name>/`. Scaffold scripts run as the user and may write anywhere in the workspace.
- Self-auditing a skill with both lenses converges in passes: each pass surfaces finer gaps once the coarse ones are fixed (skill-diagnostics `audit`: 7 → 6 → 5 → 3 findings, verdict fail → pass with warnings). Run passes until no high finding remains, then fix the rest without another full pass.
- `claude plugin eval` only runs a granted Bash inside the OS sandbox: on Linux install `bubblewrap` and `socat` first (CI too), then grant `--allow-tools Bash`; a wildcard rule like `Bash(*check_skill.py *)` did not match. A skill's own `allowed-tools` cannot widen an eval's grants.
- Eval fixtures that look hard are often easy for Sonnet: the first skill-diagnostics pilot passed 4 of 6 cases without the plugin. Calibrate differences against the baseline arm before trusting a case; reclassify a delta-0 case as a guardrail or rewrite it.
- Hook `if` and permission path rules are anchored: `**/SKILL.md` matches only at or under the session's cwd. Use `//**/SKILL.md` to match anywhere on disk (Windows paths normalize to `/c/...`, so `//**` covers every drive).
- A plugin hook started through a `python3` shebang shows a "hook error" notice on every matching tool call when `python3` is missing; a mode check inside the script can't silence it. Declare it in the README Requirements.
- The Agent Skills reserved words (`claude`, `anthropic`) only matter for uploads and the API; Claude Code instead refuses skill folders named `synced` and names in the `anthropic-skills` namespace.
- A plugin zip uploaded in the Claude app (**Customize** → **Plugins**) also reaches Claude Code as `<plugin>@synced`: a quick way to test the cached, synced path on Nery's Mac before release. Remove that copy after release so it doesn't duplicate the marketplace install. Verified 2026-10-11 with skill-diagnostics (checker, both agents and the Read grant worked).
- In a Cowork task, a plugin skill ran its Python 3 script by path and launched plugin agents (observed 2026-10-12, skill-diagnostics). Still undocumented, so keep runtimes in README Requirements.
- A skill's `allowed-tools` grant ends at the user's next message: a skill that asks the user something mid-run must invoke itself again to get its pre-approvals back.
- Fixing audit findings can plant new ones ("and that ran" made the verdict rule ambiguous): re-run the audit on the fix before calling it done.
- Claude Code's Glob lists gitignored files by default (Grep skips them); users opt out with `CLAUDE_CODE_GLOB_NO_IGNORE=false`. A plugin that lists with Glob gets full coverage and leaves the limit to the user.
- A copied (cached) install for local testing: a local marketplace whose entry uses `{"source":"git-subdir","url":"file:///abs/repo.git","path":"plugins/<name>"}`; a relative-path source loads in place instead. Isolate with `HOME=<tmp>` or `CLAUDE_CONFIG_DIR`.

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
- Moving files from a cloud session to Nery's Mac: tar in the cloud → `device_commit_files` → extract with the device shell.
