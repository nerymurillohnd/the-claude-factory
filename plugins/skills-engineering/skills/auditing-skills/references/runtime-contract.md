# Runtime contract

This file teaches you how to audit whether a skill's files resolve, package, load and are discovered on every surface it targets: its packaging boundary and archive layout, how its files link to each other, its paths and variable substitution, its plugin layout and cache, its symlinks, its discovery, precedence and sync, how subagents consume it, how its tool pre-approval and injected commands behave at runtime, how hooks, mods and permission rules act on it, and how it composes with other skills. Each section gives you the principle, why it matters, and what to do when you audit.

## Contents

- How to use this file
  - Before auditing: establish the context
  - Then, audit area by area
- 1. Supporting files and the packaging boundary
  - 1.1 Files inside the boundary
  - 1.2 Upload and archive layouts
  - 1.3 How the skill's files reach each other
  - 1.4 How the skill's files are organized
- 2. Paths and variable substitution
  - 2.1 Path variables
  - 2.2 Where substitution happens
  - 2.3 Working directory
- 3. Plugin layout, manifest and cache
  - 3.1 Layout and manifest paths
  - 3.2 Cache and in-place loading
  - 3.3 Cross-surface packaging
- 4. Symlinks
  - 4.1 Skill folders
  - 4.2 Plugins
- 5. Discovery, precedence and surfaces
  - 5.1 Claude Code locations
  - 5.2 Precedence
  - 5.3 Cloud, project and synced sessions
  - 5.4 Skills API and Managed Agents
- 6. Subagent consumption
  - 6.1 Forked skills
  - 6.2 Preloaded skills
  - 6.3 What no subagent has
  - 6.4 Agent SDK sessions
- 7. Tool pre-approval and shell execution
  - 7.1 allowed-tools at runtime
  - 7.2 Injected commands at runtime
- 8. Validator scope and blind spots
- 9. Hooks and the skill at runtime
  - 9.1 The skill's own hooks
  - 9.2 Hooks, mods and permission rules that act on the skill
- 10. Composition between skills
  - 10.1 Invoking another skill during a run
  - 10.2 Skills meant to load together
  - 10.3 Dependencies across plugins
  - 10.4 Composition the skill needs, and composition it doesn't
- Classifying findings
- Improvement opportunities
- Delivering the report

## How to use this file

Read this whole file, through its final section, "Delivering the report", before you judge anything. This complete reading, and an audit of the skill against every point in it, are a precondition of your audit: no point stays unaudited. Keep to the file's order: first establish the context, then audit area by area, then classify what you found.

Audit from the seat of a Claude that loads the skill with no prior context, on each surface the skill targets, and has to use it. Follow every file pointer, path, variable and command as that Claude would meet it there, and ask whether it would resolve, load and run. A skill can be valid but undiscoverable, discoverable but unable to run, working on one surface but broken on another, or apparently working while it relies on files or permissions it never declared. Judge these dimensions separately.

Keep these kinds of evidence apart, and say which one each finding rests on:

- **Requirement:** a constraint a specification, schema, validator or target runtime imposes.
- **Documented behavior:** what a named product or runtime does. It may be specific to a version or surface, so it isn't automatically a portable requirement.
- **Recommendation:** guidance that improves reliability, usability, maintenance or safety. Never report it as a requirement.
- **Example:** an illustration, not proof that every runtime accepts the pattern.
- **Inference:** a conclusion the evidence supports but doesn't guarantee. Label it and give the reasoning.
- **Unknown:** behavior the evidence doesn't establish. Never fill the gap with intuition.

When two sources disagree, first check whether they address different products, versions, install routes, session types or artifact types. If they do, keep the distinction and make the judgment conditional on the actual target. If they truly conflict for the same target, report the conflict and use the narrowest safe conclusion.

The prompt you receive states what the orchestrating model's scripts already verified, such as parsed frontmatter, counts, which referenced files exist, the symlinks in the skill and where they resolve, archive listings, and the structural validator's output. Take those results as verified and judge what they mean for the skill; never measure or run anything yourself. When a mechanical result a point needs is missing, record it under Checklist exceptions as blocked and judge everything else. Settle every point you can by reading the files: that reading is the audit, never an optional step, and a point the files could have settled but you left unverified is a failure of the audit. For anything this file asks about that neither the prompt nor the files can establish, report it as unverified, say why, and name the runtime check that would settle it. Never present an unverified point as passing.

### Before auditing: establish the context

Before you judge the skill's type, read `skill-types-and-frontmatter.md`, in this skill's `references/` folder, whole: it lists, from the official sources, every frontmatter field, name rule, argument, body feature and folder layout by type of skill, and a row read alone can hide a condition another section states.

A judgment that's correct for one route can be wrong for another, so settle these four points before you apply any rule. They decide what "correct" means for the skill in front of you.

1. **Where the skill lives.** Identify whether it is an enterprise skill (managed settings directory), a personal skill (`~/.claude/skills/`), a project skill (`.claude/skills/`, including nested ones), a skill from an added directory (`--add-dir`), a skill in a plugin's `skills/` directory, a single `SKILL.md` at a plugin's root, a skill folder that is also a skills-directory plugin, a skill enabled on a claude.ai account and synced, a Skills API upload, or a Managed Agents skill. Each route has its own discovery, packaging and substitution rules, so don't judge one by another's.
2. **Which surfaces will load it.** Record the actual deployment targets, not product names:
   - Claude Code in a local session: terminal, IDE, or desktop app.
   - Claude Code in a cloud session: Claude Code on the web and cloud scheduled tasks, plus project cloud threads, which load less than other cloud sessions (§5.3).
   - The Claude app. On an account moved to the unified experience, chat and Cowork are one conversation and tasks run in the cloud with no local option. On an account not yet moved, chat and Cowork are separate, and Cowork can also run locally in the desktop app. Cloud Cowork sessions reach local files, local MCP servers, browser use and computer use only while the desktop app is open.
   - The Skills API and Managed Agents.
   If the prompt names no target, infer it from the files and state the assumption in the report. Never audit against Claude Code alone and present the result as valid everywhere. For a skill that targets several surfaces, judge each one.
3. **How the skill gets invoked.** Determine whether it runs directly in a session, is forced into a subagent with `context: fork`, is preloaded into a custom subagent's `skills` list (§6), runs in an Agent SDK session (§6.4), or is invoked by another skill during that skill's run (§10). Note which paths reach it: the user typing its name, Claude calling the `Skill` tool, or both, because hooks and rules act on each path differently (§9.2).
4. **What the skill is actually trying to do**, from its own description and body. Use this to decide which areas apply. A skill with no supporting files has nothing to check under §1.1. A skill that isn't in a plugin has nothing to check under §3. Apply each area only where the skill's purpose and targets make it relevant, and never flag an absence the skill never had a reason to fill.

### Then, audit area by area

Audit what the skill has, and also what it should have. Work through the areas in order, because later judgments depend on earlier ones: a script path can't be judged valid until its base directory and packaging boundary are known. In each area, start from the skill's targets and purpose, ask what its files, paths and packaging need to work on every target, compare that with what the skill contains, and give every item exactly one of these outcomes:

- **Present and optimal.** It resolves and loads on every target, the way this file describes. Record no finding.
- **Present but wrong.** It breaks a rule of this file on at least one target, or it shouldn't be in the skill at all. Record it as a defect, classify it (see "Classifying findings"), and say whether it must be deleted, rewritten or moved.
- **Present, right, but improvable.** It works, but a sturdier pattern from this file would serve the skill's targets better. Record it as an improvement opportunity, with the adjustment it needs.
- **Absent, and the skill's targets need it.** Record it as an improvement opportunity: say exactly where it belongs, what it should contain, and cite the point of this file it rests on.
- **Absent, and the skill's targets don't need it.** Record no finding.

