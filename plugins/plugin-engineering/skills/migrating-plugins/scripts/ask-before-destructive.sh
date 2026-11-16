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

# Sets matched to 0 when extended regex $1 matches text $2, and to 1 when it doesn't.
# A grep error exits 1, so it blocks the call instead of reading as "no match".
matched=1
match() {
  local status=0
  grep -Eq -- "$1" <<< "$2" || status=$?
  if [[ ${status} -gt 1 ]]; then
    exit 1
  fi
  matched=${status}
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
# A newline, tab or carriage return arrives as \n, \t or \r: make each one a space, so a
# command on its own line, or after a tab, still has a separator before and after it.
command_text="${command_text//\\n/ }"
command_text="${command_text//\\t/ }"
command_text="${command_text//\\r/ }"

# `claude plugins` is an alias of `claude plugin`.
plugin_cli='claude[[:space:]]+plugins?[[:space:]]+'

# Paths that hold a plugin, a marketplace or Claude Code's plugin state, including a
# bare plugins folder, the whole ~/.claude folder and the plugin path variables.
plugin_path='(\.claude-plugin|plugin\.json|marketplace\.json|\.claude/plugins|installed_plugins\.json|known_marketplaces\.json|CLAUDE_PLUGIN_(ROOT|DATA)|(^|[[:space:]"/'"'"'=*])plugins([/[:space:]"'"'"';&|)]|$)|\.claude([/[:space:]"'"'"';&|)]|$))'

match '"tool_name"[[:space:]]*:[[:space:]]*"(Edit|Write)"' "${input}"
if [[ ${matched} -eq 0 ]]; then
  match 'marketplace\.json' "${input}"
  if [[ ${matched} -ne 0 ]]; then
    exit 0
  fi
  match 'forceRemoveDeletedPlugins' "${input}"
  if [[ ${matched} -eq 0 ]]; then
    ask "migrating-plugins: this edit touches forceRemoveDeletedPlugins. Once users get the catalog, every plugin removed from it is uninstalled at their next session start, with its options, secrets and data. Approve only if users were told and have exported what they need."
  fi
  # An edit inside the renames map often leaves out the "renames" key, so any null asks.
  match ':[[:space:]]*null' "${input}"
  if [[ ${matched} -eq 0 ]]; then
    ask "migrating-plugins: this marketplace.json edit sets a value to null. In renames, null retires a plugin: it stops loading for users as soon as their catalog updates. Approve only if that is intended."
  fi
  exit 0
fi

match "${plugin_cli}"'marketplace[[:space:]]+(remove|rm)([[:space:]]|[";&|]|$)' "${command_text}"
if [[ ${matched} -eq 0 ]]; then
  ask "migrating-plugins: removing a marketplace uninstalls every plugin installed from it and deletes their options, secrets and data. Approve only if that is intended."
fi

match "${plugin_cli}"'(uninstall|remove|rm)([[:space:]]|[";&|]|$)' "${command_text}"
if [[ ${matched} -eq 0 ]]; then
  ask "migrating-plugins: uninstalling from the last scope deletes the plugin's options, secrets and data directory unless --keep-data is passed. Approve only if that is intended."
fi

# Each prune or autoremove call up to the next ;, & or |, so a --dry-run elsewhere in a
# chain, such as "prune --dry-run && prune", doesn't exempt the real one.
prune_status=0
prune_calls="$(grep -oE -- "${plugin_cli}"'(prune|autoremove)([[:space:]][^;&|"]*|[";&|]|$)' <<< "${command_text}")" || prune_status=$?
if [[ ${prune_status} -eq 0 ]]; then
  without_dry_run=0
  grep -Evq -- '--dry-run' <<< "${prune_calls}" || without_dry_run=$?
  if [[ ${without_dry_run} -eq 0 ]]; then
    ask "migrating-plugins: prune removes auto-installed dependencies and their data. Review the list from --dry-run first, and approve once it looks right."
  elif [[ ${without_dry_run} -ne 1 ]]; then
    exit 1
  fi
elif [[ ${prune_status} -ne 1 ]]; then
  exit 1
fi

match "${plugin_cli}"'restore-set-aside[[:space:]].*--discard' "${command_text}"
if [[ ${matched} -eq 0 ]]; then
  ask "migrating-plugins: --discard permanently deletes the options and secrets that were set aside. Approve only if that is intended."
fi

match '(^|[[:space:]";&|(])(rm|rmdir|unlink)[[:space:]]|git[[:space:]]+rm[[:space:]]|find[[:space:]].*-delete' "${command_text}"
if [[ ${matched} -eq 0 ]]; then
  match "${plugin_path}" "${command_text}"
  if [[ ${matched} -eq 0 ]]; then
    ask "migrating-plugins: this deletes plugin, marketplace or plugin-state files. Approve only if that is intended."
  fi
fi

exit 0
