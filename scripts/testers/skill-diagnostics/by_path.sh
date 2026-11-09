#!/usr/bin/env bash
# Runs skill-diagnostics' gate hooks the way Claude Code does: each command declared in
# hooks/hooks.json, through `bash -c`, with the plugin's environment variables set into temporary
# folders. Prints one line per case and exits non-zero on the first failure. CI does not run it;
# the pre-push gate runs it locally. Needs bash, jq, python3 and the POSIX tools.
set -euo pipefail

root=$(cd "$(dirname "$0")/../../.." && pwd)
plugin="${root}/plugins/skill-diagnostics"
hooks_json="${plugin}/hooks/hooks.json"
record_verdict="${plugin}/skills/skills-best-practices/scripts/record-verdict.py"
base=$(mktemp -d)
trap 'rm -rf "${base}"' EXIT

gate_text_tail='changed. Before you finish this turn, audit it with /skill-diagnostics:skills-best-practices'

# ── Helpers ─────────────────────────────────────────────────────────────────────────────────

current=''
fail() {
  printf 'FAIL %s: %s\n' "${current}" "$1"
  local text
  if [[ -s "${base}/err" ]]; then
    text=$(cat "${base}/err")
    printf '  stderr: %s\n' "${text}"
  fi
  if [[ -s "${base}/out" ]]; then
    text=$(cat "${base}/out")
    printf '  stdout: %s\n' "${text}"
  fi
  exit 1
}

pass() {
  printf 'ok   %s\n' "${current}"
}

# new_case NAME [SUBDIR]: fresh project, config and data folders under a new work folder.
new_case() {
  current=$1
  work="${base}/${1}${2:-}"
  mkdir -p "${work}"
  proj="${work}/project"
  cfg="${work}/config"
  data="${work}/data"
  plugin_root="${plugin}"
  mode='gate'
  mode_set=1
  path_override=''
  mkdir -p "${proj}" "${cfg}"
}

# command_for EVENT: the command hooks.json declares for the event.
command_for() {
  jq -r --arg event "$1" '.hooks[$event][0].hooks[0].command' "${hooks_json}"
}

# run_hook EVENT INPUT: runs the declared command; sets rc, and leaves stdout and stderr in files.
run_hook() {
  local command
  command=$(command_for "$1")
  local -a envs=(
    "CLAUDE_PLUGIN_ROOT=${plugin_root}"
    "CLAUDE_PLUGIN_DATA=${data}"
    "CLAUDE_PROJECT_DIR=${proj}"
    "CLAUDE_CONFIG_DIR=${cfg}"
  )
  if [[ ${mode_set} == 1 ]]; then
    envs+=("CLAUDE_PLUGIN_OPTION_ON_SKILL_WRITE=${mode}")
  fi
  if [[ -n ${path_override} ]]; then
    envs+=("PATH=${path_override}")
  fi
  rc=0
  printf '%s' "$2" \
    | env -u CLAUDE_PLUGIN_OPTION_ON_SKILL_WRITE "${envs[@]}" bash -c "${command}" \
      > "${base}/out" 2> "${base}/err" || rc=$?
}

session_input() {
  jq -cn --arg sid "$1" '{session_id: $sid, hook_event_name: "SessionStart", source: "startup"}'
}

write_input() {
  jq -cn --arg sid "$1" --arg file "$2" \
    '{session_id: $sid, hook_event_name: "PostToolUse", tool_name: "Write",
      tool_input: {file_path: $file, content: "x"}, tool_response: {}}'
}

stop_input() {
  jq -cn --arg sid "$1" '{session_id: $sid, hook_event_name: "Stop", stop_hook_active: false}'
}

# make_skill DIR: a skill folder with SKILL.md and one reference, all dated 2020.
make_skill() {
  mkdir -p "$1/references"
  printf -- '---\nname: demo\ndescription: Demo. Use when asked.\n---\n\nDo it.\n' > "$1/SKILL.md"
  printf 'ref\n' > "$1/references/notes.md"
  touch -t 202001010000 "$1/SKILL.md" "$1/references/notes.md" "$1/references" "$1"
}

