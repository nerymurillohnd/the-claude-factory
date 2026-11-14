---
paths:
  - "scripts/generators/plugin-icons/**"
  - "scripts/generators/plugin-icons.mjs"
  - "plugins/*/.claude-plugin/icon.png"
  - "scripts/validators/plugin_consistency/listing.py"
---

# Plugin icons

- Load the `plugin-icons` skill before drawing, changing, rendering, renaming, removing or reviewing an icon.
- Change an icon only through its SVG source in `scripts/generators/plugin-icons/<plugin>.svg` and `npm run icons:render`, never by editing the PNG.
- Get the owner's approval on a contact sheet before committing a new or changed icon.
