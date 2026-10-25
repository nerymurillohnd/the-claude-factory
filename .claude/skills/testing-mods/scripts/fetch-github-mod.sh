#!/usr/bin/env bash
# Clone a public GitHub plugin marketplace and print the directory of one plugin.
#
# Usage: fetch-github-mod.sh <owner/repo> <plugin-name> <dest-dir>
#
# stdout: the plugin directory (one line). Progress and errors go to stderr.
# Exit 2: the plugin's source is outside this skill's scope (not on github.com,
#         or a source type other than relative path / github / url / git-subdir).
# Requires git and jq on PATH. The clones are untrusted third-party code.
set -euo pipefail

repo="${1:?usage: fetch-github-mod.sh <owner/repo> <plugin-name> <dest-dir>}"
plugin="${2:?usage: fetch-github-mod.sh <owner/repo> <plugin-name> <dest-dir>}"
dest="${3:?usage: fetch-github-mod.sh <owner/repo> <plugin-name> <dest-dir>}"

mkdir -p "${dest}"
market="${dest}/marketplace"
git clone --quiet "https://github.com/${repo}.git" "${market}" >&2

manifest="${market}/.claude-plugin/marketplace.json"
entry="$(jq -c --arg n "${plugin}" '.plugins[] | select(.name == $n)' "${manifest}")"
if [[ -z ${entry} ]]; then
  echo "plugin '${plugin}' not found in ${manifest}" >&2
  exit 1
fi

# Clone a git source into $2, honoring ref/sha. $1 = url, $3 = ref, $4 = sha.
clone_source() {
  local url="$1" target="$2" ref="$3" sha="$4"
  case "${url}" in
    https://github.com/* | git@github.com:*) ;;
    http* | git@* | file://*)
      echo "source host is not github.com: ${url} (out of scope)" >&2
      exit 2
      ;;
    *) url="https://github.com/${url}.git" ;; # owner/repo shorthand
  esac
  if [[ -n ${sha} ]]; then
    git clone --quiet "${url}" "${target}" >&2
    git -C "${target}" checkout --quiet "${sha}" >&2
  elif [[ -n ${ref} ]]; then
    git clone --quiet --depth 1 --branch "${ref}" "${url}" "${target}" >&2
  else
    git clone --quiet --depth 1 "${url}" "${target}" >&2
  fi
}

kind="$(jq -r 'if (.source | type) == "string" then "path" else .source.source end' <<< "${entry}")"

case "${kind}" in
  path)
    src="$(jq -r '.source' <<< "${entry}")"
    case "${src}" in
      .) rel="" ;;
      ./*) rel="${src#./}" ;;
      *) # bare name resolves under metadata.pluginRoot
        root="$(jq -r '.metadata.pluginRoot // empty' "${manifest}")"
        rel="${root:+${root}/}${src}"
        ;;
    esac
    printf '%s\n' "${market}/${rel}"
    ;;
  github | url)
    if [[ ${kind} == github ]]; then url="$(jq -r '.source.repo' <<< "${entry}")"; else url="$(jq -r '.source.url' <<< "${entry}")"; fi
    ref="$(jq -r '.source.ref // empty' <<< "${entry}")"
    sha="$(jq -r '.source.sha // empty' <<< "${entry}")"
    clone_source "${url}" "${dest}/plugin" "${ref}" "${sha}"
    printf '%s\n' "${dest}/plugin"
    ;;
  git-subdir)
    url="$(jq -r '.source.url' <<< "${entry}")"
    sub="$(jq -r '.source.path' <<< "${entry}")"
    ref="$(jq -r '.source.ref // empty' <<< "${entry}")"
    sha="$(jq -r '.source.sha // empty' <<< "${entry}")"
    clone_source "${url}" "${dest}/plugin" "${ref}" "${sha}"
    printf '%s\n' "${dest}/plugin/${sub}"
    ;;
  *)
    echo "source type '${kind}' is out of scope (only relative path, github, url, git-subdir on github.com)" >&2
    exit 2
    ;;
esac
