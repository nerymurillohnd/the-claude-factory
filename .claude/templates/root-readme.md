# Root README blueprint

Canonical section order and intent for `README.md`. Edit `README.md` directly following this blueprint; never hand-edit the generated `<!-- catalog:* -->` and `<!-- plugin-count:* -->` blocks — run `node .github/scripts/catalog.mjs`.

| # | Section | Intent | Rules |
| :-- | :-- | :-- | :-- |
| 0 | Hero (centered `<div>`) | Banner, one-line promise, component line, badges, quick nav | Badges: plugin count (generated), Validate, License, Claude Code. No more than 4 |
| 1 | 🏭 What is The Claude Factory? | Why this marketplace is worth adding | 2-column value table: Focused, Validated, Versioned, Documented, Open |
| 2 | ⚡ Quick start | Add marketplace → install → use | `<details>` per surface (Terminal open by default); one-step install tip with min versions |
| 3 | 📦 Catalog | Generated from `marketplace.json` + manifests | Category index table, then one table per category |
| 4 | 🔧 Manage your plugins | Update, auto-update, disable, uninstall, remove marketplace | Terminal vs in-session table; Cowork paragraph; removal warning |
| 5 | 🧭 Where plugins work | Cross-surface compatibility matrix | Must match `docs/compatibility.md` and the official platform-support page |
| 6 | 🛡️ Trust & safety | How to review before installing | Link Security policy |
| 7 | 📚 Documentation | Table of guides | Every file in `docs/` listed |
| 8 | 💬 Support | Issue forms table | Note: no pull requests, issues welcome |
| 9 | 📝 Changelog | Root vs per-plugin changelogs | |
| 10 | 📄 License | MIT, non-affiliation and trademark note | |

## Never include

- Maintenance workflow, `.claude/` contents, scripts, CI internals, release mechanics.
- Roadmap dates or promises.
- Plugin details beyond the catalog row — those live in each plugin README.
