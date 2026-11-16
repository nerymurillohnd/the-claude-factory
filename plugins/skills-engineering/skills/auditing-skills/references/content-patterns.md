# Content patterns

This file teaches you how to audit a skill's examples and output templates, its embedded commands and code, the shape of its content (prose, lists, steps, tables), and its wording. Each section gives you the principle, why it matters, and what to do when you audit.

## Contents

- How to use this file
  - Before auditing: establish the context
  - Then, audit area by area
- 1. Examples and output templates
  - 1.1 When an example earns its place
  - 1.2 How drift is really fixed
  - 1.3 Where an example or template lives
  - 1.4 How a good example is written
  - 1.5 Output templates
  - 1.6 How a skill teaches a "don't"
- 2. Embedded commands and code inside a skill
  - 2.1 Freedom matched to fragility
  - 2.2 Commands Claude will run
  - 2.3 Paths and tool names inside snippets
  - 2.4 Claude Code-only body syntax
- 3. Shape: prose, bullets, numbered steps, tables
  - 3.1 No format is banned — the shape must match the content
  - 3.2 Order and headings
  - 3.3 Tables and tone
- 4. Wording and semantics
  - 4.1 When a step explains why, and when it just says what
  - 4.2 How strong a directive should be
  - 4.3 Standing instructions
  - 4.4 Forked and preloaded skills start blind
  - 4.5 Terminology, clarity, file references
  - 4.6 Time-sensitive wording
  - 4.7 Discipline skills: closing loopholes
- Classifying findings
- Improvement opportunities
- Delivering the report

## How to use this file

Read this whole file, through its final section, "Delivering the report", before you judge anything. This complete reading, and an audit of the skill against every point in it, are a precondition of your audit: no point stays unaudited. Keep to the file's order: first establish the context, then audit area by area, then classify what you found.

The prompt you receive carries the results of the mechanical checks your areas use, such as where the body's first 5,000 tokens end or where an inline `!` command is misplaced. Take them as verified and judge what they mean; never measure or run anything yourself. When a result a point needs is missing, record it under Checklist exceptions as blocked and judge everything else.

Audit from the seat of a Claude that loads the skill with no prior context and has to use it. Read every example, template, command and instruction as that Claude would meet it, and ask whether it would know exactly what to do. Wherever it would hesitate, guess, misread, or meet an ambiguity, a friction or a gray area, record a finding under the point of this file it falls under.

### Before auditing: establish the context

A judgment that's correct for one skill can be wrong for another, so settle these four points before you apply any rule. They decide what "correct" means for the skill in front of you.

1. **Where the skill lives.** Identify whether it is a personal skill (`~/.claude/skills/`), a project skill (`.claude/skills/`, at any nested level), a skill from an added directory (`--add-dir`), a skill inside a plugin's `skills/` subdirectory, a plugin that packages a single skill at its own root (`SKILL.md` directly at the plugin root, no `skills/` folder), a skill synced from a claude.ai account (which may be synced but not enabled), or a skill delivered through managed or enterprise settings. These differ in real ways — a plugin-root skill's command-name rules aren't a `skills/`-subdirectory skill's, for instance — so don't judge one by the other's rules.
2. **How the skill gets invoked.** Determine whether it runs directly in a normal session, where it can see the conversation so far, or is forced into a forked subagent (`context: fork`), or is preloaded into a custom subagent's startup context. The last two start with zero conversation history (see §4.4), so hold such a skill to a stricter bar for self-containment.
3. **Which surface will load it.** Determine whether Claude Code loads it — terminal, IDE, desktop app or a cloud session, including the Claude app's tasks on an account where chat and Cowork are unified — or Cowork on the desktop app of an account not yet unified, or claude.ai chat or the API. Claude-Code-only body syntax (§2.4) is dead weight, or literal garbage text, on a surface that doesn't support it, so judge every such line against the surfaces you found here.
4. **What the skill is actually trying to do**, from its own description and body. Use this to decide which sections apply. A skill that never embeds a command has nothing to check against §2. A skill with no fixed output format needs no template under §1.5. Apply each section only where the skill's own stated purpose makes it relevant, and never flag an absence the skill never had a reason to fill.

