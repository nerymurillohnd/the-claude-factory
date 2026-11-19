# Phase 2: Writing style

How to word each instruction of the skill so Claude follows it the same way on every run: register, what each line must add, defaults, procedures, terms and emphasis.

## Contents

- [Register](#register)
- [What each instruction adds](#what-each-instruction-adds)
- [Defaults, not menus](#defaults-not-menus)
- [Procedures, not answers](#procedures-not-answers)
- [Terms and time](#terms-and-time)
- [Emphasis and prohibitions](#emphasis-and-prohibitions)
- [Official sources](#official-sources)

## Register

- Write in the imperative: one action per line, with its condition and its fallback.
- Name concrete things, such as the file, the command or the field, instead of categories.
- Give the reason where Claude must judge, so it can decide the cases the line doesn't name. In a fixed step, say what to do without narrating why.
- Leave out narration, filler and praise of the task.

## What each instruction adds

Write what Claude lacks, as an action it can take and check.

```markdown
<!-- Weak: tells Claude what it knows, with nothing to act on -->
Dates can be written in many formats around the world, so parse them carefully.

<!-- Strong: the fact Claude lacks, and what to do with it -->
Read invoice dates as DD/MM/YYYY: the suppliers are in Central America. A date that only parses as MM/DD is a data-entry error: flag it, don't swap it.

<!-- Weak: no way to act or to check -->
Make sure the data is valid before you continue.

<!-- Strong: the check and the fix -->
Run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_totals.py invoices.csv`. When it fails, it names the row and column: fix that value and run it again.
```

## Defaults, not menus

- Give one default, and the exception as its own condition.
- Match each step's freedom to its own fragility, since most skills mix free steps with exact ones: criteria where many approaches work, a preferred pattern where one is better, the exact command where a deviation breaks something.

```markdown
<!-- Weak: a menu -->
You could use the CSV importer, the API, a manual journal entry or a spreadsheet macro.

<!-- Strong: a default with its exception -->
Import with the accounting system's CSV importer. For a system without one, write the journal file from [Journal template](assets/journal.csv).

<!-- Weak: a fragile step left free -->
Migrate the ledger with the options that fit.

<!-- Strong: the exact command, since any change to it can corrupt the ledger -->
Run `python3 ${CLAUDE_SKILL_DIR}/scripts/migrate_ledger.py --verify --backup` as written, with no other flags.
```

## Procedures, not answers

Teach the method for the whole class of tasks the skill serves, not the answer to one request. Specific details, such as a template, a constraint or a tool's flag, stay specific inside a method that generalizes.

```markdown
<!-- Weak: the answer to one request, useless for the next -->
Join `invoices` to `suppliers` on `supplier_id`, keep the rows from March, and sum `total`.

<!-- Strong: the method for any report on the invoices -->
1. Read `schema.yaml` to find the tables the request needs.
2. Join the tables on their `_id` keys.
3. Turn each filter of the request into a `WHERE` clause.
4. Sum or count the columns the request names, and return a Markdown table.
```

## Terms and time

- Choose one term per concept, and use it in every file of the skill.
- Write each rule as it is now. Leave out dates, "until", "recently" and versions, which go stale. Keep an old way only when Claude must recognize it, as an old pattern, under the current one.

```markdown
<!-- Weak: three terms for one thing, and a date that will go stale -->
Extract the line items, then total the rows, then check each entry. Until the migration next quarter, use the old endpoint.

<!-- Strong -->
Extract the line items, then total the line items, then check each line item. Use api.example.com/v2/invoices.
```

## Emphasis and prohibitions

- State the reason instead of capitals or absolutes, and turn a rule that can't bend into a hook.
- Put a prohibition beside the instruction it limits, with what to do instead, or write it as a gotcha.
- Put a rule before the step it governs, and guidance for the whole task near the top, as a standing instruction.

```markdown
<!-- Weak: emphasis instead of a reason, and a rule after its step -->
3. Write the file.
7. NOTE: NEVER OVERWRITE EXISTING FILES!!!

<!-- Strong -->
3. Write the file under a new name: an existing file may hold the user's edits.
```

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide: each holds the full rules, edge cases and version notes this file leaves out.

- Read [Be clear and direct](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#be-clear-and-direct) and [Add context to improve performance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#add-context-to-improve-performance) when an instruction reads vague or arbitrary. They show how explicit instructions and the reason behind them change Claude's output.
- Read [Tool usage](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#tool-usage) when a line leans on emphasis. It shows how aggressive wording makes current models overtrigger, and the plain wording to use.
- Read [Concise is key](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#concise-is-key) and [Set appropriate degrees of freedom](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#set-appropriate-degrees-of-freedom) when you weigh what a line adds or how strict a step is. They give the test for a line and the three levels of freedom.
- Read [Avoid offering too many options](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#avoid-offering-too-many-options) and [Provide defaults, not menus](https://agentskills.io/skill-creation/best-practices#provide-defaults-not-menus) when a step lists approaches. They show the default with its escape hatch.
- Read [Use consistent terminology](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#use-consistent-terminology) and [Avoid time-sensitive information](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#avoid-time-sensitive-information) when you name a concept or a change over time. They show one term per concept and how to keep an old pattern.
- Read [Favor procedures over declarations](https://agentskills.io/skill-creation/best-practices#favor-procedures-over-declarations) when a step answers one request instead of teaching the method. It shows a specific answer turned into a method that works for the whole class of tasks.
- Read [What you can stop doing](https://code.claude.com/docs/en/best-practices#what-you-can-stop-doing) when emphasis seems the fix for a missed line. It says why IMPORTANT and ALL CAPS backfire and when a hook is the answer.
