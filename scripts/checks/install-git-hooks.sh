#!/usr/bin/env bash
# npm's prepare script: npm runs it after npm install and npm ci. It points Git at the tracked
# .githooks folder (core.hooksPath), so the pre-commit gate runs on every commit in this clone.
# Outside a Git work tree, such as an unpacked tarball or a container build, or with no git
# installed, there are no hooks to turn on, so it exits 0 and npm carries on.
set -euo pipefail

if ! command -v git > /dev/null 2>&1; then
  exit 0
fi
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  exit 0
fi
git config core.hooksPath .githooks
