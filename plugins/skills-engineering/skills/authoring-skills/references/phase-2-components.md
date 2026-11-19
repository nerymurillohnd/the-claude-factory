# Phase 2: Components

The components a skill can have, what each one is for, and which file of Phase 2 shows how to build it. Choose here which ones the skill needs.

## The components

A skill has its own files, mechanisms it declares in `SKILL.md`, and components outside it that it ships with or relies on.

**A. Files of the skill**

| Component | What it is for |
| :-- | :-- |
| `SKILL.md` | Required: the frontmatter, which decides when the skill loads, and the body, the instructions every run needs |
| `references/` | Depth that only some runs need, read when `SKILL.md` points to it |
| `scripts/` | Code that must run the same way every time, run without being read |
| `assets/` | Files the output starts from: templates, images, data, schemas |

**B. Mechanisms declared in `SKILL.md`**

| Component | What it is for |
| :-- | :-- |
| `hooks` | A check that must hold every time while the skill is active |
| `allowed-tools` and `disallowed-tools` | Tools pre-approved for the skill's commands, or removed while it runs |
| `context: fork` and `agent` | Running the skill as a subagent's task, out of the main conversation |
| `arguments` and `argument-hint` | Inputs the user passes with the command |
| `paths` | Loading the skill automatically only for certain files |
| Injected commands | Live data, such as a diff, put into the skill as it loads |

**C. Components outside the skill**

| Component | What it is for |
| :-- | :-- |
| Subagent | Work that needs its own context and tools, or a subagent that carries the skill as knowledge |
| Plugin hooks | A rule that must hold whether or not the skill was invoked |
| MCP server | Access to an external system the skill teaches Claude to use |
| Other skills and tools | Work an existing skill or MCP tool already does, named and relied on |
| Configuration and state | Values the user provides once, and data that must outlive a session |

## Choose the components

Start from `SKILL.md` alone, and add each component only for the failure it fixes:

| The failure | The component |
| :-- | :-- |
| `SKILL.md` grows past what every run needs | `references/` |
| Claude rewrites the same logic, or a step must give the same result every time | A script in `scripts/` |
| The output starts from a fixed file | `assets/` |
| A rule is skipped under pressure, and must always hold | A hook |
| The task would fill the main conversation and needs none of its history | `context: fork`, or a subagent |
| The skill needs an external system | An MCP server, or an existing MCP tool |
| The user supplies the same values on every run | Configuration |

For each component you choose, read its file of Phase 2: scripts, injected commands, hooks, skills for subagents, tools and other skills, or configuration, state and security. The skill architecture file of Phase 2 then lays out where each one lives.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide: each holds the full rules, edge cases and version notes this file leaves out.

- Read [Directory structure](https://agentskills.io/specification#directory-structure) and [Optional directories](https://agentskills.io/specification#optional-directories) of the Agent Skills specification when you lay out the skill's files. They give the required `SKILL.md` and what `scripts/`, `references/` and `assets/` hold.
- Read [How Skills work](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#how-skills-work) when you weigh what each file costs. It explains the three levels of loading: metadata, instructions and resources.
- Read [Add supporting files](https://code.claude.com/docs/en/skills#add-supporting-files) when the skill splits content into other files. It shows how `SKILL.md` points to them.
- Read [Frontmatter reference](https://code.claude.com/docs/en/skills#frontmatter-reference) when the skill declares a mechanism of section B. It gives each field and its effect.
- Read [Inject dynamic context](https://code.claude.com/docs/en/skills#inject-dynamic-context) when the skill needs live data as it loads. It shows how injected commands run and what aborts the skill.
- Read [Add components to a plugin](https://code.claude.com/docs/en/plugins/components) when the skill ships in a plugin with other components. It shows each component's folder and an example that validates.
- Read [Compare similar features](https://code.claude.com/docs/en/features-overview#compare-similar-features) when a need could be met by a skill or by another component. It compares them pair by pair.
