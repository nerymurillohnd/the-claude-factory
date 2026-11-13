# Notice

How to create a plugin's `NOTICE.txt` from `assets/NOTICE-template.md`.

## Produces

`plugins/<plugin>/NOTICE.txt`: the plugin's own copyright line, then each third-party source the plugin contains, with the notices its license requires.

## When

- Only when the plugin bundles or derives from third-party material (code, documentation, data). A plugin that contains only its own work has no NOTICE file.
- In the same change that adds, removes or updates a source.

## Sources

Read 2026-11-10:

- Apache Software Foundation, "Assembling LICENSE and NOTICE files": the files "must exactly represent the contents of the distribution they reside in"; only components actually included have any bearing on them; for MIT and BSD dependencies "there is no need to modify NOTICE" under normal circumstances, while the license itself must travel with the material. (The ASF writes this for Apache products; it is the closest published practice, not a requirement on MIT projects.)
- choosealicense.com `_licenses/mit.txt`: the MIT condition "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."

## Placeholders

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{name}}` | Plugin name | `plugin.json` `name` |
| `{{year}}`, `{{copyrightHolders}}` | The plugin's own copyright line | The plugin's `LICENSE` |
| `{{license}}` | The plugin's license name, such as "MIT License" | The plugin's `LICENSE` |
| `{{source}}` | Name of the third-party work | Its repository or site |
| `{{sourceUrl}}` | Repository or site URL | The source |
| `{{sourceVersion}}` | Version, tag or commit used | The exact revision read, with its date |
| `{{sourceLicense}}` | SPDX identifier of the source's license | The source's `LICENSE` |
| `{{derivedFile}}` | One line per file of the plugin derived from or bundling the source | The plugin's files |
| `{{sourceLicenseText}}` | The source's full license text, which keeps the copyright and permission notice its license requires | The source's `LICENSE`, verbatim |

## Procedure

1. Confirm the plugin contains third-party material; if it does not, stop.
2. Copy the template's `text` block into `plugins/<plugin>/NOTICE.txt`.
3. Fill the plugin's own copyright line from its `LICENSE`.
4. For each source, fill one block, from "This plugin contains material derived from" through the license text. For a source with no license, state that, quote what its owner states, and list exactly what the plugin takes from it.
5. Add the README License line's NOTICE sentence ("Parts are derived from … ; see NOTICE.txt") and a Credits entry.
6. Run the checks.

## Rules

Official:

- List only material the plugin actually contains, and only the notices its licenses require.
- Keep each source's license text verbatim.
- What each license requires (read the source's own license text every time):
  - MIT: keep the copyright notice and the permission notice with all copies or substantial portions; copy the source's full MIT text with its own copyright line.
  - BSD-2-Clause and BSD-3-Clause: keep the copyright notice, the list of conditions and the disclaimer. BSD-3-Clause also forbids using the holder's or contributors' names to endorse or promote the plugin, so never write the source's name as an endorsement.
  - CC-BY-4.0: keep the creator's identification, the copyright notice, notices referring to the license and to the disclaimer, and a link to the material where practicable; say whether it was modified; state the license with its text or a link.
  - Another license: apply what its text requires, and report any requirement the template can't carry.
  - No license: it grants no right to redistribute. Write no entry; report the source so the owner asks its author for permission or removes the material.
- Material the plugin only reads at run time, downloads, links to or follows as an approach isn't contained in it and has no entry.

This repository:

- The file is `NOTICE.txt`, plain text, at the plugin root.
- The copyright holder matches the plugin's `LICENSE`.

## Checks

- Every `{{derivedFile}}` path exists in the plugin (`ls`).
- Every `{{sourceVersion}}` names an exact revision.
- `grep -n '{{' plugins/<plugin>/NOTICE.txt` returns nothing.

## Never

- Never list a source the plugin does not contain.
- Never paraphrase a license.
