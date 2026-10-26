---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The scaffold writes a plugin's identity, not its README content

## Scope

`.claude/skills/building-plugins/scripts/scaffold-plugin.py` and the assets it fills. Out of scope: the README section set, DEBT-011's open question.

## Context and problem statement

Another session rewrote the scaffold to write README content: an emoji, the minimum Claude Code version, five badges and surface texts, with `--emoji` and `--min-claude-code` required, together with a new README template that settled DEBT-011's section question ahead of Nery's decision on the plugin-docs spec. The call `SKILL.md` documents then exited 2. What should the scaffold fill?

## Decision drivers

- A skill's script does only what is mechanical and known with certainty.
- The minimum Claude Code version depends on the components, which do not exist yet when the plugin is created.
- Creating a plugin and writing its README are different steps of the skill.

## Considered options

- **Identity only**: chosen. The scaffold fills the name, display name, description, category and surfaces; the README is written in the public-ready step, once the components are known.
- **Keep the README-writing scaffold**: rejected because it makes writing decisions at creation and settles an open question without Nery.

## Decision outcome

Chosen option: **Identity only**, because creating and writing are separate steps, and the README's details are known only after the components are written.

### Consequences

- Good, because the scaffold matches the call `SKILL.md` documents, and the validated template and checks work on what it writes.
- Bad, because the emoji, badges and minimum version stay hand work in the README.

## More information

Nery agreed on 2026-10-25 ("SI! ES LA MANERA CORRECTA") after saying the other session's scaffold was complicating everything. Commit `787941c` reverted the scaffold and the README template; `NOTICE-template.txt` stayed and was documented (`a92321d`). The plugin-docs spec (commit `6ef2eed`) stays an open proposal.
