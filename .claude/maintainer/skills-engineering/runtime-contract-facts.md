# Runtime-contract fact ledger

Verified 2026-11-14 against Claude Code 2.1.325 (latest in changelog.md). Docs downloaded as Markdown from code.claude.com/docs/en/<page>.md.
Format: claim | source | status

## Surfaces
- Chat and Cowork are merging into one Claude; rolling out from Pro and Max; on Team (beta) and Enterprise where "Chat and Cowork unified" is on; once moved, an account can't switch back | support.claude.com/en/articles/16761823 | verified
- On a merged account tasks run in the cloud, with no option to run them locally | support.claude.com/en/articles/15811196 | verified
- Cloud Cowork sessions need the desktop app open for local files, local MCP servers (including plugins that bundle them), browser use and computer use | support.claude.com/en/articles/15811196 | verified
- Cowork and cloud sessions, including cloud scheduled tasks, don't read `~/.claude/skills/`; they load skills enabled for the claude.ai account, synced at session start | skills.md "Use skills in Cowork and cloud sessions" | verified
- Project cloud threads load each repo's CLAUDE.md, `.claude/CLAUDE.md` and root `.claude/rules/`, but not `.claude/skills/`, agents, commands, `.mcp.json`, settings plugins, permission rules, hooks or env | claude-projects.md "What threads pick up from your repositories" | verified
- Other cloud sessions may load repo `.claude/skills/`; plugins in repo `.claude/settings.json` and plugins enabled only in user settings don't load in cloud sessions | skills.md same section | verified
- Desktop scheduled tasks run locally and load `~/.claude/skills/` | skills.md same section | verified
- Some self-hosted sessions don't load account skills | skills.md same section | verified
- Terminal sync: signed-in claude.ai sessions download account skills into `~/.claude/skills/synced/` (v2.1.273+); no sync with API key, ANTHROPIC_AUTH_TOKEN, CLAUDE_CODE_OAUTH_TOKEN, apiKeyHelper, Bedrock, CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC, bare mode, --safe-mode, strictPluginOnlyCustomization skills lock, --setting-sources without user | skills.md "Where synced skills load" | verified
- Synced body: cloud session keeps local-skill behavior; desktop Cowork replaces `!` lines with the disableSkillShellExecution placeholder; terminal or VS Code doesn't run `!`, doesn't attach `@` files, doesn't substitute CLAUDE_PROJECT_DIR and CLAUDE_SESSION_ID (v2.1.228+) | skills.md "How Claude Code handles the body of a synced skill" | verified
- `@` attach in local skills: inferred from the synced-skill contrast above | inferred
- API skills: sandboxed container with no network access and no runtime package installation | platform.claude.com/docs/en/agents-and-tools/agent-skills/overview | verified
- Custom skills don't sync across surfaces (claude.ai vs API) | same page | verified; disagreement: same page says Claude Code skills are separate from claude.ai, while skills.md documents claude.ai account sync into Claude Code — Claude Code docs govern for Claude Code
- API container path: page example shows `/mnt/skills/<name>/`; original's `/skills/<name>/` not found | removed (path not needed for an audit judgment)
- Managed Agents: skills attached through the agent's skills array or loaded from a mounted GitHub repo; discovery finds exactly `.claude/skills/<skill-name>/SKILL.md` one level deep at the repo root; relies on the agent's read tool; same-named repo and attached skills both available, each announced with its path | platform.claude.com/docs/en/managed-agents/skills | verified
- Managed Agents default mount path `/workspace/<repo-name>` | platform.claude.com/cookbook/managed-agents-cma-use-skills-from-a-repo | verified
- claude.ai skill ZIP: the skill folder is the ZIP's root entry, folder name matches the skill name; files directly at ZIP root are wrong | support.claude.com/en/articles/12512198 | verified
- claude.ai and Claude Code can install packages from PyPI and npm when loading skills; API skills can't | same article | verified
- Disagreement (parked, frontmatter): help center gives description max 200 and an optional `dependencies` field; platform gives 1,024 | same article | parked

