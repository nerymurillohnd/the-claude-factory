# Make a plugin public-ready

Checked 2026-10-25 against `/en/plugins/publish`, `/en/plugins/host-marketplace`, `/en/plugins/security`, claude.com `/docs/plugins/build`, `/docs/plugins/pre-submission-checklist`, `/docs/directory/publish`, and the Claude Code changelog through v2.1.310.

## Contents

- What every public plugin ships
- README: required sections
- Secrets, credentials and network calls
- Repository hygiene for git-based installs
- What users need on their machine
- Optional: Anthropic's directory
- Public readiness checklist

## What every public plugin ships

- `README.md` at the plugin root (and a marketplace README at the repo root for Layout B).
- `LICENSE` file, or `license` in `plugin.json`. A public repo without a license isn't legally reusable, and the directory blocks it.
- `CHANGELOG.md` when you version releases.
- Filled metadata: `description`, `author`, `homepage` (must be a valid URL), `repository`, `license`, `keywords`.
- `NOTICE.txt` when the plugin bundles or derives from third-party material, with each source's repo, version or commit, and license.

## README: required sections

1. **What it does** for the user, in plain words, and on which surfaces (Claude Code only, or also claude.ai/Cowork). In this repository the README states them as `docs/compatibility.md` does per component type; the surface table in `manifest-and-components.md` explains why.
2. **Install** — the exact lines, with your real names. Since v2.1.295, `claude plugin validate` prints the line to paste when a README has none (advice only; it never fails the run):

   ```bash
   claude plugin marketplace add owner/repo
   claude plugin install <plugin>@<marketplace-name>
   ```

   Also give the one-step forms (`claude plugin install <plugin> --marketplace owner/repo`, v2.1.292+; `/plugin install <plugin> --marketplace owner/repo` in a session, v2.1.275+), and the note for users without a GitHub SSH key:

   ```bash
   export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
   ```

   Keep it even though `claude plugin install` from the shell falls back to HTTPS on its own (v2.1.288+ on macOS and Linux, v2.1.296+ on Windows): installs from `/plugin` inside a session and plugin updates don't.
3. **Update** — `claude plugin update <plugin>@<marketplace>`, and that auto-update is off until they enable it under `/plugin` → Marketplaces.
4. **Prerequisites** — every tool, binary, runtime, account or service the plugin needs, how to install it, and alternatives. Missing tools are a documented prerequisite, never a silent assumption or an in-plugin installer.
5. **Configuration** — each `userConfig` option and how to set it from the shell (`--config KEY=VALUE`) or `/plugin configure`.
6. **What it runs and sends** — every hook (event, matcher, what the script does), every MCP server (command or URL), every monitor, every network destination and what data goes there. Claude Code's trust warning sends users to the plugin's homepage before they install, so this is what they read, and hooks run with their full permissions outside the sandbox.
7. **Usage** — the skill commands (`/<plugin>:<skill>`) and example prompts that trigger the plugin's skills.
8. **Uninstall** — `claude plugin uninstall <plugin>@<marketplace>`, and what `${CLAUDE_PLUGIN_DATA}` holds (deleted on last uninstall unless `--keep-data`).

Anthropic's directory blocks a README under 40 words (code blocks don't count), and its security scan looks for behavior the README doesn't disclose; covering what it does, how to use it and what it sends is a good floor for any public plugin.

## Secrets, credentials and network calls

- No API keys, tokens or real credentials in any file, including examples and docs. Every user receives every file.
- Ask for credentials through `userConfig` with `"sensitive": true` and reference them where `/en/plugins/manifest-reference` → User configuration says each form resolves, which for a hook depends on its form.
- Don't read credentials already in the user's environment (such as `$GITHUB_TOKEN`) and send them to a server; ask for them explicitly. The directory holds or blocks this, and it surprises users.
- Make network calls only when the plugin's purpose needs them, and write the README disclosure in the same commit as the call.
- Use `https://` (or `wss://`) for remote MCP URLs. Claude Code warns on `http://`/`ws://` to a non-loopback host, and the directory blocks other schemes (it also accepts a `${user_config.KEY}` reference or `""`).
- Commit readable source, not minified or packed code, so users (and scanners) can review what runs.

## Repository hygiene for git-based installs

Users install by cloning, so the repo itself must survive a clone on any OS:

