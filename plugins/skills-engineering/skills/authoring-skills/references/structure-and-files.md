# Structure and files

How Claude reads a skill decides how to lay it out. It reads all of `SKILL.md` once, in written order, when the skill loads, and the text stays in the conversation without being re-read. It opens another file only when the text points to it and the moment calls for it. It runs a script without reading its code. And after compaction it keeps only the start of each skill it invoked, within a shared budget, so what sits late in a long body is the first to go.

## Contents

- 1. What goes in `SKILL.md` and what goes elsewhere
- 2. The order of the body
- 3. Where each supporting file goes
- 4. Pointers between files
- 5. The packaging boundary and path variables
- 6. Size budgets
- 7. Questions to ask yourself

## 1. What goes in `SKILL.md` and what goes elsewhere

- Keep in `SKILL.md` what every run needs: what the skill is for and who Claude is in it, the gotchas, the essential workflow, the critical constraints and how Claude verifies its work.
- Move to supporting files what is substantial, specialized or needed only in some runs: a long reference, a large set of examples, an API's details, the procedure for one branch of the task. A supporting file costs nothing until Claude opens it; the body costs context on every turn after it loads.
- A short example used on every run stays inline. A long or conditional one goes in its own file.
- Don't split only to make `SKILL.md` shorter. Splitting what one task always needs together makes Claude open several files to do one thing, and a fact Claude needs at a step it reaches before opening the file arrives too late.

## 2. The order of the body

- Put what the whole task depends on near the top: the purpose, how Claude starts, the constraints that hold throughout, and the gotchas, before the instructions they affect. That part survives compaction, and a rule buried deep is easy to under-weight.
- Place every rule, exception or gotcha at or before the step it governs. Claude follows steps in order and reaches a step with nothing there to signal that a later line changes it. Write "back up the database, then run the migration", never a note after the migration step.
- Keep each phase's instructions inside that phase. Instructions for a later phase, placed early, get acted on too soon; instructions placed after their phase arrive once Claude has moved on.
- Define each term, file or value at or just before its first use, close to where it's used, and cut anything introduced and never used.
- Word guidance that holds for the whole task as standing ("after every edit", "whenever you open a new file") and place it near the top. Inside one step it reads as part of that step only.
- Start the body by taking up the task the description announced, in the description's terms (see the name-and-description guide).

## 3. Where each supporting file goes

The Agent Skills specification leaves the layout free: a skill folder may hold any files and folders beside `SKILL.md`, and `scripts/`, `references/` and `assets/` are recommended conventions, not requirements. Anthropic's own examples keep guides such as a forms guide at the skill's root, beside `SKILL.md`. Choose each file's place by who reads it, when, and what for.

- Material Claude reads as guidance goes in `references/` or at the root. Resources the output is made from (a template to fill, a logo, a data file) go in `assets/`. Code Claude runs goes in `scripts/`. Reading material placed in `assets/` may be copied or filled in by another host instead of read.
- Keep files for different readers apart. When the skill briefs subagents, the files each subagent receives sit in a folder whose role is that, and a playbook only the main session follows sits elsewhere, such as the root. A reader then never opens instructions written for someone else, and each folder's role stays recognizable.
- Separate by domain or feature when the task needs one at a time: `billing.md`, `reporting.md` and `admin.md`, each pointed to at the step that needs it, instead of one file that bundles all three. Split by how files are accessed, never by size alone, and keep together what one task always needs at once.
- Name each file for what it holds (`form-validation-rules.md`, not `notes.md` or `doc2.md`), because Claude decides from the name and the pointer whether opening it is worth it.
- Write every link with the file's name exactly as it is on disk, letter for letter and case for case. A link to `Reference.md` for a file named `reference.md` works on a case-insensitive file system and fails on Linux and in most containers.

## 4. Pointers between files

- Point to every supporting file directly from `SKILL.md`, one level deep. A file reached only through another reference may be previewed instead of read whole. When a reference tells Claude to use an asset, `SKILL.md` names that asset too; the reference can name it again at the step that uses it.
- Each pointer says what the file holds and when to open it: "If the API returns a non-200 status, read `references/api-errors.md` for the error codes and retries." A path alone gives Claude nothing to decide with.
- Put the pointer at the step that uses the file, not in a list at the top that Claude has to remember.
- Leave no file that nothing points to: Claude never opens it, and it still ships.
- Write paths relative to the skill's root, with forward slashes, even for Windows users.
- Don't attach a file that only some runs need with an `@` reference: in a local Claude Code skill it is attached on every load. Use the plain path with its condition.
- A URL can cite a source or offer further reading; it must never be the only home of what the skill needs to work. Fetched pages can change or carry injected instructions, and some surfaces have no network.
- When a later step depends on what a script does or prints, say it in the text ("`check_form.py` writes each field's name and type to `fields.json`"): the script's code never enters context.
- Name another skill the way Claude invokes it, with its plugin prefix, and say when to use it and what it does for this task. For a skill that ships to others, rely only on skills inside your own plugin or a plugin it declares as a dependency.
- Name MCP tools fully qualified, as `ServerName:tool_name`, so Claude can't confuse similar tools from two servers.

## 5. The packaging boundary and path variables

- Everything the skill needs at runtime must sit inside its own folder, or, for a plugin skill, inside the plugin. Only that is installed, uploaded or synced. A path with `..`, an absolute path, or a file in the surrounding repository works on your machine and nowhere else.
- In Claude Code, reach bundled files through the substituted variables, because the shell's working directory moves: the skill-directory variable for this skill's own files, the plugin-root variable for files shared across a plugin's skills, and the plugin-data variable for state that must survive an update. The plugin-root directory changes on every update; never write state there. The two plugin variables exist only in plugin skills.
- Claude Code substitutes these variables only in `SKILL.md` and in the Bash rules of `allowed-tools`, not in a reference file Claude reads later. A command that uses one goes in `SKILL.md`, or `SKILL.md` gives the reference the resolved path.
- Outside Claude Code, script paths are relative to the skill's root, and the host resolves them. Some synced routes leave certain variables unsubstituted; check the Claude Code skills page for which.
- Test a plugin skill in its installed form, not only from a development folder: a marketplace install copies the plugin into a cache and drops symlinks that point outside it, while a development run loads in place.
- For a plugin that also targets the Claude app, check the plugins documentation for folders the app refuses before choosing where executables go.

## 6. Size budgets

- Keep the body of `SKILL.md` under about 500 lines and about 5,000 tokens. Both are recommendations, not limits a surface enforces, and both exist because the body stays in context on every turn.
- Compaction keeps only the first part of each invoked skill, within a budget shared by all of them, and can drop an early skill entirely. Check the current figures on the Claude Code skills page; design so the load-bearing part sits at the top.
- Give every supporting file over 100 lines a contents list at the top, so a partial read still shows the whole file's scope.
- A skill whose rendered text changes on each invocation (through arguments or injected commands) is appended in full every time it's re-invoked. Keep such skills short when a workflow re-invokes them often.
- Uploads and installs have hard size and file-count limits that differ by route. Check the limits for each route the skill ships through before bundling large data.

## 7. Questions to ask yourself

- Read forward once: is every rule at or before its step, every term defined before use?
- If compaction kept only the top of the body, would the skill still work?
- For each supporting file: who reads it, when, and does its place and name say so?
- Does `SKILL.md` point directly to every file, with what it holds and when to open it, and does every link match its file name exactly?
- Would the skill still work copied alone onto a machine that has never seen your repository?
