# Writing instructions

How to write the body of a skill and its references so the model acts the same way on every run: what earns a line, which form each instruction takes, the register, how to embed examples and commands, and the patterns to avoid.

## Contents

- What earns a line
- Reference content and task content
- Freedom matched to fragility
- Match the form to the failure
- Register
- Examples and snippets
- Anti-patterns
- Read it from the model's seat

## What earns a line

The model is already capable; every line competes with the conversation for context. Keep a line only if the model would get the task wrong without it. When unsure, test the task without the line.

What usually earns a line:

- the project's or organization's conventions: names, formats, where things live;
- the domain's procedure, in the order an expert follows it, with the reasons that decide its edge cases;
- facts that defy reasonable assumptions: the endpoint that returns 200 on failure, the column with a misleading name;
- the exact tool, library, command or API to use, and the one to avoid;
- corrections the model needed in past runs.

What doesn't:

- what any capable model knows: what a PDF is, how to write a loop, that tests are good;
- generic advice: "handle errors appropriately", "follow best practices";
- explanations of the skill to a human reader.

Start from real expertise, never from general knowledge. Extract it from a task done with the user (the steps that worked, their corrections, the formats, the context they supplied) or from the project's own material: runbooks, style guides, incident reports, review comments, past fixes. A skill written from general knowledge produces general results.

Correct (adds what the model lacks):

```markdown
Use pdfplumber for text extraction. For scanned PDFs, use pdf2image with pytesseract instead.
```

Incorrect (tells the model what it knows):

```markdown
PDF files are a common format that contains text and images. To extract text, you'll need a library. There are many libraries available, but pdfplumber is easy to use and handles most cases well.
```

Scope the skill like a function: one coherent unit of work. Too narrow and several skills must load for one task; too broad and it triggers where it shouldn't and dilutes its guidance.

## Reference content and task content

- **Reference content** is knowledge the model applies to whatever it is doing: conventions, domain rules, a style guide. Write it as rules and facts, grouped by topic, each applicable on its own. It suits automatic invocation and preloading into subagents.
- **Task content** is a procedure for one action: deploy, release, generate a report. Write it as ordered steps with their conditions and checks. It suits user invocation, often with `disable-model-invocation`, and `context: fork` when it needs no conversation.

A skill can hold both: the steps of its task, plus the rules that hold during all of them. Write the rules as standing instructions ("after every edit"), not as a step, because the body is read once and must govern the whole task.

## Freedom matched to fragility

Set how tightly each step is specified by how badly it fails when done differently:

- **High freedom**, as goals and criteria, where several approaches work and context decides: reviewing code, writing a summary. Say what a good result is and why; let the model choose how.
- **Medium freedom**, as a preferred pattern or a parameterized script, where one way is better but variation is acceptable: "Use this template and adapt the sections to the data."
- **Low freedom**, as an exact command or sequence, where a deviation breaks something: a migration, a release, a file format. "Run exactly this script. Don't change the command or add flags."

Within any level:

- **Give a default, not a menu.** Name the tool or approach to use, and the exception as its own condition: "Use pdfplumber. For scanned PDFs, use pytesseract." Equal options make the model choose differently on each run.
- **Teach the class of problem, not one answer.** Write the procedure that solves every instance ("find the table's join keys, then..."), not the result for the instance you tested.
- **Give the reason where the model must judge.** One clause of why lets the model decide the cases the rule doesn't name: "Keep the summary under 100 words, because it is shown in a notification."

## Match the form to the failure

Choose each instruction's form by the failure it prevents. Test runs show which failure you have:

- **The model skips a step under pressure or shortcuts a discipline**: make it a gate with an exit condition ("Don't continue until the validator passes"), a checklist item, or a hook if it must hold every time.
- **The output comes out in the wrong shape**: give a template or an input and output example, not a description of the format.
- **The model misses an element it can't infer**: state the fact or rule where it applies, as a gotcha if it defies assumptions.
- **The right action depends on a condition**: write the condition and both branches: "If the file has signatures, read FORMS.md; otherwise continue."
- **The model makes a judgment call inconsistently**: write the criterion that decides it and its reason.
- **The model does too much**: state the stopping point and what not to do beyond it.
- **The model reinvents the same code each run**: bundle a script.

Read [task-mechanisms.md](task-mechanisms.md) for how to build workflows, checklists, validation loops and templates.

## Register

Write the way the official skill examples do: short and complete. Short is not thin: each instruction names the action, its object, the condition and, where one exists, the fallback.

