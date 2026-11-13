---
name: docs-maintenance
description: Writes, updates and audits The Claude Factory's documents from their templates, such as each plugin's README.md, CHANGELOG.md, LICENSE and NOTICE.txt, the root README.md and CHANGELOG.md, and the root policy files (CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, PRIVACY). Use before and while creating, editing, reviewing or auditing any of these documents, and whenever another skill says to write a document with it, even for a one-line fix.
---

# Docs maintenance

Everything these documents say reaches third parties: a plugin's README tells a stranger what runs on their machine, a changelog tells them what an update breaks, and a license or a notice carries legal terms. Each document has a fill procedure and a template here, checked against the official sources, so that every document comes out the same way whoever writes it. Write each one from its procedure and its template, never from memory.

## Who writes

- You write the documents, following the procedure and the template in the table below.
- The one exception is a plugin README written in full for the first time, such as a new plugin's: launch the `plugin-readme-writer` subagent for it, because the README is long, has many rules, and benefits from its own context. Brief it as [governance.md](references/governance.md) says. Where no subagent is available, as in a cloud thread of a Claude Project, write it yourself from the same procedure.
- Versions, change types, renames, removals and releases are decided by the `plugin-versioning`, `plugin-releases` and `plugin-catalog-changes` skills. They call this skill for the documents they need; take their decisions as given.

## Documents

| Document | Procedure | Template |
| :-- | :-- | :-- |
| `plugins/<plugin>/CHANGELOG.md` | [changelog.md](references/documents/changelog.md) | [CHANGELOG-template.md](assets/CHANGELOG-template.md) |
| Root `CHANGELOG.md` | [marketplace-changelog.md](references/documents/marketplace-changelog.md) | [marketplace-changelog-template.md](assets/marketplace-changelog-template.md) |
| `plugins/<plugin>/README.md` | [plugin-readme.md](references/documents/plugin-readme.md) | [plugin-readme-template.md](assets/plugin-readme-template.md) |
| Root `README.md` | [root-readme.md](references/documents/root-readme.md) | [root-readme-template.md](assets/root-readme-template.md) |
| Root and plugin `LICENSE` | [license.md](references/documents/license.md) | [LICENSE-template.md](assets/LICENSE-template.md) |
| `plugins/<plugin>/NOTICE.txt` | [notice.md](references/documents/notice.md) | [NOTICE-template.md](assets/NOTICE-template.md) |
| `CODE_OF_CONDUCT.md` | [code-of-conduct.md](references/documents/code-of-conduct.md) | [CODE_OF_CONDUCT-template.md](assets/CODE_OF_CONDUCT-template.md) |
| `CONTRIBUTING.md` | [contributing.md](references/documents/contributing.md) | [CONTRIBUTING-template.md](assets/CONTRIBUTING-template.md) |
| `SECURITY.md` | [security.md](references/documents/security.md) | [SECURITY-template.md](assets/SECURITY-template.md) |
| `SUPPORT.md` | [support.md](references/documents/support.md) | [SUPPORT-template.md](assets/SUPPORT-template.md) |
| `PRIVACY.md` | [privacy.md](references/documents/privacy.md) | [PRIVACY-template.md](assets/PRIVACY-template.md) |

## How to write a document

1. Read [governance.md](references/governance.md) in full: the values only the owner can give, the checks, and the conventions every document follows.
2. Read the document's procedure in full, then its template. Each procedure says what the document produces, its sources, what each placeholder means and where its true value comes from, its rules and its checks.
3. Take every value from the repository's files, the calling skill's decisions or the owner. Ask the owner for a value only the owner can give; never invent one.
4. Write the document, then run the checks in its procedure and in governance.md, and show their raw output.

## Events that call for documents

The changes the lifecycle skills handle (a plugin change, a new version, a rename, a removal, a withdrawn version) start from those skills. These other events start here; read the event's file and follow it:

| Event | It applies when | Reference |
| :-- | :-- | :-- |
| Repository foundation | The repository's own documents are created or rebuilt | [repository-foundation.md](references/events/repository-foundation.md) |
| New plugin | A plugin directory with its `plugin.json` appears and is listed in `marketplace.json` | [new-plugin.md](references/events/new-plugin.md) |
| Third-party material changes | Another author's material is added to a plugin, updated or removed | [third-party-material.md](references/events/third-party-material.md) |
| Data handling changes | A plugin starts or stops calling a remote service, collecting data or keeping files on the user's machine | [data-handling.md](references/events/data-handling.md) |
| The owner changes a policy | A copyright line, reporting channel, security policy, support channel or contribution process changes | [policy-change.md](references/events/policy-change.md) |
| Audit or review | Someone asks whether the documentation is correct, or drift is suspected | [audit.md](references/events/audit.md) |
| A small fix | A typo, a broken link or an outdated sentence | [small-fix.md](references/events/small-fix.md) |

[commands.md](references/commands.md) says what each documentation command checks and what it doesn't.
