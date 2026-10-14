# Changelog

All notable changes to **Prompt Writer** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Writes the complete text of a system prompt, skill, slash command, agent or `CLAUDE.md` in that file's own format. When it is unclear whether you want that file or a prompt so Claude creates it, Claude asks first.
- Placeholders follow what fills them: Claude Code skill and command arguments, an application's template fields, or fields you fill by hand, named in the reply.
- The design notes name anything Claude added beyond your request.
- Claude works out what you want and why from what it knows of you (this conversation, your memory, past conversations it can see, your projects), and asks only about intent, in plain words, never about technical choices.
- For complex or step-by-step work you get the first prompt and an invitation to come back with its output, so Claude can recommend the follow-up.
- Skills that would help the task are named inside the prompt and in the advice that comes with it.
- Follow-ups: bring back what a prompt produced and Claude checks it against your goal, tells you what worked and what did not, then revises the prompt or writes the next one; every delivery ends with an invitation to come back if the result misses.
- Built-in lessons from real prompt-writing sessions, read before clarifying a request.
- For a model outside the built-in guidance, Claude recommends the closest covered one, or writes with the general principles and marks it `other`.

### Changed

- The skill now starts only when you run `/prompt-writer:prompt-writer`: asking for a prompt in plain words no longer starts it, so begin your request with the command.
- Model guidance: Opus 5.5 is the default recommendation with Fable 5.1 for the most demanding work, Opus 5 is marked legacy, and the Mythos 5.1 model ID is listed.

### Fixed

- The skill states up front that it writes a prompt for you to run in another session; a request phrased as an order is the goal of that prompt, not an instruction to carry out.
- Claude reads the built-in guidance before it recommends a model, effort or approach.
- A skill, slash command or agent file keeps its own frontmatter instead of being wrapped in the prompt header.
- The effort field, the language the target model answers in, nested code fences and the file names of chained prompts now follow clear rules.
- Opus 5.5 prompts apply the Opus 5 patterns by default, and the guidance on verifier roles no longer contradicts itself.
- Sampling parameters: non-default `temperature`, `top_p` and `top_k` are documented as rejected on all four covered models.
- Asking Claude to write a prompt and run it gets only the prompt, with a note to run it in a new session; Claude does not carry out its task in the same session.
- A prompt for a model outside the built-in guidance keeps the safety, agentic and format guidance its case needs.
- Clear rules for when you get one prompt, a first prompt of several, or a fixed chain of stages.
- You paste only the prompt body; the header stays as your record, and the body states the reply language when it matters.
- A system prompt is delivered as plain text, without the prompt header.
- When live documentation contradicts the built-in guidance, Claude follows the documentation and explains the difference in the design notes instead of asking you.
- Prompts for unattended runs say which visible actions, such as pushing or sending, the run may take on its own.
- Audits list the problems found before the fixed prompt, and Claude may ask where you will use the prompt.
- Writing a prompt that builds an evaluation suite is in scope; the skill does not build test suites for its own prompts.
- Reference files are linked with paths relative to the skill, as the skill format documents, wherever the skill asks Claude to read one.
- The source list adds the official Agent Skills pages (Claude Platform and agentskills.io) for checking skills you ask for, and drops a model page outside the built-in guidance.

## [0.1.1] - 2026-10-13

### Fixed

- The skill now reads its reference files from exact paths that resolve in Claude Code and in the Claude app, so Claude no longer searches the file system for them or fails to read them.
- The skill states its scope up front: it always delivers a prompt and never carries out the task the prompt describes, including when the requested prompt is a slash command, a system prompt or skill instructions.

## [0.1.0] - 2026-10-13

### Added

- `prompt-writer` skill: turns a goal, idea or draft into one copy-ready prompt for Claude Fable 5.1, Opus 5.5, Opus 5 or Sonnet 5.5. It clarifies intent with questions that each carry a recommendation, checks current official facts the prompt depends on, applies the target model's documented guidance, and delivers the prompt with a short header plus the recommended model, effort and session setup.
- Works on new prompts, drafts to refine, existing prompts to audit and prompts to migrate to another target model, and saves the prompt to a file when you ask for one.
- Built-in references for prompting principles, agentic patterns, reliability and safety, and model selection and configuration, with a drift report when live official documentation contradicts them.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/prompt-writer--v0.1.1...HEAD
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/prompt-writer--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/prompt-writer--v0.1.0