## Discovery and precedence (Claude Code)
- Location table (enterprise, personal, project, nested, added dir, plugin, claude.ai account) | skills.md "Choose where skills load" | verified
- Project skills load from start dir and parents up to repo root; worktree searches to worktree root; v2.1.277+ falls back to main checkout's project skills when the worktree has no root `.claude/skills` | skills.md "Load skills in monorepos and subdirectories" | verified
- Nested skills load the first time Claude reads or edits a file there | same | verified; 2.1.319: with the Bash sandbox on, only if started or /cd'd there; 2.1.321: not inside `~/.claude/plugins`; 2.1.325: not in `--plugin-dir` plugins from a session started above | changelog.md | verified
- `--add-dir` loads its `.claude/skills`, commands, agents; `permissions.additionalDirectories` loads none; same-named added-dir skill runs as `/<prefix>:<name>` (v2.1.309+) | skills.md "Load skills from a directory outside the project" | verified
- Precedence: enterprise > personal > project; plugin skills namespaced and both load; synced short name yields to any other command | skills.md "Resolve skills that share a name" | verified
- Symlinked skill folders in enterprise, personal, project locations: read from target, loaded once | skills.md "Choose where skills load" | verified
- Skill folder with `.claude-plugin/plugin.json` loads as `<name>@skills-dir` plugin; project location needs workspace trust; admins can block | skills.md same | verified
- New top-level skills dir mid-session needs `/reload-skills`; plugin-folder changes to `.mcp.json`, `agents/`, `output-styles/`, `hooks/` need `/reload-plugins` | skills.md "Edit a skill during a session" | verified

## Paths and substitution
- Variables: CLAUDE_SKILL_DIR (skill subdir in a plugin), CLAUDE_PROJECT_DIR, CLAUDE_PLUGIN_ROOT and CLAUDE_PLUGIN_DATA (plugin skills only), CLAUDE_SESSION_ID, CLAUDE_EFFORT | skills.md "Available string substitutions" | verified
- Substituted in skill Markdown and in allowed-tools Bash rules; same variable in both lets a bundled script run without prompt | same | verified
- Substitution happens after argument insertion; backslash doesn't stop `${CLAUDE_*}` | same | verified
- Not in the environment of Bash tool commands (main session or subagent); hook commands, MCP stdio and LSP servers do receive CLAUDE_PLUGIN_ROOT, CLAUDE_PLUGIN_DATA, CLAUDE_PROJECT_DIR | plugins/manifest-reference.md "Where each variable resolves" | verified
- Skill, command and agent content of plugins: `${...}` resolves anywhere in the Markdown body | same | verified
- CLAUDE_PLUGIN_ROOT changes when the plugin updates; don't write state there; CLAUDE_PLUGIN_DATA = `~/.claude/plugins/data/<id>/`, created on first reference, deleted on uninstall from last place by default | plugins/manifest-reference.md "Environment variables" | verified

## Plugin layout, manifest, cache
- Component paths start with `./`; `skills` also accepts `.`; paths must resolve inside the plugin root and exist; `..` rejected | plugins/manifest-reference.md "Path rules" | verified
- `skills` adds to the default `skills/` scan; entries are directories | same, "How each key combines" and Fields table | verified
- Single `SKILL.md` at plugin root loads as one skill when no `skills/` and no `skills` key; set `name` or a marketplace install names it after its cache directory | plugins/components.md | verified
- `skills/` inside `.claude-plugin/` or a `skills` entry pointing at a file: skills missing | plugins/create.md troubleshooting | verified
- Load in place: `--plugin-dir`, skills-directory plugins, relative-path plugins in a local-path marketplace (their hooks/MCP/LSP get CLAUDE_PLUGIN_ROOT pointing at source), link-mode command sources; every other marketplace plugin is copied into `cache/<marketplace>/<plugin>/<version>/`; files outside the plugin aren't copied | plugins/loading.md | verified
- Component path outside the plugin root rejected whether in plugin.json or marketplace entry, except symlinks between plugins in one marketplace | plugins/loading.md | verified
- Top-level `bin/` is on the Bash tool PATH while enabled; claude.ai and Cowork don't install a plugin with a top-level `bin/` | plugins/components.md; plugins/host-marketplace.md | verified
- 2.1.323: `engines["claude-code"]` in plugin.json gates install/update/load by version range | changelog.md | verified
- 2.1.325: plugin loading skips, and validate reports, some unsafe paths and links | changelog.md | verified
- Marketplace entry whose source is the marketplace root and lists `skills` subdirectories loads only those; default `skills/` not scanned | plugins/manifest-reference.md "Marketplace entries and the manifest" | verified
- With a plugin.json, `strict: true` (default) appends the entry's component fields; `strict: false` makes any entry component field a conflict and the plugin fails to load | plugins/marketplace-reference.md "Strict mode" | verified

