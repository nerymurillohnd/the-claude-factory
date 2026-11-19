# Phase 2: Hooks

How to give a skill a hook once Phase 1 has decided that a rule belongs in a hook: where the hook lives, which event it uses, how its handler reaches the script, and how to check it.

## Contents

- [Gotchas](#gotchas)
- [Choose where the hook lives](#choose-where-the-hook-lives)
- [Choose the event](#choose-the-event)
- [Write the handler](#write-the-handler)
- [Check the hook](#check-the-hook)
- [Examples](#examples)
- [Official sources](#official-sources)

## Gotchas

- A hook in the skill's frontmatter registers only when the user or Claude invokes the skill, so it never sees that invocation. A check on the invocation itself belongs in the plugin's hooks file.
- A skill is invoked by two paths, and each event sees one. `PreToolUse` with the matcher `Skill` fires when Claude invokes the skill; `UserPromptExpansion` fires when the user types `/name`. To gate or log every invocation, hook both.
- `${CLAUDE_SKILL_DIR}` isn't replaced in a hook: reach the script with `${CLAUDE_PLUGIN_ROOT}` in a plugin skill or `${CLAUDE_PROJECT_DIR}` in a project skill; no variable points to a personal skill's folder.
- A failing hook lets the action through: exit code 1, a crash, a wrong path and a timeout all count as non-blocking errors. Only exit 2 blocks, unless the hook sets `onFailure: "block"`.
- A matcher with a `:`, such as `my-plugin:deploy`, is an unanchored regular expression that also matches `my-plugin:deploy-preview`. Write `^my-plugin:deploy$`.
- `if` works only on tool events: on any other event a hook with `if` set never runs, so leave it out there.
- When the organization locks hooks to plugins, a personal or project skill runs without its hooks. A skill that needs its hooks for third parties ships in a plugin installed from a marketplace.
- `hooks` isn't a portable field: an upload to claude.ai or the Skills API rejects a skill that declares it.

## Choose where the hook lives

- Put a check that must hold only once the skill is in use in the skill's `hooks` frontmatter. It runs from the skill's invocation to the end of the session.
- Put a check on the skill's invocation, or one that must hold whether or not the skill runs, in the plugin's hooks file.
- Set `once: true` on a skill hook that must run once per session; only skill frontmatter honors it. Only a successful run removes it, so a run that fails or times out keeps it for the next matching event.
- Declare few hooks with short matchers. The skills of one source, the project, the user's folder or one plugin, share a limit per session, and a skill past it registers none of its hooks.

## Choose the event

| What the skill needs | Event and matcher | Where |
| :-- | :-- | :-- |
| Block or check the user typing `/name`, or add context for it | `UserPromptExpansion`, matcher `^<plugin>:<skill>$` | Plugin hooks file |
| Block or check Claude invoking the skill | `PreToolUse`, matcher `Skill` | Plugin hooks file |
| Check or block a tool call while the skill is in use | `PreToolUse`, matcher the tool name | Skill frontmatter |
| React to a file the skill's work wrote | `PostToolUse`, matcher `Write\|Edit` | Skill frontmatter |
| Keep Claude working until the skill's check passes | `Stop`, no matcher | Skill frontmatter |
| Install or update skill files at session start | `SessionStart`, returning `reloadSkills: true`, because skills are discovered before the hook finishes | Plugin hooks file |

## Write the handler

- Write the hook as a `command` that runs a script the skill or plugin ships. Use `prompt` only for a judgment a script can't make, such as whether the work is complete on `Stop`.
- Reach the script with `${CLAUDE_PLUGIN_ROOT}`.

## Check the hook

1. Run `claude plugin validate` after each change to `hooks`: YAML that doesn't parse loads the skill with no hooks, and nothing in the session says so.
2. Invoke the skill, then run `/hooks`: it lists a skill's hooks only after the skill has been invoked.

## Examples

```yaml
# Weak: a rule written only as skill text; Claude may skip it on later turns
# Never edit CHANGELOG.md by hand.
# Strong: the skill's own hook enforces it from the moment the skill is invoked
hooks:
  PreToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          if: "Edit(CHANGELOG.md)"
          command: python3
          args: ["${CLAUDE_PLUGIN_ROOT}/scripts/block_changelog_edit.py"]

# Weak: a frontmatter hook in the deploy skill itself registers only after /deploy runs, so it
# never gates that invocation, and the unanchored matcher also catches my-plugin:deploy-preview
hooks:
  UserPromptExpansion:
    - matcher: "my-plugin:deploy"
      hooks:
        - type: command
          command: python3
          args: ["${CLAUDE_PLUGIN_ROOT}/scripts/require_approval.py"]
# Strong: in the plugin's hooks file, shown as YAML; UserPromptExpansion covers the typed path
# with an anchored matcher, and PreToolUse on Skill covers Claude's path
hooks:
  UserPromptExpansion:
    - matcher: "^my-plugin:deploy$"
      hooks:
        - type: command
          command: python3
          args: ["${CLAUDE_PLUGIN_ROOT}/scripts/require_approval.py"]
  PreToolUse:
    - matcher: "Skill"
      hooks:
        - type: command
          command: python3
          args: ["${CLAUDE_PLUGIN_ROOT}/scripts/require_approval.py"]

# Weak: CLAUDE_SKILL_DIR is not replaced in a hook, so the script is never found,
# and the failure lets every command through
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: ${CLAUDE_SKILL_DIR}/scripts/guard.sh
# Strong: the plugin root reaches the script, and a failure blocks instead of letting it through
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: python3
          args: ["${CLAUDE_PLUGIN_ROOT}/scripts/guard.py"]
          onFailure: block
```

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Hooks in skills and agents](https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents) when the hook goes in the skill's frontmatter. It gives the format and when the hook registers.
- Read [Limits on skill hooks](https://code.claude.com/docs/en/hooks#limits-on-skill-hooks) when a skill's hooks don't fire after it is invoked. It gives the plugin-only lock, the limit per source and how to tell them apart.
- Read [UserPromptExpansion](https://code.claude.com/docs/en/hooks#userpromptexpansion) when a hook acts on the user typing a skill. It gives the input fields and the decisions.
- Read [Matcher patterns](https://code.claude.com/docs/en/hooks#matcher-patterns) when you write a matcher. It gives what each event matches on and when a matcher is a regular expression.
- Read [Common fields](https://code.claude.com/docs/en/hooks#common-fields) when you set `if` or `once`. It gives each field's rule and default.
- Read [Reference scripts by path](https://code.claude.com/docs/en/hooks#reference-scripts-by-path) when the hook calls a file. It gives the path variables a hook resolves.
- Read [Exit code output](https://code.claude.com/docs/en/hooks#exit-code-output) when you decide how the hook reports. It gives what each exit code does on each event.
- Read [Block the action when a hook fails](https://code.claude.com/docs/en/hooks#block-the-action-when-a-hook-fails) when the hook is a guard. It gives `onFailure` and the events it doesn't cover.
- Read [Reload skills that a hook installs](https://code.claude.com/docs/en/hooks#reload-skills-that-a-hook-installs) when a `SessionStart` hook writes skill files. It gives the `reloadSkills` output.
- Read [Hook not firing](https://code.claude.com/docs/en/hooks-guide#hook-not-firing) when the hook doesn't run. It gives the checks in order.
