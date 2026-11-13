# License

How to create a `LICENSE` file from `assets/LICENSE-template.md`.

## Produces

`LICENSE`, all caps, at the repository root and at the root of each plugin. GitHub detects the license only from the repository root (it reads no `LICENSE` from `.github/` and has no account-wide default for it) and shows it in the sidebar and on the License tab.

## When

- When the repository is created, and when each plugin is created.
- Never edited afterwards, except to change the license, which is a breaking change for users.

## Sources

Read 2026-11-10:

- choosealicense.com `_licenses/mit.txt` (the text GitHub's license picker inserts): "Replace [year] with the current year and [fullname] with the name (or names) of the copyright holders."
- SPDX License List, `MIT`.
- GitHub Docs, "Adding a license to a repository" and "Licensing a repository" (`github/docs` at `f309096`): type `LICENSE` or `LICENSE.md` (with all caps); GitHub uses Licensee, which compares the `LICENSE` file with known license texts.
- Claude Code docs `plugins/manifest-reference`: `license` is an SPDX identifier such as `MIT`.

## Placeholders

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{year}}` | Year of first publication | The year the work was first published; keep it when the file is copied later |
| `{{copyrightHolders}}` | Name, or names, of the copyright holders | The legal name of the author or organization, as the author decides it |

## Procedure

1. Copy the content of the template's `text` block, and nothing else, into `LICENSE`.
2. Replace `{{year}}` and `{{copyrightHolders}}`.
3. Set `plugin.json` `license` to the same SPDX identifier (`MIT`).
4. Run the checks.

## Rules

Official:

- The license text stays byte for byte as published: no rewrapping, no Markdown, no added lines. A changed text stops GitHub's detection.
- The file name is `LICENSE` (with all caps), with no extension or `.md`/`.txt`.

This repository:

- Every plugin ships its own `LICENSE`, because each plugin is copied alone into the user's cache. Write it as a real file, never as a symlink to the root `LICENSE`: files outside the plugin's folder are not copied.
- The copyright holder is the same in the root `LICENSE`, every plugin `LICENSE`, every `NOTICE.txt` and every README License line.

## Checks

- The repository's sidebar names "MIT license" after the push.
- `diff` against the choosealicense text after reverting the copyright line shows no difference.
- `claude plugin validate --strict plugins/<plugin>`: the manifest's `license` is accepted.

## Never

- Never invent a copyright holder or a year.
- Never reformat the license text.