start_session() {
  local input
  input=$(session_input "$1")
  run_hook SessionStart "${input}"
  expect_rc 0
  expect_silent
  # The session started in the past, so every later write is newer than its marker.
  if [[ -f "${data}/sessions/$1" ]]; then
    touch -t 202101010000 "${data}/sessions/$1"
  fi
}

record() {
  local input
  input=$(write_input "$1" "$2")
  run_hook PostToolUse "${input}"
}

stop() {
  local input
  input=$(stop_input "$1")
  run_hook Stop "${input}"
}

start_raw() {
  local input
  input=$(session_input "$1")
  run_hook SessionStart "${input}"
}

expect_rc() {
  if [[ ${rc} != "$1" ]]; then
    fail "exit status ${rc}, expected $1"
  fi
}

expect_silent() {
  if [[ -s "${base}/out" ]]; then
    fail 'stdout is not empty'
  fi
}

# expect_json EXPECTED: stdout is exactly one JSON object equal to EXPECTED.
expect_json() {
  local got want
  local count
  got=$(jq -cS . "${base}/out" 2> /dev/null) || fail 'stdout is not JSON'
  count=$(jq -s 'length' "${base}/out")
  if [[ ${count} != 1 ]]; then
    fail "stdout holds ${count} JSON values, expected 1"
  fi
  want=$(printf '%s' "$1" | jq -cS .)
  if [[ ${got} != "${want}" ]]; then
    fail "stdout ${got}, expected ${want}"
  fi
}

gate_context() {
  jq -cn --arg c "Skill $1 ${gate_text_tail} $1 (audit branch); a Stop hook will remind you until a verdict newer than the change is recorded." \
    '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $c}}'
}

stop_context() {
  jq -cn --arg c "Skill $1 changed and has no audit after the change. Run /skill-diagnostics:skills-best-practices on $1 before finishing." \
    '{hookSpecificOutput: {hookEventName: "Stop", additionalContext: $c}}'
}

stop_message() {
  jq -cn --arg m "skill-diagnostics: $1 changed and wasn't audited after the change." \
    '{systemMessage: $m}'
}

expect_gate() {
  local want
  want=$(gate_context "$1")
  expect_json "${want}"
}

expect_stop() {
  local want
  want=$(stop_context "$1")
  expect_json "${want}"
}

expect_given_up() {
  local want
  want=$(stop_message "$1")
  expect_json "${want}"
}

# pending_is SESSION LINES: the pending list holds exactly these lines (empty: no list or empty).
pending_is() {
  local got=''
  if [[ -f "${data}/pending/$1" ]]; then
    got=$(cat "${data}/pending/$1")
  fi
  if [[ ${got} != "$2" ]]; then
    fail "pending list is '${got}', expected '$2'"
  fi
}

stdout_has() {
  if ! grep -Fq -- "$1" "${base}/out"; then
    fail "stdout lacks: $1"
  fi
}

stderr_has() {
  if ! grep -Fq -- "$1" "${base}/err"; then
    fail "stderr lacks: $1"
  fi
}

# ── Cases ───────────────────────────────────────────────────────────────────────────────────

new_case hooks-json-shape
if [[ ! -f ${hooks_json} ]]; then
  fail 'hooks/hooks.json is missing'
