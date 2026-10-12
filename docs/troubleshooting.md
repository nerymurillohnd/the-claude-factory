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
<summary>The add hangs or fails behind a proxy or firewall</summary>

Claude Code clones the repository with your local `git`. Confirm `git ls-remote https://github.com/nerymurillohnd/the-claude-factory.git` works from the same shell. If SSH to GitHub is blocked on your network, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` so Claude Code always clones over HTTPS.

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
<summary>Cowork refuses to install the plugin</summary>

The plugin ships executables in a `bin/` folder, which Cowork and Claude chat can't install. Use it from Claude Code instead — the plugin's **Compatibility** table says so.

</details>

## 🔌 Plugin installed but not working

Work through these in order:

1. **Is it enabled?** `/plugin` → **Installed**, or `claude plugin list` (look for `Status: ✔ enabled`).
2. **Any errors?** `/plugin` → **Errors** shows every load failure with a hint.
3. **Installed during this session?** Run `/reload-plugins`. It prints `Reloaded:` with counts of what loaded.
4. **Does it need setup?** If the summary says a bundled MCP server *needs configuration*, open `/plugin` → **Installed** → plugin → **Configure**. Plugins with their own settings show **Configure options** there too.
5. **Missing a tool it depends on?** Check the plugin README's **Requirements** table — some plugins need a CLI on your `PATH` or an API key.

<details>
<summary>A hook blocks a tool call or prompt</summary>

That's often the hook doing its job — the message explains what it caught. If you believe it's wrong, disable the plugin temporarily (`claude plugin disable <plugin>@the-claude-factory`) and [report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml) with the message.

</details>

<details>
<summary><code>This reload changes MCP tools … Run /reload-plugins --force to apply.</code></summary>

Adding an MCP server invalidates the prompt cache. Run `/reload-plugins --force`, or simply start a new session.

</details>

## 🔄 Updates not arriving

- `claude plugin update <plugin>@the-claude-factory` says *already at the latest version*: no new release has shipped yet — check the plugin's `CHANGELOG.md`.
- Updated but still seeing old behavior: the running session keeps the loaded version. Run `/reload-plugins` or start a new session.
- Want updates without thinking about it: [enable auto-update](./managing-plugins.md#-auto-update).

## 🆘 Still stuck?

1. Search [existing issues](https://github.com/nerymurillohnd/the-claude-factory/issues?q=is%3Aissue) — someone may have hit it already.
2. [Open a bug report](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml) with the output of `claude --version`, `claude plugin list` and anything from `/plugin` → **Errors**.
3. Problem with Claude Code itself rather than a plugin? Report it to [anthropics/claude-code](https://github.com/anthropics/claude-code/issues).

The full official reference: [Troubleshoot plugins](https://code.claude.com/docs/en/plugins/troubleshooting).

---

<sub>⬅️ [Compatibility](./compatibility.md) · Next: [FAQ](./faq.md) ➡️</sub>
