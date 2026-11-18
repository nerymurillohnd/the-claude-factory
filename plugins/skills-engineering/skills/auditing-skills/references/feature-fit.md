# Feature fit

This file teaches you how to audit whether what a skill contains belongs in a skill, given the project or environment the skill lives in. Each piece of a skill is a choice of feature: an instruction Claude loads on demand, where it could instead be always-on context, a path-scoped rule, a hook or permission rule the harness enforces, a subagent or forked run, an MCP server, or an output style. You judge each piece against the official guidance on which feature fits which job, compare the skill cross-wise with the CLAUDE.md files, rules, skills, subagents, hooks and MCP servers around it, and look the other way too: for content in the environment that belongs in the skill, or that should become a skill of its own. You audit and propose. You never create, move or convert anything. Each section gives you the principle, why it matters, and what to do when you audit.

## Contents

- How to use this file
  - Before auditing: establish the context
  - Then, audit area by area
- 1. Inventory the environment and establish the mode
  - 1.1 How your inputs reach you
  - 1.2 Mode with environment: what the inventory must cover
  - 1.3 Mode without environment
- 2. How to judge fit
  - 2.1 Weighed by Claude or enforced by the harness
  - 2.2 When the content has to be in context
  - 2.3 Most fit guidance is heuristic
- 3. Direction 1: content that belongs in another feature
  - 3.1 A rule that must hold every time belongs in a hook or a permission rule
  - 3.2 Facts every session needs belong in always-on context
  - 3.3 Guidance for one part of the codebase belongs in a path-scoped rule
  - 3.4 Side work belongs in a subagent or a forked run
  - 3.5 Access to an external system belongs in an MCP server
  - 3.6 How every response reads belongs in an output style
  - 3.7 What rightly stays in the skill
- 4. Overlap and conflict with the environment
  - 4.1 Duplication between the skill and the environment
  - 4.2 Contradictions between the skill and the environment
  - 4.3 Instructions that fight or ignore what the environment enforces
  - 4.4 Features the skill relies on but the environment may not have
- 5. Direction 2: environment content that belongs in the skill
  - 5.1 Procedures in always-on files that belong to the skill's domain
  - 5.2 Content that should become a skill of its own
  - 5.3 Subagents and other skills that should feed or absorb the skill
- 6. Recommending for a skill that is distributed
  - 6.1 What a plugin can and can't ship
  - 6.2 Recommending CLAUDE.md and rules as output
  - 6.3 Surfaces that skip a component
- Classifying findings
- Improvement opportunities
- Delivering the report

## How to use this file

Read this whole file, through its final section, "Delivering the report", before you judge anything. This complete reading, and an audit of the skill against every point in it, are a precondition of your audit: no point stays unaudited. Keep to the file's order: establish the context and the mode (§1), fix the criteria (§2), judge the skill outward (§3), against the environment (§4) and from the environment inward (§5), adjust each recommendation for distribution (§6), then classify what you found.

Audit from the seat of a Claude that loads the skill with no prior context and has to carry it out, inside the environment the inventory describes. At each point of the skill, ask what that Claude has in context at that moment: what loaded at session start, what loads only when a file is touched or a skill is invoked, what a subagent starts with, and what the harness does whatever Claude decides. A piece of content is in the wrong feature when that Claude would lack it where it needs it, carry it where it doesn't, or be trusted to follow it where only enforcement would do.

You judge by reading. The environment's configuration reaches you as an inventory in the prompt, which the main session built: take it as verified and judge what it means. When a point needs an inventory item the prompt doesn't give, record it under Checklist exceptions as blocked, name the item that would settle it, and judge everything else by reading. Where only a run would settle a point, such as whether a hook actually fires, name that check instead of guessing its result.

### Before auditing: establish the context

What fits where depends on the environment in front of you, so settle these five points first.

1. **The mode.** With environment, when the prompt gives you the environment the skill lives in; without environment, when the skill is audited alone, for example from a URL (§1.3).
2. **Where the skill lives and how it reaches its users.** A personal, project or managed skill in one environment, or a skill distributed to third parties in a plugin or as an upload. Distribution changes the form a recommendation takes (§6).
3. **How the skill is invoked.** Inline in the main conversation, forked with `context: fork`, or preloaded into a subagent. A forked or preloaded run starts without the conversation, and a subagent doesn't receive the main conversation's output style or auto memory.
4. **Which surfaces load it.** Some components are skipped on some surfaces (§6.3).
5. **What the skill is for**, from its description and body: the task it does or teaches, the output it delivers, and the situations it distinguishes. Every fit judgment is made against this purpose, and so is every Direction 2 proposal: content outside the skill's domain is not your job.

### Then, audit area by area

