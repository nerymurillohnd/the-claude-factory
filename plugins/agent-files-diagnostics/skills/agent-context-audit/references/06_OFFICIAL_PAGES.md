# Phase 6: Official pages to fetch

This is the list that you hand to `docs-researcher` for Phase 6. It fixes the topics the baseline must cover and the page where each starts, so the catalog does not change from run to run. Propose it at Gate 1 with any page the user adds. The URLs were checked on 2026-10-14. If a page has moved, `docs-researcher` finds the replacement on an admitted domain through the Claude Code docs search or the site index, records the new URL, and reports the difference. A topic the listed pages leave open may be settled on another page of an admitted domain, which the researcher records.

## Claude Code

The documentation index is `https://code.claude.com/docs/llms.txt`. Every page below lives at `https://code.claude.com/docs/en/<page>`.

| Page | Topics it must settle |
| :- | :- |
| `memory` | How `CLAUDE.md`, `CLAUDE.local.md`, rules, `AGENTS.md`, and auto memory are discovered, imported, ordered, truncated, and excluded (`claudeMdExcludes`); the maximum import depth; the managed-policy `CLAUDE.md`; the criteria for what belongs in each |
| `claude-directory` | Where each file lives, and the frontmatter fields by file type |
| `sub-agents` | Subagent definitions, their frontmatter, subagent memory, and what loads at startup |
| `output-styles` | Output style files and their frontmatter |
| `scheduled-tasks` | `loop.md`: where it lives and which one wins |
| `settings` and `settings-reference` | Where settings live, and the valid keys that decide which Markdown files load |
| `changelog` | Release notes for the installed version, the four before it, and every newer one |

## Codex

The documentation index is `https://learn.chatgpt.com/llms.txt`. The older `developers.openai.com/codex/...` addresses redirect to `learn.chatgpt.com`, so list the final address.

| Page | Topics it must settle |
| :- | :- |
| `https://learn.chatgpt.com/docs/agent-configuration/agents-md.md` | The discovery order of `AGENTS.override.md`, `AGENTS.md`, and the fallback names; the global and the project chain; the size limit |
| `https://learn.chatgpt.com/docs/config-file/config-reference.md` | The keys that decide what loads: `project_doc_fallback_filenames`, `project_doc_max_bytes`, `projects.<path>.trust_level`, and the `memories` keys |
| `https://learn.chatgpt.com/docs/config-file/config-basic.md` | Where the Codex configuration lives and how its layers combine |
| `https://learn.chatgpt.com/docs/customization/memories.md` | What Codex memories are, when they are injected, and where they are stored |
| `https://github.com/openai/codex/releases` | Release notes for Codex, for the installed version and every newer one (a Codex that is not installed has none to compare) |
