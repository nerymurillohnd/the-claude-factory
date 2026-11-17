# Name and description

Until a skill loads, its name and description are all Claude has of it. Claude matches each request against every description it can see and loads the skills that fit; the body, references and scripts arrive only after that choice. So the description is a router, not a summary: an excellent body behind a description that doesn't match the request never runs, and one that matches the wrong requests loads where it doesn't belong.

## Contents

- 1. The name
- 2. What the description must carry
- 3. Words that match real requests
- 4. Boundaries against near-misses and siblings
- 5. Length and the listing
- 6. `when_to_use`
- 7. Input at invocation
- 8. The body's first lines
- 9. Questions to ask yourself

## 1. The name

- Use the strictest format, the Agent Skills specification's, whatever the target: lowercase letters, digits and single hyphens, no hyphen at either end, within its length limit. A name in that form is valid on every surface; Claude Code accepts more, but an upload or another client may not.
- Keep the name equal to the skill's folder name. The specification and uploads require it; in Claude Code a different `name` makes the skill answer to two names.
- Leave the words `claude` and `anthropic` out of any skill that may be uploaded to claude.ai or the Skills API: uploads refuse them even though Claude Code loads the skill.
- Name the activity and its object (`reviewing-migrations`, `drafting-release-notes`). The platform suggests the gerund; a noun phrase or an action form also works. Inside a plugin or folder, follow the pattern the sibling skills already use rather than imposing a new one.
- Avoid names that fit anything (`helper`, `tools`, `documents`), and names that promise a different job than the description: Claude reads both when choosing.
- Check for collisions before settling. A bare name that matches a skill the user probably already has, a bundled command or a built-in command decides which one runs when they type it, and the two compete for the same requests. Read the current resolution order on the Claude Code skills page, or in the shared table the main skill file points to.

## 2. What the description must carry

- What the skill does, as concrete capabilities: the operations, inputs and outputs that tell it apart from its neighbors.
- When to use it, as the user's goal or situation, not the skill's internal steps.
- Third person throughout ("Drafts release notes…"). A "Use when…" clause is fine; "I can help you…" and "You can use this to…" are not, because the description is injected into the system prompt and a shifted voice there hurts discovery.
- Nothing about implementation: libraries, script names and internal phases match no request and take the room the triggers need. Move them to the body, and runtime requirements to `compatibility`.
- Only what the body does. A description that promises a job the body doesn't handle loads the skill for tasks it can't serve; a job the body handles that the description never names never gets routed.
- No angle brackets: uploads reject XML-like text and Claude Code escapes it, so `<branch>` reaches Claude as `&lt;branch&gt;`. Write `[branch]` or "a branch name". Write arrows and comparisons in words for the same reason.

Recognize the difference:

- Mechanics, no trigger: `Uses the changelog parser to diff tags and render a template.`
- Capabilities and intent: `Drafts release notes from the commits and merged pull requests since the last tag. Use when the user asks for release notes, a changelog entry or a summary of what shipped in a version.`

## 3. Words that match real requests

- Write the terms a real request would contain: file types and extensions, product and tool names, everyday verbs. A description that says "tabular data" misses users who say "spreadsheet", "CSV" or ".xlsx".
- Leave out the author's vocabulary: project codenames, the skill's own coined terms and internal process labels match nothing users type.
- When users ask for the job without naming its domain ("my manager wants this cleaned up for the board"), say so in the description ("even when they don't mention…").
- Generalize instead of copying: phrases lifted from particular test requests fit those phrasings and miss new ones. Name the category they share. Short quoted phrases that many users would type for this job are fine.
- Aim at the requests that need the skill's knowledge. A description that leads with a simple one-step task Claude does alone triggers unreliably for it.

## 4. Boundaries against near-misses and siblings

A near-miss is a request that shares the description's words but needs something else: another operation, another format, another skill's job.

- Build the plausible near-misses from your own description's nouns, and make sure the text alone keeps each one out: by sharpening the what and when, or with an explicit "Not for…" that names the neighbor's territory in the user's terms.
- Don't add exclusions for requests nobody would confuse with the skill; they route nothing and cost room.
- When the skill has siblings in the same plugin or folder, read all their descriptions side by side before writing yours. For any request two of them would both claim for different work, make each state what separates it: the input, the stage of the work, the target or the outcome. Two skills that do different parts of one task may both load; that is intended.
- Don't write an umbrella description ("use for any work on X") next to narrower skills on X, and don't restate the plugin's overall purpose in each sibling: neither separates anything.

Recognize the difference (two skills in one plugin):

- Competing: both say `Use when the user wants to check a skill.`
- Separated: one writes and changes skills and says `Not for auditing or reviewing a skill`; the other audits, and says it is not for writing one.

## 5. Length and the listing

- Hard limit for uploads and the specification: 1,024 characters. Claude Code enforces no length for its own use, but a skill that may be uploaded must stay within it.
- Recommended: about 100 tokens for name and description together, roughly 400 characters. Treat it as a target, not a rule; past it, cut what doesn't help decide when to use the skill, never the key use case or the boundaries.
- Claude Code cuts each listing entry (description plus `when_to_use`) at a fixed length, and the whole listing shares one budget for every installed skill; when it overflows, descriptions of the least-used skills drop first. Put the key use case in the first sentence so it survives any cut. Check the current figures on the Claude Code skills page.
- Every model-invocable skill costs its description on every turn of every session. A skill only a user ever starts by typing its command should not pay that cost; see the frontmatter guide on who may invoke it.

## 6. `when_to_use`

- A Claude Code-only field, appended to the description in the listing. Use it only for a skill served solely by Claude Code, when trigger phrases or example requests would otherwise bury what the skill does.
- For any skill also served elsewhere (claude.ai, the Skills API, other clients), put the triggers in the description instead: elsewhere the field doesn't route, and an upload that carries it fails.
- Spell it exactly `when_to_use`; a misspelled key is ignored silently. Don't repeat or contradict the description in it.

## 7. Input at invocation

- `argument-hint` and `arguments` are Claude Code-only. Add them only when the skill takes input the user types after the command; a skill with no input gets neither.
- `argument-hint` is what autocomplete shows, such as `[issue-number] [branch]`. A value that starts with `[` must be quoted in YAML, or it parses as a list.
- `arguments` names positions in order, so the body can write `$issue` instead of `$0`. Every named placeholder in the body must be declared, and every declared name used; keep the order the hint shows.
- With no placeholder in the body, Claude Code appends the input as `ARGUMENTS: <value>`, so a skill can take free-form input without declaring anything.
- No source documents how placeholders render in a skill preloaded into a subagent, since no invocation passes it arguments: don't make such a skill's body depend on them.
- Read the current substitution rules on the Claude Code skills page before using indexed placeholders, escapes or `${CLAUDE_*}` variables.

## 8. The body's first lines

When Claude opens the body it knows only what the description promised and what the user asked. Start the body by taking up that task in the description's own terms and naming Claude's first move. A body that opens on background, history or a different framing makes Claude reconcile the two before it can begin.

## 9. Questions to ask yourself

- From the description alone, would Claude pick this skill for each gap request, and pass it over for each near-miss?
- Could the same words describe another skill the user has?
- Does every job the description names exist in the body, and every job in the body appear in the description?
- Would a user type these words?
- Does the first sentence still carry the key use case if the rest is cut?
- Does the name resolve to this skill on every target, and is it valid for every upload route?
