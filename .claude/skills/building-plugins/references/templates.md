# Templates: what each asset is and how to work with it

This skill's `assets/` are the templates a new plugin of this repository is built from. They are the source: create from them, and change them here when what every new plugin gets should change.

## The assets

| Asset                          | Becomes                                                                                        | Placeholders                                                                                                                                                                                                                                                                                                                                         | Filled by                                                                             |
| :----------------------------- | :--------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------ |
| `assets/plugin-template.json`  | `plugins/<name>/.claude-plugin/plugin.json`                                                    | `{{name}}`, `{{displayName}}`, `{{description}}`, `{{category}}`, `{{surfacesJson}}`                                                                                                                                                                                                                                                                 | This skill's `scaffold-plugin.py`, every one                                          |
| `assets/CHANGELOG-template.md` | `plugins/<name>/CHANGELOG.md`, with its `0.1.0` section dated today                            | `{{name}}`, `{{displayName}}`, `{{date}}`                                                                                                                                                                                                                                                                                                            | `scaffold-plugin.py`, every one                                                       |
| `assets/LICENSE-template`      | `plugins/<name>/LICENSE`                                                                       | none                                                                                                                                                                                                                                                                                                                                                 | Copied as is                                                                          |
| `assets/README-template.md`    | `plugins/<name>/README.md`                                                                     | Lowercase, filled by the scaffold: `<plugin>`, `<owner>/<repo>` and its URL-encoded `<owner>%2F<repo>`, `<marketplace-name>`, `<description>`, `<category-badge>`, `<surfaces-badge>`, `<surfaces-text>`, and the `<app>` / `<code-only>` blocks it keeps or drops by surface; plus `<Display Name>`. Every other `<…>` starts with a capital letter | `scaffold-plugin.py` fills the lowercase ones and `<Display Name>`; you fill the rest |
| `assets/NOTICE-template.txt`   | `plugins/<name>/NOTICE.txt`, only when the plugin bundles or derives from third-party material | `{{name}}`, `{{source}}`, `{{sourceUrl}}`, `{{sourceVersion}}`, `{{sourceLicense}}`, `{{derivedFile}}`, `{{sourceLicenseText}}`                                                                                                                                                                                                                      | You, by hand; the scaffold never writes it                                            |

`plugin-template.json` is not valid JSON until it is rendered (`{{surfacesJson}}` stands unquoted), so `biome.json` excludes it.

## Create from them

1. Run `scaffold-plugin.py` (step 2 of `SKILL.md`). Never copy another plugin's files, and never write these files by hand for a new plugin.
2. In the new `README.md`, replace every remaining `<…>` with the plugin's facts, in the style of `readme-style.md`. Delete a section only when it cannot apply, and say why in your hand-back.
3. When the plugin bundles or derives from third-party material, copy `NOTICE-template.txt` to `plugins/<name>/NOTICE.txt` and fill it: `{{name}}` is the plugin's name; for each source, its name, repository URL, version or commit, SPDX license, every file of the plugin derived from it (one `{{derivedFile}}` line each), and its full license text. For several sources, repeat the block from "This plugin contains material derived from" through the license text once per source. The file opens with the plugin's own copyright and license; keep that line.
4. Leave `plugin.json`'s `version` at `0.1.0` and the `CHANGELOG.md` `0.1.0` entry as the launch entry; versioning after that is the release procedure's.

Which README sections are required is the open question of DEBT-011: `check-repo.mjs` requires ten sections (`REQUIRED_PLUGIN_SECTIONS` in `scripts/lib.mjs`), and this template has its own. Until DEBT-011 closes, follow this template, which outranks the older checks, and say in your hand-back that `check-repo.mjs` will flag the sections it expects; this skill does not run it.

## Change them

- Edit an asset only to change what every new plugin gets, and keep its placeholders: they are what a new plugin resolves. A new placeholder needs `scaffold-plugin.py` to fill it, or a line in steps 2 or 3 above telling the author to.
- A change to an asset brings every plugin file built from it in line in the same change. Those files are plugin files, so that part goes through a pull request.
- After a change, scaffold a throwaway plugin in a scratchpad copy of the repository (`TCF_ROOT=<copy> scaffold-plugin.py …`) and read what it wrote.

## The older copies

`.claude/templates/plugin/` and `.claude/templates/root-readme.md` hold the templates this repository used before these assets. They stay, frozen, because older parts of the repository still read them until DEBT-011 closes: `check-repo.mjs` enforces the old README shape, and the repository's tests build their fixture from the old README. Never edit them and never create a plugin from them; when DEBT-011 closes they are removed.
