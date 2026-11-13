<!--
  Procedure: references/documents/privacy.md
  Values to replace are {{camelCase}}. Instructions are HTML comments: follow each one, then delete it, this one included.
  No official template exists for this file. Anthropic's directory policy requires a privacy policy link, explaining data
  collection, usage and retention, for software that collects user data or connects to a remote service.
  Write only what is true of every plugin it covers today; a false "we collect nothing" is worse than no policy.
-->
# Privacy Policy

**Effective date:** {{effectiveDate}}

This policy covers every plugin published in the {{marketplaceDisplayName}} marketplace (`{{repositoryHost}}`). It explains what data the plugins collect, how that data is used and how long it is kept, and which third-party services a plugin can send data to on your behalf.

## Who runs the marketplace

The marketplace and its plugins are written and maintained by {{maintainerName}} ([{{maintainerProfileHost}}]({{maintainerProfileUrl}})), who is responsible for this policy.

## What the author collects

{{authorCollection}}

<!--
  authorCollection: what the author receives, how it is used and how long it is kept. When it is nothing, say so and list what that excludes:
  "Nothing. No plugin in this marketplace sends data to the author or to any server the author runs:" followed by bullets for
  telemetry, analytics, crash reports or usage statistics; accounts, sign-ups or licence checks; servers operated by the author.
  Then what the author does receive, such as what users post in public issues, under the host's own privacy statement, with its link.
-->

## What stays on your machine

Plugins run inside your own Claude Code session, with your permissions. What a plugin reads or writes on your machine stays there. Each plugin's README lists the files it reads and writes, the commands it runs and how long anything it keeps lasts, in its **{{disclosureSection}}** section.

{{localFiles}}

<!-- localFiles: the small files plugins keep in their data folder or a temporary folder, such as markers, when they delete them, and that none is sent anywhere. Delete it when no plugin keeps any. -->

## Third-party services

Some plugins connect to services that their own operators run. When they do, the data goes straight from your machine to that service, under that service's own policy. The author never sees it and keeps none of it.

| Service | Plugins | What it receives | Its policy |
| :-- | :-- | :-- | :-- |
| {{serviceName}} (`{{serviceHost}}`) | {{servicePlugins}} | {{serviceData}} | [{{servicePolicyTitle}}]({{servicePolicyUrl}}) |

<!-- One row per destination any plugin can reach, with the exact host, the plugins that reach it, the data sent there and the operator's own policy link. If the operator publishes no policy, say so, with the date you checked, and quote what it does state. -->

Claude itself, and Claude Code, process your session under [Anthropic's Privacy Policy](https://www.anthropic.com/legal/privacy) or your model provider's policy, with or without these plugins.

## Your choices

- Each plugin's README lists every destination it can reach. Read it before you install.
- Your Claude Code permission rules apply to the commands and web requests Claude makes for a plugin. Use them to block a destination you do not want.
- You can turn off any MCP server in `/mcp`, or uninstall a plugin at any time with `claude plugin uninstall <plugin>@{{marketplaceName}}`.

## Children

{{childrenStatement}}

<!-- childrenStatement: whether the plugins are directed at children, for example "The plugins are developer tools and are not directed at children." -->

## Changes to this policy

Changes are made in this file. Its [history]({{policyHistoryUrl}}) shows every change and its date. The effective date above changes with each update.

## Contact

For questions about this policy, open an [issue]({{issuesUrl}}). For a security concern, follow [SECURITY.md](SECURITY.md) instead.
