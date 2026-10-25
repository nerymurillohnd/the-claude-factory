---
name: maintaining-user-docs
description: Use to write, update or check the marketplace's own user documentation, meaning the root README outside its generated blocks, docs/, SECURITY, SUPPORT, CONTRIBUTING, CODE_OF_CONDUCT and the root LICENSE, when a Claude Code release, a docs report or a marketplace change can make them wrong, and for a freshness sweep. Not for the files a plugin ships, the root CHANGELOG, or issues and issue forms.
---

# Maintaining user docs

## Why this matters

These files are what a user reads before trusting the marketplace, and nobody reviews them after we do. A command, UI label or minimum version that drifted from the current Claude Code reaches a user we don't know as a failed install or a wrong expectation. Claude Code changes faster than these files, so a file that was right last month is not proof that it is right today.

## Scope

| In | Out |
| :-- | :-- |
| Root `README.md`, outside the generated `<!-- catalog:* -->` and `<!-- plugin-count:* -->` blocks | The files inside `plugins/<name>/` (README, CHANGELOG, LICENSE, NOTICE) and the templates in `.claude/templates/plugin/` |
| `docs/`: `installation.md`, `managing-plugins.md`, `compatibility.md`, `troubleshooting.md`, `faq.md`, `github-mcp-tools.md`, `assets/` | The root `CHANGELOG.md` and GitHub Releases |
| `SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, the root `LICENSE` | Issue forms, `.github/ISSUE_TEMPLATE/config.yml`, labels, replies to issues |

The files marked Out are read here only to check what the docs say about them. When a docs change requires an Out file to change, report it; do not edit it in the same change.

## Rules

- Write for users. Never mention maintenance, `.claude/`, scripts, CI internals, release mechanics or how we work. A user's own `.claude/settings.json` may be mentioned.
- Check every command, flag, UI path, setting and minimum version against the live official sources in step 3, never against memory or the file itself. When the docs and the release notes differ, the release notes win.
- One fact has one value everywhere. When two files state it, both change in the same commit.
- Never edit the generated blocks. Run `npm run generate`.
- State the minimum Claude Code version of every version-gated feature, and recheck it whenever the file is touched.
- Mark what you could not verify as **unverified**, and say what it affects.
- These files are outside `plugins/`, so they need no pull request. Commit signed, one topic per commit, and push only on Nery's order.

## Style

- English, second person, active voice, present tense, short sentences. Benefit first, mechanics second.
- `##` headings with one emoji each, used the same way across docs: 📥 install, 🔧 manage, 🧭 compatibility, 🩺 troubleshooting, ❓ FAQ, 🔄 update, 🗑️ uninstall, 📝 changelog, 📄 license.
- Badges only in the hero: shields.io, brand color `D97757`.
- Tables for comparisons, commands per surface, requirements and options.
- GitHub alerts (`> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`), never two back to back without text between.
- `<details>` for per-surface instructions and FAQs, with the most common option `open`.
- **Bold** for UI labels, exactly as the app shows them (`/plugin` → **Installed** → **Update now**); *italics* for emphasis or terms.
- Relative links inside the repository; absolute `https://` links outside it.

## Files and their job

| File | Job | Primary sources |
| :-- | :-- | :-- |
| Root `README.md` | The front page, in the order of [references/root-readme.md](references/root-readme.md) | Every source below, by section |
| `docs/installation.md` | Add the marketplace and install, per surface; scopes; set up a team | `/en/plugins/install`, `/en/plugins/host-marketplace` → Register the marketplace for everyone in a repository, `/en/plugins/loading` → Plugins synced from claude.ai |
| `docs/managing-plugins.md` | Update, auto-update, enable and disable, uninstall, remove the marketplace, inspect, the Claude app | `/en/plugins/install` → Manage installed plugins, Keep plugins updated, Manage marketplaces; `/en/plugins/cli-reference`; `/en/plugins/loading` → Versions and updates |
| `docs/compatibility.md` | The single source of the component × surface matrix | <https://claude.com/docs/plugins/platform-support> |
| `docs/troubleshooting.md` | Symptom, cause and fix, with the diagnostic commands | `/en/plugins/troubleshooting`, `/en/plugins/loading` |
| `docs/faq.md` | Short answers that link to the guides | The guide each answer links to |
| `docs/github-mcp-tools.md` | The tools of one plugin's MCP server | That plugin's `.mcp.json` and its server's own docs |
| `SECURITY.md` | Supported versions, private reporting, scope | GitHub's security policy docs; `/en/plugins/security` |
| `SUPPORT.md` | Where to ask, in order | The issue forms and `config.yml` (read only) |
| `CONTRIBUTING.md` | No pull requests, issues welcome, what happens after | The issue forms (read only) |
| `CODE_OF_CONDUCT.md` | Standards and enforcement | Its attributed source |
| Root `LICENSE` | MIT | — |