Work only from what is actually written in the skill and what the prompt reports, never from what it's likely to contain. If you have no line to point to, you have no finding.

---

## 1. Supporting files and the packaging boundary

### 1.1 Files inside the boundary

Only `SKILL.md` is required. Everything else the skill needs at runtime must sit inside the skill's own directory, or inside the plugin root for a plugin skill, because that directory is the only thing that is installed, uploaded, synced or copied. A file that works from the author's repository can be missing on every other machine. `references/`, `scripts/` and `assets/` are conventions; a root-level `REFERENCE.md` or a singular `reference/` folder is a layout difference, not a defect.

Recognize the difference:

**Breaks once installed:** a plugin skill that reads `../shared/glossary.md`.

**Travels with the skill:** the same file moved to `<plugin root>/shared/glossary.md` and read through the plugin-root variable.

When you audit:

- Flag every file, script or directory the skill needs that sits outside its boundary: a parent-relative path, an absolute machine path, or a file in the surrounding repository.
- Flag every MCP server, environment variable, network call or external service the skill relies on without declaring it, and ask whether the skill still works detached from its development repository.
- Take which referenced files exist from the prompt, or from your own reading of the skill. Report a file you couldn't read as missing, with the error.

### 1.2 Upload and archive layouts

Each distribution route expects its own layout, so one archive doesn't fit every surface:

- **claude.ai upload:** the ZIP holds the skill folder as its root entry, and the folder name matches the skill's name. Files placed directly at the ZIP root aren't recognized.
- **Plugin archive for one session:** a `--plugin-url` archive or a `--plugin-dir` `.zip` is extracted into a session temp directory first.
- **Skills API and Managed Agents:** skills arrive through their own upload or repository routes (§5.4).

When you audit:

- Flag packaging instructions in the skill, or an archive listing the prompt reports, that don't match the route the skill states.
- Flag one archive layout reused across surfaces without a check against each target's layout.
- Report the layout of a Skills API upload as unverified: no official source used here gives it.

### 1.3 How the skill's files reach each other

Every file Claude has to open is linked directly from `SKILL.md`, one level deep. Anthropic's best practices give the reason: "Claude might partially read files when they're referenced from other referenced files", previewing them with a command such as `head -100` instead of reading them whole, and their checklist lists "File references are one level deep". The Agent Skills specification says the same, "Avoid deeply nested reference chains", and asks for paths written "relative to the skill root". This holds for an asset as much as for a reference: when a reference tells Claude to use an asset, `SKILL.md` links that asset too. The reference may link the same asset again at the step that uses it, so both ends point to the file; that second link reinforces the first and never replaces it (recommendation; no official source covers it).

Incorrect cases, each with what goes wrong:

- **A chain.** `SKILL.md` links `references/advanced.md`, which links `references/details.md`, and nothing else links `details.md`. Claude may preview `details.md` instead of reading it.
- **An asset reached only through a reference.** `references/reporting.md` says "Fill in `assets/report.md`", and `SKILL.md` never names `assets/report.md`. Claude learns the asset exists only if it reads that reference whole.
- **An orphan.** A file in `references/`, `assets/` or `scripts/` that no file links. Claude never opens it, and its content is dead weight in the package.
- **A path written from the wrong base.** `references/reporting.md` links `../assets/report.md`, or `SKILL.md` links `report.md` for a file in `assets/`. The specification asks for paths from the skill root, such as `assets/report.md`.
- **A link to a missing file.** A path that names no file in the skill, often after a rename.
- **Content that lives outside the skill.** An essential rule kept only behind a URL, or a step that reads a file outside the skill's boundary (§1.1).

Links that leave the skill need their own judgment. A URL is fetched at run time, and Anthropic's Agent Skills overview warns: "Skills that fetch data from external URLs pose particular risk, as fetched content might contain malicious instructions. Even trustworthy Skills can be compromised if their external dependencies change over time." Skills on the Claude API run with no network access, so a fetch fails there. A URL is sound as a source to cite or an optional place to read further; it is unsound as the only home of what the skill needs to work.

Recognize the difference:

**Nested:** `SKILL.md` links `references/reporting.md`, and only that reference names `assets/report.md`.

**One level deep, both ends closed:** `SKILL.md` lists `references/reporting.md` ("how to write the report; read before step 6") and `assets/report.md` ("the report template; fill it in at step 6"), and `references/reporting.md` links `assets/report.md` again where it uses it.

When you audit:

- Map every link among the skill's files from the prompt's listing and your own reading: which file links which, and how deep each file sits from `SKILL.md`.
- Flag each file Claude must open that `SKILL.md` doesn't link directly, naming the chain that reaches it, and recommend the direct link in `SKILL.md`.
- Flag each bundled file nothing links, and ask whether it should be linked or deleted.
- Flag each path that isn't written from the skill root, or that names no file in the skill.
- Flag each URL that carries something the skill needs to work, and recommend moving that content into a reference, keeping the URL as a cited source. On a skill that targets the Claude API, flag every step that needs the network.
- Recommend, where a reference uses an asset that `SKILL.md` already links, the second link at that step, so both ends point to the file.

### 1.4 How the skill's files are organized

The layout is free. The Agent Skills specification says "A skill directory may contain any files and directories beyond the required `SKILL.md`. The conventions below are recommendations for organizing common types of content", and describes `scripts/` as executable code, `references/` as "additional documentation that agents can read when needed" (with `REFERENCE.md`, `FORMS.md` and domain files as its examples) and `assets/` as static resources. Anthropic's best practices keep `FORMS.md` and `reference.md` at the skill root next to `SKILL.md`. A layout is never a defect because it departs from these names (§1.1).

What the layout must do is let Claude find the right file and tell from where a file sits what it is for. Anthropic's best practices say "Claude navigates your skill directory like a filesystem" and "Organize for discovery: Structure directories by domain or feature", with `reference/finance.md` as good and `docs/file1.md` as bad. Inside one skill, a folder's role is a promise: once the skill gives a folder one role, such as one subagent's reference per area, a file with another role or another reader placed there is taken for that role, by Claude and by whoever maintains the skill (inference). A skill whose files have different readers, such as the main session and the subagents it briefs, keeps each reader's files apart (recommendation, inferred from the organize-by-domain guidance).

A link also has to match the file name letter for letter. On a case-sensitive file system, such as Linux's, `reference.md` doesn't open `REFERENCE.md`; on a case-insensitive one, such as macOS's default, it does, so the mismatch passes on the author's machine and breaks elsewhere (general file-system behavior; no Claude source states it).

Recognize the difference:

**Misleading:** a skill whose `references/` holds one subagent reference per area also keeps there the main session's run book, which no subagent reads.

**Clear:** the run book sits at the skill root next to `SKILL.md`, in capitals like `FORMS.md`, and `references/` holds only the subagent references.

When you audit:

- Never flag a layout for departing from `scripts/`, `references/` and `assets/`, or for keeping guides at the root, and leave where an example sits out of this judgment: that depends on how Claude uses the example, not on the layout.
- Map each folder's role from the files it holds and from how `SKILL.md` describes them. Flag each file whose role or reader differs from its folder's role everywhere else in the skill, naming who reads it, and recommend the folder or root location that matches its role.
- Flag a folder that mixes files for different readers when the skill tells each reader to read only its own, and recommend one place per reader.
- Flag a folder that mixes several domains when the task needs one domain at a time, and recommend one file or subfolder per domain.
- Compare each link's spelling, letter case included, with the file listing in the prompt or your reading of the skill. Flag every mismatch as a link to a missing file on case-sensitive file systems, even when it opens on the author's machine.

