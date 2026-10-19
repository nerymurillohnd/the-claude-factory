---
name: svelte-docs-and-autofixer
description: Fetches the official Svelte, SvelteKit and Svelte CLI docs and checks Svelte code with the Svelte autofixer, through the plugin's Svelte MCP tools. Use when an exact Svelte API, rune, option or signature matters, to check Svelte code pasted in the chat for problems (a review of project files goes to the svelte-code-auditor agent), or for a Svelte playground link.
license: MIT
metadata:
  upstream: "sveltejs/ai-tools skills/svelte-code-writer"
  base: "6b5d0dab3c9c083387247ab20dc684573481076b"
---

# Svelte docs and autofixer

## Overview

The contract for the two tools that keep Svelte code current: reading the official docs before writing (`get-documentation`, `list-sections`) and proving code with the Svelte autofixer after writing. Svelte 5 and SvelteKit 3 changed APIs that training data still shows the old way, so neither job is done from memory. It also covers the fallbacks when the MCP server is unavailable and the playground link.

## When to use it and when not

| Use it | Do not use it |
|---|---|
| Before writing or changing any `.svelte`, `.svelte.ts` or `.svelte.js` code, or replying with Svelte code | For where a symbol of the project is defined or used: that is the `svelte-lsp-intelligence` skill |
| When asked whether Svelte code pasted in the chat has problems (a review of project files goes to the `svelte-code-auditor` agent, by ground rule 0) | For React, Vue, plain TypeScript or other non-Svelte code |
| When an exact rune, template tag, SvelteKit API, option or config key matters | |
| When the project's Svelte or SvelteKit version is newer than what you remember | |

## Governance rules

Depart from any rule that holds here, ground rule or rule of this skill, only for a reason you state to the user.

### Ground rules for every Svelte task