Audit what the skill has and what it should have, with the same care for each: a piece that would work better in another feature, an enforcement the skill's purpose needs and lacks, or environment content the skill should absorb is as much your job as a misplaced rule. For every point in this file, give exactly one of these outcomes:

- **Present and optimal.** The content sits in the feature that fits its job, and agrees with the environment. Record no finding.
- **Present but wrong or excess.** It sits in a feature that makes Claude act wrongly, duplicates or contradicts an environment file, or enforces what should be judgment. Record it as a defect, classify it (see "Classifying findings"), and say whether it must be deleted, rewritten or moved, and to which feature.
- **Present, right, but improvable.** It works where it is, but another feature, or a better split between features, would serve the skill's purpose better. Record it as an improvement opportunity, with the exact content of the recommendation written out.
- **Absent, and the skill needs it.** An enforcement, a stated dependency, a pointer to an environment file, or content from the environment that the skill's purpose calls for. Record it as an improvement opportunity, or as a defect where its absence makes Claude act wrongly: write out the exact text and where it goes, and cite the point of this file it rests on.
- **Absent, and the skill doesn't need it.** Record no finding. Never recommend a feature by default: a hook, a subagent, a rule or an MCP server each carries cost and upkeep, and a skill that does its job with instructions alone needs none of them.

Work only from what is written in the skill and given in the inventory. If you have no line to point to, you have no finding; for missing content, point to where it belongs. Where nothing in the skill or the environment shows what the missing content should say, name the decision the author has to make, and invent nothing.

---

## 1. Inventory the environment and establish the mode

### 1.1 How your inputs reach you

You read the skill's files, and the Markdown instruction files of the environment, directly: `CLAUDE.md`, `CLAUDE.local.md`, the files in `.claude/rules/`, other skills, and subagent definitions. You never open a file that can hold credential values: `settings.json`, `settings.local.json`, `managed-settings.json`, `.mcp.json` and `~/.claude.json`, which also stores MCP server configurations and account details. Hooks, their events, matchers and sources, MCP server names, permission rules and the active output style reach you only through the main session's inventory. Reads outside the working directory, such as `~/.claude/`, aren't approved by default and can prompt the user, and you can't answer a prompt, so the main session reads those locations for you and passes what you need. Reading a credential file, or stalling on a prompt, would expose secrets or block the audit, and neither would add a fact the inventory doesn't already carry.

When you audit:

- Read every Markdown instruction file the prompt names, in full, before you compare the skill with it.
- Take hook, MCP, permission and output-style facts only from the inventory. Never open a settings, MCP or credential file to check one, even when its path is in front of you.
- Flag nothing that rests on a configuration file you weren't given. Record the missing inventory item under Checklist exceptions as blocked, and say which finding it would settle.
- Recommend, where a finding depends on configuration the inventory doesn't cover, the exact item the main session should add, for example "The inventory needs the project's `PreToolUse` hooks and their matchers, to settle whether `.env` edits are already blocked."

### 1.2 Mode with environment: what the inventory must cover

Features layer. CLAUDE.md files at every level are concatenated into context and none overrides another, and when they conflict Claude uses its judgment and may pick either. Hooks from every source merge, so all of them fire. Unscoped rules load at session start like CLAUDE.md, path-scoped rules load when Claude touches a matching file, and a subdirectory's CLAUDE.md loads when Claude works there. You can only judge whether the skill duplicates, contradicts or depends on its environment once you know every layer that reaches the session the skill runs in.

When you audit:

- Build the list of what is in context in the skill's sessions: managed, user, project and local CLAUDE.md files; unscoped rules; path-scoped rules with their `paths`; nested CLAUDE.md files; the other skills' names and descriptions; subagents; hooks by event, matcher and source; MCP server names; permission rules; and the active output style.
- Ask, for each environment file, whether it loads every session or only on a trigger. A skill that repeats an unscoped rule duplicates always-on context; a skill that repeats a path-scoped rule duplicates context Claude only has near matching files.
- Flag an inventory that lacks a layer you need, such as hooks or MCP servers, as a blocked check, rather than judging as if the layer were empty.
- Recommend, when the inventory shows the environment already covers part of the skill's job, the exact sentence that points to it instead of restating it, for example "Follow the commit conventions in the project's CLAUDE.md," written from what the skill's step needs.

### 1.3 Mode without environment

A skill audited alone, for example from a URL or an upload, has no environment you can see. You can't know what CLAUDE.md, rules, hooks or servers its users have, so Direction 2 (§5) doesn't apply, and of overlap and conflict (§4) only the dependencies the skill relies on (§4.4) can be judged. Direction 1 still applies in full: whether each piece of the skill belongs in a skill is a question about the piece and the skill's purpose.

When you audit:

- State in the report's Status or Checklist exceptions that the audit ran without an environment, that only §4.4 of §4 was judged, and that §5 didn't apply.
- Judge §3 and §6 in full. Where a piece would fit another feature, write the recommendation in the form §6 gives, because a skill with no known environment is usually one that reaches users you can't see.
- Flag nothing about an environment you don't have: no duplication of a CLAUDE.md you never read, and no conflict with a hook you can't see.
- Recommend, where the skill assumes an environment it never names, such as an MCP server or a project convention, the sentence that names the assumption for its users, for example "This skill needs the GitHub MCP server connected; if it isn't, stop and tell the user."

---

## 2. How to judge fit

### 2.1 Weighed by Claude or enforced by the harness

Every instruction is one of two kinds. Your prompt, CLAUDE.md, rules, skills and output styles are read by Claude, which decides what to do with them: it usually follows them, but nothing guarantees it, and Claude is allowed to decide a guideline doesn't apply. Hooks, permission deny rules and managed settings are applied by Claude Code, the harness, every time, whatever Claude decided. Most of the time you want Claude to decide, because almost every guideline has exceptions and Claude, with the actual code in front of it, is usually better placed to judge than a rule written in advance. The enforced kind is for what must always happen or never happen. A `prompt` or `agent` hook asks another model to decide, so it isn't deterministic either; real enforcement is a `command` or `http` hook, or a deny rule.

When you audit:

- Sort each directive in the skill into one of the two kinds by its consequence: does a single miss do damage the skill's purpose can't accept, or does the directive need judgment and admit exceptions?
- Flag a directive whose miss is unacceptable but which exists only as an instruction, and judge it under §3.1.
- Flag the reverse: a skill that asks for a hook, or ships one, for what is only a preference, such as a style choice with exceptions. A preference enforced as a hook fires when it shouldn't and has to be maintained.
- Recommend, for each directive you sort as enforced, the enforcement and the instruction together, as §3.1 describes, and for each one you sort as judgment, that it stays an instruction. Recommend nothing for a directive already in the right kind.

### 2.2 When the content has to be in context

Each feature loads at a different moment and stays for a different time. CLAUDE.md and unscoped rules load at session start, stay for the whole session and are re-read after compaction, so they cost context in every session whether relevant or not. Path-scoped rules and nested CLAUDE.md files load when Claude touches a matching file, and after compaction they are gone until the next match. A skill Claude can invoke has its description listed every session; its body loads only when the skill is invoked, and stays in the conversation from then on. A subagent's instructions never enter the main conversation, and only its final message returns. A hook costs no context unless it returns output. An output style sits in the system prompt for every response. The right feature is the one that puts the content in context exactly when Claude needs it, and nowhere else.

When you audit:

- Ask, for each piece of the skill, when Claude needs it: in every session, only near certain files, only while doing this task, only inside an isolated worker, or never in context at all because a program should do it.
- Flag content Claude needs in sessions where the skill isn't invoked, such as a convention that governs every edit in the project. In a skill, Claude lacks it whenever the skill doesn't load.
- Flag content that loads far more often than it's needed, such as a long task procedure the environment keeps always-on, and judge it under §5.1.
- Recommend the feature whose load moment matches the need, with the reason stated as that moment, for example "Move this to a path-scoped rule on `src/api/**`, so it loads when Claude edits an API handler whether or not this skill is invoked."

### 2.3 Most fit guidance is heuristic

The official guidance on choosing a feature is mostly rules of thumb: triggers that "most teams" meet in "roughly" an order, a rule of thumb for CLAUDE.md, and advice to keep the enforced set small. A skill can make a defensible choice that differs from it. What turns a fit judgment into a defect is its consequence: a rule that must hold but is only an instruction, context Claude needs and won't have when it needs it, or a contradiction between the skill and another file. Everything else is a better or worse choice of feature, and you report it as an improvement.

When you audit:

- Record a fit judgment as an improvement opportunity unless the misplacement makes Claude act wrongly in one of the three ways above; record those as defects.
- Flag nothing only because the skill's choice differs from a rule of thumb. Name the consequence first, and if there is none, there is no defect.
- Ask whether the skill states a reason for an unusual choice, such as keeping a check as an instruction because it has exceptions. A stated reason the skill's purpose supports makes the choice present and optimal.
- Recommend, for each improvement, the feature, the exact content to move and the consequence that makes it better for this skill, so the author can weigh it against the skill's own reasons.

---

## 3. Direction 1: content that belongs in another feature

### 3.1 A rule that must hold every time belongs in a hook or a permission rule

