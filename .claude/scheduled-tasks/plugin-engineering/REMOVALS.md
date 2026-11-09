# REMOVALS

Passages removed from each file on 2026-11-07, with the reason given by the reviewer that read the whole file. Line numbers refer to the original downloaded file.

## 01-plugins-core/anthropic-marketplaces.md

- lines 9-58: Intro, navigation, Anthropic official/community marketplace table, deprecated claude-code-plugins marketplace and official catalog: only about Anthropic's own marketplaces, not a public third-party GitHub marketplace
- lines 65-69: Searching Anthropic's catalog on the web/GitHub and Anthropic's claude.ai directory: official directory channel
- lines 72-77: Adding Anthropic's community and official marketplaces: Anthropic-specific
- lines 94-94: Link to official marketplace's LSP plugins: Anthropic-specific

## 01-plugins-core/cli-hints.md

- lines 9-125: The whole hint mechanism works only for plugins listed in an Anthropic official marketplace name (not claude-community, not a third-party marketplace): official directory channel only

## 01-plugins-core/cli-reference.md

- lines 138-138: Reserved name anthropic-plugin-directory: Anthropic directory only
- lines 243-243: Plugin required by the organization as a synced plugin: org/claude.ai distribution [confirmed on admin re-review]
- lines 282-282: managed scope for admin-installed plugins: org-managed distribution [confirmed on admin re-review]
- lines 311-311: Synced from claude.ai group: directory/account sync channel
- lines 385-390: @builtin plugins not found message: built-in plugins, not marketplace plugins
- lines 718-718: --claudeai flag: marketplace hosted on claude.ai (org library), not a GitHub marketplace [confirmed on admin re-review]
- lines 729-729: url source for self-hosted/non-git hosts: non-GitHub host
- lines 733-736: AWS CodeCommit and GitLab subgroup handling: non-GitHub hosts
- lines 747-747: Bare self-hosted GitLab host error: non-GitHub host
- lines 749-756: Adding a claude.ai-hosted marketplace with --claudeai: org/claude.ai distribution [confirmed on admin re-review]
- lines 783-790: claude.ai marketplace entries and From claude.ai section of marketplace list: org/claude.ai distribution [confirmed on admin re-review]
- lines 930-931: Admin disableSideloadFlags and Agent SDK plugins option: managed-only and outside the marketplace scenario [confirmed on admin re-review]

## 01-plugins-core/code-intelligence.md

- lines 17-18: Pointer to the official marketplace's plugin table: Anthropic-specific
- lines 27-48: Table of official LSP plugins, their maintainers and README install links: Anthropic official marketplace catalog
- lines 51-60: Installing an official LSP plugin from claude-plugins-official and its not-found error: Anthropic-specific
- lines 134-134: Browse the official marketplace: Anthropic-specific

## 01-plugins-core/components.md

- nothing removed

## 01-plugins-core/create-marketplace.md

- lines 11-12: Team/org marketplace, private repository and admin-required distribution: org-internal/private channel [confirmed on admin re-review]
- lines 17-18: Sharing a directory/.zip and submitting to Anthropic's directory: other distribution channels
- lines 179-181: archive, npm and command plugin sources: non-GitHub distribution
- lines 233-233: Manage plugins for your organization: managed/org distribution [confirmed on admin re-review]

## 01-plugins-core/create.md

- lines 135-135: Sending the directory or a .zip directly: sharing a local folder/archive as distribution
- lines 137-137: Submitting to Anthropic's directory: official directory channel
- lines 241-244: Sharing a plugin through a project's .claude/skills in a repository: a non-marketplace distribution method

## 01-plugins-core/dependencies.md

- lines 83-84: Deploying a bundle via managed settings enabledPlugins: org-managed distribution [confirmed on admin re-review]
- lines 166-180: Constraints for npm, archive and command sources and headersHelper: non-GitHub/private distribution
- lines 216-226: Dependencies for plugins synced from claude.ai: directory/account sync channel

## 01-plugins-core/host-marketplace.md

- lines 18-18: Pointer for org admins managing marketplaces across organization machines; managed-only distribution [confirmed on admin re-review]
- lines 29-31: Table rows for non-GitHub git hosts/GHES, hosted marketplace.json URL and shared filesystem hosting
- lines 43-68: Only applies to a marketplace hosted as a bare marketplace.json URL, not a GitHub repository + command and archive plugin sources excluded by user decision 2026-11-08
- lines 89-100: Distribution through claude.ai organization settings (private/internal repos, org sync); org-internal channel [confirmed on admin re-review]
- lines 114-114: HTTPS stored-credential requirements only matter for private repositories
- lines 116-118: GitHub Enterprise Server access and claude.ai organization distribution [confirmed on admin re-review]
- lines 122-122: Serving via marketplace.json URL or shared directory and private github entry sources
- lines 131-132: Shared filesystem directory marketplace for a team network
- lines 137-142: Credential behavior of background update for a private marketplace
- lines 150-150: Storing git credentials to keep a private marketplace current
- lines 153-170: Provider tokens for authenticating private-marketplace background checks + Company-wide rollout with private repository, administrators and managed settings [confirmed on admin re-review]
- lines 209-219: command plugin source, excluded by user decision 2026-11-08
- lines 250-251: Admin assigning channels via managed extraKnownMarketplaces; managed-only [confirmed on admin re-review]
- lines 298-396: Authenticated archive downloads with headers/headersHelper for private registries; credentials for private distribution
- lines 422-422: Org management next-step link; managed-only [confirmed on admin re-review]

## 01-plugins-core/install.md

- lines 49-50: Details-pane fields shown only for plugins in Anthropic's official marketplace
- lines 158-167: Plugins synced from a claude.ai account/organization; not the GitHub marketplace channel [confirmed on admin re-review]
- lines 182-182: command and archive plugin sources excluded by user decision 2026-11-08
- lines 197-197: Non-GitHub git host marketplace source
- lines 199-199: Hosted marketplace.json URL source; not GitHub
- lines 241-241: HTTPS credential helper requirements only for private repositories
- lines 246-271: GitHub Enterprise Server credentials and managed-settings registration [confirmed on admin re-review] + Adding marketplaces listed by claude.ai (org library, uploads); org/claude.ai distribution [confirmed on admin re-review]
- lines 285-288: Managed-scope plugins and org-required synced plugins; managed-only [confirmed on admin re-review]
- lines 291-299: Managing plugins synced from claude.ai; not the GitHub marketplace channel [confirmed on admin re-review]
- lines 366-369: Auto-update credentials for a private marketplace
- lines 386-386: Pointer to Anthropic's own marketplaces; not this marketplace

## 01-plugins-core/loading.md

- lines 54-55: skills-dir and claude.ai-synced origins; not marketplace distribution
- lines 74-83: Trust check and limits for plugins checked into a repository's .claude/skills; repository-folder distribution
- lines 86-93: audit: repository .claude/skills plugins, non-marketplace channel
- lines 108-154: Repository skills-dir plugin load causes, managed-settings blocks and claude.ai synced plugins [confirmed on admin re-review]
- lines 187-187: Managed settings as fetch trigger; managed-only [confirmed on admin re-review]
- lines 198-199: claude.ai sync directories
- lines 212-212: command and archive plugin sources excluded by user decision 2026-11-08
- lines 266-266: audit: npm-source distribution
- lines 280-280: audit: npm-source distribution
- lines 324-324: command and archive plugin sources excluded by user decision 2026-11-08
- lines 345-345: Seed directory supplying the marketplace; org/CI seeding [confirmed on admin re-review]
- lines 366-367: headersHelper archive-auth entries skipped by auto-update; private archive authentication
- lines 370-383: command and archive plugin sources excluded by user decision 2026-11-08
- lines 394-394: claude.ai synced plugin precedence
- lines 415-415: Org management next-step link; managed-only [confirmed on admin re-review]

## 01-plugins-core/manifest-reference.md

- nothing removed

## 01-plugins-core/marketplace-reference.md

- lines 20-20: Pointer to org allowlist/blocklist recipes; managed-only distribution [confirmed on admin re-review]
- lines 98-99: headers/headersHelper for authenticated archive downloads; credentials for private/non-GitHub hosting
- lines 142-142: url plugin source row: arbitrary non-GitHub git hosts
- lines 144-146: npm, archive and command plugin source rows: non-GitHub registries/hosts or local tool-generated plugins
- lines 173-173: settings marketplace source: inline settings catalog, not a GitHub-hosted marketplace
- lines 231-244: url plugin source section: GitLab/Azure DevOps/CodeCommit and other non-GitHub git hosts
- lines 261-365: npm, archive and command plugin source sections: npm registries, self-hosted zip archives, plugins produced by a local tool; not a public GitHub marketplace
- lines 389-389: npm marketplace source row: not implemented, not GitHub
- lines 392-392: settings, skills-dir, hostPattern, pathPattern rows: inline settings catalog and policy-only values [confirmed on admin re-review]
- lines 405-406: headers/headersHelper for authenticated url hosts; private-host credentials
- lines 414-415: settings-source fields and policy-list-only source values; managed/org-only [confirmed on admin re-review]
- lines 488-488: headersHelper validation error for archive entries; authenticated archive hosting
- lines 493-495: headers/headersHelper/archive-sha256 warnings; authenticated archive hosting
- lines 510-510: npm package cause; npm source not used in a GitHub marketplace
- lines 527-527: Next-step link to org allowlist/blocklist recipes; managed-only [confirmed on admin re-review]

## 01-plugins-core/measure.md

- lines 77-82: Context cost display only for official-marketplace plugins; nothing to act on for a third-party marketplace
- lines 87-87: Organization administrator fleet telemetry; org-internal [confirmed on admin re-review]
- lines 91-92: Usage tracking for plugins in Anthropic's directory
- lines 100-100: Managed settings and seed-directory plugins; managed-only distribution [confirmed on admin re-review]
- lines 121-163: Measure across a fleet: OpenTelemetry exporters, managed settings and Enterprise Analytics API for org administrators [confirmed on admin re-review]
- lines 168-169: Next-step links to telemetry redaction and OpenTelemetry monitoring; fleet/org-only [confirmed on admin re-review]

## 01-plugins-core/org.md

- lines 9-12: Intro to managed settings for administrators; managed-only [confirmed on admin re-review]
- lines 18-23: claude.ai/Cowork org admin pointers and managed rollout roadmap [confirmed on admin re-review]
- lines 28-83: Fleet install through managed settings: delivery mechanisms, managed source precedence, managed examples, private repo access, official marketplace in managed policy [confirmed on admin re-review]
- lines 94-95: Local directory/file marketplace source resolution; local-folder distribution
- lines 117-156: Seed containers (incl. private-repo CI credentials), allowlist/blocklist policy, control matrix, managed update policy and release channels via managed settings/gateway; managed/org-only [confirmed on admin re-review]
- lines 186-186: command and archive plugin sources excluded by user decision 2026-11-08
- lines 238-241: Seed containers (incl. private-repo CI credentials), allowlist/blocklist policy, control matrix, managed update policy and release channels via managed settings/gateway; managed/org-only [confirmed on admin re-review]
- lines 246-247: Seed containers (incl. private-repo CI credentials), allowlist/blocklist policy, control matrix, managed update policy and release channels via managed settings/gateway; managed/org-only [confirmed on admin re-review]
- lines 269-271: audit: skills-dir blocklist entry, non-marketplace channel
- lines 335-335: command and archive plugin sources excluded by user decision 2026-11-08
- lines 337-357: Admin deployment of release channels per user group (MDM, gateway policy) [narrowed on audit: 310-336 restored]
- lines 368-391: Managed pluginSuggestionMarketplaces, fleet audit telemetry/Analytics API, managed-settings limits and policy troubleshooting; managed/org-only [confirmed on admin re-review]
- lines 396-397: Managed pluginSuggestionMarketplaces, fleet audit telemetry/Analytics API, managed-settings limits and policy troubleshooting; managed/org-only [confirmed on admin re-review]
- lines 406-407: Links to org mod management, server-managed settings and policy-block messages; managed-only [confirmed on admin re-review]

## 01-plugins-core/overview.md

- lines 16-17: Anthropic directory MCP submission and IDE extensions; not plugin distribution via a public marketplace
- lines 65-68: Disambiguation of the claude.com Claude Marketplace website; nothing to act on
- lines 126-126: Link to organization plugin policy; managed-only [confirmed on admin re-review]

## 01-plugins-core/plugin-evals.md

- lines 336-336: name@skills-dir target: skills-directory plugins, a local-folder loading method

## 01-plugins-core/publish.md

- lines 18-18: CLI/SDK plugins in an official marketplace
- lines 28-28: No-marketplace route: sharing a folder or zip
- lines 30-30: Anthropic's directory route
- lines 68-80: Sharing without a marketplace (folder, zip, --plugin-url, skills dir) and shipping via a CLI/SDK installer
- lines 125-161: Submission to Anthropic's directory and synced listings
- lines 190-190: Link to recommending a plugin from your own CLI (official marketplace)

## 01-plugins-core/relevance.md

- lines 18-18: Turning suggestions off is a user/cloud preference, not something the maintainer or installer of the public marketplace acts on
- lines 23-23: Routes administrators to managed settings; org-internal administration [confirmed on admin re-review]
- lines 41-41: User/project spinner-tip toggles; not acted on for publishing or installing from the marketplace
- lines 169-192: Allowlisting a marketplace in managed settings is an org administrator task (managed-only), not available to the public maintainer or third-party users [confirmed on admin re-review]
- lines 223-223: Link to org plugin policy management; managed-only distribution [confirmed on admin re-review]

## 01-plugins-core/security.md

- lines 20-21: Pointers to org plugin management and to unrelated security plugins; not used in this scenario [confirmed on admin re-review]
- lines 58-58: Describes the Anthropic community catalog's commit pinning; applies only to Anthropic's marketplace
- lines 79-79: Pointer to browsing Anthropic's official/community marketplaces; not this marketplace
- lines 134-134: command and archive plugin sources excluded by user decision 2026-11-08
- lines 136-136: command and archive plugin sources excluded by user decision 2026-11-08
- lines 146-146: Org administrator enforcement via managed settings; managed-only [confirmed on admin re-review]
- lines 150-158: Org telemetry export and Analytics API reporting; org-internal administration [confirmed on admin re-review]
- lines 161-161: Link to org plugin management; managed-only [confirmed on admin re-review]
- lines 163-163: Link to Anthropic's marketplaces page; official distribution channel

## 01-plugins-core/troubleshooting.md

- lines 105-128: Only about registering Anthropic's official marketplace, not the public GitHub marketplace
- lines 136-136: claude.ai-hosted marketplaces; a different distribution channel
- lines 263-263: Background auto-update credentials concern private repositories and their credentials
- lines 345-355: Seed-directory deployments and GitHub Enterprise Server hosts; org-internal/GHES distribution [confirmed on admin re-review]
- lines 423-450: command and archive plugin sources excluded by user decision 2026-11-08
- lines 491-491: Keeping a marketplace on a network drive; local/network-folder distribution
- lines 517-528: Fix consists of adding Anthropic's official marketplace and browsing Anthropic marketplaces
- lines 608-608: Dependency met by a claude.ai-synced plugin; claude.ai org distribution channel [confirmed on admin re-review]
- lines 747-747: Org-required plugins synced from claude.ai; managed/org distribution [confirmed on admin re-review]
- lines 761-761: Org pre-install through managed settings; managed-only [confirmed on admin re-review]
- lines 958-961: Old-version note about plugins synced from claude.ai; different distribution channel
- lines 1142-1142: Tip for repositories on an internal git host; non-GitHub/self-hosted
- lines 1172-1185: command and archive plugin sources excluded by user decision 2026-11-08
- lines 1191-1191: Administrator-side policy troubleshooting; managed-only [confirmed on admin re-review]

## 02-mods/mod-admin.md

- lines 11-23: Admin audience routing and the allowManagedModsOnly managed-settings procedure; managed-only [confirmed on admin re-review]
- lines 49-52: Admin audience routing and the allowManagedModsOnly managed-settings procedure; managed-only [confirmed on admin re-review]
- lines 87-87: Admin instructions for stopping mods' fetches via managed policy [confirmed on admin re-review]
- lines 126-132: Admin changes to managed settings to let guarded hooks run; managed-only [confirmed on admin re-review]
- lines 149-150: Mapping of org plugin controls to loadable mods and admin review/blocking advice; managed-only [confirmed on admin re-review]
- lines 206-253: Org mod policies, guard options, deploying org-owned mods from a local directory and policy mods; managed-only/org-internal distribution [confirmed on admin re-review]
- lines 274-441: Org mod policies, guard options, deploying org-owned mods from a local directory and policy mods; managed-only/org-internal distribution [confirmed on admin re-review]

## 02-mods/mod-api.md

- nothing removed

## 02-mods/mod-create.md

- lines 352-354: Sharing channels that are not a public GitHub marketplace: sending a folder or zip, a team's private-repository marketplace, and org-wide install through managed settings [confirmed on admin re-review]

## 02-mods/mod-events.md

- nothing removed

## 02-mods/mod-gallery.md

- nothing removed

## 02-mods/mod-interface.md

- nothing removed

## 02-mods/mod-overview.md

- lines 31-31: Using Claude Code's built-in mods is not making, publishing or installing marketplace plugins
- lines 62-62: Keeping a sample by adding a local clone as a marketplace: local-folder distribution
- lines 114-116: Early-access env var note; nothing the maintainer or user acts on
- lines 201-204: Section about administrators controlling mods through managed settings: org-only [confirmed on admin re-review]
- lines 227-228: Built-in AGENTS.md and /diff mods: how to turn off Claude Code features, unrelated to the marketplace's plugins
- lines 231-232: Built-in telemetry and You should know mods: turning off Claude Code features, unrelated to the marketplace's plugins
- lines 253-253: Link to org mod management: managed/org-only [confirmed on admin re-review]

## 02-mods/mod-reference.md

- nothing removed

## 02-mods/mod-test.md

- lines 349-408: testing a policy mod that an organization lists in managed prependPlugins; org-internal/managed distribution only [confirmed on admin re-review]

## 02-mods/mod-troubleshoot.md

- nothing removed

## 03-components/channels-reference.md

- nothing removed

## 03-components/channels.md

- lines 23-220: setup walkthroughs for Anthropic's own Telegram/Discord/iMessage plugins from claude-plugins-official; not part of building, publishing or installing plugins from the public marketplace
- lines 350-365: conceptual comparison with cloud sessions, Slack, Remote Control; nothing the maintainer or user acts on for the marketplace
- lines 371-372: links to Remote Control and scheduled tasks, unrelated to plugin channels in the marketplace

## 03-components/hooks-guide.md

- lines 817-817: Managed policy settings row: org-wide admin-controlled hook location, managed-only distribution [confirmed on admin re-review]

## 03-components/hooks.md

- lines 246-246: Managed policy settings row: org-wide admin-controlled location, managed-only [confirmed on admin re-review]
- lines 261-262: command and archive plugin sources excluded by user decision 2026-11-08
- lines 723-723: disableAllHooks vs administrator-managed hooks hierarchy: managed-only [confirmed on admin re-review]
- lines 1338-1350: Example distributes skills by syncing an org-internal team skills repo from a private git host into ~/.claude/skills, not through the public marketplace [confirmed on admin re-review]
- lines 1496-1497: Agent SDK callback hook timeout behavior; plugin hooks are not SDK callbacks
- lines 1622-1622: Use case only for Agent SDK applications, not for plugin maintainers or users
- lines 1762-1763: Agent SDK callback hook timeout behavior; plugin hooks are not SDK callbacks
- lines 2028-2062: audit: answering AskUserQuestion/ExitPlanMode serves -p integrations
- lines 2064-2119: Deferring tool calls is for integrations driving claude -p as a subprocess (Agent SDK apps, custom UIs), not for publishing or installing marketplace plugins
- lines 2328-2328: In-process Agent SDK callbacks only; plugin hooks fall under the previous bullet
- lines 2980-2980: Matcher for managed policy settings files only (managed-only configuration) [confirmed on admin re-review]
- lines 3034-3035: Behavior of enterprise managed and server-managed settings changes; managed-only distribution [confirmed on admin re-review]
- lines 3092-3092: Matcher for SDK client register_repo_root control request; SDK integration only
- lines 3117-3117: Output handling for SDK register_repo_root source only

## 03-components/mcp.md

- lines 15-25: Generic end-user use-case examples of MCP; nothing the maintainer or plugin user acts on
- lines 28-33: Browsing Anthropic Directory connectors and adding them by hand; not part of building or installing marketplace plugins
- lines 69-80: claude mcp add examples for personal user-scoped config, not plugin-bundled servers
- lines 85-90: SDK-host-only server type and --mcp-config stream-json reporting; not used by plugin servers
- lines 97-112: claude mcp add --transport sse commands for hand-configured servers; plugins declare type in .mcp.json
- lines 123-144: claude mcp add CLI syntax and -- separator for hand-added stdio servers; not plugin configuration
- lines 158-164: claude mcp add-json command for a hand-added WebSocket server
- lines 167-226: Converting other clients' setup instructions into claude mcp add commands for personal config
- lines 245-246: Token cleanup on claude mcp remove; plugin servers are removed by uninstalling the plugin
- lines 249-250: Save confirmation messages of claude mcp add
- lines 255-256: Approval/rejection statuses of project .mcp.json servers, not plugin servers
- lines 260-273: Enterprise managed-policy block status and project .mcp.json approval/workspace-trust rules; managed and project-scoped, not plugin distribution [confirmed on admin re-review]
- lines 323-323: Microsoft Foundry Azure deployment specifics; unrelated to the scenario
- lines 348-353: Runtime selection on third-party providers and gateways; not relied on for a public plugin marketplace
- lines 444-449: claude mcp add flag tips (scope, env, short forms) for hand-added servers
- lines 748-821: Local, project and user scope procedures for hand-configured servers; plugin servers live in the plugin's own .mcp.json
- lines 838-839: Managed-settings precedence and Desktop Code tab duplicate resolution; managed/other-surface only [confirmed on admin re-review]
- lines 900-901: Display of managedMcpServers URLs; managed distribution only [confirmed on admin re-review]
- lines 904-955: Practical examples of hand-adding GitHub and PostgreSQL servers for personal use
- lines 963-963: claude.ai connector session-token behavior; not plugin servers
- lines 965-965: Connectors delivered to cloud sessions; not plugin servers
- lines 986-993: Quickstart step adding the sentry server by hand with claude mcp add
- lines 1036-1041: claude mcp add --callback-port command for a hand-added server
- lines 1043-1087: audit: pre-configured OAuth flags for hand-added servers
- lines 1088-1097: CI env-var client-secret variant of claude mcp add for a hand-added server
- lines 1273-1339: add-json for personal config, importing from Claude Desktop, claude.ai connectors and their org controls, and running Claude Code as an MCP server; none concern building or installing marketplace plugins [confirmed on admin re-review]
- lines 1344-1385: add-json for personal config, importing from Claude Desktop, claude.ai connectors and their org controls, and running Claude Code as an MCP server; none concern building or installing marketplace plugins [confirmed on admin re-review]
- lines 1392-1510: add-json for personal config, importing from Claude Desktop, claude.ai connectors and their org controls, and running Claude Code as an MCP server; none concern building or installing marketplace plugins [confirmed on admin re-review]
- lines 1740-1743: Microsoft Foundry Azure tool-search limitation; unrelated to the scenario
- lines 1794-1795: Experimental-betas, managed-settings and HIPAA overrides of tool search; managed/compliance only [confirmed on admin re-review]
- lines 1798-1804: Google Cloud Agent Platform model-specific tool search behavior; third-party provider only
- lines 1837-1849: Tool search through an LLM gateway; gateway deployments are outside the scenario