fi
bad=$(jq -r '
  def want($f; $t): {type: "command", shell: "bash",
    command: ("bash \"${CLAUDE_PLUGIN_ROOT}/hooks/" + $f + "\""), timeout: $t};
  [ (.hooks.PostToolUse | length == 1 and .[0].matcher == "Write|Edit"
       and (.[0].hooks == [want("skill-changed.sh"; 10)])),
    (.hooks.SessionStart | length == 1 and (.[0] | has("matcher") | not)
       and (.[0].hooks == [want("session-start.sh"; 10)])),
    (.hooks.Stop | length == 1 and (.[0] | has("matcher") | not)
       and (.[0].hooks == [want("audit-gate.sh"; 15)])),
    (.hooks | keys == ["PostToolUse", "SessionStart", "Stop"]) ]
  | all | not' "${hooks_json}")
if [[ ${bad} != false ]]; then
  fail 'hooks.json differs from the specified handlers'
fi
for script in session-start.sh skill-changed.sh audit-gate.sh; do
  first=''
  if [[ -f "${plugin}/hooks/${script}" ]]; then
    first=$(head -n 1 "${plugin}/hooks/${script}")
  fi
  if [[ ! -x "${plugin}/hooks/${script}" ]] || [[ ${first} != '#!/usr/bin/env bash' ]]; then
    fail "${script} lacks the bash shebang or the executable bit"
  fi
done
pass

new_case session-start-cleans-old
mkdir -p "${data}/sessions" "${data}/pending" "${data}/guard/old"
for f in sessions/old pending/old guard/old/key; do
  : > "${data}/${f}"
  touch -t 202001010000 "${data}/${f}"
done
touch -t 202001010000 "${data}/guard/old"
: > "${data}/sessions/recent"
start_raw s1
expect_rc 0
expect_silent
for f in sessions/old pending/old guard/old/key guard/old; do
  if [[ -e "${data}/${f}" ]]; then
    fail "${f} older than 7 days was kept"
  fi
done
if [[ ! -f "${data}/sessions/s1" ]] || [[ ! -f "${data}/sessions/recent" ]]; then
  fail 'session marker missing, or a recent marker was deleted'
fi
pass

new_case record-skill-md-edit
start_session s1
make_skill "${proj}/skills/demo"
record s1 "${proj}/skills/demo/SKILL.md"
expect_rc 0
expect_gate "${proj}/skills/demo"
pending_is s1 "${proj}/skills/demo"
record s1 "${proj}/skills/demo/SKILL.md"
expect_rc 0
expect_silent
pending_is s1 "${proj}/skills/demo"
pass

new_case edit-reference-in-skill
start_session s1
make_skill "${proj}/skills/demo"
input=$(jq -cn --arg f "${proj}/skills/demo/references/notes.md" \
  '{session_id: "s1", hook_event_name: "PostToolUse", tool_name: "Edit",
    tool_input: {file_path: $f, old_string: "a", new_string: "b"}}')
run_hook PostToolUse "${input}"
expect_rc 0
expect_gate "${proj}/skills/demo"
pending_is s1 "${proj}/skills/demo"
pass

new_case edit-outside-skill
start_session s1
mkdir -p "${proj}/src"
: > "${proj}/src/a.txt"
record s1 "${proj}/src/a.txt"
expect_rc 0
expect_silent
pending_is s1 ''
stop s1
expect_rc 0
expect_silent
pass

new_case skip-plugin-cache
start_session s1
make_skill "${cfg}/plugins/cache/m/p/1.0.0/skills/x"
touch "${cfg}/plugins/cache/m/p/1.0.0/skills/x/SKILL.md"
record s1 "${cfg}/plugins/cache/m/p/1.0.0/skills/x/SKILL.md"
expect_rc 0
expect_silent
pending_is s1 ''
pass

new_case skip-synced
start_session s1
make_skill "${cfg}/skills/synced/x"
touch "${cfg}/skills/synced/x/SKILL.md"
record s1 "${cfg}/skills/synced/x/SKILL.md"
expect_rc 0
expect_silent
pending_is s1 ''
stop s1
expect_rc 0
expect_silent
pending_is s1 ''
pass

new_case skip-own-plugin-root
plugin_root="${work}/plugin root"
mkdir -p "${plugin_root}"
cp -R "${plugin}/hooks" "${plugin_root}/hooks"
start_session s1
make_skill "${plugin_root}/skills/own"
record s1 "${plugin_root}/skills/own/SKILL.md"
expect_rc 0
expect_silent
pending_is s1 ''
pass

new_case stop-pending
start_session s1
make_skill "${proj}/skills/demo"
record s1 "${proj}/skills/demo/SKILL.md"
stop s1
expect_rc 0
expect_stop "${proj}/skills/demo"
pass

new_case stop-after-newer-verdict
start_session s1
make_skill "${proj}/skills/demo"
record s1 "${proj}/skills/demo/SKILL.md"
python3 "${record_verdict}" --data-dir "${data}" "${proj}/skills/demo" pass > /dev/null
stop s1
expect_rc 0
expect_silent
pending_is s1 ''
pass

new_case stop-third-unchanged
start_session s1
make_skill "${proj}/skills/demo"
record s1 "${proj}/skills/demo/SKILL.md"
stop s1
expect_stop "${proj}/skills/demo"
input=$(jq -cn '{session_id: "s1", hook_event_name: "Stop", stop_hook_active: true}')
run_hook Stop "${input}"
expect_stop "${proj}/skills/demo"
input=$(jq -cn '{session_id: "s1", hook_event_name: "Stop", stop_hook_active: true}')
run_hook Stop "${input}"
expect_rc 0
expect_given_up "${proj}/skills/demo"
pending_is s1 ''
stop s1
expect_rc 0
expect_silent
pass

new_case change-after-guard-resets
start_session s1
make_skill "${proj}/skills/demo"
record s1 "${proj}/skills/demo/SKILL.md"
stop s1
stop s1
expect_stop "${proj}/skills/demo"
# The guard was written in the past; the change now is newer than it.
find "${data}/guard" -type f -exec touch -t 202101010000 {} +
touch "${proj}/skills/demo/references/notes.md"
stop s1
expect_stop "${proj}/skills/demo"
stop s1
expect_stop "${proj}/skills/demo"
stop s1
expect_given_up "${proj}/skills/demo"
pass

new_case bash-written-skill
start_session s1
make_skill "${proj}/made-by-bash"
touch "${proj}/made-by-bash/SKILL.md"
stop s1
expect_rc 0
expect_stop "${proj}/made-by-bash"
pending_is s1 "${proj}/made-by-bash"
pass

new_case mode-suggest
mode='suggest'
start_session s1
make_skill "${proj}/skills/demo"
record s1 "${proj}/skills/demo/SKILL.md"
expect_rc 0
event=$(jq -r '.hookSpecificOutput.hookEventName' "${base}/out")
if [[ ${event} != PostToolUse ]]; then
  fail 'suggest output is not PostToolUse additionalContext'
fi
stdout_has "/skill-diagnostics:skills-best-practices ${proj}/skills/demo"
stdout_has 'offer'
stop s1
expect_rc 0
expect_silent
pass

new_case mode-off
mode='off'
make_skill "${proj}/skills/demo"
start_raw s1
expect_rc 0
expect_silent
touch "${proj}/skills/demo/SKILL.md"
record s1 "${proj}/skills/demo/SKILL.md"
expect_rc 0
expect_silent
stop s1
expect_rc 0
expect_silent
if [[ -e ${data} ]]; then
  fail 'off mode wrote plugin data'
fi
pass

new_case mode-unset-is-gate
mode_set=0
start_session s1
make_skill "${proj}/skills/demo"
record s1 "${proj}/skills/demo/SKILL.md"
expect_rc 0
expect_gate "${proj}/skills/demo"
stop s1
expect_stop "${proj}/skills/demo"
pass

new_case non-json-input
for event in SessionStart PostToolUse Stop; do
  run_hook "${event}" 'not json {'
  expect_rc 1
  expect_silent
  if [[ ! -s "${base}/err" ]]; then
    fail "${event}: nothing on stderr"
  fi
done
pass

new_case missing-jq
fakebin="${work}/bin"
mkdir -p "${fakebin}"
for tool in bash env cat mkdir find sed mv rm touch tr dirname head; do
  target=$(command -v "${tool}")
  ln -s "${target}" "${fakebin}/${tool}"
done
path_override="${fakebin}"
make_skill "${proj}/skills/demo"
for event in SessionStart PostToolUse Stop; do
  case "${event}" in
    SessionStart) input=$(session_input s1) ;;
    PostToolUse) input=$(write_input s1 "${proj}/skills/demo/SKILL.md") ;;
    *) input=$(stop_input s1) ;;
  esac
  run_hook "${event}" "${input}"
  expect_rc 1
  expect_silent
  stderr_has 'jq'