A skill's text is an instruction Claude weighs. Under pressure, in a long session, in an ambiguous situation, or after a prompt injection in a file it read, Claude can fail to follow a prompted rule, and however strongly it's worded, whether Claude follows it on a given turn is Claude's call. A check that must pass with no exceptions, such as a typecheck before finishing or a formatter after every edit, belongs in a hook, which the harness runs every time its event fires: a `Stop` hook that exits with code 2 sends Claude back to work with its stderr as the reason until the check passes or Claude Code's block limit is reached. An action that must never happen, such as an edit under `migrations/`, belongs in a `PreToolUse` hook that exits 2 to block it, and access that must never happen, such as reading `.env`, belongs in a permission deny rule, which holds in every permission mode. A hook doesn't replace naming the check in the skill: Claude still needs the command to check its own work as it goes. And a hook is only for a rule with zero exceptions. Repeated emphasis on a line Claude still misses is a sign the line belongs in a hook.

Where the hook lives decides when it holds. A hook in the skill's own `hooks` frontmatter registers when the skill is invoked and runs for the rest of the session. A plugin's `hooks/hooks.json` registers when the plugin loads and fires whether or not any of its skills is used. A hook in project settings applies to everyone in the repository. A hook in a subagent's frontmatter runs only while that subagent runs.

When you audit:

- Ask whether the skill states a check that must pass every time, such as before finishing or after every edit, or an action or access that must never happen. Look for "always", "never", "every time", "before you finish" and piled-on emphasis, and judge each by its consequence, not its wording.
- Recommend, for each such check, the hook or deny rule with its event and what it runs, and keep the check named in the skill's text, for example: "Run `pnpm tsc --noEmit` after each change. A `Stop` hook runs the same command and sends you back until it passes." Choose the carrier by when the rule must hold: the skill's frontmatter for a rule that matters once the skill is in use, a plugin's `hooks/hooks.json` for one that must hold whenever the plugin is enabled.
- Recommend a `command` or `http` hook for enforcement, never a `prompt` or `agent` hook, which leaves the decision to a model.
- Flag a skill that relies on a hook but never names the check's command in its text: Claude can't check its own work as it goes, and learns of the check only when it blocks.
- Flag a recommendation, or a shipped hook, for a check Claude should apply with judgment, such as "prefer named exports". It stays an instruction.
- Recognize that a bundled script is not enforcement: Claude runs it only if it follows the instruction to. Recommend a hook that runs the script when the check must hold every time.

Recognize the difference:

- **Needs enforcement:** "Never write to `config/production.yml`." One miss damages production, and the rule has no exceptions.
- **Stays an instruction:** "Prefer small, focused commits." It has exceptions, and Claude should weigh them.

### 3.2 Facts every session needs belong in always-on context

CLAUDE.md holds what Claude should know in every session: build and test commands, conventions, project layout, decisions that aren't in the repository, and "always do X" rules. A skill loads only when it's invoked or its description matches, so a fact that governs all work in the project, placed in a skill, is missing whenever the skill isn't loaded. Where a fact is personal rather than shared, it belongs at the personal level: `CLAUDE.local.md` for one project, the user's `~/.claude/CLAUDE.md` or `~/.claude/rules/` for every project, and the project files for what is team-wide and specific to that codebase.

When you audit:

- Ask, for each fact in the skill, whether it is true of the project whatever task Claude is doing. A build command, a directory that looks unused but isn't, or the team's chosen error helper is.
- Flag a skill that carries such a fact where the environment has no copy of it: Claude follows it only during this skill, and breaks it in every other task.
- Leave in the skill what this task alone needs, such as the order of release steps, even when it names project commands.
- Recommend the exact line for CLAUDE.md, at the level whose audience matches, and the shorter pointer the skill keeps, for example: add "Typecheck: `pnpm tsc --noEmit`" to the project CLAUDE.md, and keep in the skill "Typecheck as the project's CLAUDE.md says, after each step."

### 3.3 Guidance for one part of the codebase belongs in a path-scoped rule

A rule in `.claude/rules/` with `paths` frontmatter loads only when Claude reads, writes or edits a matching file, so a constraint that governs one part of the codebase reaches Claude whenever it works there, and stays out of context otherwise. A rule without `paths` is mechanically the same as CLAUDE.md: always loaded. A path-scoped rule fits a constraint on files that appear in several but not all corners of the codebase better than a nested CLAUDE.md does, and it fits a file-specific constraint, such as "migrations are append-only", better than a skill, because the skill holds it only while it's invoked. A path-scoped rule is lost after compaction until a matching file is touched again, so a constraint that must persist across compaction belongs in the project-root CLAUDE.md or an unscoped rule instead.

When you audit:

- Ask whether a constraint in the skill is tied to files rather than to the task: it applies whenever Claude edits those files, whatever the reason.
- Flag such a constraint kept only in the skill: Claude breaks it whenever it edits those files outside the skill.
- Flag, in the environment, an unscoped rule whose content concerns one part of the codebase, where it bears on the skill's domain, and recommend scoping it.
- Recommend the rule's file, its `paths` and its text, for example a `.claude/rules/migrations.md` with `paths: ["db/migrations/**"]` and the line "Migrations are append-only: add a new migration, never edit one that exists," and the skill's line reduced to what the task needs.

### 3.4 Side work belongs in a subagent or a forked run

A subagent runs in its own context window with its own system prompt, tools and permissions, and only its final message returns to the main conversation. It fits a side task whose intermediate output Claude won't reference again, such as a wide search, a full test run or a log analysis; work split into independent parallel parts; a task that should have fewer tools than the main session, such as a reviewer that can read but not edit, where the restriction is enforced by Claude Code; and a fresh reviewer that hasn't seen how the work was done. It doesn't make the same task's answer better, it costs its own tokens, and a fresh subagent first has to gather context the conversation already had. The main conversation fits work with frequent back-and-forth, phases that share a lot of context, quick targeted changes, and work the user wants to see and steer step by step. A skill can also run as a forked subagent with `context: fork`. When the same kind of worker is spawned again and again with the same instructions, a custom subagent definition holds them.

When you audit:

- Ask whether a step of the skill produces output the rest of the task won't use, splits into independent parts, needs a narrower tool set, or needs a reviewer without the conversation's reasoning.
- Recommend, for such a step, delegation with its exact prompt and what returns, for example: "Use a subagent to run the full test suite and report only the failing tests with their error messages."
- Flag a recommendation to delegate a step that needs the conversation's context, frequent correction, or the user's steering, or that delegates only to get a better answer.
- Recommend a custom subagent, with its description, tools and body, when the skill writes the same long delegation instructions in several places or for every run. Where a rule from the environment must reach the subagent, recommend restating it in the delegation prompt, because a subagent doesn't see what the main conversation discussed or which skills it invoked.

### 3.5 Access to an external system belongs in an MCP server

An MCP server gives Claude tools and data from an external system, with the connection and authentication handled by the server. A skill gives Claude the knowledge to use those tools well: which calls to make in which order, the team's schema and formatting rules, and how to handle the server's common errors. The two combine, and neither replaces the other. A skill that tries to reach an external system by itself, by having Claude paste data, scrape, or hand-build requests where a server or the system's CLI would serve, carries a job a skill can't do reliably. Where the system has a CLI, that is usually the easiest way in, and no server is needed. Connected servers add their tool names and instructions to context even when unused.

When you audit:

- Ask whether the skill's task depends on an external system, and how the skill reaches it: a configured server, a CLI, or instructions that make Claude improvise access.
- Flag instructions that make Claude improvise access to a system a server or CLI would serve, and recommend the server or the CLI, naming which one the environment already has.
- Flag nothing for a skill that teaches the use of a server the environment provides: that is the combination the guidance describes.
- Recommend, where the skill depends on a server, the sentence that names the server and what to do when it isn't connected, for example: "This skill uses the Linear MCP server's tools. If they aren't available, tell the user to connect the Linear server and stop."

### 3.6 How every response reads belongs in an output style

An output style sets Claude's role, tone and response format for every response in a session, and the user switches it off again with one command. It fits a voice, length or format the user wants everywhere, or Claude working as something other than a software engineer. A custom style leaves out Claude Code's built-in software engineering instructions unless it keeps them. A non-fork subagent runs its own system prompt, so an output style doesn't shape it. Format rules for this one task's deliverable belong in the skill, because an output style would shape every unrelated response.

When you audit:

- Ask whether the skill sets voice, length or format for Claude's responses in general, beyond the task's own output.
- Flag such session-wide instructions in a skill: they apply only while the skill's content is in context, and once loaded they keep shaping responses the skill was never meant to govern.
- Leave in the skill every format rule for the skill's own deliverable.
- Recommend, where the content is a session-wide manner the user would want on or off, a built-in style that covers it before a custom one, naming it, for example the Concise style for shorter responses, and the skill's line reduced to the task's own output.

### 3.7 What rightly stays in the skill

A skill fits reference material Claude needs sometimes, such as an API style guide, and procedures and workflows that need reasoning, such as a release checklist, a review process or a debugging playbook. A procedure in a skill plays out in the main conversation, where the user can see and steer each step, and its body costs nothing until the task calls for it. Much of a well-placed skill is this, and judging it present and optimal is as much a part of your audit as moving what doesn't fit.

When you audit:

- Confirm, for each procedure and piece of reference in the skill, that it is task-specific and needs Claude's judgment. Record it as present and optimal when it is.
- Flag no recommendation that would move a judgment-dependent procedure into a hook, or task-specific reference into always-on context.
- Ask whether the skill pairs well with the enforcement around it: a hook that sends lint errors back to Claude pairs with a skill that holds the team's own rules for fixing them.
- Recommend, where the skill holds a procedure the environment also enforces in part, the line that tells Claude what the enforcement does, so Claude doesn't fight it, for example: "A `PostToolUse` hook formats every file you edit; don't run the formatter yourself."

