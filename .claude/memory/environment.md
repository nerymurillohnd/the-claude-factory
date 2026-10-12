# Environment and access

## Nery's machine

- macOS on Apple Silicon (M4), zsh. Node via nvm at the version in the repo's `.nvmrc` (26.11.1; LTS from 2026-10-28), no Homebrew Node; Python only via uv.
- Local clone: `~/Claude/the-claude-factory`.
- His network blocks SSH to GitHub → always use **HTTPS** remotes (`https://github.com/nerymurillohnd/the-claude-factory.git`).

## Surfaces we work from

| Surface | What works | Limits |
| :-- | :-- | :-- |
| Cloud session (claude.ai/code, Claude desktop) | Full clone, `claude` CLI, Node, npx; **push** through the Claude GitHub App; `gh api` REST reads, issues, labels, releases | Repository **settings** writes are refused by the session proxy; GraphQL is unavailable (use REST) |
| Linked Mac (device shell) | Read/write in the connected folder, git, node | Linux VM, no `gh`, no GitHub credentials; deleting files needs Nery's per-session approval (git commit/pull leaves `.lock` files without it) |
| Built-in browser (desktop app) | Nery's GitHub session: repo settings, topics, anything the proxy blocks | Sudo-protected pages need Nery to enter his 2FA code |

## Tooling and pins

- `claude` CLI pinned in CI at `2.1.296` (`CLAUDE_CODE_VERSION` in `validate.yml`); local validation uses the same command via `.github/scripts/validate-claude.sh`.
- `markdownlint-cli2@0.23.3`, actionlint `1.7.12`, `actions/checkout` v7.0.1, `actions/setup-node` v7.1.0 and `anthropics/claude-code-action` v1.0.248 pinned by SHA; Linux jobs on `ubuntu-24.04`; CI Node from `.nvmrc`. Review with `/docs-drift-check`.
- Claude Code Docs MCP is available for live docs; claude.com docs via WebFetch (`.md` URLs work).

## Keeping Nery's local clone in sync

After pushing from a cloud session, update the Mac copy with `git -C ~/Claude/the-claude-factory pull --ff-only` (device shell, public repo, no credentials needed) — or ask Nery to pull.
