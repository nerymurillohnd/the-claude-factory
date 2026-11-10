# NOTICE template

<!-- Procedure: .claude/references/notice.md -->

Template of a `NOTICE.txt` file, for a plugin that bundles or derives from third-party material whose license requires its notices to travel with it. A plugin that contains only its own work has no NOTICE file.

- **Becomes:** `NOTICE.txt` at the plugin root, as plain text: the content of the block below.
- **Placeholders:** `{{name}}` (the plugin's name), `{{year}}`, `{{copyrightHolders}}` and `{{license}}` (the plugin's own license name, such as "MIT License"); for each source, `{{source}}`, `{{sourceUrl}}`, `{{sourceVersion}}`, `{{sourceLicense}}` (its SPDX identifier), one `{{derivedFile}}` line per derived or bundled file, and `{{sourceLicenseText}}` (the source's full license text, which keeps the copyright and permission notice its license requires).
- **Several sources:** repeat the block from "This plugin contains material derived from" through the license text once per source.
- **Keep it to the facts:** list only material the plugin actually contains, and only the notices its licenses require.

```text
{{name}}
Copyright (c) {{year}} {{copyrightHolders}}. Licensed under the {{license}} (see LICENSE).

This plugin contains material derived from {{source}}:

  Repository:  {{sourceUrl}}
  Version:     {{sourceVersion}}
  License:     {{sourceLicense}}

Derived files:

  {{derivedFile}}

{{sourceLicenseText}}
```
