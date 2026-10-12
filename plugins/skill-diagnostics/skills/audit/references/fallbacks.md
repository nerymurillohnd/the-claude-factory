# Fallbacks

Read the section for the case at hand; the main path in `SKILL.md` covers everything else.

## The checker cannot run

Any exit other than 0, no valid JSON, an error trace, no `python3` 3.9+ on `PATH`, or no shell.

- First, if the path of this audit skill's own folder (the start of the script path) contains a space, retry once with the script path quoted; the command then needs the user's approval, which is safe to give.
- Still failing: record `checker not run: <reason, with the first error line>` and continue; the lenses still run.
- Inventory: if `--list` worked and only the check failed, keep the step 1 inventory. Only if `--list` failed, list the files with this session's own tool, `find "<skill-dir>" -type f` by default (Glob with `**/*` and `**/.*` stops at 100 results), and the links with `find "<skill-dir>" -type l`. Without the checker there is no way to see where a link leads: report every link as not inspected. Name the tool on the report's Files line.

## The inventory is incomplete

`not_listed` has an entry, `find` printed an error or found links, or Glob returned 100 results. `outside` and `loops` entries are not gaps.

- List what is missing as not inspected; step 6 of `SKILL.md` decides the verdict.
- If no inventory can be made at all, skip the checker and the lenses for that skill, give it the verdict not determinable, and say why in place of the findings.

## A skill from a URL

The user wants a skill checked before installing it. It needs `git`; without it, report `URL needs git: <url>` and go on with the other paths.

1. From a folder URL such as `https://github.com/<owner>/<repo>/tree/<ref>/<path>`, take the repository URL (`https://github.com/<owner>/<repo>.git`), the ref and the path. For any other form, ask the user for the repository URL and the folder.
2. Run `mktemp -d` and use the folder it prints as `<tmp>` in every command below (shell variables don't survive between commands). Clone only the skill, plus the README and plugin manifest at the root and in each folder above `<path>`, which tell what the skill targets:

   ```bash
   git clone --quiet --depth 1 --filter=blob:none --no-checkout --branch <ref> <repo-url> "<tmp>"
   git -C "<tmp>" sparse-checkout set --no-cone '/<path>/' '/README.md' '/.claude-plugin/' '/<parent>/README.md' '/<parent>/.claude-plugin/'
   git -C "<tmp>" checkout --quiet
   ```

   Then delete `<tmp>/.git`, so a skill at the repository root has only its own files in the inventory.

   Repeat the two `<parent>` patterns for each folder above `<path>` (for `plugins/notes/skills/todo`: `plugins`, `plugins/notes`, `plugins/notes/skills`).
3. Audit `<tmp>/<path>` with the origin web. In the report, write each location as `<url>/<file>:<line>` and the path as the URL, never the temp folder.
4. After the report, delete `<tmp>`.

## A path fits no listed form

- A folder the user calls a plugin, without `.claude-plugin/plugin.json` (the manifest is optional): treat it as a plugin root with no `skills` field.
- A plugin installed from a marketplace whose entry declares `skills` paths: those paths add to the plugin's own, relative to the plugin root. Audit them when the user names the marketplace or the entry.
- A plugin's `commands/*.md` are commands, not skill folders: audit one only when the user names it, as a skill whose folder holds only that file.
- Otherwise, follow the next section.

## A path resolves to no skill

- A path that does not exist: report `path not found: <path>`. A file or folder with no `SKILL.md` at, above or below it: `no skills in: <path>`. A plugin root with no skills: `no skills in plugin: <path>`. Go on with the other paths.
- In the summary table, give it a row with that text as the verdict. With a single path, reply with that text alone.

## An agent is unavailable or fails

Agents not available, or an agent returns anything other than its report block:

- Read that lens's reference completely and apply it yourself, one skill at a time. Its rules hold for you too: read each file in full with Read, and rest every finding on what you read, not on a search.
- Its report block feeds the merge (step 4); it is not your final message.
