---
status: accepted
date: 2026-11-19
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# authoring-skills replaces its configuration file with a credentials-only security standard

## Scope

`plugins/skills-engineering/skills/authoring-skills/SKILL.md` standard 12, and the removed `references/phase-2-config-and-security.md`.

## Context and problem statement

The owner removed the configuration, state and security reference on 2026-11-19, and asked for a security standard in `SKILL.md`. The standard keeps credential values out of every file of a skill, allows credential names, and pushes back when the user insists on a value. Asked what to keep from the removed file, he chose credentials only.

## Decision drivers

- No credential value may ever reach a skill's files.
- Naming a credential's variable stays allowed.

## Considered options

- **Credentials only in standard 12**: chosen.
- **Fold userConfig with sensitive values, the fetched-content rule and the state locations into the standard**: rejected by the owner.

## Decision outcome

Chosen option: **credentials only**.

### Consequences

- Good, because every run reads the rule in `SKILL.md`, with what to do when the user insists.
- Bad, because guidance on `userConfig` with `"sensitive": true`, on treating fetched content as data, and on state in claude.ai and cloud sessions is gone. The state of a plugin in `${CLAUDE_PLUGIN_DATA}` survives as a gotcha in the scripts file.

## More information

Released as skills-engineering 0.2.0 on 2026-11-19.
