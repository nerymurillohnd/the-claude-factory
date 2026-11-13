---
paths:
  - "scripts/generators/plugin-icons/**"
  - "scripts/generators/plugin-icons.mjs"
  - "plugins/*/.claude-plugin/icon.png"
  - "scripts/validators/plugin_consistency/listing.py"
---

# Plugin icons

Every plugin ships `.claude-plugin/icon.png`, rendered from `scripts/generators/plugin-icons/<plugin>.svg` on the owner-approved shared frame.

- Load the `plugin-icons` skill before drawing, changing, rendering, renaming, removing or reviewing an icon or its source.
- Change an icon only through its SVG source and `npm run icons:render`, never by editing the PNG, so every icon can be rendered again identically.
- Keep one source per listed plugin and no other: `npm run check:consistency` (PC-09) fails a missing or stray source.
- Get the owner's approval on a contact sheet before committing a new or changed icon.
