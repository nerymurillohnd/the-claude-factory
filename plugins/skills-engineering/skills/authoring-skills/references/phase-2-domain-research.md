# Phase 2: Domain research

How to learn the domain the skill works in, from the project's code and data and from the official sources of every technology it uses, at the version its users run, before you design the skill.

## Gotchas

- The documentation of a tool's latest version can describe options, defaults or commands that the version the user runs doesn't have: find the installed version first, and read the release notes between it and the latest.
- A domain's specialized tool, such as its MCP or documentation server, skill or plugin, often holds newer and more exact documentation than a web search returns: use it before the web.

## 1. Map what the skill depends on

List every technology the skill's task touches, each with the version the user's project or machine runs:

- languages, frameworks and libraries, from the lockfile or the manifest;
- command-line tools and binaries, from their `--version`;
- databases, APIs and services, from the configuration or the user;
- MCP servers, connectors and apps, from the session's tools and settings;
- file formats and standards that the input or the output follows.

When a version can't be found, ask the user, or research the latest and say so.

## 2. Review what the skill acts on

Read the project's code, configuration, schemas, scripts and a sample of the data the skill will work with, and how the project uses each technology: its wrappers, its conventions and the paths it takes. Leave the values of secrets and credentials unread.

## 3. Research the official sources

For each technology on the map:

1. Use the domain's specialized tool first, then its official documentation, API reference, changelog or release notes and official repository, and a web search only to find their current pages.
2. Read whole sections, and follow their links to the parts the skill depends on.
3. Check the release notes from the installed version to the latest for removals, renames, changed defaults and fixes that bear on the skill.
4. Record each source with its URL, its date and the version it covers.

## 4. Gather the project's own material

Build the skill from the project's own material, not from general knowledge: a skill built from the team's runbooks and incident reports carries their schemas, failure modes and fixes, which a general article on the topic can't.

- Read what the project holds on the skill's domain:
  - runbooks, internal documentation and style guides;
  - API specifications, schemas and configuration files;
  - code review comments and issues, for the concerns that recur;
  - the version control history of fixes, for what really changed;
  - past failures and how they were resolved.

## 5. Settle conflicts

- When the project's material and a general article differ, follow the project's.
- When the project's material contradicts a technology's official documentation, tell the user, ask which prevails, and record the answer with the other decisions of Phase 2.
- When two official sources disagree, follow the one that owns the technology, and tell the user.

## 6. Carry it into the design

Put each technology, its version and its sources in the Domain sources section of the design proposal. Write every fact that defies what Claude would assume into the skill, as a rule or a gotcha.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Start from real expertise](https://agentskills.io/skill-creation/best-practices#start-from-real-expertise) when you are about to write a skill from general knowledge. It explains why a skill built without the domain's own context comes out vague and generic.
- Read [Synthesize from existing project artifacts](https://agentskills.io/skill-creation/best-practices#synthesize-from-existing-project-artifacts) when you gather the project's material. It lists the material that grounds a skill, and why it beats a general reference.