---

## 2. Paths and variable substitution

### 2.1 Path variables

Claude Code substitutes these placeholders in skill content:

- `${CLAUDE_SKILL_DIR}`: the directory holding the skill's `SKILL.md`. In a plugin, it is the skill's subdirectory, not the plugin root.
- `${CLAUDE_PROJECT_DIR}`: the project root.
- `${CLAUDE_PLUGIN_ROOT}`: the plugin's installed version directory. Substituted only in plugin skills. It changes when the plugin updates.
- `${CLAUDE_PLUGIN_DATA}`: the plugin's persistent data directory, `~/.claude/plugins/data/<id>/`, created on first reference and kept across updates. Substituted only in plugin skills. By default it is deleted when the plugin is uninstalled from the last place it's installed.
- `${CLAUDE_SESSION_ID}` and `${CLAUDE_EFFORT}`: the session ID and the current effort level.
- `${user_config.KEY}`: a plugin's saved option, substituted in skill and agent content only for non-sensitive values. A sensitive value there becomes a placeholder.

When you audit:

- Flag the plugin-root or plugin-data variable in a skill that isn't in a plugin: it is never substituted there.
- Flag state written under the plugin root, which moves on every update, and recommend the plugin-data directory.
- Flag a sensitive `user_config` value the skill expects to read in its content: it arrives as a placeholder.

### 2.2 Where substitution happens

- Claude Code substitutes the skill-directory and project-directory variables in the skill's Markdown and in Bash rules of `allowed-tools`. In a plugin skill it substitutes the plugin-root and plugin-data variables in the same two places. In a plugin's command and agent content, the variables resolve anywhere in the Markdown body.
- Substitution happens after arguments are inserted. A backslash doesn't stop it.
- In a terminal or VS Code session, a skill synced from claude.ai doesn't get the project-directory or session-ID variables substituted; they reach Claude as literal text.
- In claude.ai chat and through the API, Claude Code-only body features don't function.

Judge whether each variable exists and resolves on each target surface, and what the synced routes of §5.3 drop.

When you audit:

- For each variable the skill uses, name the targets where it resolves and the targets where it reaches Claude as literal text, and flag every target where the skill depends on it resolving.
- Flag reliance on the skill-directory variable in a synced skill on a local session, or inside a skill's frontmatter hooks, as unverified: no official source establishes either case.

### 2.3 Working directory

Claude Code runs commands in the session shell's current working directory, which moves with `cd`, so a bundled file is reached only through a substituted path or a target's documented equivalent.

When you audit:

- Flag a fixed installation path for a plugin resource: the cache path changes with each version.
- For a target that doesn't substitute these variables, recommend that target's documented equivalent rather than the Claude Code form.

---

## 3. Plugin layout, manifest and cache

### 3.1 Layout and manifest paths

- Plugin skills load from `skills/<name>/SKILL.md` at the plugin root. A `skills/` directory inside `.claude-plugin/` isn't scanned, and a manifest `skills` entry that points at a file loads nothing.
- With no `skills/` directory and no `skills` key, a `SKILL.md` at the plugin root loads as one skill. Without `name` in its frontmatter, a marketplace install names it after its cache directory rather than the plugin.
- Every component path in the manifest is relative to the plugin root and starts with `./`; `skills` also accepts `.`. A path must resolve inside the plugin root and exist, or that component doesn't load. A path that leaves the plugin root, as written with `..` or through a symlink, is rejected, except links between plugins in one marketplace (§4.2).
- Claude Code doesn't load a `CLAUDE.md` at the plugin root; a plugin's instructions have to be skills.
- The manifest `skills` key adds to the default `skills/` scan. A marketplace entry whose source is the marketplace root and that lists `skills` subdirectories loads only those, and the default `skills/` isn't scanned.
- With a `plugin.json`, `strict: true` (the default) appends the marketplace entry's component fields to the manifest, and `strict: false` turns any component field in the entry into a conflict that stops the plugin from loading.
- `engines["claude-code"]` in `plugin.json` keeps the plugin from installing, updating or loading outside its stated version range.

When you audit:

- Take path, containment and existence errors from the validator output in the prompt, and judge which skill each one removes on which target.
- Flag a plugin-root `SKILL.md` that relies on its folder for its command name.
- Flag a marketplace entry and a manifest that declare skills in a way that drops some of them or conflicts under the entry's `strict` value.
- Flag an `engines` range that excludes a Claude Code version the skill's own text says it supports.
- Flag instructions the plugin keeps in a root `CLAUDE.md`: they never load. Recommend moving them into a skill.

### 3.2 Cache and in-place loading

Where a plugin loads from depends on how it arrived:

- `--plugin-dir` plugins and skills-directory plugins load in place and are never copied.
- Relative-path plugins in a marketplace added from a local path load in place, and their hooks and MCP and LSP servers get a plugin root pointing at the source directory.
- `command`-source plugins in link mode load in place through links in the cache entry.
- Every other marketplace plugin is copied into `cache/<marketplace>/<plugin>/<version>/` and loads from that copy. Files outside the plugin directory aren't copied.

So a path above the plugin root can work during in-place development and fail after a marketplace install.

When you audit:

- Judge every plugin path in its installed, cached form, not in the author's working copy.
- Flag in-place success, such as a working `--plugin-dir` run, offered as proof that a marketplace install works.

### 3.3 Cross-surface packaging

- A top-level `bin/` directory is on the Bash tool's `PATH` while the plugin is enabled in Claude Code, but claude.ai and Cowork don't install a plugin that has one, and claude.ai rejects it when syncing a marketplace.
- Plugins declared in a repository's `.claude/settings.json`, and plugins enabled only in user settings, don't load in cloud sessions.
- A plugin turned on for a claude.ai account, including one the organization turns on, loads as `<name>@synced`: Cowork sessions download it at session start, and terminal sessions signed in with the account sync it once at startup (v2.1.273 or later) and load all its components with marketplace-plugin trust. Which components Cowork loads is set by the component support table on claude.com.

When you audit:

- Flag a top-level `bin/` in a plugin that targets the Claude app, and recommend another folder, such as `scripts/`, referenced through the plugin-root variable.
- Flag a plugin that reaches cloud sessions only through repository or user settings, and recommend turning it on for the claude.ai account.

---

## 4. Symlinks

### 4.1 Skill folders

A skill folder in the enterprise, personal or project location can be a symlink to a directory elsewhere. Claude Code reads `SKILL.md` from the target and loads the skill once, even when several locations point at the same target. No official source establishes symlink behavior for claude.ai or Skills API uploads, for Managed Agents repository discovery, or for single symlinked files inside a skill folder.

When you audit:

- Take the skill's symlinks and their targets from the prompt. Where the prompt doesn't report them, report this area as unverified.
- Flag a skill that depends on a symlink on a target where symlink behavior is undocumented, as unverified, with the install test that would settle it.

### 4.2 Plugins

When Claude Code copies a plugin into its cache, it handles each symlink by where its target resolves:

- Inside the plugin's own directory: kept as a relative symlink.
- Elsewhere in the same marketplace: dereferenced, and the target's content copied in its place.
- Outside the marketplace: skipped for security.
- For plugins installed from a local path, or from a `command` source in the default `copy` mode, only symlinks that resolve inside the plugin are kept.

