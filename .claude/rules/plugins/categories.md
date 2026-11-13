---
paths:
  - "plugins/*/.claude-plugin/plugin.json"
  - "plugins/*/README.md"
  - ".claude-plugin/marketplace.json"
  - "/README.md"
---

# Plugin categories

Users browse the marketplace by category: the root README catalog groups plugins by it.

## Choose the category

- Give each plugin one category, chosen by what users install it for, not by the component types it ships.
- Classify a mod, hook or MCP plugin by its purpose like any other plugin: the catalog's Includes column already shows its component types.
- When no category fits, propose a new one to the owner instead of stretching an existing one.
- Set it in `metadata.category` of `plugin.json`, and give the plugin's `marketplace.json` entry, README badge and root catalog row the same category.

## Categories

| id | Title | Scope |
| :-- | :-- | :-- |
| `development` | 🛠️ Development | Write, refactor, review and ship code faster |
| `productivity` | ⚡ Productivity | Everyday workflows, planning and knowledge work |
| `automation` | 🤖 Automation | Hooks, agents and pipelines that run work for you |
| `monitoring` | 📈 Monitoring | Observability, usage tracking and audit trails |
| `testing` | 🧪 Testing & Quality | Tests, audits, linting and quality gates |
| `security` | 🛡️ Security | Guardrails, secret hygiene and security reviews |
| `documentation` | 📚 Documentation & Writing | Docs, changelogs, records and written content |
| `data` | 📊 Data & Analytics | Databases, data processing and reporting |
| `design` | 🎨 Design & Frontend | UI, accessibility and visual work |
| `devops` | 🚀 DevOps & Deployment | CI/CD, infrastructure, releases and monitoring |
| `integrations` | 🔌 Integrations | MCP servers and connectors to external services |
| `language-support` | 🧠 Language Support | LSP servers and code intelligence for specific languages |
| `learning` | 🎓 Learning | Output styles and skills that teach as they work |

- Copy the emoji and title exactly: the catalog headings, their anchors and the README badges are built from them.

## Use the skills

- When setting or changing a published plugin's category, load the `plugin-versioning` skill: the change edits `plugin.json`, so the plugin needs a new version.
- When writing a README badge, a catalog row or a new category's catalog section, load the `docs-maintenance` skill; for a new plugin, follow its New plugin event.
