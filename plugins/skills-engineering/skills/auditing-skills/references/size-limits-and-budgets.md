# Size limits and budgets

This file teaches you how to audit every length, line, token, byte and count ceiling that applies to a skill on the surfaces it targets, and what happens when the skill crosses one: rejected, truncated, dropped or silently disabled. It covers its frontmatter field lengths, its `SKILL.md` body, its supporting files, its upload and install size, how many skills can be active at once, the output of its scripts and injected commands, and the budget of its frontmatter hooks. Each section gives you the principle, why it matters, and what to do when you audit. How a skill's files are discovered, resolved and loaded is runtime-contract.md's; the order of the skill's instructions and how its commands are written are content-patterns.md's; eval and test design are outside this file. Leave them out of your findings.

## Contents

- How to use this file
  - Before auditing: establish the context
  - Then, audit area by area
- 1. Frontmatter field lengths
  - 1.1 Upload gates
  - 1.2 The Claude Code skill listing
- 2. `SKILL.md` body size
- 3. Catalog cost at startup
- 4. Context after invocation and after compaction
- 5. Supporting file size and splitting
- 6. Upload and install size limits
- 7. How many skills can be active at once
- 8. Output size and time of scripts and injected commands
- 9. Frontmatter hooks: registration budget and output caps
- 10. Figures no official source states
- Classifying findings
- Improvement opportunities
- Delivering the report

## How to use this file

Read this whole file, through its final section, "Delivering the report", before you judge anything. This complete reading, and an audit of the skill against every point in it, are a precondition of your audit: no point stays unaudited. Keep to the file's order: first establish the context, then audit area by area, then classify what you found.

Audit from the seat of a Claude that loads the skill with no prior context, on each surface the skill targets, and has to use it. Ask, for every ceiling, whether that Claude would meet the skill rejected, truncated, missing its descriptions, missing its instructions after compaction, missing a preloaded skill, flooded by a script's output, or running without its hooks.

The prompt you receive carries the measurements the orchestrating model's scripts took: character counts of the frontmatter fields, including the combined `description` and `when_to_use` count and where its 1,536th character falls, the body's line and approximate token counts, where the body's first 5,000 tokens end, line counts of the supporting files and which of them lack a table of contents, the bundle's size and file count, the hook totals of the skill's source, and the length of any preload list shipped with it. Take those figures as measured and judge what they mean on each target. Measuring is the scripts' work: never count characters, lines, tokens or bytes yourself. When the prompt lacks a measurement a point needs, record it once under Checklist exceptions as blocked, naming the missing measurement, set Status to incomplete, and judge everything else. Settle by reading every other point within your reach: a point the prompt or the files could settle and you left unverified is a failure of the audit. Report a point as unverified only when neither can settle it, say why, and name the check that would settle it, such as `/doctor` or the Skills row of `/context` for the listing, `/skill-doctor` for each skill's cost, `claude plugin details` for a plugin's projected cost, `--debug` for dropped descriptions or unregistered hooks, or a test upload. Never present a size as fine, or as too large, without a figure behind it.

### Before auditing: establish the context

Almost every number in this file belongs to one surface. Settle these four points before you apply any ceiling; they decide which numbers govern the skill in front of you.

1. **Where the skill lives and which surfaces load, run or validate it.** Claude Code (terminal, IDE, desktop app or a cloud session) enforces different ceilings than a skill uploaded to claude.ai or the Skills API, which differ again from a skill attached to a Managed Agent or a plugin installed in the Claude app. A number stated for one surface doesn't transfer to another: the spec's cap on `description` and Claude Code's listing cap (§1) are two different gates. Treat a surface the skill names, or one its distribution route implies, as a target; a surface it might reach someday is a possible target (see "Classifying findings").
2. **Whether the skill is invoked or preloaded.** An invoked skill keeps only its name and description in context until it's used. A skill preloaded into a custom subagent's `skills` list loads its full content at that subagent's startup. This decides which cost in §3 and §4 applies, and whether the preload cap in §7 is in play.
3. **Which other skills share its source.** The hook budget is per source, where a project, a personal skills folder and each plugin count separately, so a skill that looks fine alone can lose its hooks because a sibling from the same source used the budget first (§9).
4. **What the skill is actually trying to do and whether it will be packaged or uploaded.** Use its purpose to decide which areas apply, and never flag an absence the skill never had a reason to fill. Ceilings Claude Code doesn't enforce apply the moment the same files are uploaded or shipped in a plugin.

