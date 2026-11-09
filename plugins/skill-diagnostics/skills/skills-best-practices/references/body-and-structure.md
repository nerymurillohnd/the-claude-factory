# Body and structure

How to write the `SKILL.md` body, how to lay out the skill's files, and the order of blocks in `SKILL.md`.

## Contents

- [Writing the body](#writing-the-body)
- [Structure and supporting files](#structure-and-supporting-files)
- [Paths and placeholders](#paths-and-placeholders)
- [Integrity of the skill's files](#integrity-of-the-skills-files)
- [Order of blocks in SKILL.md](#order-of-blocks-in-skillmd)

## Writing the body

Write only what the agent would get wrong without the skill, at the level of control the task's fragility needs \[AS\]\[PL\].

1. **Start from real expertise.** Extract the skill from a real task you completed with the agent (steps that worked, your corrections, input/output formats, context you supplied), or synthesize it from your own runbooks, specs, review comments, fixes and incidents. A skill generated from generic knowledge comes out vague \[AS\]\[PL\].
2. **Add what the agent lacks, omit what it knows.** Ask of each passage: "Would the agent get this wrong without this?" If not, cut it \[AS\]. "Claude is already very smart"; challenge each paragraph's token cost \[PL\].
3. **Explain why only where it changes behavior.** In Claude Code, state what to do rather than narrating how or why \[CC\]; the open standard says to explain the why, because reasoning-based instructions work better than rigid directives \[AS\]. The first targets token cost, the second compliance: give the reason only where it changes what the agent does.
4. **Prefer a reason to emphatic wording.** Reasoning works better than "ALWAYS do X, NEVER do Y" \[AS\], though on the Platform, Claude A (the instance that refines a skill, [evaluation.md](evaluation.md#what-an-audit-cant-assess)) may recommend "stronger language such as 'MUST filter'" \[PL\]. Prefer a reason; a rule that must always hold goes in a hook (item 13).
5. **Design a coherent unit.** Like a function: too narrow forces several skills to load for one task; too broad makes it hard to trigger precisely \[AS\].
6. **Aim for moderate detail.** Concise stepwise guidance with one working example beats exhaustive documentation; leave most edge cases to the agent's judgment \[AS\].
7. **Match specificity to fragility.** High freedom (prose heuristics) when many approaches are valid; medium (pseudocode, parameterized scripts) when a preferred pattern exists; low (an exact command, "do not modify the command") when operations are fragile or order matters. "Narrow bridge with cliffs" versus "open field" \[PL\]\[AS\]. Calibrate each part separately \[AS\].
8. **Give defaults, not menus.** Pick one tool or approach and name an escape hatch ("Use pdfplumber… For scanned PDFs, use pdf2image with pytesseract instead") \[AS\]\[PL\].
9. **Teach procedures, not answers.** The approach should generalize to the class of problems; specific details such as output templates or "never output PII" are still fine \[AS\].
10. **Write a Gotchas section.** Concrete, environment-specific facts that defy reasonable assumptions, kept in `SKILL.md` so the agent reads them before it hits them. Add every correction you have to make \[AS\].
11. **Provide templates and examples for output.** A concrete template is more reliable than prose; strict ("ALWAYS use this exact template") or flexible ("a sensible default") as needed. Input/output example pairs convey style best \[AS\]\[PL\]. Output that another step parses gets the strict form \[PL\] `rec`.
12. **Use one term per concept** throughout (always "field", never "box" or "element") \[PL\].
13. **Write standing instructions.** In Claude Code a loaded skill isn't re-read, so word guidance for the whole task ("Run the tests after every edit"); move rules that must hold every time into a hook \[CC\]. A rule that must hold every time belongs in a hook (the skill's `hooks` frontmatter keeps it with the skill), because instructions can be skipped later in a session \[CC\]. What a hook in a skill needs is in [claude-code-features.md](claude-code-features.md#hooks-in-a-skill).
14. **Avoid time-sensitive text.** No "before August 2025 use…"; put legacy material in a collapsed "Old patterns" section \[PL\].
15. **Test with every model you will use.** Haiku may need more guidance; Opus may be over-explained \[PL\].
16. **State what running the skill authorizes.** A skill with side effects says what invoking it permits and what still needs the user ("authorizes migrations on the development database; production still needs the user") \[SD\] `rec`.
17. **Give a forked or preloaded skill a closed contract.** It states its input, its single final output, and what to return when input is missing, and it never asks the user, because no one is there to answer \[SD\] `rec`.
18. **Name MCP tools in the form of the surface you ship to.** The Platform names them `ServerName:tool_name`, for example `GitHub:create_issue` \[PL\]; Claude Code names them `mcp__<server>__<tool>`, and `mcp__plugin_<plugin-name>_<server-name>__<tool-name>` for a plugin's server \[CC\].

## Structure and supporting files

Keep `SKILL.md` under 500 lines (the open standard also says under 5,000 tokens) and move detail into files that the body names, with the condition for reading each one \[AS\]\[PL\]\[CC\].

```text
my-skill/
├── SKILL.md        # overview and navigation; loaded on trigger
├── references/     # docs read when needed (e.g. finance.md, api-errors.md)
├── assets/         # templates, images, data files, schemas
└── scripts/        # code that is run, not loaded
```

- **Say when to load each file.** "Read `references/api-errors.md` if the API returns a non-200 status" beats "see references/" \[AS\]. Point to a file Claude reads with a relative Markdown link and its condition, as the official pages do: `[FORMS.md](FORMS.md)` \[PL\], `[the reference guide](references/REFERENCE.md)` \[AS\], `[reference.md](reference.md)` \[CC\]; for example "For tracked changes, read `[references/redlining.md](references/redlining.md)`" `rec`.
- **No `${CLAUDE_SKILL_DIR}` inside a link.** Don't put `${CLAUDE_SKILL_DIR}` inside a link, because chat doesn't replace it and the link breaks there \[CP\] `default`.
- **Three organizing patterns** \[PL\]: a high-level guide that links to FORMS.md, REFERENCE.md and EXAMPLES.md; one file per domain (finance, sales, product) so only the relevant one loads; basic content inline with links to advanced topics.
- **One level deep.** Link every reference file directly from `SKILL.md`; nested references may be only partly read (for example with `head -100`) \[PL\]\[AS\].
- **Table of contents** at the top of any reference file over 100 lines \[PL\].
- **Relative paths with forward slashes**, from the skill root, also inside reference files \[AS\]\[PL\].
- **Descriptive file names** (`form_validation_rules.md`, not `doc2.md`); folders by domain or feature \[PL\].
- **Bundle comprehensive resources** freely: unread files cost no context \[PL\].
- **Keep reference files focused**, because smaller files use less context when loaded \[AS\].
- **Say whether to run or read a script**: "Run `analyze_form.py`…" (execute) versus "See `analyze_form.py` for the algorithm" (read) \[PL\].

## Paths and placeholders

- **`${CLAUDE_SKILL_DIR}` in commands.** In Claude Code, reference bundled files with `${CLAUDE_SKILL_DIR}` in commands so paths resolve from any working directory \[CC\]. In a plugin skill it is "the skill's subdirectory within the plugin, not the plugin root" \[CC\] `req`, and it's "a placeholder in the skill text, not an environment variable" \[CP\]. How a plugin hook reaches a script is in [claude-code-features.md](claude-code-features.md#hooks-in-a-skill).
- **Paths that work on every surface.** Name a reference or an asset by its path relative to `SKILL.md` (`references/frontmatter.md`). Run a script as `python3 ${CLAUDE_SKILL_DIR}/scripts/<file>` ([scripts.md](scripts.md#how-to-call-a-script)), keeping the part after the placeholder relative to the skill, so the same line works in Claude Code and Cowork and reads correctly in chat \[CP\]\[CC\] `rec`.
- **Files shared by a plugin's skill and its agents.** `${CLAUDE_PLUGIN_ROOT}` reaches "files bundled anywhere in the plugin, including resources shared between the plugin's skills" \[CC\], but chat copies only the skill's folder \[CP\]. Keep shared rules inside the skill that owns them, and have each agent read them as `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/references/<file>`; agents run only in Cowork and Claude Code \[CP\] `req`.

## Integrity of the skill's files

- **One source per rule.** When a skill and its agents use the same checklist, the checklist lives in one reference file and every other place points to it `default`.
- **No broken or orphan files.** Every local link and every path under `${CLAUDE_SKILL_DIR}` points to a file that exists, and every file in the skill is used by something (an `evals/` folder is exempt) \[SD\] `req`.

## Order of blocks in SKILL.md

`default`. No official page sets a section order. Three facts bear on it: after compaction Claude Code keeps the first 5,000 tokens of each invoked skill \[CC\]; gotchas belong in `SKILL.md` where the agent reads them before it meets the situation \[AS\]; and `SKILL.md` serves as an overview that points Claude to the other files \[PL\]. The order derived from them:

1. Purpose, inputs and the condition for done.
2. Standing rules and defaults that hold for the whole task.
3. Gotchas.
4. Workflow steps and, for a complex workflow, the checklist.
5. Validation loop.
6. Output template and examples.
7. File index: every reference, asset and script, each with when to read or run it. A file can also be named in the step that needs it; the index still lists every one, one level deep from `SKILL.md`.
8. Old patterns, last.

- **A rule after the step it governs is a finding**, because the agent may already have acted.
- **Reference files follow the same idea:** a table of contents first when the file has more than 100 lines \[PL\], then the content in the order the workflow uses it.