done
pass

new_case spaces-in-path '/dir with spaces/ñandú é'
proj="${work}/my project"
data="${work}/plugin data"
mkdir -p "${proj}"
start_session s1
skill="${proj}/skills/my skill ü"
make_skill "${skill}"
record s1 "${skill}/SKILL.md"
expect_gate "${skill}"
pending_is s1 "${skill}"
stop s1
expect_stop "${skill}"
python3 "${record_verdict}" --data-dir "${data}" "${skill}" pass-with-warnings > /dev/null
stop s1
expect_rc 0
expect_silent
pending_is s1 ''
pass

new_case pending-skill-deleted
start_session s1
make_skill "${proj}/skills/demo"
make_skill "${proj}/skills/no-skill-md"
record s1 "${proj}/skills/demo/SKILL.md"
record s1 "${proj}/skills/no-skill-md/SKILL.md"
rm -rf "${proj}/skills/demo"
rm -f "${proj}/skills/no-skill-md/SKILL.md"
stop s1
expect_rc 0
expect_silent
pending_is s1 ''
pass

new_case scan-prunes-heavy-dirs
start_session s1
for heavy in .git node_modules .venv venv __pycache__ dist build target; do
  make_skill "${proj}/${heavy}/pkg/skills/x"
  touch "${proj}/${heavy}/pkg/skills/x/SKILL.md"