### Then, audit area by area

Audit what the skill has, and also what it should have. In each area, start from the skill's targets and purpose, ask what its size and budgets need to hold on every target, compare that with what the skill and the measurements show, and give every item exactly one of these outcomes:

- **Present and optimal.** It stays within every ceiling that governs it, the way this file describes. Record no finding.
- **Present but wrong.** It crosses a ceiling on a target, applies another surface's number to this skill, or carries content that shouldn't be in it at all. Record it as a defect, classify it (see "Classifying findings"), and say whether it must be deleted, rewritten or moved.
- **Present, right, but improvable.** It is within every ceiling, but a better budgeting pattern from this file would serve the skill's targets. Record it as an improvement opportunity, with the adjustment it needs.
- **Absent, and the skill's targets need it.** Record it as an improvement opportunity: say exactly where it belongs, what it should contain, and cite the point of this file it rests on.
- **Absent, and the skill's targets don't need it.** Record no finding.

An absent pattern is a defect when its absence causes a documented failure or breaks a stated guideline on a target, such as a missing table of contents on a reference over 100 lines; otherwise it is an improvement opportunity.

Work only from what the skill and the measurements actually show, never from an assumption that it's "probably fine." If you have no line or figure to point to, you have no finding.

---

## 1. Frontmatter field lengths

### 1.1 Upload gates

The Agent Skills spec and every upload surface validate the frontmatter; a field over its length rejects the whole upload:

- **`name`:** 1–64 characters.
- **`description`:** 1–1,024 characters. The help center's article on creating custom skills gives a 200-character maximum for a claude.ai upload, while the Claude Code docs say claude.ai uploads follow the spec; for a claude.ai target, report a description between 201 and 1,024 characters as unverified, with a test upload as the check that settles it.
- **`compatibility`:** 1–500 characters when present.
- **`display_name`:** a Skills API field, not a frontmatter field. It may be up to 255 characters and needn't be unique; when omitted, it derives from `name`. The older `display_title` was capped at 64 characters and unique, so its rules don't apply to `display_name`.

When you audit:

- For each measured field, name the targets whose gate it crosses, and flag every crossing on a target the skill is or will be uploaded to.
- Claude Code enforces none of these lengths. Flag a skill, or its documentation, that cites one against a skill that only runs in Claude Code.

### 1.2 The Claude Code skill listing