When you audit:

- Flag every plugin symlink whose target is outside the marketplace, or, for local-path and copy-mode sources, outside the plugin: the target won't exist after install.

---

## 5. Discovery, precedence and surfaces

### 5.1 Claude Code locations

- **Enterprise:** `.claude/skills/<name>/SKILL.md` in the managed settings directory, for every user on machines where the organization deploys it.
- **Personal:** `~/.claude/skills/<name>/SKILL.md`, for every project on that machine, but not in Cowork or cloud sessions.
- **Project:** `.claude/skills/<name>/SKILL.md`, in the starting directory and every parent up to the repository root. In a linked worktree, the search stops at the worktree root; when the worktree has no root `.claude/skills`, Claude Code loads the main checkout's project skills.
- **Nested:** `<subdir>/.claude/skills/` loads at startup in a session started in or below `<subdir>`. A session started above it loads it the first time Claude reads or edits a file there. With the Bash sandbox on, it loads only if the session starts or moves there. Nested folders inside `~/.claude/plugins`, and in `--plugin-dir` plugins below the starting folder, don't load.
- **Added directory:** the `.claude/skills/` of a directory passed with `--add-dir` or `/add-dir`. `permissions.additionalDirectories` grants file access only and loads no skills.
- **Plugin:** `<plugin>/skills/<name>/SKILL.md`, wherever the plugin is enabled, as `/plugin-name:skill-name`.
- **claude.ai account:** skills enabled on the account, in Cowork sessions, cloud sessions, and terminal sessions signed in with that account.
- **Skills-directory plugin:** a skill folder with `.claude-plugin/plugin.json` loads as `<name>@skills-dir`, with its own agents, hooks and MCP servers. It is read only from the `.claude/skills/` of the session's primary working directory, with no parent search. In a project's `.claude/skills/` it needs the workspace trust dialog accepted first, and administrators can block it.

Claude Code watches the skill directories that existed at session start. A top-level skills directory created during the session needs `/reload-skills`, and a skill folder that is also a plugin needs `/reload-plugins` after changes to its `.mcp.json`, `agents/`, `output-styles/` or `hooks/`.

When you audit:

- Flag a skill whose stated audience can't reach its location, such as a personal skill meant for cloud sessions.
- Flag a nested skill that the skill's own workflow needs before Claude has touched files in its subdirectory.
- Flag reliance on `permissions.additionalDirectories` to load skills.
- Flag a workflow that creates a top-level skills directory, or changes a skill-folder plugin's components, mid-session without the reload it needs.
- Flag a skills-directory plugin the skill expects to load from a parent of the starting directory.

### 5.2 Precedence

- Enterprise wins over personal, and personal over project, for the same name.
- A skill replaces a bundled skill of the same name, and, in a local terminal session, a built-in command of the same name, but not their aliases.
- A skill wins over a same-named file in `.claude/commands/`.
- Plugin skills are namespaced, so they load alongside same-named skills elsewhere.
- An added directory's same-named skill runs under a prefixed name.
- A synced skill whose short name another command uses runs only under its full name, `/anthropic-skills:<name>`.
- This order is documented for Claude Code. Don't assume it holds in another Agent Skills client.

When you audit:

- Flag a name collision visible in the audited files or reported in the prompt that makes a different skill run on a target, and recommend a unique name.

### 5.3 Cloud, project and synced sessions

- Cowork and cloud sessions, including cloud scheduled tasks, don't read `~/.claude/skills/`. They load the skills enabled on the claude.ai account, synced at session start. Desktop scheduled tasks run locally and do load `~/.claude/skills/`.
- Project cloud threads load each repository's root `CLAUDE.md`, `.claude/CLAUDE.md` and `.claude/rules/`, but not its `.claude/skills/`, agents, commands, `.mcp.json`, the plugins its settings enable, its permission rules, hooks or `env`. A skill reaches a project thread through the claude.ai account.
- Other cloud sessions can load the repository's `.claude/skills/`.
- Some self-hosted sessions don't load account skills.
- In a terminal, Claude Code syncs account skills into `~/.claude/skills/synced/` only in sessions signed in with `/login` to a claude.ai account that fetch feature flags. It doesn't sync with an API key or a token supplied by environment or helper, on providers such as Amazon Bedrock, in bare or safe mode, with a `--setting-sources` list that leaves out `user`, with `syncClaudeAiSkills` set to `false`, or when managed settings lock skills to plugins. Edits under `synced/` aren't saved back to the account.
- A synced skill's body keeps local behavior in a cloud session. In a desktop Cowork session, every `!` command line becomes the `disableSkillShellExecution` placeholder. In a terminal or VS Code session, `!` commands don't run and `@` references aren't attached (variables: §2.2).
- Custom skills don't sync between claude.ai and the API; each surface needs its own upload.

Recognize the difference:

**Collapses distinct sessions:** "Plugin agents and hooks never work in chat."

**Conditional on the session:** "Establish the session type and how the plugin reached it, then check the component in that session."

When you audit:

- For each target, name the route by which the skill reaches it, and flag every target the skill has no route to.
- Flag a skill that needs `!` commands or `@` attachments on a synced terminal or VS Code route, or `!` commands in a desktop Cowork session.
- Flag any blanket claim, in the skill or its instructions, that a component works or fails on "chat" without naming the session type and account state.

### 5.4 Skills API and Managed Agents

- API skills run in a sandboxed code-execution container with no network access and no runtime package installation; only preinstalled packages are available. Claude and Claude Code, by contrast, can install packages from PyPI and npm when loading skills. Until an API skill triggers, only its name and description are in context.
- Managed Agents attach skills through the agent's `skills` array, or discover them in a GitHub repository mounted on the session, by default at `/workspace/<repo-name>`. Discovery finds exactly `.claude/skills/<skill-name>/SKILL.md`, one level deep at the repository root, and relies on the agent's read tool. A same-named repository skill and attached skill are both available, each announced with its own path.

When you audit:

- Flag a skill targeting the API that installs packages or calls the network at runtime.
- Flag a Managed Agents repository skill placed anywhere other than `.claude/skills/<skill-name>/SKILL.md` at the repository root, or used by an agent with its read tool disabled.

---

## 6. Subagent consumption

Judge the mechanics that decide whether the subagent gets the skill at all, with which tools, and what it can do with them.

### 6.1 Forked skills

With `context: fork`, Claude Code starts a new subagent of the `agent` type and gives it the skill content as its prompt. Despite the name, it isn't a fork of the conversation and doesn't see the history. The `agent` field "determines the execution environment (model, tools, and permissions)": a custom agent from `.claude/agents/` brings its own tool list, and the built-in Explore and Plan agents are read-only, with Write and Edit denied. It runs in the background by default, with the background tool set: every MCP tool, but of the built-in tools only `Read`, `Grep`, `Glob`, `LSP`, `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`, `EnterWorktree`, `ExitWorktree`, `Monitor`, `TaskStop`, `SendMessage` and `Artifact`; `background: false` makes it wait and keeps the full tool set. Claude Code also waits, whatever `background` says, in `-p` runs and the Agent SDK, with `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` set to `1`, when an earlier invocation of the same skill is still running, and when a session-scoped scheduled task fires the skill; an agent in a dynamic workflow that invokes a forked skill waits for and receives its result from v2.1.295, and before that the result went to the main conversation. A forked skill that runs in the background applies its edits outside the session's checkpoints, so `/rewind` doesn't restore the files it changed. The built-in Explore and Plan agents start without `CLAUDE.md`.

When you audit:

- Flag a forked skill whose steps need a tool outside the background set while it runs in the background.
- Flag a forked skill whose steps write or edit files while it names Explore or Plan as its agent: both deny Write and Edit, so those steps fail.
- Flag a forked skill that names a custom agent whose `tools` list, or `disallowedTools`, removes a tool the skill's steps need. Take the agent's lists from the prompt or read its file; where neither is available, report the point as unverified.
- Flag a forked skill that relies on `CLAUDE.md` while it names Explore or Plan as its agent.
- Flag `context: fork` on a skill that holds guidelines but no task: the subagent gets no actionable prompt.
- Flag a background forked skill that edits files while the skill, or its documentation, tells the user `/rewind` can undo the run, and recommend the line that tells the user to revert those edits with git.

### 6.2 Preloaded skills

A custom subagent's `skills` field injects the full content of the listed skills at startup. In that subagent the system prompt is the subagent's own body and the task is Claude's delegation message, so a preloaded skill arrives as reference beside the task, never as the task itself. The field controls what is preloaded, not what the subagent can invoke: a subagent with the `Skill` tool can still invoke other skills. Listing `Skill` in the subagent's `tools` preloads nothing: the docs say to use the `skills` field "rather than listing `Skill` here". Built-in agents don't preload skills. A skill with `disable-model-invocation: true` can't be preloaded, and a listed skill that is missing or disabled is skipped with only a debug-log warning. Plugin subagents ignore `hooks`, `mcpServers`, `permissionMode` and `initialPrompt`. No official source says whether a plugin agent's `skills` entries take bare or namespaced names, and no source says how a preloaded skill's `$ARGUMENTS` and other invocation placeholders render, since no invocation passes arguments to it.

When you audit:

- Flag a skill meant for preloading that a built-in agent is expected to preload, or that sets `disable-model-invocation: true`.
- Flag a preloaded skill that may be missing or disabled on a target, such as one outside the subagent's plugin and its declared dependencies.
- Flag a subagent whose explicit `tools` list leaves out `Skill` while its instructions require invoking skills.
- Flag a subagent that lists `Skill` in `tools` as its way of preloading a skill, and recommend the `skills` entry instead.
- Flag a skill written to be preloaded whose body depends on `$ARGUMENTS`, a positional argument or a named argument, as unverified, with the load test that would settle how the placeholder renders.
- Flag a plugin agent that relies on `hooks`, `mcpServers`, `permissionMode` or `initialPrompt`.
- Flag a plugin agent's `skills` entry for a plugin skill as unverified, with the load test that would settle it.

### 6.3 What no subagent has

Some tools never reach a subagent, whatever its `tools` list says: `AskUserQuestion`, `EndConversation`, `EnterPlanMode`, `ScheduleWakeup`, `WaitForMcpServers` and `Workflow`, `ExitPlanMode` unless the subagent's `permissionMode` is `plan`, and `Agent` once the subagent sits at the depth limit, by default three layers below the main conversation. Only a conversation fork, a subagent that copies the conversation, skips this filter. A forked or preloaded skill therefore can't ask the user a structured question, enter or leave plan mode, schedule its own wake-up or start a workflow. A background subagent surfaces each permission prompt in the main session, and an answer that lasts beyond one tool call, such as a grant for the rest of the session, applies to the whole session, the main conversation included. Only the subagent's final message returns to the parent, which may summarize it.

Recognize the difference:

**Fails in a forked skill:** "Use AskUserQuestion to ask which environment to deploy to."

**Works in a forked skill:** "Take the environment from `$ARGUMENTS`. If it is missing, stop and return a message that names the missing argument."

When you audit:

- Flag every step of a forked skill, or of a skill meant to be preloaded, that needs one of the tools above, and recommend the replacement: input taken from the arguments or the delegation prompt, or a final message that tells the parent what it must ask.
- Flag a skill that runs in a subagent and expects to spawn further subagents while it may already sit at the depth limit, as unverified unless the prompt reports the nesting it runs under.
- Flag a forked or preloaded skill whose output the parent must present verbatim while nothing tells the parent so, and recommend the line, in the skill or the delegating instruction, that asks the parent to keep the subagent's report as written.

### 6.4 Agent SDK sessions

The Agent SDK discovers skills only through the filesystem setting sources: with default options it loads the user and project sources, and with an explicit `settingSources` (`setting_sources` in Python) that leaves both out it loads no skills; the `plugins` option loads skills from a given path instead. The `skills` option decides which discovered skills Claude may invoke: omitted, every discovered skill; `"all"`, every one; a list, only those, named by the skill's directory name or, for a plugin skill, `plugin:skill`; `[]`, none. Claude doesn't see an unlisted skill, and the Skill tool rejects it with `Skill <name> is not in this session's skills allowlist`, while `/<name>` in a prompt still runs any user-invocable skill. With an explicit `tools` list, `Skill` must be in it, or Claude can't invoke skills. A subagent defined in the SDK's `agents` option preloads through `AgentDefinition.skills`, and unlisted skills stay invocable through the Skill tool.

When you audit:

- Flag a skill, or its documentation, meant for SDK sessions that tells the integrator to set `settingSources` without the source the skill lives in, or to pass an explicit `tools` list without `Skill`.
- Flag an SDK `skills` list, in the skill's documentation or example code, that names a plugin skill without its `plugin:` prefix, or that leaves out a skill the audited skill invokes.
- Recommend, for a skill whose documentation targets the SDK, the exact options that load and allow it, for example: `settingSources: ["project"]`, `skills: ["my-plugin:review"]`, and `"Skill"` in `tools` when `tools` is set.

---

## 7. Tool pre-approval and shell execution

### 7.1 allowed-tools at runtime

`allowed-tools` grants the listed tools during the turn that invokes the skill, and the grant clears with the next user message. It doesn't restrict which tools exist, and deny and ask rules still win. A rule matches the whole command line, so the skill body and the rule must name the same path through the same variable. A project skill's grant applies even in a `-p` run in an untrusted folder. `allowManagedPermissionRulesOnly` makes Claude Code ignore `allowed-tools` in project and personal skills. When managed settings list `hooks` in `strictPluginOnlyCustomization`, a personal or project skill that declares hooks loses its pre-approval in the main conversation, and keeps it when it runs through `context: fork`. Scheduled tasks and `/loop` ask before running a skill that declares `allowed-tools` or hooks, unless `Skill(name)` is in `permissions.allow`.

When you audit:

- Flag a bundled-script rule whose path differs from the path the body tells Claude to run: the command prompts or aborts.
- Flag `allowed-tools` treated as a tool restriction, or as a grant that lasts beyond the invoking turn.
- Flag a broad grant, such as `Bash` alone or a wildcard before the path, where an exact rule would do.
- Flag a skill meant to run unattended, on a schedule or under managed rules, that depends on a grant those conditions remove.

### 7.2 Injected commands at runtime

Injected commands never prompt while the skill renders. Each one is checked against the permission rules first: a deny match aborts the invocation, and outside auto mode any result other than allow aborts it unless `allowed-tools` pre-approves the command. In a folder that looks like a bare repository, Claude Code ignores `allowed-tools` for a Bash command that contains `git`. In auto mode an unapproved command doesn't abort; the skill loads and tells Claude to run it, except in a forked skill that sets `agent`.

When you audit:

- Flag an injected command no rule allows on a target that runs outside auto mode: the skill never loads.
- Flag an injected `git` command in a skill meant for bare-repository worktrees or similar checkouts.

---

## 8. Validator scope and blind spots