## 03-components/model-config.md

- lines 11-24: Session model setting per cloud provider and gateway routing; not used to build or install plugins
- lines 42-58: Per-provider alias resolution and gateway Fable details; personal/provider session configuration
- lines 60-113: Model version requirements, Fable usage and usage-credit consent prompts; account/session concerns, not plugin work
- lines 115-136: How a user sets their own session model and Enterprise account recording; not plugin work [confirmed on admin re-review]
- lines 138-224: Personal session model selection, resume, pricing, managed/host precedence, default model for new sessions; not plugin work [confirmed on admin re-review]
- lines 229-231: Host-embedded platform precedence over managed model settings; managed/org-only [confirmed on admin re-review]
- lines 234-236: Allowlist effect on main session, alias env vars and fast mode; admin configuration, not plugin components [confirmed on admin re-review]
- lines 239-245: Allowlist effect on advisor/background agents and admin alias substitution; admin-only [confirmed on admin re-review]
- lines 248-250: Handling of blocked main-session selections; admin/session configuration [confirmed on admin re-review]
- lines 257-571: Admin allowlist details, surface coverage, org restrictions/defaults/effort limits, default/opusplan behavior, fallback chains and automatic fallback for sessions; managed/org-only or personal session settings [confirmed on admin re-review]
- lines 572-580: audit: fallback governed by user /config
- lines 581-602: Fallback on Bedrock/Agent Platform/Foundry and security workloads; non-Anthropic provider deployment and account concerns
- lines 616-666: Session effort resolution order, saving levels, ultracode toggle; personal session settings, not plugin frontmatter
- lines 678-680: Ultracode row and blog test anecdote; not a frontmatter effort value or plugin action
- lines 684-695: Opus 5 to 5.5 migration advice and ultrathink keyword troubleshooting; personal session usage
- lines 699-705: Effort set via /effort, /model, flag, env var, settings, Remote Control; personal session controls, not plugin components
- lines 715-753: Checking session effort, when it starts, sending no effort, adaptive thinking env vars; personal session configuration
- lines 754-939: Extended thinking toggles, 1M context plans and gateways, auto-compact window, gateway/custom model ID windows, checking current model, custom picker option; personal session, plan or gateway configuration, not plugin work
- lines 941-943: Intro to alias-mapping env vars for provider IDs; user/provider configuration
- lines 946-949: Alias-mapping env vars for Fable/Opus/Sonnet/Haiku; user/provider configuration, not plugin components
- lines 951-1112: Third-party provider pinning, pinned model display/capabilities, enterprise modelOverrides, prompt caching env vars and alias version history; provider/admin deployment or personal settings [confirmed on admin re-review]

## 03-components/output-styles.md

- lines 13-13: Pointer to built-in styles, which are not plugin content
- lines 24-90: Descriptions of Claude Code's built-in output styles; neither built nor installed through a plugin marketplace
- lines 120-121: Creating a style from the VS Code menu; not how plugin output styles are produced
- lines 128-128: Managed policy output-styles location; managed-only distribution [confirmed on admin re-review]
- lines 182-182: --append-system-prompt launch flag; not a plugin component
- lines 202-202: Link about the built-in Proactive style vs auto mode; not plugin related

## 03-components/skills.md

- lines 21-96: Bundled skills (/doctor, /run, /verify, pre-commit verify, /claude-api): built-in Claude Code features, not used to build, publish or install marketplace plugins
- lines 158-162: Enterprise, personal, project, nested and add-dir skill locations: not the plugin distribution channel [confirmed on admin re-review]
- lines 164-164: claude.ai account skill location: different distribution channel
- lines 166-173: Folder rules that apply outside plugins (symlinks in local locations, reserved names, command files, skills-dir plugins)
- lines 175-204: Monorepo/subdirectory and --add-dir loading of project skills: not plugin skills
- lines 211-217: Name resolution among enterprise/personal/project/added-dir/bundled skills: plugin skills are namespaced and unaffected [confirmed on admin re-review]
- lines 219-219: Synced claude.ai skill name resolution: different channel
- lines 221-323: Cowork/cloud personal skills, claude.ai synced skills and live reload of local skill directories: not part of the public marketplace workflow
- lines 328-329: Removing personal/project/enterprise skills: not plugin skills [confirmed on admin re-review]
- lines 331-332: Removing synced and bundled skills: not plugin skills
- lines 334-334: Keeping a personal/project skill via skillOverrides: not plugin skills
- lines 445-449: Command-name sources for local skill dirs, nested, added dirs and .claude/commands: not plugin layouts
- lines 452-452: Command name of skills synced from claude.ai: different channel
- lines 619-619: Workspace trust for project skills checked into a repository and org-wide managed withholding: not plugin skills [confirmed on admin re-review]
- lines 745-745: Synced claude.ai skill shell-command restriction: different channel [confirmed on admin re-review]
- lines 889-892: Deny-rule effects on bundled aliases, nested skills and synced skills: not plugin skills
- lines 895-895: Version note about nested skill deny rules
- lines 897-901: Allow rules for synced claude.ai skills: different channel
- lines 911-939: skillOverrides details: the setting does not affect plugin skills (line 941 kept says so)
- lines 943-950: /skill-doctor usage report for a user's own skill budget: not part of building, publishing or installing marketplace plugins
- lines 959-959: Baseline for personal or project skills via skillOverrides: not plugin skills
- lines 993-993: Sharing via committed project skills: not the marketplace channel
- lines 995-995: Managed org-wide distribution: excluded channel [confirmed on admin re-review]
- lines 1239-1246: Personal skills disappeared into .trash (claude.ai sync, manifest.json): not plugin skills
- lines 1255-1255: Memory/CLAUDE.md link: unrelated to plugin skills
- lines 1258-1258: Claude Tag channel project skills: different channel

## 03-components/statusline.md

- lines 9-1087: Main statusLine: configured only in the user's own or project settings (plugins can ship subagentStatusLine, not statusLine), so its setup, JSON fields, examples and Windows config are not used to build or install marketplace plugins
- lines 1128-1135: Tips and community statusline projects for the main status line
- lines 1138-1160: Troubleshooting specific to the main status line (not appearing, empty values, context percentage)
- lines 1206-1213: Notifications sharing the main status line row

## 03-components/sub-agents.md

- lines 13-24: Pointers to background agents/agent teams and generic benefit list (user-level reuse); not used to build or install marketplace plugins
- lines 29-149: Built-in subagents and a quickstart creating a personal ~/.claude/agents subagent; not plugin authoring or installation
- lines 166-177: Project/user .claude/agents discovery, --add-dir and naming in those directories; not plugin agents
- lines 180-229: CLI-defined --agents JSON subagents and managed subagents; not the plugin distribution path [confirmed on admin re-review]
- lines 238-239: Reusing subagent definitions as agent-team teammates; unrelated to the marketplace
- lines 244-253: File watcher behavior for ~/.claude/agents and .claude/agents only, not plugin directories
- lines 268-269: Headless --append-subagent-system-prompt flag; not used for plugin development or install
- lines 285-286: Main conversation running isolated in a worktree; session-level behavior not relied on for plugins
- lines 331-340: Skip rules scoped to project/user/managed/--add-dir agents directories, not plugin agents (plugin case kept at 341) [confirmed on admin re-review]
- lines 388-412: User-side env vars forcing one model on every subagent; not something the maintainer or installer applies for the marketplace
- lines 444-447: ListAgents cross-session messaging and agent-team teammate tools; unrelated to plugin agents
- lines 529-610: mcpServers scoping, inline MCP trust and permissionMode sections; both fields are ignored for plugin subagents
- lines 682-749: Frontmatter hooks (ignored for plugin subagents) and user settings to deny specific subagents
- lines 759-800: Hooks in subagent frontmatter, which plugin subagents ignore
- lines 927-946: User configuration to let Claude wait (fork mode env var, Ctrl+B); not plugin work
- lines 957-971: Subagent panel UI, agent-team naming and API error handling at runtime; not acted on for building or installing plugins
- lines 1004-1037: End-user prompting patterns for ad hoc subagent use
- lines 1055-1056: /btw side question tip; unrelated
- lines 1080-1081: Terminal panel tree display and user-side concurrent subagent limit
- lines 1132-1157: SendMessage resume mechanics, stop/cancel handling and message authority during interactive use; not plugin authoring or installation
- lines 1166-1175: Messaging a subagent by name after a restart; session operation detail
- lines 1216-1279: Forking the current conversation, fork panel controls and fork mode; not a plugin-authored component
- lines 1291-1291: Tip to check project subagents into version control for a team; not the plugin path
- lines 1404-1469: Example relies on frontmatter hooks, which plugin subagents ignore
- lines 1475-1476: Next steps for headless SDK and MCP servers for subagents (mcpServers ignored for plugin subagents)

## 03-components/workflows.md

- lines 34-81: Walkthrough of the built-in /deep-research workflow; not plugin authoring or installation
- lines 125-159: Dismissing the ultracode keyword, where it triggers, and session ultracode mode; user session settings
- lines 203-211: Symlink checks, monorepo placement and project-vs-personal precedence for saved workflows; not the plugin location
- lines 342-345: User-side cache TTL setting and prefix stagger env var
- lines 384-408: Resuming runs after leaving the session, cloud sessions and usage-limit waits; session operation details
- lines 441-445: Settings that change when the Large workflow warning shows (size guideline, ultracode)
- lines 448-473: User cost tips, org availableModels allowlist and the user size guideline setting [confirmed on admin re-review]
- lines 478-485: How a user or organization (managed settings, admin page) turns workflows off [confirmed on admin re-review]
- lines 493-494: Ultracode availability and org effort caps [confirmed on admin re-review]
- lines 497-497: Link comparing parallel agent features; not used for plugins
- lines 499-499: Cost management link; not used for plugins [confirmed on admin re-review]

## 04-settings-admin/env-vars.md

- lines 16-16: Points to feature-flag fetching section, not used for building or installing plugins from a public marketplace
- lines 95-95: Managed settings deployed by an org admin: managed-only distribution [confirmed on admin re-review]
- lines 101-102: Model and IDE variable-vs-setting precedence, unrelated to plugin work
- lines 105-110: Vertex provider override, managed/project env restrictions and model/effort flag precedence; not acted on for plugin work [confirmed on admin re-review]
- lines 121-128: List of telemetry/demo/tmux presence-only variables, none used for plugin development or installation
- lines 133-186: Provider auth, model pinning, timeout and cloud-bundling variables; not used to develop, publish or install plugins
- lines 188-219: SDK, accessibility, compaction, artifact, auto mode, AWS and terminal variables unrelated to plugins
- lines 221-225: mTLS, MCP config lock and removed connect timeout variables; not plugin work
- lines 228-285: Feature disable toggles, provider and rendering variables, official marketplace autoinstall (official directory); not used for a public GitHub marketplace
- lines 287-304: Chrome, telemetry, task, permission, gateway and terminal variables unrelated to plugins
- lines 306-320: Fork mode, gateway, Git Bash, glob, IDE, compaction and subagent cap variables; user runtime tuning, not plugin work
- lines 322-322: Fork mode, gateway, Git Bash, glob, IDE, compaction and subagent cap variables; user runtime tuning, not plugin work
- lines 324-326: Output tokens, retries, subagent limits, MCP runtime tuning, OAuth, OTel, package manager and Perforce variables; not plugin work [confirmed on admin re-review]
- lines 328-329: Output tokens, retries, subagent limits, MCP runtime tuning, OAuth, OTel, package manager and Perforce variables; not plugin work [confirmed on admin re-review]
- lines 331-332: Output tokens, retries, subagent limits, MCP runtime tuning, OAuth, OTel, package manager and Perforce variables; not plugin work [confirmed on admin re-review]
- lines 334-353: Output tokens, retries, subagent limits, MCP runtime tuning, OAuth, OTel, package manager and Perforce variables; not plugin work [confirmed on admin re-review]
- lines 358-358: Offline/airgapped marketplace refresh fallback, not the remotely served public marketplace scenario
- lines 360-360: Container seed directories (org/managed distribution) and PowerShell, background wait, corporate launcher, prompt cache, proxy, cloud session, restricted mode and resume variables [confirmed on admin re-review]
- lines 362-368: Container seed directories (org/managed distribution) and PowerShell, background wait, corporate launcher, prompt cache, proxy, cloud session, restricted mode and resume variables [confirmed on admin re-review]
- lines 370-378: Container seed directories (org/managed distribution) and PowerShell, background wait, corporate launcher, prompt cache, proxy, cloud session, restricted mode and resume variables [confirmed on admin re-review]
- lines 380-382: Script caps, scroll speed and feedback variables unrelated to plugins
- lines 385-399: Shell selection, simple mode, provider auth skips, prompt history and startup failure variables; not plugin work
- lines 401-404: Subagent model, prompt cache TTL and env scrub user configuration; not acted on for plugin work
- lines 407-430: claude.ai skill sync, syntax, task list, tmpdir, tmux, memory caps, transcripts, dialogs, provider selection, disk warnings, WebFetch/WebSearch and workflow variables; not plugin work
- lines 431-432: Workflow cache stagger and You-should-know mod debug; not plugin work
- lines 434-437: Effort level and streaming watchdog variables; not used for plugin development or installation
- lines 439-444: Background job dir, PID, Remote Control and streaming timeout variables; not plugin work
- lines 446-473: Updater, compaction, command-hiding, telemetry, prompt caching, tracing and tool search variables; user/admin configuration unrelated to plugins [confirmed on admin re-review]
- lines 475-479: Hyperlinks, prompt cache, proxy and demo mode variables; not plugin work
- lines 481-510: Structured output, thinking, MCP OAuth/discovery cache/runtime tuning and OpenTelemetry variables; not plugin work
- lines 512-537: Removed task output, ripgrep, Vertex region overrides and OpenTelemetry notes; not used for a public plugin marketplace
- lines 539-566: Subprocess credential scrub is a user security setting, not acted on to build, publish or install plugins
- lines 567-601: Feature-flag fetching and its unavailable features (including claude.ai account plugin sync, not the public marketplace channel); not plugin work
- lines 606-607: Network and monitoring links unrelated to plugin work

## 04-settings-admin/github-enterprise-server.md

- lines 9-247: Entire page covers self-hosted GitHub Enterprise Server setup, cloud sessions, GHES-hosted and managed/org marketplaces; fails the public GitHub marketplace test [confirmed on admin re-review]

## 04-settings-admin/managed-settings.md

- lines 9-47: Whole page body is organization administration: deploying, combining, verifying and debugging managed settings (MDM, files, registry, server-managed, parent settings, managed-only keys, org telemetry). Neither the public marketplace maintainer nor a third-party user deploys managed policy; managed-only distribution/restriction controls fail the test. [confirmed on admin re-review]
- lines 49-75: Whole page body is organization administration: deploying, combining, verifying and debugging managed settings (MDM, files, registry, server-managed, parent settings, managed-only keys, org telemetry). Neither the public marketplace maintainer nor a third-party user deploys managed policy; managed-only distribution/restriction controls fail the test. [confirmed on admin re-review]
- lines 80-82: Whole page body is organization administration: deploying, combining, verifying and debugging managed settings (MDM, files, registry, server-managed, parent settings, managed-only keys, org telemetry). Neither the public marketplace maintainer nor a third-party user deploys managed policy; managed-only distribution/restriction controls fail the test. [confirmed on admin re-review]
- lines 90-398: Whole page body is organization administration: deploying, combining, verifying and debugging managed settings (MDM, files, registry, server-managed, parent settings, managed-only keys, org telemetry). Neither the public marketplace maintainer nor a third-party user deploys managed policy; managed-only distribution/restriction controls fail the test. [confirmed on admin re-review]
- lines 409-409: Whole page body is organization administration: deploying, combining, verifying and debugging managed settings (MDM, files, registry, server-managed, parent settings, managed-only keys, org telemetry). Neither the public marketplace maintainer nor a third-party user deploys managed policy; managed-only distribution/restriction controls fail the test. [confirmed on admin re-review]
- lines 413-413: Whole page body is organization administration: deploying, combining, verifying and debugging managed settings (MDM, files, registry, server-managed, parent settings, managed-only keys, org telemetry). Neither the public marketplace maintainer nor a third-party user deploys managed policy; managed-only distribution/restriction controls fail the test. [confirmed on admin re-review]
- lines 416-416: command and archive plugin sources excluded by user decision 2026-11-08
- lines 418-421: Whole page body is organization administration: deploying, combining, verifying and debugging managed settings (MDM, files, registry, server-managed, parent settings, managed-only keys, org telemetry). Neither the public marketplace maintainer nor a third-party user deploys managed policy; managed-only distribution/restriction controls fail the test. [confirmed on admin re-review]
- lines 424-426: Whole page body is organization administration: deploying, combining, verifying and debugging managed settings (MDM, files, registry, server-managed, parent settings, managed-only keys, org telemetry). Neither the public marketplace maintainer nor a third-party user deploys managed policy; managed-only distribution/restriction controls fail the test. [confirmed on admin re-review]
- lines 429-466: Whole page body is organization administration: deploying, combining, verifying and debugging managed settings (MDM, files, registry, server-managed, parent settings, managed-only keys, org telemetry). Neither the public marketplace maintainer nor a third-party user deploys managed policy; managed-only distribution/restriction controls fail the test. [confirmed on admin re-review]

## 04-settings-admin/permissions.md

- lines 9-10: Sharing permission settings across an organization via version control; not plugin authoring or installing [confirmed on admin re-review]
- lines 23-46: Interactive permission prompt UI, where saved approvals are stored, and commenting on prompts; end-user session UX, not used to build, publish or install plugins
- lines 62-62: audit: EndConversation exception unrelated to plugins
- lines 68-69: Auto mode tab in /permissions dialog; session UX unrelated to plugins
- lines 83-88: bypassPermissions warning and disabling bypass/auto mode, mainly for managed policy; not acted on for a public marketplace [confirmed on admin re-review]
- lines 463-530: Symlink and network-path permission checks for file tools; session security behavior not applied when writing plugin allowed-tools or hooks
- lines 554-557: WebFetch rule effect on claude.ai artifact reads; unrelated to plugins
- lines 570-571: Auto mode per-command sandbox domains; unrelated to plugins
- lines 588-591: Organization connector ask settings and Cowork workspace tools under managed rules; org/Cowork-specific [confirmed on admin re-review]
- lines 610-625: Cd rules for the user-run /cd command; not model-invocable and not part of plugin components
- lines 662-773: Working directories, /cd moves, additional directories, sandboxing interaction, managed settings and settings precedence; general session/admin configuration not relied on for a public plugin marketplace [confirmed on admin re-review]
- lines 776-800: Workspace trust keying and local settings trust; general session security unrelated to plugin distribution
- lines 807-808: Trust table rows for repository hooks/env/helpers and project allow rules; not plugin-related
- lines 810-822: Trust table rows for subagent inline MCP, .mcp.json and headersHelper plus advice for running claude -p in untrusted repos; not plugin distribution
- lines 823-826: Starter settings for organizational deployment scenarios; not plugin authoring or installation [confirmed on admin re-review]
- lines 830-833: See-also links to org auto mode config, sandboxing, authentication and security; not relied on for the public marketplace [confirmed on admin re-review]

## 04-settings-admin/server-managed-settings.md

- lines 9-131: Whole page body covers Team/Enterprise server-managed settings from the claude.ai admin console (requirements, configuration, delivery, caching, approval dialogs, platform availability, audit, security); org-managed administration that neither the public marketplace maintainer nor a third-party user performs. [confirmed on admin re-review]
- lines 134-269: Whole page body covers Team/Enterprise server-managed settings from the claude.ai admin console (requirements, configuration, delivery, caching, approval dialogs, platform availability, audit, security); org-managed administration that neither the public marketplace maintainer nor a third-party user performs. [confirmed on admin re-review]
- lines 272-283: Whole page body covers Team/Enterprise server-managed settings from the claude.ai admin console (requirements, configuration, delivery, caching, approval dialogs, platform availability, audit, security); org-managed administration that neither the public marketplace maintainer nor a third-party user performs. [confirmed on admin re-review]
- lines 286-302: Whole page body covers Team/Enterprise server-managed settings from the claude.ai admin console (requirements, configuration, delivery, caching, approval dialogs, platform availability, audit, security); org-managed administration that neither the public marketplace maintainer nor a third-party user performs. [confirmed on admin re-review]
- lines 305-306: Whole page body covers Team/Enterprise server-managed settings from the claude.ai admin console (requirements, configuration, delivery, caching, approval dialogs, platform availability, audit, security); org-managed administration that neither the public marketplace maintainer nor a third-party user performs. [confirmed on admin re-review]
- lines 310-340: Whole page body covers Team/Enterprise server-managed settings from the claude.ai admin console (requirements, configuration, delivery, caching, approval dialogs, platform availability, audit, security); org-managed administration that neither the public marketplace maintainer nor a third-party user performs. [confirmed on admin re-review]
- lines 343-356: Whole page body covers Team/Enterprise server-managed settings from the claude.ai admin console (requirements, configuration, delivery, caching, approval dialogs, platform availability, audit, security); org-managed administration that neither the public marketplace maintainer nor a third-party user performs. [confirmed on admin re-review]
- lines 359-400: Whole page body covers Team/Enterprise server-managed settings from the claude.ai admin console (requirements, configuration, delivery, caching, approval dialogs, platform availability, audit, security); org-managed administration that neither the public marketplace maintainer nor a third-party user performs. [confirmed on admin re-review]

