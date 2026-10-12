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
- Moving files from a cloud session to Nery's Mac: tar in the cloud → `device_commit_files` → extract with the device shell.
