#!/usr/bin/env bash
set -Eeuo pipefail
# Any unexpected failure exits 1, never 2: the skill registers this hook with
# onFailure "block", so a failure blocks the action instead of letting it through.
trap 'exit 1' ERR

# PreToolUse hook of the migrating-plugins skill.
# Asks the user before an action that destroys a plugin, its data or a marketplace:
# plugin CLI removals, deleting plugin or marketplace files, and catalog edits that
# uninstall plugins from users' machines. Everything else passes silently.
# It never blocks on its own: it returns "ask", and the user decides.
# Reads the hook input JSON on stdin and matches it as text, so it needs no JSON parser.
# Outputs only constant JSON; nothing from the input is echoed back.

input="$(cat)"

ask() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"%s"}}\n' "$1"
  exit 0
}

# The Bash command alone, still JSON-escaped, so fields such as cwd never match.
# grep exits 1 when there is no command field (an Edit or Write call) and 2 on an error.
command_status=0
command_text="$(grep -oE '"command"[[:space:]]*:[[:space:]]*"([^"\\]|\\.)*"' <<< "${input}")" || command_status=$?
if [[ ${command_status} -eq 1 ]]; then
  command_text=""
elif [[ ${command_status} -ne 0 ]]; then
  exit 1
fi

# Paths that hold a plugin, a marketplace or Claude Code's plugin state.
plugin_path='(\.claude-plugin|plugin\.json|marketplace\.json|\.claude/plugins|installed_plugins\.json|known_marketplaces\.json|(^|[[:space:]"/'"'"'=])plugins/)'

if grep -Eq -- '"tool_name"[[:space:]]*:[[:space:]]*"(Edit|Write)"' <<< "${input}"; then
  if ! grep -Eq -- 'marketplace\.json' <<< "${input}"; then
    exit 0
  fi
  if grep -Eq -- 'forceRemoveDeletedPlugins' <<< "${input}"; then
    ask "migrating-plugins: this edit touches forceRemoveDeletedPlugins. Once users get the catalog, every plugin removed from it is uninstalled at their next session start, with its options, secrets and data. Approve only if users were told and have exported what they need."
  fi
  if grep -Eq -- 'renames\\?"' <<< "${input}" && grep -Eq -- ':[[:space:]]*null' <<< "${input}"; then
    ask "migrating-plugins: this edit maps a plugin to null in renames, which retires it. It stops loading for users as soon as their catalog updates. Approve only if the retirement is intended."
  fi
  exit 0
fi

if grep -Eq -- 'claude[[:space:]]+plugin[[:space:]]+marketplace[[:space:]]+(remove|rm)([[:space:]]|"|$)' <<< "${command_text}"; then
  ask "migrating-plugins: removing a marketplace uninstalls every plugin installed from it and deletes their options, secrets and data. Approve only if that is intended."
fi

if grep -Eq -- 'claude[[:space:]]+plugin[[:space:]]+(uninstall|remove|rm)([[:space:]]|"|$)' <<< "${command_text}"; then
  ask "migrating-plugins: uninstalling from the last scope deletes the plugin's options, secrets and data directory unless --keep-data is passed. Approve only if that is intended."
fi

if grep -Eq -- 'claude[[:space:]]+plugin[[:space:]]+(prune|autoremove)([[:space:]]|"|$)' <<< "${command_text}" && ! grep -Eq -- '--dry-run' <<< "${command_text}"; then
  ask "migrating-plugins: prune removes auto-installed dependencies and their data. Review the list from --dry-run first, and approve once it looks right."
fi

if grep -Eq -- 'claude[[:space:]]+plugin[[:space:]]+restore-set-aside[[:space:]].*--discard' <<< "${command_text}"; then
  ask "migrating-plugins: --discard permanently deletes the options and secrets that were set aside. Approve only if that is intended."
fi

if grep -Eq -- '(^|[[:space:]";&|(])(rm|rmdir|unlink)[[:space:]]|git[[:space:]]+rm[[:space:]]|find[[:space:]].*-delete' <<< "${command_text}" && grep -Eq -- "${plugin_path}" <<< "${command_text}"; then
  ask "migrating-plugins: this deletes plugin, marketplace or plugin-state files. Approve only if that is intended."
fi

exit 0
