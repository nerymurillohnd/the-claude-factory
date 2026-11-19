# Phase 2: Domain research

How to research everything the skill draws on, in any field, from the user's own material and from primary and expert sources, deeply enough that the skill meets its goal, before you design it.

## Gotchas

- The documentation of a tool's latest version can describe options, defaults or commands that the version the user runs doesn't have: find the installed version first, and read the release notes between it and the latest.
- A domain's specialized tool, such as its MCP or documentation server, skill or plugin, often holds newer and more exact information than a web search returns: use it before the web.
- A general article can repeat outdated or unverified advice: check each claim it makes against a primary source before the skill states it.

## 1. Map what the skill draws on

List everything the skill's task depends on, whatever the field, such as code, data, design, marketing, documentation, science, operations or productivity:

- the discipline's knowledge: its methods, standards, quality criteria and common failures, such as a style guide, an accounting standard, a regulation or a research method;
- technologies: languages, libraries, binaries, databases, APIs and operating systems, each with the version its users run, from the lockfile, the manifest, `--version`, the configuration or the user;
- platforms, apps, MCP servers and connectors, and the rules they impose, such as an ad platform's policies or an API's limits;
- the user's own material: their templates, guidelines, examples, past work and conventions.

When a version or an edition can't be found, ask the user, or research the latest and say so.

## 2. Review what the skill acts on

When the skill serves a project or works on the user's material, read what it will act on: the code, configuration, data, documents, designs or campaigns, and how the user works with them, such as their wrappers, conventions and the paths they take. Leave the values of secrets and credentials unread.

## 3. Research the sources

For each item on the map:

1. Read the primary sources first: the domain's specialized tool, then the official documentation, official repository, standard, regulation, platform policy or peer-reviewed research that owns each fact, and each tool's own `--help` or `--version` output. Use a web search to find their current pages.
2. Then read recognized expert sources, such as practitioner guides, case studies and articles from established authorities, for the practice the primary sources don't cover.
3. Read whole sections, and follow their links to the parts the skill depends on. Cover every dimension the task touches, and stop when the last two sources add no new fact.
4. For a technology, check the release notes from the installed version to the latest for removals, renames, changed defaults and fixes that bear on the skill.
5. When the research is broad and the environment offers subagents, split it among parallel subagents, one area each, and check their facts against the sources before you use them.
6. Record each source with its URL, its date and the version or edition it covers.

## 4. Gather the project's own material

When the skill serves a project, build it from the project's own material, not from general knowledge: a skill built from the team's runbooks and incident reports carries their schemas, failure modes and fixes, which a general article on the topic can't.

- Read what the project holds on the skill's domain:
  - runbooks, internal documentation and style guides;
  - API specifications, schemas and configuration files;
  - code review comments and issues, for the concerns that recur;
  - the version control history of fixes, for what really changed;
  - past failures and how they were resolved.

## 5. Settle conflicts

- When a primary source and an expert source differ, follow the primary source.
- When the project's material and a general article differ, follow the project's.
- When the project's material contradicts a primary source, tell the user, ask which prevails, and record the answer with the other decisions of Phase 2.
- When two primary sources disagree, follow the one that owns the subject, and tell the user.

## 6. Carry it into the design

Put each area and technology, its version or edition, and its sources in the Domain sources section of the design proposal. Write every fact that defies what Claude would assume into the skill, as a rule or a gotcha.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Start from real expertise](https://agentskills.io/skill-creation/best-practices#start-from-real-expertise) when you are about to write a skill from general knowledge. It explains why a skill built without the domain's own context comes out vague and generic.
- Read [Synthesize from existing project artifacts](https://agentskills.io/skill-creation/best-practices#synthesize-from-existing-project-artifacts) when you gather the project's material. It lists the material that grounds a skill, and why it beats a general reference.