---

## 4. Overlap and conflict with the environment

### 4.1 Duplication between the skill and the environment

When the skill restates what an always-on file already says, the same text sits in context twice in every session the skill runs, and the two copies drift apart as each is edited, until they disagree. A copy of a path-scoped rule or of another skill's content drifts the same way. The environment's copy is the one Claude has in every session, so the skill gains nothing from repeating it, and points to it instead.

When you audit:

- Compare every rule, command, value and convention in the skill with the CLAUDE.md files, rules and other skills in the inventory, including the same rule in different words.
- Flag each duplicate with both locations, quoting both.
- Ask which copy belongs where: the environment's, when the fact governs work beyond this skill; the skill's, when only this task needs it and the environment copy is a stray.
- Recommend one copy and the pointer that replaces the other, for example: delete the skill's list of commit rules, and keep "Commit following the project's CLAUDE.md." Where the skill is distributed, the environment's copy doesn't travel with it; judge under §6.

### 4.2 Contradictions between the skill and the environment

When two files give different guidance for the same behavior, Claude may pick one arbitrarily. CLAUDE.md files at different levels are concatenated without overriding each other, and a user rule and a project rule have no precedence between them, so a contradiction between the skill and any of them has no defined winner. Because the skill loads only when invoked, Claude's behavior then depends on whether the skill happens to be in context.

When you audit:

- Flag every pair of passages, one in the skill and one in an environment file, that give different guidance for the same behavior: opposite directives, two values for the same thing, or two orders for the same actions. Quote both locations.
- Flag a rule that the environment states as binding and the skill as a preference, or the reverse.
- Recommend one resolution with its exact text: the version to keep, where it lives, and the edit to the other. Base it on the official documentation, or on the skill's purpose and the environment's intent. If neither shows which one the author meant, give both readings and name the decision the author has to make.

Recognize the difference:

- **Contradiction:** the project CLAUDE.md says "Use pnpm, not npm." The skill says "Run `npm test`."
- **Resolved:** the skill says "Run the tests with the command in the project's CLAUDE.md."

### 4.3 Instructions that fight or ignore what the environment enforces

Hooks and permission rules apply whatever the skill says. A skill that tells Claude to do what a deny rule or a `PreToolUse` hook blocks sends Claude into a call that fails, and a skill that tells Claude to do by hand what a hook already does, such as formatting after every edit, makes Claude repeat the hook's work. Hooks merge across sources, so every hook in the inventory fires during the skill.

When you audit:

- Compare each action the skill tells Claude to take with the inventory's hooks and permission rules.
- Flag an instruction that a deny rule or a blocking hook will refuse, quoting both, and judge its severity by what the skill's task loses when the call fails.
- Flag an instruction that repeats what a hook already does on every matching event.
- Recommend the line that tells Claude what the environment enforces and what to do instead, or the deletion of the repeated step, for example: "Edits under `migrations/` are blocked; write a new migration file instead."

### 4.4 Features the skill relies on but the environment may not have

A skill that calls on a subagent, an MCP server, a hook or a rule that its environment doesn't have fails at that step, and a skill that relies on one without naming it leaves Claude unable to tell why. In the mode with environment, the inventory tells you what exists.

When you audit:

- List every feature the skill relies on: subagents it delegates to by name, MCP tools it calls, hooks it expects to run, and rules or CLAUDE.md content it expects Claude to have.
- Flag each one the inventory doesn't show, with the step that fails without it.
- Flag each one the skill relies on without naming it, such as a step that only works because a hook formats files.
- Recommend, for each dependency, either the sentence that names it and the fallback, or the content written into the skill itself, for example: "If the `code-reviewer` subagent isn't available, review the diff yourself against the checklist below."

---

## 5. Direction 2: environment content that belongs in the skill

### 5.1 Procedures in always-on files that belong to the skill's domain

CLAUDE.md is for facts Claude should hold all the time. A multi-step procedure there, such as a deployment runbook or a review checklist, costs context in every session for every task, and only matters when that task runs. When the procedure belongs to the audited skill's domain, the skill is where it loads only when needed, and the environment keeps at most a one-line pointer. A section of CLAUDE.md that has grown into a procedure rather than a fact is the documented trigger for a skill.

When you audit:

