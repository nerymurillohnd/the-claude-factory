# Plugin manifest

How to create a plugin's `plugin.json` from `.claude/templates/plugin-template.md`.

## Produces

`plugins/<plugin>/.claude-plugin/plugin.json`: the plugin's identity, version, listing fields and catalog metadata.

## When

- When the plugin is created.
- In every change to its version, description, components, `userConfig`, dependencies, category or surfaces.

## Sources

Read 2026-11-10:

- Claude Code docs `plugins/manifest-reference`: `name` is the only required key ("Use kebab-case"); `homepage` "Must parse as a URL, or the plugin fails to load"; `license` is an SPDX identifier; `metadata` is a free-form object Claude Code doesn't read; `icon`, `documentationUrl`, `supportUrl`, `privacyPolicyUrl` and `termsOfServiceUrl` are read by Anthropic's directory, ignored by Claude Code, set only in `plugin.json` (a marketplace entry reports them as unknown fields), `icon` a path to an image inside the plugin and each URL `https://`; `claude plugin validate` stops reporting them as unknown from v2.1.281.
- `.claude/skills/building-plugins/references/manifest-and-components.md` (this repository): `license` (SPDX) or a `LICENSE` file is required by Anthropic's directory; each `userConfig` option needs `type`, `title` and `description`, unknown option keys fail validation, and `"sensitive": true` masks the value and keeps it in the platform's credential store.
- Claude Code docs `plugins/manifest-reference` → `name`: the reserved-name errors (`claude-`, `anthropic-` prefixes, `official` beside `claude` or `anthropic`) and warnings.

## Placeholders

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{name}}` | Kebab-case plugin name, permanent | Chosen once; equals the directory name |
| `{{displayName}}` | Name shown in UI | Chosen |
| `{{version}}` | `0.1.0` for a new plugin | Then only through the bump procedure |
| `{{description}}` | One sentence, what the plugin does | Written for `/plugin` |
| `{{authorName}}`, `{{authorUrl}}` | Author | The publisher |
| `{{homepageUrl}}`, `{{documentationUrl}}` | The plugin README URL | This repository: `…/tree/main/plugins/<name>#readme` |
| `{{repositoryUrl}}` | Repository URL | The marketplace repository |
| `{{iconPath}}` | Icon path inside the plugin | This repository: `./.claude-plugin/icon.png`, rendered from `scripts/generators/plugin-icons/<name>.svg` |
| `{{supportUrl}}` | Where users get help | This repository: `…/issues/new/choose` |
| `{{privacyPolicyUrl}}` | The privacy policy | This repository: `…/blob/main/PRIVACY.md` |
| `{{license}}` | SPDX identifier | The plugin's `LICENSE` |
| `{{keyword}}` | Discovery tags, one per item | The plugin's purpose |
| `{{category}}` | Category id | `scripts/categories.json` (skill `plugin-categories`) |
| `{{surfacesJson}}` | JSON array of surface ids, unquoted in the template | `["claude-code"]` or `["claude-code", "claude-app"]`, per `docs/compatibility.md` |

## Procedure

1. Copy the template's `json` block into `plugins/<plugin>/.claude-plugin/plugin.json`.
2. Fill every value; `{{surfacesJson}}` becomes a real JSON array.
3. Add component keys (`userConfig`, `dependencies`, `hooks`, `mcpServers` and the rest) after `keywords`, only when the plugin needs them. A credential goes in `userConfig` with `"sensitive": true`, never in a file.
4. Add `termsOfServiceUrl` only when a terms of service exists.
5. Run `npm run generate` so `marketplace.json` and the catalog pick the plugin up.
6. Run the checks.

## Rules

Official:

- `name` is required, kebab-case, with no reserved form.
- `homepage` must parse as a URL; directory URLs are `https://`.
- Directory listing fields only in `plugin.json`, never in the marketplace entry.

This repository:

- `version` lives only in `plugin.json`; the marketplace entry and `marketplace.json` carry none.
- `metadata.category` and `metadata.surfaces` are set on every plugin; `npm run generate` copies the category into the marketplace entry and the catalog.
- Every plugin ships `.claude-plugin/icon.png`, declared as `"icon": "./.claude-plugin/icon.png"`.
- `scripts/schemas/` is strict: a field its schema lacks fails validation; add it to the schema from the official docs.

## Checks

- `claude plugin validate --strict plugins/<plugin>` and `claude plugin validate --profile directory plugins/<plugin>`.
- `npm run validate` and `npm run generate:check`.

## Never

- Never rename `name` after publication without the rename procedure.
- Never put `version` in the marketplace entry.
