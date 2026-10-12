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

## GitHub

- Issue-form query parameters prefill **text inputs** only, so the `plugin` field is an `input`, not a dropdown.
- Issue-form labels that don't exist in the repo are silently dropped — run `sync-labels.mjs` after adding labels or plugins.
- "Pull requests → Collaborators only" exists natively since 2026-02 (Settings → General → Features).
- The `release.yml` workflow is triggered by `workflow_run` after Validate on `main`; never tag by hand.

## Tooling

- `node --test <dir>` fails on Node ≥ 22 — pass a glob: `node --test ".github/scripts/tests/*.test.mjs"`.
- GitHub heading anchors keep the emoji variation selector (U+FE0F) and start with `-` for emoji headings (`#-catalog`); markdownlint MD051 checks them, and `catalog.mjs` `anchor()` mirrors that.
- Nested code fences inside a markdown example: use `~~~` for the outer fence.
- Don't write literal double-brace placeholders in template comments — `check-repo.mjs` flags them.
- Moving files from a cloud session to Nery's Mac: tar in the cloud → `device_commit_files` → extract with the device shell.
