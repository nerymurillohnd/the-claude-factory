# How to Work With Nery in This Project

## Rules by Task

Each section below applies to one kind of work. Follow the section for the task at hand before you start it.

### When Checking Quality

The commands live in `.claude/CLAUDE.md` → Commands.

- Do not advance to the next step, file or task while a detected issue is open.
- Report an issue as open only when it is blocked on a decision or a spend only Nery can make. Stop and ask.
- Run the gates for every `.py`, `.mjs`, `.ts` and `.sh` file you edit, write or create, right after the edit and before the next task.
- Run them in this order: formatter, linter, type checker, tests.
- Pass each strict `tsc` flag with an explicit value: `--strict` does not override an explicit `false` in a tsconfig.
- Before every push, run the steps in order. Stop at the first failure, fix the cause, then restart from step 1.
- Report the gates as a table: gate, result and key output line.

### When Maintaining Plugins and Repo Documentation

- Read its README. Add what the change made missing and remove what it made obsolete.
- Summarize the change in its `CHANGELOG.md`. Each plugin changelog tells the full story of that plugin.
- The Version badge in a plugin README must stay dynamic, reading `version` from `plugin.json`. Never hardcode a version in it.
- The root `CHANGELOG.md` is a summary, never a copy of a plugin changelog.
- Changelogs follow Keep a Changelog 2.0.0. Write entries under `## [Unreleased]` as you work.
- User-facing language: what changed for the user, not implementation detail. Reference issues as `(#12)`.
- Mark breaking entries with a leading `**Breaking:**` inside their change type (they force a major bump, or a minor bump in `0.x`).
- Root `CHANGELOG.md` is grouped by date, newest first, with one line per plugin launch, version bump or substantial change under that day's heading: `- **plugin-name** 1.2.0 — one-line summary.`
- Create the `## YYYY-MM-DD` heading when it is missing, with `### Added`, `### Changed` and so on below it.

### When Writing Plugins

- When a plugin needs a specific version, tool, binary or program, list it as a prerequisite in its README, with how to install it and the applicable alternatives.
- When the new plugin overlaps an existing one by domain, weigh integrating it into that plugin against creating an independent one. Propose the choice to Nery.
- Whether a plugin has evals is Nery's decision.
- Read the Claude Code changelog for the installed version, the four before it and every newer one. Contrast what you find and apply it.
- Name skills and plugins for what the skill does, not how it is implemented.
- Keep the version in `plugin.json`. Never set `version` on a marketplace entry.
- Change `displayName` to relabel a plugin.
- After moving or creating files, delete `.DS_Store` files and orphaned cache directories.
- Ship a plugin's Node dependencies only with an npm or Bun lockfile; other lockfiles leave no `node_modules`.
- Do not set `hooks` in the frontmatter of a plugin agent: it is ignored. Declare the hook in the plugin's `hooks/hooks.json`.
- Scripts start with `#!/usr/bin/env <interpreter>` (no version), are committed as `100755`, and are called by path (`${CLAUDE_SKILL_DIR}` or `${CLAUDE_PLUGIN_ROOT}`).
- Network calls only when the plugin's purpose requires them and the README discloses them.

### When Writing Hooks

#### Declare

- Use the three levels of `hooks/hooks.json`: event, matcher group, handler. The contract is JSON on stdin. Never write a `"hook"` object or read `$TOOL_INPUT`.
- Write the command in shell form with the placeholder in double quotes: `"command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/<script>\""`. Exec form (`args`) needs a real `.exe` on Windows, and Windows runs only through Git Bash here.
- Set `timeout` on every handler. A command hook defaults to 600 seconds.
- A matcher of letters, digits, `_`, `-` and `|` is an exact tool-name match. `Bash` does not cover `PowerShell`.
- Resolve `node` and `tsc` across every Node manager: plugin hooks and LSP servers get no shell profile.

#### Decide