Claude Code pages live at `https://code.claude.com/docs/en/<page>.md`; `https://code.claude.com/docs/llms.txt` lists them all. Claude app claims need a claude.com or support.claude.com source, such as <https://support.claude.com/en/articles/13837440-use-plugins-in-claude>. The README's Trust & safety section follows `/en/plugins/security` → Review a plugin before you install.

## Pairs that must agree

| Fact | Files |
| :-- | :-- |
| Compatibility matrix | README → Where plugins work ↔ `docs/compatibility.md`. Every plugin README's Compatibility cells copy it too: report the ones that must follow |
| Install, update and uninstall commands, with their minimum versions | README → Quick start and Manage your plugins ↔ `docs/installation.md` ↔ `docs/managing-plugins.md` ↔ `docs/troubleshooting.md` |
| List of guides | README → Documentation ↔ the files in `docs/` |
| How to get help | README → Support ↔ `SUPPORT.md` ↔ the issue forms and `config.yml` links (read only) |
| No pull requests, issues welcome | README → Support ↔ `CONTRIBUTING.md` ↔ `docs/faq.md` |
| Private security reporting | `SECURITY.md` ↔ `SUPPORT.md` ↔ `config.yml` (read only) |
| Marketplace source and suffix | `nerymurillohnd/the-claude-factory` and `@the-claude-factory` in every file |

## Workflow

Tick each step as you finish it.

Progress:
- [ ] 1. **Trigger**: what can have made the docs wrong.
- [ ] 2. **Files**: every file the trigger reaches.
- [ ] 3. **Sources**: the live pages behind each claim.
- [ ] 4. **Write**: one pass per file.
- [ ] 5. **Cross-scope**: what outside this scope must follow.
- [ ] 6. **Check**: the scripts, the links and the names.
- [ ] 7. **Report and commit**.

### 1. Trigger

Name what changed:
- a Claude Code release (read its `CHANGELOG.md` entries from the last version the docs were checked against);
- a report that a doc is wrong;
- a plugin added, renamed, removed or recategorized;
- a change in what a component supports on a surface;
- Nery's request;
- a freshness sweep.

### 2. Files

From the two tables above, list every file and every pair the trigger reaches. A plugin added, renamed or removed changes the generated catalog: run `npm run generate` rather than editing it, then check the prose around it (counts, examples, the documentation table).

### 3. Sources

For each claim the trigger reaches, read its primary source in full, live, and keep the URL. Read the release notes too, raw from <https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md>; expect missing version headings. Compare UI labels and error messages with the source character by character.

### 4. Write

Edit each file in one coherent pass, then reread it whole. Change both sides of every pair in the same pass.

### 5. Cross-scope

List each file outside the scope that must follow (a plugin README's Compatibility cells, a template, an issue form) with what it must say. It changes in its own change: inside `plugins/` that means a pull request.

### 6. Check

Run from the repository root and show the output:
- `node scripts/generators/marketplace.mjs --check` and `node scripts/generators/catalog.mjs --check`;
- `node scripts/check-repo.mjs`;
- `grep -rnoE 'nerymurillohnd/[A-Za-z0-9._-]+|@[a-z-]*claude-factory'` over the touched files, which must return only the source and the suffix above.

Then open the target of every relative link and `#anchor` in the touched files, and confirm the file and heading exist. No script does this.

### 7. Report and commit

Report, in this order:
1. What was wrong, one row each: file:line · claim · what the source says · source URL · fixed or open.
2. The files changed.
3. The output of step 6.
4. The cross-scope list from step 5.
5. What is **unverified**, and the last Claude Code version the docs were checked against.

Commit signed, one topic per commit, with a message that says what changed and why.

## Freshness sweep

Run steps 3 to 7 on every file in scope, against every Claude Code release since the last sweep and the current claude.com platform-support page. List each source you could not reach as not fetched.

## Gotchas

- No linter reads these files: Biome ignores Markdown here (`biome check README.md` reports it as ignored), so a broken link, anchor or table shows up only when you open it.
- `check-repo.mjs` checks plugin READMEs, not these files. A clean run says nothing about them.
- The catalog's version column is generated and is the only version number of a plugin in the root README.
- GitHub reads `SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` from `.github/` first, then the root, then `docs/`. A copy added in `.github/` would silently replace the root one.
- `docs/compatibility.md` drives the Compatibility cells of every plugin README, so a change to it is never only a docs change.
- The minimum versions in the install commands (`claude plugin install … --marketplace` from the shell, `/plugin install … --marketplace` in a session) come from `/en/plugins/publish` → Tell users how to install and `/en/plugins/install`; recheck them on every change to those commands.
