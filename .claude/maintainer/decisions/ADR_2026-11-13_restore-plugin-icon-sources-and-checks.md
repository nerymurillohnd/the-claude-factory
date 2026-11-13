---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Restore the plugin icon sources and renderer, and check icons in check:consistency

## Scope

Every plugin's directory listing icon (`plugins/<plugin>/.claude-plugin/icon.png`, declared as `"icon": "./.claude-plugin/icon.png"`) and listing URLs (`documentationUrl`, `supportUrl`, `privacyPolicyUrl` in `plugin.json`); the sources in `scripts/generators/plugin-icons/<plugin>.svg`; the renderer `scripts/generators/plugin-icons.mjs` (`npm run icons:render`); and checks PC-09 and PC-10 in `scripts/validators/plugin_consistency/listing.py` (`npm run check:consistency`). Out of scope: the directory submissions themselves.

## Context and problem statement

On 2026-11-05 the owner made a directory icon mandatory for every plugin, drawn as one SVG per plugin on a shared frame, rendered by a maintainer script and checked by a validator (ADR_2026-11-05_every-plugin-ships-a-directory-icon). Commit `ced195b` (#104, 2026-11-13) deleted that ADR, the 22 SVG sources, the renderer and the validator, while all 22 plugins kept shipping their `icon.png`. Two maintainer documents still pointed at the deleted sources.

Evidence checked on 2026-11-13 with Claude Code 2.1.323, the latest release:

- `claude plugin validate --strict --profile directory` passed a plugin with no `icon` and one with a 100 x 60 px PNG; it failed only an icon path that is not a file (`ICON_INVALID`). The 2026-11-05 ADR relied on the `ICON_MISSING` warning of 2.1.318, which no longer appears; the changelog from 2.1.318 to 2.1.323 has no entry about it.
- The manifest reference says the directory reads `icon` and the URL fields from `plugin.json` only ([Directory listing fields](https://code.claude.com/docs/en/plugins/manifest-reference.md#directory-listing-fields)). Neither the [submission page](https://claude.com/docs/plugins/submit.md) nor the [pre-submission checklist](https://claude.com/docs/plugins/pre-submission-checklist.md) states icon dimensions or size limits.
- `plugin-engineering` was the only plugin without the three listing URLs.

How should the icon convention be kept now that nothing checks it?

## Decision drivers

- Keep the owner-approved icon design editable and reproducible.
- Detect a plugin that ships without a valid icon or listing URLs, since the CLI no longer does.
- Follow ADR_2026-11-13_five-scripts-cover-release-and-consistency-checks: one consolidated owner per mechanical check, no per-check scripts.

## Considered options

- **Restore the sources and the renderer, and add the icon and URL checks to `check:consistency` as PC-09 and PC-10**: chosen.
- **Restore `plugin-icons.py` as its own validator in `npm run validate`**: rejected by the owner because it reintroduces a per-check script, which the five-scripts ADR rejected.
- **Rely on `claude plugin validate`**: rejected because 2.1.323 no longer reports a missing or misshapen icon.

## Decision outcome

Chosen option: **restore the sources and renderer, check in `check:consistency`**, because it brings back the approved design with a tested owner for the check, inside the consolidated script.

### Consequences

- Good, because rendering the 22 restored sources gives PNGs byte-identical to the committed ones.
- Good, because PC-09 fails a listed plugin whose icon is undeclared, missing, outside the plugin, not a PNG, not square, outside 512 to 2048 px or over 2 MB, or has no SVG source, and a source with no plugin; PC-10 fails a missing or non-`https://` listing URL.
- Bad, because the 512 to 2048 px and 2 MB limits are a project convention: the only source for them is the 2.1.318 validator text, and no current official page states them.
- Bad, because `plugin-engineering` needs a version bump to add its three URLs.
- Neutral, because `npm run icons:render` needs Playwright's Chromium, ImageMagick and the JetBrains Mono font on the machine; the checks need none of them.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| PC-09 and PC-10 catch each failure | `npm run test:scripts`; the three new tests fail with both checks disabled | 2026-11-13: 239 tests OK; 3 of 3 fail with the checks disabled | Every change under `scripts/validators/plugin_consistency/` |
| The restored sources reproduce the shipped icons | `npm run icons:render`, then `git status plugins` | 2026-11-13: 22 rewritten, 0 changed | After any source edit |
| Every plugin passes PC-09 and PC-10 | `npm run check:consistency -- --offline` | 2026-11-13: only PC-10 on `plugin-engineering` (three URLs); pending its fix | After the `plugin-engineering` change |
| The directory still accepts these icons | The developer portal's Validate step on the first submission | pending | First submission |

## More information

- Decided by the owner on 2026-11-13: approval of the restoration, then the choice of `check:consistency` over a separate validator.
- ADR_2026-11-05_every-plugin-ships-a-directory-icon was deleted in `ced195b` and is not on disk, so this record cannot set its `superseded-by`; it restates that decision's design: a navy rounded square with a faint grid and a flat turquoise glyph per plugin, no text except the language labels of the LSP plugins, no Claude or third-party marks.
