# Security policy

How to create `SECURITY.md` from `assets/SECURITY-template.md`.

## Produces

`SECURITY.md` at the repository root. GitHub looks in `.github/`, then the root, then `docs/`, and links it from the Security tab and the community profile.

## When

- When the repository becomes public.
- When the supported versions, the reporting channel, the response targets or the scope change.

## Sources

Read 2026-11-10 (`github/docs` at `f309096`):

- "Adding a security policy to your repository": "add information about supported versions of your project and how to report a vulnerability."
- "Configuring private vulnerability reporting for a repository": owners of public repositories enable it in Settings, on the security page of the sidebar, with **Enable** next to "Private vulnerability reporting" (the page label varies by plan, so it is not quoted here); the default form asks for a summary, details, proof of concept and impact; a `.github/VULNERABILITY_REPORT.yml` (or `.yaml`) customizes it with issue-form syntax, and GitHub shows the default form when it cannot parse it; maintainers can require a CWE and set report limits.
- "Creating a default community health file": file precedence and the account-wide `.github` repository.
- Never invent a reporting mechanism; keep only sections that state a real commitment; give out-of-scope reporters somewhere to go.
- Claude Code docs `plugins/security`: what a plugin can run on a user's machine (for the intro and scope).

## Placeholders

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{securityIntro}}` | Why security matters for what the project ships | The project |
| `{{supportedVersionsStatement}}` | Which versions get fixes, and how to update | The release policy |
| `{{owner}}`, `{{repo}}` | Repository, for the private report link | The repository |
| `{{component}}` | What a report names, such as "plugin" | The project |
| `{{ackTarget}}`, `{{assessTarget}}`, `{{fixTarget}}` | Response targets | Only what the maintainer commits to |
| `{{disclosureStatement}}` | Updates, credit, advisory | The maintainer's practice |
| `{{inScope}}`, `{{outOfScope}}` | What the policy covers, and where to report the rest | The project and its upstreams |

## Procedure

1. Confirm with the owner that private vulnerability reporting is enabled on the repository; the owner enables it in the repository's settings, which a cloud session can't change. Link it only once it is.
2. Copy the template to `SECURITY.md` and fill every value; delete each instruction comment.
3. Delete "What to expect" unless the maintainer commits to its targets.
4. For each out-of-scope item, give where to report it instead.
5. Optionally add `.github/VULNERABILITY_REPORT.yml` to ask for the template's list of details.
6. Run the checks.

## Rules

Official:

- Supported versions and how to report are required content.
- The private report link works only with private vulnerability reporting enabled.

This repository:

- Write the policy per plugin, never as one marketplace version: each plugin has its own `version` and `<plugin>--v<version>` tags.
- Only the latest released version of each plugin receives security fixes; the update command is `claude plugin update <plugin>@the-claude-factory`, and the update applies after a restart or `/reload-plugins`.
- Never say fixes arrive automatically: auto-update is off by default for this marketplace, so users get a fix only when they update.
- Never write the settings path for private vulnerability reporting into the file: it is for the owner, not for readers.
- Out of scope, each with where to report it: Claude Code, Claude and Anthropic's services (Anthropic's security disclosure channel, verified on its site); GitHub's platform (GitHub's security reporting); third-party MCP servers and tools a plugin connects to (their maintainers); flaws that need an attacker who already controls the user's machine or Claude settings; general bugs and questions (`SUPPORT.md`).
- `SECURITY.md`, `SUPPORT.md` and `.github/ISSUE_TEMPLATE/config.yml` state the same private reporting route.
- No copy in `.github/`: it would replace the root file silently.

## Checks

- The repository's Security tab shows the policy, and **Report a vulnerability** opens the form, after the push.
- `grep -n '{{\|<!--' SECURITY.md` returns nothing.

## Never

- Never link a channel nobody reads, or a form that is not enabled.
- Never promise a response time the maintainer does not keep.