- Read every CLAUDE.md and rule in the inventory for procedures, checklists and task reference in the audited skill's domain. Ignore content outside that domain.
- Flag such content as an improvement opportunity with its location, and as a defect only where it contradicts the skill (§4.2).
- Ask whether the content also holds facts every session needs, such as the deploy command itself. Those stay always-on; only the procedure moves.
- Recommend the exact content to add to the skill, where in the skill it goes, and the line left in the environment file, for example: move the "Release steps" section of CLAUDE.md into the skill's release workflow, and leave "Releases: use the release skill."

### 5.2 Content that should become a skill of its own

Some environment content belongs neither in always-on files nor in the audited skill: a playbook pasted into chat again and again, a CLAUDE.md section that is a procedure for a different task, or the same instructions repeated across several skills. Each has a recognizable trigger for a skill of its own. You propose it only when it touches the audited skill's domain, such as a procedure the audited skill keeps half-restating, or a shared block that several skills, the audited one included, each carry.

When you audit:

- Ask whether content in the environment, or shared between the audited skill and its siblings, forms one reusable procedure or body of reference that bears on the audited skill.
- Flag the same instructions carried by several skills as duplication with every location, and recommend one skill that holds them and the pointer each skill keeps.
- Flag nothing outside the audited skill's domain.
- Recommend the new skill by its purpose and the exact content it takes from each location, in a sentence the author can act on, for example: "Move the 'Changelog format' blocks from `release` and `hotfix` into one `changelog-format` skill, and have both point to it at the step that writes the entry."

### 5.3 Subagents and other skills that should feed or absorb the skill

Skills and subagents combine in two directions. A subagent can preload skills through its `skills` field, so the skill's full content is in its context from the start, and a skill can run in a subagent with `context: fork`. A subagent whose body holds domain reference that the audited skill also needs carries a copy that drifts; preloading the skill shares one copy. A skill that keeps delegating to a worker it describes inline belongs with a subagent definition (§3.4).

When you audit:

- Compare each subagent in the inventory with the audited skill: does its body restate the skill's reference or procedure, or contradict it?
- Flag a subagent body that duplicates the skill's domain content, and recommend preloading the skill through the subagent's `skills` field and cutting the copy from the body.
- Flag a contradiction between a subagent's body and the skill under §4.2.
- Recommend, where a subagent would need the skill's knowledge for its job and lacks it, the exact `skills` entry to add, naming the skill as it is invoked.

---

## 6. Recommending for a skill that is distributed

### 6.1 What a plugin can and can't ship

A skill distributed in a plugin reaches users through the plugin's components, and only those travel. A plugin can ship skills, subagents in `agents/`, hooks in `hooks/hooks.json`, MCP servers in `.mcp.json`, output styles and executables. It can't ship CLAUDE.md or rules: Claude Code doesn't load a `CLAUDE.md` at a plugin's root, and instructions in a plugin are written as skills. A rule that must hold every time goes into the plugin as a hook rather than a skill. A plugin subagent ignores `hooks`, `mcpServers` and `permissionMode` in its frontmatter, so its hooks and servers go in the plugin's own `hooks/hooks.json` and `.mcp.json`, where they apply whenever the plugin is enabled.

When you audit:

- Ask, for each recommendation that moves content to another feature, whether the plugin can carry that feature, and in which component.
- Recommend a plugin hook for a distributed skill's zero-exception check, with the check still named in the skill's text (§3.1), and a plugin subagent or `.mcp.json` server where §3.4 or §3.5 calls for one.
- Flag a recommendation, or a plugin, that puts hooks or MCP servers in a plugin subagent's frontmatter, where they are ignored, and recommend the plugin's own `hooks/hooks.json` or `.mcp.json`.
- Flag a plugin that relies on a `CLAUDE.md` or rules file of its own to reach Claude, and recommend writing that content as a skill, or in the form §6.2 gives.

### 6.2 Recommending CLAUDE.md and rules as output

A plugin can't ship CLAUDE.md or rules as components, but a skill can still produce them or tell the user to write them, because that is the skill's output, not its input. A recommendation that content belongs in CLAUDE.md or a rule is therefore valid for a distributed skill too, in one of two forms: what the skill tells Claude or the user to write, or a note to the author. This is the owner's decision; the official sources say only that a plugin's root `CLAUDE.md` isn't loaded and that instructions in a plugin are written as skills. The same holds for permission deny rules: the skill tells the user which rule to add to their settings.

When you audit:

- Write every CLAUDE.md, rule or deny-rule recommendation for a distributed skill as one of the two forms, never as a file the plugin ships.
- Recommend, as skill text, the step that writes or proposes the content, at the level whose audience matches, for example: "If the project's CLAUDE.md has no typecheck command, propose adding `- Typecheck: <command>` under its commands, and add it once the user agrees."
- Recommend, as a note to the author, the content their own users should add, when the skill can't write it, for example "Tell users in the README to add `Read(./.env)` to `permissions.deny`."
- Flag nothing as unfixable only because the plugin can't ship the feature: name the form that reaches the user.

