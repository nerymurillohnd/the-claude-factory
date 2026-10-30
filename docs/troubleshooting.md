# 🩺 Troubleshooting

> Quick fixes for the most common problems with **The Claude Factory**. Match the message you see, apply the fix, and you're back in business.

**On this page:** [Adding the marketplace](#-adding-the-marketplace) · [Installing a plugin](#-installing-a-plugin) · [Plugin not working](#-plugin-installed-but-not-working) · [Updates](#-updates-not-arriving) · [Still stuck?](#-still-stuck)

---

## 🏪 Adding the marketplace

<details>
<summary><code>Invalid marketplace source format</code></summary>

The source must be a GitHub `owner/repo`, a full URL, or a local path. Use exactly:

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
```

</details>

<details>
<summary><code>'github.com/…' is not a valid GitHub owner/repo shorthand</code></summary>

Drop the host from the shorthand (`nerymurillohnd/the-claude-factory`), or use the full URL: `https://github.com/nerymurillohnd/the-claude-factory.git`.

</details>

<details>
<summary><code>SSH authentication failed</code> or <code>SSH host key is not in your known_hosts file</code></summary>

When an SSH key for github.com looks configured, Claude Code clones over SSH, with prompts turned off and only hosts already in `known_hosts`. This marketplace is public, so you don't need SSH: add it by its HTTPS URL, or set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` so `owner/repo` sources always clone over HTTPS.

```bash
claude plugin marketplace add https://github.com/nerymurillohnd/the-claude-factory.git
```

To keep SSH instead, run `ssh -T git@github.com` once to accept GitHub's host key, and make sure your key works without a passphrase prompt.

</details>

<details>
<summary>The add hangs or fails behind a proxy or firewall</summary>

Claude Code clones the repository with your local `git`. Confirm `git ls-remote https://github.com/nerymurillohnd/the-claude-factory.git` works from the same shell. If SSH to GitHub is blocked on your network, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` so Claude Code always clones over HTTPS. On a slow connection, `Git clone timed out after 120s` means the clone needs longer: raise the limit with `export CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS=300000` and retry in the same shell.

</details>

<details>
<summary>Blocked by my organization</summary>

Your administrator restricts which marketplaces you can add. Ask them to allowlist `nerymurillohnd/the-claude-factory` — see [Manage plugins for your organization](https://code.claude.com/docs/en/plugins/org).

</details>

## 📦 Installing a plugin

<details>
<summary><code>Marketplace "the-claude-factory" not found</code></summary>

The marketplace isn't added on this machine yet. Add it, then retry:

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
```

Or install in one step: `claude plugin install <plugin> --marketplace nerymurillohnd/the-claude-factory`.

</details>

<details>
<summary><code>Plugin "&lt;name&gt;" not found in marketplace "the-claude-factory"</code></summary>

1. Refresh your copy of the catalog: `claude plugin marketplace update the-claude-factory`.
2. Check the spelling against the [catalog](../README.md#-catalog) or `/plugin` → **Discover**.
3. Plugin names are lowercase with hyphens — the display name (with spaces) isn't the install name.

</details>

<details>
<summary><code>is already installed globally</code> / <code>is already installed (scope: user)</code></summary>

The first message comes from `/plugin install` in a session, the second from `claude plugin install` in your shell (which exits successfully). Either way the plugin is already installed at that scope — manage it from `/plugin` → **Installed**, or pass a different `--scope`.

</details>

<details>
<summary>The Claude app refuses to install the plugin</summary>

The plugin ships executables in a `bin/` folder, which the Claude app can't install. Use it from Claude Code instead — the plugin's **Compatibility** table says so.

</details>

## 🔌 Plugin installed but not working

Work through these in order:

1. **Is it enabled?** `/plugin` → **Installed**, or `claude plugin list` (look for `Status: ✔ enabled`).
2. **Any errors?** `/plugin` → **Errors** shows every load failure with a hint.
3. **Installed during this session?** Run `/reload-plugins`. It prints `Reloaded:` with counts of what loaded.
4. **Does it need setup?** If the summary says a bundled MCP server _needs configuration_, open `/plugin` → **Installed** → plugin → **Configure**. Plugins with their own settings show **Configure options** there too.
5. **Missing a tool it depends on?** Check the plugin README's **Prerequisites** section — some plugins need a CLI on your `PATH` or an API key, and it shows how to install each one.

<details>
<summary>A plugin from the Claude app doesn't appear in Claude Code</summary>

Claude Code (v2.1.273+) syncs plugins from your claude.ai account once each time it starts, in the background, and loads them as `<plugin>@synced`. If one is missing:

- **Signed in another way?** Plugins sync only in a session signed in with your claude.ai account. They don't sync when `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN` or an `apiKeyHelper` script supplies the credential, when `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set, in bare mode, with `--safe-mode`, or with a `--setting-sources` list that leaves out `user`.
- **Signed in on an older version?** Run `/login` again; the sync starts the next time you start Claude Code.
- **Turned on during this session?** It arrives at the next start. If the session says _Plugins changed_, run `/reload-plugins`.
- **Also installed from the marketplace?** Claude Code loads your marketplace copy and reports the synced one as not loaded. Disable the marketplace copy to use the one from the app.
- **Turned off for everything?** `"syncClaudeAiPlugins": false` in your settings, or in your organization's managed settings, stops every synced plugin.

</details>

<details>
<summary>A hook blocks a tool call or prompt</summary>

That's often the hook doing its job — the message explains what it caught. If you believe it's wrong, disable the plugin temporarily (`claude plugin disable <plugin>@the-claude-factory`) and [report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml) with the message.

</details>

<details>
<summary><code>This reload changes MCP tools … Run /reload-plugins --force to apply.</code></summary>

Adding an MCP server invalidates the prompt cache. Run `/reload-plugins --force`, or simply start a new session.

</details>

## 🔄 Updates not arriving

- `claude plugin update <plugin>@the-claude-factory` says _already at the latest version_: no new release has shipped yet — check the plugin's `CHANGELOG.md`.
- Updated but still seeing old behavior: the running session keeps the loaded version. Run `/reload-plugins` or start a new session.
- A plugin shown as `<plugin>@synced` came from the Claude app: update it there (**Customize** → **Plugins**), then start Claude Code again or run `/reload-plugins` when it says _Plugins changed_.
- Want updates without thinking about it: [enable auto-update](./managing-plugins.md#-auto-update).
- Auto-update is on but nothing changed yet: it runs once per interactive session, up to ten minutes after your first message. Run `claude plugin update <plugin>@the-claude-factory` to update now.
- **Enable auto-update** is missing from `/plugin`: `DISABLE_UPDATES`, `DISABLE_AUTOUPDATER` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set, which turns plugin auto-update off. Add `FORCE_AUTOUPDATE_PLUGINS=1` to keep plugin updates on, or update by hand.
- `Plugin "<plugin>" is not installed at scope user`: the plugin is installed for one project only. On Claude Code v2.1.281 and later, run the update from inside that project; on earlier versions, add `--scope project`.

## 🆘 Still stuck?

1. Search [existing issues](https://github.com/nerymurillohnd/the-claude-factory/issues?q=is%3Aissue) — someone may have hit it already.
2. [Open a bug report](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml) with the output of `claude --version`, `claude plugin list` and anything from `/plugin` → **Errors**.
3. Problem with Claude Code itself rather than a plugin? Report it to [anthropics/claude-code](https://github.com/anthropics/claude-code/issues).

The full official reference: [Troubleshoot plugins](https://code.claude.com/docs/en/plugins/troubleshooting).

---

<sub>⬅️ [Compatibility](./compatibility.md) · Next: [FAQ](./faq.md) ➡️</sub>
