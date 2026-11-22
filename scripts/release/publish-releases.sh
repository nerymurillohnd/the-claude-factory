#!/usr/bin/env bash
# Tag and publish a GitHub Release for each plugin whose current version has no tag on origin,
# at TARGET_SHA (default HEAD), and publish the missing Release of a tag that has none.
# release.yml runs it from the repository root.
#
# PLUGIN limits the run to one marketplace plugin (exit 2 if it isn't listed).
# BACKFILL_TARGET, with PLUGIN, releases the version that was current at that commit instead,
# with its notes from today's CHANGELOG. Every tag goes on a commit of origin/main: a target or
# backfill commit that main doesn't have is refused (exit 1), whatever branch was dispatched.
# A hand dispatch (GITHUB_EVENT_NAME=workflow_dispatch) that isn't a backfill also needs Validate's
# Checks passed on the target commit; a backfill targets commits older than Validate.
# Needs git, node, uv and gh; gh reads GH_TOKEN.
set -Eeuo pipefail
trap 'exit 1' ERR

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
plugin="${PLUGIN:-}"
backfill="${BACKFILL_TARGET:-}"
target="${TARGET_SHA:-$(git rev-parse HEAD)}"

# release-notes needs only the standard library, so no project dependencies are installed in the
# step that holds the write token.
notes=(env "PYTHONPATH=${root}" uv run --no-project python -P -m scripts.release.notes --root .)

git fetch -q origin main

# The tags of the repository's GitHub Releases, read once, before the first one is needed.
releases=""
releases_read=0
read_releases() {
  if ((releases_read == 0)); then
    releases="$(gh release list --limit 10000 --json tagName --jq '.[].tagName')"
    releases_read=1
  fi
}

publish() {
  local name="$1" at="$2" tag file found
  shift 2
  tag="$("${notes[@]}" "${name}" --tag "$@")"
  found=0
  git ls-remote --exit-code --tags origin "refs/tags/${tag}" > /dev/null || found=$?
  if ((found != 0 && found != 2)); then
    echo "publish-releases: git ls-remote origin failed (${found})" >&2
    exit 1
  fi
  read_releases
  if ((found == 0)) && grep -qxF -- "${tag}" <<< "${releases}"; then
    echo "✔ ${tag} already released"
    return 0
  fi
  file="$(mktemp)"
  "${notes[@]}" "${name}" "$@" > "${file}"
  if ((found == 0)); then
    # A tag never moves: its missing Release is published on the tag as it stands.
    gh release create "${tag}" --verify-tag --title "${tag}" --notes-file "${file}"
    echo "🚀 Published the missing Release of ${tag}"
  else
    gh release create "${tag}" --target "${at}" --title "${tag}" --notes-file "${file}"
    echo "🚀 Released ${tag} at ${at}"
  fi
  rm -f "${file}"
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
  status=0
  git merge-base --is-ancestor "${backfill}" origin/main || status=$?
  if ((status != 0)); then
    echo "publish-releases: ${backfill} is not on main" >&2
    exit 1
  fi
  commit="$(git rev-parse "${backfill}^{commit}")"
  version="$(git show "${commit}:plugins/${plugin}/.claude-plugin/plugin.json" \
    | node -e 'let s = ""; process.stdin.on("data", (d) => (s += d)).on("end", () => console.log(JSON.parse(s).version))')"
  publish "${plugin}" "${commit}" --version "${version}"
  exit 0
fi

status=0
git merge-base --is-ancestor "${target}" origin/main || status=$?
if ((status != 0)); then
  echo "publish-releases: ${target} is not on main; release only from a commit main has" >&2
  exit 1
fi

if [[ ${GITHUB_EVENT_NAME:-} == workflow_dispatch ]]; then
  conclusions="$(gh api "repos/${GITHUB_REPOSITORY:?}/commits/${target}/check-runs?check_name=Checks" \
    --jq '.check_runs[].conclusion')"
  if ! grep -qx success <<< "${conclusions}"; then
    echo "publish-releases: Validate's Checks hasn't passed on ${target}; release after it does" >&2
    exit 1
  fi
fi

if [[ -n ${plugin} ]]; then
  publish "${plugin}" "${target}"
  exit 0
fi

names="$(node -e 'console.log(require("./.claude-plugin/marketplace.json").plugins.map((p) => p.name).join(" "))')"
for name in ${names}; do
  publish "${name}" "${target}"
done
