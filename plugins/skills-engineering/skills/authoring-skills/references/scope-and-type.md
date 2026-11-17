# Scope and type

Decide these before naming or writing anything: whether the content should be a skill at all, what one skill covers, where it lives, which surfaces run it, how it runs, and what it relies on. A wrong call here can't be fixed by better wording later.

## Contents

- 1. Whether it should be a skill
- 2. Content that belongs in another feature
- 3. One coherent unit
- 4. Where it lives and who receives it
- 5. Surfaces
- 6. Inline, forked or preloaded
- 7. Relying on other skills
- 8. Questions to ask yourself

## 1. Whether it should be a skill

A skill earns its place only by what Claude lacks without it. Once invoked, its text stays in the conversation for the rest of the session and competes for attention with everything else, so a skill that restates what Claude already does costs every turn and buries the lines that matter.

- Write a skill when the gap requests from understanding the request show Claude failing in a way the skill can fix: the project's or team's conventions, a domain procedure and its order, edge cases and corrections, which of several tools is right here, decisions written nowhere Claude can read, facts about the environment that defy a reasonable guess, or platform facts newer than training.
- Don't write one when Claude handles the whole task well alone. Say so to the user, and suggest checking with one run with the skill and one without before building it.
- Aim the skill at the harder tasks in its area. Claude consults skills for work beyond what it does unaided; a skill pitched at a one-step request such as "read this file" triggers unreliably, because Claude just does the task.

## 2. Content that belongs in another feature

Every instruction is either weighed by Claude or enforced by the harness. Skills, CLAUDE.md, rules and output styles are read and weighed: Claude usually follows them and may decide one doesn't apply. Hooks, permission deny rules and managed settings run every time, whatever Claude decides. Choose by two questions: when does Claude need the content in context, and what does one miss cost?