`claude plugin validate` checks structure, not runtime behavior. Run on a directory, it validates the marketplace or plugin manifest, or, without one, the component files in a directory named `skills`, `agents` or `commands`, or under `.claude`. It doesn't follow symlinks: a linked `skills`, `agents` or `commands` directory is warned about and not read, a linked entry inside one is skipped with a count, and a named directory that is itself a symlink errors and checks nothing. It doesn't check a `SKILL.md` at the plugin root, and from a marketplace directory it doesn't open the component files of plugins listed from other directories. A passing run therefore proves nothing about discovery, permissions, execution, sync or the cached install.

When you audit:

- Read the validator output in the prompt for what it covered, and flag each blind spot the skill falls into (a symlinked folder, a plugin-root `SKILL.md`, a plugin listed from another directory) as not validated.
- Flag a validator pass offered as proof that the skill loads or runs on a target.

---

## 9. Hooks and the skill at runtime

Judge whether the hooks the skill declares run when and where its task needs them, and whether the hooks, mods and rules around the skill reach it on every path it is invoked by.

### 9.1 The skill's own hooks

A skill's frontmatter hooks register when the user or Claude invokes the skill, and Claude Code keeps running them for the rest of the session; until the first invocation, `/hooks` doesn't list them. They can therefore act on nothing that happened before that invocation: a hook on an event that already fired, such as this session's `SessionStart`, never runs for it (inference from the registration point). Claude Code v2.1.299 changed a skill's own `UserPromptSubmit` hook to first run on the prompt after the one that invokes the skill. With `once: true`, a run that fails, blocks with exit code 2 or times out leaves the hook in place, so it runs again on the next matching event. A project skill's hooks register even in a `-p` run in a folder that was never trusted. Invoking a skill that declares hooks through the Skill tool can prompt for permission.

A hook command runs in the current directory with Claude Code's environment, and that directory moves with `cd`. The documented placeholders for a hook's script path are `${CLAUDE_PROJECT_DIR}`, the project root where the session started, and, for plugin scripts, `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}`. Claude Code rewrites these three placeholders in a PowerShell shell-form command "whether the hook is defined in `settings.json`, a plugin, or a skill", which implies it expands them in a skill's hooks (inference). The documented skill example writes `'"${CLAUDE_PROJECT_DIR}"/scripts/security-check.sh'`, a script in the user's project, not in the skill.

Several conditions keep a skill's hooks from running at all:

- Under `strictPluginOnlyCustomization` locking hooks, only a plugin skill, a bundled skill or a skill in the managed settings directory keeps its frontmatter hooks, and a lock on any surface also stops skills-directory plugins from loading.
- `allowManagedHooksOnly` and `disableAllHooks` name settings, plugin and agent-frontmatter hooks among what they block, but no official source says what either does to a skill's frontmatter hooks.
- In claude.ai chat a plugin's hooks are ignored; no official source says whether Cowork runs a plugin skill's frontmatter hooks.
- Plugin skill hooks defined in frontmatter were silently ignored before v2.1.94.

Subagent frontmatter hooks run only while the subagent runs, and Claude Code converts their `Stop` hook to `SubagentStop`. The docs state only the session lifetime for skill hooks: no official source says where a forked skill's hooks register, whether they end with the fork, or whether a `Stop` hook there becomes `SubagentStop`, and none says the same for a skill a subagent invokes through the Skill tool. Under the hooks lock, a personal or project skill that runs through `context: fork` keeps its `allowed-tools` pre-approval, which it loses in the main conversation.

Recognize the difference:

**Doesn't reach the script:** a plugin skill whose hook runs `./scripts/check.sh`, or `"${CLAUDE_PROJECT_DIR}"/scripts/check.sh`, while `check.sh` ships in the skill's `scripts/` folder. The first resolves against wherever the session's directory is; the second points into the user's project.

**Reaches the script:** the same hook running `"${CLAUDE_PLUGIN_ROOT}"/skills/<skill>/scripts/check.sh`, quoted for shell form.

When you audit:

- Flag a skill hook the skill needs before its first invocation, such as a setup step on `SessionStart`, or a `UserPromptSubmit` hook the skill expects to see the prompt that invokes it.
- Flag a hook command that reaches a bundled script through a relative path or through `${CLAUDE_PROJECT_DIR}`. Recommend `${CLAUDE_PLUGIN_ROOT}` in a plugin skill; in a skill outside a plugin, report the skill-directory variable in a hook as unverified (§2.2) and name the test that would settle it.
- Flag a personal or project skill whose task depends on its own hooks on a target under a hooks lock, and recommend moving the skill into a plugin, which keeps its hooks.
- Flag a skill whose task depends on its hooks under `allowManagedHooksOnly` or `disableAllHooks`, in Cowork, in a forked run, or when a subagent invokes it, as unverified, naming the check: invoke the skill there and run `/hooks`, or read the debug log.
- Flag a plugin skill that depends on its frontmatter hooks while the plugin's `engines` range admits a version before v2.1.94.
- Flag a `once: true` hook the skill treats as having run once whatever the outcome: a failed, blocking or timed-out run keeps it in place.
- Recommend, for a skill with hooks that must run unattended or without a prompt, the exact `Skill(<name>)` allow rule its users add, stated in the skill's documentation.

### 9.2 Hooks, mods and permission rules that act on the skill

Hooks and rules in the environment, or in the skill's own plugin, can act on the skill when it is invoked, when its text expands and on every tool call during its run, and each mechanism sees only some paths.

- **Invocation by Claude:** a `PreToolUse` or `PostToolUse` hook with the matcher `Skill` fires only when Claude calls the Skill tool; typing `/<name>` bypasses `PreToolUse`.
- **Invocation by the user:** `UserPromptExpansion` fires when a typed command expands, before the text reaches Claude, matches on `command_name`, such as `my-plugin:example-skill`, and can block the expansion or add context. In the Agent SDK's event table, it "doesn't fire when Claude invokes a skill itself". `UserPromptSubmit` sees the typed line, not the expanded skill, and runs before expansion, so a block there also stops the skill's injected commands.
- **Matchers:** a matcher made only of letters, digits, `_`, `-`, spaces, `,` and `|` is an exact string; any other character, such as the colon of a plugin skill's name, makes it an unanchored regular expression. A matcher on a plugin skill's bare name therefore doesn't equal its `command_name` (inference from the documented example), and an unanchored scoped name can match more than one command.
- **During the run:** hooks from settings files, managed settings and plugins also fire inside subagents, forked runs included, with `agent_id` and `agent_type` in their input.
- **Loading:** `InstructionsLoaded` fires when a `CLAUDE.md` or `.claude/rules/*.md` file loads, and its load reasons name no skill, so it doesn't report a skill loading (inference from its documented scope). `ConfigChange` with the `skills` source fires when a skill file in `.claude/skills/` changes.
- **Mods:** a mod's `skill.prompt` hook runs when a skill's text is expanded for Claude and can return changed `text` or `frontmatter`; Claude reads the final text. Mods run in Claude Code: the reference covers the CLI, the Desktop app and the VS Code extension, and the directory lists a mod for Claude Code.
- **Permission rules:** a `Skill` deny rule disables every skill; `Skill(name)` matches exactly and `Skill(name *)` by prefix; a deny on an unqualified name also blocks a nested skill listed as `dir:name`, and `Skill(skill:<name>)` blocks the skill under any of its names. An allow rule matches only the skill's own name and the name in Claude's invocation, and doesn't limit Claude to the skills it names; a synced skill is approved only inside its namespace, as `Skill(anthropic-skills:<name>)`. `skillOverrides` can hide a skill from Claude or turn it off, but doesn't affect plugin skills.