- Block with one JSON object on stdout and exit 0: `hookSpecificOutput.hookEventName` `"PreToolUse"`, `permissionDecision` `"deny"`, and a `permissionDecisionReason` that tells Claude what to do instead. Exit 2 with a reason on stderr blocks too. Exit 1 never blocks.
- Print nothing else on stdout. A second line turns the output into plain text or a parse failure.
- To pass a call, print nothing and exit 0. Silence leaves the decision to the permission flow; it never approves.
- A guard that cannot read or parse its own input denies the call and says why.

#### Filter

- Never put `if` on a hook that enforces a policy. The page calls the filter best-effort: it strips leading `VAR=` assignments, and the permissions page strips only `timeout`, `time`, `nice`, `nohup`, `stdbuf`, `command`, `builtin` and `noglob`. Treat `sudo`, `env`, `xargs`, `watch` and `bash -c` as not stripped until a test shows otherwise, so `if: "Bash(git *)"` would skip `sudo git commit --no-verify`.
- Filter inside the script instead, on the words after lexing, never on the raw text. The shell joins quotes, so `g"i"t commit --no-verify` runs git and contains no `git` substring. Parsing costs far less than starting the interpreter.
- Write one permission rule per hook `if` field. A rule joined with `|` never matches.

#### Fail

- Set `"onFailure": "block"` on a check hook, so a broken hook never passes in silence.
- Report a missing tool as a non-blocking `systemMessage` plus `additionalContext`, never as a silent pass. A guard whose job is to deny is the exception: it denies the commands it guards and says what to install.
- Declaring `onFailure` makes Claude Code 2.1.295 the plugin's minimum. Older versions let a hook that cannot start pass the call.
- A hook that runs an interpreter starts from a launcher script. The launcher checks the interpreter and its minimum version first. When either is missing it prints `systemMessage` and `additionalContext` and exits 0, because with `"onFailure": "block"` a missing interpreter would block every call, not only the guarded ones.
- Past that check, a crash, a timeout or an exit code other than 0 or 2 blocks. That is the intent.

#### Cover

- Test a hook in `settings.json` right after editing it: the file watcher loads it with no restart. A plugin hook needs `/reload-plugins`.
- Test a hook script with `env -i`, an empty `HOME` and a minimal `PATH` for each Node manager.
- Plugin hooks also run inside subagents. The input carries `agent_id` and `agent_type`. Test one call made from a subagent before the README says the hook covers them.
- Test the hook in `default` and in `bypassPermissions` mode before the README states what it blocks. The page does not say the hook runs in both.
- Hooks that match one event run in parallel, and the strictest decision wins: `deny`, then `defer`, `ask`, `allow`.

#### Document

- Under Limitations in the README, name what the hook does not reach:
  - a tool the matcher leaves out, such as the PowerShell tool when `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` turns it on;
  - the policies that turn hooks off, `allowManagedHooksOnly` and `disableAllHooks`;
  - the surfaces where it does not run, per [compatibility](../../docs/compatibility.md).
- State that a hook is a barrier for Claude, not a security boundary, and that it never sees what a person types in their own terminal. The page says to enforce a hard allow or deny through permissions.

### When Versioning a Plugin

| Bump | When |
| :-- | :-- |
| **major** | Breaking: removed/renamed skill, agent or command; changed config keys; new required dependency; behavior users rely on changes |
| **minor** | New component, option or capability, backwards compatible |
| **patch** | Bug fix, prompt wording fix, performance, internal refactor with same behavior |

- `0.x` while a plugin is new; `1.0.0` only when Nery declares its interface stable.
- In `0.x`, a breaking change bumps the minor (`0.y.z` → `0.(y+1).0`) and its changelog entry keeps `**Breaking:**`. From `1.0.0` on, breaking means major.
- Never rename silently. Add `"renames": { "old": "new" }` (or `"old": null` for removal) to `marketplace.json` and note it in the root changelog.

### When Using GitHub

