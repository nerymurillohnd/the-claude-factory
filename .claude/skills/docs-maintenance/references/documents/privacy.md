# Privacy policy

How to create `PRIVACY.md` from `assets/PRIVACY-template.md`.

## Produces

`PRIVACY.md` at the repository root: one policy for every plugin, linked from each `plugin.json` `privacyPolicyUrl` and from each plugin README's "What this plugin runs and sends".

## When

- When the marketplace publishes its first plugin that collects user data or connects to a remote service.
- In the same change as any plugin that adds, removes or changes a destination.

## Sources

Read 2026-11-10:

- No official template exists: GitHub defines no privacy file among community health files.
- Anthropic Software Directory Policy, section 3.A (quoted in `ADR_2026-11-05_plugins-share-one-root-privacy-policy`): "Developers of Software that collects user data or connects to a remote service must provide a clear, accessible privacy policy link explaining data collection, usage, and retention."
- Claude Code docs `plugins/manifest-reference`: `privacyPolicyUrl` is a directory listing field, an `https://` URL.

## Placeholders

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{effectiveDate}}` | Date of this version, written out | The day of the change |
| `{{marketplaceDisplayName}}` | Marketplace display name | The owner (`governance.md`), as the root README and CHANGELOG state it |
| `{{repositoryHost}}`, `{{marketplaceName}}` | The repository host path and the marketplace `name` | The repository and `marketplace.json` |
| `{{maintainerName}}`, `{{maintainerProfileHost}}`, `{{maintainerProfileUrl}}` | Who is responsible | The maintainer |
| `{{authorCollection}}` | What the author receives, how it is used and kept | The plugins' code |
| `{{disclosureSection}}` | The README section that lists destinations | `What this plugin runs and sends` |
| `{{localFiles}}` | Files plugins keep locally | The plugins' hooks and scripts |
| `{{serviceName}}`, `{{serviceHost}}`, `{{servicePlugins}}`, `{{serviceData}}`, `{{servicePolicyTitle}}`, `{{servicePolicyUrl}}` | One row per third-party destination | Each plugin's README and code; the operator's site |
| `{{childrenStatement}}` | Whether the plugins target children | The audience |
| `{{policyHistoryUrl}}`, `{{issuesUrl}}` | History and contact | The repository |

## Procedure

1. Inventory every destination: search each plugin's hooks, scripts, MCP configurations and README for hosts.
2. Copy the template to `PRIVACY.md`, fill every value, delete each instruction comment.
3. Write one row per destination; for an operator with no published policy, say so with the date checked and quote what it states.
4. Check that each plugin's `privacyPolicyUrl` is the policy's `https://` URL on `main`; set it where it isn't.
5. Run the checks.

## Rules

Official:

- The policy explains collection, usage and retention, and is reachable from `privacyPolicyUrl` (Anthropic Software Directory Policy, section 3.A). Claude Code ignores `privacyPolicyUrl` at load time; Anthropic's directory reads it, and its security scan looks for destinations a plugin does not disclose.
- Permission rules apply to the tool calls Claude makes for a plugin, not to what its hooks, MCP servers or mods run on their own: a `Read(.env)` deny doesn't stop a mod's `$.fs.read`, and a `WebFetch` deny doesn't stop its `$.http.fetch` (code.claude.com/docs/en/plugins/mods/admin).
- Claude Code's own traffic (model API, telemetry, error reporting, updates) is Anthropic's: point to Anthropic's Privacy Policy for it and don't restate it.

This repository:

- One root policy for all plugins (`ADR_2026-11-05_plugins-share-one-root-privacy-policy`); each README keeps its own list of destinations.
- The effective date changes with each update.
- Build the inventory from the plugins' files, not from their READMEs:
  - destinations: remote MCP servers (`url` in `.mcp.json` or `mcpServers`); local MCP servers and package launchers (`npx`, `uvx`) that reach a registry; hook scripts (search for `curl`, `wget`, `fetch`, `http`, `urllib`, `requests`, `git clone`, `npm`, `npx`, `pip`, `gh`); HTTP hooks (their `url`) and prompt or agent hooks (the model); skills, agents and commands that use `WebFetch`, `WebSearch`, `gh`, `curl` or fixed URLs; dependencies installed from a registry
  - files kept on the machine: writes to the plugin's data directory (the `CLAUDE_PLUGIN_DATA` variable), `TMPDIR`, `/tmp` or elsewhere in hooks, scripts, mods and MCP servers, with what each holds and when it's deleted
  - a tool the user supplies and the plugin only drives (the user's `gh` login, language servers, linters) is not a plugin destination unless the plugin directs data to a named service.
- "The author never sees it and keeps none of it" holds only while no plugin relays data through an author-run server.

## Checks

- Every host named in a plugin README's "What this plugin runs and sends" appears in a row, and every row's plugins exist.
- Every policy link opens.
- `grep -n '{{\|<!--' PRIVACY.md` returns nothing.

## Never

- Never state that nothing is collected unless the code shows it.
- Never paraphrase an operator's statement as a quote.
