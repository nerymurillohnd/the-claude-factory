# <Display Name>

<One or two sentences: what the plugin does for the user and when it helps.>

Works in: Claude Code<, claude.ai and Cowork — list only the surfaces that load every component this plugin needs>.

## Install

```bash
claude plugin marketplace add <owner>/<repo>
claude plugin install <plugin>@<marketplace-name>
```

Or in one step: `claude plugin install <plugin> --marketplace <owner>/<repo>` (Claude Code 2.1.292+), or inside a session `/plugin install <plugin> --marketplace <owner>/<repo>` (2.1.275+).

No GitHub SSH key? Set this first, so installs from `/plugin` and updates use HTTPS:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

## Update

Auto-update is off for this marketplace until you turn it on (`/plugin` → Marketplaces → <marketplace-name> → Enable auto-update). To update now:

```bash
claude plugin update <plugin>@<marketplace-name>
```

Then run `/reload-plugins` in any open session.

## Prerequisites

- <tool> — <why it's needed>. Install: `<command>` (macOS), `<command>` (Linux). <Alternatives.>

## Configuration

| Option | What it sets | Default |
| :-- | :-- | :-- |
| `<key>` | <description> | <default> |

Set options when installing (`claude plugin install <plugin>@<marketplace-name> --config <key>=<value>`) or later with `/plugin configure <plugin>@<marketplace-name>`.

## Usage

- `/<plugin>:<skill>` — <what it does>
- Or just ask, for example: "<a prompt that triggers the skill>"

## What this plugin runs and sends

- **Hooks:** `<Event>` on `<matcher>` runs `scripts/<file>`, which <what it does>.
- **MCP servers:** `<server>` — <command or URL>, <what it's used for>.
- **Network:** <every destination and the data sent there, or "none">.
- **Files written:** <paths, including anything under the plugin data directory, or "none">.

## Uninstall

```bash
claude plugin uninstall <plugin>@<marketplace-name>
```

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you pass `--keep-data`.

## License

<SPDX id> — see [LICENSE](LICENSE).
