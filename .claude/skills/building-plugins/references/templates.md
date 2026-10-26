# Templates: what each asset is and how to work with it

This skill's `assets/` are the templates a new plugin of this repository is built from. They are the source: create from them, and change them here when what every new plugin gets should change.

## The assets

| Asset | Becomes | Placeholders | Filled by |
| :-- | :-- | :-- | :-- |
| `assets/plugin-template.json` | `plugins/<name>/.claude-plugin/plugin.json` | `{{name}}`, `{{displayName}}`, `{{description}}`, `{{category}}`, `{{surfacesJson}}` | This skill's `scaffold-plugin.py`, every one |
| `assets/CHANGELOG-template.md` | `plugins/<name>/CHANGELOG.md`, with its `0.1.0` section dated today | `{{name}}`, `{{displayName}}`, `{{date}}` | `scaffold-plugin.py`, every one |
| `assets/LICENSE-template` | `plugins/<name>/LICENSE` | none | Copied as is |
| `assets/README-template.md` | `plugins/<name>/README.md` | `<Display Name>`, `<plugin>`, `<owner>/<repo>`, `<marketplace-name>`, and every other `<…>` | `scaffold-plugin.py` fills the first four; you fill the rest |

`plugin-template.json` is not valid JSON until it is rendered (`{{surfacesJson}}` stands unquoted), so `biome.json` excludes it.

## Create from them

1. Run `scaffold-plugin.py` (step 2 of `SKILL.md`). Never copy another plugin's files, and never write these files by hand for a new plugin.
2. In the new `README.md`, replace every remaining `<…>` with the plugin's facts, in the style of `readme-style.md`. Delete a section only when it cannot apply, and say why in your hand-back.
3. Leave `plugin.json`'s `version` at `0.1.0` and the `CHANGELOG.md` `0.1.0` entry as the launch entry; versioning after that is the release procedure's.

## Change them

- Edit an asset only to change what every new plugin gets, and keep its placeholders: they are what a new plugin resolves. A new placeholder needs `scaffold-plugin.py` to fill it, or a line in step 2 above telling the author to.
- A change to an asset brings every plugin file built from it in line in the same change. Those files are plugin files, so that part goes through a pull request.
- After a change, scaffold a throwaway plugin in a scratchpad copy of the repository (`TCF_ROOT=<copy> scaffold-plugin.py …`) and read what it wrote.

## The older copies

`.claude/templates/plugin/` and `.claude/templates/root-readme.md` hold the templates this repository used before these assets. They stay, frozen, because older parts of the repository still read them until DEBT-011 closes: `check-repo.mjs` enforces the old README shape, and the repository's tests build their fixture from the old README. Never edit them and never create a plugin from them; when DEBT-011 closes they are removed.
