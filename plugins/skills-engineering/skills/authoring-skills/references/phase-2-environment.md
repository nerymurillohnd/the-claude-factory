# Phase 2: Environment and project

How to establish the environment you work in, understand the project and every instruction Claude loads in it so the skill duplicates and collides with nothing, and gather the project's material the skill is built from.

## Contents

- [Gotchas](#gotchas)
- [1. Establish the execution environment](#1-establish-the-execution-environment)
- [2. Understand the project and what Claude loads in it](#2-understand-the-project-and-what-claude-loads-in-it)
- [3. Gather the domain sources](#3-gather-the-domain-sources)
- [Official sources](#official-sources)

## Gotchas

- A cloud session runs in a fresh container, so the `~/.claude/` you see isn't the user's: don't take its personal skills or settings as theirs.
- Your skill listing omits skills with `disable-model-invocation: true`, nested skills not loaded yet and some descriptions: search the skill folders before you conclude a skill doesn't exist.
- A personal skill hides a project skill of the same name, while CLAUDE.md files, rules and hooks all add up: check for a same-name skill and for a hook that already enforces the rule.
- A subfolder's CLAUDE.md or a rule with `paths` loads only when Claude touches matching files, so a convention can govern the skill's files without being in your context: search for them.

## 1. Establish the execution environment

Know where you are and what you work from before you open any file: it decides which files you can see, and whether they are the ones the user's skill will meet. Most of it is already in your context at the start: the environment block, the skill listing, the subagent types and the MCP tools.

1. Surface and session
   - Identify where you run: a local terminal, the desktop app, an IDE, a cloud session, Cowork, a project thread, claude.ai, the Agent SDK, or a subagent.
2. Machine
   - Identify whether you run on the user's machine or in a container, and which operating system.
3. Workspace
   - Identify the working directory, whether it is a git repository and on which branch, and any added directories or worktrees.
4. Account and authentication
   - Identify how the session signs in: a claude.ai account syncs that account's skills, and an API key, Bedrock or a token doesn't.
5. What you can do
   - Identify the tools, permissions and network access the session gives you.
6. Your environment against the skill's target
   - Compare where you write the skill with where it will run. When they differ, design for the target, and say what you couldn't check from here.

```text
Environment: cloud session in a Linux container, repository acme/billing on
branch feature/invoices, signed in with a claude.ai account, network limited
to package registries.
Target: the user's laptop and the team's cloud scheduled tasks.
Consequence: ~/.claude/skills/ here is not the user's; check their personal
skills by asking, and place the skill where the cloud tasks reach it.
```

## 2. Understand the project and what Claude loads in it

Learn what the project is and every instruction Claude follows in it, to find what the new skill would duplicate, contradict or depend on, before you design it.

1. Identify the project type
   - Read the root: README, manifests and build files (`package.json`, `pyproject.toml`, `Makefile`, CI config), and the folder layout.
   - State what it is: code (languages, frameworks, how it builds and tests), documentation, data, operations, or a mix.
   - Note the conventions the project already follows: naming, language, structure, tooling.
2. Inventory what Claude loads
   - Instructions: every CLAUDE.md, CLAUDE.local.md and `.claude/rules/` file at user, project and subfolder level, and any managed CLAUDE.md.
   - Skills: project, nested, personal, plugin and synced skills, and `.claude/commands/` files.
   - Subagents, hooks, permissions, output styles and MCP servers.
   - Project memory: auto memory, decision records, conventions and other documents Claude is told to follow.
   - Read names and descriptions first, and open a file in full when it can overlap or collide with the skill.
   - Read setting keys and non-secret values. Leave the values of secrets and credentials unread.
3. Find overlap
   - A skill, rule or subagent that already does what the new skill would do, fully or in part.
   - A skill whose description shares the new skill's trigger words.
4. Find friction
   - An instruction, rule, hook or skill that contradicts the new skill's goal, or the way it reaches it.
   - A convention the new skill would break: a name, a path, a format, a tool, a step order.
   - A rule or hook that would block a step the skill needs.
5. Flag each finding and ask
   - Make no assumption about which side wins.
   - For each overlap or friction, tell the user what it is, where it lives (file and line), and why it collides with the skill.
   - Ask which prevails:
     - The existing instruction prevails: the skill adapts to it, relies on it, or extends the existing skill.
     - The new skill prevails: record the files to align or correct after the skill is built, and change them only with the user's approval.
   - When something loads only in the user's own session, such as a managed setting or a plugin on their machine, ask the user to run `/context` or `/skills` and share what it shows.
6. Record the decisions
   - Carry each finding and the user's decision into the design you present at the end of Phase 2.

```text
Friction: .claude/rules/commits.md:12 says "never commit without running
npm test". The new release skill commits after building, with no tests.
Why it collides: the skill would break a project rule on every run.
Which prevails?
- The rule: the skill runs npm test before it commits.
- The skill: it commits without tests, and commits.md:12 is updated
  after the build to exempt release commits.
```

## 3. Gather the domain sources

Build the skill from the project's own material, not from general knowledge: a skill built from the team's runbooks and incident reports carries their schemas, failure modes and fixes, which a general article on the topic can't.

- Read what the project holds on the skill's domain:
  - runbooks, internal documentation and style guides;
  - API specifications, schemas and configuration files;
  - code review comments and issues, for the concerns that recur;
  - the version control history of fixes, for what really changed;
  - past failures and how they were resolved.
- When the project's material and a general article differ, follow the project's, and tell the user about each difference that changes the skill.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide: each holds the full rules, edge cases and version notes this file leaves out.

- Read [What carries over from your setup](https://code.claude.com/docs/en/cloud-environments#what-carries-over-from-your-setup) when you run in a cloud session. It tables what the session gets from the user's machine and from the repository, and what it doesn't.
- Read [Skills synced from claude.ai](https://code.claude.com/docs/en/skills#how-synced-skills-behave) when the account or the authentication decides which skills you see. It says which sessions sync the account's skills and which don't.
- Read [Explore the .claude directory](https://code.claude.com/docs/en/claude-directory) when the project holds a file the inventory doesn't list, such as an output style, a workflow or agent memory. It maps every file Claude Code reads, with its scope, whether it is committed, and the frontmatter each file accepts.
- Read [Understand how features layer](https://code.claude.com/docs/en/features-overview#understand-how-features-layer) when the new skill shares a name with a skill, subagent or MCP server at another level. It gives the order in which each feature overrides, and which features merge instead.
- Read [How CLAUDE.md files load](https://code.claude.com/docs/en/memory#how-claude-md-files-load) when an instruction the skill must respect can sit in a parent folder, a subfolder or an added directory. It gives the load order, when subfolder files load, and how `claudeMdExcludes` skips files.
- Read [Organize rules with .claude/rules/](https://code.claude.com/docs/en/memory#organize-rules-with-claude/rules/) when a rule may govern the files the skill touches. It covers `paths` patterns, user-level rules and rules shared through symlinks.
- Read [Deploy organization-wide CLAUDE.md](https://code.claude.com/docs/en/memory#deploy-organization-wide-claude-md) when the user's organization manages Claude Code. It gives where managed instructions live on each operating system.
- Read [Auto memory](https://code.claude.com/docs/en/memory#auto-memory) when the project keeps auto memory. It says where Claude stores it and how it loads.
- Read [`enabledPlugins`](https://code.claude.com/docs/en/settings-reference#enabledplugins) when you must tell which plugins are on. It gives the setting's format and how each scope sets it.
- Read [Control who invokes a skill](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill), [Load skills in monorepos and subdirectories](https://code.claude.com/docs/en/skills#discovery-from-parent-and-nested-directories) and [Skill descriptions are cut short](https://code.claude.com/docs/en/skills#skill-descriptions-are-cut-short) when a skill you expect is missing from your listing. Together they explain each reason a skill or its description stays out of it.
- Read [Synthesize from existing project artifacts](https://agentskills.io/skill-creation/best-practices#synthesize-from-existing-project-artifacts) when you gather the domain sources. It lists the project material that grounds a skill, and why it beats a general reference.
- Read [See what loaded into context](https://code.claude.com/docs/en/debug-your-config#see-what-loaded-into-context) before you ask the user to run a command. It lists each command and what it shows them.
