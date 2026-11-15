# Project settings hooks

Read this in step 5 when the hook goes in `.claude/settings.json`, committed with the repository.

## Role

You write a team hook that runs for everyone who clones the repository, on their machines and in their cloud sessions.

## Knowledge

- Scope: one project, shared through the repository with everyone who opens it.
- Precedence: hook entries merge across settings levels; each teammate can add hooks in `.claude/settings.local.json` but cannot remove a committed one, short of `disableAllHooks`.
- Trust: in an interactive session the hooks wait for the workspace trust dialog. In a `-p` or SDK run they run in a folder nobody has trusted, so a repository's committed hooks run on any machine that scripts `claude -p` over it.
- Cloud: the repository's `.claude/settings.json` reaches cloud sessions with the checkout.
- Placeholders: `${CLAUDE_PROJECT_DIR}` is the project root where the session started. It stays there when Claude enters a worktree, while the input's `cwd` follows Claude.
- Policy: managed `allowManagedHooksOnly` blocks project hooks.
- Docs: `### Hook locations`, `### Reference scripts by path`, `### Workspace trust` and `### Security best practices` in `hooks`, and `settings`.

## Gotchas

- A hook committed here runs for every teammate on every platform the team uses: a `.sh` script in exec form fails on a Windows teammate's machine.
- A hook that needs the worktree the session is working in must read `cwd`, not `${CLAUDE_PROJECT_DIR}`.

## Rules

- Commit the script under `.claude/hooks/` with mode 100755, and reference it through `${CLAUDE_PROJECT_DIR}`.
- Check which platforms the team uses (README, CI matrix) and pick the form that runs on all of them.
- Keep the hook to what the whole team agreed on; a personal preference belongs in `references/location-local-settings.md`.

## Structure

- File: `.claude/settings.json`, under `"hooks"`.
- Template: `assets/project-settings.json`, shell form.
