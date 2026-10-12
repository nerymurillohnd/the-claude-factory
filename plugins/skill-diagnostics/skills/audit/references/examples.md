# Weak and strong forms

Examples for the conformance checklist: each pair shows the weak form a rule catches and a strong form that passes it, with the rule's label from `fields.md`. They illustrate the rules; they are not templates. A skill that looks different but meets every rule passes.

Full skills that pass every rule, one per profile, are in `assets/examples/`: `forked.md`, `with-hooks.md`, `script-backed.md`, `live-data.md`, `preloaded.md`.

## Description says what, then when [rec]

- Weak: `description: Reads the diff, groups the changes, drafts a subject, then a body.`
- Strong: `description: Writes commit messages from the staged diff. Use when the user asks for a commit message or wants staged changes described.`
- Why: the weak one summarizes the procedure and never says when to use it; the model may follow the summary and skip the body.

## A colon in an unquoted value [default]

- Weak: `description: Use when: the user asks for a report`
- Strong: `description: "Use when: the user asks for a report"`
- Why: Claude Code reads it, but strict YAML parsers, uploads and the API reject it.

## A reference says when to read it [rec]

- Weak: `See references/ for details.`
- Strong: `Read [api-errors.md](references/api-errors.md) when the API returns a non-200 status.`

## A default, not a menu [rec]

- Weak: `Use pypdf, pdfplumber, PyMuPDF or pdf2image.`
- Strong: `Use pdfplumber. For scanned PDFs, use pdf2image with pytesseract.`

## A fork needs a task and a return [req]

- Weak: a skill with `context: fork` whose body is a list of style rules.
- Strong: `assets/examples/forked.md`: one task, its steps, and the exact final message.
- Why: a fork of plain guidelines has nothing to do and returns nothing.

## Explore and Plan load no CLAUDE.md [req]

- Weak: `context: fork` with `agent: Explore` and a body that says `Follow the project's conventions.`
- Strong: the conventions the task needs are written in the skill.

## No argument inside a dynamic-context command [observed]

- Weak: a body line `` !`git log --grep="$ARGUMENTS"` ``
- Strong: `` !`git log --oneline -20` `` in the body, then `Find the commits that match: $ARGUMENTS`.
- Why: the argument is substituted into the command before the shell runs it, so `$(…)` in it runs as code. High.

## allowed-tools names the exact command [req]

- Weak: `allowed-tools: Bash`
- Strong: `allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/check_totals.py *)`
- Why: the weak form pre-approves every shell command for that turn.

## A script runs by its path from the skill [req]

- Weak: `Run python scripts/check_totals.py data.csv`
- Strong: `Run ${CLAUDE_SKILL_DIR}/scripts/check_totals.py data.csv`
- Why: commands run in the session's directory, not the skill's.

## A script reports problems and exits 0 [req]

- Weak: `Prints JSON findings; exit 1 when any invoice fails.`
- Strong: `Prints a JSON report and exits 0 whenever it printed one, with the failing invoices inside; exits 2 on unreadable input.`
- Why: Claude Code cuts a failing command's output to about 10,000 characters.

## A hook reaches its script through the plugin root [req]

- Weak: `command: ${CLAUDE_SKILL_DIR}/scripts/check.py`
- Strong: `command: "${CLAUDE_PLUGIN_ROOT}/skills/<name>/scripts/check.py"` with `args: []` (exec form), as in `assets/examples/with-hooks.md`.
- Why: hooks resolve the project, plugin root and plugin data placeholders, not the skill directory.

## onFailure does nothing on Stop [req]

- Weak: a `Stop` hook with `onFailure: block`, relied on to stop an unfinished turn.
- Strong: the `Stop` hook itself returns its decision; `onFailure: block` only on events where it applies, such as `PreToolUse`.
