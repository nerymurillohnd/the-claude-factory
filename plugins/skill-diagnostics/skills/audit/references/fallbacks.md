# Fallbacks

Read the section for the case at hand; the main path in `SKILL.md` covers everything else.

## The inventory is incomplete

A folder could not be listed, or the listing tool stopped before the end (Glob stops at 100 results). Links that leave the skill and loops are not gaps.

- List what is missing as not inspected; step 5 of `SKILL.md` decides the verdict.
- If no inventory can be made at all, skip the lenses for that skill, give it the verdict not determinable, and say why in place of the findings.

## A skill from a URL

The user wants a skill checked before installing it. It needs `git`; without it, report `URL needs git: <url>` and go on with the other paths.

1. From a folder URL `https://github.com/<owner>/<repo>/tree/<rest>`, the repository URL is `https://github.com/<owner>/<repo>.git`, and `<rest>` is the ref followed by the path. Run `git ls-remote --heads --tags <repo-url>`: `<ref>` is the longest branch or tag name (without `refs/heads/` or `refs/tags/`) that equals `<rest>` or starts it followed by `/`, and the remainder is `<path>`, empty for a skill at the repository root. When none matches and `<rest>` starts with a 40-character commit SHA, that SHA is `<ref>`. Otherwise, or for any other URL form, ask the user for the repository URL, the ref and the folder.
2. Run `mktemp -d` and use the folder it prints as `<tmp>` in every command below (shell variables don't survive between commands). Clone only the skill, plus the README and plugin manifest at the root and in each folder above `<path>`, which tell what the skill targets:

   ```bash
   git clone --quiet --depth 1 --filter=blob:none --no-checkout <repo-url> "<tmp>"
   git -C "<tmp>" fetch --quiet --depth 1 --filter=blob:none origin <ref>
   git -C "<tmp>" sparse-checkout set --no-cone '/<path>/' '/README.md' '/.claude-plugin/' '/<parent>/README.md' '/<parent>/.claude-plugin/'
   git -C "<tmp>" checkout --quiet FETCH_HEAD
   ```

   With an empty `<path>`, skip `sparse-checkout`: the whole repository is the skill. Then delete `<tmp>/.git`, so the inventory holds only the skill's own files.

   Repeat the two `<parent>` patterns for each folder above `<path>` (for `plugins/notes/skills/todo`: `plugins`, `plugins/notes`, `plugins/notes/skills`).

   A command that fails: report `URL clone failed: <url> — <first error line>`, delete `<tmp>` and go on with the other paths.
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

The Agent tool does not exist in this session, its call returned an error, or an agent returns anything other than its report block. Quote the missing tool or the error under Coverage → Lenses:

- Read that lens's reference completely and apply it yourself, one skill at a time. Its rules hold for you too: read each file in full with Read, and rest every finding on what you read, not on a search.
- Its report block feeds the merge (step 3); it is not your final message.
