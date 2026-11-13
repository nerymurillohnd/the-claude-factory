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
| `claude plugin tag plugins/<plugin> --dry-run` | Before you write a release's changelog section, on a committed tree (it exits `1` while any file under the plugin is uncommitted) | The version `plugin.json` and the marketplace entry agree on, and the tag name `<name>--v<version>` the changelog links use. It creates nothing |

Two things these commands do not do:

- A marketplace run (`validate .`) does not open each plugin's skills, agents, hooks or servers. Validate each changed plugin directory too.
- `claude plugin tag` creates no tag here. Tags and GitHub Releases belong to the `plugin-releases` skill.
