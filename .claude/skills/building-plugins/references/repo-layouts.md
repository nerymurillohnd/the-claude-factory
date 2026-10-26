# Repo layouts, marketplace.json and names

Checked 2026-10-25 against `/en/plugins/publish`, `/en/plugins/create-marketplace`, `/en/plugins/host-marketplace`, `/en/plugins/marketplace-reference`, `/en/plugins/manifest-reference` (Claude Code v2.1.310).

## Contents
- Choose a layout
- Layout A: one plugin per repo
- Layout B: a marketplace repo with several plugins
- marketplace.json fields
- Plugin sources for a GitHub marketplace
- Names: plugin, marketplace, reserved
- How users add and install

## Choose a layout

| Situation | Layout |
| :-- | :-- |
| One plugin, its own repo, its own release cadence | A: the plugin at the repo root with a one-entry `marketplace.json` beside its `plugin.json` |
| Several plugins one author or team maintains together | B: a marketplace repo, each plugin under `plugins/<name>/` as a relative-path entry |
| A catalog that points at plugins living in other repos | B with `github` or `git-subdir` entries instead of relative paths |

A plugin repo without any `marketplace.json` can still be cloned and loaded with `--plugin-dir`, but users can't install it by name or update it with a command. For a public GitHub audience, always add the marketplace file.

## Layout A: one plugin per repo

```text
deploy-helper/                 ← repo root = plugin root = marketplace root
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/<skill>/SKILL.md
├── agents/<agent>.md
├── hooks/hooks.json
├── scripts/                   ← executables called by hooks, never a top-level bin/ unless Claude Code-only
├── .mcp.json
├── README.md
├── LICENSE
└── CHANGELOG.md
```

```json
{
  "name": "deploy-helper",
  "owner": { "name": "Your Name", "url": "https://github.com/you" },
  "description": "One-line description of the marketplace",
  "plugins": [
    { "name": "deploy-helper", "source": "./" }
  ]
}
```

The entry's `source` is `"./"`, the repo root, and its `name` matches `plugin.json`. Running `claude plugin validate .` in this directory validates both the marketplace and the plugin (v2.1.289+).

## Layout B: a marketplace repo

```text
my-marketplace/                ← marketplace root (the directory that contains .claude-plugin/)
├── .claude-plugin/marketplace.json
├── plugins/
│   ├── formatter/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/…
│   │   ├── README.md
│   │   └── LICENSE
│   └── reviewer/…
├── README.md                  ← marketplace README: add command + catalog
└── LICENSE
```

```json
{
  "name": "my-marketplace",
  "owner": { "name": "Your Name" },
  "description": "Plugins for …",
  "plugins": [
    { "name": "formatter", "source": "./plugins/formatter", "description": "…", "category": "development" },
    { "name": "reviewer",  "source": "./plugins/reviewer",  "description": "…" }
  ]
}
```

Rules that cause most failed installs:

- Relative paths resolve from the marketplace root, not from `.claude-plugin/`. They start with `./`, use forward slashes, and never contain `..` (validation rejects it). A path to a missing directory passes validation and fails only at install with `Source path does not exist`.
- From a marketplace directory, `claude plugin validate` doesn't open the skill, agent, command or hook files of plugins in other directories. Validate each plugin directory too.
- With `metadata.pluginRoot` (v2.1.239+) entries can use bare names under that directory.
- Keep the plugin in a subdirectory if the repo has large git submodules a build uses: Claude Code (v2.1.295+) fetches only submodules inside a plugin's directory, but a plugin at the root that refers to any submodule path pulls every submodule.
- Symlinks: a link that stays inside the plugin is kept; one to elsewhere in the same marketplace is copied in; one leaving the marketplace is skipped.

## marketplace.json fields

Required: `name`, `owner` (with `owner.name`), `plugins`. Useful optional top-level fields: `description` (validate warns when missing), `renames`, `forceRemoveDeletedPlugins`, `allowCrossMarketplaceDependenciesOn`, `metadata.pluginRoot`, `$schema` (ignored at load).

Entry fields beyond `name` and `source`: `description`, `version` (avoid; see versioning), `category`, `tags`, `strict` (default `true`), `relevance`, `dependencies`, `defaultEnabled`, `displayName`, `metadata` (v2.1.222+), `headers`/`headersHelper` (archive sources only). An entry also accepts the `plugin.json` fields, except the directory-listing ones (`icon`, `documentationUrl`, `supportUrl`, `privacyPolicyUrl`, `termsOfServiceUrl`), which `validate` reports as unknown there. An entry that sets `headersHelper` must also set `"strict": false`.

