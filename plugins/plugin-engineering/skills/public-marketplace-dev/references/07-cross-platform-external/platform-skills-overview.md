---
title: Agent Skills
url: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
description: Agent Skills are modular capabilities that extend Claude's functionality. Each Skill packages instructions, metadata, and optional resources (scripts, templates) that Claude uses automatically when relevant.
featureMetadata:
  status: stable
  zdr:
    eligibility: not-eligible
    note: Skill data retained according to standard policy.
  supportedModels:
    - claude-fable-5-1
    - claude-mythos-5-1
    - claude-fable-5
    - claude-mythos-5
    - claude-mythos-preview
    - claude-opus-5-5
    - claude-opus-5
    - claude-sonnet-5-5
    - claude-sonnet-5
    - claude-haiku-5-5
    - claude-haiku-4-5-20251001
    - claude-opus-4-8
    - claude-opus-4-7
    - claude-opus-4-6
    - claude-sonnet-4-6
    - claude-opus-4-5-20251101
    - claude-sonnet-4-5-20250929
  supportedPlatforms:
    Claude API: stable
    Claude Platform on AWS: stable
    Claude Models on Google Cloud (Anthropic managed): stable
    Microsoft Foundry (hosted on Anthropic):
      availability: stable
      note: Hosted on Anthropic deployments only; the skill version download endpoint (`GET /v1/skills/{skill_id}/versions/{version}/content`) is not supported on Foundry.
---

# Agent Skills

Agent Skills are modular capabilities that extend Claude's functionality. Each Skill packages instructions, metadata, and optional resources (scripts, templates) that Claude uses automatically when relevant. This file explains how Skills load, where they work in Claude Code, the required `SKILL.md` structure, and the security and runtime constraints to design for. The frontmatter above records the page's feature status, ZDR eligibility, supported models and supported platforms.

## Contents