## 04-settings-admin/settings-reference.md

- lines 19-19: Index row for advisor model setting; unrelated to building, publishing or installing plugins from a public marketplace
- lines 21-23: Index rows for general, managed-only, auth, provider, model, memory, UI and update settings; none is applied when maintaining or installing marketplace plugins [confirmed on admin re-review]
- lines 27-27: Index rows for general, managed-only, auth, provider, model, memory, UI and update settings; none is applied when maintaining or installing marketplace plugins [confirmed on admin re-review]
- lines 30-57: Index rows for general, managed-only, auth, provider, model, memory, UI and update settings; none is applied when maintaining or installing marketplace plugins [confirmed on admin re-review]
- lines 59-70: Index rows for general, managed-only, auth, provider, model, memory, UI and update settings; none is applied when maintaining or installing marketplace plugins [confirmed on admin re-review]
- lines 72-76: Index rows for general, managed-only, auth, provider, model, memory, UI and update settings; none is applied when maintaining or installing marketplace plugins [confirmed on admin re-review]
- lines 78-88: Index rows for desktop, MCP-managed, managed-only marketplace blocking, sideload and remote-control settings; org/managed or unrelated [confirmed on admin re-review] + command and archive plugin sources excluded by user decision 2026-11-08
- lines 91-97: Index rows for workflows, editor, effort, emoji, artifact and MCP approval settings; unrelated to plugin marketplace work
- lines 99-102: Index rows for workflows, model allowlist, env and external editor settings; unrelated [confirmed on admin re-review]
- lines 104-118: Index rows for model, feedback, login, gateway, hooks-in-settings, HTTP hook limits, notifications, managed MCP and managed sources; not plugin distribution or install [confirmed on admin re-review]
- lines 120-138: Index rows for model, feedback, login, gateway, hooks-in-settings, HTTP hook limits, notifications, managed MCP and managed sources; not plugin distribution or install [confirmed on admin re-review]
- lines 140-151: Index rows for managed parent settings, permissions and plan directory; general configuration, not plugin marketplace work [confirmed on admin re-review]
- lines 155-214: Index rows for managed-only marketplace suggestion/trust message, policy helper, mods, sandbox, PR links, remote and model display settings; managed/org-only or unrelated [confirmed on admin re-review]
- lines 218-228: Index rows for permission prompts, UI, SSH, status line, managed-only strictKnownMarketplaces/strictPluginOnlyCustomization and prompt cache; managed/org-only or unrelated [confirmed on admin re-review]
- lines 235-235: Index rows for permission prompts, UI, SSH, status line, managed-only strictKnownMarketplaces/strictPluginOnlyCustomization and prompt cache; managed/org-only or unrelated [confirmed on admin re-review]
- lines 237-266: Index rows for model switching, claude.ai-synced plugins/skills (another channel), UI, teams, voice, workflows, worktrees and WSL managed settings; unrelated or another channel [confirmed on admin re-review]
- lines 270-690: Model and responses entries (advisor, thinking, model allowlists, effort, fast mode, language, model picker, pricing, modelSettings) are not applied when developing, publishing or installing marketplace plugins [confirmed on admin re-review]
- lines 709-806: Remaining model/response settings (prompt cache TTLs, thinking summaries, classifier model switching, ultracode) are not used to build, publish or install marketplace plugins
- lines 847-1216: Permission settings section: managed-only rule lockdown, auto mode classifier, permission rules, working-directory blocks and bypass prompts are general session security config, not applied for a public plugin marketplace (the managed-only allowed-tools note is org-internal) [confirmed on admin re-review]
- lines 1217-2014: Sandbox settings for Bash isolation, filesystem/network/credential masking and managed-only binary paths; unrelated to developing, publishing or installing marketplace plugins [confirmed on admin re-review]
- lines 2015-2249: Sandbox network settings (sockets, domains, proxies, TLS, managed domain locks): end-user/admin security config, not used to build, publish or install plugins from a public marketplace [confirmed on admin re-review]
- lines 2254-2543: Compaction, auto memory, bash output limits, managed claudeMd, CLAUDE.md excludes, env, checkpointing, idle compaction, plans directory: general session behavior unrelated to plugin development or marketplace installation [confirmed on admin re-review]
- lines 2576-2583: Removed taskOutputMaxChars key: no effect, unrelated to plugins
- lines 2588-3113: Interface and terminal preferences (timeouts, announcements, shell, dialogs, editor, emoji, file suggestion, footer badges, motion, spinner tips/verbs, statusLine): personal UI settings; plugins can't supply these via settings
- lines 3133-3184: Syntax highlighting, terminal progress bar, terminal title: personal UI settings unrelated to plugins
- lines 3209-3278: Time format, time zone, TUI renderer: personal UI settings unrelated to plugins
- lines 3298-3538: viewMode, vim remaps, voice, scroll, git attribution settings, HTTP hook URL allowlist and managed-only hooks policy: personal/admin settings not used for the public marketplace scenario; the Hooks and automation section's remaining keys are all removed in the next chunk too, so its heading goes [confirmed on admin re-review]
- lines 3561-3562: viewMode, vim remaps, voice, scroll, git attribution settings, HTTP hook URL allowlist and managed-only hooks policy: personal/admin settings not used for the public marketplace scenario; the Hooks and automation section's remaining keys are all removed in the next chunk too, so its heading goes [confirmed on admin re-review]
- lines 3587-3588: command and archive plugin sources excluded by user decision 2026-11-08
- lines 3612-3612: disableAllHooks, workflows, settings-file hooks key, HTTP hook env allowlist, workflow keyword/size: user/admin session settings; plugin hooks are authored in the plugin, not via these keys [confirmed on admin re-review]
- lines 3622-3623: disableAllHooks, workflows, settings-file hooks key, HTTP hook env allowlist, workflow keyword/size: user/admin session settings; plugin hooks are authored in the plugin, not via these keys [confirmed on admin re-review]
- lines 3635-3697: disableAllHooks, workflows, settings-file hooks key, HTTP hook env allowlist, workflow keyword/size: user/admin session settings; plugin hooks are authored in the plugin, not via these keys [confirmed on admin re-review]
- lines 3716-3753: disableAllHooks, workflows, settings-file hooks key, HTTP hook env allowlist, workflow keyword/size: user/admin session settings; plugin hooks are authored in the plugin, not via these keys [confirmed on admin re-review]
- lines 3758-3776: disableBundledSkills affects built-in skills only, not plugin skills
- lines 3795-3859: skillOverrides (excludes plugin skills), claude.ai skill/plugin sync (other distribution channel), channel plugin allowlist, managed marketplace blocklist/allowlist, command sources, suggestions, trust message, strictKnownMarketplaces and strictPluginOnlyCustomization: managed/org-only or non-public-marketplace distribution [confirmed on admin re-review]
- lines 3923-3940: command and archive plugin sources excluded by user decision 2026-11-08
- lines 3957-3970: skillOverrides (excludes plugin skills), claude.ai skill/plugin sync (other distribution channel), channel plugin allowlist, managed marketplace blocklist/allowlist, command sources, suggestions, trust message, strictKnownMarketplaces and strictPluginOnlyCustomization: managed/org-only or non-public-marketplace distribution [confirmed on admin re-review]
- lines 4002-4008: skillOverrides (excludes plugin skills), claude.ai skill/plugin sync (other distribution channel), channel plugin allowlist, managed marketplace blocklist/allowlist, command sources, suggestions, trust message, strictKnownMarketplaces and strictPluginOnlyCustomization: managed/org-only or non-public-marketplace distribution [confirmed on admin re-review]
- lines 4010-4022: skillOverrides (excludes plugin skills), claude.ai skill/plugin sync (other distribution channel), channel plugin allowlist, managed marketplace blocklist/allowlist, command sources, suggestions, trust message, strictKnownMarketplaces and strictPluginOnlyCustomization: managed/org-only or non-public-marketplace distribution [confirmed on admin re-review]
- lines 4061-4080: skillOverrides (excludes plugin skills), claude.ai skill/plugin sync (other distribution channel), channel plugin allowlist, managed marketplace blocklist/allowlist, command sources, suggestions, trust message, strictKnownMarketplaces and strictPluginOnlyCustomization: managed/org-only or non-public-marketplace distribution [confirmed on admin re-review]
- lines 4268-4269: url and file marketplace source types: non-GitHub hosting / local file distribution
- lines 4271-4274: Inline settings marketplace source and self-hosted/private git authentication: not a public GitHub marketplace
- lines 4279-4317: headersHelper for url sources and inline settings-source plugin entries with headers: authenticated/non-GitHub or settings-declared distribution
- lines 4349-4350: Built-in plugin @builtin option IDs (AGENTS.md): not relevant to third-party plugins
- lines 4353-4392: prependPlugins/appendPlugins (managed org mods) and MCP policy/approval settings: org-managed or end-user MCP config, not marketplace plugin work [confirmed on admin re-review]
- lines 4397-4432: prependPlugins/appendPlugins (managed org mods) and MCP policy/approval settings: org-managed or end-user MCP config, not marketplace plugin work [confirmed on admin re-review]
- lines 4498-4591: prependPlugins/appendPlugins (managed org mods) and MCP policy/approval settings: org-managed or end-user MCP config, not marketplace plugin work [confirmed on admin re-review]
- lines 4613-4932: Cross-session messaging, agent view, process wrapper, teammates, worktrees, remote/desktop/notification settings: unrelated to building or installing plugins
- lines 4933-5552: Remote Control, desktop/SSH, notifications, authentication providers and login enforcement, update channels and version pins, desktop tools, privacy/telemetry, managed-settings machinery (incl. disableSideloadFlags, managed-only), and ~/.claude.json UI keys: none is applied to develop, publish or install plugins from a public GitHub marketplace [confirmed on admin re-review]
- lines 5586-6034: Remote Control, desktop/SSH, notifications, authentication providers and login enforcement, update channels and version pins, desktop tools, privacy/telemetry, managed-settings machinery (incl. disableSideloadFlags, managed-only), and ~/.claude.json UI keys: none is applied to develop, publish or install plugins from a public GitHub marketplace [confirmed on admin re-review]
- lines 6040-6040: audit: generic example-settings link
- lines 6041-6042: links to organization managed-settings setup and deployment, managed-only distribution [confirmed on admin re-review]

## 04-settings-admin/settings.md

- lines 92-92: pre-v2.1.211 local-file location history and Agent SDK resolveSettings detail, not acted on for plugins
- lines 99-108: checking organization enforcement and managed delivery mechanisms, managed-only [confirmed on admin re-review]
- lines 114-129: system prompt/CLAUDE.md note and /config menu for personal UI options; no plugin or marketplace use
- lines 166-175: /model and /effort saving behavior and model example, unrelated to plugins
- lines 182-188: model/effort and blockReadsOutsideWorkingDirectories reload exceptions, unrelated to plugins
- lines 201-201: invalid managed settings handling, managed-only [confirmed on admin re-review]
- lines 224-224: pointer to managed precedence exceptions, managed-only [confirmed on admin re-review]
- lines 230-234: model-list merge rules (fallbackModel, modelPicker, availableModels, modelSettings), unrelated to plugins
- lines 245-250: organization managed override example, managed-only [confirmed on admin re-review]
- lines 257-262: model flag/env var override example, unrelated to plugins
- lines 272-275: security-key, permission mode and telemetry env restrictions, unrelated to plugin distribution [confirmed on admin re-review]
- lines 284-287: managed change delivery troubleshooting, managed-only [confirmed on admin re-review]
- lines 297-322: permission rule combination and managed precedence exceptions table, not used for plugin development or install [confirmed on admin re-review]
- lines 327-327: project cloud threads ignoring permission rules/hooks/env, not a plugin marketplace workflow
- lines 331-332: managed settings in cloud and cloud /config/env var changes, managed-only or unrelated [confirmed on admin re-review]
- lines 340-340: permissions page link, not needed for plugin scenario

## 05-cli-diagnostics/changelog.md

