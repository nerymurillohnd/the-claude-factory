# 🔐 Security policy

Plugins can run hooks, scripts and MCP servers on your machine, so we treat security reports as our top priority.

## Supported versions

Only the **latest released version** of each plugin receives security fixes. Update with:

```bash
claude plugin update <plugin>@the-claude-factory
```

## Reporting a vulnerability

> [!CAUTION]
> Please **do not** open a public issue for security problems.

Report privately through GitHub: **[Report a vulnerability](https://github.com/nerymurillohnd/the-claude-factory/security/advisories/new)**.

Include, if you can:

- The plugin and version affected.
- What an attacker could do, and under which conditions.
- Steps or a proof of concept to reproduce it.
- Any suggested fix.

## What to expect

| Step                                            | Target                                            |
| :---------------------------------------------- | :------------------------------------------------ |
| Acknowledgement of your report                  | within **3 business days**                        |
| Initial assessment and severity                 | within **7 days**                                 |
| Fix released for confirmed critical/high issues | as fast as possible, typically within **14 days** |

We'll keep you updated, credit you in the release notes if you wish, and publish a security advisory once a fix is available.

## In scope

- Code, hooks, scripts and MCP/LSP configurations shipped in [`plugins/`](./plugins).
- The marketplace catalog (`.claude-plugin/marketplace.json`) and this repository's automation.

## Out of scope

- Vulnerabilities in Claude Code, the Claude apps or Anthropic services — report those to [Anthropic](https://www.anthropic.com/responsible-disclosure-policy).
- Vulnerabilities in third-party services a plugin connects to — report those to the service owner.
