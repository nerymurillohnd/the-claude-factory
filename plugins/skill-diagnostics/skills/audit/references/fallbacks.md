# Fallbacks

Read the section for the case at hand; the main path in `SKILL.md` covers everything else.

## The checker cannot run

Any exit other than 0 or 1, an error trace, no `python3` 3.9+ on `PATH`, or no shell.

- Record `checker not run: <reason, with the first error line>` and continue; the lenses still run.
- Inventory: list the files with this session's own tool, `find -L "<skill-dir>" -type f` by default (Glob with `**/*` and `**/.*` stops at 100 results). Name the tool on the report's Files line.
- If the path of this audit skill's own folder (the start of the script path) contains a space, quote the script path: the command then needs the user's approval, which is safe to give.

## The inventory is incomplete

`not_listed` has an entry, `find` printed an error, or Glob returned 100 results.

- List what is missing as not inspected; the verdict is not determinable.
- If no inventory can be made at all, skip the checker and the lenses for that skill, give it not determinable, and say why in place of the findings.

## A path resolves to no skill

- A file or folder with no `SKILL.md` at or above it, or a plugin root with no skills: report `path not found: <path>` or `no skills in plugin: <path>`, and go on with the other paths.
- In the summary table, give it a row with that text as the verdict.

## An agent is unavailable or fails

Agents not available, or an agent returns anything other than its report block:

- Read that lens's reference completely and apply it yourself, one skill at a time.
- Its report block feeds the merge (step 4); it is not your final message.