Recognize the difference:

**Guards one path:** a plugin that must refuse its `deploy` skill without an approval file ships only a `PreToolUse` hook matching `Skill`. A user who types `/deploy-kit:deploy` runs it unchecked.

**Guards both paths:** the same check also runs on `UserPromptExpansion` with the matcher `^deploy-kit:deploy$`.

When you audit:

- Flag a hook in the skill's plugin, meant to guard or prepare the skill, that covers only the Skill-tool path or only the typed path while the skill can be reached both ways. Recommend the matching hook on the missing path, with its anchored matcher.
- Flag a `UserPromptExpansion` matcher on a plugin skill's bare name, or an unanchored scoped name that also matches other commands.
- Flag a skill or plugin that relies on `InstructionsLoaded` to observe the skill loading.
- Flag a skill whose text is complete or correct only after a `skill.prompt` mod rewrites it, on a target that doesn't run mods, such as claude.ai chat or the Skills API (inference from where mods run).
- Flag an allow rule the skill's documentation tells users to add that can't match the skill, such as `Skill(anthropic *)` for a synced skill, and recommend the exact form.
- Ask, where the prompt reports a deny rule or `skillOverrides` entry that names the skill or a skill it invokes, which step that removes, and judge it under §10.1.

---

## 10. Composition between skills

Judge whether a skill that relies on another skill can reach it at runtime, on every target and path, and whether the composition the skill uses, or lacks, serves its task.

### 10.1 Invoking another skill during a run

Claude has only another skill's description until that skill is invoked; its full content loads on invocation, through the Skill tool or a typed `/<name>`. So a skill that relies on another during its run works only when four things hold: the name resolves, Claude may invoke the target, the Skill tool is present, and the target is loaded on the target surface.

- **The name.** A plugin skill is `/<plugin>:<skill>`, and its bare name also invokes it unless another command already uses that name. When a bare name matches exactly one plugin skill, the Skill tool's "Unknown skill" error names the full name (changelog). A synced skill runs under its short name only while no other command uses it, and otherwise only as `anthropic-skills:<name>`.
- **Who may invoke it.** With `disable-model-invocation: true`, Claude can't invoke the target on its own: Claude Code blocks the call unless the user's message names `/<name>` as a separate word, and the description leaves Claude's context. With `user-invocable: false`, Claude still can.
- **The Skill tool.** It is in the background tool set. A subagent without it in `tools`, or with it in `disallowedTools`, can't invoke skills, and an SDK session with an explicit `tools` list needs it there. A `Skill` deny rule, a `Skill(name)` deny rule, an SDK `skills` list without the target, or a `skillOverrides` entry that hides it removes the target (§9.2, §6.4). The Skill tool can prompt for a target that sets `allowed-tools`, `disallowed-tools` or `hooks`.
- **A forked target.** It runs in the background by default, and its result arrives in the conversation when it completes, so the calling skill's turn doesn't have it unless the target sets `background: false` or one of the waiting cases of §6.1 applies.
- **Pre-approval.** Each skill's `allowed-tools` grants its tools during the turn that invokes that skill, and the grant clears with the next user message. The invoked skill's grant covers its own commands; the caller's grant covers only the commands the caller lists (inference from the per-skill field).

Incorrect cases, each with what goes wrong:

- **A name another command shadows.** The skill says "Run `/review`" for its plugin sibling `my-plugin:review` while a bundled or personal command uses `review`: the other command runs (documented for the typed name; for the Skill tool, inference).
- **A target Claude may not start.** The skill says "Now invoke the `deploy` skill", and `deploy` sets `disable-model-invocation: true`: Claude Code blocks the call.
- **No Skill tool.** A subagent with `tools: Read, Grep` is told to "use the `lint-rules` skill": it has no way to load it.
- **A result read too early.** The skill invokes a forked `collect-metrics` skill and, in the next step, reads its numbers: in the background, they haven't arrived.

Recognize the difference:

**Unresolvable:** "Then run the changelog skill."

**Resolvable:** "Invoke `release-kit:changelog` with the Skill tool and wait for it to finish before step 5; it writes the CHANGELOG entry."

When you audit:

- List every skill the audited skill tells Claude to invoke, and for each one judge the four conditions above on every target and invocation path, taking the target's frontmatter, its location and the session's rules from the prompt or from your own reading.
- Flag each invoked name that doesn't resolve to the intended skill on a target, with the command that would run instead, and recommend the full invocable name with its plugin prefix.
- Flag each invocation of a target that sets `disable-model-invocation: true`, and recommend either dropping the field from the target, if nothing requires it, or telling the user to type `/<name>` at that step.
- Flag each invocation from a subagent, forked or custom, whose tools leave out `Skill`.
- Flag each step that uses a forked target's result in the same turn while the target runs in the background, and recommend `background: false` on the target or a step that waits for its result.
- Flag a skill meant to run unattended that invokes a target the Skill tool would prompt for, and recommend the `Skill(<name>)` allow rule its users add.
- Flag usage instructions, in the skill or its documentation, that tell the user to type `/<name>` after other text in a message to run a skill: after plain text, the name "gives Claude permission to run the skill but doesn't run it", and Claude judges from the wording whether it was asked to. Recommend `/<name>` at the start of the message.

### 10.2 Skills meant to load together

A user can stack several skills at the start of one message, but only at the terminal prompt: through the Agent SDK or `claude -p`, Claude Code loads only the first skill and passes the rest of the line as its arguments. Expansion stops at the first token that isn't an inline user-invocable skill, such as a skill that runs as a forked subagent, and that token and everything after it become the argument text for every skill already expanded. Without stacking, Claude can still use several skills in one task, as the Agent Skills overview's "Compose capabilities" describes, and on the Claude API each skill must be in the request's `container.skills` list to be used at all.

When you audit:

- Flag usage instructions that rely on stacking, such as "type `/prep /review`", for a target that runs through `-p`, the Agent SDK or a scheduled task: only the first skill loads.
- Flag a documented stack that places a forked skill, or a skill whose arguments may start with another command, before an inline skill: the later names become arguments.
- Recommend, where two skills must run together on a non-interactive target, one skill that invokes the other at the step that needs it (§10.1), or two separate invocations.

### 10.3 Dependencies across plugins