- **No Git LFS** for anything the plugin loads: clones never fetch LFS content, files arrive as pointer files.
- **Submodules**: Claude Code (v2.1.295+) fetches only submodules inside a plugin's directory; a plugin at the repo root that refers to any submodule path pulls all of them. Avoid submodules for plugin content; commit real files.
- **Symlinks**: kept inside a plugin; dereferenced across plugins of the same marketplace; skipped when they leave the marketplace. Prefer real files; the directory blocks symlinks the plugin loads.
- **File names**: valid on Windows and macOS (no `:`, no trailing dot or space, no `con`/`prn`, no two names differing only by case). Remove `.DS_Store`, `Thumbs.db`, `desktop.ini`, `__MACOSX`.
- **Executable bit**: commit a script that anything runs by its path as `100755` (`git update-index --chmod=+x <file>`, then check with `git ls-files -s`). A lost bit then fails it on every user's machine.
- **Self-contained**: everything a hook, MCP server or script runs lives inside the plugin directory; installed plugins are copies and can't reach `../`.
- **`.gitattributes`**: no `export-ignore`, `export-subst`, or content filters (LFS included) affecting the plugin.
- **No top-level `bin/`** unless Claude Code-only by design.

## What users need on their machine

- `git` on `PATH`. Claude Code runs it non-interactively with the user's existing credentials; it has no token of its own and `marketplace.json` has no credential field.
- For a public repo nothing else: `owner/repo` probes SSH and falls back to HTTPS; `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` skips the probe for users with no SSH key.
- The prerequisites your README lists.

## Optional: Anthropic's directory

A public GitHub marketplace needs no submission. Listing in Anthropic's directory (claude.ai and Cowork, reaching Claude Code as `<name>@synced`) is a separate route: a paid claude.ai plan, submission from the developer portal at claude.ai/directory/manage, a public GitHub repo by go-live, one plugin folder per submission, and automated validation plus a security scan on every version. `claude-plugins-official` doesn't take submissions through the portal. Before submitting, work through claude.com `/docs/plugins/pre-submission-checklist`; the rules that most often bite:

- Name: lowercase letters, digits and hyphens, ≤ 64 chars, distinctive (not `claude`, `anthropic`, `official`, `plugin`, `mcp`, `test` as the whole name), unique across organizations.
- README ≥ 40 words and a license: **blocking**.
- Files: each file other than images and fonts under 256 KiB, ≤ 512 files, only text, common images and fonts — otherwise held for a reviewer.
- Package launchers (`npx`, `bunx`, `pnpm dlx`, `yarn dlx`, `uvx`, `pipx run`, `uv run`): must pin an exact version (`npx pkg@1.2.3`, `uvx pkg==1.2.3`), and `uv run` needs `--locked` or `--frozen`, or the submission is **blocked**; and even pinned they're held for review. Bundling the code into the plugin, or a local server run as `node ${CLAUDE_PLUGIN_ROOT}/server.js`, avoids both.
- Hook and MCP commands: write each path in full from `${CLAUDE_PLUGIN_ROOT}`, with no other variables, command substitution or inline programs (`python3 -c`) — blocking when the plugin is a subfolder of the repo.
- `package.json` beside a lockfile (`package-lock.json`, `npm-shrinkwrap.json`, `bun.lock`, `bun.lockb`) in the plugin root is always held for a reviewer.

If the author's own convention is "never pin tool versions", note the difference: that convention is about scripts calling tools already on the user's `PATH`; the directory rule is about launchers that download code at run time. The cleanest way to satisfy both is not to use launchers at all.

## Public readiness checklist

- [ ] Permanent kebab-case `name` that passes the reserved-name rules; `displayName` set
- [ ] `description`, `author`, `homepage` (valid URL), `repository`, `license`, `keywords` filled
- [ ] README with install, HTTPS note, update, prerequisites, configuration, what it runs and sends, usage, uninstall
- [ ] `LICENSE` present; third-party material attributed
- [ ] No secrets anywhere; credentials via `userConfig` `sensitive: true`
- [ ] Every network call disclosed; remote MCP over `https://`
- [ ] Scripts with `#!/usr/bin/env <interpreter>`, reached through `${CLAUDE_PLUGIN_ROOT}`, committed `100755` when run by path
- [ ] No LFS, no stray OS files, portable file names, nothing outside the plugin directory
- [ ] Surfaces stated; no top-level `bin/` unless Claude Code-only
- [ ] `version` set in `plugin.json` and absent from the marketplace entry (see `versioning-and-release.md`)
