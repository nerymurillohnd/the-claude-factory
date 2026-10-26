#!/usr/bin/env bash
# Print the plugins that should get the FULL eval suite in CI.
#
# A plugin is a target only if it has an eval directory AND is either
#   new    - its .claude-plugin/plugin.json did not exist at BASE, or
#   edited - one of its components or dependencies changed between BASE and HEAD:
#            any file under its directory except the eval directory and the
#            documents README.md, CHANGELOG.md, LICENSE* and NOTICE* at its root.
# Any other plugin with evals is skipped.
#
# Usage: changed-eval-plugins.sh BASE HEAD [PLUGINS_DIR] [EVAL_DIR_NAME]
#   PLUGINS_DIR     directory holding one folder per plugin (default: plugins)
#   EVAL_DIR_NAME   eval directory inside each plugin      (default: evals)
# Output: one "<plugin>\t<new|edited>" line per target. Exit 0 even when empty.
# Needs full history for BASE (checkout with fetch-depth: 0).
set -euo pipefail

base="${1:?usage: $0 BASE HEAD [PLUGINS_DIR] [EVAL_DIR_NAME]}"
head="${2:?usage: $0 BASE HEAD [PLUGINS_DIR] [EVAL_DIR_NAME]}"
plugins_dir="${3:-plugins}"
eval_dir="${4:-evals}"

zero='^0+$'
all_new=0
if [[ ${base} =~ ${zero} ]] || ! git cat-file -e "${base}^{commit}" 2> /dev/null; then
  echo "warning: BASE '${base}' is empty or unknown; treating every plugin with evals as new" >&2
  all_new=1
fi

changed=""
if [[ ${all_new} -eq 0 ]]; then
  changed="$(git diff --name-only "${base}...${head}" -- "${plugins_dir}/" || true)"
fi

for dir in "${plugins_dir}"/*/; do
  [[ -d ${dir} ]] || continue
  name="$(basename "${dir}")"
  [[ -d "${dir}${eval_dir}" ]] || continue

  if [[ ${all_new} -eq 1 ]]; then
    printf '%s\tnew\n' "${name}"
    continue
  fi

  touched="$(printf '%s\n' "${changed}" \
    | grep -E "^${plugins_dir}/${name}/" \
    | grep -Ev "^${plugins_dir}/${name}/(${eval_dir}/|README\.md$|CHANGELOG\.md$|LICENSE[^/]*$|NOTICE[^/]*$)" || true)"
  [[ -n ${touched} ]] || continue

  if git cat-file -e "${base}:${plugins_dir}/${name}/.claude-plugin/plugin.json" 2> /dev/null; then
    printf '%s\tedited\n' "${name}"
  else
    printf '%s\tnew\n' "${name}"
  fi
done
