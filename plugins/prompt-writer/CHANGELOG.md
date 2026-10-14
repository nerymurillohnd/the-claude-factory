# Changelog

All notable changes to **Prompt Writer** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-10-14

### Added

- Claude Fable 5 is a covered model, next to Fable 5.1, Opus 5.5, Opus 5 and Sonnet 5.5.
- Every prompt comes with a session mode: interactive or unattended, and plan mode or direct execution in Claude Code, with the reason and how to start it. The prompt is written for that mode, and the header records it in `session_mode` and `claude_code_mode`. Interactive is the default; audits, reviews and other read-only work run in direct execution and report findings without editing.
- Each time, Claude reads the target model's current Anthropic page, what's new or its overview, and follows it where it differs from the built-in guidance, telling you the difference in the design notes.
- Writes the complete text of a system prompt, skill, slash command, agent or `CLAUDE.md` in that file's own format. When it is unclear whether you want that file or a prompt so Claude creates it, Claude asks first.
- Placeholders follow what fills them: Claude Code skill and command arguments, an application's template fields, or fields you fill by hand, named in the reply.
- Success criteria you can check: the prompt states measurable criteria from what you said a good result is, and the reply tells you how to check it.
- Safeguards only where your case needs them: against invented facts, format drift, hostile input or untrusted content, prompt leaks and slow answers.
- When the next step depends on a result nobody has seen yet, you get the first prompt plus drafts of the next ones, each marked as a draft and saying what output it waits for. Bring the output back and Claude checks it against your goal, then revises the prompt, the setup or the next draft. If your first message is an output that disappointed you, Claude asks for the prompt behind it, the model and where it ran.
- A fixed automated sequence comes as all its stages at once, each with its input, output and stage number.
- Skills that would help the task are named in the prompt and in the setup advice, once Claude confirms they exist on your surface.
- Every delivery ends with the checklist Claude verified the prompt against; an item Claude could not verify stays unchecked with its reason. The **Sources** and **Verification checklist** headings stay in English in every reply language. In Claude Code, a check then compares the reply's claims, such as the pages it cites and the verified items, with what Claude actually did, and sends Claude back to fix any claim without evidence.
- Audits list the problems found before the fixed prompt, and the design notes say how each was fixed and name anything added beyond your request.

### Changed

- The skill starts only when you run `/prompt-writer:prompt-writer`: asking for a prompt in plain words no longer starts it, so begin your request with the command.
- Model choice: Opus 5.5 is the default recommendation, Fable 5.1 for the hardest or longest work, Sonnet 5.5 when speed matters most; Fable 5 and Opus 5 when you are tied to them or migrating a prompt tuned for them.
- The built-in guidance is each covered model's official prompting page and Anthropic's prompting best practices, rewritten as instructions for Claude and dated 2026-10-14.

### Removed

- Mythos 5.1 is no longer listed with Fable 5.1's guidance.

### Fixed

- The skill states up front that it writes a prompt for you to run in another session; a request phrased as an order is the goal of that prompt, not an instruction to carry out.
- Asking Claude to write a prompt and run it gets only the prompt, with a note to run it in a new session.
- A skill, slash command or agent file keeps its own frontmatter instead of being wrapped in the prompt header, and a system prompt comes without the header.
- You paste only the prompt body; the header stays as your record, and the body states the reply language when it matters.
- Settings that return an error on the covered models, such as a prefilled reply, non-default `temperature`, `top_p` or `top_k`, and manual thinking budgets, are left out of the recommended setup.
- When live documentation contradicts the built-in guidance, Claude follows the documentation and explains the difference in the design notes instead of asking you.
- The reply gives the URL of every official page Claude read. When a long page cannot be read, Claude moves to a shorter one instead of fetching it again, and says what stayed unverified.
- Claude asks at most four questions in a round, the reply language included, in a fixed order of priority, and at most one short follow-up when an answer still leaves the goal unclear.

## [0.1.1] - 2026-10-13

### Fixed

- The skill now reads its reference files from exact paths that resolve in Claude Code and in the Claude app, so Claude no longer searches the file system for them or fails to read them.
- The skill states its scope up front: it always delivers a prompt and never carries out the task the prompt describes, including when the requested prompt is a slash command, a system prompt or skill instructions.

## [0.1.0] - 2026-10-13

### Added

- `prompt-writer` skill: turns a goal, idea or draft into one copy-ready prompt for Claude Fable 5.1, Opus 5.5, Opus 5 or Sonnet 5.5. It clarifies intent with questions that each carry a recommendation, checks current official facts the prompt depends on, applies the target model's documented guidance, and delivers the prompt with a short header plus the recommended model, effort and session setup.
- Works on new prompts, drafts to refine, existing prompts to audit and prompts to migrate to another target model, and saves the prompt to a file when you ask for one.
- Built-in references for prompting principles, agentic patterns, reliability and safety, and model selection and configuration, with a drift report when live official documentation contradicts them.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/prompt-writer--v0.2.0...HEAD
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/prompt-writer--v0.2.0
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/prompt-writer--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/prompt-writer--v0.1.0
