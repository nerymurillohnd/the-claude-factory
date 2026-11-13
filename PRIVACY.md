# Privacy Policy

**Effective date:** 13 November 2026

This policy covers every plugin published in The Claude Factory marketplace (`github.com/nerymurillohnd/the-claude-factory`). It explains what data the plugins collect, how that data is used and how long it is kept, and which third-party services a plugin can send data to on your behalf.

## Who runs the marketplace

The marketplace and its plugins are written and maintained by Nery Murillo ([github.com/nerymurillohnd](https://github.com/nerymurillohnd)), who is responsible for this policy.

## What the author collects

Nothing. No plugin in this marketplace sends data to the author or to any server the author runs:

- no telemetry, analytics, crash reports or usage statistics;
- no accounts, sign-ups or licence checks;
- no server operated by the author or by this marketplace.

The author receives only what you choose to post in a [GitHub issue](https://github.com/nerymurillohnd/the-claude-factory/issues), under [GitHub's privacy statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement).

## What stays on your machine

Plugins run inside your own Claude Code session, with your permissions. What a plugin reads or writes on your machine stays there. Each plugin's README lists the files it reads and writes, the commands it runs and how long anything it keeps lasts, in its **What this plugin runs and sends** section.

Some plugins keep small files in their own data folder or in a temporary folder, such as a marker that a notice was already shown, and delete them as their README describes. None of them sends those files anywhere.

## Third-party services

Some plugins connect to services that their own operators run. When they do, the data goes straight from your machine to that service, under that service's own policy. The author never sees it and keeps none of it.

| Service                                                                                                                                      | Plugins                                                                                                                                                                                        | What it receives                                                                                                                                                                                                                                                                                                          | Its policy                                                                                                                   |
| :------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------- |
| Svelte's remote MCP server (`mcp.svelte.dev`)                                                                                                | svelte-development                                                                                                                                                                             | The docs sections Claude looks up, and the full code of each Svelte file the autofixer checks. The Svelte team states that it "does not log, store, or inspect code sent to the remote server" ([remote setup](https://svelte.dev/docs/mcp/remote-setup)). You can keep your code local, as the plugin's README explains. | No separate privacy policy published as of 5 November 2026; see the statement quoted here                                    |
| GitHub (`github.com`, `api.github.com`, `raw.githubusercontent.com`, and `api.githubcopilot.com` for the GitHub MCP server you add yourself) | github-operations, project-maintainer, hook-engineering, plugin-evals, skill-diagnostics, svelte-development, tailwind-development, typescript6-lsp-intelligence, typescript7-lsp-intelligence | For github-operations and project-maintainer, the requests `git`, `gh` or the GitHub MCP server make in your repositories, with your own credentials. For the others, plain requests for public files, such as changelogs, with nothing of yours in them.                                                                 | [GitHub General Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement) |
| npm registry (`registry.npmjs.org`)                                                                                                          | tailwind-development                                                                                                                                                                           | The download of the plugin's pinned packages when Claude Code installs or updates it, and Tailwind's upgrade tool if you ask for a migration.                                                                                                                                                                             | [npm Privacy Policy](https://docs.npmjs.com/policies/privacy)                                                                |
| PyPI (`pypi.org`)                                                                                                                            | github-operations                                                                                                                                                                              | The download of two pinned packages through `uv`, on their first run.                                                                                                                                                                                                                                                     | [PyPI Privacy Notice](https://policies.python.org/pypi.org/Privacy-Notice/)                                                  |
| jsDelivr (`cdn.jsdelivr.net`)                                                                                                                | tailwind-development                                                                                                                                                                           | The request your browser makes for Tailwind's Play CDN script when you open a standalone preview page.                                                                                                                                                                                                                    | [jsDelivr Privacy Policy](https://www.jsdelivr.com/terms/privacy-policy-jsdelivr-net)                                        |
| Your Claude account or model provider                                                                                                        | prompt-writer, plugin-test-bench                                                                                                                                                               | prompt-writer's checking agent is a model call that receives the session transcript. plugin-test-bench's eval runs and test requests call the model with the throwaway configuration you sign in to. Both go through the same account or provider as your session.                                                        | [Anthropic Privacy Policy](https://www.anthropic.com/legal/privacy), or your provider's policy                               |
| Public documentation sites (such as `code.claude.com`, `platform.claude.com`, `svelte.dev`, `tailwindcss.com`, `typescriptlang.org`)         | several plugins, as each README lists                                                                                                                                                          | Plain `GET` requests for public pages, through your session's web tools or `curl`, under your own permission rules, with nothing of yours in them.                                                                                                                                                                        | Each site's own policy                                                                                                       |

Claude itself, and Claude Code, process your session under [Anthropic's Privacy Policy](https://www.anthropic.com/legal/privacy) or your model provider's policy, with or without these plugins.

## Your choices

- Each plugin's README lists every destination it can reach. Read it before you install.
- Your Claude Code permission rules apply to the tool calls Claude makes for a plugin, such as its commands and web requests, and you can use them to block those. They don't apply to what a plugin's hooks, MCP servers or mods run on their own: to stop those, disable or uninstall the plugin.
- You can turn off any MCP server in `/mcp`, or uninstall a plugin at any time with `claude plugin uninstall <plugin>@the-claude-factory`.

## Children

The plugins are developer tools and are not directed at children.

## Changes to this policy

Changes are made in this file. Its [history](https://github.com/nerymurillohnd/the-claude-factory/commits/main/PRIVACY.md) shows every change and its date. The effective date above changes with each update.

## Contact

For questions about this policy, open an [issue](https://github.com/nerymurillohnd/the-claude-factory/issues). For a security concern, follow [SECURITY.md](SECURITY.md) instead.
