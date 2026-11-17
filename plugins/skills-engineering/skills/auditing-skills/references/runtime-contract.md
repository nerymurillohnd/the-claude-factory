# Runtime contract

This file teaches you how to audit whether a skill's files resolve, package, load and are discovered on every surface it targets: its packaging boundary and archive layout, how its files link to each other, its paths and variable substitution, its plugin layout and cache, its symlinks, its discovery, precedence and sync, how subagents consume it, and how its tool pre-approval and injected commands behave at runtime. Each section gives you the principle, why it matters, and what to do when you audit.

## Contents

- How to use this file
  - Before auditing: establish the context
  - Then, audit area by area
- 1. Supporting files and the packaging boundary
  - 1.1 Files inside the boundary
  - 1.2 Upload and archive layouts
  - 1.3 How the skill's files reach each other
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
- 7. Tool pre-approval and shell execution
  - 7.1 allowed-tools at runtime
  - 7.2 Injected commands at runtime
- 8. Validator scope and blind spots
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

A judgment that's correct for one route can be wrong for another, so settle these four points before you apply any rule. They decide what "correct" means for the skill in front of you.

1. **Where the skill lives.** Identify whether it is an enterprise skill (managed settings directory), a personal skill (`~/.claude/skills/`), a project skill (`.claude/skills/`, including nested ones), a skill from an added directory (`--add-dir`), a skill in a plugin's `skills/` directory, a single `SKILL.md` at a plugin's root, a skill folder that is also a skills-directory plugin, a skill enabled on a claude.ai account and synced, a Skills API upload, or a Managed Agents skill. Each route has its own discovery, packaging and substitution rules, so don't judge one by another's.
2. **Which surfaces will load it.** Record the actual deployment targets, not product names:
   - Claude Code in a local session: terminal, IDE, or desktop app.
   - Claude Code in a cloud session: Claude Code on the web and cloud scheduled tasks, plus project cloud threads, which load less than other cloud sessions (§5.3).
   - The Claude app. On an account moved to the unified experience, chat and Cowork are one conversation and tasks run in the cloud with no local option. On an account not yet moved, chat and Cowork are separate, and Cowork can also run locally in the desktop app. Cloud Cowork sessions reach local files, local MCP servers, browser use and computer use only while the desktop app is open.
   - The Skills API and Managed Agents.
   If the prompt names no target, infer it from the files and state the assumption in the report. Never audit against Claude Code alone and present the result as valid everywhere. For a skill that targets several surfaces, judge each one.
3. **How the skill gets invoked.** Determine whether it runs directly in a session, is forced into a subagent with `context: fork`, or is preloaded into a custom subagent's `skills` list (§6).
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

Judge the mechanics that decide whether the subagent gets the skill at all, and with which tools.

### 6.1 Forked skills

With `context: fork`, Claude Code starts a new subagent of the `agent` type and gives it the skill content as its prompt. Despite the name, it isn't a fork of the conversation and doesn't see the history. It runs in the background by default, with the background tool set: every MCP tool, but of the built-in tools only `Read`, `Grep`, `Glob`, `LSP`, `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`, `EnterWorktree`, `ExitWorktree`, `Monitor`, `TaskStop`, `SendMessage` and `Artifact`; `background: false` makes it wait and keeps the full tool set. Claude Code also waits in non-interactive runs. The built-in Explore and Plan agents start without `CLAUDE.md`.

When you audit:

- Flag a forked skill whose steps need a tool outside the background set while it runs in the background.
- Flag a forked skill that relies on `CLAUDE.md` while it names Explore or Plan as its agent.
- Flag `context: fork` on a skill that holds guidelines but no task: the subagent gets no actionable prompt.

### 6.2 Preloaded skills

A custom subagent's `skills` field injects the full content of the listed skills at startup. It controls what is preloaded, not what the subagent can invoke: a subagent with the `Skill` tool can still invoke other skills. Built-in agents don't preload skills. A skill with `disable-model-invocation: true` can't be preloaded, and a listed skill that is missing or disabled is skipped with only a debug-log warning. Plugin subagents ignore `hooks`, `mcpServers`, `permissionMode` and `initialPrompt`. No official source says whether a plugin agent's `skills` entries take bare or namespaced names.

When you audit:

- Flag a skill meant for preloading that a built-in agent is expected to preload, or that sets `disable-model-invocation: true`.
- Flag a preloaded skill that may be missing or disabled on a target, such as one outside the subagent's plugin and its declared dependencies.
- Flag a subagent whose explicit `tools` list leaves out `Skill` while its instructions require invoking skills.
- Flag a plugin agent that relies on `hooks`, `mcpServers`, `permissionMode` or `initialPrompt`.
- Flag a plugin agent's `skills` entry for a plugin skill as unverified, with the load test that would settle it.

---

## 7. Tool pre-approval and shell execution

### 7.1 allowed-tools at runtime

`allowed-tools` grants the listed tools during the turn that invokes the skill, and the grant clears with the next user message. It doesn't restrict which tools exist, and deny and ask rules still win. A rule matches the whole command line, so the skill body and the rule must name the same path through the same variable. A project skill's grant applies even in a `-p` run in an untrusted folder. `allowManagedPermissionRulesOnly` makes Claude Code ignore `allowed-tools` in project and personal skills. When managed settings list `hooks` in `strictPluginOnlyCustomization`, a personal or project skill that declares hooks loses its pre-approval. Scheduled tasks and `/loop` ask before running a skill that declares `allowed-tools` or hooks, unless `Skill(name)` is in `permissions.allow`.

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

## Classifying findings

Give every finding four things: the exact file and line(s) in the skill under audit, the point in this file it violates or falls short of, the kind of evidence it rests on, why it is a defect stated as a consequence on a named target (not just "doesn't match the guide"), and a specific fix with the reason it's the right one. If you have no line to point to, you have no finding.

Classify each defect by what it does to the skill on the surfaces it targets. Ask these questions in order and stop at the first yes:

1. Does a target surface fail to discover the skill, fail to load it, reject it, or fail to run its main action? Assign Critical. For example: a plugin dependency above the plugin root that the cache doesn't copy; a top-level `bin/` in a plugin that targets the Claude app; a skill meant for cloud sessions that lives only in `~/.claude/skills/`; an injected command no rule allows, which aborts the skill outside auto mode; a plugin-root variable in a non-plugin skill's required command.
2. Does it load but fail silently, make Claude do something else, or lose a required behavior on a target? Assign High. For example: a link to a file the skill doesn't contain; a required step that fetches a URL on the Claude API, which has no network; a preloaded skill disabled on a target, skipped with only a debug-log warning; a project-directory variable a synced terminal session leaves literal; a bundled-script rule whose path doesn't match the body, so the script prompts; a forked skill that needs a tool the background set lacks; a same-named skill that runs instead of this one.
3. Does it work, but cost extra steps, fragile assumptions or harder maintenance? Assign Medium. For example: state written under the plugin root; a broad `Bash` grant where an exact rule would do; one archive layout reused across surfaces; a reference or asset reached only through another reference.
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
