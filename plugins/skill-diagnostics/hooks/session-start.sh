#!/usr/bin/env bash
# skill-diagnostics SessionStart hook. Writes the session marker
# ${CLAUDE_PLUGIN_DATA}/sessions/<session_id>, whose time is the session start: the Stop hook
# gates every skill folder changed after it. Deletes the plugin's session state older than 7 days.
# Prints nothing. In "off" mode it does nothing at all.
# Needs bash 3.2+ and jq. When a command fails it writes the error to stderr and exits 1.
set -euo pipefail
export LC_ALL=C
unset CDPATH

# Any failure exits 1, never 2: exit 2 would block, and this hook only informs.
trap '[[ $? -eq 0 ]] || { echo "skill-diagnostics: session-start.sh failed" >&2; exit 1; }' EXIT

die() {
  printf 'skill-diagnostics: %s\n' "$1" >&2
  exit 1
}

mode=${CLAUDE_PLUGIN_OPTION_ON_SKILL_WRITE:-gate}
if [[ ${mode} == off ]]; then
  exit 0
fi

data=${CLAUDE_PLUGIN_DATA:-}
if [[ -z ${data} ]]; then
  die 'CLAUDE_PLUGIN_DATA is not set'
fi

input=$(cat)
if ! printf '%s' "${input}" | jq -e 'type == "object"' > /dev/null; then
  die 'cannot read the hook input: jq is missing or the input is not a JSON object'
fi
session_id=$(printf '%s' "${input}" | jq -r '.session_id // empty | strings')
source_event=$(printf '%s' "${input}" | jq -r '.source // empty | strings')
case "${session_id}" in
  '' | . | .. | *[!A-Za-z0-9._-]*) die 'the hook input has no usable session_id' ;;
  *) ;;
esac

# Old state: files under sessions/, pending/ and guard/ untouched for more than 7 days, then the
# guard folders left empty. A failed cleanup is reported and does not stop the marker.
for folder in sessions pending guard; do
  if [[ -d "${data}/${folder}" ]]; then
    find "${data}/${folder}" -mindepth 1 -type f -mtime +7 -exec rm -f {} + \
      || printf 'skill-diagnostics: could not remove old files under %s\n' "${data}/${folder}" >&2
  fi
done
if [[ -d "${data}/guard" ]]; then
  find "${data}/guard" -mindepth 1 -maxdepth 1 -type d -empty -exec rmdir {} + \
    || printf 'skill-diagnostics: could not remove empty folders under %s\n' "${data}/guard" >&2
fi

# The marker keeps its time through a compaction, which happens inside the session; a startup,
# resume or clear starts it again.
mkdir -p "${data}/sessions"
marker="${data}/sessions/${session_id}"
if [[ ${source_event} != compact ]] || [[ ! -f ${marker} ]]; then
  touch "${marker}"
fi
exit 0
