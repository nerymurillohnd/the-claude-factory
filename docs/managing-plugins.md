# 🔧 Managing plugins

> Keep plugins from **The Claude Factory** up to date, turn them on and off, and remove them cleanly.

**On this page:** [Updates](#-updates) · [Auto-update](#-auto-update) · [Enable & disable](#️-enable--disable) · [Uninstall](#️-uninstall) · [Remove the marketplace](#-remove-the-marketplace) · [Inspect a plugin](#-inspect-a-plugin) · [Cowork](#-in-cowork)

---

## 🔄 Updates

Every plugin here declares a semantic version. You receive a new release when the plugin's version changes and you update — on request, or automatically if you turn on [auto-update](#-auto-update).

| Do this | 💻 Terminal | 💬 In a session |
| :-- | :-- | :-- |
| Update one plugin | `claude plugin update <plugin>@the-claude-factory` | `/plugin` → **Installed** → plugin → **Update now** |
| Update every plugin from this marketplace | — | `/plugin` → **Marketplaces** → **the-claude-factory** → **Update marketplace** |
| Refresh the catalog only | `claude plugin marketplace update the-claude-factory` | `/plugin marketplace update the-claude-factory` |

> [!NOTE]
> A running session keeps the version it already loaded. After an update you'll see `Plugin updated: <name> · Run /reload-plugins to apply`; the next session loads the new version automatically.

Wondering what changed? Each plugin's `CHANGELOG.md` lists every release, and every release also appears on the [Releases page](https://github.com/nerymurillohnd/the-claude-factory/releases).

## 🔁 Auto-update

Auto-update is **off by default** for third-party marketplaces, including this one. Turn it on once and Claude Code refreshes the marketplace after each session starts and updates the plugins you installed from it:

1. Run `/plugin`.
2. Open **Marketplaces** → select **the-claude-factory**.
3. Select **Enable auto-update**.

## ⏯️ Enable & disable

Disabling keeps the plugin installed but stops it from loading — handy for trying a session without it.

```bash
claude plugin disable <plugin>@the-claude-factory
claude plugin enable <plugin>@the-claude-factory
```

In a session: `/plugin` → **Installed**, select the plugin and press **Space**.

## 🗑️ Uninstall

```bash
claude plugin uninstall <plugin>@the-claude-factory                 # user scope
claude plugin uninstall <plugin>@the-claude-factory --scope project # project scope
```

In a session: `/plugin` → **Installed** → plugin → **Uninstall**. If the repository's `.claude/settings.json` enables the plugin, Claude Code asks whether to **disable it for you** (`y`) or **uninstall it for everyone** (`u`).

Dependencies that were installed automatically stay until you run `claude plugin prune`.

## 🧹 Remove the marketplace

```bash
claude plugin marketplace remove the-claude-factory
```

> [!WARNING]
> Removing the marketplace **uninstalls every plugin** you installed from it and removes their entries from your settings.

## 🔍 Inspect a plugin

| Question | Command |
| :-- | :-- |
| What's installed, which version, which scope? | `claude plugin list` |
| What does a plugin add, and how many tokens does it cost each session? | `claude plugin details <plugin>` |
| Which plugins haven't I used lately? | `/plugin` → **Installed** → **Not used recently** |
| Why didn't something load? | `/plugin` → **Errors** |

## 🤝 In Cowork

Everything lives under **Customize** → **Plugins**:

- **Update** — click **Update** on the marketplace to pull the latest versions. Cowork warns you before an update overwrites files you edited locally.
- **Turn components on or off** — open the installed plugin and toggle its skills, connectors, agents or hooks.
- **Uninstall** — open the plugin and click **Uninstall**.

In Claude Code (v2.1.273+, signed in with the same claude.ai account), these plugins appear as `<plugin>@synced`. Update and uninstall them here; in `/plugin` you can only turn them on or off, unless your organization requires them. Claude Code picks up changes when it starts; if it says *Plugins changed*, run `/reload-plugins`.

---

<sub>⬅️ [Installation](./installation.md) · Next: [Compatibility](./compatibility.md) ➡️</sub>
