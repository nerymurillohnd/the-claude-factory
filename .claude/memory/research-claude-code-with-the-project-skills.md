---
name: research-claude-code-with-the-project-skills
description: Before answering anything about Claude Code or plugin commands, load cc-docs-research and plugin-engineering:cli-commands-guide, and report gaps as "not documented", never as "not possible".
metadata:
  type: feedback
---

Load `anthropic-skills:cc-docs-research` and `plugin-engineering:cli-commands-guide` before the first answer about Claude Code behavior, settings or any `claude plugin` command, including `claude plugin eval`; then follow their procedure: the installed binary's `--help`, the full official page downloaded locally, the changelog, and every page the topic spans.

**Why:** on 2026-11-13 an answer about eval effort used only a few MCP searches, skipped both skills, and stated "it can't be done" where the evidence only showed "not documented". The owner had to push back to get the research done.

**How to apply:** when a search finds nothing, say which sources were read and that the feature is not documented there; list what remains unverified (for example, which `CLAUDE_CODE_*` variables an eval run inherits) and the cheapest check that would settle it.