### Then, audit area by area

Audit what the skill has, and also what it should have. In each of the four areas, start from the skill's nature and purpose and ask which examples, output templates, commands, snippets, outputs and assets a skill like this one needs to work at its best. Then compare that with what the skill actually contains, and give every item exactly one of these outcomes:

- **Present and optimal.** It is the right pattern for this skill's purpose, written the way this file describes. Record no finding.
- **Present but wrong.** It violates a rule of this file, misleads Claude, or shouldn't be in the skill at all. Record it as a defect, classify it (see "Classifying findings"), and say whether it must be deleted, rewritten or moved.
- **Present, right, but improvable.** It is the right pattern and it works, but a stronger version from this file would serve the skill's purpose better. Record it as an improvement opportunity, with the adjustment it needs.
- **Absent, and the skill's purpose needs it.** Record it as an improvement opportunity: say exactly where it belongs, what it should contain, and cite the point in this file the recommendation rests on.
- **Absent, and the skill's purpose doesn't need it.** Record no finding. A skill is not defective for lacking something it never had a reason to have.

Work only from what is actually written in the skill under audit, never from what it's likely to contain. If you have no line to point to, you have no finding.

---

## 1. Examples and output templates

### 1.1 When an example earns its place

An example earns its place when the output's quality depends on seeing one — a style, a level of detail, or a format that's genuinely hard to pin down in words. It conveys what's wanted far more clearly than a description, because it shows the result instead of describing it.

When you audit:

- Flag a style, level of detail or format the skill describes only in words where the output's quality depends on seeing it, and recommend one example.
- For any handoff that matters, look for three things together: the format named, the tone set (who the output is for, how it should read), and one real example the author was actually happy with. That one example teaches more about the quality bar than any amount of description, so flag a handoff that lacks it.
- Flag an example longer than it needs to be to teach, and a second example of a pattern another example already teaches. Every line of an example is paid on every run.

Recognize the difference:

**Verbose (42 words):** a full dialogue that restates the request, narrates the search, and spells out the query.

**Compact (20 words):**
> Partner: "How did we handle auth errors in React Router?"
> You: Searching…
> [Dispatch subagent → synthesis]

### 1.2 How drift is really fixed

Where output varies across runs, the usual mistake is to add an example for the case that just failed. That patch fixes one instance and leaves the underlying ambiguity untouched, and the skill is used across many requests, not just the ones already seen.

When you audit:

- Flag an example that covers one narrow case while the instruction around it stays vague. Recommend fixing the ambiguous instruction instead, so the fix generalizes.

### 1.3 Where an example or template lives

A short example or template used every single time the skill runs belongs inline in the body. Anything long, or only needed in some cases — a full reference document, a large example collection, an API spec — belongs in a separate file. Such a file costs nothing until Claude opens it, so there's effectively no limit on what can be bundled there; the limit applies only to what loads with every invocation.

The folder matters too. `references/` (or a root-level file such as `examples.md`) is for material Claude reads as guidance. `assets/` is for static resources consumed in producing the output itself — a document template, a logo, a data file. A reading-only example collection in `assets/` costs nothing in Claude Code, but on another Agent-Skills-compliant host the file can be copied or filled in, never read.

Point to these files as §4.5 describes. Name a file that only some runs need as a plain path with its condition, never as an `@` reference: an `@path` in a local skill's body is attached when the skill loads, so the file costs context on every run even when the task never needs it. The docs show this behavior indirectly — they state that a skill synced from claude.ai, in a terminal session, does not attach the files its `@` references name — so treat it as the expected behavior for local skills.

Recognize the difference:

**Loads on every run:** `@references/migration-guide.md`

**Loads only when needed:** "Read `references/migration-guide.md` if the project still uses the v1 config."

When you audit:

- Flag a long or conditional example left inline, and recommend the separate file it belongs in.
- Flag reading material placed in `assets/`, and recommend moving it to `references/` or a root-level file.
- Flag every `@` reference to a file that only some runs need, and recommend the plain path with its condition.

### 1.4 How a good example is written

A good example is paired with an explicit rule, not left as a sample to imitate silently. A short closing line — "follow this style: type(scope): brief description" — turns a bare example into something Claude can generalize to a new case with confidence. A good example is also concrete, never abstract. Judge it by picturing Claude imitating it on a new case: same structure, same register. If the result would still need a manual fix, the skill's rule line is missing or too loose, and that line is what to sharpen, not a one-off correction.

Recognize the difference:

**Bad example (vague, nothing to imitate):**
> Write a commit message describing the change.

**Good example (concrete, paired with the rule):**
> Follow this style: `type(scope): brief description`.
>
> `fix(auth): handle expired refresh tokens`

When you audit, flag every example with no rule line that says what to imitate, and every example that is abstract instead of concrete.

### 1.5 Output templates

When Claude must produce output in a specific format, the skill must give it a template, never a prose description of the format. A concrete structure is far more reliable to pattern-match against than a described one. How strict the template reads must match how much deviation is actually acceptable:

- A format that must not vary opens with language like "ALWAYS use this exact structure."
- A format that can flex opens with language like "here's a sensible default — use your judgment."

For a format that must not vary:

> ALWAYS use this exact structure:
> ```markdown
> ## Summary
> ## Findings
> ## Recommendation
> ```

For a format that can flex:

> Here's a sensible default — use your judgment:
> ```markdown
> ## Summary
> ## Notes
> ```

Short templates stay inline in the body. Long ones, or ones only needed in certain cases, go in a separate file referenced from the step that needs them.

When you audit:

- Flag every required output format described in prose, and recommend the template that replaces it.
- Compare each template's opening words with how much deviation the skill can accept, and flag a mismatch in either direction.

### 1.6 How a skill teaches a "don't"

A working skill doesn't teach with paired do/don't examples in its body. Pairing good and bad samples is how documentation *about* skills teaches authors — as this file does — not how a skill talks to Claude. Inside an actual skill, a prohibition is one plain sentence right next to the instruction it limits: "Default the category from the merchant type; ask only if it's ambiguous. Don't paste the full API response." A mistake Claude would otherwise make by default is stated once, concretely, near the top — the pattern a skill's own Gotchas section uses.

When you audit, flag every paired do/don't example inside the skill body, and recommend the one-sentence prohibition, or the Gotchas entry, that replaces it.

---

## 2. Embedded commands and code inside a skill

### 2.1 Freedom matched to fragility

The latitude a step gives Claude must match how fragile and variable the underlying task is. Most skills mix levels across steps, so each step is calibrated on its own, not once for the whole skill.

- **High freedom** (many valid approaches, nothing fragile): plain text instructions, no fixed command.
  > Review the diff for readability, naming and dead code, and report what you find.
- **Medium freedom** (a known shape, details vary): a template command with parameters to fill in.
  > Run `pytest <path> -k <name>`, where `<path>` is the test file and `<name>` the test to rerun.
- **Low freedom** (one exact sequence must be followed, consistency matters more than flexibility): one exact command or script, explicitly marked as not to be altered.
  > Run exactly `./scripts/migrate.sh --dry-run`. Don't add flags.

When a one-off command is complex enough to be hard to get right on the first try, it belongs in a tested script in `scripts/`, not inline.

When you audit:

- For each step, name its fragility, then compare it with the freedom the step gives. Flag every mismatch.
- Flag a complex inline command that should be a tested script.

### 2.2 Commands Claude will run

A command Claude runs must work as written, every time:

- **Versions are pinned** in any command shown (`npx eslint@9.0.0`), so it behaves the same over time instead of drifting with whatever is latest.
- **Prerequisites are stated** in the skill text ("Requires Node.js 18+"), not assumed.
- **No package is assumed installed.** The skill gives the exact install command instead of silently depending on it.
- **Every placeholder is explained** on the next line (what `<sides>` means, what values are valid).
- **Every script says whether to run it or read it:** "Run `analyze_form.py` to extract fields" when Claude only needs the result; "See `analyze_form.py` for the field-extraction algorithm" when Claude needs the logic itself.
- **Every bundled script is listed** in the body with a one-line purpose, and its output format if structured, so Claude never has to discover a script by browsing the folder.

Run versus read — the first line needs only the script's output, the second needs its logic:

> Run `analyze_form.py` to extract fields.
>
> See `validate_boxes.py` for the field-matching algorithm.

For a skill with several scripts, the commands sit directly beneath each script, not scattered through prose. This one runs inside Claude Code, so it uses the skill's directory variable (§2.3):

> **Utility scripts** (requires Python 3.10+)
> - `analyze_form.py` — extract all form fields from a PDF; prints JSON
>   ```bash
>   python3 ${CLAUDE_SKILL_DIR}/scripts/analyze_form.py input.pdf > fields.json
>   ```
> - `validate_boxes.py` — check extracted fields against the form's schema
>   ```bash
>   python3 ${CLAUDE_SKILL_DIR}/scripts/validate_boxes.py fields.json
>   ```

When you audit, walk every shown command through each point above, and flag every one it misses.

### 2.3 Paths and tool names inside snippets

- **Forward slashes, always** — even for a Windows path. A backslash path in skill text is a defect.
- **Every MCP tool name is fully qualified** as `ServerName:tool_name`. An unqualified name risks a "tool not found" error.
- **Script paths outside Claude Code** are relative to the skill's own root directory; the host resolves them from there.
- **Script paths inside Claude Code** use `${CLAUDE_SKILL_DIR}` for a file that belongs to this skill, and `${CLAUDE_PLUGIN_ROOT}` for a file shared across an entire plugin, written so the path still reads as a plain relative path (`${CLAUDE_SKILL_DIR}/scripts/render.py` still looks like `scripts/render.py` to someone skimming). Claude Code substitutes these variables only in the skill's own Markdown content and in the Bash rules of `allowed-tools`, once, over `SKILL.md` as it loads — never in the environment of a command Claude runs, and not in a reference file Claude reads later. A command that uses one of these variables belongs in `SKILL.md`, or the body supplies the resolved path to the reference.

**Won't resolve:** a command in `references/build.md` that uses the skill-directory variable.

**Resolves:** the same command written in `SKILL.md`.

Recognize the difference:

**Bad (unqualified):** `search_docs("skills frontmatter")` — ambiguous when more than one connected server exposes a similarly named tool.

**Good (fully qualified):** `Claude_Code_Docs:search_claude_code_docs("skills frontmatter")`

When you audit, check every path and every tool name against these points, and flag each one that breaks them.

### 2.4 Claude Code-only body syntax

This syntax works only in Claude Code. In claude.ai chat or through the API, the characters and placeholders below reach Claude as literal text.