- lines 20-36: 2.1.319 Added: env vars, permissions, gateway, billing, cloud, Claude Tag entries unrelated to building or installing marketplace plugins
- lines 40-42: auto mode/gateway and MCP task feature-flag changes not acted on by plugin maintainer or user
- lines 44-50: Bash/permission/proxy changes, --add-dir local marketplace registration, project .claude/skills loading, /loop; not plugin marketplace work
- lines 52-61: subagent, cloud, TLS, artifacts, Chrome, self-hosted runner, VSCode, Code Review changes unrelated to plugins
- lines 65-76: general UX/gateway improvements unrelated to plugins
- lines 78-80: VSCode gateway sign-in, diagnostics tool, cloud self-hosted warnings
- lines 85-115: general bug fixes (diff, auth, auto mode, Bash, settings, SDK, editor) unrelated to plugin development or installation
- lines 118-118: terminal link fix unrelated to plugins
- lines 120-155: rewind, claude-api skill, artifacts, telemetry, agents view, cloud, runner, permission and managed fixes unrelated to plugins [confirmed on admin re-review]
- lines 158-173: subagent, gateway, runner, VSCode, cloud, Claude Tag fixes unrelated to plugins
- lines 181-182: mod opt-in record and gateway assume_role not relied on for plugin marketplace
- lines 184-191: auth expiry, gateway, self-hosted runner, cloud session additions
- lines 195-198: IDE install and subagent model/background changes
- lines 200-205: managed deniedMcpServers, /permissions UI, claude-api skill, thinking, runner logs, cloud connectors [confirmed on admin re-review]
- lines 207-224: 2.1.318 improvements section: none relate to plugins
- lines 227-232: general session, auth and claude mcp config fixes unrelated to plugins
- lines 236-239: allowedProviders, compaction, credits notice, slash command output fixes
- lines 241-259: headless, remote-control, cloud, cert, workflows, notification fixes unrelated to plugins
- lines 261-273: config backup, login, VSCode, cloud, Claude Tag fixes
- lines 279-290: 2.1.317 Added: schedule, SDK hooks, desktop managed notice, OTel, gateway, runner, cloud; none for plugin marketplace [confirmed on admin re-review]
- lines 294-295: SendMessage and subagent effort changes
- lines 297-300: built-in skill behavior, Read stub, cloud admin, Claude Tag [confirmed on admin re-review]
- lines 302-312: 2.1.317 improvements: none relate to plugins
- lines 315-340: desktop MCP, auto mode, auth, claude.ai-synced skills/plugins, settings, teams, gateway fixes; not public marketplace plugins
- lines 342-376: Bedrock env, TLS, compaction, OTel, Windows, gateway, runner, VSCode, cloud, Remote Control fixes
- lines 382-411: 2.1.316 Added, Changed and improvements: env vars, gateway, managed settings, cloud, Claude Tag, Code Review; none plugin-related [confirmed on admin re-review]
- lines 414-416: Bash tool shell fixes
- lines 418-428: network, model fallback, gateway, auth, restricted mode, prompt, auto mode fixes [confirmed on admin re-review]
- lines 430-447: SDK, artifacts, model, UI, runner, Windows, VSCode, cloud, Claude Tag fixes
- lines 453-461: 2.1.314 Added: permissions, gateway, idle compaction, cloud, Claude Tag
- lines 464-471: bundled skills, settings edit prompts, Bash which, permissions, Cowork auto mode changes
- lines 473-499: claude-api skill, model fallback, compaction, hyperlinks, macOS git, VSCode, cloud changes and the whole improvements section
- lines 502-512: effort, provider, TLS, MCP auth, managed settings (incl. managed plugin settings), usage limit, tool call fixes [confirmed on admin re-review]
- lines 514-518: effort, provider, TLS, MCP auth, managed settings (incl. managed plugin settings), usage limit, tool call fixes [confirmed on admin re-review]
- lines 520-529: diff, UI, transcript, remote-control, sandbox fixes
- lines 531-582: settings sources, auto mode, gateway, UI, vim, trash cleanup, runner, VSCode, cloud, Claude Tag fixes
- lines 588-594: 2.1.312 Added: gateway, fullscreen, cloud routines
- lines 597-600: provider system prompt, model switch, usage labels, cloud names
- lines 603-637: official Anthropic marketplace OTel naming, telemetry, VSCode, improvements and bug fixes unrelated to public marketplace plugins
- lines 643-650: 2.1.311 Added: runner flags, tips, VSCode UI, Claude Tag
- lines 653-659: ultrathink, agent view, JSON escaping, model names, warnings, code-review
- lines 661-687: model catalog, skills sync, UI, VSCode, Claude Tag changes and the whole improvements section
- lines 690-696: startup, interrupt, context, Write, subagent MCP, memory, transcript fixes
- lines 698-729: file picker, worktree, Bash, mcp CLI, Remote Control, cloud, background, UI fixes
- lines 731-745: usage, status line, rewind, retry, sandbox, runner, VSCode, cloud fixes
- lines 754-755: cloud custom roles and setup script file
- lines 757-771: 2.1.310 Changed and improvements: MCP timeout message, cloud admin, auto mode, memory, mod image terminal support, sandbox, Code Review [confirmed on admin re-review]
- lines 774-778: gateway, cleanup, compaction, permission prompt, question fixes
- lines 780-787: VSCode, cloud, Claude Tag, Code Review fixes
- lines 793-807: 2.1.309 Added and Changed: VSCode TLS, bundled skills, sed, ultrareview, rm prompt, sandbox, worktrees, claude-api
- lines 810-810: Windows git speed
- lines 812-817: disk-full handling, claude-api skill, runner, VSCode, cloud improvements
- lines 821-851: sandbox, permission, worktree, UI, feedback, add-dir skills, claude-api skill fixes
- lines 854-955: claude.ai-synced plugins, artifacts, Bedrock, GitHub mentions, platform, VSCode, cloud, Claude Tag, Code Review fixes; 2.1.308, 2.1.307 and 2.1.306 have no plugin-related entries
- lines 960-966: 2.1.305 Added: sandbox namespaces, retry watchdog, VSCode hook spinner, Claude Tag
- lines 969-971: managed-mcp allowlist, Desktop-mounted plugins under managed settings, artifacts confirmation [confirmed on admin re-review]
- lines 973-1008: VSCode, Code Review changes; improvements and bug fixes with no plugin relevance
- lines 1019-1025: auto-mode-setup, claude-api, compaction, Pro/Max warning, VSCode, Code Review additions
- lines 1029-1033: managed mod settings ceiling (org-internal), artifacts, mod opt-in question, tool search, compaction skill list [confirmed on admin re-review]
- lines 1036-1036: managed plugins-only hooks policy (org-internal) and claude-api skill [confirmed on admin re-review]
- lines 1038-1055: fast label, VSCode subagents; improvements section with claude.ai-synced plugins and general perf
- lines 1058-1061: policy refresh, sandbox, rm prompt, transcript GC fixes [confirmed on admin re-review]
- lines 1065-1088: managed-settings mod sharing, Cowork, claude.ai Directory plugin, Remote Control, SDK, UI and other fixes not for public marketplace plugins [confirmed on admin re-review]
- lines 1090-1107: UI, VSCode, cloud, Claude Tag, Code Review fixes; 2.1.303 has only generic fixes
- lines 1112-1118: 2.1.302 Added: auto mode model, idle compaction, design notice, cloud banner
- lines 1121-1125: permission mode, fork subagents, background subagents, footer, Chrome prompt
- lines 1127-1129: feedback policy message and Claude Tag admin [confirmed on admin re-review]
- lines 1134-1139: auto mode, gateway, cloud, Claude Tag improvements
- lines 1143-1147: compaction, provider, Read, gateway, prompt cache fixes
- lines 1151-1185: desktop MCP, artifacts, OTel, UI, built-in plugin lookup, worktree, cloud, runner, VSCode, Claude Tag, Code Review fixes
- lines 1193-1195: retry watchdog, claude-api skill, vim motion
- lines 1197-1200: OTel attributes and VSCode additions
- lines 1209-1211: model switching, rendering and artifact changes unrelated to plugin development or installation
- lines 1216-1221: general CLI, model alias, login, search, workflow and artifact fixes not used for plugins
- lines 1224-1238: terminal, auth, model, vim, Read and session fixes unrelated to plugins
- lines 1240-1242: diff, workflow and theme fixes unrelated to plugins
- lines 1244-1252: fullscreen, self-hosted runner, Windows and VS Code fixes unrelated to plugins
- lines 1261-1261: OpenTelemetry field, not a plugin concern
- lines 1264-1265: advisor on AWS and OpenTelemetry attributes, not plugin related
- lines 1268-1271: VS Code setting and Claude Tag Slack features unrelated to plugins
- lines 1275-1284: provider, gateway, Desktop, sandbox, Cowork and transcript changes unrelated to plugins
- lines 1286-1287: remote-control flag removal and Claude Tag change, not plugin related
- lines 1291-1291: Cowork WebFetch improvement, not plugin related
- lines 1293-1294: Claude 3 PDF note and artifact updates, not plugin related
- lines 1298-1312: cloud session, autocompact, agents view, login, transcript fixes unrelated to plugins
- lines 1314-1316: OpenTelemetry and transcript display fixes, not acted on by plugin maintainer or user
- lines 1318-1323: worktree, scratchpad, remote-control and IDE launch fixes unrelated to plugins
- lines 1326-1356: headless/SDK resume, Remote Control, daemon, cloud session, runner, VS Code, Claude Tag and Code Review fixes unrelated to plugins
- lines 1364-1368: file mention env var, idle compaction, and managed-settings-only mod APIs [confirmed on admin re-review]
- lines 1370-1370: self-hosted runner orchestrator flag
- lines 1372-1374: agent view, safe mode and plan mode notes unrelated to plugins
- lines 1376-1377: Claude apps gateway attribution header settings
- lines 1380-1381: /usage warnings and Claude Tag canvas, not plugin related
- lines 1387-1388: connector proxy and cloud MCP proxy redirect behavior, not plugin related
- lines 1391-1391: WebFetch effort selection, not plugin related
- lines 1393-1393: user permission rule syntax for MCP, not a plugin authoring or install step
- lines 1395-1401: Chrome in Cowork, cloud MCP negotiation, first-party MCP, auto mode, resume command and /btw changes
- lines 1405-1409: ultrareview, cyber notice, cloud environments and Claude Tag changes
- lines 1413-1418: runner, cloud login, managed enforcement, PDF, sandbox and model ID improvements [confirmed on admin re-review]
- lines 1420-1428: Skill tool prefix, reload-skills, worktree, artifact, notifications, VS Code and cloud improvements unrelated to plugin distribution
- lines 1432-1449: cloud, gateway, Remote Control, sandbox, debug log, MCP list and scheduling fixes unrelated to plugins
- lines 1451-1463: Remote Control, sandbox, MCP naming, claude.ai-synced/Cowork plugins, artifact and Chrome fixes outside scenario
- lines 1465-1467: gateway and ANTHROPIC_BASE_URL fixes
- lines 1469-1469: enabledMcpjsonServers settings fix, not plugin related
- lines 1471-1471: cloud/Remote Control memory fix
- lines 1474-1484: usage display, text wrapping, cloud, Cowork account plugins, MCP rules, images, telemetry and gateway key fixes
- lines 1487-1488: cloud session regression and scheduler fix
- lines 1490-1495: settings validation, paste, managed settings and MCP policy fixes [confirmed on admin re-review]
- lines 1497-1500: text layout, bare mode and Remote Control fixes
- lines 1502-1508: push notification, cloud, Read, prompt, stream-json and runner fixes
- lines 1510-1531: prompt rendering, managed login, bare, Remote Control, SDK, scheduling, sandbox, worktree, background, runner, Ultracode, MCP OAuth and artifact fixes [confirmed on admin re-review]
- lines 1537-1547: background subagent, SendMessage, token limit, encoding, cloud, Remote Control, managed-hook env and Windows process fixes [confirmed on admin re-review]
- lines 1549-1562: Windows Bash, runner, VS Code, cloud sessions, Remote Control, Claude Tag and Code Review fixes
- lines 1570-1570: Claude apps gateway policy key [confirmed on admin re-review]
- lines 1572-1573: workflow model and retry delay env vars
- lines 1575-1577: Read option, cloud admin filters and Claude Tag memory [confirmed on admin re-review]
- lines 1581-1582: pricing and bundled dataviz skill updates
- lines 1584-1586: backgrounding, VS Code Chrome and Claude Tag footer changes
- lines 1590-1593: fullscreen, transcript, Desktop gateway and cloud error improvements
- lines 1595-1595: auto mode display
- lines 1597-1598: transcript GC and Code Review admin [confirmed on admin re-review]
- lines 1602-1603: managed-settings hooks, headless MCP, gateway, teleport, token count and subagent fixes [confirmed on admin re-review]
- lines 1605-1609: managed-settings hooks, headless MCP, gateway, teleport, token count and subagent fixes [confirmed on admin re-review]
- lines 1611-1614: secret redaction, terminal escape, toasts and headless interrupt fixes
- lines 1616-1618: self-hosted runner and workflow script fixes
- lines 1624-1630: cloud auto mode, resume, Bash permission, encoding, backgrounding and headless /clear fixes
- lines 1632-1643: cloud MCP wording, code-review, artifacts, claude.ai-synced skills/plugins, local path, workflow, telemetry, transcript and Windows fixes outside scenario
- lines 1645-1657: Windows rm, VS Code, cloud sessions, Claude Tag and Code Review fixes
- lines 1666-1667: terminal status protocol and /copy picker
- lines 1669-1673: claude -p stderr line, gateway timeouts, backgrounding message, gateway models and login method
- lines 1675-1675: gateway audit field
- lines 1678-1681: retry watchdog, gateway header, VS Code file row and Claude Tag admin [confirmed on admin re-review]
- lines 1687-1690: Ctrl+C loop, claude agents, claude.ai connectors and artifact background changes
- lines 1692-1700: tab stops, artifact permissions, routines, org mod toasts, gateway, WebSocket MCP, runner and Claude Tag changes [confirmed on admin re-review]
- lines 1704-1711: gateway, Remote Control status, usage warnings, built-in plugin-authoring wording and Grep improvements
- lines 1713-1716: workflow tool, upload message and cloud session improvements
- lines 1720-1727: 1M context, claude -p output, MCP connection, Bash and Chrome fixes not tied to plugins
- lines 1730-1742: backgrounding, push, remote files, managed settings, display, gateway, subagent worktree and tools flag fixes [confirmed on admin re-review]
- lines 1744-1754: loop, env color, claude agents, agent naming, Bash, workflow, teammate, TaskStop, MCP stop, loop and hyperlink fixes
- lines 1756-1760: advisor dialog, MCP task id, vim, paste and terminal freeze fixes
- lines 1764-1765: SendMessage resume and Bash read tracking fixes
- lines 1770-1771: piped output and quote rendering fixes
- lines 1773-1773: claude mcp serve output fix
- lines 1777-1778: managed-settings cache and Claude 3 tool search fixes [confirmed on admin re-review]
- lines 1780-1781: text rendering and /model effort wording
- lines 1783-1783: Read pages parameter fix
- lines 1786-1790: queued message, SDK hot-reload question, prompt history, MCP auth notice and gateway telemetry fixes
- lines 1792-1802: Edit, CRLF, scheduling, syntax highlight, ultrareview, auto mode, claude.ai-synced plugins, rewind, cloud mod hang, macOS and SDK MCP fixes outside scenario
- lines 1804-1816: macOS, VS Code, runner, cloud, Claude Tag, Code Review and effort fixes
- lines 1831-1832: new Haiku model and subagent status line field
- lines 1835-1855: Changed and improvements sections of 2.1.293 hold no plugin-relevant entries (auto mode, skill sync, ordering, telemetry, runner, Chrome, artifacts, Claude Tag, Code Review)
- lines 1858-1874: compaction, MCP memory, backgrounding, model, Chrome, subagent, synced skill, auth, agents view, artifact, ultrareview, Remote Control fixes
- lines 1878-1895: gateway, claude agents, backgrounding, rules loading, paste, feedback, purge, keybindings, vim, Windows and Claude Tag fixes
- lines 1904-1905: Agent tool effort and retry delay env var
- lines 1909-1910: Claude Tag and Code Review additions
- lines 1914-1914: stdio MCP protocol negotiation default, not acted on
- lines 1916-1917: usage links and routine artifact changes
- lines 1919-1920: Claude Tag changes
- lines 1924-1926: startup, rendering and draft recovery improvements
- lines 1928-1928: tool input tolerance improvement
- lines 1930-1936: sandbox, artifact, cloud, Chrome, focus, stdio MCP and Claude Tag improvements
- lines 1940-1946: subagent permission mode, sandbox, managed cache, Windows rm, UNC, allowed-tools mode and NO_PROXY fixes [confirmed on admin re-review]
- lines 1948-1948: subagent permission mode, sandbox, managed cache, Windows rm, UNC, allowed-tools mode and NO_PROXY fixes [confirmed on admin re-review]
- lines 1951-1971: managed-settings ordering, headless, scheduling, Grep, Read, usage, Remote Control, desktop, feedback, vim, paste, fullscreen and compaction fixes [confirmed on admin re-review]
- lines 1973-1977: cloud and Cowork session fixes
- lines 1989-1989: organization-managed plugin precedence, managed-only distribution [confirmed on admin re-review]
- lines 1993-2003: cloud sessions, Remote Control, Claude Tag and Code Review fixes
- lines 2005-2011: 2.1.291 holds only cloud session and quit regressions unrelated to plugins
- lines 2023-2029: gateway sign-in, attach/logs, claude-api onboarding, managed settings warnings and VS Code screen reader [confirmed on admin re-review]
- lines 2031-2032: Claude Tag additions
- lines 2036-2038: nonessential traffic, Chrome project settings and pyright permission changes
- lines 2040-2040: daemon log format
- lines 2042-2043: /artifacts and ps permission changes
- lines 2045-2054: background sessions, prompt confirm, ultrareview, code-review, teammate ids, loop, claude agents, gateway, WebSearch and attachments changes
- lines 2056-2060: cloud gh api, claude-api skill, runner, VS Code timestamps and Claude Tag changes
- lines 2064-2065: MCP proxy retry and background agent shortcut
- lines 2068-2082: Bash diff, gateway, cloud login, Read binary, ultrareview, Chrome, resume, suggestions, VS Code and Claude Tag improvements
- lines 2086-2104: proxy betas, images, content filter, subagent, WebFetch, crash, rewind, scheduling, headless, plan mode, rules, URL patterns, org MCP, ultrareview, daemon and runner fixes [confirmed on admin re-review]
- lines 2107-2107: Cowork cloud reply fix
- lines 2109-2110: ultrareview and effort fixes
- lines 2112-2113: permissions tab hang and compaction error
- lines 2118-2119: image read safety, org plugin precedence and managed MCP rules [confirmed on admin re-review]
- lines 2122-2128: @-mention safety, agents view, permission rules, Read deny and org guard precedence fixes [confirmed on admin re-review]
- lines 2130-2150: agents view, language, freezes, respawn, ultrareview, auto mode, teleport, channels, Chrome, gateway mods, sandbox, Homebrew and Bash permission fixes
- lines 2152-2164: Bash/sandbox, feature flags, ultrareview, cloud, gateway, Monitor, workflow, SDK startup and sleep fixes
- lines 2166-2171: plan loss, Bash aliases, MCP memory, artifacts, remote files and plan restore fixes
- lines 2173-2187: compaction, rewind, AGENTS.md, runner, secret scan, Bash rules, dialog timeout, MCP listing, paste, Chrome, worktree, gateway telemetry, restricted and background fixes [confirmed on admin re-review]
- lines 2189-2189: secret masking freeze
- lines 2191-2216: login, display, paste, keychain, SDK, sandbox, scheduling, settings symlink, VS Code, cloud, Remote Control, Claude Tag and Code Review fixes
- lines 2226-2229: Changed section holds only a VS Code auth status revert
- lines 2237-2239: managed-machine mod rule, terminal freeze and Read deny symlink fixes [confirmed on admin re-review]
- lines 2244-2244: organization-managed MCP server protection, managed-only [confirmed on admin re-review]
- lines 2248-2249: Bash deny rules under sandbox auto-allow
- lines 2252-2252: general text rendering fix
- lines 2255-2255: Anthropic official marketplace plugin validation
- lines 2258-2258: published artifact page fix
- lines 2268-2273: cloud gh api, Ctrl+C recovery, MCP scope reauth, code-review, agents view and screen reader additions
- lines 2275-2298: Changed and improvements sections of 2.1.288 hold no plugin-relevant entries
- lines 2301-2312: API timeout, compaction, resume, structured outputs, auto mode, cloud and Cowork fixes
- lines 2319-2321: background session timing and Bash/sandbox permission fixes
- lines 2323-2330: cross-session messaging, telemetry, Cowork, retry watchdog, login, Bedrock and auth refresh fixes
- lines 2332-2336: SIGTERM, cloud model, MCP duplicate call, Desktop memory server and Chrome fixes
- lines 2338-2338: sandbox credentials setting fix
- lines 2339-2340: artifact/Windows keyboard fixes unrelated to plugin development or installation
- lines 2342-2344: model, npm auto-updater and Remote Control fixes unrelated to plugins
- lines 2346-2347: project rules loading and rm safeguard fixes, not plugin behavior
- lines 2351-2353: output limit, UI hint and --bare login fixes unrelated to plugins
- lines 2355-2363: mcp serve, UI, VSCode, cloud sessions and Claude Tag fixes unrelated to plugins
- lines 2373-2375: built-in mod, agents view filter and OTel field; not used for a public marketplace
- lines 2377-2380: Windows shell warning, self-hosted runner and VSCode features unrelated to plugins
- lines 2384-2388: permission, context window, agents and paste changes unrelated to plugins
- lines 2390-2393: screen reader, model switch, prompt order and Chrome changes unrelated to plugins
- lines 2397-2397: /config UI improvement
- lines 2400-2402: gateway, SDK and /memory improvements unrelated to plugins
- lines 2404-2413: UI, file delivery, MCP headless and Windows improvements unrelated to plugins
- lines 2415-2416: Claude Tag and Code Review improvements
- lines 2420-2421: fast mode and Remote Control fixes
- lines 2423-2463: SDK, model, screen reader, cloud, --plugin-url/http sparse and synced-plugin fixes not relevant to a public GitHub marketplace
- lines 2465-2486: cloud, remote, platform, VSCode, Claude Tag and Code Review fixes unrelated to plugins
- lines 2492-2500: Added section of 2.1.286 has no plugin-relevant entries
- lines 2502-2519: Changed section of 2.1.286 has no entries relevant to a public GitHub marketplace (npm sources are another host)
- lines 2523-2536: UI, commit guidance, prompt and gateway improvements unrelated to plugins
- lines 2538-2538: Claude Tag improvement
- lines 2542-2575: auth, resume, redaction, MCP connector, claude.ai plugin sync and subagent fixes unrelated to marketplace plugins
- lines 2577-2590: cosmetic /plugin quoting and Windows, VSCode, cloud, Claude Tag fixes
- lines 2598-2599: WebFetch env var and --desktop flag unrelated to plugins
- lines 2602-2604: managed setting, retry env var and VSCode note unrelated to plugins [confirmed on admin re-review]
- lines 2606-2607: VSCode diagnostics and Claude Tag DMs
- lines 2612-2627: background commands, Code Review, providers, auto mode, ultrareview and settings changes unrelated to plugins
- lines 2629-2631: /claude-api, chrome config and managed sandbox changes [confirmed on admin re-review]
- lines 2633-2633: cloud session MCP cache change
- lines 2637-2638: Chrome and Bedrock/Vertex improvements
- lines 2641-2651: artifact, Remote Control, subagent, SDK and performance improvements unrelated to plugins
- lines 2653-2653: Code Review improvement
- lines 2657-2657: fork subagent fix in -p
- lines 2659-2660: managed settings and cloud artifact fixes [confirmed on admin re-review]
- lines 2662-2674: Remote Control, model, redaction, SSH prompt, MCP CLI, sandbox and subagent fixes unrelated to plugins
- lines 2677-2679: cloud latency, auth token and workflow script fixes
- lines 2681-2697: WebFetch, transcript, Bedrock, artifact, ultrareview, auth and PowerShell fixes
- lines 2699-2700: vim mode and content filter fixes
- lines 2702-2732: compaction, ultrareview, sign-in, agents, mcp CLI, settings, VSCode UI fixes unrelated to plugins
- lines 2734-2742: VSCode, cloud, Claude Tag and Code Review fixes
- lines 2750-2759: model, auto mode, gateway, keybinding and VSCode timestamp additions unrelated to plugins
- lines 2761-2763: VSCode Ultracode and Claude Tag additions
- lines 2765-2777: Changed section of 2.1.284 has no plugin-relevant entries
- lines 2781-2787: usage, Chrome, Monitor, startup, /claude-api and list UI improvements
- lines 2789-2798: managed sign-in, memory, remote-control, artifact and Claude Tag improvements [confirmed on admin re-review]
- lines 2802-2808: stream, compaction, model, SDK, MCP resume, usage and managed mcp add fixes [confirmed on admin re-review]
- lines 2811-2813: Foundry, Desktop gateway and shell mode fixes
- lines 2816-2826: UI, vim, trust, rules symlink and managed-only allowed-tools fixes [confirmed on admin re-review]
- lines 2831-2851: SendMessage, Remote Control, usage, Explore, loop, ultrareview, sandbox, artifact, gateway and VSCode fixes
- lines 2853-2858: VSCode, cloud, Claude Tag (GitHub Enterprise) and Code Review fixes [confirmed on admin re-review]
- lines 2866-2871: gateway headers, managed model settings, OTel, prompt-audit and UI additions [confirmed on admin re-review]
- lines 2873-2876: gateway and Claude Tag additions
- lines 2880-2887: auto mode, ultrareview, model picker, system prompt, Desktop skill deny rules and list changes
- lines 2889-2891: artifact watching and self-hosted runner changes
- lines 2893-2893: cloud routine schedules
- lines 2897-2903: MCP list, tasks, list, compaction and sign-in page UI improvements
- lines 2905-2905: prompt-audit improvement
- lines 2907-2912: artifact, latency, startup and cloud improvements
- lines 2916-2925: SDK, MCP progress/connect, usage, model and caching fixes
- lines 2935-2968: screen reader, context, mcp CLI, keybinding, sandbox, vim, VSCode, cloud, Claude Tag and Code Review fixes
- lines 2974-2983: Added section of 2.1.282 has no plugin-relevant entries
- lines 2987-2993: claude-api skill, auto mode, sandbox, telemetry, managed settings and synced-skill allow rule changes [confirmed on admin re-review]
- lines 2995-2999: MCP server naming, effort visuals, mascot and Claude Tag changes
- lines 3001-3008: Improvements section of 2.1.282 has no plugin-relevant entries
- lines 3012-3027: API, thinking, model, login, managed settings, Bash rules, UI and feedback fixes unrelated to plugins [confirmed on admin re-review]
- lines 3029-3042: API, thinking, model, login, managed settings, Bash rules, UI and feedback fixes unrelated to plugins [confirmed on admin re-review]
- lines 3045-3070: skills UI, lists, artifact, vim, VSCode, cloud and Claude Tag fixes
- lines 3078-3083: gateway, attribution and MCP elicitation additions unrelated to plugins
- lines 3085-3090: insights, scrollbar, VSCode, web and Claude Tag additions
- lines 3094-3108: send now, auto mode, rm prompt, AGENTS.md, gateway, self-hosted, UI and MCP resource changes
- lines 3110-3112: tasks list, /agents menu and Claude Tag changes
- lines 3116-3127: startup, resume, auto mode, sandbox, --agents and /batch improvements
- lines 3129-3148: synced skill names, research, artifact, UI and dialog improvements unrelated to plugin development
- lines 3152-3193: crash, resume, proxy stream, tool, PDF, permission, sandbox, cloud, Remote Control and login fixes
- lines 3206-3263: permissions, model, UI, vim, agent panel, Windows, VSCode, web, Claude Tag and Code Review fixes
- lines 3269-3282: Added section of 2.1.280 has no plugin-relevant entries
- lines 3286-3292: keybinding, default model, effort, footer and self-hosted runner changes
- lines 3295-3297: VSCode and web admin changes [confirmed on admin re-review]
- lines 3301-3311: permissions, cost, artifact, install-github-app and UI improvements
- lines 3313-3321: file suggestions, artifact, ultrareview, VSCode, web, Claude Tag and Code Review improvements
- lines 3325-3338: write symlink, auto mode, Write validation, dialog, dictation and caching fixes
- lines 3340-3360: user skills trash, UI, API, resume, settings and subagent fixes unrelated to plugins
- lines 3362-3382: background shells, agents, MCP, private-repo marketplace credentials, official marketplace snapshot, artifact, cloud, Windows and VSCode fixes
- lines 3383-3401: VSCode/web/Claude Tag fixes and 2.1.278 auto-mode billing entries; nothing a plugin maintainer or marketplace user acts on
- lines 3406-3431: 2.1.277 Added/Changed entries (AGENTS.md, gateway, VSCode, web, Tag, tool changes) unrelated to building or installing plugins
- lines 3434-3435: headless startup and gateway messages; unrelated to plugins
- lines 3438-3443: general UI, prompt, ultrareview, artifact and rm-prompt improvements; unrelated to plugins
- lines 3447-3452: general crash/login/update fixes unrelated to plugins
- lines 3454-3458: core tool fixes unrelated to plugins
- lines 3460-3472: general crash, rendering, sandbox, Cowork and gateway fixes unrelated to plugins
- lines 3474-3474: auto-update staging cleanup; unrelated to plugins
- lines 3480-3503: archive reload previews and general CLI/VSCode/web/Tag fixes; not part of public GitHub marketplace workflow
- lines 3505-3510: 2.1.276 gateway/proxy regression only
- lines 3517-3520: gateway sign-in, send-now key, OTel warning, claude.ai account sync; not public marketplace related
- lines 3522-3529: VSCode, web and Claude Tag additions unrelated to plugins
- lines 3533-3536: gateway logout, hosted sessions, artifact icon, Chrome auto mode; unrelated to plugins
- lines 3538-3541: routines, startup notice and VSCode changes unrelated to plugins
- lines 3543-3558: 2.1.275 improvements; none concern plugins or the marketplace (ListPlugins is claude.ai account plugins)
- lines 3561-3564: memory cache, stream-json, @-mention and fullscreen fixes unrelated to plugins
- lines 3566-3570: credential-in-URL masking (private-source concern) and general UI fixes
- lines 3572-3584: general gateway, sandbox, resume, crash fixes unrelated to plugins
- lines 3586-3586: self-hosted runner drain fix
- lines 3588-3594: sandbox, artifact, update-config, claude-api skill, VSCode fixes unrelated to plugins
- lines 3596-3620: VSCode, web, Tag and Code Review fixes; credential masking for private marketplace URLs
- lines 3626-3641: 2.1.274 Added: memory warning, MCP wait, OTel, gateway, VSCode, web, Tag; unrelated to plugins
- lines 3644-3645: provider MCP client defaults and /code-review prompts; unrelated to plugins
- lines 3647-3647: artifact watching change
- lines 3649-3654: self-hosted runners, status wording, VSCode, routines, Tag changes
- lines 3656-3671: 2.1.274 improvements unrelated to plugins (gateway, artifacts, OTel, Code Review)
- lines 3674-3698: general MCP, goal, agents, AskUserQuestion, artifact and session fixes not specific to plugins
- lines 3700-3706: MCP config, Stop hooks, Wayland, gateway, admin remote-managed plugin policy, headless fixes; not public marketplace workflow
- lines 3709-3744: MCP secret masking, permissions, zip-archive plugins, VSCode, web, Tag, Code Review fixes
- lines 3746-3831: 2.1.273 and 2.1.272 entries: gateway headers, auto mode, OTel, artifacts, admin MCP settings, web, Tag, Code Review; none concern public marketplace plugins
- lines 3838-3841: fast mode, /config mouse, self-hosted runner, sandbox domains; unrelated to plugins
- lines 3844-3847: chargeback pricing, provider tips, VSCode and web additions
- lines 3852-3859: subagent hand-back, Monitor deadlines, IDE pill, workflows, gateway, claude-api skill, VSCode, routines changes
- lines 3861-3881: 2.1.271 improvements unrelated to plugins
- lines 3884-3885: organization policy caching fixes
- lines 3887-3942: proxy, cloud, fast mode, permissions, MCP, resume, artifacts, runner, synced skills, UI, VSCode, Tag, Code Review fixes; not plugin-specific
- lines 3944-3949: 2.1.270 git permission regression only
- lines 3957-3969: output-style, bash diff, OTel, gateway, workflow, VSCode, web, Tag additions
- lines 3971-3980: 2.1.269 Changed: ultrareview, artifacts, claude.ai synced skills, VSCode, web; unrelated to public marketplace
- lines 3983-3984: /diff and prompt suggestion improvements
- lines 3986-3993: keyboard, responsiveness, VSCode and Tag improvements
- lines 3997-4009: cache, terminal, permission, synced plugin MCP, image, managed telemetry fixes; not public marketplace workflow
- lines 4011-4013: redacted URL display and /fork fix
- lines 4015-4062: attribution, terminal, SDK, goal, managed org plugins, archive extraction, VSCode, web, Tag fixes; not public marketplace workflow
- lines 4070-4074: gateway pricing/CIDR/networks, self-hosted runner, auth status additions
- lines 4076-4080: artifact icons, VSCode, Tag, Code Review additions
- lines 4084-4090: provider system prompt, todo tools, artifact, Cowork, WebFetch, MCP notice changes
- lines 4092-4093: VSCode artifact prompt and Tag memory changes
- lines 4097-4106: rendering, resume, startup, auto mode, Chrome, memory, footer, usage improvements
- lines 4108-4112: routine and Claude Tag improvements
- lines 4116-4142: endpoint, WebFetch, permissions, secret masking for git source URLs, model access, compaction, agents, Chrome, UI fixes; not plugin-specific
- lines 4145-4174: WebFetch, generic hook timing, policy, cloud commands, sandbox, VSCode, web, Tag, Code Review fixes
- lines 4180-4200: 2.1.267 Added/Changed/improvements: effort caps, system prompt snapshot, runner, gateway, UI; unrelated to plugins
- lines 4203-4207: Cowork, mobile, tmux, fullscreen, workflow fixes
- lines 4209-4214: cloud credentials, resume, managed hook URL allowlists, gateway login, artifact fixes
- lines 4216-4243: artifact, agents, remote control, prompt cache, VSCode, web, Tag fixes
- lines 4245-4250: 2.1.266 gateway env var regression only
- lines 4257-4257: gateway telemetry attributes
- lines 4259-4260: tool result cap and VSCode archiving
- lines 4264-4266: .claude permission wording, gateway login, image processing
- lines 4268-4268: gateway OpenTelemetry export
- lines 4272-4273: worktree and /workflows improvements
- lines 4275-4278: MCP OAuth, resume, image error, artifact read improvements
- lines 4282-4287: prompt cache, resume, model alias, highlighting, fullscreen fixes
- lines 4290-4298: login, remote control, bg sessions, git probes, advisor, artifact, admin skill locks, shortcuts, forked skill streaming
- lines 4300-4300: gateway telemetry relay fix
- lines 4302-4315: gateway login, model, remote control, config, workflow, claude-api skill, MCP SSE, connectors, Windows, VSCode fixes
- lines 4317-4322: 2.1.263 generic bug fixes line only
- lines 4329-4331: org policy status, output caps, subagent prompt file
- lines 4333-4337: VSCode additions
- lines 4339-4355: 2.1.261 Changed and improvements: gateway, auto mode, keys, context, model picker, Vertex, rm prompt, timeouts
- lines 4358-4382: input, Bedrock, synced plugins under managed settings, Remote Control, gcp, connectors, gateway, Chrome fixes
- lines 4384-4398: agent-team cache and VSCode fixes
- lines 4400-4404: VSCode usage, session list and Remote Control fixes
- lines 4412-4413: diff panel and prompt-cache cause additions
- lines 4415-4419: advisor, gateway OIDC/desktop policy keys (admin deployment), VSCode additions
- lines 4421-4446: 2.1.260 Changed and improvements: permissions, claude-api skill, managed CLAUDE.md, Chrome, gateway org plugin settings, sandbox, runner, compaction
- lines 4449-4459: permission rules, Bedrock certs, managed settings, skillOverrides, Fable model fixes
- lines 4461-4486: org-managed plugin marketplace, SDK MCP, Chrome, rendering, rewind, agents, URL-hosted marketplace, artifact, GitLab, VSCode fixes; not public GitHub marketplace workflow
- lines 4494-4496: managed MCP servers, permission prompts none, GitLab MR recognition
- lines 4498-4498: VSCode session filter
- lines 4500-4511: allowedMcpServers change and 2.1.259 improvements unrelated to plugins
- lines 4514-4518: concurrency, thinking, Bash Read() deny, prompt cache, fullscreen fixes
- lines 4520-4523: Vertex context tokens, shell preview, GitHub check, resume fixes
- lines 4525-4532: artifact, managed refresh, worktree, OTel, MCP, edit dialog, repo detection, managed parse fixes; not plugin-specific
- lines 4533-4534: remote-control/workflow session fixes unrelated to plugin marketplace
- lines 4537-4547: remote session/worktree fixes and 2.1.258 launch/remote fixes; no plugin relevance
- lines 4554-4556: model, time format and auto-mode additions unrelated to plugins
- lines 4558-4597: UI/effort/gateway/managed admin additions, changes and improvements that do not affect plugin publishing or install
- lines 4600-4621: general session, provider, sandbox and UI fixes
- lines 4624-4635: general session, background and permission fixes
- lines 4637-4676: non-plugin fixes and 2.1.252 entries with no plugin relevance
- lines 4684-4688: remote control, usage, cost and help additions
- lines 4691-4692: provider/Chrome changes
- lines 4694-4719: commit trailer, telemetry, sandbox, managed-settings changes and performance improvements
- lines 4722-4722: file tool symlink fix, not plugin-specific
- lines 4724-4742: tracing, permission, model and session fixes
- lines 4744-4769: remote/session/provider fixes and 2.1.250 generic entry
- lines 4776-4776: restricted mode flag for operators, not plugin distribution
- lines 4778-4799: self-hosted runner, admin diagnostics, cross-session and UI changes
- lines 4802-4814: prompt cache, login, agents view fixes
- lines 4817-4817: project .mcp.json connector display fix, not plugin
- lines 4819-4834: gateway, UI, cloud session and remote-control fixes
- lines 4839-4856: feedback, org tips, claude-api skill, compaction and gateway/admin changes
- lines 4860-4860: provider MCP failure notice, not plugin-specific
- lines 4864-4876: keyboard, UI, background session fixes
- lines 4878-4883: remote/self-hosted/cloud session fixes
- lines 4888-4900: permission UI, code-review, goal, install consent and claude.ai-synced plugin telemetry (org distribution)
- lines 4903-4904: /cd and bash latency improvements
- lines 4906-4908: non-interactive retry and telemetry attribution
- lines 4911-4924: rendering, background session and MCP/auto-mode fixes not plugin-specific
- lines 4931-4943: theme, keybinding, UI and tool fixes
- lines 4945-4947: resume, install script and plan mode fixes
- lines 4949-4966: permission, MCP, telemetry, cloud fixes and 2.1.245 crash fix
- lines 4971-5006: usage, model picker, pricing, login, sandbox and performance changes
- lines 5009-5023: MCP reconnection, auto mode, resume and auth fixes not plugin-specific
- lines 5027-5054: agents flag, UI, proxy, remote-control fixes and generic 2.1.241/2.1.240 entries
- lines 5059-5088: fullscreen, claude-api, cost, claude.ai-synced plugins (org distribution), remote and messaging changes
- lines 5091-5106: provider, IDE, resume and theme fixes
- lines 5108-5108: /insights fix
- lines 5110-5120: UI, OTel, keybinding and sandbox fixes
- lines 5122-5129: rules, remote-control and input fixes
- lines 5134-5139: keybinding and self-hosted runner additions
- lines 5142-5149: url/catalog marketplace headersHelper (credentialed non-GitHub hosts), cross-session, claude-api, UI and project .mcp.json changes
- lines 5151-5158: startup and remote-control improvements
- lines 5161-5161: memory fix
- lines 5163-5275: remaining 2.1.238 fixes and 2.1.237, 2.1.236, 2.1.235 entries: UI, model, remote, sandbox, auto mode; no plugin relevance
- lines 5280-5315: 2.1.234 additions, changes and improvements unrelated to plugins
- lines 5318-5324: auto mode, API, git remote and MCP diagnostics fixes
- lines 5326-5342: UI, permission prompt, remote-control and messaging fixes
- lines 5347-5367: GitLab, gateway, Bash, todo tools, runner and validate for bare .claude/skills (not plugins)
- lines 5370-5371: cloud session and MCP v2 stream fixes
- lines 5373-5374: sandbox CPU and bundled skill alias fixes
- lines 5376-5378: Windows path and auto mode fixes
- lines 5383-5388: config rows, GitLab redaction and GitLab marketplaces (non-GitHub host)
- lines 5391-5394: subagent fork and session messaging/naming changes
- lines 5397-5401: gateway, advisor, remote-control and feedback changes
- lines 5403-5421: code-review, remote-control, sandbox, cowork changes and UI/managed-settings improvements
- lines 5424-5438: permission, MCP connect, remote-control, provider and UI fixes
- lines 5440-5449: update/usage/advisor fixes and 2.1.231 MCP OAuth fix
- lines 5454-5476: self-hosted runner hooks, gateway, local command marketplace sources (not GitHub), VSCode and other changes
- lines 5479-5488: rendering, crash, auth, MCP OAuth, remote and IDE fixes
- lines 5490-5497: workflow, watcher, SDK, OTel and self-hosted runner fixes
- lines 5502-5514: claude.ai-synced skills (org distribution), UI, Write tool and provider changes
- lines 5517-5524: rendering, git, tui, messaging, runner and memory folder fixes
- lines 5526-5574: marketplace custom headers merge (credentialed hosts), deferred tools fix, and 2.1.227/2.1.226/2.1.225 entries without plugin relevance
- lines 5579-5603: self-hosted environments, archive plugin source (archive distribution), sandbox, messaging, feedback and remote-control changes
- lines 5606-5610: project path, messaging, sandbox and MCP tool search fixes
- lines 5612-5621: paste, clipboard, feedback and remote-control fixes
- lines 5629-5653: subagent model warning, teleport hint, context/code-review changes and permission/workflow/session fixes
- lines 5658-5662: remote-control auto-start and ultraplan removal
- lines 5665-5665: auto mode SendMessage classification
- lines 5667-5668: diff view improvement
- lines 5671-5671: worktree isolation fix
- lines 5673-5687: usage, proxy, model, connector and UI fixes
- lines 5694-5695: VSCode focus view and sandbox mask additions
- lines 5697-5698: claude-api skill subcommand
- lines 5701-5702: auto mode cache and background session git behavior
- lines 5706-5722: status, emoji, fork, Chrome, fast mode, gateway changes and provider/auto-mode improvements
- lines 5725-5737: permission, MCP config, SDK, sandbox, provider and session-name fixes
- lines 5739-5748: notification and vim fixes and generic 2.1.220 entry
- lines 5755-5756: model and sandbox allowlist additions
- lines 5758-5788: stream-json, workflow, MCP list, model and UI changes and fixes
- lines 5795-5796: screen reader and fast-mode announcements
- lines 5801-5804: code-review, deep-research, plan mode and server-managed settings changes
- lines 5807-5840: auto mode, sandbox, trust improvements and general fixes; agent frontmatter hooks do not apply to plugin agents
- lines 5845-5860: emoji, transcript warnings, subagent caps, login and PR badge changes
- lines 5863-5872: memory, update, isolation, provider, OTel and remote-control fixes
- lines 5874-5876: transcript layout and budget fixes
- lines 5881-5899: sandbox, context, rewind, bundled skill and review/fork improvements
- lines 5902-5906: performance, auto mode, AskUserQuestion and web session fixes
- lines 5907-5926: fixes for background sessions, worktrees, permissions, terminal UI, telemetry; nothing a plugin maintainer or installer acts on
- lines 5929-5931: telemetry, VS Code text rendering, cloud sessions; unrelated to plugins
- lines 5933-5938: 2.1.215: bundled /verify and /code-review skills behavior only
- lines 5945-5949: EndConversation tool, heartbeat, memory frontmatter, OTel; not plugin-related
- lines 5951-5951: docker permission prompts; not plugin-related
- lines 5956-5957: file command permissions and connection pooling; not plugin-related
- lines 5960-5963: claude rc trust message; not plugin-related
- lines 5966-5990: permission, PowerShell, daemon, background session and scheduled task fixes; not plugin-related
- lines 5992-5997: feature flags, ultrareview, doctor, memory, telemetry, advisor; not plugin-related
- lines 5999-6000: OTel and MCP refresh internals; not actionable for plugin maintainer
- lines 6006-6034: 2.1.212 Added/Changed/Improved: session caps, /fork, agent view, auth, caching; not plugin-related
- lines 6037-6038: plan mode and worktree symlink fixes; not plugin-related
- lines 6040-6059: SIGTERM, background, ultrareview, UI, worktree fixes; not plugin-related
- lines 6061-6064: OTel, image, web search fixes; not plugin-related
- lines 6070-6091: 2.1.211 Added/Changed/Improved: stream-json flag, env var parsing, Chrome, UI; not plugin-related
- lines 6094-6094: chat channel permission preview sanitizing; not plugin-related
- lines 6096-6096: credential store logout; not plugin-related
- lines 6098-6117: model, subagent, rules, Chrome, UI and background fixes; not plugin-related
- lines 6123-6142: 2.1.210 Added/Changed/Improved: UI, memory, auto mode, bundled dataviz skill; not plugin-related
- lines 6145-6150: worktree subagents, ultracode, telemetry, paste, attach, renderer crash; not plugin-related
- lines 6152-6152: background cd handling; not plugin-related
- lines 6154-6156: plan approvals, doctor auto mode, Grep pagination; not plugin-related
- lines 6159-6166: background workers, agents view, SDK MCP, sandbox symlinks; not plugin-related
- lines 6168-6173: 2.1.209: agents dialogs fix only
- lines 6178-6204: 2.1.208 Added/Changed/Improved: screen reader, vim, wrapper, CPU/memory, background sessions; not plugin-related
- lines 6207-6223: fast mode, background, streaming, env vars, tools, auth, stream-json fixes; not plugin-related
- lines 6225-6234: usage, SDK hosts, workflows, memory leaks, permissions, Bedrock; not plugin-related
- lines 6242-6244: auto mode availability and provider default models; not plugin-related
- lines 6248-6252: agent view improvements; not plugin-related
- lines 6255-6261: terminal, managed settings consent, updater, permissions, worktree config fixes; not plugin-related
- lines 6263-6271: agent teams, background, Remote Control, Bedrock, usage-credits fixes; not plugin-related
- lines 6277-6294: 2.1.206 Added/Changed/Improved: /cd, doctor, commit-push-pr, gateway, worktrees, agents view; not plugin-related
- lines 6297-6298: login and resume fixes; not plugin-related
- lines 6300-6310: background env, OAuth MCP, model picker, desktop, agents fixes; not plugin-related
- lines 6312-6314: doctor Homebrew, fullscreen pill, Bedrock; not plugin-related
- lines 6320-6336: 2.1.205 Added/Changed/Improved: auto mode, updater, doctor, reserved MCP names, agent view; not plugin-related
- lines 6339-6346: json-schema, max-turns, worktree, background, attach, PR linking, mcp add-from-claude-desktop; not plugin-related
- lines 6348-6353: crash, file watcher, verify skills, agent view, Remote Control, Cowork; not plugin-related
- lines 6355-6360: 2.1.204: headless hook event streaming for remote workers; not actionable for plugin maintainer
- lines 6365-6384: 2.1.203 Added/Changed/Improved: login warning, badges, MCP roots, binary size, agents view; not plugin-related
- lines 6387-6411: background agent, worktree, terminal fixes; not plugin-related
- lines 6418-6426: workflow size setting, OTel attributes, /review change; not plugin-related
- lines 6429-6429: /workflows layout; not plugin-related
- lines 6434-6445: history search, rename, mTLS, Remote Control, sign-in URL, workflows, voice, resume, installer fixes; not plugin-related
- lines 6448-6453: 2.1.201: Sonnet 5 system role; not plugin-related
- lines 6458-6467: AskUserQuestion, permission mode rename, screen reader, install script; not plugin-related
- lines 6470-6477: config crash, background session/daemon, subagent rate-limit fixes; not plugin-related
- lines 6480-6483: /mcp accessibility, voice, tmux flicker; not plugin-related
- lines 6491-6493: retry behavior and agents PR links; not plugin-related
- lines 6497-6508: SSL, streaming, subagent errors, background daemon, model picker fixes; not plugin-related
- lines 6510-6517: daemon subcommand, SendMessage, transcript, color, config reset, Chrome, plan mode; not plugin-related
- lines 6525-6566: bundled dataviz skill, gateway, subagent defaults, Chrome GA, /agents wizard removal, UI and background fixes; not plugin-related
- lines 6567-6572: 2.1.197: Sonnet 5 announcement; not plugin-related
- lines 6577-6596: 2.1.196 Added/Changed/Improved: org default models, project .mcp.json approval, watchdog, Remote Control, background reliability, code-review; not plugin-related
- lines 6599-6606: background job, rate-limit, PowerShell, agents panel, Remote sessions, /cd fixes; not plugin-related
- lines 6608-6611: rewind, MCP OAuth scopes on self-hosted IdPs, Bedrock context, deep-research; not plugin-related
- lines 6613-6615: agents status and voice dictation fixes; not plugin-related
- lines 6620-6629: mouse clicks, voice mode, agents list, Remote startup; not plugin-related
- lines 6633-6634: voice dictation fixes; not plugin-related
- lines 6637-6640: background job and daemon fixes; not plugin-related
- lines 6645-6653: auto-mode settings, OTel response logging, bash autocomplete, MCP auth notice, shell reaping; not plugin-related
- lines 6656-6656: background agent launch wording; not plugin-related
- lines 6659-6668: /add-dir message and UI/background fixes; not plugin-related
- lines 6673-6689: 2.1.191 Added/Changed/improvements: rewind, CPU, sandbox, MCP retries and OAuth, vim; not plugin-related
- lines 6692-6698: scroll, background agents, voice, login URL, Cmd+click, agents fixes; not plugin-related
- lines 6700-6704: permissions tab, agent panel, splash, managed settings refresh; not plugin-related
- lines 6705-6710: 2.1.190: generic bug fixes
- lines 6711-6744: 2.1.187: sandbox credentials, org model restrictions, install-github-app, /btw, /plugin unused-plugins hint, resume, structured output, remote MCP idle timeout and UI fixes; nothing the maintainer or installer acts on
- lines 6749-6763: mcp login CLI, workflows filter, /plugin Skills section, teammateMode, AWS login, bash respond, retries, subagent prompts, /review; not plugin-related
- lines 6766-6767: mcp get/remove suggestions and MEMORY.md reminder; not plugin-related
- lines 6770-6793: 2.1.186 bug fixes: streaming, transcripts, Chrome, agent rules, /plugin scroll indicator, workflows; not plugin-related
- lines 6794-6799: 2.1.185: stream-stall hint wording
- lines 6807-6818: attribution setting, /config, startup line, auto mode git safety; not plugin-related
- lines 6821-6825: thinking 400s, WebSearch, vim cursor, Windows TUI, thinking-only turns; not plugin-related
- lines 6827-6832: headless MCP auth stubs, tmux teammates, scheduled task, focus mode; not plugin-related
- lines 6833-6887: 2.1.181: /config syntax, sandbox Apple Events, Bun upgrade, streaming, startup and UI fixes; nothing plugin-related
- lines 6888-6901: 2.1.179: connection drops, scrolling, sandbox globs, UI fixes and generic remote plugin loading performance; not actionable
- lines 6906-6924: permission rule syntax, agent teams, nested .claude dirs, workflows, /bug, auto mode, doctor, Remote Control; not plugin-related
- lines 6927-6935: OOM, Chrome, nested skills, subagent, gateway, compaction, auth, background, sandbox symlink fixes; not plugin-related
- lines 6938-6941: vim undo, statusline links in agents, VS Code IME; not plugin-related
- lines 6946-6958: footer links setting, session titles, background guidance, Bedrock caching; not plugin-related
- lines 6961-6962: availableModels enforcement and auto mode on Fable; not plugin-related
- lines 6964-6979: sandbox, clipboard, Remote Control, /cd, agents, background, cloud session fixes; not plugin-related
- lines 6980-6985: 2.1.175: admin model allowlist setting; administrator operation only
- lines 6986-7008: 2.1.174: scroll setting, VS Code usage, model picker, Bedrock, background env, skill hot-reload internals; not actionable
- lines 7009-7015: 2.1.173: model name and sandbox warning fixes
- lines 7016-7061: 2.1.172: /plugin search bar, OTEL, nested subagents, Bedrock region, UI, model picker, permissions and memory fixes; not actionable for the scenario
- lines 7062-7068: 2.1.170: Fable 5 announcement and transcript fix
- lines 7076-7097: /cd, bundled skills setting, tips, workflows, CPU, Vertex timeout, remote settings, background, CLAUDE.md warning, updater, promos; not plugin-related
- lines 7100-7110: arrow keys, managed MCP policies, UI stalls, Remote Control, Git Credential Manager, agents fixes; not plugin-related
- lines 7113-7114: OTEL client-cert trust; not plugin-related
- lines 7115-7126: 2.1.168 and 2.1.167: generic bug fixes
- lines 7127-7160: 2.1.166: fallback models, deny-rule globs, cross-session messaging, thinking, terminal and background fixes; not plugin-related
- lines 7161-7166: 2.1.165: generic bug fixes
- lines 7173-7173: admin version range managed setting; administrator operation
- lines 7175-7175: /btw copy shortcut; not plugin-related
- lines 7182-7185: background updates, menu descriptions, subscription toast, agents dispatch dir; not plugin-related
- lines 7189-7197: claude -p, TMPDIR, Windows, managed permission, background, desktop, paste fixes; not plugin-related
- lines 7199-7201: deny rules on $HOME paths and stray transcript line; not plugin-related
- lines 7206-7224: 2.1.162 Changed/Improved: agents json, --tools, effort, autocomplete, Remote Control, startup notices; not plugin-related
- lines 7227-7231: config dir, WebFetch rules, Windows permission rules, stream-json interrupt, surrogate errors; not plugin-related
- lines 7234-7242: claude agents UI and SendMessage fixes; not plugin-related
- lines 7247-7263: 2.1.161 Added/Changed/Improved: VS Code tip, OTEL, agents rows, connectors, parallel tools, clipboard, rendering; not plugin-related
- lines 7266-7271: reduce motion, managed login policies, -p output, usage-credits, autofix-pr, resume picker; not plugin-related
- lines 7273-7280: OTel, mcp CLI redaction, workflow worktrees, background model, crash, subagents, EADDRINUSE; not plugin-related
- lines 7281-7323: 2.1.160: shell startup prompts, acceptEdits, env var removal, ultracode, background and UI fixes; nothing plugin-related
- lines 7324-7335: 2.1.159 internal and 2.1.158 auto mode on providers; not plugin-related
- lines 7343-7344: /plugin autocomplete and workflow keyword setting; not actionable
- lines 7349-7384: agents setting, worktrees, telemetry, terminal setup, startup banners, workflows, UI and background fixes; not plugin-related
- lines 7385-7390: 2.1.156: Opus 4.8 thinking fix
- lines 7395-7399: dynamic workflows and /claude-api skill update; not plugin-related
- lines 7402-7411: Opus 4.8 defaults, fast mode, system prompt, simplify, effort labels, agents, Chrome; not plugin-related
- lines 7414-7414: streaming tool execution flag; not plugin-related
- lines 7416-7450: project .mcp.json approval display, Remote Control, fast mode deprecation, VS Code auto mode, classifier, and 2.1.154 bug fixes; not plugin-related
- lines 7458-7499: npm notice, status line env, agents, doctor, macOS privacy, strict-mcp-config agents, /bg, /model, keybinding, and 2.1.153 bug fixes; not plugin-related
- lines 7508-7509: org-only marketplace suggestion allowlist and OTel entrypoint; administrator/org distribution only
- lines 7513-7513: /code-review --fix behavior; not plugin-related
- lines 7518-7525: fallback model, auto mode, vim, usage, thinking display, workflow UI; not plugin-related
- lines 7529-7534: terminal styling, sandbox warning, spinner, focus mode, links, markdown tables; not plugin-related
- lines 7538-7545: remote egress MCP, effort dialog, --bare agent list, agents crash, cache tokens, push notification, thinking signatures; not plugin-related
- lines 7546-7551: 2.1.150: internal infrastructure
- lines 7556-7569: enterprise claude.ai MCP setting, /usage, /diff, markdown checkboxes, /feedback; not plugin-related
- lines 7572-7582: PowerShell, sandbox, permission analysis, find, managed dialog, ultraplan, otelHeadersHelper, UI fixes; not plugin-related
- lines 7585-7593: transcript view, history, /config, /insights, PowerShell classification, Remote Control rename, UI fixes; not plugin-related
- lines 7594-7599: 2.1.148: Bash exit code regression fix
- lines 7606-7606: pinned background sessions; not plugin-related
- lines 7607-7613: Non-plugin CLI changes (/code-review, prompt history, auto-updater, diff rendering)
- lines 7617-7621: Login, shell output, /help, shell snapshot fixes unrelated to plugins
- lines 7624-7627: PowerShell tool and /effort fixes unrelated to plugins
- lines 7629-7631: Terminal/background session fixes
- lines 7633-7637: UI, SDK, Windows rendering and paste fixes
- lines 7639-7644: Background sessions, paste, subagent model env, menu spacing, images; not plugin-relevant
- lines 7650-7654: claude agents JSON and OTEL span attributes
- lines 7657-7657: Status line JSON content
- lines 7659-7660: claude agents tab title and suggestion list mouse support
- lines 7663-7666: Read tool truncation behavior
- lines 7669-7678: Permissions, MCP prompt errors, UI, Windows, voice, official marketplace banner, teams, /review fixes
- lines 7686-7690: Background session /resume and notification durations
- lines 7694-7703: Model, usage credits, rendering, search, background session changes
- lines 7705-7705: Cosmetic /plugin navigation
- lines 7708-7713: Survey hint and stream/SDK MCP startup improvements
- lines 7717-7726: Startup, terminal, background, model picker, login fixes
- lines 7730-7730: Session title from monitor output; nothing to act on
- lines 7733-7746: Project .mcp.json listing, side-queries, background session and agent view fixes
- lines 7756-7756: Worktree background isolation setting
- lines 7758-7772: PowerShell, background sessions and claude agents flag changes
- lines 7775-7776: Credentials and paste fixes
- lines 7778-7782: /loop, /goal, color env, agent view, /bg fixes
- lines 7784-7792: Agent view, background sessions, error message fixes
- lines 7798-7801: claude agents flags for background sessions
- lines 7804-7804: Fast mode model change
- lines 7807-7808: /web-setup and refusal message changes
- lines 7812-7812: Compaction improvement
- lines 7817-7828: MCP timeout env, background sessions, daemon, claude agents, titles, remote clients
- lines 7842-7844: Workload identity, claude agents cwd, rewind menu
- lines 7846-7863: Feedback, auto mode, IDE diff, background agents, Bedrock, voice, spinner, plugin menu key navigation
- lines 7866-7873: Provider side-queries, daemon, claude agents, model, permission prompt fixes
- lines 7875-7896: Rendering, history, keybindings, UI, provider, analytics fixes
- lines 7901-7909: MCP auth display, Remote Control, OTel, keybindings, paste, SDK binary, VSCode fixes
- lines 7917-7917: Agent color palette
- lines 7923-7935: /goal, settings hot-reload, background service, managed settings, /loop, Windows, Read tool, cursor fixes
- lines 7943-7945: Agent view, /goal, /scroll-speed
- lines 7947-7947: Transcript view navigation
- lines 7954-7955: Compaction prompt and /mcp reconnect of project .mcp.json
- lines 7960-7963: Remote MCP retry, OTEL headers, API key feature gating, VSCode shortcut
- lines 7967-7968: Auth deadlock and sandbox auto-approve fixes
- lines 7970-7970: MCP memory cap fix
- lines 7972-7972: User settings symlink hot-reload
- lines 7974-7990: Model picker, timeouts, UI, rendering, Grep fixes
- lines 7992-7993: ProgressBar and task polling fixes
- lines 7995-7997: Insights chart, keybindings, OTel metric fixes
- lines 8000-8011: 2.1.138 internal fixes and 2.1.137 VSCode Windows fix; no plugin entries
- lines 8016-8030: Feedback survey env, auto mode rules, WSL paste, marketplace removal key, dialog consistency, worktree error
- lines 8034-8038: Login, OAuth, thinking, resume, plan mode fixes
- lines 8040-8050: Rendering, worktree, file picker, UI, insights fixes
- lines 8052-8053: IDE lock files and copy whitespace
- lines 8055-8055: Truncation marker fix
- lines 8057-8061: /branch, wrapping, dialogs, /doctor MCP schema, Bash prompt fixes
- lines 8063-8077: AskUserQuestion, /clear, CronList, rendering, paste, UI fixes
- lines 8084-8089: Worktree baseRef, sandbox binaries, admin SDK settings merge
- lines 8093-8098: --help listing, focus mode, memory improvements
- lines 8102-8109: Credentials, permissions, locks, compaction, proxy, network drive, Remote Control, effort fixes
- lines 8111-8111: VSCode process wrapper fix
- lines 8113-8163: 2.1.132 and 2.1.131: env vars, UI, terminal, MCP connection display, provider fixes; no plugin entries
- lines 8168-8173: --plugin-url archive loading (archive distribution), sync output and package manager auto-update env vars
- lines 8177-8179: Gateway model discovery, history picker, third-party tips
- lines 8181-8202: OTel metric, policy refusal IDs and 2.1.129 bug fixes unrelated to plugins
- lines 8210-8212: /color, /mcp tool count, --plugin-dir zip archives (not needed for GitHub marketplace)
- lines 8214-8215: Model picker and OTEL env inheritance
- lines 8217-8220: MCP reconnect summary, SDK localSettings, EnterWorktree, auto mode hint
- lines 8225-8230: Focus mode, notifications, Remote Control, paste, piping, URL fixes
- lines 8232-8244: MCP images, copy, config, links, context, shell, effort, provider, vim, rename fixes
- lines 8246-8249: SHELL_PREFIX MCP args, subagent cache, npm-sourced plugin updates (non-GitHub source), subagent summaries
- lines 8255-8270: Gateway models, project purge, permissions, auth, OTel, Windows PowerShell changes
- lines 8273-8285: Security sandbox managed domains, images, OAuth, streams, scrolling, connectors, rendering fixes
- lines 8287-8291: Plan-mode with channels, /plugin uninstall label, Remote Control, SDK fixes
- lines 8293-8329: 2.1.123 and 2.1.122: OAuth, Bedrock, OTel, /resume, /mcp, provider and UI fixes; no plugin entries
- lines 8338-8339: /skills filter box and OTel span attributes
- lines 8344-8380: Fullscreen, dialogs, permissions, terminal, MCP retry, connectors, Vertex, SDK, VSCode changes and 2.1.121 bug fixes
- lines 8386-8389: claude ultrareview subcommand
- lines 8392-8392: Windows shell tool fallback
- lines 8394-8398: AI_AGENT env, spinner tips, scroll hint, connector startup, auto mode link
- lines 8400-8402: Auto-compact display and VSCode changes
- lines 8406-8413: MCP Esc, rewind, scrollback, telemetry, auto mode, UI fixes
- lines 8415-8415: Bash find descriptor fix
- lines 8421-8425: PR badge URL and hide cwd env var
- lines 8428-8429: /config persistence and --from-pr hosts
- lines 8431-8432: Built-in agent permissionMode and PowerShell auto-approve
- lines 8434-8434: Subagent/SDK MCP parallel connect
- lines 8436-8439: Vim, slash picker, shorthand links
- lines 8441-8444: OTel, status line, Vertex tool search, Windows MCP warning
- lines 8448-8454: Paste, Glob/Grep, scrolling, MCP OAuth, rewind, auto mode fixes
- lines 8456-8458: Spinner, file completion, Terminal.app fixes
- lines 8460-8462: MCP client secret, /skills Enter, /agents labels
- lines 8464-8466: /export, verbose, /usage fixes
- lines 8468-8469: List wrapping and /plan fixes
- lines 8472-8479: Worktree isolation, /status, TaskList, rate limit hints, SDK, PR linking, /doctor MCP scope, VSCode
- lines 8487-8489: Vim visual mode, DISABLE_UPDATES, auto mode prompt
- lines 8494-8494: /cost and /stats merge
- lines 8497-8501: WSL managed settings, auto mode rules, resume, /color, model picker
- lines 8506-8516: MCP OAuth, credentials, login, UI, plan dialog fixes
- lines 8519-8522: /fork, keyboard, remote model setting, typeahead fixes
- lines 8524-8526: File watcher, Remote Control, SendMessage cwd fixes
- lines 8534-8537: Forked subagents, --agent mcpServers, /resume, MCP startup
- lines 8541-8546: Advisor tool, cleanup, OTel, embedded search tools, Windows, default effort
- lines 8548-8551: /model persistence improvement
- lines 8554-8565: OAuth, WebFetch, proxy, undo, Bedrock, MCP elicitation, re-render fixes
- lines 8567-8567: Opus 4.7 context window fix
- lines 8575-8580: /resume, MCP startup, scrolling, spinner, /config, /doctor changes
- lines 8582-8602: gh rate limit, usage tab, --agent hooks, security, download URL and 2.1.116 bug fixes unrelated to plugins
- lines 8604-8609: 2.1.114 teammate permission dialog fix
- lines 8614-8638: Sandbox domains, native binary, input keys, Remote Control, Bash security, /loop, /ultrareview
- lines 8641-8656: MCP timeout, input, tables, subagent, sandbox, UI, effort, ToolSearch, compaction fixes
- lines 8658-8669: Ultraplan, SDK images, Remote Control, Bedrock fixes and 2.1.112 auto mode fix
- lines 8674-8681: Effort level, theme, permission skill, /ultrareview, OTel bodies
- lines 8684-8696: Opus/auto mode, effort slider, PowerShell, permissions, typo hints, plan names, input keys
- lines 8698-8699: Error suppression and retry revert
- lines 8701-8701: Windows permission rule paths
- lines 8705-8705: Vertex/Bedrock setup wizard improvements
- lines 8707-8719: 2.1.111 bug fixes unrelated to plugins
- lines 8725-8747: /tui, push notifications, autoscroll, editor, transcript, Remote Control, Bash, SDK tracing, recap, /plugin tab and /doctor MCP scope
- lines 8750-8753: MCP hang, retries, focus mode, CPU fixes
- lines 8756-8760: Resume, queue, cleanup, keystroke, rendering fixes
- lines 8763-8768: Stdio MCP stray output, headless title, memory, /skills scroll, Remote Control fixes
- lines 8770-8821: 2.1.109, 2.1.108 and 2.1.107: thinking hints, prompt caching, recap, UI, resume fixes, policy-managed plugin auto-update (managed distribution)
- lines 8828-8828: EnterWorktree path parameter
- lines 8832-8835: /proactive alias
- lines 8838-8842: Stream, network error, write display, /doctor, /config improvements
- lines 8844-8846: WebFetch, worktree cleanup, MCP truncation prompt improvements
- lines 8850-8859: Queue images, rendering, input, worktree, focus, scheduled tasks, channel notification fixes
- lines 8861-8873: Official marketplace auto-update, resume hint, survey, MCP, Bedrock, rate limit, keybindings, palette fixes
- lines 8879-8887: /team-onboarding, CA store, ultraplan cloud environment
- lines 8890-8896: Brief/focus mode, errors, rate limits, resume, user settings hook event names
- lines 8899-8902: Ultraplan, beta tracing, SDK query cleanup
- lines 8905-8923: Security, memory, resume, timeout, permission, Bedrock, worktree, sandbox, MCP serve, UI fixes
- lines 8925-8935: MCP headersHelper menu, keybindings, login, rendering, settings, Remote Control, insights, VSCode fixes
- lines 8941-8950: Vertex wizard, Perforce, Monitor tool, sandboxing, prompt caching flag, status line, OTEL
- lines 8954-8955: /claude-api skill update and /compact hints
- lines 8959-8961: /resume, footer, /agents improvements
- lines 8963-8964: Accept Edits and Vim improvements
- lines 8966-8967: OTEL tracing and transcript usage
- lines 8971-8994: Bash permission, retry, MCP OAuth, keyboard, permissions, UI, resume, export, effort fixes
- lines 8996-9001: Upsell text, MCP meta size, voice, autoupdater, Remote Control, subagent progress
- lines 9003-9008: Survey, grep pattern file, worktree cleanup, sandbox, VSCode, context tokens fixes
- lines 9014-9040: Focus view, status line, agents indicator, syntax highlighting, /claude-api skill and 2.1.97 improvements
- lines 9043-9056: Permissions, MCP buffers/OAuth, retries, resume, transcript fixes
- lines 9058-9059: Subagent cwd leak and compaction duplicates
- lines 9062-9077: NO_FLICKER mode and Bedrock fixes; 2.1.96 Bedrock fix
- lines 9084-9085: Bedrock Mantle and Slack header
- lines 9088-9088: VSCode settings parse warning
- lines 9092-9092: Default effort level change
- lines 9094-9098: VSCode subprocess work and --resume worktree improvement
- lines 9102-9103: Rate limit and Console login fixes
- lines 9107-9117: Scrollback, prompts, input, hyperlinks, rendering, Bedrock, SDK, VSCode fixes
- lines 9123-9141: Remote settings refresh policy, Bedrock wizard, /cost, release notes, Remote Control names, removed commands, sandbox, Write speed
- lines 9144-9144: Tmux subagent pane fix
- lines 9146-9153: Tool input, API, survey, hints, Homebrew, input, scrolling fixes
- lines 9162-9162: MCP result size annotation
- lines 9164-9164: Deep link multi-line prompts
- lines 9169-9183: /feedback, Edit anchors, /claude-api skill, performance and 2.1.91 bug fixes
- lines 9191-9191: /powerup lessons
- lines 9193-9206: Protected dirs, PowerShell hardening, resume picker, DNS auto-allow, performance improvements
- lines 9210-9211: Rate-limit dialog and resume cache fixes
- lines 9214-9218: UI and auto mode fixes
- lines 9227-9227: NO_FLICKER env var
- lines 9229-9230: Subagent mention typeahead and MCP nonblocking
- lines 9234-9235: Auto mode denied notices and Edit after sed/cat
- lines 9237-9238: cleanupPeriodDays and thinking summaries
- lines 9240-9246: Task notifications, PowerShell, /env, /usage, paste, /buddy
- lines 9248-9254: Tool summary, Bash, typeahead, PowerShell prompt improvements
- lines 9257-9262: Permission rule symlinks, voice, CRLF, StructuredOutput, memory, large session fixes
- lines 9264-9269: History, stats, deferred tools, deep links, MCP errors, SDK images
- lines 9271-9275: Autocompact, cache, CLAUDE.md, resume, rate limit message fixes
- lines 9277-9293: UI, voice, terminal, PowerShell, Edit fixes; 2.1.87 Cowork Dispatch fix
- lines 9298-9316: Session header, VCS exclusions, connectors, tokens, memories, /skills listing cap (superseded), auto mode, Read format, provider caching
- lines 9319-9328: Resume, file access, config writes, feedback, bare mode, OAuth, official marketplace scripts, statusline, scroll fixes
- lines 9330-9334: Transcript, ultrathink, memory, VSCode fixes
- lines 9342-9342: MCP headersHelper env vars
- lines 9344-9345: Scheduled task markers and image placeholder spacing
- lines 9349-9349: Deep link query length
- lines 9350-9350: MCP OAuth server discovery internals; not plugin authoring or install
- lines 9353-9354: OTel and UI performance entries
- lines 9356-9361: Improved section: autocomplete/PowerShell/scroll, unrelated to plugins
- lines 9364-9364: compaction fix, unrelated
- lines 9367-9380: fixes for claude.ai MCP, computer-use, OTel, terminal, Remote Control, SDK; unrelated
- lines 9388-9390: PowerShell tool, 3p model env vars, stream timeout; unrelated
- lines 9394-9396: request header, idle prompt, VSCode banner; unrelated
- lines 9400-9400: deep links, unrelated
- lines 9403-9411: UI, connector dedup, caching and display changes; unrelated
- lines 9413-9437: improvements and bug fixes with no plugin/hook/skill/marketplace impact
- lines 9444-9444: admin policy-fragment deployment only
- lines 9446-9447: sandbox and deep-link settings; unrelated
- lines 9449-9452: transcript search, keybindings, streaming fallback, VSCode; unrelated
- lines 9456-9456: image paste chips, unrelated
- lines 9458-9465: keybindings, memory, startup, UI changes; unrelated
- lines 9467-9469: Linux protocol handler, keybinding, TaskOutput deprecation; unrelated
- lines 9471-9476: clipboard, screen, SDK, memory, channels, VSCode; unrelated
- lines 9480-9481: Bedrock and resume performance; unrelated
- lines 9483-9484: Remote Control titles, WebFetch UA; unrelated
- lines 9488-9502: terminal, MCP policy, UI and agent fixes with no plugin impact
- lines 9504-9528: UI, voice, remote session, sandbox, VSCode fixes; unrelated
- lines 9537-9537: channels permission relay, not plugin distribution
- lines 9539-9545: Changed section: worktree, MCP OAuth, plan mode, Windows streaming; unrelated
- lines 9548-9549: MCP display and bash mode hints; unrelated
- lines 9551-9551: Remote Control titles; unrelated
- lines 9555-9561: auth, voice, beta header, channels, Node, Bash prompt fixes; unrelated
- lines 9563-9571: background agents, /btw, tmux, Remote Control, VSCode fixes; unrelated
- lines 9579-9580: statusline rate limits; settings-inline marketplace source is not the GitHub channel
- lines 9583-9583: channels research preview; unrelated
- lines 9588-9588: startup memory; unrelated
- lines 9590-9596: Improved section: autocomplete, /effort, /permissions, tasks panel; unrelated
- lines 9599-9603: resume, voice, proxy, remote-control, sandbox fixes; unrelated
- lines 9610-9625: auth flag, config toggle, VSCode; plugin seed dir is a pre-population channel, not GitHub marketplace; memory/fallback
- lines 9628-9635: print mode, /btw, voice, permissions, terminal title, statusline, 429 fixes; unrelated
- lines 9637-9638: VSCode UI fixes
- lines 9649-9649: custom model picker env var; unrelated
- lines 9651-9659: Changed/Improved: terminal notifications, streaming, memory; unrelated
- lines 9662-9663: sandbox git and resume truncation fixes; unrelated
- lines 9665-9672: permission, sandbox, keybinding, voice fixes; unrelated
- lines 9674-9680: git instructions, PATH, color, betas, queue, VSCode fixes; unrelated
- lines 9686-9703: sandbox setting and Changed section (tokens, /copy, startup, agents, VSCode); unrelated
- lines 9706-9706: Esc abort; unrelated
- lines 9708-9709: seed-dir headless install (non-marketplace channel); VSCode titles
- lines 9713-9715: permissions, auto-updater, resume fixes; unrelated
- lines 9717-9725: write tool, memory, cost, betas, Bash, paste, Desktop auth fixes; unrelated
- lines 9727-9740: UI, worktree, tmux, terminal, teammate fixes; unrelated
- lines 9750-9751: session name flag, sparse worktree setting; unrelated
- lines 9753-9754: /effort command, survey admin setting; unrelated
- lines 9760-9769: improvements section: worktree, agents, notifications, UI, voice; unrelated
- lines 9772-9776: tool search, slash commands, plan mode, voice fixes; unrelated
- lines 9778-9782: model strings, permission rules, compaction, MCP spinner; unrelated
- lines 9784-9791: clipboard, export, transcript, login, Remote Control, VSCode fixes; unrelated
- lines 9799-9802: context window, /color, session name, memory timestamps; unrelated
- lines 9808-9808: Windows managed-settings path for administrators only
- lines 9810-9813: macOS startup improvement; unrelated
- lines 9816-9819: voice, header, crash, Bash fixes; unrelated
- lines 9821-9821: token estimation; unrelated
- lines 9823-9826: resume, status dialog, plan, teams footer fixes; unrelated
- lines 9832-9836: /context suggestions, auto-memory directory; unrelated
- lines 9841-9844: VSCode scroll; unrelated
- lines 9847-9847: streaming memory leak; unrelated
- lines 9850-9852: MCP OAuth callback/refresh and voice entitlement fixes; unrelated
- lines 9856-9859: slash command input, RTL, LSP URIs on Windows, VSCode; unrelated
- lines 9865-9883: model overrides, SSL guidance, default models, output-style command, UI improvements; unrelated
- lines 9886-9893: CPU, skill file deadlock, Bash output, provider models, resume, /ide, /loop fixes; unrelated
- lines 9896-9901: voice, sandbox, Linux, Remote Control, heapdump, VSCode fixes; unrelated
- lines 9907-9924: Added (copy, plan, worktree, cron, allowlist, non-GitHub git URLs, VSCode) and Changed (agent model, effort, bundle, CLAUDE.md comments); unrelated or non-GitHub
- lines 9927-9930: config, history, voice, bash parsing improvements; unrelated
- lines 9932-9932: CPU; unrelated
- lines 9936-9938: tool search, exits, agent progress; unrelated
- lines 9940-9942: voice, continue, bash parsing; unrelated
- lines 9944-9956: survey, effort, background, model, sandbox, SDK cache, keys, permissions fixes; unrelated
- lines 9958-9968: Desktop, terminal title, permission rules, images, Bedrock, titles, VSCode fixes; unrelated
- lines 9974-9985: /loop, cron, keybinding, allowlist, debug, connector notices; unrelated
- lines 9988-9989: startup and bridge reconnection; unrelated
- lines 9995-10000: stdin, voice, connectors, fork, Read, heredoc fixes; unrelated
- lines 10002-10006: claude.ai connectors, agents, Bash, Chrome fixes; unrelated
- lines 10009-10012: permissions, print, ToolSearch, Windows prompt fixes; unrelated
- lines 10018-10035: VSCode additions, render/memory/poll changes, voice/compaction/rename improvements; unrelated
- lines 10038-10048: gateway, Bedrock, ToolSearch, cache, SSH, clipboard, voice, links, model fixes; unrelated
- lines 10051-10057: security-review, /color, AskUserQuestion, flags, Remote mode, resume, teleport fixes; unrelated
- lines 10065-10073: bundled skill, keyboard, remote-control name, voice, effort, agent title, sandbox, git instructions; unrelated
- lines 10075-10075: Desktop suggestion prompt; unrelated
- lines 10079-10082: status line worktree field; admin trust message; Team policy limits; pathPattern for file/directory marketplace sources (not GitHub)
- lines 10085-10085: VSCode compaction card
- lines 10087-10116: Changed and improvements sections: memory, models, UI, performance, docs note; no plugin impact
- lines 10119-10134: skill discovery in gitignored dirs, trust dialog, remote-control, auth, terminal, worktree fixes; unrelated to plugin components
- lines 10137-10147: memory, API, teammates, compaction, Windows, symlink, sandbox fixes; unrelated
- lines 10149-10163: memory, Escape, Android, leaks, MCP config, startup, permissions, rules, UI fixes; unrelated
- lines 10168-10176: /context, Windows nul, UI, CCR logs, voice, VSCode fixes; unrelated
- lines 10178-10191: 2.1.68 and 2.1.66: model defaults and logging only
- lines 10198-10199: bundled commands, claude.ai MCP opt-out; unrelated
- lines 10201-10203: MCP OAuth paste fallback, /copy option, VSCode; unrelated
- lines 10205-10233: worktree config sharing, model menu, memory leak fixes; unrelated
- lines 10234-10295: versions 2.1.62-2.1.52: cache, Windows, memory, Remote Control, VSCode fixes only
- lines 10300-10305: remote-control subcommand, npm-source registries (not GitHub), SDK account vars
- lines 10309-10312: BashTool login shell, tool result persistence, model picker, admin managed-settings channels
- lines 10316-10317: statusLine trust and duplicate control_response fixes; unrelated
- lines 10329-10331: agents CLI listing, 1M context env var, VSCode; unrelated
- lines 10333-10360: simple mode, fast mode context, memory improvements and leak fixes; unrelated
- lines 10367-10368: worktree flag, kill keybinding; unrelated
- lines 10376-10379: simple mode, SDK permission suggestions, model changes; unrelated
- lines 10381-10390: MCP auth and startup performance improvements; unrelated
- lines 10393-10395: path suggestions, Ctrl+C, cache fixes; unrelated
- lines 10397-10400: verbose, WASM, yoga fixes; unrelated
- lines 10402-10402: resume picker fix; unrelated
- lines 10411-10431: keybinding, statusline, Changed UI items, memory/performance improvements; unrelated
- lines 10434-10440: write tool, Windows rendering, compaction, bash, permission classifier, NFS agents fixes; unrelated
- lines 10442-10450: Windows temp, API, parallel edits, titles, bash, autocomplete, MCP dialog fixes; unrelated
- lines 10452-10467: resume, doctor, sandbox, UI, teammates, provider, telemetry, permission fixes; unrelated
- lines 10469-10471: fork crash, FSEvents, project-level worktree discovery; unrelated
- lines 10473-10476: CLAUDE.md casing, markdown, spinner, shell fixes; unrelated
- lines 10478-10486: LSP gitignore results, resume, shell, spinner, VSCode, worktree, Unicode, OSC fixes; unrelated
- lines 10488-10494: 2.1.46: macOS process and claude.ai connectors; unrelated
- lines 10501-10501: model support; unrelated
- lines 10503-10504: spinner tips setting, SDK types; unrelated
- lines 10506-10512: performance and VSCode improvements; unrelated
- lines 10515-10520: provider teams, sandbox, Task, autocomplete, subagent skills, backup fixes; unrelated
- lines 10523-10547: versions 2.1.44-2.1.42: auth, paths, performance fixes only
- lines 10552-10564: nesting guard, OTel, auth subcommands, ARM64, error/rename/layout improvements; unrelated
- lines 10567-10570: provider teams, MCP image crash, resume, plugin browse hint; not acted on
- lines 10572-10580: file resolution, FIFO, SDK, UI and permission fixes; unrelated
- lines 10583-10623: versions 2.1.39-2.1.34: rendering, sandbox, fast mode fixes only
- lines 10634-10635: VSCode remote sessions and picker
- lines 10637-10655: managed-settings errors, connection error messages, thinking/proxy/VSCode fixes; unrelated
- lines 10660-10665: agent teams preview, summarize, VSCode spinner; unrelated
- lines 10668-10671: Opus release, memories, add-dir skills, resume agent; unrelated
- lines 10674-10680: @ completion, heredoc, Thai, VSCode fixes; unrelated
- lines 10681-10824: versions 2.1.31-2.1.21: UI, PDF, MCP OAuth credentials, performance, proxy fixes; no plugin impact
- lines 10829-10853: vim history, editor, PR status, add-dir CLAUDE.md, tasks; UI changes and improvements; unrelated
- lines 10856-10862: compaction, agents, rendering, MCP unicode, history, ghost text fixes; unrelated
- lines 10864-10867: output, task list, syntax highlighting, cancel fixes; unrelated
- lines 10875-10875: tasks env var; unrelated
- lines 10877-10877: SDK replay; unrelated
- lines 10883-10883: VSCode forking
- lines 10887-10892: AVX, process, rename, resume, stash, agent list fixes; unrelated
- lines 10894-10894: file write preview; unrelated
- lines 10896-10907: 2.1.18 keybindings and 2.1.17 AVX fix; unrelated
- lines 10912-10912: task management system; unrelated
- lines 10914-10918: VSCode sessions, memory and UI fixes; unrelated
- lines 10920-10928: 2.1.15: npm deprecation notice, rendering, compact, MCP timeout fixes
- lines 10935-10935: bash history autocomplete; unrelated
- lines 10938-10938: VSCode /usage
- lines 10940-10969: 2.1.14 improvements/fixes and 2.1.12, 2.1.11: UI and memory fixes only
- lines 10975-10980: OAuth URL copy, heredoc, startup, suggestions, VSCode listing display; unrelated
- lines 10986-10989: tool search threshold, plans dir, editor, session URL attribution; unrelated
- lines 10992-10994: orphan tool_result, MCP reconnection, Ctrl+Z fixes; unrelated
- lines 11000-11014: turn duration, feedback, notifications, MCP tool search, console URLs, typing; unrelated
- lines 11017-11022: permission rule, Windows, tool_result, context, spinner, title fixes; unrelated
- lines 11024-11025: Windows temp paths, VSCode wrapper; unrelated
- lines 11027-11080: versions 2.1.6-2.1.4: config search, doctor, stats, nested project skills, UI fixes, env vars; unrelated
- lines 11085-11090: release channel, unreachable permission rules, VSCode selector; unrelated
- lines 11096-11109: rendering improvements and plan/skill-inode/task/model/trust fixes; unrelated
- lines 11116-11119: image metadata, hyperlinks, winget, Shift+Tab; unrelated
- lines 11123-11147: output persistence, /plugins tab layout, admin Windows path, SDK; improvements; security and UI fixes unrelated to plugins
- lines 11154-11154: hot-reload of user/project skill directories, not plugin skills
- lines 11157-11164: language, gitignore, demo, Bash wildcards, backgrounding, MCP list_changed, teleport, agent disabling; unrelated
- lines 11167-11171: vim, /plan, autocomplete, --tools, read token env var; unrelated
- lines 11175-11181: image paste, tab nav, thinking display, task details, context viz, VSCode; unrelated
- lines 11183-11193: Changed section: terminal, permissions, startup, Atlassian, UI, SDK; unrelated
- lines 11196-11205: CLI help, rendering, notebooks, piped input, compaction, subagent, skill progress improvements; not acted on
- lines 11207-11214: skill suggestions, spinner, async agents, permission UX, Chrome, macOS, /stats; unrelated
- lines 11218-11222: debug log secrets, resume, paste, Esc, command search fixes; unrelated
- lines 11224-11237: file-based marketplace path resolution (not GitHub); LSP, background, Chrome, Windows, OAuth, Bedrock, terminal fixes
- lines 11239-11271: Write permissions, bash parsing, slash commands, UI, model picker, memory, VSCode, Windows fixes; unrelated
- lines 11273-11284: 2.0.76 and 2.0.75: Chrome code-sign and minor fixes
- lines 11292-11296: terminal setup, theme, macOS guidance, VSCode promo; unrelated
- lines 11298-11301: /context visualization improvement; unrelated
- lines 11305-11309: Opus tip, highlighting crash, discover UI, macOS labels, Windows rendering; unrelated
- lines 11311-11362: versions 2.0.73-2.0.71: UI, Chrome, search, MCP/permission/Bedrock fixes; no plugin marketplace impact
- lines 11369-11370: prompt suggestions, MCP permission wildcard; unrelated
- lines 11372-11372: status line current_usage; unrelated
- lines 11374-11407: 2.0.70 Changed/Improved/Fixed, 2.0.69, 2.0.68 (IME, MCP, admin managed settings enablement); unrelated
- lines 11412-11421: permissions search, thinking mode, autoupdater reason; unrelated
- lines 11424-11429: update lock, .mcp.json pending, permissions, word nav, install, CLAUDE.md parsing fixes; unrelated
- lines 11432-11482: versions 2.0.65-2.0.62: model switch, status line, rules, Bedrock, UI, attribution, symlink fixes; none affect plugins (2.0.62 has no plugin entries, its last entry continues in chunk 09)
- lines 11483-11501: IDE diff fix (end of 2.0.62), 2.0.61 and 2.0.60: VSCode, background agents, CLI flags; unrelated
- lines 11506-11506: --agent session flag; not used by plugin authoring or install
- lines 11508-11508: VS Code config path fix
- lines 11510-11540: versions 2.0.58-2.0.55: models, Windows admin path, UI, proxy; unrelated
- lines 11546-11546: iTerm notifications
- lines 11548-11602: versions 2.0.52-2.0.46: UI, usage, models, MCP schema, teleport, Vertex fixes; unrelated
- lines 11607-11607: Microsoft Foundry provider support
- lines 11609-11609: web background tasks
- lines 11619-11622: CLAUDE.md, rendering, NotebookEdit fixes; unrelated
- lines 11639-11645: Changed: history search, SDK hook timeouts, git approvals, teleport; unrelated
- lines 11648-11649: user-settings slash command fixes; unrelated
- lines 11651-11653: Bedrock picker, docs links, ESC fixes; unrelated
- lines 11659-11659: notification idleness
- lines 11663-11697: versions 2.0.36-2.0.33: autoupdater, search, VSCode, SDK, OAuth, doctor fixes; unrelated
- lines 11703-11703: admin announcements setting
- lines 11710-11714: Windows shortcut, Vertex, VSCode, subagent MCP, compact fixes; unrelated
- lines 11723-11724: keychain hint, sandbox policy setting; unrelated
- lines 11727-11727: VSCode respectGitIgnore
- lines 11729-11735: Changed: SSE native build, superseded output-style deprecation, ripgrep, VSCode; unrelated
- lines 11738-11742: Explore agent, /context, --mcp-config, session permissions, subagent MCP fixes; unrelated
- lines 11744-11744: typeahead delay
- lines 11750-11755: Plan subagent, subagent resume/model, SDK budget, gitignore discovery, terminal setup; unrelated
- lines 11757-11758: macOS prompt and misc fixes
- lines 11760-11784: versions 2.0.27-2.0.24: UI, SDK migration, project skills flag, web teleport, sandbox, Bedrock; unrelated
- lines 11789-11791: layout, IDE thinking toggle, duplicate prompts; unrelated
- lines 11794-11803: 2.0.21: MCP structuredContent, question tool, models; unrelated
- lines 11810-11852: versions 2.0.19-2.0.13: bash, models, Explore, OTEL, resume, UI polish, native /plugin fix; unrelated
- lines 11863-11869: blog/doc links, doctor, model selector, help, resume, verbose; not acted on
- lines 11871-11879: 2.0.11: system prompt, IDE, rate limit, add-dir fixes
- lines 11884-11886: renderer, MCP toggle, tab completion; unrelated
- lines 11888-11889: editor shortcut, bash permission fix; unrelated
- lines 11891-12018: versions 2.0.9-1.0.113: VS Code, models, UI, SDK, Bash permissions, MCP headers, misc; no plugin component impact
- lines 12023-12024: transcript model display, Max recognition
- lines 12026-12027: spinner tips setting, IDE
- lines 12029-12101: versions 1.0.111-1.0.86: models, MCP OAuth refresh, SDK, settings, proxy, statusline, /context; unrelated
- lines 12106-12106: status line cost info
- lines 12109-12193: versions 1.0.84-1.0.69: UI, SDK, output styles release, Bash, MCP config files, statusline; unrelated
- lines 12198-12202: model names, Windows, doctor, SDK canUseTool; unrelated
- lines 12204-12204: file suggestions performance
- lines 12206-12212: 1.0.65: IDE and Windows fixes
- lines 12218-12218: recursive agent tool fix
- lines 12220-12221: SDK input tracking, hidden files
- lines 12223-12228: 1.0.63: Windows fixes
- lines 12233-12233: agent @-mention typeahead
- lines 12235-12236: /add-dir typeahead, network check
- lines 12238-12250: 1.0.61: transcript, settings flag, OTEL, IDE, shell prefix; unrelated
- lines 12261-12262: SDK callbacks and env
- lines 12265-12265: Max/Opus fallback fix
- lines 12271-12272: PDF reading, mcp list display
- lines 12280-12281: permission messages, bash output fix
- lines 12283-12299: 1.0.56 and 1.0.55: Windows, WSL, AWS, models, SDK, system prompt file; unrelated
- lines 12306-12308: Windows OAuth and mode switching, shell snapshot
- lines 12310-12336: versions 1.0.53-1.0.51: @-mention, AWS helpers, MCP instructions, Windows, Bedrock, misc; unrelated
- lines 12341-12342: freeze fix, Bash progress
- lines 12344-12345: shell snapshots, IDE WSL
- lines 12347-12347: vim mode
- lines 12353-12357: Grep redesign, IDE diffs, config writes, undo, old Stop hook fix; not acted on
- lines 12360-12381: versions 1.0.44-1.0.42: export, MCP display, Ctrl+Z, theme, EPIPE, add-dir; unrelated
- lines 12389-12390: MCP duplicate display, telemetry
- lines 12392-12403: 1.0.40 and 1.0.39: CA certs, OTel; unrelated
- lines 12410-12455: versions 1.0.37-1.0.31: proxy auth, web search, MCP OAuth discovery, logging, login; unrelated
- lines 12461-12463: autocomplete, Ctrl-r, jq
- lines 12465-12480: 1.0.29 and 1.0.28: CJK, images, XDG, telemetry; unrelated
- lines 12486-12488: MCP OAuth, MCP resource mentions, /resume; not acted on
- lines 12490-12885: versions 1.0.25-0.2.21: early UI, SDK, MCP CLI scopes, project slash commands, permissions history; no current plugin marketplace relevance

