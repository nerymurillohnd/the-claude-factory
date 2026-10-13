#!/usr/bin/env bash
# SessionStart hook: stamp when this session started (or resumed), so the Stop gate can find
# project files modified since then, including Bash-made changes the transcript doesn't list.
#   startup/clear/fork -> create the stamp if missing
#   resume             -> refresh it (earlier changes were gated at earlier stops)
#   compact            -> keep it (the session goes on)
# Stamps live in ${CLAUDE_PLUGIN_DATA}/sessions/<session_id>.stamp; ones older than 30 days are
# pruned. Silent and exit 0 on any error: a missing stamp only disables the scan.
set -uo pipefail

input=$(cat)
command -v jq > /dev/null 2>&1 || exit 0
session_id=$(jq -r '.session_id // empty' <<< "${input}") || exit 0
source=$(jq -r '.source // empty' <<< "${input}") || exit 0
[[ -n ${session_id} && -n ${CLAUDE_PLUGIN_DATA:-} ]] || exit 0

dir="${CLAUDE_PLUGIN_DATA}/sessions"
mkdir -p "${dir}" || exit 0
stamp="${dir}/${session_id}.stamp"
if [[ ${source} == resume || ! -e ${stamp} ]]; then
  touch "${stamp}" || exit 0
fi
find "${dir}" -name '*.stamp' -mtime +30 -delete 2> /dev/null
exit 0