- **Imperative, to the model**: "Run", "Read", "Write", not "You should consider running" or "The skill runs".
- **One action per line or bullet**, with its condition and fallback: "Run `scripts/validate.py out/`. If it reports missing fields, add them to the CSV and run it again."
- **Concrete names**, not categories: the file, the command, the field, the value. "Check `amount` is positive", not "validate the data".
- **The reason only where it decides an unnamed case**, in one clause. Don't narrate why every step exists.
- **No narration**: no "First, we'll...", "Now that we have...", "This is important because...".
- **Positive instructions**: say what to do. Use a prohibition only for a specific mistake the model actually makes, and pair it with what to do instead.
- **No emphasis by capitals or alarm words** ("CRITICAL", "YOU MUST"). Current models follow plain instructions; emphasis makes them over-apply a rule. If a rule keeps being skipped, move it earlier, make it a gate, or enforce it with a hook.
- **Lists over tables** in instructions the model follows; paragraphs only where the reasoning lives in the connections between ideas.
- **One term per concept**, the same in every file: if it is a "field", it is never a "box" or an "element".
- **No time-sensitive wording** ("currently", "the new API", "after August"). Write the current method; put a superseded one under an "Old patterns" heading, if anywhere.

Correct:

```markdown
Run `python scripts/validate.py --input data.csv`. If it fails, the error names the column: fix the value in the CSV and run it again.
```

Incorrect:

```markdown
Make sure to validate the data before proceeding.
```

## Examples and snippets

An example teaches what prose can't: a tone, a level of detail, a format. Add one only where the output depends on seeing it, because the model imitates examples closely, including their accidents.

- **Input and output pairs** for transformations and style: show the input, the output, then the rule line that says what to imitate.
- **Two or three examples that differ** where the output varies, so the model learns the pattern, not one instance.
- **The rule after the examples**: "Follow this style: type(scope): description, then the detail."
- **Commands** in a fenced block with the language tag, versions pinned, placeholders in square brackets with what goes there: `python scripts/fill.py [input.pdf] [fields.json] [output.pdf]`.
- **Code** only as long as the pattern needs: the call and its arguments, not a whole program.
- **Inline** when short and needed on every run; **in a file** (`references/examples.md` or `assets/`) when long or needed only in some cases, with a pointer that says when to read it.
- **Correct and incorrect pairs** where the model would otherwise produce the incorrect one, each with a one-line reason.

Correct:

````markdown
Write commit messages like these:

Input: Added user authentication with JWT tokens
Output:
```text
feat(auth): implement JWT-based authentication
```

Input: Fixed dates shown in the wrong timezone in reports
Output:
```text
fix(reports): use UTC timestamps in timezone conversion
```

Follow this style: type(scope): what changed, in the imperative.
````

Incorrect:

```markdown
Write good commit messages that follow conventional commits and are descriptive.
```

## Anti-patterns

Each with what to write instead.

General knowledge:

```markdown
Incorrect: Git is a version control system. Commits record changes.
Correct:   Commit with `git commit -s`: this repository requires sign-off.
```

Catch-all phrases:

```markdown
Incorrect: Handle errors appropriately and follow best practices.
Correct:   On a 429, wait the seconds in the Retry-After header, then retry once.
```

A menu instead of a default:

```markdown
Incorrect: You can use pypdf, pdfplumber, PyMuPDF or pdf2image.
Correct:   Use pdfplumber. For scanned PDFs, use pdf2image with pytesseract.
```

Time-sensitive wording:

```markdown
Incorrect: If it's before August 2025, use the old API.
Correct:   Use `api.example.com/v2/messages`.
```

One term for two concepts, or two terms for one:

```markdown
Incorrect: Extract the fields ... then pull the boxes ... then validate each element.
Correct:   Extract the fields ... then fill each field ... then validate each field.
```

The same fact in two places:

```markdown
Incorrect: SKILL.md says the limit is 50 rows; references/api.md says 100.
Correct:   State the limit once, where the model first needs it.
```

A rule after the step it governs:

```markdown
Incorrect: 3. Write the file.  ...  7. Note: never overwrite existing files.
Correct:   3. Write the file under a new name; never overwrite an existing one.
```

Standing guidance written as one step:

```markdown
Incorrect: 5. Run the tests.
Correct:   Run the tests after every edit.   (near the top, before the steps)
```

A vague step with no check:

```markdown
Incorrect: Make sure the output is correct.
Correct:   Open output.pdf and confirm every field in fields.json has a value on the page.
```

## Read it from the model's seat

After writing each section, read it as the model will: a fresh session that knows only the description, the body and the files the body points to, with none of this conversation.

1. Read the description alone. Would it pick this skill for each use case, and not for the near-misses?
2. Read the body top to bottom. At each instruction, predict what the model does. Where two readings are possible, rewrite until only the right one is.
3. Follow each pointer. Is the condition one the model can check at that moment? Does the file hold what the pointer promised?
4. Look for what the model would need and not find: a term never defined, a step that assumes a file exists, a decision with no criterion.
5. Look for what it would find and not need: anything it does well without being told.

Then confirm with a run in a fresh session; reading only predicts. Read [validation.md](validation.md) for running it.
