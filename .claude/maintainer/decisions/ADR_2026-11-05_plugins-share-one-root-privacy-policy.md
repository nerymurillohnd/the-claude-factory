---
status: accepted
date: 2026-11-05
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# All plugins share one privacy policy in a root PRIVACY.md

## Scope

`PRIVACY.md` at the repository root, the `privacyPolicyUrl` field of every `plugins/<plugin>/.claude-plugin/plugin.json`, and the link to it from each plugin README's "What this plugin runs and sends" section. Per-plugin disclosure of what a plugin runs and sends stays in each README.

## Context and problem statement

Anthropic's [Software Directory Policy](https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy), section 3.A, says: "Developers of Software that collects user data or connects to a remote service must provide a clear, accessible privacy policy link explaining data collection, usage, and retention." At least svelte-development (the remote `mcp.svelte.dev` server), github-operations (GitHub and the GitHub MCP server) and prompt-writer (a model call that receives the session transcript) connect to remote services, and several others read public documentation pages. On 2026-11-05 `claude plugin validate --strict` reported `PRIVACY_URL_MISSING` for svelte-development. Nery asked whether an existing file already covers privacy, and whether the content should go into one of them instead of a new file.

## Decision drivers

- One stable `https://` URL for the `privacyPolicyUrl` of every plugin.
- The policy must state collection, usage and retention, and link the third parties' own policies.
- Existing files must keep their purpose: `LICENSE` stays the unmodified MIT text, and GitHub surfaces `SECURITY.md` as the security policy.

## Considered options

- **A new root `PRIVACY.md`, linked from every plugin**: chosen.
- **A Privacy section in each plugin README**: rejected because 21 copies would drift, and the README sections already disclose destinations but not usage, retention or third-party policies.
- **A section in `SECURITY.md`**: rejected because that file is for vulnerability reports.
- **A section in the root `README.md`**: rejected because it is the generated catalog page, where a legal section is easy to miss.
- **No policy, only README disclosures**: rejected because the directory policy requires a privacy policy link for plugins that connect to remote services.

## Decision outcome

Chosen option: **a new root `PRIVACY.md`, linked from every plugin**, because it gives all 21 plugins one policy to maintain and one URL, while each README keeps its own list of destinations.

### Consequences

- Good, because a new destination in any plugin changes one file and the plugin's README, not 21 policies.
- Good, because the `privacyPolicyUrl` of every plugin is the same `https://` URL on `main`.
- Bad, because a plugin that adds a remote service must also update `PRIVACY.md`, which nothing checks automatically yet.

## More information

Decided by Nery on 2026-11-05 after reviewing the coverage of `README.md`, `SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` and `LICENSE`. The icon and the other listing fields are recorded in ADR_2026-11-05_every-plugin-ships-a-directory-icon.