- Unknown keys are ignored at load and reported by `validate` as warnings, so a typo loads silently. Run `--strict`.
- For an entry with a relative-path source, Claude Code reads the plugin's `plugin.json` before install for display fields; for any other source type users see only the entry's own fields until they install. In a catalog of remote plugins, put `description` on the entry.
- `strict: true` (default): `plugin.json` is the authority and entry component fields are appended to it, except `hooks`, whose matchers replace the manifest's per event. `strict: false`: when the plugin has a `plugin.json`, any component field in the entry makes the plugin fail to load. Prefer declaring components only in the plugin.
- Hooks written in an entry must be an inline object; a path there passes validation but never runs.

## Plugin sources for a GitHub marketplace

| Source | When | Minimal value |
| :-- | :-- | :-- |
| Relative path | Plugin lives in this repo | `"./plugins/formatter"` |
| `github` | Plugin is its own GitHub repo | `{ "source": "github", "repo": "owner/formatter" }` |
| `git-subdir` | Plugin is a folder of another repo | `{ "source": "git-subdir", "url": "owner/monorepo", "path": "tools/formatter" }` |
| `url` | Any git host by full URL | `{ "source": "url", "url": "https://gitlab.com/g/formatter.git" }` |

`github`, `url` and `git-subdir` accept `ref` (branch or tag) and `sha` (full 40-char lowercase commit). Pinning `sha` makes the entry serve exactly that commit, which is what curated public catalogs do; it also means every release needs a catalog edit. `npm`, `archive` (v2.1.224+) and `command` (v2.1.229+) sources exist but are rarely right for a GitHub-hosted public plugin.

## Names

### Plugin `name` (in `plugin.json` and the entry)

- Kebab-case: lowercase letters, digits, hyphens. No spaces, `@`, `:`, path separators, control or bidi characters. The entry name may use `.` and `_` too, but stay with kebab-case so `validate` doesn't warn and the directory accepts it (up to 64 characters, starting and ending with a letter or digit).
- Error from `validate`: starts with `claude-`, `anthropic-`, `anthropics-` or `cc-plugin-`; is `claude`, `anthropic`, `anthropics`, `claude-code` or `claude-mods`; puts `official` beside `claude`/`anthropic`. Warning: `claude`/`anthropic` as a whole word elsewhere (`mcp-for-claude`).
- It prefixes every skill and agent (`/deploy-helper:hello`, `deploy-helper:reviewer`), so pick one that reads well as a prefix.
- It is permanent. Use `displayName` for a human label.

### Marketplace `name`

- Letters, digits, `.`, `_`, `-`, starting with a letter or digit, no `..`. A user can register only one marketplace per name.
- Reserved and refused: the official and community names (`claude-plugins-official`, `claude-code-marketplace`, `claude-code-plugins`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `anthropic-agent-skills`, `knowledge-work-plugins`, `life-sciences`, `claude-for-legal`, `claude-for-financial-services`, `financial-services-plugins`, `first-party-plugins`, `claude-tag-plugins`, `claude-community`, `claude-plugins-community`, `healthcare`, `anthropic-plugin-directory`, `claude-plugin-directory`) unless sourced from `github.com/anthropics/`; look-alikes such as `official-claude-plugins` or `claude-plugins-v2`; any non-ASCII name; other spellings of a reserved name (`claude.code.plugins`); `inline`, `builtin`, `skills-dir`, `synced`, `claude-plugin-test`; `npm`, `pip`, `uv`, `cargo`, `github`, `gh` in any casing; JavaScript object member names (`constructor`, `toString`, …); names starting with `claudeai-`.
- A marketplace added from `owner/repo` downloads into a folder named `<owner>-<repo>`. Don't name a different marketplace exactly that (refused since v2.1.290).
- `validate` passes the exact official names; the refusal appears only at `marketplace add`. Check the list yourself.

## How users add and install

Users add by GitHub shorthand; Claude Code takes the marketplace name from the file, not the repo:

```bash
claude plugin marketplace add owner/repo            # prints: Successfully added marketplace: <name>
claude plugin install <plugin>@<marketplace-name>
# one command, shell, v2.1.292+:
claude plugin install <plugin> --marketplace owner/repo
# one command, inside a session, v2.1.275+:
/plugin install <plugin> --marketplace owner/repo
```

`owner/repo#ref` (or `@ref`) pins a branch or tag of the catalog. `owner/repo` always means github.com; GitHub Enterprise and other hosts need the full git URL.

To register the marketplace for everyone working in one repository, run `claude plugin marketplace add owner/repo --scope project` there and commit the `.claude/settings.json` it writes; teammates get it once they trust the folder.