done
make_skill "${cfg}/skills/user-skill"
touch "${cfg}/skills/user-skill/SKILL.md"
stop s1
expect_rc 0
expect_stop "${cfg}/skills/user-skill"
pending_is s1 "${cfg}/skills/user-skill"
pass

new_case verdict-from-other-session
start_session a
make_skill "${proj}/skills/demo"
record a "${proj}/skills/demo/SKILL.md"
python3 "${record_verdict}" --data-dir "${data}" "${proj}/skills/demo" fail > /dev/null
start_session b
record b "${proj}/skills/demo/SKILL.md"
stop b
expect_rc 0
expect_silent
touch -t 203001010000 "${proj}/skills/demo/SKILL.md"
record b "${proj}/skills/demo/SKILL.md"
stop b
expect_stop "${proj}/skills/demo"
stop a
expect_stop "${proj}/skills/demo"
pass

new_case windows-backslash-path
start_session s1
make_skill "${proj}/skills/demo"
forward="${proj}/skills/demo/SKILL.md"
backslashed=${forward//\//\\}
record s1 "${backslashed}"
expect_rc 0
expect_gate "${proj}/skills/demo"
pending_is s1 "${proj}/skills/demo"
pass

new_case subagent-write
start_session s1
make_skill "${proj}/skills/demo"
input=$(jq -cn --arg f "${proj}/skills/demo/SKILL.md" \
  '{session_id: "s1", hook_event_name: "PostToolUse", tool_name: "Write",
    agent_id: "agent-1", agent_type: "general-purpose", tool_input: {file_path: $f}}')
run_hook PostToolUse "${input}"
expect_rc 0
expect_gate "${proj}/skills/demo"
pending_is s1 "${proj}/skills/demo"
pass

new_case suggest-once-per-session
mode='suggest'
start_session s1
make_skill "${proj}/skills/demo"
record s1 "${proj}/skills/demo/SKILL.md"
stdout_has "${proj}/skills/demo"
record s1 "${proj}/skills/demo/references/notes.md"
expect_rc 0
expect_silent
start_session s2
record s2 "${proj}/skills/demo/SKILL.md"
stdout_has "${proj}/skills/demo"
pass

echo 'all cases passed'
