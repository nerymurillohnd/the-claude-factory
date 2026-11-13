# Commands

The plugin commands you run during documentation work. Each event file names the ones it needs; this file says what each one tells you and what it does not check.

These commands check the files a document is built from, or the document itself. Run them from the repository root and read the exit code (`0` passes, `1` fails), not the symbols: without a terminal, ✔ ⚠ ✘ print as √ ‼ ×.

| Command | When | What it tells you |
| :-- | :-- | :-- |
| `claude --version` and `claude plugin <subcommand> --help` | Before you rely on a flag in this table | The installed CLI is the authority on which flags exist |
| `claude plugin validate plugins/<plugin> --strict` | After a plugin's `plugin.json` changes, before you write a document that copies values from it | The manifest the documents copy values from is valid |
| `claude plugin validate . --strict` | After you change `marketplace.json` | The catalog is valid, and each entry's version agrees with its `plugin.json` |
| `claude plugin validate plugins/<plugin> --strict --profile directory` | After a plugin's README is written or rewritten | Exit `1` when the README is missing or too short for Anthropic's directory. Also read the `Advice` lines: one appears when the README has no install-from-marketplace line, and it never changes the exit code |
| `claude --plugin-dir plugins/<plugin> plugin details <name>` | Before you write or brief a plugin README for a new or changed plugin | The plugin's real component inventory, to check the README against. A mod's hooks module shows as `Hooks (0)` |
| `npm run check:consistency` | After any document that names a plugin, its version or its category changes | Exit `1` with one `PC-xx` line per finding: names across folder, `plugin.json` and the marketplace entry, `renames`, changelog headings against tags, an empty `[Unreleased]` on `main`, README placeholders, length, badge and install, update and uninstall commands, one catalog row per plugin at its version and category, each plugin's icon and SVG source, and its `documentationUrl`, `supportUrl` and `privacyPolicyUrl`. It doesn't check what the prose says |
| `npm run release:status` | Before you write a release's changelog section | The plugins whose version differs from `origin/main`, versions on `origin/main` with no tag, and declared dependencies with their ranges |
| `npm run release:changelog -- <plugin>` | At release, when the `plugin-releases` skill calls for it | Dates `## [Unreleased]` and writes the link references (`changelog.md` steps 4 and 5). It writes the file; it never writes the notes |
| `claude plugin list --json --data-size <plugin>` | Before you write a plugin README's Uninstall section, on an install made by `npm run check:install` or in a throwaway configuration where the plugin ran | The `dataDirSize` of the plugin's saved data directory, absent when it is missing or empty. A fresh install that never ran shows nothing, so search the plugin's hooks, scripts and modules too |
| `claude plugin tag plugins/<plugin> --dry-run` | Before you write a release's changelog section, on a committed tree (it exits `1` while any file under the plugin is uncommitted) | The version `plugin.json` and the marketplace entry agree on, and the tag name `<name>--v<version>` the changelog links use. It creates nothing |

Two things these commands do not do:

- A marketplace run (`validate .`) does not open each plugin's skills, agents, hooks or servers. Validate each changed plugin directory too.
- `claude plugin tag` creates no tag here. Tags and GitHub Releases belong to the `plugin-releases` skill.
