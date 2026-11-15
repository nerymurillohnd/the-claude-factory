#!/usr/bin/env bash
# Tag and publish a GitHub Release for each plugin whose current version has no tag on origin,
# at TARGET_SHA (default HEAD). release.yml runs it from the repository root.
#
# PLUGIN limits the run to one marketplace plugin (exit 2 if it isn't listed).
# BACKFILL_TARGET, with PLUGIN, releases the version that was current at that commit instead,
# with its notes from today's CHANGELOG; the commit must be in HEAD's history (exit 1 if not).
# Needs git, node, uv and gh; gh reads GH_TOKEN.
set -Eeuo pipefail
trap 'exit 1' ERR

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
plugin="${PLUGIN:-}"
backfill="${BACKFILL_TARGET:-}"
target="${TARGET_SHA:-$(git rev-parse HEAD)}"

notes=(uv run --project "${root}" python "${root}/scripts/release/release-notes.py" --root .)

publish() {
  local name="$1" at="$2" tag file found
  shift 2
  tag="$("${notes[@]}" "${name}" --tag "$@")"
  found=0
  git ls-remote --exit-code --tags origin "refs/tags/${tag}" > /dev/null || found=$?
  if ((found == 0)); then
    echo "✔ ${tag} already released"
    return 0
  fi
  if ((found != 2)); then
    echo "publish-releases: git ls-remote origin failed (${found})" >&2
    exit 1
  fi
  file="$(mktemp)"
  "${notes[@]}" "${name}" "$@" > "${file}"
  gh release create "${tag}" --target "${at}" --title "${tag}" --notes-file "${file}"
  rm -f "${file}"
  echo "🚀 Released ${tag} at ${at}"
}

if [[ -n ${plugin} ]]; then
  status=0
  "${notes[@]}" "${plugin}" --tag > /dev/null || status=$?
  if ((status != 0)); then exit "${status}"; fi
fi

if [[ -n ${backfill} ]]; then
  if [[ -z ${plugin} ]]; then
    echo "publish-releases: BACKFILL_TARGET needs PLUGIN" >&2
    exit 2
  fi
  if ! git merge-base --is-ancestor "${backfill}" HEAD; then
    echo "publish-releases: ${backfill} is not in the history of HEAD" >&2
    exit 1
  fi
  commit="$(git rev-parse "${backfill}^{commit}")"
  version="$(git show "${commit}:plugins/${plugin}/.claude-plugin/plugin.json" \
    | node -e 'let s = ""; process.stdin.on("data", (d) => (s += d)).on("end", () => console.log(JSON.parse(s).version))')"
  publish "${plugin}" "${commit}" --version "${version}"
  exit 0
fi

if [[ -n ${plugin} ]]; then
  publish "${plugin}" "${target}"
  exit 0
fi

names="$(node -e 'console.log(require("./.claude-plugin/marketplace.json").plugins.map((p) => p.name).join(" "))')"
for name in ${names}; do
  publish "${name}" "${target}"
done
