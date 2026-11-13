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
- The live `PRIVACY.md` for the structure.

## Placeholders

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{effectiveDate}}` | Date of this version, written out | The day of the change |
| `{{marketplaceDisplayName}}`, `{{repositoryHost}}`, `{{marketplaceName}}` | Marketplace | `marketplace.json` and the repository |
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
4. Set each plugin's `privacyPolicyUrl` to the policy's `https://` URL on `main`.
5. Run the checks.

## Rules

Official:

- The policy explains collection, usage and retention, and is reachable from `privacyPolicyUrl`.

This repository:

- One root policy for all plugins (`ADR_2026-11-05_plugins-share-one-root-privacy-policy`); each README keeps its own list of destinations.
- The effective date changes with each update.

## Checks

- Every host named in a plugin README's "What this plugin runs and sends" appears in a row, and every row's plugins exist.
- Every policy link opens.
- `grep -n '{{\|<!--' PRIVACY.md` returns nothing.

## Never

- Never state that nothing is collected unless the code shows it.
- Never paraphrase an operator's statement as a quote.
