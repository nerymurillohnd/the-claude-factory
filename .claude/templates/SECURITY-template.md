<!--
  Procedure: .claude/references/security.md
  Values to replace are {{camelCase}}. Instructions are HTML comments: follow each one, then delete it, this one included.
  GitHub requires two things in a security policy: the supported versions and how to report a vulnerability.
  Every other section is optional: keep it only when it states a real commitment.
-->
# 🔐 Security policy

{{securityIntro}}

<!-- securityIntro: one sentence on why security matters for what the project ships, for example that its plugins run hooks, scripts and MCP servers on users' machines. -->

## Supported versions

{{supportedVersionsStatement}}

<!--
  supportedVersionsStatement: which versions receive security fixes, for example "Only the **latest released version** of each plugin receives security fixes.", followed by the update command in a fenced block.
  When versions are supported differently, use a table instead:
  | Version | Supported |
  | :-- | :-- |
  | {{supportedRange}} | ✅ |
  | {{unsupportedRange}} | ❌ |
-->

## Reporting a vulnerability

> [!CAUTION]
> Please **do not** open a public issue, discussion or pull request for a security problem.

Report privately through GitHub: **[Report a vulnerability](https://github.com/{{owner}}/{{repo}}/security/advisories/new)**.

<!-- This link works only after private vulnerability reporting is enabled: Settings, then the security page of the sidebar, then **Enable** next to "Private vulnerability reporting". If the project uses another channel, such as a monitored email address, name that channel here instead; never link a channel that does not reach someone who acts on it. -->

Include, if you can:

- The {{component}} and version affected.
- What an attacker could do, and under which conditions.
- Steps or a proof of concept to reproduce it.
- Any suggested fix.

<!-- To make the private report form ask for these fields, add `.github/VULNERABILITY_REPORT.yml` (issue-form syntax); without it, GitHub's default form asks for a summary, details, proof of concept and impact. -->

## What to expect

| Step                                            | Target                    |
| :---------------------------------------------- | :------------------------ |
| Acknowledgement of your report                  | within **{{ackTarget}}**  |
| Initial assessment and severity                 | within **{{assessTarget}}** |
| Fix released for confirmed critical/high issues | {{fixTarget}}             |

{{disclosureStatement}}

<!-- Keep this section only with targets the maintainers actually commit to; otherwise delete it. disclosureStatement: what the reporter gets, for example updates, credit in the release notes if they wish, and a published security advisory once a fix is available. -->

## In scope

- {{inScope}}

<!-- What this policy covers, one item per bullet: the code, hooks, scripts and server configurations the project ships, and its own automation. -->

## Out of scope

- {{outOfScope}}

<!-- What the project does not control, one item per bullet, each with where to report it instead, for example the platform the project runs on and third-party services it connects to. -->
