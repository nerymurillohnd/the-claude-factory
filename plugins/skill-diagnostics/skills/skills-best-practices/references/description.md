# Description

How to write the `description`, the only text the agent sees before it decides to load the skill.

## Writing the description

The description is the only text the agent sees before it decides to load the skill, so it must say what the skill does and when to use it, in the words users actually type \[AS\]\[PL\]\[CC\].

- **What and when.** State the capabilities and the triggers or contexts \[PL\]\[AS\].
- **Beyond what the agent does alone.** Agents consult skills mainly for tasks that need knowledge or capabilities they lack: "A simple, one-step request like 'read this PDF' may not trigger a PDF skill even if the description matches perfectly" \[AS\]. Judge triggering on requests where the skill adds something, not on trivial ones.
- **Key terms.** Include the words users would naturally say; Claude chooses among possibly 100+ skills \[PL\]\[CC\].
- **User intent, not mechanics.** Describe what the user is trying to achieve \[AS\].
- **Be pushy about scope.** List contexts where it applies, including when the user doesn't name the domain ("even if they don't explicitly mention 'CSV'") \[AS\].
- **Concise.** A few sentences to a short paragraph; hard limit 1,024 characters \[AS\]. In Claude Code put the key use case first, because the listing cuts `description` + `when_to_use` at 1,536 characters and drops the descriptions of least-used skills when the listing overflows its budget (1% of the context window) \[CC\]. `/doctor` estimates the listing's cost and `/skill-doctor` finds unused skills; `skillListingBudgetFraction` raises the budget, `"name-only"` in `skillOverrides` lists a low-priority skill without its description, and `skillListingMaxDescChars` changes the 1,536 cap \[CC\].
- **Portable length.** The open standard and the Platform cap the description at 1,024 characters \[AS\]\[PL\]; Claude Code cuts `description` + `when_to_use` at 1,536 in the listing \[CC\]. 1,024 is the portable limit.
- **Point of view.** Write the capability in the third person ("Processes Excel files…") and the triggers as "Use when…". The Platform says always third person and to avoid "You can use this to process Excel files" \[PL\]; the open standard says imperative phrasing, "Use this skill when…" rather than "This skill does…" \[AS\]. Third person for the capability plus "Use when…" for the triggers fits both, as the Platform's own examples do. The reason: "The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems" \[PL\].
- **Too broad or too narrow.** If it triggers too often, make it more specific or set `disable-model-invocation: true` \[CC\]; state what it does *not* do and the boundary with adjacent skills \[AS\].
- **When, not how.** The description gives "enough detail for Claude to determine when to select this Skill, whereas the rest of SKILL.md provides the implementation details" \[PL\]. Don't summarize the procedure in it: Claude may follow the summary and never read the body \[SD\] `default`.
- **Cover every capability the body offers.** A capability missing from the description never triggers \[SD\] `default`.
- **Tell sibling skills apart by the kind of request**, not by naming them \[SD\] `default`.
- **Avoid vague descriptions** such as "Helps with documents", "Processes data" or "Does stuff with files" \[PL\].

## Example before and after

\[AS\]:

```yaml
# Before
description: Process CSV files.

# After
description: >
  Analyze CSV and tabular data files — compute summary statistics,
  add derived columns, generate charts, and clean messy data. Use this
  skill when the user has a CSV, TSV, or Excel file and wants to
  explore, transform, or visualize the data, even if they don't
  explicitly mention "CSV" or "analysis."
```
