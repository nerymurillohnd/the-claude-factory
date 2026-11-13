#!/usr/bin/env bash
set -euo pipefail

# Install plugins of this marketplace into a throwaway Claude Code configuration and check what
# users receive: the install, its load errors, its components, a strict validation and, for a
# mod, its tests. Run it through `npm run check:install -- --from local|<ref> <plugin>...`.
#   --from local  adds the marketplace from the working tree (./)
#   --from <ref>  adds nerymurillohnd/the-claude-factory#<ref> from GitHub
# Plugins install in the order given. Exit 1 on the first failed check, 2 on a usage error.

readonly MARKETPLACE="the-claude-factory"
readonly REPOSITORY="nerymurillohnd/the-claude-factory"

usage() {
  printf 'usage: check-install.sh --from local|<ref> <plugin>...\n' >&2
  exit 2
}

fail() {
  printf 'check-install: %s\n' "$1" >&2
  exit 1
}

run() {
  printf '+ claude %s\n' "$*"
  claude "$@"
}

[[ $# -ge 3 && $1 == --from ]] || usage
from="$2"
shift 2
case "${from}" in
  local) source_arg="./" ;;
  "" | -*) usage ;;
  *) source_arg="${REPOSITORY}#${from}" ;;
esac
for plugin in "$@"; do
  [[ ${plugin} != -* ]] || usage
done
command -v jq > /dev/null || {
  printf 'check-install: jq is required\n' >&2
  exit 2
}

T="$(mktemp -d)"
trap 'rm -rf "${T}"' EXIT
export CLAUDE_CONFIG_DIR="${T}/config" CLAUDE_CODE_PLUGIN_CACHE_DIR="${T}/cache"

run plugin marketplace add "${source_arg}"
for plugin in "$@"; do
  run plugin install "${plugin}@${MARKETPLACE}"
done
printf '+ claude plugin list --json\n'
list="$(claude plugin list --json)"
printf '%s\n' "${list}"

for plugin in "$@"; do
  entry="$(jq -c --arg id "${plugin}@${MARKETPLACE}" '.[] | select(.id == $id)' <<< "${list}")"
  [[ -n ${entry} ]] || fail "${plugin} is not listed as ${plugin}@${MARKETPLACE}"
  if jq -e '(.errors // []) | length > 0' <<< "${entry}" > /dev/null; then
    fail "${plugin} has load errors"
  fi
  # A plugin loaded in place from a local marketplace reports readFromFolder, not installPath.
  path="$(jq -r '.installPath // .readFromFolder // empty' <<< "${entry}")"
  [[ -d ${path} ]] || fail "${plugin} has no install folder"
  run plugin details "${plugin}"
  run plugin validate --strict "${path}"
  if compgen -G "${path}/tests/*.test.ts" > /dev/null || compgen -G "${path}/tests/*.test.tsx" > /dev/null; then
    run plugin test "${path}"
  fi
  version="$(jq -r '.version' <<< "${entry}")"
  printf 'check-install: %s %s ok\n' "${plugin}" "${version}"
done