## 05-cli-diagnostics/cli-reference.md

- lines 19-21: Continuing/resuming conversations is general session use, not plugin development, testing or installation
- lines 23-23: Self-hosted apps gateway for administrators on cloud providers; unrelated to plugins
- lines 25-35: Account auth, agent view, background sessions, auto-mode and daemon commands are not used to build, test or install plugins
- lines 37-38: Importing other agents' config and background-session logs are unrelated to plugins
- lines 41-41: Clearing MCP OAuth credentials is general MCP account maintenance, not plugin work
- lines 43-50: Purge, remote control, background session management, self-hosted runner, setup-token and ultrareview are unrelated to plugin development or installation
- lines 52-54: Typo suggestion and daemon alias routing are not acted on for plugins
- lines 62-63: Additional directories and advisor model are not plugin-related
- lines 65-66: CLI-defined subagents and bypass mode cycling are not plugin components or plugin testing steps
- lines 68-73: System prompt, autocompact and screen reader flags do not affect building or testing plugins
- lines 75-76: Beta headers and background agents are unrelated to plugins
- lines 78-80: Chrome, cloud sessions and continuing conversations are unrelated to plugins
- lines 82-82: Skipping permissions is a general session mode, not a plugin step
- lines 85-97: Desktop, slash-command disabling, tool denial, effort, auto mode, self-hosted environments, prompt caching, exec, fallback, fork, subagent text forwarding, PR picker and IDE flags are not used for plugin work
- lines 101-103: Partial messages, input format and JSON schema output are SDK/scripting features not tied to plugins
- lines 105-111: Budget, turns, standalone MCP config, model, naming, chrome and persistence flags are not plugin-related
- lines 113-115: Permission mode and prompt-handling flags are general session controls, not plugin work
- lines 117-117: Loading a plugin zip from an arbitrary URL is archive-based distribution, not the public GitHub marketplace; local testing is covered by --plugin-dir
- lines 119-126: Prompt suggestions, environment refs, remote/remote control, replay, restricted mode and resume are unrelated to plugins
- lines 128-128: Specific session IDs are not plugin-related
- lines 131-138: Standalone MCP config, system prompt, teleport, agent teams, tmux and built-in tool restriction flags are not plugin work
- lines 141-141: Git worktree sessions are unrelated to plugins
- lines 143-178: System prompt flags section concerns customizing Claude's system prompt, not building, testing or installing plugins
- lines 181-184: Links to Chrome, interactive mode, quickstart and workflows are not relied on for plugins
- lines 186-186: Agent SDK link is programmatic usage, not plugin work

