---
name: plugin-icons
description: Designs, draws, renders, reviews and checks the directory listing icon of every plugin in this marketplace, on the owner-approved shared frame. Use whenever a new plugin needs its icon, an icon should be redesigned, re-rendered or reviewed, a plugin is renamed or removed and its icon source must follow, check:consistency reports PC-09, or plugins are being prepared for Anthropic's directory, even if the request only says "make it a logo" or "it needs a picture".
---

# Plugin icons

Each plugin ships one icon, `plugins/<plugin>/.claude-plugin/icon.png`, which Anthropic's directory shows on the plugin's listing. All 22 icons share one frame and one style, so a new icon has to look like part of the family, and nothing about it can be generated in a way that can't be reproduced. The decision and its evidence are in `.claude/maintainer/decisions/ADR_2026-11-13_restore-plugin-icon-sources-and-checks.md`.

## The pieces

| Piece | Path | Ships to users |
| :-- | :-- | :-- |
| Source, one per plugin | `scripts/generators/plugin-icons/<plugin>.svg` | No |
| Renderer | `npm run icons:render [-- <plugin>...]` (`scripts/generators/plugin-icons.mjs`) | No |
| Rendered icon | `plugins/<plugin>/.claude-plugin/icon.png`, 1024 × 1024, 256 colors, about 50 KB | Yes |
| Declaration | `"icon": "./.claude-plugin/icon.png"` in `plugin.json`, next to `documentationUrl`, `supportUrl` and `privacyPolicyUrl` | Yes |
| Check | `npm run check:consistency` (PC-09 icon and source, PC-10 listing URLs) | No |

The renderer needs Playwright's Chromium, ImageMagick and the JetBrains Mono font; the check needs none of them. `claude plugin validate` only reports an icon path that isn't a file, so PC-09 is the only check of size, shape and source.

## The style

The owner approved this style; keep every new icon inside it:

- **Frame:** a navy rounded square with a faint grid and a thin light border. Every source carries the same frame markup, byte for byte, up to and including the `<rect … rx="212" …/>` border line. Never edit the frame in one icon.
- **Glyph:** one flat, centered symbol that names what the plugin does, drawn after the border line and filled or stroked with the turquoise gradient `url(#g)` (`#5EEAD4` to `#14B8A6`). Keep it inside roughly x 200 to 824 and y 200 to 840, the span the gradient covers.
- **Lines:** strokes of about 44 to 56 units with `stroke-linecap="round"` and `stroke-linejoin="round"`, so a glyph reads at 32 px.
- **Details on the glyph:** navy `#0F1E33` at 0.25 to 0.45 opacity for cut-outs and inner lines, white at low opacity for highlights.
- **Text:** none, except a short language label (`$_`, `.py`, `.ts`, a version digit) in JetBrains Mono for a language plugin.
- **No marks of others:** no Claude, Anthropic or third-party logo or lookalike. The directory holds listings that look like a known brand.
- **Distinct:** at 48 px the new glyph must not be mistaken for another plugin's icon in the family.

Never use an AI image generator or a raster file as a source: the icon could not be edited or rendered again identically, and generated images tend to imitate known logos.

## Make a new plugin's icon

1. **Choose the glyph** from the plugin's purpose (its `description` and category), and show the owner one or two ideas in words before drawing.
2. **Start from the closest existing source**: copy it to `scripts/generators/plugin-icons/<plugin>.svg`, keep everything up to and including the border line, and replace only what follows it with the new glyph, closing with `</g></svg>`. Copying keeps the frame identical without a second template to drift.
3. **Render it**: `npm run icons:render -- <plugin>`. It writes `plugins/<plugin>/.claude-plugin/icon.png` and stops with the reason on a missing source or tool.
4. **Show the owner a contact sheet** of the new icon next to the whole family at review sizes, and wait for approval before any commit. From the repository root, with a scratchpad folder as `<out>`:

   ```bash
   args=(); for d in plugins/*/; do args+=(-label "$(basename "$d")" "$d.claude-plugin/icon.png"); done
   montage "${args[@]}" -resize 160x160 -geometry +14+10 -tile 6x -background white -pointsize 12 <out>/icons-160.png
   montage plugins/<plugin>/.claude-plugin/icon.png -resize 48x48 -geometry +8+8 <out>/new-48.png
   montage plugins/<plugin>/.claude-plugin/icon.png -resize 32x32 -geometry +8+8 <out>/new-32.png
   ```

   Read the images yourself before sending them, and fix a glyph that blurs at 32 px or looks like a sibling at 48 px.
5. **Declare it** in `plugin.json` as `"icon": "./.claude-plugin/icon.png"`, with the three listing URLs in the same order as the other manifests.
6. **Check it**: `npm run check:consistency -- --offline` reports no PC-09 or PC-10 for the plugin, and `claude plugin validate --strict --profile directory plugins/<plugin>` passes.
7. **Commit** the source (maintainer scope, no pull request) and the plugin's files separately. The icon and the declaration are part of the plugin's next version: version it with the `plugin-versioning` skill; for a new plugin they ship in its `0.1.0`.

## Other icon tasks

- **Redesign one icon:** steps 1 to 6 on its existing source. A shipped plugin's new `icon.png` changes the plugin, so it needs a patch bump and a pull request.
- **Re-render the family** (after a font or renderer change): `npm run icons:render`, then `git status plugins`. Unchanged sources must give byte-identical PNGs; any other difference is a regression to explain to the owner before committing.
- **Rename a plugin:** with the `plugin-catalog-changes` skill, rename its source to the new name in the same change, or PC-09 reports a missing source and a stray one.
- **Remove a plugin:** delete its source in the same change, or PC-09 reports it as stray.
- **Audit:** run `npm run check:consistency -- --offline` and review the contact sheet at 160, 48 and 32 px against the style above.
- **Prepare a directory submission:** run `claude plugin validate --strict --profile directory plugins/<plugin>`, then, in the developer portal's **Listing details** step, ask the owner to check the icon preview. Whether the portal crops the transparent rounded corners is undocumented; report what the preview shows.

## Size limits

PC-09 enforces a square PNG of 512 to 2048 px under 2 MB. These limits come from the text of `claude plugin validate` 2.1.318; no current official page states them, so treat them as this project's convention and report any portal finding that contradicts them.
