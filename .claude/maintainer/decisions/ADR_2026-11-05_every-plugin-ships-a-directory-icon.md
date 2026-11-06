---
status: accepted
date: 2026-11-05
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# Every plugin ships a directory icon rendered from a maintainer-scope SVG

## Scope

The directory listing fields of every `plugins/<plugin>/.claude-plugin/plugin.json` (`icon`, `documentationUrl`, `supportUrl`, `privacyPolicyUrl`), the file `plugins/<plugin>/.claude-plugin/icon.png`, the icon sources in `scripts/generators/plugin-icons/`, the renderer `scripts/generators/plugin-icons.mjs`, the validator `scripts/validators/plugin-icons.py`, the shipped-file check in `scripts/check-repo.mjs` and the manifest schema in `scripts/schemas/plugin-manifest-schema/`. The submissions to Anthropic's directory themselves, and `.claude-plugin/marketplace.json`, are out of scope.

## Context and problem statement

Nery plans to submit the plugins to Anthropic's directory, one submission per plugin folder. On 2026-11-05, `claude plugin validate --strict` (Claude Code 2.1.318) passed all 21 plugins but reported the directory warning `ICON_MISSING` for each, and `PRIVACY_URL_MISSING` for svelte-development. The validator states that an icon must be a square PNG or JPEG of 512 to 2048 px, under 2 MB, inside the plugin, and that "that file may become the listing icon only once: the first time the plugin is saved or submitted in the developer portal". The manifest reference ([Directory listing fields](https://code.claude.com/docs/en/plugins/manifest-reference#directory-listing-fields)) says the directory reads `icon` and the four URL fields from `plugin.json` only, and that `claude plugin validate` reports them as unknown fields in a marketplace entry. The maintainer schema sets `additionalProperties: false` and did not list these fields, so `npm run validate` would reject them.

How should each plugin get an icon that is consistent, editable, free of third-party marks, and checked on every change?

## Decision drivers

- The first portal save fixes a listing icon for good, so icons must be final and reviewed before any submission.
- Anthropic's [Trademark Guidelines](https://www.anthropic.com/legal/trademark-guidelines) and the directory checklist hold listings that look like a known brand: no Claude or third-party logos.
- Maintainer files must not ship to users (CLAUDE.md, Maintainer and Plugin Scopes).
- Every check must run in the gates without adding a browser to CI or Husky.
- A new plugin must not reach users without an icon.

## Considered options

- **Hand-drawn SVG per plugin on one shared frame, rendered by a maintainer script, checked by a validator, mandatory for every plugin**: chosen.
- **AI-generated raster icons (Gemini, ChatGPT)**: rejected because they cannot be edited or regenerated identically, are hard to keep consistent across 21 plugins, and tend to imitate known logos.
- **One shared icon for every plugin**: rejected because listings would be indistinguishable in the directory.
- **Render inside the gates**: rejected because it would add Playwright and Chromium to CI and the pre-push hook.
- **Icons only for plugins sent to the directory**: rejected by Nery, who made the icon mandatory for every plugin, including future ones.

## Decision outcome

Chosen option: **hand-drawn SVG per plugin on one shared frame, rendered by a maintainer script, checked by a validator, mandatory for every plugin**, because it gives one recognizable family that stays editable and reproducible, keeps the sources out of users' caches, and lets a stdlib-only validator enforce the directory's rules on every push. Nery approved the style on 2026-11-05: a navy rounded square with a faint grid and a flat turquoise glyph per plugin, with no text other than the language labels of the four LSP plugins.

### Consequences

- Good, because `claude plugin validate --strict` reports no `ICON_MISSING` once each plugin carries its icon.
- Good, because the SVG sources and the renderer never ship to users; only the PNG does.
- Bad, because each plugin's cache grows by about 50 KB.
- Bad, because adding the icon and the URL fields changes `plugin.json` in all 21 plugins, which the version-bump gate (`scripts/release/check-version-bump.py`) answers with a patch bump and a release per plugin.
- Bad, because re-rendering needs the Playwright Chromium and the JetBrains Mono font on the maintainer's machine; the committed PNGs do not.

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| The directory crops icons to its own shape, cutting the transparent rounded corners | Not documented as of 2026-11-05 | A listing icon fixed with a poor crop | Check the portal preview on the first submission before saving | Nery |
| 256-color compression bands a gradient | Visible only at large sizes | Slight banding | Review the contact sheet at full size | Nery |
| `claude plugin validate --strict` on Claude Code below v2.1.281 reports the new fields as unknown | A user validates on an old build | A warning only; loading is unaffected | None needed | Nery |

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Every plugin has a declared, square, 512 to 2048 px icon under 2 MB | `npm run validate` (`plugin-icons.py`) | pending | Every push |
| No directory warning remains | `claude plugin validate plugins/<plugin> --strict` on all 21 | pending | Before each submission |

## More information

Decided by Nery on 2026-11-05 in the project thread on marketplace visibility, after reviewing a pilot icon and a contact sheet of all 21. The privacy policy that `privacyPolicyUrl` points to is a separate decision: ADR_2026-11-05_plugins-share-one-root-privacy-policy.
