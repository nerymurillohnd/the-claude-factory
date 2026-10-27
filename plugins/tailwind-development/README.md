<div align="center">

# 🌊 Tailwind CSS Development

<p><strong>Designs, builds and refactors Tailwind CSS v4 interfaces with a product designer's craft, and grounds every utility, variant and configuration in its exact official documentation page before verifying the result in your project.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Ftailwind-development%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude%20app-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Development-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.292-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Install](#-installation) •
[Usage](#-usage) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

> [!TIP]
> **TL;DR** — Ask for a component, a page or a redesign in a Tailwind project, and Claude designs it like a product designer (clear hierarchy, real design-system tokens, every state covered) instead of the generic generated look; every utility it writes is checked against the official page for your installed Tailwind version and proven with your build.

## ✨ Why use it

- **Interfaces that look designed** — Claude ranks what matters before it adds colour, styles actions by importance, presents data by meaning instead of label-value walls, groups with space, and frames images and numbers properly, then checks the result against a list of generic-UI tells.
- **A design system, not one-off values** — type scale, spacing subset, OKLCH colour ramps, elevation and radius live as `@theme` tokens; your project's own tokens, brand and rules always come first.
- **Seen, not assumed** — when your environment can render, Claude screenshots each appearance mode at narrow and wide widths and measures rendered contrast against WCAG 2.2 AA, and tells you which checks it could not run.
- **Classes that exist in your version** — Claude reads your resolved Tailwind version from the lockfile and checks each utility, variant and directive against the official page for it, so v3 habits don't leak into a v4 project, or the reverse.
- **The right page, not a close guess** — a built-in index of all 222 pages of the Tailwind docs, the 19 framework installation guides included, maps each need to its exact page, and to the exact section of the long concept pages, because page names don't follow class names: `blur` lives on `filter-blur`, and `drop-shadow` on `filter-drop-shadow`.
- **Styles that actually ship** — complete, statically detectable class strings instead of interpolated names, no broad safelists to hide a missing class, and your existing tokens reused before new ones are added.
- **Checked, not assumed** — Claude runs your project's own build, lint and tests, inspects generated CSS when syntax is uncertain, and tells you exactly what it verified and what it didn't.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `tailwind-development:tailwind-ui-design` | Builds, refactors and reviews interfaces with a product designer's craft: reads your tokens and components first, checks the systems exist, composes hierarchy before colour, depth and finish, covers every state, verifies the rendered result and critiques it against generic-UI tells | Automatically when you build, redesign, polish or review a page, view or component in a Tailwind project, or `/tailwind-development:tailwind-ui-design` |
| 🎯 Skill | `tailwind-development:tailwind-official-docs` | Reads your installed Tailwind version and setup, plans the exact official page for each utility family, variant and configuration the task touches, implements the change and verifies it with your project's own checks | Automatically when the question is how Tailwind works or how to write something in it (classes, variants, `@theme`, missing styles, setup, upgrades), and whenever the design skill needs exact syntax; or `/tailwind-development:tailwind-official-docs` |

## ✅ Requirements

| Requirement             | Details                                                                   |
| :---------------------- | :------------------------------------------------------------------------ |
| **Claude Code**         | v2.1.292 or later — check with `claude --version`   |
| **Surfaces**            | See [Compatibility](#-compatibility)                                      |
| **External tools**      | None. Claude uses your project's own package manager and scripts to verify changes. Optional: the Context7 MCP server, which Claude queries first for the docs when you have it |
| **Accounts / API keys** | None                                                                      |
| **Network**             | See [What this plugin runs and sends](#-what-this-plugin-runs-and-sends)  |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install tailwind-development --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install tailwind-development@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

No GitHub SSH key? Set this first, so installs from `/plugin` and updates use HTTPS:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install tailwind-development --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install tailwind-development@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<details>
<summary><b>🖥️ Claude app (web and desktop)</b></summary>

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Tailwind CSS Development** in **Discover** and select **Add**.

In the desktop app's **Code** tab you can also click **+** next to the prompt box → **Add plugins** (or **Plugins** → **Browse plugins**), or open **Settings** → **Plugins** → **Discover**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

## 🚀 Usage

You don't need to call anything: `tailwind-ui-design` loads when you build, redesign or review an interface or change how something looks, and `tailwind-official-docs` when the question is Tailwind syntax, behaviour, setup or an upgrade; the design skill hands every syntax question to the docs skill. To call one directly, type `/tailwind-development:tailwind-ui-design` or `/tailwind-development:tailwind-official-docs` followed by your request.

### Redesign a view that looks generic

```text
Our settings page looks like every template: identical cards, the same shadow everywhere, nothing stands out. Make it look designed.
```

**Result:** Claude reads your `@theme` tokens, brand sources and nearby components, screenshots the current page, and works through the view from the biggest problem down: what should read first, which action is primary, labels that only repeat what the value says, spacing that doesn't group anything, values that should be tokens. It keeps your brand, behaviour and markup semantics, adds the states that were missing, and shows before and after screenshots with the contrast it measured.

### Review a design before it ships

```text
Review the new pricing section for design problems. Don't change anything yet.
```

**Result:** a prioritized list of findings, ranking first and polish last, each with the file, the line and the fix, including the generic-UI tells the section shows and the states it doesn't cover.

### Build a component

```text
Add a responsive product grid: one column on phones, three from md up, cards with a hover lift and a visible focus ring, and dark mode.
```

**Result:** Claude reads your Tailwind version and how dark mode is set up, then reads `display`, `grid-template-columns`, `gap`, `responsive-design`, `hover-focus-and-other-states`, `dark-mode` and the shadow or outline page for the focus ring. It writes complete class strings, runs your build and checks, and reports the pages each decision rests on.

### Add Tailwind to a project

```text
Add Tailwind to this SvelteKit app.
```

**Result:** Claude reads your framework and package manager, opens the official SvelteKit guide and follows its steps exactly, with your package manager's install command. For a framework without its own guide, it uses the Vite plugin, the PostCSS plugin or the CLI, depending on what your project already has. Then it adds one test class to a page and confirms it renders.

### Fix styles that never appear

```text
The bg-${color}-500 classes on my badges don't show up in production.
```

**Result:** Claude reads `detecting-classes-in-source-files`, explains why a class built from a template string is never generated, and replaces it with complete class names in a lookup map, instead of adding a broad safelist.

### Upgrade from v3

```text
We're moving this project from Tailwind 3 to 4. What breaks?
```

**Result:** Claude starts from `upgrade-guide` and the `installation/*` page for your integration, lists the renamed and removed utilities your code uses, the PostCSS and CLI package changes and the new browser baseline, and changes nothing until you agree to the plan.

### Style a Svelte, Vue or Astro component

```text
Use @apply inside the <style> block of Button.svelte.
```

**Result:** Claude reads `compatibility` and `functions-and-directives`, tells you Tailwind recommends avoiding `<style>` blocks, and when you keep one adds the `@reference` to your global stylesheet that `@apply` needs, or uses your theme's CSS variables instead.

## 🔍 What this plugin runs and sends

- **Hooks:** none.
- **MCP servers:** none. When you already have the Context7 MCP server connected, Claude queries it first for Tailwind's docs; the plugin doesn't install or configure it.
- **Network:** the plugin makes no calls itself. Claude reads documentation pages from `tailwindcss.com` (and `v3.tailwindcss.com` or older versioned sites for older projects) with its own web fetch tool, or through Context7 when you have it, each under your usual permission prompts. The requests carry the page address or a short docs query, never your code.
- **Files written:** none by the plugin. Claude edits your project files only as the task asks, like any other edit. When it checks a design visually, it uses the browser or screenshot tools you already have, under your usual permission prompts.

## 🔄 Updating

```bash
claude plugin update tailwind-development@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Tailwind CSS Development** → **Update now**. Then run `/reload-plugins`.

Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `tailwind-development@synced`: update and uninstall it in the app (**Customize** → **Plugins**); in `/plugin` you can only turn it on or off, unless your organization requires it.

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall tailwind-development@the-claude-factory
```

Installed with `--scope project`? Add `--scope project` here too. Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you pass `--keep-data`.

In a session: `/plugin` → **Installed** → **Tailwind CSS Development** → **Uninstall**. In the Claude app: **Customize** → **Plugins** → **Tailwind CSS Development** → its menu → **Remove**.

The plugin keeps no data and writes no files, so nothing is left behind.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component                              |                         Claude Code                          |                                                                                                                                          Claude app                                                                                                                                           |
| :------------------------------------- | :----------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| 🎯 Skills                              |                              ✅                              |                                                                                                                                              ✅                                                                                                                                               |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/tailwind-development:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>How does it work with Anthropic's frontend-design skill?</b></summary>

They complement each other. `frontend-design` sets the aesthetic direction: the identity, the typefaces, the look. `tailwind-ui-design` supplies the craft beneath it (hierarchy, systems, colour ramps, depth, states, verification) and its Tailwind v4 implementation. Without `frontend-design`, Claude takes the direction from your project's brand or brief.

`tailwind-ui-design` works best with `frontend-design` installed; it doesn't depend on it, and this plugin never installs it for you.

</details>

<details>
<summary><b>Will it override our brand or design system?</b></summary>

No. Your project's tokens, brand sources and design rules always win; the skill's defaults apply only where your project leaves a choice open. When it needs a value your system lacks, it adds a token instead of a one-off value, and tells you.

</details>

<details>
<summary><b>Does it work without Context7 or web access?</b></summary>

Yes, with less certainty. Without Context7, Claude fetches the official pages with its web fetch tool. With no documentation tool at all, Claude says that verification is blocked and doesn't present what it remembers as checked documentation.

</details>

<details>
<summary><b>My project is on Tailwind 3. Does it push me to v4?</b></summary>

No. Claude reads the version your lockfile resolves and uses that version's official docs, such as `v3.tailwindcss.com` for v3. It never upgrades Tailwind to make an example work; an upgrade happens only when you ask for one.

</details>

<details>
<summary><b>Does Claude fetch a page for every class it writes?</b></summary>

No. It reads each page once per session and reuses it. A lookup is required for a utility family new to the task, a feature that changed in v4, and any syntax it isn't sure of.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 📖 [Claude Code skills](https://code.claude.com/docs/en/skills)
- 🌊 [Tailwind CSS documentation](https://tailwindcss.com/docs/installation/using-vite)
- 📘 [Refactoring UI](https://www.refactoringui.com), for a book-length treatment of interface design craft

## 🙏 Sources and credits

- **[Tailwind CSS documentation](https://tailwindcss.com/docs)**, © Tailwind Labs Inc. The skills send Claude to these pages; their index lists the site's page URLs and section headings so Claude can open the right one. No documentation text or example is reproduced.
- **[Tailwind CSS](https://github.com/tailwindlabs/tailwindcss)** (MIT, © Tailwind Labs, Inc.): its release posts, changelog and GitHub releases answer version questions, and its package READMEs and CLI behaviour informed the skills. No code is copied.
- **[frontend-design](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design)** by Anthropic, the complementary skill for aesthetic direction.
- **[Refactoring UI](https://www.refactoringui.com)** by Adam Wathan and Steve Schoger, recommended as further reading. The design skill reflects established interface-design practice in its own words and is not derived from the book.

See [NOTICE.txt](./NOTICE.txt) for the details.

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=tailwind-development) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=tailwind-development) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=tailwind-development)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. Third-party sources and their licenses are listed in [NOTICE.txt](./NOTICE.txt). Not affiliated with or endorsed by Tailwind Labs Inc. _Tailwind CSS_ is a trademark of Tailwind Labs Inc.