## 05-cli-diagnostics/debug-your-config.md

- lines 11-12: Pointer to installation/login troubleshooting is not about plugin components loading
- lines 23-23: /memory covers CLAUDE.md and auto memory files, which plugins do not ship
- lines 27-27: Resolved permission rules are general session configuration, not plugin loading
- lines 32-41: CLAUDE.md loading and instruction adherence guidance concerns project memory files, not plugin components
- lines 54-54: One-time approval of project-scoped .mcp.json servers does not apply to plugin-provided MCP servers
- lines 64-64: Says hooks cannot live in a standalone file; for plugins hooks/hooks.json is the correct location, so this does not apply
- lines 73-76: settings.json live reload and /hooks refresh concern user/project settings hooks, not plugin hooks
- lines 92-93: Managed policy behavior in safe mode only explains an organization's own setup
- lines 153-154: ~/.claude.json vs settings.json and settings.local precedence are user configuration issues, not plugin issues
- lines 157-159: Subdirectory CLAUDE.md, subagent CLAUDE.md loading and SessionEnd in settings.json are not plugin troubleshooting
- lines 161-162: settings.json mcpServers and project server approval do not apply to plugin MCP servers
- lines 165-165: Bash permission rule limits are a user permissions matter, not plugin work
- lines 171-172: .claude directory and settings references are general user configuration links
- lines 175-176: Installation/login and performance troubleshooting links are not plugin-related

