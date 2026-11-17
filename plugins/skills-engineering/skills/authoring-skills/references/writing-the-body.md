# Writing the body

Once invoked, every line of a skill stays in the conversation for the rest of the session, competing with everything else for Claude's attention. So each line has to change what Claude does, and has to be read one way. One test decides what goes in: would Claude get this wrong without it?

## Contents

- 1. What earns a place
- 2. What to leave out
- 3. When you can't tell
- 4. Examples
- 5. One picture across every file
- 6. Leave nothing to guess
- 7. Register and wording
- 8. Discipline skills
- 9. Questions to ask yourself

## 1. What earns a place

Write what Claude can't know or infer without the skill:

- The conventions of this project, team or organization, and decisions written nowhere Claude can read.
- The domain's procedures and the order they must follow.
- Gotchas: concrete facts about the environment that defy a reasonable assumption (a table with soft deletes, an ID named differently in each service, a health check that stays green while its database is down). These usually matter most. State each once, in `SKILL.md`, before the step it affects.
- The corrections the user had to make to Claude, in their words. Each correction you learn while building or using the skill joins the gotchas.
- Which tool, library or command to use where several would work, as one default with the condition for any alternative: "Use pdfplumber for text; for scanned pages, pdf2image with pytesseract."
- Facts newer than training: a version, limit, field, flag, default or rename. Familiar subject, new detail: keep the detail, cut the wrapping. Verify each against its current source before writing it.
- The reason behind each judgment call, when it's specific to this skill or its users: "pick the lighter dependency, because this ships inside a size-capped bundle." The reason lets Claude decide a case the skill never named.

Walk the task step by step and ask, at each step, what Claude needs there and lacks. Look hardest where versions and defaults change, where the project made its own choices, and where several approaches would work but one is right here. A skill that only avoids waste can still be silent exactly where Claude fails.

## 2. What to leave out

- General knowledge: what a common format, protocol or tool is, and how it works in general. A reason that only restates general knowledge ("tests catch bugs") goes too.
- Behavior Claude already has: "write clean code", "be careful", "be thorough", "think it through". Keep a line only when it names a concrete bar Claude couldn't guess, such as the project's lint rule or definition of done.
- Workarounds written for older models: capitals and IMPORTANT, "keep going until done", "don't be lazy", "think hard", and descriptions of a file layout Claude can read itself. They cost context, and emphasis and keep-going lines make Claude over-apply a rule or over-work a task.
- Copies of what Claude can reach when it needs it on every target: the project's files, a tool's `--help`, a file the skill already bundles. Say where to look and when, in one line, and keep only what the original doesn't say (which option, which output to trust, which step first). Where a target can't reach the original (no repository, no network), the copy stays.
- Narration: how the process unfolds, why the skill exists, the history behind a fixed step. It changes no decision.
- Anything wrong. A restated syntax that is outdated, or a rule narrowed where it doesn't fit, makes Claude do worse than without the skill.

## 3. When you can't tell

Your sense of what Claude knows is not proof of what the model running the skill does by default. When you can't tell whether a passage changes behavior, keep it and mark it for a comparison: the same realistic request with and without the skill (a plugin's evals can run this). Never cut on a guess. Judge against the least capable model the skill states it serves; guidance a stronger model doesn't need may be what a weaker one needs.

## 4. Examples

- Add an example where quality depends on seeing one: a style, a level of detail, a format hard to pin down in words. For any output that matters, give the format, the audience and tone, and one real example the user was happy with.
- Pair each example with the rule it illustrates, so Claude generalizes instead of copying: "Follow `type(scope): brief description`", then `fix(auth): handle expired refresh tokens`.
- Make examples concrete, and as short as they can be while still teaching. Don't add a second example of a pattern another already shows.
- When output drifts between runs, fix the ambiguous instruction; an example for the one case that just failed fixes that case only.
- Inside a skill, teach a "don't" as one plain sentence beside the instruction it limits, or as a gotcha, not as paired good and bad samples.
- Where examples live is covered in the structure-and-files guide.

## 5. One picture across every file

Claude builds one model of the task from `SKILL.md` and every file it opens. That model holds only if the passages agree.