- [How Skills work](#how-skills-work)
  - [Level 1: Metadata (always loaded)](#level-1-metadata-always-loaded)
  - [Level 2: Instructions (loaded when triggered)](#level-2-instructions-loaded-when-triggered)
  - [Level 3: Resources and code (loaded as needed)](#level-3-resources-and-code-loaded-as-needed)
  - [The Skills architecture](#the-skills-architecture)
  - [Example: Loading a PDF processing Skill](#example-loading-a-pdf-processing-skill)
- [Where Skills work](#where-skills-work)
  - [Claude Code](#claude-code)
- [Skill structure](#skill-structure)
- [Security considerations](#security-considerations)
  - [Sharing scope](#sharing-scope)
  - [Runtime environment constraints](#runtime-environment-constraints)
- [Documentation References](#documentation-references)

## How Skills work

Skills use Claude's VM environment to provide capabilities beyond what prompts alone allow. Claude operates in a virtual machine with filesystem access, so a Skill exists as a directory containing instructions, executable code, and reference materials, organized like an onboarding guide for a new team member.

This filesystem-based architecture enables **progressive disclosure:** Claude loads information in stages as needed, rather than consuming context upfront.

A Skill can contain three types of content, each loaded at a different time:

### Level 1: Metadata (always loaded)

The Skill's YAML frontmatter provides discovery information:

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---
```

Claude loads this metadata at startup and includes it in the system prompt. Claude matches the user's request against the `description` to decide whether to trigger the Skill, so the description must say both what the Skill does and when to use it. Because only a Skill's name and description occupy context until the Skill is triggered, many Skills can be installed without a context penalty.

### Level 2: Instructions (loaded when triggered)

The main body of `SKILL.md` contains procedural knowledge: workflows, best practices, and guidance:

````markdown
# PDF Processing

## Quick start

Use pdfplumber to extract text from PDFs:

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

For advanced form filling, see [FORMS.md](FORMS.md).
````

When a request matches a Skill's description, Claude reads `SKILL.md` from the filesystem using bash. Only then does this content enter the context window.

### Level 3: Resources and code (loaded as needed)

A Skill can bundle additional materials:

* `pdf-processing/`

  * `SKILL.md` (main instructions)
  * `FORMS.md` (form-filling guide)
  * `REFERENCE.md` (detailed API reference)
  * `scripts/`
    * `fill_form.py` (utility script)

**Instructions:** Additional Markdown files (`FORMS.md`, `REFERENCE.md`) containing specialized guidance and workflows

**Code:** Executable scripts (`fill_form.py`, `validate.py`) that Claude runs using bash, providing deterministic operations without loading their code into context

**Resources:** Reference materials such as database schemas, API documentation, templates, or examples

Claude accesses these files only when referenced. Each content type has a different strength: instructions for flexible guidance, code for reliability, resources for factual lookup.

| Level                     | When loaded             | Token cost             | Content                                                                                                                     |
| ------------------------- | ----------------------- | ---------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **Level 1: Metadata**     | Always (at startup)     | \~100 tokens per Skill | `name` and `description` from YAML frontmatter                                                                              |
| **Level 2: Instructions** | When Skill is triggered | Under 5k tokens        | `SKILL.md` body with instructions and guidance                                                                              |
| **Level 3+: Resources**   | As needed               | None until accessed    | Bundled files. Reference files load into context when read. Scripts run through bash, and only their output enters context. |

Progressive disclosure ensures only relevant content occupies the context window at any given time.

### The Skills architecture

Skills run in a code execution environment where Claude has filesystem access, bash commands, and code execution capabilities. Skills exist as directories on a virtual machine, and Claude interacts with them using the same bash commands used to navigate files on a computer.

Diagram (image): Agent Skills architecture, showing how Skills integrate with the agent's configuration and virtual machine.

![Agent Skills architecture, showing how Skills integrate with the agent's configuration and virtual machine](https://platform.claude.com/docs/images/agent-skills-architecture.svg)

> **View the image** [`assets/agent-skills-architecture.png`](../../assets/agent-skills-architecture.png) **to** see how skills live in the agent's file system next to its configuration.

**How Claude accesses Skill content:**

When a Skill is triggered, Claude uses bash to read `SKILL.md` from the filesystem, bringing its instructions into the context window. If those instructions reference other files (such as `FORMS.md` or a database schema), Claude reads those files too using additional bash commands. When instructions mention executable scripts, Claude runs them through bash and receives only the output (the script code itself never enters context).

**What this architecture makes possible:**

* **On-demand file access:** Claude reads only the files each task needs. A Skill can include dozens of reference files, but if a task only needs the sales schema, that's the one file Claude loads. The rest stay on the filesystem and cost zero tokens.
* **Efficient script execution:** When Claude runs `validate_form.py`, the script’s code never loads into the context window. Only its output (such as “Validation passed” or a specific error message) consumes tokens, which makes scripts far more efficient than having Claude generate equivalent code during the task.
* **No practical limit on bundled content:** Files don't consume context until accessed, so Skills can include comprehensive API documentation, large datasets, or extensive examples. There's no context penalty for bundled content that isn't used.

### Example: Loading a PDF processing Skill

This is how Claude loads and uses the custom `pdf-processing` Skill from the earlier examples (not the pre-built `pdf` Skill):

1. **Startup:** System prompt includes: `pdf-processing - Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.`
2. **User request:** "Extract the text from this PDF and summarize it."
3. **Claude calls:** `bash: cat pdf-processing/SKILL.md` → Instructions loaded into context.
4. **Claude determines:** Form filling is not needed, so Claude doesn't read `FORMS.md`.
5. **Claude completes the task:** Uses the instructions from `SKILL.md`.

Diagram (image): Skills loading into the context window: the progressive loading of Skill metadata and content.

![Skills loading into the context window: the progressive loading of Skill metadata and content](https://platform.claude.com/docs/images/agent-skills-context-window.svg)

> **View the image** [`assets/agent-skills-context-window.png`](../../assets/agent-skills-context-window.png) **to** see how skill metadata and content load into the context window in stages.

## Where Skills work

Skills are available across Claude's agent products. This pruned copy keeps only Claude Code.

### Claude Code

[Claude Code](https://code.claude.com/docs/en/overview) supports custom Skills. The pre-built document Skills (PowerPoint, Excel, Word, PDF) are not available in Claude Code, though the open-source [Claude API skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/claude-api-skill) comes bundled with it. See the full list of [built-in commands and Skills](https://code.claude.com/docs/en/commands) that ship with Claude Code.

**Custom Skills:** Create Skills as directories with `SKILL.md` files. Claude discovers and uses them automatically.

To learn more, see [Use Skills in Claude Code](https://code.claude.com/docs/en/skills).

## Skill structure

Every Skill requires a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: your-skill-name
description: Brief description of what this Skill does and when to use it
---

# Your Skill Name

## Instructions
[Clear, step-by-step guidance for Claude to follow]

## Examples
[Concrete examples of using this Skill]
```

**Required fields:** `name` and `description`

**Field requirements:**

`name`:

* Maximum 64 characters
* Must contain only lowercase letters, numbers, and hyphens
* Cannot contain XML tags
* Cannot contain reserved words: `anthropic`, `claude`

`description`:

* Must be non-empty
* Maximum 1,024 characters
* Cannot contain XML tags

The `description` must include both what the Skill does and when Claude should use it. For complete authoring guidance, see [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

## Security considerations

Use Skills only from trusted sources: Skills the user created or obtained from Anthropic. Skills give Claude new capabilities through instructions and code, which also means a malicious Skill can direct Claude to call tools or run code in ways that don't match the Skill's stated purpose.

> **Warning:** If you must use a Skill from an untrusted or unknown source, exercise extreme caution and thoroughly audit it before use. Depending on what access Claude has when running the Skill, malicious Skills could lead to data exfiltration, unauthorized system access, or other security risks.

**Key security considerations:**

* **Audit thoroughly:** Review all files bundled in the Skill: `SKILL.md`, scripts, images, and other resources. Look for unusual patterns such as unexpected network calls, file access patterns, or operations that don't match the Skill's stated purpose.
* **External sources are risky:** Skills that fetch data from external URLs pose particular risk, as fetched content might contain malicious instructions. Even trustworthy Skills can be compromised if their external dependencies change over time.
* **Tool misuse:** Malicious Skills can call tools (file operations, bash commands, code execution) in harmful ways.
* **Data exposure:** Skills with access to sensitive data could be designed to leak information to external systems.
* **Treat like installing software:** Be especially careful when integrating Skills into production systems with access to sensitive data or critical operations.

### Sharing scope

Skills have different sharing models depending on the surface:

* **Claude Code:** Personal (`~/.claude/skills/`) or project-based (`.claude/skills/`). Can also be shared through Claude Code plugins.

### Runtime environment constraints

The exact runtime environment available to a Skill depends on the product surface where it runs.

* **claude.ai:**
  * **Varying network access:** Depending on user/admin settings, Skills might have full, partial, or no network access. For more details, see the [Create and edit files with Claude](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude#h_6b7e833898) support article.

* **Claude Code:**

  * **Full network access:** Skills have the same network access as any other program on the user's computer.
  * **Global package installation discouraged:** Skills should only install packages locally to avoid interfering with the user's computer.

Design Skills to work within these constraints.

## Documentation References

- Source page: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview — the full Agent Skills overview, including the surfaces other than Claude Code that this pruned copy omits.
- https://platform.claude.com/docs/images/agent-skills-architecture.svg — the Agent Skills architecture diagram.
- https://platform.claude.com/docs/images/agent-skills-context-window.svg — the diagram of Skills loading progressively into the context window.
- https://code.claude.com/docs/en/overview — Claude Code overview.
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/claude-api-skill — the open-source Claude API skill bundled with Claude Code.
- https://code.claude.com/docs/en/commands — built-in commands and Skills that ship with Claude Code.
- https://code.claude.com/docs/en/skills — creating and managing custom Skills in Claude Code (also the "Use Skills in Claude Code" card in the removed "Next steps" section).
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices — Skill authoring best practices: how to write effective Skills that Claude can discover and use successfully (also a card in the removed "Next steps" section).
- https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude — claude.ai support article on creating and editing files, including Skill network access.
