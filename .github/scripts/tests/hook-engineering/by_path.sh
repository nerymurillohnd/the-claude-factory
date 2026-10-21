#!/usr/bin/env bash
# Runs the hook-development skill's scripts by path, the way its SKILL.md tells Claude to:
# `python3 <path>` and `bash <path>`, from a folder outside the repository, with whatever
# python3 and bash are first on PATH. No network: hook-changes.sh runs with a stub curl.
# Exits non-zero on the first failure.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../../.." && pwd)
scripts="${root}/plugins/hook-engineering/skills/hook-development/scripts"
work=$(mktemp -d)
trap 'rm -rf "${work}"' EXIT

fail() {
  echo "FAIL: $*"
  exit 1
}

# Fails with the message and the contents of a captured output file.
fail_with() {
  echo "FAIL: $1"
  cat "$2"
  exit 1
}

python=$(command -v python3)
version=$(python3 --version)
shell=$(command -v bash)
echo "python3: ${python} (${version})"
echo "bash: ${shell} (${BASH_VERSION})"

# 1. Committed as executable, so they also run by path after a clone or install.
for script in hook-changes.sh lint-hooks-config.py probe-hook.py; do
  mode=$(git -C "${root}" ls-files -s -- "${scripts#"${root}"/}/${script}" | cut -d' ' -f1)
  [[ ${mode} == 100755 ]] || fail "${script} is '${mode}', not 100755"
done
echo "modes: 100755"

cd "${work}"

# 2. The linter: a clean file exits 0, a wrong event name exits 1.
printf '{"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"x","timeout":10}]}]}}' > ok.json
printf '{"hooks":{"stop":[]}}' > bad.json
python3 "${scripts}/lint-hooks-config.py" ok.json > /dev/null || fail "linter rejected a clean file"
if python3 "${scripts}/lint-hooks-config.py" bad.json > lint.out; then
  fail "linter accepted an unknown event"
fi
grep -q "unknown event 'stop'" lint.out || fail_with "linter output:" lint.out
echo "linter: ok"

# 3. The probe: exit 2 on PreToolUse is a block.
printf '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"ls"}}' > in.json
printf '#!/usr/bin/env bash\necho no >&2\nexit 2\n' > hook.sh
chmod +x hook.sh
python3 "${scripts}/probe-hook.py" --input in.json -- ./hook.sh > probe.out
grep -q '^outcome: blocking error' probe.out || fail_with "probe output:" probe.out
echo "probe: ok"

# 4. The changelog script, with a stub curl: entries listed, a failed download exits 3.
mkdir bin
printf '## 2.1.306\n\n- Fixed a PreToolUse hook bug\n\n## 2.1.305\n\n- Older\n' > body.txt
printf '#!/usr/bin/env bash\ncat "%s/body.txt"\n' "${work}" > bin/curl
chmod +x bin/curl
out=$(PATH="${work}/bin:${PATH}" bash "${scripts}/hook-changes.sh" 2.1.305 2.1.306)
[[ ${out} == *"Fixed a PreToolUse hook bug"* ]] || fail "hook-changes.sh output: ${out}"
printf '#!/usr/bin/env bash\nexit 7\n' > bin/curl
status=0
PATH="${work}/bin:${PATH}" bash "${scripts}/hook-changes.sh" 2.1.305 > /dev/null 2>&1 || status=$?
[[ ${status} == 3 ]] || fail "hook-changes.sh exited ${status} on a failed download, not 3"
echo "hook-changes.sh: ok"