## 05-cli-diagnostics/errors.md

- lines 9-16: General scope of the error page and raw API error pointer; not acted on for plugins
- lines 23-45: Server, retry, auto mode, usage limit, account authentication and Remote Control error rows are unrelated to plugins
- lines 47-113: Server, retry, auto mode, usage limit, account authentication and Remote Control error rows are unrelated to plugins
- lines 116-116: Cowork-specific MCP credential message, not a Claude Code plugin case
- lines 124-179: Cloud gateway, cloud provider credentials, network, prompt length, image and PDF error rows are unrelated to plugins
- lines 184-194: Model selection and availability errors are unrelated to plugins
- lines 196-244: Model defaults, thinking, safety, installation, CLI flag, cloud session, settings file and temp directory errors are unrelated to plugins
- lines 246-254: Remote Control, ultrareview, import and managed-scope MCP add errors are unrelated to plugins
- lines 256-256: Anthropic-hosted connector OAuth is not a plugin MCP case
- lines 258-259: Saving/removing user-configured MCP servers is not plugin work
- lines 262-264: Permission prompt tool and OAuth port errors are general CLI issues
- lines 269-273: Print-mode input and stdin errors are unrelated to plugins
- lines 275-303: Ultrareview, GitHub cloud cloning, resume, renderer, restart, Desktop, Zed, skill usage reports, output style relay, recap and feedback policy errors are unrelated to plugins
- lines 318-318: command and archive plugin sources excluded by user decision 2026-11-08
- lines 329-329: Organization-required synced plugin applies only to org-managed distribution
- lines 340-427: Permission, file, symlink, disk, teammate, artifact, WebFetch, background session, wrapper, rewind, transcript and renderer errors are unrelated to plugins
- lines 430-430: Instruction file loading concerns CLAUDE.md files, not plugins
- lines 433-447: Workspace trust for permissions, network working directories, remote managed settings and provider/model policy errors only concern an organization's own setup
- lines 450-477: Managed settings parsing, telemetry, Foundry, permission rule, context window, model ID and sandbox warnings are unrelated to plugins
- lines 479-553: Automatic retries, retry tuning and server/API timeout errors concern API connectivity, not building, installing or debugging plugins
- lines 555-645: Automatic retries, retry tuning and server/API timeout errors concern API connectivity, not building, installing or debugging plugins
- lines 646-762: Mid-stream API failures and auto mode classifier availability errors: general session runtime troubleshooting, nothing the maintainer or marketplace user acts on for building, publishing or installing plugins
- lines 764-798: Server-side classifier no-verdict denials and gateway causes: auto mode/API behavior unrelated to plugins; heading kept only as parent of the hook-changed-input subsection
- lines 815-832: Classifier context overflow, subagent API errors, and the whole Usage limits section (plan quotas, spend limits, credits, 429s): account/billing troubleshooting not tied to the plugin marketplace
- lines 848-1030: Classifier context overflow, subagent API errors, and the whole Usage limits section (plan quotas, spend limits, credits, 429s): account/billing troubleshooting not tied to the plugin marketplace
- lines 1032-1629: Login, API key, apiKeyHelper, OAuth, Remote Control, organization policy, gateway sign-in and profile authentication errors: account credential troubleshooting that does not affect adding a public marketplace or building/installing plugins; H2 kept as parent of MCP auth subsections in the next chunk
- lines 1630-1656: Claude login OAuth scope and claude.ai connector session-token errors: account login issues, not plugin-bundled MCP servers
- lines 1758-1791: audit: MCP OAuth server-operator errors
- lines 1792-2001: AWS, Google Cloud, Foundry and Claude apps gateway credential errors: cloud-provider/gateway authentication operated by the user's own setup, unrelated to the marketplace or plugin components
- lines 2004-2323: API connectivity, TLS, cloud-session allowlist, artifact proxy, cloud environments, teleport, Remote Control and feedback errors: network/session troubleshooting not involved in adding the marketplace or running plugin components
- lines 2347-2575: Context window, request size, image, PDF and beta-field gateway errors: request-content troubleshooting unrelated to plugins
- lines 2617-2651: Overlong tool_use names in history and selected-model errors: conversation/model configuration issues not tied to plugin development or installation
- lines 2652-2766: Model-switch, plan, version-minimum errors for the session model; general usage, not plugin development, publishing or installing
- lines 2787-2808: Default-model switch blocked by managed model lists; about the user's session model, not plugin components
- lines 2827-3069: Saving default model, advisor, thinking/effort/output limits, history corruption, proxy and usage-policy/cyber refusals; general API usage errors unrelated to the plugin marketplace
- lines 3089-3101: Output content filter refusal; general usage, not plugin-related
- lines 3103-3532: Command-line errors for --bg, system prompt flags, --agents, cloud sessions, teleport, --json-schema, --settings, ~/.claude.json, cwd/temp dir, /add-dir, Remote Control, ultrareview trust, claude import, Desktop MCP import, managed-scope MCP add; none used to build, publish or install marketplace plugins
- lines 3550-3610: Errors of claude mcp add/remove on user's own config and Anthropic-hosted connectors; not plugin-provided servers
- lines 3659-3674: --permission-prompt-tool in headless runs; not part of plugin development or installation
- lines 3717-3722: Git setups lacking origin/HEAD for /security-review; specific to that built-in command, not plugin skills
- lines 3730-3735: Fixes for /security-review's missing origin/HEAD ref; not about plugin skills' injected commands
- lines 3754-3820: Headless input, keyboard, whitespace and stream-json errors; general CLI usage unrelated to plugins
- lines 3832-3832: Built-in commands unavailable by platform/plan/policy; not plugin commands
- lines 3835-3848: How non-interactive surfaces handle unmatched slash names and history of menu matching; not acted on for plugins
- lines 3854-4243: Ultrareview, cloud sessions, GitHub app/SSO, resume, renderer restart, Desktop, Zed keymap, skill-doctor and output styles over Remote Control, /recap, /feedback policy; none concern building, publishing or installing marketplace plugins
- lines 4369-4386: command and archive plugin sources excluded by user decision 2026-11-08
- lines 4527-4542: Plugins synced from claude.ai and required by an organization; org-managed distribution channel
- lines 4591-4656: Generic MCP tool-call errors (missing tool, closed connection, disabled server, elicitation timeout); not specific to plugin development or installation
- lines 4683-4737: Read deny rules and blockWritesOutsideWorkingDirectories for Claude's file writes; user permission configuration unrelated to plugins
- lines 4738-4753: Null-byte file tool error: generic runtime tool error, nothing the plugin maintainer or marketplace user acts on
- lines 4767-5775: Remaining tool errors (restart approval, image size, subagent_type, memory index, pkill, agent teams, cross-session messaging, symlink/path refusals, task output, disk full, git on Mac, UTF-8, artifacts, Cowork, WebFetch), background session, wrapper/IDE, rewind and session-saving errors: general Claude Code usage/runtime diagnostics unrelated to building, publishing, adding or installing plugins from a public GitHub marketplace
- lines 5787-5801: Terminal renderer crash: general UI failure, not plugin related
- lines 5829-5854: CLAUDE.md/rules file withheld by Read deny rules: user instruction files, not plugin components
- lines 5889-5988: Workspace trust for project allow rules, network working directories, server-managed settings fetch/org settings load/declined approval: admin or local-setup diagnostics that do not affect adding or installing the marketplace's plugins
- lines 6001-6040: Managed settings blocking default model or API provider: admin model/provider policy, unrelated to plugin distribution
- lines 6076-6469: Managed settings document parse/read failures, managed invalid hooks, otelHeadersHelper, headersHelper trust, permission rule warnings, crossSessionInbound, Foundry, 200K limit, unrecognized model ID, sandbox locks/mask files, ~/.claude.json save, response quality: admin, provider or general usage diagnostics the maintainer/user would not act on for this scenario
- lines 6481-6481: /feedback disabled by organization policy: org-admin case only

