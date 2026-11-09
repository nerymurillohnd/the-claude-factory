# Anthropic's marketplaces

Anthropic's official and community plugin marketplaces for Claude Code: their names, repositories, how a user adds each, and where to browse their plugins. Use this to explain how users find plugins, and how a third-party marketplace such as a public GitHub one differs.

## Contents

- [Browse and install from Anthropic's marketplaces](#browse-and-install-from-anthropics-marketplaces)
- [Third-party marketplaces](#third-party-marketplaces)
- [Documentation References](#documentation-references)

## Browse and install from Anthropic's marketplaces

A user searches Anthropic's marketplaces for a plugin in Claude Code, on the web, or on GitHub:

* **In Claude Code, by browsing**: run `/plugin` in an interactive session. Its **Discover** tab lists the plugins from the user's marketplaces.
* **In Claude Code, by name**: run `/plugin install <name>` in a session, which looks the name up in the user's marketplaces. If the plugin is in one of them, its details open in the `/plugin` panel, and nothing installs until the user chooses an [installation scope](https://code.claude.com/docs/en/plugins/install.md#install-a-plugin) and confirms there. If it isn't, Claude Code shows `Plugin "<name>" not found in any marketplace`.

To install from the desktop app or from a script, or to see what a cloud session loads, read [Install plugins](https://code.claude.com/docs/en/plugins/install.md).

For `not found` errors and marketplaces that won't add, read [Troubleshoot plugins](https://code.claude.com/docs/en/plugins/troubleshooting.md#install-a-plugin).

## Third-party marketplaces

Many popular plugins aren't in any Anthropic marketplace. They're in their authors' own marketplaces, usually a GitHub repository with a `.claude-plugin/marketplace.json` at its root.

Anthropic doesn't review third-party marketplaces, so users should read [Plugin security and trust](https://code.claude.com/docs/en/plugins/security.md) before adding one.

To use a third-party marketplace, add its repository in a Claude Code session with `/plugin marketplace add <owner>/<repo>`, then install with `/plugin install <plugin>@<marketplace-name>`. The marketplace name is the `name` field of that `marketplace.json`, and Claude Code prints it once it has added the marketplace.

For other ways to add a marketplace, read [Add a marketplace](https://code.claude.com/docs/en/plugins/install.md#add-a-marketplace).

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/anthropic-marketplaces
- https://code.claude.com/docs/en/plugins/install.md: install a plugin from one of these marketplaces, choose a scope, and add a marketplace by other sources
- https://code.claude.com/docs/en/plugins/troubleshooting.md: `not found` errors and marketplaces that won't add
- https://code.claude.com/docs/en/plugins/security.md: what a plugin can do on a user's machine and how to review one before installing it
- https://code.claude.com/docs/en/plugins/create-marketplace.md: run your own marketplace alongside Anthropic's