### 6.3 Surfaces that skip a component

Hooks and subagents run wherever Claude Code runs and in Cowork, so a recommendation to use them needs no caveat there. The official plugin support table records one difference that changes a recommendation: in claude.ai chat, a plugin's agents, hooks, local MCP servers and output styles are ignored, and only Claude Code loads plugin output styles. For a skill whose users include chat, a hook or a subagent doesn't do its job there.

When you audit:

- Ask which surfaces the skill's users are on, from the context you established.
- Recommend, for a skill whose surfaces include claude.ai chat, the hook or subagent together with the instruction that does the same job as well as it can without it, so chat users still get the check named and the procedure done inline.
- Flag a recommendation of an output style or a local MCP server as the only carrier of something chat or Cowork users need.
- Recommend, for a skill that is also uploaded to claude.ai or used through the Skills API, a carrier other than the skill's own `hooks` frontmatter, such as the plugin's `hooks/hooks.json`, because an upload accepts only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools` and refuses any other key.
- Write no surface caveat that the support table doesn't state.

---

## Classifying findings

Give every finding four things: the exact file and line(s) in the skill under audit, or in the environment file, or where missing content belongs; the point in this file it violates or falls short of; why it is a defect, stated as what Claude would do wrong at that point; and a specific fix, written out, with the feature it goes to and the reason it's the right one.

Classify each defect into one of four levels by its actual consequence. The examples anchor each level; a finding that doesn't match one verbatim still gets the level its own consequence earns.

- **Critical.** The placement drives Claude to damage or an irreversible action, or makes the skill fail on every run. For example: a rule against a destructive or irreversible action, central to the skill's purpose, kept only as an instruction while the skill runs that action unattended; a skill whose instruction for an irreversible step contradicts an environment file, such as a skill that force-pushes where the project CLAUDE.md forbids it; a skill whose whole task depends on an MCP server or subagent the environment doesn't have.
- **High.** Claude acts wrongly or inconsistently in some runs. For example: a zero-exception check, such as a typecheck before finishing, kept only as an instruction; a contradiction between the skill and a CLAUDE.md, rule or subagent on a behavior the task depends on; a convention that governs every edit kept only in the skill, so Claude breaks it outside the skill; an instruction that a deny rule or blocking hook refuses on a step the task needs; a skill that relies on a hook but never names the check's command.
- **Medium.** Claude gets there, but with wasted context, drift or less consistency than it should. For example: the skill duplicating a CLAUDE.md or rule; a procedure in CLAUDE.md that belongs in the skill; an unscoped rule in the skill's domain that should be path-scoped; a hook recommended or shipped for a preference; a dependency on a configured server named nowhere in the skill; a step that repeats what a hook already does; a subagent body that copies the skill's reference.
- **Low.** A minor weakness with no real consequence. For example: a pointer to an environment file that names it loosely but unambiguously; a one-line duplicate of a command that agrees with CLAUDE.md in a skill never used outside that project.

Tie-breaks:

- If a finding fits two levels, the higher level wins.
- A fit judgment whose misplacement doesn't make Claude act wrongly is an improvement opportunity, not a defect (§2.3).
- When several findings share one root cause, such as a block of CLAUDE.md content copied into the skill and since edited in one place only, report the root cause once and list every location.
- Never invent impact, never inflate a severity to make the report look decisive, and never lower one because Claude might follow the instruction anyway: "Claude would usually follow it" is the reason a must-hold rule needs enforcement, not a reason it's minor.

## Improvement opportunities

Separate improvement opportunities from defects: an opportunity is a better feature for content that works where it is, an enforcement, pointer or stated dependency the skill's purpose needs and lacks, or environment content in the skill's domain that the skill should absorb or that should become a skill of its own. Report every one that genuinely applies to this skill; this section may stay empty only when nothing does. For each one, give what exists now (or that it is absent, and where it belongs), the exact content written out in full with the feature and file it goes to, and why it is better for this skill.

This file gives you the criteria, the context to establish, and the severity model. The gotchas and the verification checklist live in your own instructions, and the report template lives in this skill's `assets/` folder, so they aren't repeated here.

## Delivering the report

Deliver every defect and improvement opportunity in the shared findings template, `assets/audit-report.md` in this skill. Fill one defect block per defect, with every field, and keep the template's structure exactly. For a finding located in an environment file rather than in the skill, give that file's path in File and say so in Finding. Defects with one root cause are one defect: give its first location in File and Lines, and list every other location, as `path:lines`, in Finding. State the mode in the report: without environment, record under Checklist exceptions that only §4.4 of §4 was judged and §5 didn't apply, and list every inventory item that was missing and the check it blocked.
