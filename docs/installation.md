# 📥 Installation guide

> Add **The Claude Factory** to Claude and install its plugins — on every surface, step by step.

**On this page:** [Before you start](#-before-you-start) · [Terminal](#-terminal) · [Claude Code session](#-inside-a-claude-code-session) · [Desktop app](#️-claude-desktop-app--code-tab) · [VS Code](#-vs-code) · [JetBrains](#-jetbrains) · [Cowork](#-cowork) · [Choose a scope](#-choose-an-install-scope) · [Teams](#-set-it-up-for-a-whole-team) · [Verify](#-verify-the-install)

---

## ✅ Before you start

| You need | Notes |
| :-- | :-- |
| **Claude Code** *or* the **Claude desktop app** with Cowork | Claude Code runs in the terminal, the desktop app's **Code** tab, VS Code and JetBrains. |
| A recent Claude Code version | Run `claude --version`. One-step installs need **v2.1.292+** in the shell and **v2.1.275+** in a session. |
| Network access to `github.com` | The marketplace is a public GitHub repository; no GitHub account or token is needed. |

Two names to remember:

| Name | Used for |
| :-- | :-- |
| `nerymurillohnd/the-claude-factory` | The **source** — what you type when you *add* the marketplace. |
| `the-claude-factory` | The **marketplace name** — what goes after `@` when you *install*: `<plugin>@the-claude-factory`. |

## 💻 Terminal

```bash
# 1. Add the marketplace (once per machine)
claude plugin marketplace add nerymurillohnd/the-claude-factory

# 2. Install a plugin (user scope by default)
claude plugin install <plugin>@the-claude-factory
```

Or do both in one command (v2.1.292+):

```bash
claude plugin install <plugin> --marketplace nerymurillohnd/the-claude-factory
```

Plugins installed from the shell load the next time you start Claude Code, or right away in an open session after `/reload-plugins`.

## 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install <plugin>@the-claude-factory
```

`/plugin install` opens the plugin's details instead of installing immediately: review **Will install** (the skills, agents, hooks and servers it adds), then choose a [scope](#-choose-an-install-scope).

> [!TIP]
> Prefer browsing? Run `/plugin`, open **Discover**, type to search, and press **Enter** on a plugin.
> One step (v2.1.275+): `/plugin install <plugin> --marketplace nerymurillohnd/the-claude-factory`.

## 🖥️ Claude desktop app — Code tab

In a local or SSH session:

1. Click **+** next to the prompt box → **Plugins** → **Add plugin**.
2. Find the plugin and select it.
3. Choose a scope.

Manage installed plugins later from **+** → **Plugins** → **Manage plugins**. The plugin browser isn't available in the desktop app's cloud sessions.

> [!NOTE]
> The desktop app's local sessions, the terminal and VS Code on the same computer share the same settings files — a plugin installed at user scope in one is available in the others.

## 🧩 VS Code

1. Type `/plugins` in the Claude Code prompt box to open **Manage plugins**.
2. On the **Marketplaces** tab, add `nerymurillohnd/the-claude-factory`.
3. On the **Plugins** tab, search for the plugin and click **Install**, then choose a scope.

Open sessions reload their plugins after you save changes.

## 🧱 JetBrains

The JetBrains plugin runs Claude Code in the IDE's terminal, so follow the [Terminal](#-terminal) or [session](#-inside-a-claude-code-session) steps there.

## 🤝 Cowork

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add marketplace** and enter `nerymurillohnd/the-claude-factory` (the full `https://github.com/nerymurillohnd/the-claude-factory` URL also works).
3. Plugins from The Claude Factory now appear alongside other marketplaces. Select one and click **Install**.

A plugin you install on your claude.ai account in Cowork also appears in Claude Code as a synced plugin (`<plugin>@synced`) at your next session start (Claude Code v2.1.273+, signed in with the same claude.ai account); if it says *Plugins changed*, run `/reload-plugins`. If you also install the same plugin in Claude Code, Claude Code loads that copy and reports the synced one as not loaded; disable your terminal copy to use the one from the app.

> [!IMPORTANT]
> Not every component loads in Cowork. Check the plugin's **Compatibility** table first — see [Compatibility](./compatibility.md).

## 🎯 Choose an install scope

| Scope | Who gets the plugin | Recorded in |
| :-- | :-- | :-- |
| **User** *(default)* | You, in every project on this machine | `~/.claude/settings.json` |
| **Project** | Everyone who works in this repository | `.claude/settings.json` (commit it) |
| **Local** | You, in this repository only | `.claude/settings.local.json` |

From the shell, pass `--scope project` or `--scope local`:

```bash
claude plugin install <plugin>@the-claude-factory --scope project
```

When the same plugin is set at several scopes, local overrides project, and project overrides user.

## 👥 Set it up for a whole team

Declare the marketplace and the plugins in your repository's `.claude/settings.json` and commit it. Once a teammate trusts the folder, Claude Code registers the marketplace for them in the background:

```json
{
  "extraKnownMarketplaces": {
    "the-claude-factory": {
      "source": { "source": "github", "repo": "nerymurillohnd/the-claude-factory" }
    }
  },
  "enabledPlugins": {
    "<plugin>@the-claude-factory": true
  }
}
```

Plugins in this marketplace live inside the repository, so they load from the marketplace copy once those settings apply. If a teammate still sees `Plugin "<plugin>" is enabled in project settings but isn't installed here` in `/plugin` → **Errors**, they run `claude plugin install <plugin>@the-claude-factory --scope project` once. Cloud sessions never show the trust dialog, so they don't pick up these entries. Organization-wide rollout through managed settings is covered in the [official docs](https://code.claude.com/docs/en/plugins/org).

## 🔎 Verify the install

```bash
claude plugin list                 # shows <plugin>@the-claude-factory with Status: ✔ enabled
claude plugin details <plugin>     # lists the components and their context cost
```

In a session, type `/<plugin>:` to see the plugin's skills. Something missing? See [Troubleshooting](./troubleshooting.md).

---

<sub>⬅️ [Back to the README](../README.md) · Next: [Managing plugins](./managing-plugins.md) ➡️</sub>
