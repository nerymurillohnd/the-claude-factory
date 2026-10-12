---
name: safe-migrations
description: Runs database migrations with a check that blocks destructive SQL. Use when the user asks to run, apply or roll back migrations.
disable-model-invocation: true
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/skills/safe-migrations/scripts/check_migration.py"
          args: []
          onFailure: block
---

Running this skill authorizes applying pending migrations to the development database. Still needs the user: any migration against production.

From now on in this session, the `check_migration.py` hook blocks a Bash command that drops a table or column, and blocks the command when the check itself cannot run.

## Steps

1. List the pending migrations.
2. Apply them to the development database, one at a time.
3. After each one, confirm the schema version advanced; stop at the first failure and report it.
