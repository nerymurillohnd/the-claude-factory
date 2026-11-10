# The owner changes a policy

This file is part of the docs-maintenance skill. Follow `references/governance.md` for briefing, checking and the rules that apply to every event, and `references/commands.md` for what each command named here tells you. "Stage 1, 2, 3" means order; subagents named in the same stage run in parallel, launched in one message, and a stage starts only when the previous one has returned.

Send only the owner of the affected document, with the new value:

| Change | Subagent |
| :-- | :-- |
| Copyright year or holders | `license-writer`, then `notice-writer` for any notice that repeats the holder |
| Conduct reporting channel or enforcement policy | `code-of-conduct-writer` |
| Vulnerability reporting channel, supported versions or response targets | `security-writer` |
| Issue forms or how users report problems | `contributing-writer`, then `support-writer` |
| Support channels or guides | `support-writer` |
| How the marketplace is added or its plugins installed | `marketplace-readme-writer` |

Then check the root README: if it states the changed policy, add `marketplace-readme-writer`.
