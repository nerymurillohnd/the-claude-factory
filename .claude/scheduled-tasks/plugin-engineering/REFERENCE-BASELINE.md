# Reference baseline: plugin-engineering

## Purpose

The weekly audit of the `plugin-engineering` plugin reads this file first. It covers the plugin's two skills, `public-marketplace-dev` (65 references, 32 assets) and `cli-commands-guide` (4 references). The audit compares them with the current official docs and with the Claude Code releases published after this baseline. Then it reports what changed. It does not repeat the work recorded here, and it changes no file.

## Baseline

- Official pages downloaded on 2026-11-07.
- On 2026-11-08, 63 of the 64 source pages were byte-identical to the live pages. The support article has no Markdown version to compare.
- Newest Claude Code release at the baseline: 2.1.319, dated November 6, 2026 (https://code.claude.com/docs/en/changelog.md). It was also the installed build. Both skills were checked against it.
- The next audit reads the releases after 2.1.319 and the pages changed since 2026-11-08.

## Scope test

The references serve one reader: Claude, working on a public plugin marketplace hosted on GitHub, whose plugins third parties install on their own machines.

- Kept: every fact a public GitHub marketplace, its plugins and their users rely on, including the rules that govern public GitHub clones.
- Removed: what applies only to another distribution channel, to an administrator, or to one user's own session.

## Method

1. 2026-11-07, line pruning. One reviewer read each whole file and removed whole lines, each with a reason. Organization and administrator removals were confirmed by a second, admin-focused review.
2. 2026-11-08, Nery's decision: `command` and `archive` plugin sources are excluded.
3. 2026-11-08, directive rewrite of the 46 files of 500 lines or fewer, addressed to Claude. Code blocks, tables, schemas and examples were kept verbatim. An independent verifier compared each rewrite with its original.
4. 2026-11-09, large files rewritten in two stages, under the same rules. Each was read in chunks of at most 250 lines, with a map of every original heading. Separate verifiers then read the results in full.
5. 2026-11-09, images: the 29 official images (16 PNG, 13 SVG rendered to PNG) became `assets/*.png`. Each image line keeps a "View the image" pointer to its copy. Three standalone JSON examples of 20 lines or more became `assets/*.json`, each replaced by a "Read the example" pointer.
6. 2026-11-09, `01-plugins-core/cli-reference.md` was slimmed to pointers to `cli-commands-guide`. Only the facts that skill lacks stayed verbatim.
7. 2026-11-09, the pruned changelog was deleted and replaced by `05-cli-diagnostics/official-source-validation.md`, a procedure for reading official sources and release ranges.
8. 2026-11-09, `hooks.md` was trimmed by a novelty audit. A fresh agent kept only what it could not predict, and a second agent checked every removed line. The file was then split into `hooks.md` and `hooks-events.md`, under the repository's 256 KiB limit.
9. 2026-11-09, standard layout for all 65 files: a title, a one-line description, `## Contents` listing every heading from `##` to `####`, and `## Documentation References` last, with the source page first.
10. 2026-11-09, `SKILL.md` got its rules, gotchas, workflow, validation loop and an index linking every reference and asset.

## Removed and why

Each item was removed because it applies only to another channel, to an administrator, or to a single session.

| Category | Why | Files most affected |
| :-- | :-- | :-- |
| Anthropic's directory and official marketplaces | Anthropic's own channel, not a third-party GitHub marketplace | `anthropic-marketplaces.md`, `cli-hints.md` (whole body), `code-intelligence.md`, `publish.md`, `security.md`, `build.md` |
| Private repositories and credentials | A public marketplace needs no credentials | `host-marketplace.md`, `settings-reference.md`, `errors.md`, `env-vars.md`, `marketplace-reference.md` |
| Non-GitHub and self-hosted hosts | Other hosts (GitLab, GitHub Enterprise Server, bare `marketplace.json` URLs, shared folders) | `marketplace-reference.md`, `cli-reference.md`, `host-marketplace.md`, `install.md` |
| `url`, `npm`, `archive` and `command` sources | Not GitHub distribution; `command` and `archive` by Nery's decision of 2026-11-08 | `marketplace-reference.md`, `loading.md`, `host-marketplace.md`, `install.md` |
| Local-folder or zip sharing | Not marketplace distribution | `loading.md`, `create.md`, `org.md`, `create-marketplace.md` |
| Managed settings and organization administration | Administrator-only | `settings-reference.md`, `org.md`, `env-vars.md`, `managed-settings.md`, `server-managed-settings.md` |
| claude.ai sync | Account and organization sync, not the GitHub channel | `server-managed-settings.md`, `skills.md`, `cli-reference.md`, `loading.md` |
| Agent SDK callbacks | Programmatic hosts, not plugins | `sdk-skills.md`, `sdk-plugins.md`, `hooks.md` |
| Personal-session settings | One user's own session | `settings-reference.md`, `model-config.md`, `skills.md`, `mcp.md` |
| Built-in features | Not shipped by a plugin | `skills.md`, `mod-overview.md`, `output-styles.md` |

The line-by-line lists are in git history (see History).

## Link audit

| Tool | Checks |
| :-- | :-- |
| `scripts/checkers/reference-pages.py` | Offline: the Contents and References layout, same-file and cross-file anchors (GitHub slugs, `-1` for a repeated slug, percent-decoded), and the existence of every relative link and asset. Fenced code is ignored. |
| `scripts/checkers/markdown-urls.py` | Live: every http(s) URL answers, and its `#fragment` names an id on the page. Verdicts: validated, broken (fix it), unverified (401, 403, 429 or a timeout; prove it another way), skipped (a placeholder). |

Run from the repository root:

```bash
scripts/checkers/reference-pages.py plugins/plugin-engineering/skills/public-marketplace-dev/references
scripts/checkers/reference-pages.py --links-only plugins/plugin-engineering/skills/cli-commands-guide/references
scripts/checkers/markdown-urls.py plugins/plugin-engineering
```

`--links-only` is for `cli-commands-guide`: its references have `## Contents` but no `## Documentation References`. Each tool exits 0 on a pass, 1 on a finding and 2 on a bad argument.

Result on 2026-11-09:

- Layout and local links: 65 and 4 pages, 0 problems.
- Anchors to other sites: of 993, all match a live id except `claude-directory#ce-claude-json` (the official settings page uses it too) and `github.com/npm/node-semver#ranges` (GitHub renders it from the README heading `## Ranges`).

## Watch list

Open items the audit rechecks. Each is closed once the official source settles it.

**Hook facts in `hooks.md` marked *not yet on this page***:

- 2.1.312: prompt and agent hook concurrency; the page still says 12 per event.
- 2.1.300: `updatedInput` validation.
- 2.1.299: plugin hook hand-off and the 28,000-level nesting limit. The release notes don't say whether these cover command hooks or only mods' function hooks.

**Mods corrections where the docs lag 2.1.319** (`mod-create.md`, `mod-reference.md`):

- The wording and answers of the hot-reload question (2.1.304).
- A failed hook of a mod Claude wrote comes back to Claude as a notice.
- `next.error.kind` is only `'throw' | 'timeout'`, with no `cause`. Re-entry not reaching `.catch` still needs an empirical test.
- The `mobile` render surface is missing from the official tables.

Drift items were reported to Anthropic through Claude Code Docs feedback on 2026-11-09. A fixed page closes its item.

**Anchors that the official text links but the live pages don't hold**. They were found on 2026-11-08 and are still in the references:

- `agent-view.md#from-inside-a-session`, `best-practices.md#keep-claude-md-short`, `claude-code-on-the-web#from-terminal-to-cloud`, `claude-directory#ce-claude-json`
- `costs#using-the-/usage-command`, `desktop.md#what%E2%80%99s-not-available-in-desktop`, `interactive-mode#side-questions-with-%2Fbtw`, `managed-mcp#exclusive-control-with-managed-mcp-json`
- `memory#agents-md`, `memory.md#how-claude-md-files-load`, `permission-modes.md#eliminate-prompts-with-auto-mode`, `permission-modes.md#how-the-classifier-evaluates-actions`
- `self-hosted-environments-configuration.md#connection-timing` (all under code.claude.com/docs/en/)
- `platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#refusal-response`

**Kept under doubt**. These passages were kept although they may fall outside the scope; line numbers are those of the 2026-11-07 download:

- `host-marketplace.md` 151: `KEEP_MARKETPLACE_ON_FAILURE`, also useful when a public remote is unreachable.
- `install.md` 242-245: SSH and `known_hosts` rules that also govern public GitHub clones.
- `mod-reference.md` 425-427: the built-in sec-default guard under managed settings.
- `hooks.md` 251: cloud-session plugin and hook carry-over, mixed with managed-tier details.
- `skills.md` 100-150: the first-skill tutorial, which uses the personal `~/.claude/skills`.
- `skills.md` 418-435: frontmatter portability to claude.ai and the Skills API.
- `statusline.md` 1197-1204: exit-code and hang behavior; unclear for a plugin `subagentStatusLine`.
- `sub-agents.md` 991-1002: output scanning of subagent reports.
- `settings-reference.md` 691-707: `outputStyle`, how a user selects a plugin's output style.
- `settings-reference.md` 3279-3297: `verbose`, for debugging hooks and MCP servers.
- `settings-reference.md` 3777-3794: `disableSkillShellExecution`, which can disable a plugin skill's inline shell.
- `errors.md` 4369-4385: an `archive` source pinned by sha256, usable only from a GitHub release asset.
- `troubleshoot-install.md` 1263-1265: `/logout` removes plugin sensitive values.
- `platform-support.md` 17: the Desktop feature matrix for third-party model providers.
- Six more were in the deleted `changelog.md`, so no file holds them now.

## Audit run

- Inputs: this file, both skills, and the two checkers above.
- Procedure, sources, precedence and report format: follow `plugins/plugin-engineering/skills/public-marketplace-dev/references/05-cli-diagnostics/official-source-validation.md`, sections `When to validate`, `Source precedence`, `Read a range of Claude Code releases`, `Procedure` and `Report format`.
- Report open issues of `anthropics/claude-code` that touch plugins as unconfirmed signals, apart from the findings.
- The report changes no file. Nery and Claude review it in a session and decide what to apply.

## History

The line-by-line removal lists (`REMOVALS.md`) and the 2026-11-08 link audit (`LINK-AUDIT.md`) were deleted when this file was written. Read them from git:

```bash
for f in REMOVALS.md LINK-AUDIT.md; do
  p=.claude/scheduled-tasks/plugin-engineering/$f
  sha=$(git log --diff-filter=D -1 --format=%H -- "$p")
  git show "$sha^:$p"
done
```

At writing, both files are also in commit `3318c07`, but a rebase changes that hash. The files exist only in the history of branch `claude/project-thread-2mfqwl`, because `main` never held `.claude/scheduled-tasks/`. Their history reaches `main` through a merge commit or a rebase merge, but not a squash merge. Nery chose a merge commit for this branch's pull request (2026-11-09).