- Changes to plugin manifests, components and dependencies always go through a PR.
- Changes to maintainer documentation need no PR unless Nery explicitly asks for one.
- Check the failed jobs and the reviews of Claude and of third parties. Verify each finding.
- Repeat until everything is green and no more reviews, issues or failed jobs are found.
- Comment on each review and resolve it. A PR is not ready to merge before that.
- Always stop at ready to merge and tell Nery, then wait for the green light.

### When Releasing

- Release right after a plugin PR that carries a version change merges. There is no separate release commit.
- The plugin PR holds the bump: the level from the diff, the notes under `[Unreleased]`, `node .github/scripts/bump-version.mjs <plugin> <level>` and the root `CHANGELOG.md` line.
- Reference fixed issues with `Refs #n`. Never write `Closes #n`: issues close in the release step.
- If Validate failed, fix the cause first. Release only after it passes.
- Never tag by hand.

After the merge:

1. `gh run list --workflow release.yml --branch main --limit 1` - Run to read the release run that follows the merge.
2. `gh release view <plugin>--v<version>` - Run to confirm the tag and the GitHub Release exist.
3. `gh workflow run release.yml` - Run only when Validate passed and no release run exists.
4. For each fixed issue: comment that the fix is released, label it `status: released` and close it.

### When Writing Skills

- Description: what it does + when to use it, third person, ≤ ~500 characters, specific trigger phrases.
- Body: headers, numbered steps, bullets; under 500 lines and ~5,000 tokens. Follow [agentskills.io best practices](https://agentskills.io/skill-creation/best-practices):
  - Moderate detail: each line must be something the model would get wrong without it. The main path stays in `SKILL.md`; situational paths go to `references/` with a "read when …" trigger. Leave layout and rare cases to the model.
  - Prescriptive only where the task is fragile (exact commands, sequences, formats); elsewhere state the goal and why.
  - Defaults, not menus: one default with a short escape hatch.
  - A short input/output example; a template for output that must keep its shape.
- Word guidance that needs judgment for the whole task ("after every edit", not "once").
- Audit our own skills with `/skill-diagnostics:audit`, and re-audit after any rewrite: slimming can drop a load-bearing rule.
- In a file under `references/`, link with a path relative to that file, and only to templates: `[template](../assets/template.md)`.
- Never link from one reference to another. Keep references one level deep from `SKILL.md`.
- Project skill in `.claude/skills/`: use `${CLAUDE_PROJECT_DIR}/...`, such as `[rule](${CLAUDE_PROJECT_DIR}/.claude/rules/WORKFLOW.md)`.
- Skill inside a plugin: use `${CLAUDE_PLUGIN_ROOT}/...` for files of that plugin.
- Never reference a file outside the plugin from a plugin skill. The install does not copy it.
- Personal skill: use `${CLAUDE_SKILL_DIR}/...` for its own files.
- Skill synced from claude.ai: reference no file outside the skill.
- Never use `../` to leave the skill folder.

### When Writing User Docs

- READMEs sell: lead with the outcome and why to install, then teach. Never mention maintenance, `.claude/`, internal scripts, CI internals or how we work.
- English, second person, active voice, present tense. Short sentences.
- Benefit first, mechanics second.
- Emoji-prefixed `##` headings, one emoji per heading, consistent across docs (📥 install, 🔧 manage, 🧭 compatibility, 🩺 troubleshooting, ❓ FAQ, 🔄 update, 🗑️ uninstall, 📝 changelog, 📄 license).
- Badges in the hero only: shields.io, brand color `D97757`.
- Tables for comparisons, commands per surface, requirements and options.
- GitHub alerts (`> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`) — never two alerts back to back without text between.
- `<details>` for per-surface instructions and FAQs; the most common option `open`.
- **Bold** for UI labels exactly as shown in the app (`/plugin` → **Installed** → **Update now**). *Italics* for emphasis or terms.
- Relative links inside the repo; absolute `https://` links outside.
- Version-gated features state the minimum version (e.g. "v2.1.292+").
