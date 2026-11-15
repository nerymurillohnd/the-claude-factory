# Local settings hooks

Read this in step 5 when the hook goes in `.claude/settings.local.json`: one person, one project, never committed.

## Role

You write a personal hook for one project that must leave what the team shares untouched.

## Knowledge

- Scope: one person in one project. Claude Code applies it over the committed `.claude/settings.json`, and hook entries from both run.
- Git: Claude Code adds the file to the user's global git excludes the first time it writes it. A file created by hand is not ignored until it is added to `.gitignore`.
- Trust and placeholders: the same as project settings ([location-project-settings.md](location-project-settings.md)).
- Docs: `### Hook locations` in `hooks`, and `### Keep personal settings out of a repository` in `settings`.

## Gotchas

- Writing the file yourself does not ignore it: check `git check-ignore -v .claude/settings.local.json` and, if nothing matches, tell the user and add it to `.gitignore` or their global excludes.
- A script placed under `.claude/hooks/` can still be committed by accident: keep a local hook's script out of the tracked tree, or ignore it too.

## Rules

- Leave `.claude/settings.json` unchanged; merge into an existing `.claude/settings.local.json` instead of replacing it.
- Confirm the file is ignored before you finish, with the command above.

## Structure

- File: `.claude/settings.local.json`, under `"hooks"`.
- Template: [../assets/project-settings.json](../assets/project-settings.json), shell form.
