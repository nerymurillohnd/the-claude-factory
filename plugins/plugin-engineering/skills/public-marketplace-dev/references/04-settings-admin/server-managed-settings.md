# Configure server-managed settings

> Covers how an organization configures Claude Code centrally through server-delivered settings, without device management infrastructure. This pruned copy keeps only what happens when a `claude plugin` command cannot show the approval dialog, and how server-managed settings behave in Cowork.

## Contents

- [Settings delivery](#settings-delivery)
  - [Security approval dialogs](#security-approval-dialogs)
    - [Approval memory](#approval-memory)
- [Platform availability](#platform-availability)
- [Documentation References](#documentation-references)

## Settings delivery

### Security approval dialogs

#### Approval memory

Claude Code can't always show the approval dialog. Each case below states which settings apply when it can't, and when the user next sees the dialog:

* **A `claude plugin` command that prints to a terminal but can't read from the keyboard**: when Claude Code doesn't wait for the settings fetch at startup, the command doesn't apply the delivered settings. Without [cached settings](https://code.claude.com/docs/en/server-managed-settings#fetch-and-caching-behavior), a command that changes plugins or marketplaces [stops with an error](https://code.claude.com/docs/en/errors.md#managed-settings-need-your-approval). With cached settings, it runs with the last-approved settings. The dialog appears the next time the user runs `claude` in a terminal.

  The command can't read from the keyboard when its input is piped or redirected and, on macOS and Linux, it also can't open `/dev/tty`. When its output is piped or redirected too, the run is non-interactive instead, and the delivered settings apply for that run only.

## Platform availability

In a [Cowork](https://claude.com/docs/cowork/overview) session in the Claude Desktop app, Claude Code doesn't fetch server-managed settings from the claude.ai admin console, even when the user signs in with a Team or Enterprise account. [Where and when a policy applies](https://code.claude.com/docs/en/managed-settings.md#where-and-when-a-policy-applies) covers which policy reaches Cowork sessions on the user's machine and remote Cowork sessions. claude.ai still applies the organization's [`strictKnownMarketplaces`](https://code.claude.com/docs/en/settings-reference#strictknownmarketplaces) and [`blockedMarketplaces`](https://code.claude.com/docs/en/settings-reference#blockedmarketplaces) lists itself when a Cowork user adds a marketplace from a git repository on claude.ai or from **Customize** in Cowork. [How restrictions work](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install) describes that check.

## Documentation References

- Source page: https://code.claude.com/docs/en/server-managed-settings (server-delivered settings: delivery, approval dialogs, fetch and caching, platform availability)
- https://code.claude.com/docs/en/errors.md (error reference, including "managed settings need your approval")
- https://claude.com/docs/cowork/overview (Cowork in the Claude Desktop app)
- https://code.claude.com/docs/en/managed-settings.md (deploying managed settings and where each policy applies)
- https://code.claude.com/docs/en/settings-reference (every settings key, including `strictKnownMarketplaces` and `blockedMarketplaces`)
- https://code.claude.com/docs/en/plugins/org.md (organization plugin controls and how marketplace restrictions work)