## 05-cli-diagnostics/headless.md

- lines 75-100: Background tasks and MCP work at exit of -p runs: general scripting behavior, not used for testing or publishing plugins
- lines 101-115: SIGTERM handling and deleted working directory: process-supervisor details unrelated to plugin work
- lines 120-153: Piping data and build-script linter examples: generic usage, not plugin testing
- lines 168-196: --json-schema structured output and jq tip: generic data extraction, not needed for plugin load checks
- lines 207-217: Slow consumer drain and text-delta streaming example: generic streaming UI details
- lines 218-261: Following subagent messages and API retry events: SDK stream consumption details not used for building or verifying plugins
- lines 309-353: Auto-approve tools and permission prompts in unattended runs: general permission configuration for scripts, not plugin distribution or testing
- lines 356-364: Commit-creation example and allowedTools prefix syntax: generic example
- lines 375-412: System prompt customization and continuing conversations: generic scripting
- lines 415-415: Agent SDK quickstart link: SDK app building, not plugin work
- lines 418-418: GitLab CI/CD link: non-GitHub host

## 05-cli-diagnostics/troubleshoot-install.md

- lines 9-1136: Troubleshooting the installation of the Claude Code CLI itself (network, PATH, conflicting installs, permissions, OS/binary errors, npm, Windows shells) and general login errors; nothing here is about building, publishing, adding or installing plugins from a public GitHub marketplace
- lines 1138-1232: Troubleshooting the installation of the Claude Code CLI itself (network, PATH, conflicting installs, permissions, OS/binary errors, npm, Windows shells) and general login errors; nothing here is about building, publishing, adding or installing plugins from a public GitHub marketplace
- lines 1234-1262: OAuth token expiry, parallel-session renewal and macOS Keychain repair for the Claude login; not part of the marketplace or plugin workflow
- lines 1266-1315: Login on network home directories, cloud-provider credential loading and generic support channels; unrelated to adding the marketplace or installing/running its plugins

## 06-agent-sdk/sdk-hooks.md

- lines 9-907: Agent SDK in-process callback hooks registered through options.hooks in Python/TypeScript applications (events per SDK, HookMatcher, callback inputs/outputs, onFailure, SDK examples, SDK troubleshooting and links); plugin hooks are shell/hooks.json hooks documented elsewhere, so neither the marketplace maintainer nor the installing user applies these passages

## 06-agent-sdk/sdk-mcp.md

- lines 9-188: Agent SDK MCP intro, quickstart, adding servers via options.mcpServers or project .mcp.json, and SDK first-turn connection timing; SDK application configuration, not plugin marketplace work
- lines 205-907: SDK allowedTools, tool discovery via init message, transports in code, SDK MCP servers, tool search, SDK auth/OAuth, SDK examples, error handling, troubleshooting and related links; all specific to building an Agent SDK app

## 06-agent-sdk/sdk-plugins.md

- lines 9-278: Loading plugins into Agent SDK sessions from local paths (type local, path rules, reloadPlugins/addPlugins, init-message verification, SDK prompts, CLI-installed path reuse, complete SDK example); another way of loading plugins, not adding/installing from the public marketplace
- lines 303-334: Combining local plugin paths in SDK options and SDK plugin-loading troubleshooting (init plugins list, plugin_errors, nonexistent paths skipped)
- lines 340-340: Checks the SDK init message skills list; only applies to SDK sessions
- lines 342-350: See-also pointers to SDK pages and to plugin docs; nothing actionable in this scenario

## 06-agent-sdk/sdk-skills.md

- lines 24-24: contrast with SDK programmatic subagents; nothing to act on for plugin skills
- lines 48-90: example for loading project/personal filesystem skills via setting_sources, not plugin skills
- lines 104-104: name clashes in additionalDirectories, not a plugin distribution path
- lines 123-160: SDK command discovery code examples, not needed to build or install marketplace plugins
- lines 170-172: SDK maxTurns error handling for commands, not plugin related
- lines 174-259: /compact and /clear behavior in SDK sessions, unrelated to plugins
- lines 261-342: creating project/personal skills in .claude/skills for SDK sessions, not plugin skills
- lines 344-389: pre-approving tools for project/personal skills in SDK query config, not plugin skills
- lines 393-455: troubleshooting filesystem setting sources and cwd for .claude/skills, not plugin skills
- lines 462-495: audit: Agent SDK skill-name validation
- lines 512-512: link to built-in commands surface, not plugin related
- lines 516-519: generic SDK reference links, not used for the marketplace

## 07-cross-platform-external/build.md

- lines 15-15: making a plugin for own use from a conversation, not marketplace development
- lines 39-39: Anthropic directory acceptance and publishing requirements
- lines 137-161: README and license framed as Anthropic directory listing/validation requirements
- lines 267-267: directory submission validation in developer portal
- lines 279-279: org-internal distribution by Team/Enterprise Owner
- lines 281-281: publishing to Anthropic's directory

## 07-cross-platform-external/platform-skills-best-practices.md

- lines 777-779: claims no built-in way to run evaluations; plugin skills are evaluated with claude plugin eval, so the maintainer would not rely on it
- lines 1036-1036: Claude API code execution limits, not a plugin install surface
- lines 1180-1183: API Agent Skills quickstart card, not plugin development
- lines 1188-1190: uploading skills through the API, not plugin distribution

## 07-cross-platform-external/platform-skills-overview.md

- lines 37-40: Messages API and Managed Agents usage, not plugin distribution
- lines 42-54: conceptual benefits and blog link, nothing to act on
- lines 56-69: pre-built skills and API/cloud-provider/claude.ai-settings upload of custom skills, not plugins
- lines 179-193: Claude API and cloud-provider skill usage
- lines 201-201: personal/project skill folders, not plugin skills
- lines 205-218: claude.ai pre-built skills and zip upload of custom skills, not plugin installation
- lines 274-274: enterprise governance and scanning of uploaded skills, admin operation
- lines 276-297: catalog of pre-built and Anthropic open-source skills and cookbook
- lines 299-317: data retention, API/Foundry limits and cross-surface sync of uploaded skills
- lines 323-323: API workspace sharing scope
- lines 333-337: Claude API runtime constraints, not a plugin surface
- lines 349-355: API quickstart and API guide cards
- lines 366-406: API and cloud availability and data handling tables

## 07-cross-platform-external/platform-support.md

- lines 18-18: MCP Apps rendering pointer, not about installing or building marketplace plugins
- lines 42-42: Anthropic directory submission and listing
- lines 56-56: browsing and publishing to Anthropic's directory
- lines 63-63: Owner-side org plugin administration guide

## 07-cross-platform-external/support-chat-and-cowork.md

- lines 8-8: audit: chat/Cowork merge says nothing about plugins
- lines 10-89: end-user feature tour, rollout, usage and Cowork migration notes; nothing about building, adding or installing marketplace plugins

## Kept under doubt

- `01-plugins-core/host-marketplace.md` lines 151-151: Bullet sits under a private-marketplace intro (line 148, kept with it), but KEEP_MARKETPLACE_ON_FAILURE also helps when a public remote is unreachable
- `01-plugins-core/install.md` lines 242-245: Kept under the private-marketplace heading (237-239) for SSH/known_hosts and owner/repo SSH-vs-HTTPS probe rules that also govern public GitHub clones
- `02-mods/mod-reference.md` lines 425-427: built-in sec-default guard loads under managed settings or Team/Enterprise login; may affect how a public mod behaves for some users, but is admin-oriented
- `03-components/hooks.md` lines 251-251: Mixes cloud-session plugin/hook carry-over (possibly relevant to users) with self-hosted runner and managed-tier details (not relevant)
- `03-components/skills.md` lines 100-150: First-skill tutorial teaches SKILL.md authoring and testing, useful for plugin skills, but uses the personal ~/.claude/skills location
- `03-components/skills.md` lines 418-435: Frontmatter portability outside Claude Code (claude.ai upload, Skills API); relevant only if the maintainer also targets Claude app distribution of the same skills
- `03-components/statusline.md` lines 1197-1204: Script exit-code/hang behaviour is described for the main status line; unclear if it applies the same way to a plugin-shipped subagentStatusLine
- `03-components/sub-agents.md` lines 991-1002: Output scanning of subagent reports: may help a maintainer debug plugin agent reports, but is runtime behavior rather than authoring
- `04-settings-admin/settings-reference.md` lines 691-707: outputStyle is general, but it is how a user selects an output style a plugin ships; kept as possibly relied on
- `04-settings-admin/settings-reference.md` lines 3279-3297: verbose setting kept because it is suggested for debugging hooks/MCP servers, which a plugin maintainer may use; marginal
- `04-settings-admin/settings-reference.md` lines 3777-3794: disableSkillShellExecution can disable a plugin skill's inline shell; kept as a debugging aid for maintainers but it is a user/policy setting
- `05-cli-diagnostics/changelog.md` lines 1583-1583: MCP tool description length limit: matters only if a marketplace plugin ships an MCP server; kept with its 1685 counterpart
- `05-cli-diagnostics/changelog.md` lines 1728-1728: /plugin Errors tab removing a failed marketplace on Enter: user-side UI fix, unclear if a third-party user relies on it
- `05-cli-diagnostics/changelog.md` lines 5877-5880: 2.1.216 heading kept only because its bug-fix list continues into the next chunk; drop if no entry there passes
- `05-cli-diagnostics/changelog.md` lines 5900-5901: 2.1.216 bug-fix heading kept for entries continuing in the next chunk; drop if none pass
- `05-cli-diagnostics/changelog.md` lines 6612-6612: dependency version pins with a marketplace added as a local git-backed folder: local-folder marketplace, but maintainers may test this way before publishing
- `05-cli-diagnostics/changelog.md` lines 9106-9106: CLAUDE_PLUGIN_ROOT fix for local-marketplace plugins: local distribution, but the maintainer may add the repo locally as a marketplace while testing
- `05-cli-diagnostics/errors.md` lines 4369-4385: archive plugin source with sha256 pin; usable from a GitHub-hosted marketplace only if the archive URL is e.g. a GitHub release asset, otherwise a non-GitHub host
- `05-cli-diagnostics/troubleshoot-install.md` lines 1263-1265: Keychain log-out step, kept only for its statement that /logout removes plugin sensitive values (user must re-enter plugin secrets); heading 1233 kept for context
- `07-cross-platform-external/platform-support.md` lines 17-17: third-party model provider Desktop feature matrix may or may not restrict plugin features

## Rewrite of 2026-11-08

On 2026-11-08 the 46 files of 500 lines or fewer were rewritten for Claude as their reader. After this rewrite those 46 files are no longer line-for-line copies of the official pages; the line numbers in the sections above refer to the files as downloaded on 2026-11-07, not to the rewritten files. The 18 files over 500 lines were not rewritten and remain byte-identical to the pruned copies of 2026-11-07: `01-plugins-core/` `cli-reference.md`, `components.md`, `manifest-reference.md`, `plugin-evals.md` and `troubleshooting.md`; `02-mods/` `mod-events.md` and `mod-interface.md`; `03-components/` `channels-reference.md`, `hooks-guide.md`, `hooks.md`, `mcp.md`, `skills.md` and `sub-agents.md`; `04-settings-admin/` `permissions.md` and `settings-reference.md`; `05-cli-diagnostics/` `changelog.md` and `errors.md`; `07-cross-platform-external/` `platform-skills-best-practices.md`.

### What changed in every rewritten file

- Prose rewritten in a directive voice addressed to Claude. Meaning, conditions, caveats and version requirements were kept; code blocks, tables, schemas, examples and notes were kept verbatim, except two anchors corrected in `01-plugins-core/dependencies.md` and `04-settings-admin/env-vars.md`.
- The `Documentation Index` block at the top was replaced by a `## Contents` list of the file's headings, and its source URL moved to a `## Documentation References` section at the end, which also lists the other official pages the file links to. Links to official pages inside the text were kept.
- Each rewrite was checked against its original by a separate verifier; the wording drifts it found were restored to the original meaning (for example, the six headings of `04-settings-admin/settings.md`).

### File-specific changes

- `01-plugins-core/overview.md`, `02-mods/mod-gallery.md`: the text descriptions first added under the 17 images were replaced on 2026-11-09 by pointers to local copies; see Image assets below.
- `02-mods/mod-overview.md`: a duplicated description of the recording was removed.
- `02-mods/mod-create.md`, `02-mods/mod-reference.md`: four corrections where the official pages lag Claude Code 2.1.319, each marked in the text with the evidence (binary, bundled types, changelog or a `claude plugin test` run): the wording and answers of the hot-reload question (changed in 2.1.304); a failed hook of a mod Claude wrote coming back to Claude as a notice; `next.error.kind` declared only as `'throw' | 'timeout'` with no `cause` field, and re-entry not reaching `.catch`; the `mobile` render surface missing from the official tables.
- `02-mods/mod-api.md`, `02-mods/mod-reference.md`, `02-mods/mod-create.md`: 16 sections whose content the built-in `plugin-authoring` skill of Claude Code 2.1.319 holds in full were shortened to a pointer: load that skill and search its `claude-code.d.ts` for the named types, or read the named section on the official page. Headings were kept, and facts the skill does not hold stay in the text (the `Box` border styles table, the telemetry `{ to: 'collector' }` validation rule, confirmed on 2.1.319, and the calling-hook context of methods added in `engine.create`). Sections shortened: in `mod-api.md`, the intro, the `session.start` note, Send one prompt (its `/triage` code block replaced by a one-line description), What a `model.complete` hook receives, Start a turn from a background job and Stop background work; in `mod-reference.md`, the Events intro, Turns, Other mods, Telemetry, Settings hook events, Mods API calls and `Box` border styles; in `mod-create.md`, How the example mod works and Get type definitions for your version.

## Image assets of 2026-11-09

- The 29 images of the official pages (16 PNG screenshots and 13 SVG diagrams) are stored as PNG files in the skill's `assets/` folder, named after the official file, because Claude's Read tool shows PNG and JPG images but reads an SVG as XML text. The SVG diagrams were rendered to PNG; each copy was checked against the official file (pixel-identical for the PNGs, same aspect ratio and only antialiasing differences for the rendered SVGs).
- Each image keeps its official Markdown line and alt text. Under it, one added line points to the local copy: `> **View the image** [`assets/<name>.png`](../../assets/<name>.png) **to** <what the image shows>.`
- In `01-plugins-core/overview.md` and `02-mods/mod-gallery.md`, that line replaces the longer text description added on 2026-11-08; the summary line at the top of `mod-gallery.md` now names the `assets/` folder instead of the descriptions.
- In the other six files (`plugin-evals.md`, `mod-interface.md`, `channels-reference.md`, `hooks.md`, `platform-skills-best-practices.md`, `platform-skills-overview.md`), the pointer lines are the only change; nothing was removed.
