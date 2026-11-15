# User settings hooks

Read this in step 5 when the hook goes in `~/.claude/settings.json`.

## Role

You write a personal hook that follows one person into every project on one machine.

## Knowledge

- Scope: every project the user opens on this machine. Not shared and not committed.
- Precedence: hook entries merge across settings levels instead of replacing each other, so user hooks run beside project, local, managed and plugin hooks. `disableAllHooks` is read after precedence, so a project's `"disableAllHooks": false` overrides the user's `true`.
- Trust: in an interactive session, Claude Code holds back hooks from every settings file, this one included, until the user accepts the workspace trust dialog for the folder or a parent whose trust extends to it. A `-p` or SDK session treats the folder as trusted.
- Placeholders: no Claude Code placeholder points at `~/.claude/`. `${CLAUDE_PROJECT_DIR}` points at whichever project the session started in.
- Policy: managed `allowManagedHooksOnly` blocks user hooks.
- Docs: `### Hook locations`, `### Workspace trust` and `### Disable or remove hooks` in `hooks`, and `settings`.

## Gotchas

- Cloud sessions don't read the user's local `~/.claude/settings.json`: a user hook never runs there.
- Exec form expands no shell variable, so `$HOME` in exec form stays literal. A script under `~/.claude/hooks/` needs shell form, or an absolute path written into `command`.

## Rules

- Keep the script in `~/.claude/hooks/` and reference it as `"$HOME/.claude/hooks/<script>"` in shell form.
- Make the hook safe in any project: read `cwd` from the input or test for the files it needs, and exit 0 where it does not apply.
- Tell the user the hook will not run in cloud sessions when they also work there.

## Structure

- File: `~/.claude/settings.json`, under `"hooks"`.
- Template: `assets/user-settings.json`. `$HOME` is ordinary shell expansion in shell form; the docs don't state it for hooks (not verified).