- No contradictions: never two values, two orders or opposite directives for the same thing, and never a rule binding in one place and a preference in another. A reference that disagrees with `SKILL.md` makes behavior depend on whether Claude opened it. Where a general rule has an exception, say where the exception applies and which one wins.
- One term per concept, in every file, and one concept per term. Verbs too: not "extract" here, "pull" there. When the environment uses several names for one thing, map them once ("`user_id` in the database, `uid` in the auth service: the same value") and keep your own term otherwise.
- Each fact once, where Claude first needs it. A second statement, literal or in other words, costs context and drifts into a contradiction; a later passage points back by name ("apply the naming rule in step 2"). A short checklist that names rules the body teaches is not a duplicate, as long as it doesn't teach them again.

## 6. Leave nothing to guess

Claude reads the skill like a capable new colleague who doesn't know your norms: it does what the text says and fills every gap with its own guess.

- Every action says what it produces, what comes next, what to do when it fails or doesn't apply, and how to tell it's done. "Validate the data" is a dead end; "run `validate.py`; on a missing field, add it to the CSV and rerun" is not. The skill as a whole says what finished looks like and what Claude delivers.
- Every repeat ("search again", "refine until right") has an exit Claude can check and a fallback: "up to three times, then report the queries tried."
- Every coined term, project-specific sense, tool and agreed decision is stated at or before first use: "the error helpers in `src/lib/errors.ts`", never "the approved helpers".
- Every value, scope and format the result depends on is stated: no "large", "recent" or "the relevant tests" without a measure, and no menu of equal options without a default.
- No catch-alls such as "handle errors appropriately" or "follow best practices": name the pattern, case or criterion. Test: would two careful readers agree whether a result passes?
- No instruction with two readings: a verb that can mean advise or act ("suggest changes" gets suggestions, not edits), a "this" with two antecedents, an "or" where it matters whether one option or all apply.
- Leave open on purpose what Claude should judge from context: covering every edge case where several approaches are valid hurts more than it helps.

## 7. Register and wording

- Shape follows content: related standing rules as bullets, context and reasoning as prose (the "because" and "unless" carry the meaning), numbered steps for a fixed order, a table only for a real grid. A body written in heavy markdown pulls Claude's output toward markdown; when the skill wants prose out, write the blocks that model that output in prose.
- Where Claude must act, write an imperative that names the action and its object; a question or "you could" reads as optional, and Claude takes wording literally. Where Claude must understand, state the fact and what follows from it ("…uses soft deletes, so every query filters `deleted_at IS NULL`"). Where Claude must judge, add the reason in one clause.
- Match firmness to what one deviation costs: exact wording for a fragile step, a default plus room to adapt where several approaches work. Hedges ("try to", "if possible", "consider") hand Claude the choice; use them only where the choice really is Claude's.
- No shouting: no capitals, "CRITICAL" or stacked "MUST". A plain "never" or "exactly" is enough where any deviation is a failure. A line Claude still misses is buried, or is a zero-exception rule that needs a hook, not louder words.
- Say what to do rather than listing what to avoid: "write three to five sentences of plain prose, findings first", not five "don't" lines. Keep a prohibition for a real hazard, with the permitted path in the same sentence ("don't edit `src/gen/`; regenerate it with `npm run gen`").
- Address Claude in one person throughout, normally the imperative. Text that addresses the skill's author or the user ("you'll want to test this with your team") confuses who each instruction is for.
- Nothing that goes stale: no dates as conditions, "latest", "currently", "the new", counts that change, or UI details. State the current method without a date; history still worth keeping goes under an "Old patterns" heading.

## 8. Discipline skills

When the skill enforces a discipline Claude is tempted to skip under pressure (test first, verify before claiming success, an exact sequence), stating the rule leaves open the workarounds it didn't name.

- Close the likely workarounds in so many words, next to the rule: "Run exactly `migrate.py --verify --backup`; don't add flags, even ones that look harmless."
- Say why the rule still holds under the pressures that tempt Claude to skip it: the user in a hurry, a case that seems simpler, a check that seems redundant. A short list of the thoughts that signal a rationalization works ("too simple to test", "I'll verify after").
- Close only the workarounds Claude would plausibly take. For anything that isn't a discipline, this becomes the prohibition list section 7 warns against.

## 9. Questions to ask yourself

- For each passage: would Claude get this wrong without it?
- Where would Claude fail if the skill stayed silent, and does the skill speak there?
- Does every key concept have one name in every file?
- Is any fact stated twice, or anywhere after the first passage that needs it?
- For each instruction: what does it produce, what's next, what if it fails, how do I know it's done?
- Could a careful reader take any line two ways?
