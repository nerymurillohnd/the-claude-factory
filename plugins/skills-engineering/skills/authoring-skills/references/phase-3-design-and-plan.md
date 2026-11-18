# Phase 3: Design and plan

How to design the skill and plan it: its name, description and frontmatter, each component in detail, the body, and the plan the requester approves.

1. **Name.** Name the activity the skill gives, in lowercase letters, digits and hyphens, at most 64 characters, matching its folder, with no hyphen at the start or end and no two in a row, and without "anthropic" or "claude" if it may be uploaded. Prefer the gerund form, such as `exporting-invoices`, unless sibling skills follow another pattern. Avoid names that say nothing (`helper`) or cover too much (`data`). Propose it with alternatives and the reason.
2. **Description.** Write it by the rules in phase-3-descriptions.md, then judge it from the model's seat: list the requests that should load it and the near-misses that shouldn't, and check it picks right for each.
3. **Other frontmatter.** Add a field beyond `name` and `description` only when the skill's type and intent need it, knowing first every field that type accepts and its gotchas, from phase-3-frontmatter.md.
4. **Components in detail.** For each component phase 2 chose, decide its specifics: each hook's events and how many; each script's language, inputs, outputs and what it checks, by phase-3-scripts-and-hooks.md; each template's shape; each mechanism the task needs, chosen by phase-3-task-mechanisms.md.
5. **What earns a line.** Apply the line test in SKILL.md's Mission and perspective to every line. Lines that pass it: the domain's procedure and reasons, the conventions, facts that defy assumptions, the exact tool, the corrections from phase 1. Cut what any capable model knows. A platform fact earns a line only if it changes what the model writes or does; otherwise write "When [case], consult [page]", or leave it out.
6. **The form matches the failure** each line prevents:
   - output in the wrong shape: a template, or an input and output example;
   - an element the model can't infer: the fact where it applies, or a gotcha;
   - an action that depends on a condition: the condition and both branches;
   - a judgment made inconsistently: the criterion and its reason;
   - a rule skipped under pressure: the rule, each shortcut around it named and closed, and a hook if it must always hold;
   - code rewritten on every run: a script.
7. **Freedom matches fragility.** Give criteria where many approaches work, a preferred pattern where one way is better, and an exact command where a deviation breaks something. Give one default with its exception as its own condition, never a menu. Teach the class of problem, not the answer for one instance.
8. **Body or file.**
   - The body holds what every run needs. Write guidance for the whole task as standing ("after every edit") and near the top: the body is read once, and in Claude Code only its start survives compaction.
   - Files hold what only some runs need, exclusive variants, long examples and lookups: `references/` to read, `scripts/` to run, `assets/` for the output. Move content to files as the body nears its budget, organize them by variant or domain, and name each for what it holds.
   - Put no README and no copy of public documentation in the folder.
   - In a skill whose work runs in phases, give each reference one phase and one topic, name it with its phase and topic, such as `phase-2-placements.md`, and split a topic two phases use into one file per phase: a rule kept in another phase's file is applied late or not at all.
9. **Pointers.** Put each pointer at the step that needs the file, on its own line, as a Markdown link from the skill root, with the verb for its use (read, run, fill in) and a condition the model can check then. Never point to a folder, bury a link in a paragraph, or use an at-mention, which loads the file on every run. In a phased skill, list each phase's files under that phase in the order of the steps that read them, each with its condition and, where the phase's steps are numbered, the step that reads it, and tell the model to read them in that order.
10. **The plan.** Present it and get the requester's approval:

   ```text
   Goal: [one sentence]
   Use cases: [trigger and checkable result for each]
   Location and surfaces: [where it lives, where it runs]
   Name: [proposed name], because [reason]; alternatives: [names]
   Description: [full text]
   Other frontmatter: [each field and value, with its reason]
   Files: [each path, what it holds, when the model reads or runs it]
   Components: [each hook, script, template and mechanism, with its specifics and reason]
   Assumptions: [each one still open]
   ```

Exit: an approved plan you can build without another design decision.
