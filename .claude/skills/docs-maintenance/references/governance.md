# Governance

The rules for every documentation task, whatever the document. Read this file in full before you write the first document of a task.

## What this skill doesn't decide

- `plugins/<plugin>/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, except two fields this skill keeps in line with its documents: `license` (the `license.md` procedure) and `privacyPolicyUrl` (the `privacy.md` procedure). The version a release gets, its change types and whether it is breaking: the `plugin-versioning`, `plugin-releases` and `plugin-catalog-changes` skills settle them before a document is written. When a document needs one of these decisions and none was made, stop and run the skill that makes it.
- Commits, pull requests and releases, under the rules in `.claude/CLAUDE.md`.

## Values only the owner can give

Ask the owner for any of these that the files don't already hold; never invent one.

| Document | Owner's values |
| :-- | :-- |
| Plugin and root `CHANGELOG.md` | Release date (from the release); marketplace display name |
| Plugin `README.md` | Plugin emoji; surfaces (`metadata.surfaces`) when not yet set; minimum Claude Code version when neither `engines` nor a changelog entry sets it |
| Root `README.md` | Marketplace display name and emoji |
| `LICENSE` | Copyright year and holders |
| `NOTICE.txt` | Source, exact version and license of each third-party work, when the files don't show them |
| `CODE_OF_CONDUCT.md` | Private reporting channel; enforcement policy, if not the Covenant's |
| `CONTRIBUTING.md` | How the owner triages issues, when it changes |
| `SECURITY.md` | Reporting channel; supported versions policy; response targets and disclosure practice, if any |
| `SUPPORT.md` | Support channels and any response expectations |
| `PRIVACY.md` | Effective date; marketplace display name; maintainer; what the author collects |

## Launching `plugin-readme-writer`

Use it only for a plugin README written in full for the first time. It starts with no context, so the brief is its whole picture:

- **Scenario**: create the README of a new plugin.
- **Target**: `plugins/<plugin>/README.md`.
- **What the plugin does**: in the user's terms, with the paths of its components, and the output of `claude --plugin-dir plugins/<plugin> plugin details <plugin>` so the brief matches the real inventory.
- **Owner values**: every value the table above lists for the plugin README, exactly as the owner gave it.

Leave out what it already knows: the template, its rules, how to format the document. When it ends, read its final message, act on its missing values and on the changes it says other files need, and run the checks below.

## Checks after writing any document

1. `git status --short` shows only the documents the task touched, plus `.claude/agent-memory/` when `plugin-readme-writer` ran.
2. `grep -n '{{' <file>` and `grep -n '<!--' <file>` find nothing, except where the document's procedure keeps them.
3. After a plugin's document changes: `claude plugin validate plugins/<plugin> --strict --profile directory` exits 0.
4. Read the diff: it says what changed, and states nothing the files, the calling skill or the owner didn't give.

## When something gets in the way

- **An official source contradicts a template**: keep the template, and bring the conflict to the owner; a template changes only with the owner's decision.
- **The owner asks for a direct edit** that the procedure would write differently: say once what the procedure requires, then do what the owner decides.

## Conventions that bind every document

They are in `.claude/CLAUDE.md`. The ones that shape documents most often:

- Release dates are UTC, `YYYY-MM-DD`, the day the tag and GitHub Release are created.
- The two surfaces are named **Claude Code** and **Claude**, and no other surface name is used.
- Prerequisites, tools and minimum versions a plugin needs go in its README's Prerequisites section.
- A change limited to a plugin's documentation needs no pull request, unless the owner asks for one.
- The repository is public: no personal, client or business data in any document or memory.
