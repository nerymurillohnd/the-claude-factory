#!/usr/bin/env bash
set -Eeuo pipefail
trap 'exit 1' ERR

if [[ ${CLAUDE_CODE_REMOTE:-} != "true" ]]; then
  exit 0
fi

project_dir="${CLAUDE_PROJECT_DIR:-${PWD}}"
log_dir="${HOME}/.cache/the-claude-factory"
log_file="${log_dir}/cloud-setup.log"
stamp_file="${project_dir}/node_modules/.cloud-setup.sha256"
local_bin="${HOME}/.local/bin"

mkdir -p "${log_dir}"
exec 3>&1 1> "${log_file}" 2>&1
cd "${project_dir}"

problems=()
notes=()

align_node() {
  export NVM_DIR="${NVM_DIR:-${HOME}/.nvm}"
  if [[ ! -s "${NVM_DIR}/nvm.sh" ]]; then
    problems+=("nvm is missing from ${NVM_DIR}; the environment's setup script installs it")
    return 0
  fi
  local node_exe node_dir linked_node
  if ! node_exe="$(bash -c '. "${NVM_DIR}/nvm.sh" --no-use >&2 && nvm use >&2 && command -v node')"; then
    problems+=("nvm use found no installed Node.js for .nvmrc")
    return 0
  fi
  node_dir="${node_exe%/node}"
  export PATH="${node_dir}:${PATH}"
  hash -r
  linked_node="$(readlink -f "${local_bin}/node")"
  if [[ ${linked_node} != "${node_exe}" ]]; then
    local executable
    for executable in node npm npx; do
      ln -sfn "${node_dir}/${executable}" "${local_bin}/${executable}"
    done
    notes+=("linked Node.js from .nvmrc into ${local_bin}")
  fi

  local npm_range npm_root npm_version
  npm_range="$(node -p 'require("./package.json").devEngines.packageManager.version')"
  npm_root="$(npm root --global)"
  npm_version="$(npm --version)"
  if ! node -e '
    const semver = require(require("path").join(process.argv[1], "npm", "node_modules", "semver"));
    process.exit(semver.satisfies(process.argv[2], process.argv[3]) ? 0 : 1);
  ' "${npm_root}" "${npm_version}" "${npm_range}"; then
    if ! npm install --global --no-audit --no-fund "npm@${npm_range}"; then
      problems+=("npm ${npm_version} does not satisfy devEngines ${npm_range}, and installing it failed")
    fi
  fi
}

fetch_history() {
  local shallow
  shallow="$(git rev-parse --is-shallow-repository)"
  if [[ ${shallow} == "true" ]] && ! git fetch --unshallow --tags --quiet origin; then
    notes+=("the clone stays shallow: git fetch --unshallow failed")
  fi
}

install_dependencies() {
  local inputs=(package.json package-lock.json pyproject.toml uv.lock .nvmrc .python-version .claude/hooks/cloud-setup.sh)
  local lock
  for lock in plugins/*/package-lock.json; do
    if [[ -f ${lock} ]]; then
      inputs+=("${lock}")
    fi
  done

  if [[ -d .venv && -f ${stamp_file} ]] && sha256sum --check --status "${stamp_file}"; then
    notes+=("dependencies already match the lockfiles")
    return 0
  fi

  # npm run setup also installs each plugin's own lockfile (setup:plugins).
  if ! npm run setup; then
    problems+=("npm run setup failed")
    return 0
  fi
  if ((${#problems[@]} == 0)); then
    sha256sum "${inputs[@]}" > "${stamp_file}"
    notes+=("installed the project dependencies")
  fi
}

align_node
fetch_history
if ((${#problems[@]} == 0)); then
  install_dependencies
fi

node_version="$(node --version)"
npm_version="$(npm --version)"
summary="Cloud setup: Node.js ${node_version}, npm ${npm_version}"
if ((${#notes[@]} > 0)); then
  summary+="; $(printf '%s; ' "${notes[@]}")"
  summary="${summary%; }"
fi

if ((${#problems[@]} == 0)); then
  jq -cn --arg msg "${summary}." '{systemMessage: $msg}' >&3
  exit 0
fi

failures="$(printf '%s; ' "${problems[@]}")"
failures="${failures%; }"
jq -cn \
  --arg msg "Cloud setup failed: ${failures}. Log: ${log_file}" \
  --arg ctx "The project's cloud setup hook failed: ${failures}. Read ${log_file}, fix the cause, and tell the user before running the project's checks, which need node_modules and .venv." \
  '{systemMessage: $msg, hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $ctx}}' >&3