- An inline command, `` !`command` ``, only executes when the `!` sits at the start of a line or right after whitespace.
- A command spanning multiple lines goes in a fenced block opened with ` ```! ` instead of the inline form.
- A failed injected command aborts the whole skill, so Claude never sees its content. With the default `bash` shell, any non-zero exit counts as a failure, except exit code 1 from search and comparison commands; every other command expected to sometimes exit non-zero needs `|| true` appended.
- A literal `$` before a digit, `ARGUMENTS`, or a declared argument name must be escaped: `\$1.00`. The backslash doesn't stop the substitution of a `${CLAUDE_*}` variable.
- The word `ultrathink` anywhere in the skill content requests deeper reasoning when the skill runs.

Recognize the cases:

**Inert — the exclamation mark follows a character:** `` KEY=!`git branch --show-current` ``

**Runs — it follows whitespace:** `` - Branch: !`git branch --show-current` ``

**Can't abort the skill on findings:** `./scripts/check.sh || true`

When you audit:

- Check every use of this syntax for correctness against each point above.
- Flag any of it in a skill whose surfaces, from the context you established, don't support it.

---

## 3. Shape: prose, bullets, numbered steps, tables

### 3.1 No format is banned — the shape must match the content

No format is restricted in a skill's body. What matters is that the shape matches what the content actually is:

- **A fixed, ordered procedure** (a deployment, a commit flow, any operation where sequence matters) → numbered steps.
- **Standing knowledge applied across many requests** (conventions, domain facts, style rules) → a bullet list under a heading.
- **A short, simple procedure** → plain prose is enough; headings and lists belong only where there's enough structure to need them.
- **A specific output format Claude must match** → a template (see 1.5), never a prose description of the format.

When you audit, name what each block of content is, compare it with the shape it has, and flag every mismatch. Never flag a shape for not following a house style.

### 3.2 Order and headings

The instructions that matter most belong near the top of the body. A loaded skill is never re-read, and after compaction Claude Code keeps only the first 5,000 tokens of each skill, within a 25,000-token budget shared by the most recently invoked skills, so what sits deep in a long body can be lost. Everything below the opening instructions is where the detailed how-to goes.

When you audit:

- Flag a load-bearing instruction that sits deep in the body instead of near the top. When the prompt reports where the body's first 5,000 tokens end, flag every instruction past that point that the skill still needs after compaction.
- Flag any rule that first appears after the step it governs, because by then Claude has already acted.

### 3.3 Tables and tone

No official guidance fixes a table's use inside a skill body, or the tone and grammatical person of the skill's own text. Both are left to judgment. The pattern seen across working skills is to address Claude directly, in the imperative, second person — "Run the tests after every edit," not a passive or third-person phrasing — but that's an observed convention, not a stated rule.

A table pulls its weight when there's a real grid to scan — several items, each compared against the same few properties:

| Field | Required for | Notes |
|---|---|---|
| `name` | all skills | kebab-case, matches directory |
| `license` | marketplace skills | SPDX identifier |

It doesn't for a single linear fact: "the `name` field is required for every skill and must be kebab-case" reads faster as one sentence than as a one-row table.

When you audit:

- Flag a table that has no real grid to scan.
- Check that tone and grammatical person stay consistent across the skill, and flag where they change. Rate this as cosmetic, because no official source rules on it.

---

## 4. Wording and semantics

### 4.1 When a step explains why, and when it just says what

Whether a step explains its reasoning or just states the action depends on how much judgment it leaves open:

- A **flexible, judgment-calling** step explains why. An instruction with its reasoning attached lets Claude make the right call in a situation the skill didn't specifically anticipate.
- A **forced, fragile, must-happen-exactly-this-way** step skips the narration and states only the action. Explaining why a fixed sequence must be followed doesn't make Claude follow it more exactly; it just spends tokens on something that was never a judgment call.

**Flexible, reasoning attached:** "Pick the lighter dependency when two libraries do the same job — this skill runs inside a size-constrained bundle, so every extra kilobyte matters." (The reasoning lets Claude extend the judgment to a library the skill never named.)

**Forced, bare action:** "Run `npm run build` before every commit." (No reasoning attached — the sequence must happen exactly this way regardless of why.)

When you audit:

- Flag a judgment step that gives Claude no reasoning to decide an unnamed case.
- Flag a fixed step that spends lines explaining itself.

### 4.2 How strong a directive should be

The strength of the wording must match how non-negotiable the rule actually is:

- Capitalized, absolute language (MUST, ALWAYS, NEVER) is reserved for true non-negotiables — a strict output template, a security-critical constraint, anything where any deviation is a real failure.
- Everything else is a reasoned default. An instruction that explains why a choice is usually right gets followed more reliably than a blanket ALWAYS/NEVER with no reasoning behind it.
- A rule that has to hold with zero tolerance for a missed case can't be trusted to wording at either strength; it belongs in a hook.

**Reserved for non-negotiables:** "NEVER commit the `.env` file." (A real failure if violated even once.)

**Reasoned default, everything else:** "Prefer `const` over `let` — it signals the binding won't be reassigned, which helps whoever reads this next." (Claude can still choose `let` when the reasoning doesn't apply.)

When you audit:

- Compare every directive's strength with the cost of one deviation, and flag a mismatch in either direction.
- Flag every zero-exception rule that lives only in wording, and recommend the hook.

### 4.3 Standing instructions

Because a loaded skill is never re-read (§3.2), an instruction meant to apply throughout the task must say so explicitly — "Run the tests after every edit," never "Run the tests," which reads as a one-time step and gets followed exactly once.

When you audit, find every instruction meant to hold for the whole task, and flag each one worded as a one-time step.

### 4.4 Forked and preloaded skills start blind

A skill run with `context: fork`, or preloaded into a subagent, hands that subagent the skill's full text with zero conversation history — no memory of what's been discussed, no files already read in the main conversation, nothing. Everything the subagent needs has to be written in the skill itself. A reference to "what we discussed earlier," or any reliance on the main conversation, produces nothing there, because the subagent never had it.

**Relies on history:** "Apply the plan we agreed on."

**Self-contained:** "Apply the plan in `plan.md`; read it first."

When you audit a skill that runs forked or preloaded, flag every passage that relies on conversation history or on files read earlier.

### 4.5 Terminology, clarity, file references

- **Terminology:** one term per concept, used the same way every time it appears. Switching between synonyms for the same thing ("API endpoint," "URL," "route," "path") makes the instructions harder to parse and follow, even where a human reader would find the variation natural.
- **Clarity:** vague catch-all phrasing — "handle errors appropriately," "follow best practices" — gives Claude nothing concrete to execute, so it falls back to generic behavior. The fix is the specific pattern, edge case or convention that actually applies. When Claude ignores an instruction, treat that as a sign the wording is ambiguous, not that Claude failed to try.
- **File references:** a pointer to a file is a concrete trigger tied to a condition — "Read `references/api-errors.md` if the API returns a non-200 status" — not a generic "see references/ for details." A generic pointer is easy to skip past; a conditional one names exactly when to open the file.
- **References to other skills:** another skill is named in full, with whether it's required and when to use it, and its content isn't repeated. A skill distributed to third parties relies only on skills in its own plugin or in a plugin its manifest declares in `dependencies`, because the user may not have any other.

Recognize the difference:

**Drifting terms:** "Call the endpoint… then retry the URL… log the route."

**One term:** "Call the endpoint… retry the endpoint… log the endpoint."

**Unclear skill reference:** "See skills/testing/test-driven-development."

**Clear skill reference:** "Before writing implementation code, use `my-plugin:test-driven-development`; it is required for every change."

When you audit:

- Flag every concept named by more than one term.
- Flag every catch-all phrase, and recommend the specific pattern it should state.
- Flag every file reference with no condition.
- Flag every reference to another skill that doesn't say whether it's required and when, every passage that repeats what that skill already says, and, in a skill distributed to third parties, every reliance on a skill outside its plugin and declared dependencies.

### 4.6 Time-sensitive wording

Nothing that will go stale belongs in the main instructions — a current version number, a UI detail that will get redesigned, "the latest" anything. Historical context worth keeping belongs in its own clearly labeled section (for example, "Old patterns"), so it doesn't contaminate the main instructions once it's outdated.

**Goes stale:** "Use the latest Node version."

**Stable:** "Requires Node.js 18+."

When you audit, flag every time-sensitive claim in the main instructions, and recommend isolating or removing it.

### 4.7 Discipline skills: closing loopholes

Some skills enforce a discipline Claude knows and is tempted to skip under pressure, such as writing the test before the code. In those skills, stating the rule isn't enough: Claude finds the workaround the rule didn't close. Each known workaround is closed explicitly, next to the rule, and the thoughts that signal a rationalization are listed so Claude can catch itself. This pattern comes from third-party skill-writing practice, not from official guidance.

The same tool backfires elsewhere. For output that comes out in the wrong shape, or with elements missing, a pile of prohibitions doesn't help; a template (§1.5) or a positive instruction does.

**Open loophole:** "Write code before the test? Delete it."

**Closed:**
> Write code before the test? Delete it and start over. Don't keep it as reference, and don't adapt it while writing the test.
>
> These thoughts mean stop and start over:
> - "It's too simple to test."
> - "I'll test after."
> - "This case is different."

When you audit:

- In a skill that enforces a discipline, check that each known workaround is closed next to its rule and that the rationalizing thoughts are listed. Where they're missing, propose them as an improvement.
- Flag a list of prohibitions used to fix wrong-shaped output or omitted elements, and recommend the template or positive instruction that replaces it.
- Rate findings under this section Medium at most.

---

## Classifying findings

Give every finding four things: the exact file and line(s) in the skill under audit, the point in this file it violates or falls short of, why it is a defect stated as a consequence (not just "doesn't match the guide"), and a specific fix with the reason it's the right one. If you have no line to point to, you have no finding.

Classify each defect into one of four levels by its actual consequence. The examples below anchor each level; a finding that doesn't match one verbatim still gets the level its own consequence earns.

- **Critical.** Breaks the skill mechanically, or produces wrong behavior every time, not just suboptimal behavior. For example: an inline `` !`command` `` placed where `!` isn't at the start of a line or after whitespace, so it never fires; an injected command that can exit non-zero with no `|| true`, which aborts the whole skill; an unescaped literal `$` before a digit or an argument name; a plugin path variable read from a script's own shell environment instead of written in the Markdown body, where it never resolves; a zero-exception rule written only as skill text instead of a hook; a task-long instruction worded as a one-time step; a skill meant to run forked or preloaded that assumes conversation history it will never have.
- **High.** Doesn't break syntax, but produces a silent, inconsistent failure, or defeats what the skill is trying to do. For example: a script with no stated run-or-read instruction, left for Claude to guess; a required exact output format described in prose instead of given as a template; several options presented as equally valid instead of one default with an escape hatch; vague catch-all wording standing in for the skill's specific guidance; a file reference phrased as a generic pointer instead of a conditional trigger; reliance on a skill the user may not have; an example that contradicts the rule it illustrates; a path variable in a reference file, where it never resolves.
- **Medium.** Costs efficiency, maintainability, or adherence to the pattern, without making the skill wrong. For example: inconsistent terminology for the same concept; a shown command with no pinned version or no stated prerequisite; an example that's abstract instead of concrete; a long example or template left inline instead of moved to a separate file; a directive's strength mismatched, in either direction, to how non-negotiable the rule is; an `@` reference to a file only some runs need; an example longer than it needs to be, or a second example of the same pattern; misapplied discipline hardening.
- **Low.** Cosmetic, or a minor staleness risk, with no real behavior consequence. For example: wording that will go stale left in the main instructions instead of isolated; heading order that could be tightened but doesn't bury anything load-bearing; a tone or grammatical-person inconsistency, which no official source rules on.

## Improvement opportunities

Separate improvement opportunities from defects: an opportunity is something correct and working that a stronger pattern in this file would improve, or a pattern the skill's purpose needs and the skill lacks. Report one only where it genuinely applies to this skill; this section of your report may stay empty. For each one, give what exists now (or that it is absent, and where it belongs), what this file recommends instead, and why that's actually better for this specific skill, given its purpose and its audit context — never a generic "could be better."

This file gives you the rules, the context to establish, and the severity model. The gotchas and the verification checklist live in your own instructions, and the report template lives in this skill's `assets/` folder, so they aren't repeated here.

## Delivering the report

Deliver every defect and improvement opportunity in the findings template, `assets/audit-report.md` in this skill. Fill one defect block per defect, with every field, and keep the template's structure exactly.