- A rule with zero exceptions, where one miss does damage (a check that must pass before finishing, a file that must never be edited, a secret that must never be read): put the enforcement in a hook or deny rule, and still name the check in the skill so Claude can run it as it works. How to write that pair is in the scripts-and-hooks guide.
- A preference with exceptions (prefer small commits, prefer named exports): keep it as an instruction. Enforced as a hook, it fires where it shouldn't.
- A fact every session needs whatever the task (the build command, a directory that looks unused but isn't): it belongs in always-on context, CLAUDE.md or an unscoped rule. In a skill it's missing whenever the skill isn't loaded.
- A constraint tied to files rather than to the task (migrations are append-only): a path-scoped rule, which loads whenever Claude touches those files.
- Side work whose intermediate output the task won't reuse, work that splits into independent parts, a worker that must have fewer tools, or a reviewer that must not see the reasoning: a subagent. Not work that needs the conversation's context, frequent correction or the user's steering.
- Access to an external system: an MCP server or the system's CLI. The skill then teaches how to use it well: which calls in which order, the team's formats, the common errors, and what to do when it isn't connected.
- Voice, length or format for every response in the session: an output style. Format rules for the skill's own deliverable stay in the skill.
- Reference Claude needs sometimes, and procedures that need judgment: these rightly stay in the skill, where they cost nothing until the task calls for them and the user can watch and steer each step.

When the skill ships in a plugin, only the plugin's components travel. A plugin can carry skills, subagents, hooks, MCP servers and output styles; it can't carry CLAUDE.md or rules. When the design needs always-on content or a deny rule, write it as the skill's output: a step that proposes the line to the user and writes it once they agree, or a line in the plugin's documentation telling users what to add.

## 3. One coherent unit

- One skill, one job a user would name. A description that spans unrelated jobs (querying a database and administering it) can't route precisely: split it. A skill scoped too narrowly forces several to load for one task: merge it.
- Before writing, compare the planned content with what the environment already has: CLAUDE.md files, rules, other skills, subagents. Point to an existing copy instead of repeating it, because two copies drift until they disagree. For a skill that ships to others, the environment's copy doesn't travel, so the skill carries what its users won't have.
- When the planned content contradicts an environment file, resolve it before writing: there is no defined winner between them, so Claude's behavior would depend on which happens to be in context.
- Don't tell Claude to do what a hook or deny rule in the environment blocks, or to repeat by hand what a hook already does. Tell Claude what the enforcement does, so it doesn't fight it.
- When several skills carry the same block of instructions, or a procedure keeps being pasted into chat, that block is a skill of its own; the others point to it.

## 4. Where it lives and who receives it

Where a skill lives decides who gets it, under which name, and on which surfaces. Read the current location list on the Claude Code skills page before choosing; the shared table the main skill file points to records the command name each location gives and which one wins on a name clash.

- Personal: one person, every project on one machine; not in Cowork or cloud sessions, which load account skills instead.
- Project: everyone working in the repository; not in cloud threads inside a Claude Code project, which reach skills through the claude.ai account.
- Plugin: everyone who installs the plugin, namespaced as `plugin:skill`, so it never collides with skills elsewhere. The right home for anything distributed to people you don't know.
- claude.ai account or upload: chat, Cowork, cloud sessions, and terminal sessions signed in with that account. Uploads accept only the specification's frontmatter fields (see the frontmatter guide).
- Skills API and Managed Agents: their own upload or attachment routes, and their own runtime limits (see section 5).

For each surface the user named, trace the route by which the skill reaches it. A surface with no route is a design defect, not a footnote.

## 5. Surfaces

Each surface runs a different subset of what a skill can do. Decide the surfaces in understanding the request, then design for the most limited one, or say where a part doesn't work.

- Claude Code runs everything a skill can declare, subject to the user's settings and permission rules.
- claude.ai chat ignores a plugin's agents, hooks, local MCP servers and output styles. When chat is a target, give every hook or subagent step an inline fallback the skill can do without it.
- Account skills synced into a terminal or VS Code session don't run injected commands or attach `@` files; a desktop Cowork session replaces injected commands with a placeholder. A skill that depends on them fails on those routes.
- The Skills API runs skills in a sandbox with no network and no package installation: everything a script needs must be preinstalled there.
- Check the official plugin and surface pages for the current support table before stating any of this to the user; write no caveat they don't state.

## 6. Inline, forked or preloaded

- Inline (the default): the skill runs in the main conversation, can lean on what was already discussed, and the user can steer each step. The right choice for most procedures.
- Forked (`context: fork`): the skill's text becomes the prompt of a fresh subagent. Choose it for self-contained side work whose result alone matters. The fork sees no conversation history, so the skill must name every input it needs ("apply the plan in `plan.md`", never "the plan we agreed on"). It must contain a task, not only guidelines, or it returns nothing useful. By default it runs in the background with a narrower tool set; a read-only agent type can't write files.
- Preloaded (a subagent's `skills` field): the skill arrives as reference beside the subagent's own task. Write it as knowledge, not as the task. A skill that sets `disable-model-invocation: true` can't be preloaded.
- No subagent can ask the user a structured question, enter or leave plan mode, schedule its own wake-up or start a workflow. A forked or preloaded skill takes its input from its arguments or the delegation message, and ends with a message that tells the parent what it must ask.
- When the parent must show a subagent's report as written, say so in the delegating step; otherwise the parent may summarize it.

## 7. Relying on other skills

Claude sees only another skill's description until that skill is invoked. A step that says "write it the way the changelog skill does" leaves Claude improvising.

- Invoke the other skill at the step that needs it, by its full invocable name (`plugin:skill` for a plugin skill), and say what it produces and whether to wait for it.
- Before relying on it, check that it can run there: the name resolves to that skill and not a same-named command; the target doesn't set `disable-model-invocation: true`; the Skill tool is available, including inside any subagent; and the target is installed on every surface you named.
- A forked target that runs in the background delivers its result later. Don't read its output in the next step unless it waits.
- Outside a plugin, nothing installs a skill another skill relies on. To guarantee it, ship both in one plugin, or declare the other plugin in `dependencies` with a version range you have tested.
- Compose only where a step uses it. Each extra invocation or dependency is another way to fail.

## 8. Questions to ask yourself

- Which gap request fails today, and what in this skill fixes it?
- For each piece of content: when does Claude need it, and what does one miss cost?
- Would a user name this skill's job in one phrase?
- What does the environment already say about this, and do I repeat or contradict it?
- For each target surface: by what route does the skill arrive, and which of its parts runs there?
- If this runs in a subagent, does every input reach it without the conversation?
- For each other skill this one relies on: does its name resolve, may Claude invoke it, and is it installed everywhere this one runs?
