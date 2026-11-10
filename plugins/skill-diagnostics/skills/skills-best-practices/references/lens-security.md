# Security lens

What the security reviewer checks: everything the skill would make Claude do that reaches the network, reads sensitive files, sends data out, or goes beyond what the description announces.

## Items

Each line names the checklist item from [checklist.md](checklist.md), then the area file and heading that hold the rule, then the rule's bold lead-in. Read the rule there; it is not repeated here.

- `SE-1` · [security.md#what-to-audit](security.md#what-to-audit) · **Network.**
- `SE-1` · [security.md#what-to-audit](security.md#what-to-audit) · **Reads outside the skill and the project.**
- `SE-1` · [security.md#what-to-audit](security.md#what-to-audit) · **Unannounced actions.**
- `SE-2` · [security.md#what-to-audit](security.md#what-to-audit) · **Network.**
- `SE-3` · [security.md#what-to-audit](security.md#what-to-audit) · **Reads outside the skill and the project.**
- `SE-3` · [security.md#what-to-audit](security.md#what-to-audit) · **Data leaving the machine.**
- `SE-3` · [security.md#what-to-audit](security.md#what-to-audit) · **Unannounced actions.**
- `SE-4` · [security.md#what-to-audit](security.md#what-to-audit) · **Shell injection**
- `SE-4` · [security.md#what-to-audit](security.md#what-to-audit) · **Over-broad pre-approval**
- `SE-4` · [claude-code-features.md#dynamic-context](claude-code-features.md#dynamic-context) · **Never put an argument placeholder inside a `!` command.**
- `SE-4` · [claude-code-features.md#substitutions-and-pre-approved-tools](claude-code-features.md#substitutions-and-pre-approved-tools) · **Name the exact command.**
- Severity of every security finding · [security.md#severity-of-a-security-finding](security.md#severity-of-a-security-finding)
- `SU-4` · [surfaces.md#names-and-folders](surfaces.md#names-and-folders) · **A skill folder that is a plugin.**

## Method

1. Read the area file each pointer names at the step that uses it.
2. Read the description first and write down every action it announces.
3. Read every instruction, script and asset in the inventory from its first line to its last, and list every action each one would make Claude take: commands, tool calls, file reads and writes, network requests.
4. Compare that list with the announced actions. An action the description doesn't announce is high severity; an announced one that the skill doesn't state as a requirement is a finding.
5. For each network call or fetched URL, check whether the model then follows the fetched content.
6. For each file read, check whether the path can leave the skill and the project: credentials, keys, `~/.ssh`, `.env`, browser or shell history.
7. For each `!` line, check whether an argument reaches the command; for each `allowed-tools` grant, check what else it would let run.
8. Confirm or reject each script lead on network calls and on reads of credentials or history.
9. When the skill folder holds `.claude-plugin/plugin.json`, read what that plugin adds (agents, hooks, MCP servers) and check that the description announces it.
