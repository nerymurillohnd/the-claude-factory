# plugin.json template

<!-- Procedure: .claude/references/plugin-manifest.md -->

Template of a plugin's manifest.

- **Becomes:** `.claude-plugin/plugin.json` inside the plugin: the content of the block below.
- **Placeholders:** `{{name}}` (kebab-case plugin name), `{{displayName}}`, `{{version}}` (`0.1.0` for a new plugin), `{{description}}` (one sentence), `{{authorName}}`, `{{authorUrl}}`, `{{homepageUrl}}`, `{{repositoryUrl}}`, `{{iconPath}}` (an image inside the plugin; this marketplace uses `./.claude-plugin/icon.png`), `{{documentationUrl}}`, `{{supportUrl}}`, `{{privacyPolicyUrl}}`, `{{license}}` (an SPDX identifier, such as `MIT`), `{{keyword}}` (one discovery tag per array item), `{{category}}` and `{{surfacesJson}}` (a JSON array of surface ids, such as `["claude-code"]`).
- **Not valid JSON until rendered:** `{{surfacesJson}}` stands unquoted.
- **Directory listing fields:** `icon`, `documentationUrl`, `supportUrl`, `privacyPolicyUrl` and the optional `termsOfServiceUrl` (not in the block; add it only when a terms of service exists) are read by Anthropic's plugin directory; Claude Code ignores them. Set them only in `plugin.json`, never in the marketplace entry. Each URL is `https://`.
- **Component keys:** add `userConfig`, `dependencies`, `hooks`, `mcpServers` and the other component keys after `keywords` only when the plugin needs them.

```json
{
  "name": "{{name}}",
  "displayName": "{{displayName}}",
  "version": "{{version}}",
  "description": "{{description}}",
  "author": {
    "name": "{{authorName}}",
    "url": "{{authorUrl}}"
  },
  "homepage": "{{homepageUrl}}",
  "repository": "{{repositoryUrl}}",
  "icon": "{{iconPath}}",
  "documentationUrl": "{{documentationUrl}}",
  "supportUrl": "{{supportUrl}}",
  "privacyPolicyUrl": "{{privacyPolicyUrl}}",
  "license": "{{license}}",
  "keywords": ["{{keyword}}"],
  "metadata": {
    "category": "{{category}}",
    "surfaces": {{surfacesJson}}
  }
}
```
