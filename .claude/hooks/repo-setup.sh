#!/usr/bin/env bash
set -euo pipefail
# Repository setup, run by checkout.sh at every session start: installs the dependencies, copies
# the mods' missing type declarations, runs the validators, lists outdated packages, and prints the repository's tool versions beside the global
# ones. A failing step stops the script with its own error.

root="${CLAUDE_PROJECT_DIR:-${PWD}}"
cd "${root}"

echo "== npm install"
npm install --no-audit --no-fund

# A plugin's own package.json holds only its runtime dependencies, which Claude Code installs for
# users when it caches the plugin. The local gates (tsc-plugins, the plugin's node tests) need them
# too. --ignore-scripts matches that install: no package code runs.
for lock in plugins/*/package-lock.json; do
  [[ -e ${lock} ]] || continue
  plugin_dir="$(dirname "${lock}")"
  echo "== npm install (${plugin_dir})"
  npm install --prefix "${plugin_dir}" --ignore-scripts --no-audit --no-fund
done

# A mod's .claude-plugin/types/ is git-ignored, and Claude Code writes it only when an interactive
# session loads the mod with --plugin-dir: a new worktree has none, and its mod-tsc gates fail. Copy
# the missing ones from the main worktree, whose sessions write them.
echo "== mod types"
main_tree="$(git worktree list --porcelain | sed -n '1s/^worktree //p')"
this_tree="$(pwd -P)"
for config in plugins/*/tsconfig.json; do
  [[ -e ${config} ]] || continue
  plugin_dir="$(dirname "${config}")"
  types="${plugin_dir}/.claude-plugin/types"
  [[ -e "${types}/tsconfig.json" ]] && continue
  if [[ ${main_tree} != "${this_tree}" && -e "${main_tree}/${types}/tsconfig.json" ]]; then
    rm -rf "${types}"
    cp -R "${main_tree}/${types}" "${types}"
    echo "copied ${types} from ${main_tree}"
  else
    echo "missing ${types}: open an interactive claude session with --plugin-dir ${plugin_dir}"
  fi
done

echo "== validators"
npm run --silent validate

echo "== npm outdated"
# npm outdated exits 1 when a package is outdated: that is the report, not a failure.
npm outdated || true

echo "== repo vs global"
npm ls --depth=0
repo_biome="$(npx --no-install biome --version)"
global_biome="$(biome --version)"
repo_tsc="$(npx --no-install tsc --version)"
global_tsc="$(tsc --version)"
global_node="$(node --version)"
echo "biome: repo ${repo_biome} | global ${global_biome}"
echo "tsc:   repo ${repo_tsc} | global ${global_tsc}"
echo "node:  global ${global_node}"