The Agent Skills specification defines no field through which one skill declares another: its frontmatter fields are `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`, and `compatibility` is free text about environment requirements. So outside a plugin nothing installs, enables or checks the skill a skill relies on (inference from the spec's fields). Inside a plugin, `dependencies` in `plugin.json` lists "Plugins that must be enabled for this one to work". What it guarantees and how it fails:

- **Install.** Installing the plugin installs each missing dependency, and so do `/reload-plugins`, an auto-update of the marketplace, a repeated `claude plugin install` and `claude plugin marketplace add`. Claude Code never installs a dependency with a `command` source, so users install it first.
- **Version.** Without a constraint, a dependency moves to each new release, and a release that renames what the plugin calls breaks the plugin for everyone who updates. A constraint resolves against git tags named `<plugin-name>--v<version>`: with no satisfying tag, the install fails for a plugin with its own repository, and a plugin referenced by a relative path installs the marketplace's current copy and stays disabled while that copy is outside the range. For an `npm`, `archive` or `command` source, the range is checked against the dependency's `plugin.json` `version` at load, and a `plugin.json` with no version satisfies no constraint.
- **Another marketplace.** A dependency from a different marketplace installs only when the root marketplace lists it in `allowCrossMarketplaceDependenciesOn`, or the user already has it enabled at the same scope; declared in `plugin.json` without that, "the install completes without the dependency and your plugin then fails to load".
- **Local development.** A `--plugin-dir` copy satisfies the entry without a version check, and the plugin stops loading whenever that copy is disabled or absent.
- **claude.ai.** A plugin turned on from claude.ai loads as `<name>@synced`, and a dependency entry counts as met by the dependency installed from its marketplace or by a claude.ai plugin of the same name; the docs tell authors to tell users to turn the dependency on there too. No official source says how claude.ai chat or Cowork treat `dependencies`.

A dependency makes a plugin present and enabled. It doesn't establish that a given skill name exists in it: the docs' own warning is a release that renames what the dependent plugin calls (inference from L74).

Recognize the difference:

**Fails to load:** `"dependencies": [{ "name": "audit-logger", "marketplace": "shared-tools" }]` in `plugin.json`, while the plugin's marketplace has no `allowCrossMarketplaceDependenciesOn`.

**Loads:** the same entry, with `"allowCrossMarketplaceDependenciesOn": ["shared-tools"]` in the root `marketplace.json`, and a `version` range the dependency's tags satisfy.

When you audit:

- Take the plugin's `dependencies`, its marketplace entry and, where the prompt reports them, the dependencies' tags and sources. For each entry, judge install, version and marketplace on every install route the plugin targets.
- Flag a cross-marketplace dependency without the allowlist entry: on install the plugin fails to load.
- Flag a version constraint that no tag satisfies, as the prompt reports it, with its consequence for the dependency's source type; report the point as unverified when the prompt doesn't report the tags.
- Flag an unconstrained dependency whose skills, agents or MCP tools the plugin calls by name, and recommend a range the author has tested, such as `~2.1.0`.
- Flag a `command`-source dependency, or one whose marketplace entry sets a `headersHelper`, that the plugin's documentation doesn't tell users to install first.
- Flag a `dependencies` entry that no component of the plugin uses: every user installs it (inference from the install behavior).
- Flag a plugin meant to be turned on from claude.ai whose documentation doesn't tell users to turn the dependency on there too.
- Flag a skill outside any plugin that declares the skill it relies on only in `compatibility`, `metadata` or prose and expects that skill to be installed: nothing installs it. Recommend packaging both in one plugin, or in plugins linked through `dependencies`.
- Report how claude.ai chat and Cowork treat `dependencies` as unverified wherever the plugin targets them and relies on a dependency.

### 10.4 Composition the skill needs, and composition it doesn't

Because another skill's procedure is in context only once that skill is invoked or preloaded, a step that points at another skill's procedure without invoking it leaves Claude with that skill's description alone, or with nothing when the description isn't listed, and Claude improvises the procedure. The opposite also happens: composition that adds a runtime dependency the task doesn't need, such as a forked invocation for a step whose result the caller needs at once, or a plugin dependency for a skill the plugin never invokes, adds a way to fail without adding anything the task uses.

Recognize the difference:

**Relies on content it never loads:** "Write the entry the way the changelog skill describes."

**Loads what it relies on:** "Invoke `release-kit:changelog` with the Skill tool; it writes the entry."

When you audit:

- Flag each step that relies on another skill's procedure, format or rules without invoking or preloading it, and recommend the invocation at that step, named as in §10.1.
- Ask, for each invocation and each `dependencies` entry, which step of the task uses it. Flag one no step uses, and recommend removing it.
- Flag a forked invocation, or a chain of skills, where the step's result is needed inline and one skill could do it in the main conversation, and recommend the inline form.
- Flag an invocation that can't work on one of the skill's targets, such as a Skill-tool step on the Claude API or in claude.ai chat, where the target's own composition rules apply instead (§10.2), as unverified unless a source the prompt names settles it.

---

## Classifying findings

Give every finding four things: the exact file and line(s) in the skill under audit, the point in this file it violates or falls short of, the kind of evidence it rests on, why it is a defect stated as a consequence on a named target (not just "doesn't match the guide"), and a specific fix with the reason it's the right one. If you have no line to point to, you have no finding.

Classify each defect by what it does to the skill on the surfaces it targets. Ask these questions in order and stop at the first yes:

1. Does a target surface fail to discover the skill, fail to load it, reject it, or fail to run its main action? Assign Critical. For example: a cross-marketplace dependency declared in `plugin.json` without the allowlist entry, so the plugin fails to load after install; a skill whose main action invokes a skill with `disable-model-invocation: true`, which Claude Code blocks; a plugin dependency above the plugin root that the cache doesn't copy; a top-level `bin/` in a plugin that targets the Claude app; a skill meant for cloud sessions that lives only in `~/.claude/skills/`; an injected command no rule allows, which aborts the skill outside auto mode; a plugin-root variable in a non-plugin skill's required command.
2. Does it load but fail silently, make Claude do something else, or lose a required behavior on a target? Assign High. For example: a guard hook that covers only one of the paths that reach the skill; a forked or preloaded skill that needs `AskUserQuestion`; a step that reads a background forked skill's result before it arrives; a bundled hook script reached through a relative path or the project-directory variable; a skill invoked from a subagent whose tools lack `Skill`; usage instructions that stack skills on a `-p` target; a link to a file the skill doesn't contain; a required step that fetches a URL on the Claude API, which has no network; a preloaded skill disabled on a target, skipped with only a debug-log warning; a project-directory variable a synced terminal session leaves literal; a bundled-script rule whose path doesn't match the body, so the script prompts; a forked skill that needs a tool the background set lacks; a same-named skill that runs instead of this one.
3. Does it work, but cost extra steps, fragile assumptions or harder maintenance? Assign Medium. For example: an unconstrained dependency whose names the plugin calls; a skill hook's behavior in a forked run or a subagent, unverified; a `dependencies` entry no component uses; state written under the plugin root; a broad `Bash` grant where an exact rule would do; one archive layout reused across surfaces; a reference or asset reached only through another reference; a file kept in a folder whose role or reader is another's.
4. Otherwise, assign Low. For example: a fixed install path that appears only in an illustrative comment Claude never runs.

Tie-breaks:

- If a finding fits two levels, the first level in the list wins.
- A departure from a recommendation alone never raises a finding to Critical or High; only a broken requirement or documented behavior can.
- A surface the skill doesn't target gets no finding.
- A point that neither the prompt nor the files can settle is Medium. Name in its finding the level it would reach if the check fails.
- When the consequence differs by target, set the severity of the most affected target, and name each affected target with its consequence in the finding.

Never invent impact. Never inflate a severity to make the report look decisive, and never lower one because a workaround exists. When several symptoms share one root cause, report the root cause once and list every affected location. Split findings only when they have independent causes or need independent fixes.

## Improvement opportunities

Separate improvement opportunities from defects: an opportunity is something that works on every target but that a sturdier pattern in this file would improve, or something the skill's targets need and the skill lacks. Report one only where it genuinely applies to this skill; this section of your report may stay empty. For each one, give what exists now (or that it is absent, and where it belongs), what this file recommends instead, and why that's actually better for this skill on its targets, never a generic "could be better."

This file gives you the rules, the context to establish, and the severity model. The gotchas and the verification checklist live in your own instructions, and the report template lives in this skill's `assets/` folder, so they aren't repeated here.

## Delivering the report

Deliver every defect and improvement opportunity in the shared findings template, `assets/audit-report.md` in this skill. Fill one defect block per defect, with every field, and keep the template's structure exactly. Symptoms with one root cause are one defect: give its first location in File and Lines, and list every other location, as `path:lines`, in Finding.
