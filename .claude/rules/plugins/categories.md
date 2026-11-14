---
paths:
  - "plugins/*/.claude-plugin/plugin.json"
  - "plugins/*/README.md"
  - ".claude-plugin/marketplace.json"
  - "/README.md"
---

# Plugin categories

- Give each plugin one category from the table, chosen by what users install it for, not by its component types.
- Propose a new category to the owner when none fits, instead of stretching one.
- Use the same category in `metadata.category` of `plugin.json`, the `marketplace.json` entry, the README badge and the root catalog row.
- Copy each emoji and title exactly: the catalog headings, anchors and badges are built from them.
- Change a published plugin's category with the `plugin-versioning` skill, because it changes `plugin.json`.

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
