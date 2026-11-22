#!/usr/bin/env bash
# Check that every http(s) URL in the repository's tracked text files answers.
#
# Usage: live-urls.sh [file...]   With no file, every tracked file is checked.
# A URL fails on 404, 410 or no connection (code 000: DNS, refused, TLS). A timeout and any other
# non-2xx answer, such as 403 or 429 from sites that turn away scripts, is only a warning.
# A URL that holds a line of live-urls.ignore is not checked: list there the URLs that only work
# for a tool, such as an apt repository base, and documented examples that were never meant to load.
# Exit codes: 0 every URL answers, 1 at least one broken URL or an unreadable file.
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "${root}"
ignore="scripts/checks/live-urls.ignore"
# This repository's own tag and compare links: a CHANGELOG links each new version's tag before
# release.yml creates it at the merge, and check:consistency (PC-04) already matches tags.
origin="$(git remote get-url origin)"
repo="${origin%.git}"
repo="github.com/${repo#*github.com[:/]}"

files=("$@")
if ((${#files[@]} == 0)); then
  tracked="$(git ls-files -z | tr '\0' '\n')"
  while IFS= read -r file; do files+=("${file}"); done <<< "${tracked}"
fi

# URLs in text files (grep -I skips binaries; it exits 1 when it finds none), with trailing
# punctuation from prose or Markdown trimmed. Left out: hosts without a dot, reserved example
# names (RFC 2606, RFC 6761: example.com, .example, .test, .invalid, localhost), .internal and
# .local, URLs with a shell variable ($) or cut at a line break (a trailing -), and every URL
# that contains a line of live-urls.ignore, and this repository's own tag and compare links.
urls="$(grep -IhoE 'https?://[^][[:space:]"'"'"'`<>(){}|\\^]+' -- "${files[@]}" \
  | sed -E 's/[.,;:!?*_]+$//' \
  | awk -F/ '$3 ~ /\./ && $3 !~ /(^|\.)(example\.(com|org|net)|[^.]+\.(example|test|invalid|localhost|internal|local))(:|$)/ && $3 !~ /^(127\.0\.0\.1|0\.0\.0\.0)(:|$)/ && !/[$]/ && !/-$/' \
  | grep -vFf "${ignore}" \
  | awk -v own="${repo}/" 'index($0, own "releases/tag/") == 0 && index($0, own "compare/") == 0' \
  | sort -u)" || (($? == 1))

# One curl per URL, 16 at a time, printing the HTTP code, curl's exit code (28 is a timeout) and
# the URL as given, before any redirect. xargs exits 123 when a curl fails, such as on a DNS
# error: that URL is reported with code 000 below.
results=""
if [[ -n ${urls} ]]; then
  results="$(awk 'NF' <<< "${urls}" | xargs -P 16 -n 1 curl -sL -o /dev/null --max-time 20 \
    --retry 2 -A 'Mozilla/5.0 (compatible; live-urls)' -w '%{http_code} %{exitcode} %{url}\n')" || (($? == 123))
fi

broken="$(awk '$1 ~ /^(404|410)$/ || ($1 == "000" && $2 != 28) { print $1, $3 }' <<< "${results}")"
warned="$(awk 'NF && $1 !~ /^(2..|404|410|000)$/ { print "WARN", $1, $3 }
  $1 == "000" && $2 == 28 { print "WARN timeout", $3 }' <<< "${results}")"

if [[ -n ${warned} ]]; then printf '%s\n' "${warned}"; fi
while read -r code url; do
  [[ -n ${url-} ]] || continue
  printf 'BROKEN %s %s\n' "${code}" "${url}"
  awk -v url="${url}" 'index($0, url) { print "  " FILENAME ":" FNR; if (++n == 5) exit }' \
    "${files[@]}"
done <<< "${broken}"

n_urls="$(awk 'NF' <<< "${urls}" | wc -l)"
n_broken="$(awk 'NF' <<< "${broken}" | wc -l)"
n_warned="$(awk 'NF' <<< "${warned}" | wc -l)"
printf 'live-urls: %d URLs, %d broken, %d warnings\n' "${n_urls}" "${n_broken}" "${n_warned}"
[[ -z ${broken} ]]
