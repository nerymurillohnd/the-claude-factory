---
status: accepted
date: 2026-10-24
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Schemas are strict on every known shape

## Scope

- In scope: `additionalProperties` on every object of `scripts/schemas/`.
- Out of scope: free-form maps whose keys are the user's own: `metadata`, an `mcp_tool` handler's `input`, `settings.subagentStatusLine`.

## Context and problem statement

The manifest schema rejected unknown keys everywhere, while the marketplace schema's rule said to accept them wherever `claude plugin validate` stays silent, and never to tighten those. With one source per shape, one policy must hold. Measured on 2.1.310, the CLI ignores unknown keys in hook handlers, MCP servers, `author`, `owner`, source objects and dependency objects, so a typo there (`onFailre`) passes validation without a message. Which policy?

## Decision drivers

- These schemas check files we author before they reach users.
- A typo the CLI ignores is a bug the user receives.

## Considered options

- **`additionalProperties: false` on every object with a known shape, recording what the CLI does in `x-cli-unknown-keys`**: chosen.
- **Mirror the CLI: `true` where it accepts unknown keys silently**: rejected because then the schema misses exactly the typos nothing else catches.

## Decision outcome

Chosen option: **strict on every known shape**, because where the CLI is silent the schema is the only check.

### Consequences

- Good, because measured: an invented key in a handler, an MCP server, `oauth`, `owner`, a `github` source and a dependency object now fails, while every real file of the repository stays valid.
- Bad, because a field the CLI starts accepting fails here until a schema adds it; each field addition is checked against the changelog and `claude plugin validate --strict` first.

## More information

- Decided by Nery in the session of 2026-10-24, choosing the strict option of the proposal.
- Related: ADR_2026-10-24_one-schema-source-per-shape.
