# Security

What to audit in every instruction, script and asset of a skill, and how severe a security finding is.

## What to audit

Treat a skill like installed software: it can make Claude run commands, read files and reach the network \[PL\]. Audit every instruction, script and asset for what it would make Claude do \[PL\]\[SD\].

- **Network.** Network calls, or content fetched from an external URL that the model then follows; fetched content may carry instructions and is untrusted \[PL\]\[SD\] `req`.
- **Reads outside the skill and the project.** Credentials, keys, `~/.ssh`, `.env`, browser or shell history \[SD\] `req`.
- **Data leaving the machine.** Anything sent to an external system \[SD\] `req`.
- **Unannounced actions.** Tool calls, file operations or commands the `description` doesn't announce \[SD\] `req`.
- **Shell injection** through an argument inside a `!` command ([claude-code-features.md](claude-code-features.md#dynamic-context)) \[SD\] `observed`.
- **Over-broad pre-approval** through `allowed-tools` ([claude-code-features.md](claude-code-features.md#substitutions-and-pre-approved-tools)) \[SD\] `rec`.

## Severity of a security finding

\[SD\]: high when the action doesn't match the skill's `description`. When it does (a deploy skill that uses the network), the skill must state it as a requirement, and it is a finding only if the skill doesn't.
