# Phase 2: Environment and architecture

How to decide, from the intent and current official sources, what you can do here, what exists, whether a skill is the answer, the discipline it serves, where it lives and how it runs, and its architecture.

Decide each point from the goal, without waiting for the requester to ask, and record its reason for the plan. Aim for the simplest skill that does the job safely, stably and at the scale it will meet.

1. **What you can do here.** Note whether you can write files, run commands, start subagents and reach the web. If you can't write files, deliver each file's path and content in your reply.
2. **What exists.** Inventory what the skill you write could duplicate, contradict or rely on: skills in your context and in the skill folders here, CLAUDE.md files, rules, subagents and hooks. Read names and descriptions, open a file in full only when the new skill must fit with it, and note the conventions for skills here.
3. **Whether a skill is the answer**, by the failure it must fix:
   - a task that won't repeat: do the task instead;
   - something the model already does well: no skill;
   - a fact every session needs: CLAUDE.md or a rule;
   - a rule that must hold every time, or a constraint a check can enforce: a hook or the check;
   - work that needs its own context and tools: a subagent, which a skill can supply with knowledge;
   - access to an external system: an MCP server, with a skill only for how to use it;
   - a procedure or knowledge the model needs for some tasks: a skill.

   When it isn't a skill, say which feature fits and why, and stop unless the requester still wants one. Split a request with several needs by trigger and task.

4. **The discipline.** Name the kind of work the skill serves and the disciplines that govern it, and derive from them the knowledge, methods, tools, failure modes and quality criteria the skill must carry. The higher the cost of an error in that domain, the more evidence, verification and human control the skill must require.
5. **Where it lives and how it runs**, by who must get it and in which sessions:
   - only the requester, in local Claude Code sessions on this machine: `~/.claude/skills/<name>/`. Cowork and cloud sessions don't read it;
   - the requester in Cowork, cloud sessions and claude.ai: their claude.ai account, through an upload;
   - everyone working in a repository: `.claude/skills/<name>/`, committed. Cloud threads in a Claude project don't load it;
   - work in one part of a monorepo: `<subdir>/.claude/skills/<name>/`, which loads once Claude works on files there;
   - every user on the organization's managed machines: the managed settings directory's `.claude/skills/<name>/`;
   - users who install a plugin: the plugin's `skills/<name>/`, or its root for a single-skill plugin. claude.ai and Cowork don't install a plugin that has a `bin/` folder;
   - an application on the Claude API: an upload to the Skills API.

   Never name the skill's folder `synced` or `anthropic-skills`: Claude Code reserves both outside plugins and skips the skill. Before choosing, consult https://code.claude.com/docs/en/skills#choose-where-skills-load for the current list.

6. **Architecture.** Start from `SKILL.md` alone, and add each component only for a need: a reference for depth some runs need, a script for an operation that must give the same result every run, an asset the output starts from, a hook for a check on every event, a subagent that consumes the skill, and the tools, skills or MCP servers the task relies on.

7. **Current features.** Beyond the references, read the official sources for the surfaces, platforms and Claude versions the requester uses, and build on the current features they offer there.

Exit: every piece has a purpose tied to the goal, and every platform fact behind a decision is verified.