## Symlinks
- Plugin cache copy: target inside plugin → preserved relative; elsewhere in same marketplace → dereferenced and copied; outside marketplace → skipped; local-path and copy-mode command sources keep only in-plugin targets | plugins/host-marketplace.md "Share files within a marketplace with symlinks" | verified

## Subagents
- `context: fork` starts a new subagent of the `agent` type with skill content as prompt; it doesn't see conversation history and is not a fork of the conversation; background by default, `background: false` waits; backgrounded fork uses the narrower background tool set | skills.md "Run skills in a subagent" | verified
- Built-in Explore and Plan start without CLAUDE.md and git status | same | verified
- Preload: `skills` field injects full content of up to the first 32 distinct names; controls preload, not access; omit `Skill` from tools or add to disallowedTools to prevent invocation; skills with disable-model-invocation can't be preloaded; built-in agents don't preload | sub-agents.md "Preload skills into subagents" | verified
- Plugin subagents ignore `hooks`, `mcpServers`, `permissionMode`; `initialPrompt` ignored for plugin subagents | sub-agents.md | verified
- Subagents spawn up to three layers below main; CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH | sub-agents.md | verified
- Plugin agent `skills` entries bare vs namespaced: not documented | evidence gap (kept as unverified)

## Tool pre-approval and shell execution
- allowed-tools grants listed tools during the invoking turn; clears on next message; doesn't restrict available tools; permission settings govern the rest | skills.md "Pre-approve tools for a skill" | verified
- Project skill allowed-tools applies even in `-p` in an untrusted folder | same | verified
- allowManagedPermissionRulesOnly ignores allowed-tools in project and personal skills (v2.1.282+); strictPluginOnlyCustomization listing hooks removes allowed-tools from personal/project skills that declare hooks | same | verified
- Injected commands never prompt; deny match aborts; outside auto mode a non-allow result aborts unless pre-approved by allowed-tools; deny/ask still abort; bare-repo folders ignore allowed-tools for git commands | skills.md "Permission checks on injected commands" | verified
- 2.1.325: scheduled tasks and /loop ask before running a skill that declares allowed-tools or hooks; `Skill(name)` in permissions.allow runs it unattended | changelog.md | verified

## Added after final review (all verified 2026-11-14)
- Validator scope and symlink handling | plugins/cli-reference.md "Validate" block (lines ~610-632) | verified
- `${user_config.KEY}` sensitive values become placeholders in skill and agent content | plugins/manifest-reference.md "Reference a saved value" | verified
- Claude Code-only body features don't function in claude.ai chat or the API | skills.md "Using skill frontmatter outside Claude Code" | verified
- Forked skill also waits in non-interactive runs | skills.md "Run skills in a subagent" | verified
- Auto mode: unapproved injected command loads with instruction to run it, except forked skill with `agent` | skills.md "Permission checks on injected commands" | verified
- Background subagent built-in tool set (Read … Artifact, plus every MCP tool) | sub-agents.md, background filter | verified
- Synced plugins load as `<name>@synced`; Cowork downloads at session start; terminal sync once at startup v2.1.273+, all components with marketplace trust | plugins/loading.md "Plugins synced from claude.ai" | verified
- Skills-directory plugins are read only from the primary working directory's `.claude/skills/`, no parent search | plugins/loading.md | verified
- Plugin-root `CLAUDE.md` isn't loaded | plugins/components.md | verified
- Preloaded skill missing or disabled is skipped with a debug-log warning | sub-agents.md "Preload skills into subagents" | verified
- Nested skills load at startup in sessions started in or below the subdir | skills.md location table | verified
- Built-in command replacement applies in a local terminal session | skills.md "Resolve skills that share a name" | verified
- Unified-experience accounts have no local task option; non-unified accounts can toggle local Cowork | support.claude.com/en/articles/15811196 | verified
- Plugin ZIP layout (`.claude-plugin/plugin.json` at ZIP root or one enclosing folder) | not found in downloaded docs | removed
- Skills API upload layout | not found | removed; reviewer reports it unverified