The ground rules (0 to 5) live in the `svelte-development:svelte-best-practices` skill and hold for this skill; "ground rule N" below means rule N there, and its rule 0 decides who does the work. Load that skill first with the Skill tool unless it is already in your context (the plugin's agents have it preloaded).

### Rules of this skill

The short tool names (`get-documentation`, `svelte-autofixer`, `list-sections`, `playground-link`) stand for their full names, `mcp__plugin_svelte-development_svelte__<tool>`.

1. **Sections from the docs map.** Fetch every section a change touches in one `get-documentation` call (ground rule 2), with the path from the docs map's second column; a title works only when it is unique in the map (titles such as "Overview" repeat). Call `list-sections` only for a topic the map lacks; this wins over that tool's description, which says to always call it first. Astro and Tailwind CSS docs are not on the server: fetch their raw URLs from the map with `curl -sS`.
2. **Pass code, never a path, to the remote server.** It treats a file path as code and answers "no issues" instead of refusing it. Read the file and pass its full content as `code`, and its real file name as `filename` (`Counter.svelte`, `counter.svelte.ts`). Without a filename the code is checked as a component, and a plain `.ts` name gives false errors; empty code comes back clean too. Only the local command line below takes a path.
3. **The autofixer is not proof.** It does not type-check, does not know SvelteKit routing rules and does not run the code. Type errors come from the language server and the project check.
4. **Older versions.** The live docs describe the newest Svelte and SvelteKit. On an older installed version, check each API against it before using it, reading the changelog window when "When to run the check" in the changelogs reference calls for it.
5. **Playground links only for code answered in the chat**, never for code written to the project's files. A user's request for a link is their consent; otherwise offer one and wait for a yes.
6. **Network and privacy.** Every MCP call needs network access. `svelte-autofixer` sends the code you pass to the Svelte team's server (Svelte states it does not log, store or inspect it); when the user does not want code to leave the machine, use the local command line below.
7. **No downloads without consent.** Never install `@sveltejs/mcp` or run it through `npx` (which downloads it) without the user's confirmation.

## Contents

- [Where things are](#where-things-are)
- [Tools](#tools)
- [Procedure](#procedure)
- [When the MCP server is unavailable](#when-the-mcp-server-is-unavailable)
- [What the user can start](#what-the-user-can-start)

## Where things are

- `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/docs-map.md`: every documentation section classified by area, with its `get-documentation` path and raw URL. Read it to choose sections.
- `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/known-doc-errata.md`: doc statements known to be wrong or out of date, with what is right. Look up every page you read before copying its example.
- `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`: when to read a changelog window, and the commands that read it.
- The `svelte-best-practices` skill: the ground rules, who does the work, and the Svelte 5 and SvelteKit 3 rules to write by. The `svelte-lsp-intelligence` skill: language server diagnostics and how to prove the server answers.

## Tools

The plugin connects to the Svelte team's remote MCP server, `https://mcp.svelte.dev/mcp`. The tools may be deferred; load the ones you need before concluding they are missing:

```text
ToolSearch
  query: "select:mcp__plugin_svelte-development_svelte__get-documentation,mcp__plugin_svelte-development_svelte__svelte-autofixer,mcp__plugin_svelte-development_svelte__list-sections,mcp__plugin_svelte-development_svelte__playground-link"
```

| Tool | Returns |
|---|---|
| `list-sections` | Every section with its `path` and a use-case hint |
| `get-documentation` | The full text of each requested section |
| `svelte-autofixer` | `issues`, `suggestions`, `require_another_tool_call_after_fixing` |
| `playground-link` | A svelte.dev playground URL holding the code |

Section paths are written exactly as `list-sections` prints them, without a leading `docs/`: `svelte/$state`, `kit/load`, `cli/sv-migrate`. A `docs/kit/…` path returns only "similar results". The `list-sections` hints are missing for the newest sections, including every SvelteKit 3 addition and declaration tags; the docs map classifies them.

## Procedure

Copy this checklist for any Svelte code you write, change or review, and run the calls in this order.

```
- [ ] 1 Baseline  in a project, when the change touches what other files use: the project check once (ground rule 5)
- [ ] 2 Find      choose the sections in docs-map.md; call list-sections only for a topic the map lacks
- [ ] 3 Read      one get-documentation call with every section the code touches; look each page up in known-doc-errata.md
- [ ] 4 Write     write or edit the code from what the sections say (a review skips this step)
- [ ] 5 Fix       svelte-autofixer on each Svelte file's full code, until no issues remain and each suggestion is applied
                  or named as skipped (ground rule 4); in a review, report instead of applying
- [ ] 6 Verify    in a project: language server diagnostics after an edit, when the server answers (a review uses
                  the project check), and the project check (ground rule 5)
```

**Step 3, read the sections in one call:**

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["svelte/$props", "svelte/$bindable"]
```

**Step 5, check the code.** Pass the whole file as `code` and the installed `svelte` version in full (ground rules 1 and 4); with no project, pass `5` unless the user says the code is Svelte 4. Version 4 checks Svelte 4 syntax with the Svelte 5 compiler in legacy mode; Svelte 3 is refused, so report a Svelte 3 file as not checked by the autofixer. Set `async: true` only when the project enables `compilerOptions.experimental.async`: in `svelte.config.js`, or in SvelteKit 3 in the `sveltekit({ … })` options in `vite.config`.

```text
mcp__plugin_svelte-development_svelte__svelte-autofixer
  code: "<script lang=\"ts\">\n  let { value = $bindable(0) }: { value?: number } = $props();\n</script>\n…"
  desired_svelte_version: "<installed svelte version from npm ls, such as 5.57.2>"
  filename: "Counter.svelte"
```

It reports Svelte compiler errors and Svelte-specific mistakes: legacy syntax, effects that should be derived values, runes misuse, and version-gated suggestions such as replacing `class:` directives with the `class` attribute. Compiler warnings (accessibility, deprecations) arrive as issues. Only the first compiler error is reported, and it stops every other check for the file: fix it and run again. The suggestion attached to a JavaScript parse error is generic: fix the error at the reported line.

**Step 6, verify.** Skip it for code pasted in the chat with no project. A review edits nothing, so it gets no language server diagnostics and relies on the project check. Diagnostics come after each edit of a `.svelte` file only (the language server serves no `.svelte.ts` or `.svelte.js` file), and only when the server answers: "no diagnostics" proves nothing until `documentSymbol` on a `.svelte` file has listed its symbols (`svelte-lsp-intelligence`, rule 9). Without the server, rely on the project check and say so. The project check and its commands are ground rule 5's. One Svelte, preprocessor or configuration error hides the file's other Svelte compiler diagnostics (TypeScript and CSS diagnostics still appear): `${CLAUDE_PLUGIN_ROOT}/skills/svelte-lsp-intelligence/references/troubleshooting.md`, "Diagnostics that hide others".

**Done** when the autofixer returns no issues and every remaining suggestion is applied or named as skipped with its reason (or the remaining issues are reported as likely false positives), and, in a project, ground rule 5 is met; `require_another_tool_call_after_fixing` stays true while any suggestion remains. A review is done when it has reported the autofixer and check results.

**Playground link**, when the user asked for one or said yes:

```text
mcp__plugin_svelte-development_svelte__playground-link
  name: "Bindable counter"
  tailwind: false
  files: { "App.svelte": "<the code from the answer>" }
```

## When the MCP server is unavailable

Claude Code reconnects a dropped server on its own; the user can also reconnect it from `/mcp`. While the tools still fail, say in the answer that the documentation or the code could not be checked through the server, and use these fallbacks in order:

1. **Raw download of the docs.** Fetch the section's text and filter it:

   ```sh
   curl -sS 'https://svelte.dev/docs/kit/load/llms.txt' | grep -n 'depends'
   ```

   The URL pattern is `https://svelte.dev/docs/<area>/<slug>/llms.txt`; the docs map lists it for every section. Keep the URL in single quotes: slugs such as `$state` would otherwise be expanded by the shell.
2. **Local command line, if the user has it.** The `@sveltejs/mcp` package, installed globally by the user, provides the `svelte-mcp` command: it runs on their machine, sends no code and reads file paths. Use it offline or when code must not leave the machine. Put arguments that contain `$` in single quotes, because double quotes let the shell expand `$state`, and pass the full installed version to `--svelte-version`:

   ```sh
   svelte-mcp list-sections
   svelte-mcp get-documentation 'svelte/$props,svelte/$bindable'
   svelte-mcp svelte-autofixer src/lib/components/Counter.svelte --svelte-version <installed svelte version> # add --async when the project enables experimental async
   ```

   Probe it with `svelte-mcp list-sections`, never with `command -v svelte-mcp`. The Bash command's environment may not be the user's shell, so `command not found` there does not prove the tool is missing: ask the user to confirm in their own shell. If it is missing, the user installs it with `npm install -g @sveltejs/mcp`; ask before suggesting `npx`. On an autofixer run, check that the output starts with `Detected file path`: `File not found, treating input as code` means the path was wrong and the result says nothing about the file.

When neither the server nor the local command line can run the autofixer, report the code as not checked by the autofixer and finish with the project check.

## What the user can start

The server also offers two things the user starts, not the model:

- **Resources (`doc-section`)**: every section as a `svelte://` resource. The user attaches one by typing `@` and picking it, for example the transition docs before asking for an animated component. When a user wants a page "in context", tell them they can attach it this way; you fetch the same content with `get-documentation`.
- **Prompt `svelte-task`**: takes a `task` argument and injects instructions plus the section list for it; the user runs it from the `/` menu.

Derived from the `svelte-code-writer` skill of sveltejs/ai-tools (MIT), base `6b5d0da`; see the plugin's NOTICE.txt. Sources: the remote server's `tools/list` schemas and runtime output, and the `@sveltejs/mcp` command line; https://svelte.dev/docs/ai/llms.txt, https://svelte.dev/docs/ai/resources, https://svelte.dev/docs/ai/prompts; https://code.claude.com/docs/en/mcp and https://code.claude.com/docs/en/plugins-reference (plugin agents are named `<plugin>:<agent>`).
