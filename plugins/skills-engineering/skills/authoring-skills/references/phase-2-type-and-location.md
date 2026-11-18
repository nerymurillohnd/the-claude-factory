# Phase 2: Type and location

Decide what kind of skill this is, who invokes it and where it loads from. This file covers:

- whether a skill is the right feature
- what already exists
- the type of skill and who invokes it
- where it loads from
- skills outside Claude Code

## Is a skill the right feature

Match the failure the user wants fixed to the feature that fixes it:

- A task that won't repeat: do the task, no skill.
- Something the model already does well: no skill.
- A fact every session in a project needs: CLAUDE.md or a rule.
- A rule that must always hold, or a constraint a check can enforce: a hook, or the check.
- Work that needs its own context and tools: a subagent. A skill can give it knowledge.
- Access to an external system: an MCP server. A skill only teaches how to use it.
- A procedure or knowledge the model needs for some tasks: a skill.

If it isn't a skill, tell the user which feature fits and why, and stop unless they still want a skill. If the request holds several needs, split it by trigger and task.

Read [Compare similar features](https://code.claude.com/docs/en/features-overview#compare-similar-features) when two features could do the job.

## What already exists

List what the new skill could duplicate, contradict or rely on: the skills, CLAUDE.md files, rules, subagents and hooks of the user's environment. Read names and descriptions, and open a file in full only when the new skill must fit with it. Note the conventions this environment follows for skills. If a skill already covers the need, propose extending it instead of writing a new one.

## Type and who invokes it

Pick the kind of content:

- Reference content: knowledge the model applies to the current work, such as conventions or domain rules. It runs inline.
- Task content: step-by-step instructions for one action, such as a deployment or a commit. Users often run it directly with `/skill-name`.

Pick who invokes it by consequence. If the model running the skill on its own could change something the user didn't approve, only the user invokes it.

- Both, the default: the description is in context, and the skill loads when invoked.
- Only the user: for actions with side effects or timing the user must control, such as deploying, sending or publishing. The description stays out of context, so neither the model nor another skill can load it, a subagent can't preload it, and a session-scoped scheduled task can't run it. Write the body as the procedure the command runs.
- Only the model: for background knowledge that isn't an action. It leaves the `/` menu and the model loads it from the description.

A scheduled task or `/loop` asks before running a skill that declares `allowed-tools` or hooks (Claude Code 2.1.325 and later). For a skill meant to run unattended, tell its users to add `Skill(name)` to `permissions.allow`.

Read [Control who invokes a skill](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill) when you need the fields and the table of what loads.

## Where it loads from

Ask who must get the skill and where they work, then pick the location that reaches them. If the location the user named misses a session they need, choose the one that reaches it and say so in the plan.

- **Personal**, `~/.claude/skills/<name>/SKILL.md`: loads in all the user's projects on this machine. Does not reach Cowork or cloud sessions.
- **Project**, `.claude/skills/<name>/SKILL.md`, committed: loads in sessions in the repository, from the folder where the session starts up to the repository root. Does not reach cloud threads in a project.
- **Nested**, `<subdir>/.claude/skills/<name>/SKILL.md`: loads in sessions started in or below `<subdir>`. A session started above it loads the skill once Claude works on files there. Does not reach cloud threads in a project.
- **Additional directory**, `.claude/skills/<name>/SKILL.md` in a directory passed with `--add-dir`: loads in that session only. The setting `permissions.additionalDirectories` grants file access and loads no skills.
- **Plugin**, `<plugin>/skills/<name>/SKILL.md`, or `SKILL.md` at the plugin root: loads wherever the plugin is enabled, as `/plugin-name:skill-name`.
- **claude.ai account**, skills enabled for the account: loads in Cowork, cloud sessions, and terminal sessions signed in with that account.
- **Enterprise**, `.claude/skills/<name>/SKILL.md` in the managed settings directory: loads for all users on machines where the organization deploys it.

Write a skill, not a file in `.claude/commands/`: that format is older and still works.

Read [Choose where skills load](https://code.claude.com/docs/en/skills#where-skills-live) when the list doesn't cover the case.

Read [Load skills from a directory outside the project](https://code.claude.com/docs/en/skills#skills-from-additional-directories) when the skill must reach a session through `--add-dir`.

Read [Load skills in monorepos and subdirectories](https://code.claude.com/docs/en/skills#discovery-from-parent-and-nested-directories) when the skill lives below the repository root.

## Skills outside Claude Code

claude.ai uploads, the Skills API and other Agent Skills clients run the skill without Claude Code's processing:

- Frontmatter: only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`. Any other key is a hard error on upload.
- Body: Claude Code features such as argument placeholders, `${CLAUDE_*}` variables and injected commands don't work. Refer to bundled files by paths relative to the skill root.
- Runtime: the Claude API has no network and no runtime package installation. On claude.ai, network access depends on the user's and the admin's settings. Claude Code has the user's full network access.
- Sharing: custom skills don't sync across surfaces. A skill uploaded to claude.ai is not on the API, and neither is in Claude Code's folders. Upload to each surface separately.

List each Claude Code feature the skill loses there in the plan.

Read [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#limitations-and-constraints) when you need a surface's limits.

Read [Skills with the Claude API](https://platform.claude.com/docs/en/build-with-claude/skills-guide) when the skill is uploaded through the API.

Read [Extend agents with skills](https://code.claude.com/docs/en/agent-sdk/skills) when the skill must work in the Agent SDK.

Read [Skills for Managed Agents](https://platform.claude.com/docs/en/managed-agents/skills) when the skill must work in Managed Agents.
