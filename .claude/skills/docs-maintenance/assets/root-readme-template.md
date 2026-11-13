# Root README blueprint

<!-- Procedure: references/documents/root-readme.md -->

Section order, intent and rules of a plugin marketplace's root `README.md`, its front page. The README is written once and then edited section by section against this blueprint, never rebuilt. The blocks a generator writes ({{generatedBlocks}}) are never edited by hand: run `{{generateCommand}}`.

- **Placeholders:** `{{generatedBlocks}}` (the HTML comment markers that fence the generated blocks), `{{generateCommand}}` (the command that rewrites them), `{{marketplaceDisplayName}}`, `{{ciBadges}}` (the status badges of the workflows that validate the marketplace), `{{compatibilityPage}}` (the page that holds the component × surface matrix), `{{securityPolicy}}` (the `SECURITY.md` path), `{{contributionPolicy}}` (whether pull requests are accepted or only issues) and `{{license}}`.

| #   | Section                        | Intent                                                      | Rules                                                                                                                                                                 |
| :-- | :----------------------------- | :---------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0   | Hero (centered `<div>`)        | Banner, one-line promise, component line, badges, quick nav | Badges: plugin count (generated), {{ciBadges}}, License, Claude Code; no more than 5. The component line names every component type the catalog ships              |
| 1   | {{emoji}} What is {{marketplaceDisplayName}}? | Why this marketplace is worth adding         | 2-column value table, one row per promise the marketplace keeps                                                                                                       |
| 2   | ⚡ Quick start                 | Add marketplace → install → use                             | `<details>` per surface (Terminal open by default); one-step install tip with its minimum Claude Code version                                                         |
| 3   | 📦 Catalog                     | Generated from `marketplace.json` and the plugin manifests  | Category index table, then one table per category                                                                                                                     |
| 4   | 🔧 Manage your plugins         | Update, auto-update, disable, uninstall, remove marketplace | Terminal vs in-session table; Claude paragraph; removal warning                                                                                                       |
| 5   | 🧭 Where plugins work          | Cross-surface compatibility matrix                          | Two columns (Claude Code, Claude) plus the note on where Claude can run tasks; identical to {{compatibilityPage}}                                                     |
| 6   | 🛡️ Trust & safety              | How to review before installing                             | Follows the official "Review a plugin before you install" guidance; links {{securityPolicy}}                                                                          |
| 7   | 📚 Documentation               | Table of guides                                             | Every marketplace guide in `docs/`, plus the official plugin docs. A file in `docs/` that serves one plugin is linked from that plugin's README, not from here        |
| 8   | 💬 Support                     | Issue forms table                                           | States {{contributionPolicy}}                                                                                                                                         |
| 9   | 📝 Changelog                   | Root vs per-plugin changelogs                               |                                                                                                                                                                       |
| 10  | 📄 License                     | {{license}}, non-affiliation and trademark note             |                                                                                                                                                                       |
| 11  | Footer (centered `<div>`)      | Sign-off and a way back up                                  | One `<sub>` line ending in a **Back to top** link                                                                                                                     |

## Never include

- The maintainer's workflow, `.claude/` contents, scripts, CI internals or release mechanics.
- Roadmap dates or promises.
- Plugin details beyond the catalog row: those live in each plugin's README.