Claude Code puts every skill's name and description into a listing so Claude knows what's available. Each entry's combined `description` and `when_to_use` text is capped at 1,536 characters, configurable with `skillListingMaxDescChars`. The whole listing has a budget of 1% of the model's context window, configurable with `skillListingBudgetFraction` or the `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable. The budget is one for the whole session, shared by every installed skill. When the listing overflows, Claude Code keeps every name but drops descriptions, starting with the least-invoked skills, and also writes a warning to the debug log. A dropped description takes with it the keywords Claude matches requests against.

When you audit:

- Flag a description whose key use case sits past the measured 1,536-character cut, and recommend putting the key use case first.
- Flag, as a risk to the shared budget, a plugin whose many model-invocable skills carry long descriptions, and recommend shorter descriptions or fewer model-invocable skills. `skillOverrides` doesn't affect plugin skills and is a user setting, so never offer it as the author's fix.

---

## 2. `SKILL.md` body size

Keep the `SKILL.md` body under 500 lines: the platform's best practices give it as practical guidance "for optimal performance", with splitting into separate files as the remedy when content approaches it, and no surface rejects a longer body. The skill-content table of the Skills overview puts the instructions level at under 5,000 tokens; that figure is a size guideline, separate from the 5,000 tokens compaction keeps (§4), and that they share a number is a coincidence (inferred: no source links them). Both guidelines are recommendations, never validation rules. They exist because the body stays in context once loaded (§4), so every line is a recurring cost. Whether an oversized body holds an example or template that belongs in a separate file is content-patterns.md's judgment.

Recognize the difference:

**Wrong severity:** "The body has 612 lines, over the limit: Critical."

**Right severity:** "The body has 612 lines, past the 500-line recommendation; its migration tables are needed only for migrations and can move to `references/`: Medium."

When you audit:

- Flag a body past either recommendation, at Medium at most unless you can show a concrete failure it causes, and name what can move out and where.
- Flag a skill or its documentation that presents either figure as a hard limit.

---

## 3. Catalog cost at startup

At session start, every installed skill a model can invoke costs its name and description in context on every turn, whether or not it's used: about 100 tokens per skill, per the Skills overview. A plugin's skills, agents and commands that Claude can invoke on its own all add to this per-turn cost. `disable-model-invocation: true` takes a skill out of this cost.

When you audit:

- Flag a skill that only runs when the user types its command yet stays model-invocable, paying the per-turn cost for nothing, and recommend `disable-model-invocation: true`; the preload consequence of that field is runtime-contract.md's.
- Flag a plugin that splits one purpose across many small skills whose combined catalog cost a single skill with references would avoid.

---

## 4. Context after invocation and after compaction

An invoked skill's rendered body enters the conversation as one message and stays there, never re-read. Re-invoking it with identical rendered content adds a short note instead of a copy; when the content differs, because the arguments changed or an injected command produced new output, the full content is appended again. A preloaded skill pays its full content at the subagent's startup instead.

When auto-compaction summarizes the conversation, Claude Code re-attaches the most recent invocation of each skill, keeping the first 5,000 tokens of each, within a combined budget of 25,000 tokens filled from the most recently invoked skill backwards. Whatever lies past a skill's first 5,000 tokens is gone after compaction, and a skill invoked early in a session with many invoked after it can be dropped entirely.

Which instructions are load-bearing, and whether content past the measured cut must move up, is content-patterns.md's judgment: it receives the same measurement. Here, judge the re-invocation cost and the shared budget.

When you audit:

- Flag a skill whose rendered content changes on every invocation, through an argument or an injected command, in a workflow that re-invokes it often: each call appends the whole body again.
- Flag a skill meant to run alongside many others in long sessions that relies on staying attached after compaction, though the shared 25,000-token budget can drop it entirely, and recommend a body short enough to survive or a workflow that re-invokes it when needed.

---

## 5. Supporting file size and splitting

No source caps the size of a file in `references/`, `assets/` or `scripts/`, and none of it costs context until it is read; a script's source never enters context, only its output. The one threshold: a reference file over 100 lines needs a table of contents at the top, so Claude sees the file's full scope even when it previews it with a partial read such as `head -100`.

Size alone is never the reason to split. "Bundled content costs nothing until read" argues for complete files; "smaller files cost less once read" argues for splitting. Both hold, because they describe different costs. Decide by access pattern: split a file that bundles independent lookups different tasks trigger separately, and keep together what one task needs at once.

Recognize the difference:

**Split by size:** "`api.md` has 900 lines; split it into three files of 300."

**Split by access:** "`api.md` holds the billing, reporting and admin endpoints, and each task reads only one group; split it into `billing.md`, `reporting.md` and `admin.md`, each named at the step that needs it."

When you audit:

- Flag every reference file the prompt reports over 100 lines without a table of contents, and name the sections a partial read would not show.
- Flag a reference file that bundles lookups different tasks need separately, and recommend the split by access pattern.
- Flag a split that scatters what one task always needs together across several files.
- Never flag a supporting file for its size alone.

---

## 6. Upload and install size limits

These are validation rules: crossing one rejects the whole upload or install.

- **Skills API:** at most 30 MB per skill upload, all files combined, uncompressed.
- **Plugins in the Claude app:** up to 5,000 files and 200 MB per plugin; 200 MB is also the largest file **Upload plugin** accepts.
- **Claude Code, `archive` plugin source:** the zip downloads up to 256 MiB, with 120 seconds for the server to respond and at most five redirects. The install then fails past 100,000 files and directories, 512 MiB for any one file uncompressed, 1 GiB uncompressed in total, or uncompressed content 50 times the zip's size.
- **Claude Code, `command` plugin source:** in the default copy mode, the install fails when the directory is larger than 256 MiB or has more than 20,000 entries; in link mode nothing is copied and these limits don't apply.
- **Claude Code, `url` marketplace source:** the `marketplace.json` downloads up to 5 MiB, with 10 seconds for the server to respond. This limits the manifest, not a skill.

When you audit:

- For the measured bundle, name the routes the skill ships through, and flag every limit it crosses on one of them.
- Flag a skill, or its documentation, that applies one route's limit to another, such as the `archive` extraction limits cited for a git-sourced plugin.
- Flag large data bundled in a skill that targets the Skills API or the Claude app, where it counts against the upload limit even though it costs no context.

---

## 7. How many skills can be active at once

None of these counts are interchangeable:

- **Skills API:** up to 20 skills per request, a hard cap on the request.
- **Managed Agents:** up to 500 skills per session, counted as the deduplicated set across every agent in it. Mounting more skills slows the session's sandbox startup.
- **A custom subagent's `skills` preload field:** the full content of up to the first 32 distinct names is injected at startup; names past the 32nd aren't preloaded.
- **Claude Code's listing:** no count ceiling, only the character budget of §1.2.
- **Stacked invocations at the terminal prompt:** the first skill plus up to five more in one message expand together. This is per-message behavior, not a session or request ceiling.

When you audit:

- Flag a skill, or a subagent shipped with it, that relies on more skills than its target allows, such as a preload list whose needed skill sits past the 32nd name.
- Flag a skill, or its documentation, that cites one surface's count against another surface.
- Flag a Managed Agents setup that attaches skills an agent doesn't need, and recommend attaching only what each agent uses.

---

## 8. Output size and time of scripts and injected commands

An injected `!` command runs through the Bash tool, or the PowerShell tool, with the same timeout and output handling as Claude's own commands. It runs under the default 2-minute timeout: a command the Bash tool moves to the background lets the skill render and names the file collecting its output, and one it kills at the timeout aborts the invocation. A valid result stays inline up to roughly 30,000 characters. Past that, Claude gets the path of a file saved to the session directory and a preview of up to the first 2,000 characters, and reads the file when it needs the rest. A failed command's output stays inline up to roughly 10,000 characters, as a head-and-tail excerpt with no file. These figures are the defaults; `bashOutputMaxChars` raises the inline ceiling up to 128,000 characters (Claude Code v2.1.261 or later). A bundled script that Claude runs through the Bash tool meets the same output limits, but not the fixed timeout: Claude sets a longer timeout for its own commands when it expects one, up to a ten-minute ceiling by default.

So a script that can print more than the inline limit hands Claude a preview and a file instead of its answer. Defaulting to a summary or a bounded result, with an option to ask for more, keeps the answer inline; this is inferred from the Bash tool's limits above, not stated as skill guidance by the official docs.

When you audit:

- Read every bundled script and every injected command the skill runs, judge whether its output can exceed the inline limits on a realistic input, and flag one that can.
- Flag an injected command that can run past the two-minute default on a realistic input, and a bundled script that can run past the Bash tool's ceiling, or that runs long without the skill telling Claude so.
- For a script that can produce large output, recommend a summary or a bounded default and an option to request the rest.

---

## 9. Frontmatter hooks: registration budget and output caps

- **Registration budget:** in Claude Code v2.1.304 or later, each source of skills, where the project, the personal skills folder and each plugin count separately, can register at most 1,024 hooks per session, whose matchers total at most 16,384 characters. A matcher with several hooks under it counts once per hook. Both totals build up skill by skill as skills are invoked, and a skill that would go past either one registers none of its hooks: `/hooks` lists none of them, and the debug log has a line saying it "registers none of its hooks." Which skills lose their hooks therefore depends on invocation order. The fix is fewer hooks or shorter matchers across that source's skills, then a new session; until then, invoking the needed skill before any other skill from its source keeps its hooks.
- **Output caps:** a hook's `additionalContext`, `systemMessage` and `initialUserMessage` strings, and its plain stdout, are capped at 10,000 characters. Past that, except for PreCompact stdout, Claude Code saves the output to a file in the session directory and passes the path with a preview of up to the first 2,000 characters, and it doesn't ask Claude to read the file; unlike the Bash tool's limit, this cap can't be raised. Notes the hooks attach to one tool call for the auto-mode classifier share a 2,000-character cap across every hook that responds to that call.

When you audit:

- With the source's measured totals from the prompt, flag a skill whose hooks can go unregistered because it or its siblings push the source past either budget, name the invocation order that triggers it, and give the fix above.
- Flag a skill hook whose output can exceed 10,000 characters while the skill needs Claude to act on all of it.

---

## 10. Figures no official source states

No official source gives a figure for these:

- The tokenizer or method behind the approximate figures in this file, such as the ~100 tokens per skill and the 5,000- and 25,000-token budgets.
- Whether the 500-line guidance counts the frontmatter; the best practices speak of the body.
- Whether the 1,536-character cap is counted before or after angle-bracket escaping, and whether it counts the text that joins `description` to `when_to_use`.
- The context fill that triggers auto-compaction.
- What a plugin's context-cost estimates measure, methodologically.
- Size limits for a claude.ai skill ZIP uploaded through the settings UI, or for a plugin from a git source.
- Container, package or size limits for a skill run through the API's code-execution tool, beyond the upload limit and the absence of network and runtime installs.

When you audit:

- Flag a skill, or its documentation, that states one of these figures as fact.
- Cite none of them as fact in your own findings.

---

## Classifying findings

Give every finding four things: the exact file and the measured figure or line in the skill under audit, the point in this file it violates or falls short of, why it is a defect stated as a consequence on a named target, and a specific fix with the reason it's the right one. If you have no figure or line to point to, you have no finding.

Classify each defect by what it does to the skill on the surfaces it targets. Ask these questions in order and stop at the first yes:

1. Is the skill rejected, not installed, or a component of it not registered at all on a target? Assign Critical. For example: a `description` over 1,024 characters in a skill uploaded to the Skills API; a bundle over 30 MB for the Skills API; a skill whose hooks go unregistered because its source passes the registration budget.
2. Does it load, but with something it needs truncated, dropped, cut off or missing on a target? Assign High. For example: a description whose key use case falls past the listing cut; a preload list whose needed skill sits past the 32nd name; a script whose output overflows the inline limit where Claude needs the whole answer; documentation that cites the wrong surface's limit and leads the user to a broken setup.
3. Is it within every limit but wasting budget, breaking a guideline, or risking a future limit? Assign Medium. For example: a body past the 500-line or 5,000-token recommendation with content that can move to `references/`; a reference file over 100 lines with no table of contents; a reference file that bundles independent lookups; a user-only skill that stays model-invocable.
4. Otherwise, assign Low. For example: documentation that states a recommendation without saying it isn't a validation rule.

Tie-breaks:

- If a finding fits two levels, the first level in the list wins.
- A departure from a recommendation alone never raises a finding to Critical or High; only a crossed validation limit or a documented behavior that fails can.
- A surface the skill doesn't target gets no finding. A possible target, one the skill might reach without naming it, gets Medium at most, such as a `compatibility` string over 500 characters in a skill that only runs in Claude Code today.
- When the consequence differs by target, set the severity of the most affected target, and name each affected target with its consequence in the finding.
- A point that neither the prompt nor the files can settle is Medium. Name in its finding the level it would reach if the measurement fails.

Never invent impact, never inflate a severity to make the report look decisive, and never lower one because a workaround exists. When several symptoms share one root cause, report the root cause once and list every affected location.

## Improvement opportunities

Separate improvement opportunities from defects: an opportunity is something within every ceiling that a better budgeting pattern in this file would improve, or a budgeting pattern the skill's targets need and the skill lacks. Report one only where it genuinely applies to this skill; this section of your report may stay empty. For each one, give what exists now (or that it is absent, and where it belongs), what this file recommends instead, and why that's actually better for this skill on its targets, never a generic "could be smaller."

This file gives you the ceilings, the context to establish, and the severity model. The gotchas and the verification checklist live in your own instructions, and the report template lives in this skill's `assets/` folder, so they aren't repeated here.

## Delivering the report

Deliver every defect and improvement opportunity in the shared findings template, `assets/audit-report.md` in this skill. Fill one defect block per defect, with every field, and keep the template's structure exactly. Symptoms with one root cause are one defect: give its first location in File and Lines, and list every other location, as `path:lines`, in Finding.
