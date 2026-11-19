# Phase 2: Examples

When the skill needs examples, how many, and how to write and place them so Claude learns the pattern and not one instance.

## Gotchas

- Claude copies what examples share: when every example has the same length, tone or opening, the output takes it too. Vary them where the output may vary.

## When to add examples

Add examples only where the output depends on seeing them: a tone, a level of detail, a format. Where an instruction or a template states the output, write that instead.

- When the output drifts across runs, sharpen the instruction that allows it before you add an example for the case that failed.
- Write the examples from the skill's own domain: an example taken from documentation teaches that page's domain, not the skill's.

## How to write them

- Give 3 to 5 examples that differ where the output varies.
- Show each as an input and its output, then close with a rule line that says what to imitate.
- Wrap each example in `<example>` tags, and several in `<examples>`, so Claude tells them apart from the instructions.

````markdown
<!-- Weak: one example, no tags, nothing that says what to imitate -->
Example: "Add CSV export" becomes "- Added CSV export."

<!-- Strong -->
Write each changelog line like these:

<examples>
<example>
Input: PR "Add CSV export to the invoices page" (label: feature)
Output: - Added CSV export on the invoices page.
</example>
<example>
Input: PR "Fix rounding of tax on multi-currency invoices" (label: bug)
Output: - Fixed tax rounding on invoices with more than one currency.
</example>
<example>
Input: PR "Drop the legacy XML export" (label: breaking)
Output: - Removed the XML export; use the CSV export instead.
</example>
</examples>

Follow this style: past-tense verb, what changed for the user, one line, no PR jargon.
````

## Where to put them

- Inline in `SKILL.md`, when they are short and every run needs them.
- In a reference file, when they are long or only some runs need them, with a pointer at the step that says when to read it.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide: each holds the full rules, edge cases and version notes this file leaves out.

- Read [Use examples effectively](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#use-examples-effectively) when you write the examples. It gives how many, how diverse, and the tags that set them apart.
- Read [Examples pattern](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#examples-pattern) when the skill's output is a format such as a commit message. It shows input and output pairs in a skill.
- Read [Structure prompts with XML tags](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags) when the examples sit among instructions and inputs. It shows how tags keep each kind of content apart.
