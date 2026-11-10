#!/usr/bin/env bash
# Shared helpers for the documentation governance scripts and hooks. Sourced,
# never run.
# Everything that sources this file fails open: a missing tool or registry
# lets the action through, so a broken script never blocks work.

# Print the repository root.
docs_root() {
  if [[ -n "${CLAUDE_PROJECT_DIR:-}" ]]; then
    printf '%s\n' "${CLAUDE_PROJECT_DIR}"
  else
    git rev-parse --show-toplevel 2>/dev/null || true
  fi
}

# Set DOCS_ROOT and DOCS_REGISTRY, or exit 0 from the caller when jq or
# the registry is missing.
docs_require() {
  if ! command -v jq >/dev/null 2>&1; then
    echo "documentation governance: jq not found, check skipped" >&2
    exit 0
  fi
  DOCS_ROOT="$(docs_root)"
  DOCS_REGISTRY="${DOCS_ROOT}/.claude/skills/documentation-governance/chains.json"
  if [[ ! -f "${DOCS_REGISTRY}" ]]; then
    echo "documentation governance: registry not found, check skipped" >&2
    exit 0
  fi
}

# Print a path relative to the repository root. Paths outside it print unchanged.
docs_relpath() {
  case "$1" in
    "${DOCS_ROOT}"/*) printf '%s\n' "${1#"${DOCS_ROOT}"/}" ;;
    *) printf '%s\n' "$1" ;;
  esac
}

# Print "owner kind" for a repository-relative path, or nothing when ungoverned.
docs_lookup() {
  jq -r --arg p "$1" \
    'first(.documents[] | select(.pattern as $re | $p | test($re)) | "\(.owner) \(.kind)") // empty' \
    "${DOCS_REGISTRY}" 2>/dev/null || true
}

# Print one field of the hook input held in the first argument.
docs_field() {
  printf '%s' "$1" | jq -r "$2 // empty" 2>/dev/null || true
}
