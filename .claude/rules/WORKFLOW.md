# How to Work With Nery in This Project

## Rules by Task

Each section below applies to one kind of work. Follow the section for the task at hand before you start it. The sections run in the order of a plugin's life: quality applies to all of them, then create, write, change, version, review, ship, support and keep current. Commands live in `.claude/CLAUDE.md` → Commands.

A line that says "Recall memory `<name>`" points to a verified fact or a past correction: read `<name>.md` in the project memory (`.claude/memory/`) or, when it is not there, in the global memory (`~/.claude/memory/`) before you act on that step.

### When Checking Quality

Applies to every task.

1. After you edit, write or create a `.py`, `.mjs`, `.ts` or `.sh` file, run the commands for its type in Commands → After Editing a File, right away and before the next task, in this order: formatter, linter, type checker, tests.
2. Pass each strict `tsc` flag with an explicit value: `--strict` does not override an explicit `false` in a tsconfig. Before the first edit of a `.ts`, `.mts`, `.js` or `.mjs` file in a task, tests and scratch scripts included, invoke the TypeScript lifecycle skill: recall memory `ts-lifecycle-before-ts-edits`.
3. Fix every finding before you advance to the next step, file or task. An issue stays open only when it waits on a decision or a spend only Nery can make: then stop and ask.
4. Before every push, run Commands → Before Every Push in order. Stop at the first failure, fix the cause, then restart from step 1.
5. Report that run as a table: gate, result and key output line.

### When Creating a Plugin

Only when Nery explicitly asks to create, build or start a plugin. Each step names the section that governs it.

1. Write the design brief and agree it with Nery, in Spanish, before building anything:
   - Market check: what already exists for this domain, what users must combine today, and what this plugin covers in one install that they cannot find elsewhere.
   - Problem and outcome: the recurring friction it removes, and who it is for.
   - Overlap: when an existing plugin of this marketplace covers part of the domain, weigh extending it against a new plugin, and propose the choice. Never argue a design choice from another plugin of the marketplace: recall memory `no-other-plugins-as-precedent`.
   - Name: kebab-case, permanent, no `claude-` or `anthropic-` prefix, named for what it does; a display name and an emoji.
   - Category: an `id` from `.github/scripts/categories.json`.
   - Components: skills, agents, hooks, MCP, LSP, output styles, monitors, scripts, each justified by a user task.
   - Surfaces: Claude Code and the Claude app by default. Check every component against `docs/compatibility.md`; if a part forces Claude Code-only, say why and get Nery's OK.
   - Requirements: CLIs, accounts, API keys (`userConfig`), dependencies, minimum Claude Code version.
   - Evals: ask Nery whether the plugin gets them (When Writing Evals).
   - Sources: the current official docs for every component type used, with their version-gated features.
2. Scaffold with `new-plugin.mjs`. Pass `--claude-code-only` only when the brief approved it. It creates `plugins/<name>/` with the manifest, README, CHANGELOG and LICENSE, registers the marketplace entry and regenerates the catalog.
3. Build the components per When Writing Plugins, When Writing Skills and When Writing Hooks. Exercise each one while you build with `claude --plugin-dir plugins/<name>`.
4. Write the README per When Writing User Docs, starting from the scaffolded template.
5. Fill `CHANGELOG.md` → `## [0.1.0]` → `### Added` with what ships, and add `- **<name>** 0.1.0 — <summary>.` under `### Added` in today's heading of the root `CHANGELOG.md`. Move that line to the merge day if the PR merges on a later day.
6. Write the evals when Nery approved them (When Writing Evals).
7. Stop and tell Nery the plugin is built. While he is still shaping it, run only the cheap checks each edit needs, and do not run or announce live tests, the full gate sequence or the plugin review: recall memory `no-unrequested-verification-while-designing`. Run the closing checks only once he says it is ready:
   - every step of Before Every Push passes;
   - the plugin review passes (When Reviewing a Plugin) and every confirmed finding is fixed;
   - Nery runs the Claude app check in a Cowork session and a chat conversation, unless the plugin is Claude Code-only.
8. Open the PR per When Using GitHub. After the first push, run `sync-labels.mjs` to create the `plugin: <name>` label.
9. Hand off: what was built, the raw gate output, the surfaces tested and the release step (When Versioning and Releasing a Plugin).

### When Writing Plugins

Every time you scaffold, create, edit or remove any of these:

- A file under `plugins/<name>/`: a component (skill, agent, hook, MCP or LSP server, mod, output style, `bin/`), a script, `plugin.json`, `LICENSE`, `NOTICE.txt`, the README or the CHANGELOG.
- A plugin file that Nery hands over in his own version.

Do this:

1. Invoke the `plugin-development` skill with the Skill tool as soon as you touch the file, and follow it until its last step.
2. State the user task each component serves, and read the official docs for each component type before you write it.
3. Recall the memories those components depend on, then write for any user of the public marketplace: the required files, the manifest fields, each script called by path, every network call disclosed in the README.
4. Clean up, exercise the plugin with `claude --plugin-dir plugins/<name>`, and finish with the `plugin-consistency` skill.

### When Writing Skills

- Description: what it does and when to use it, third person, at most about 500 characters, with specific trigger phrases.
- Body: headers, numbered steps and bullets; under 500 lines and about 5,000 tokens, following [agentskills.io best practices](https://agentskills.io/skill-creation/best-practices):
  - Each line is something the model would get wrong without it. The main path stays in `SKILL.md`; situational paths go to `references/` with a "read when …" trigger. Leave layout and rare cases to the model.
  - Be prescriptive only where the task is fragile (exact commands, sequences, formats); elsewhere state the goal and why.
  - Give one default with a short escape hatch, not a menu.
  - Include a short input and output example, and a template for any output that must keep its shape.
- Word guidance that needs judgment for the whole task ("after every edit", not "once").
- Links: from `SKILL.md`, relative to the skill folder; from a file under `references/`, relative to that file and only to templates, such as `[template](../assets/template.md)`. References never link to each other and stay one level deep.
- Use `${CLAUDE_PLUGIN_ROOT}/...` for other files of the plugin. Never reference a file outside the plugin, and never use `../` to leave the skill folder: the install copies only the plugin.
- Audit every skill with `/skill-diagnostics:audit` after writing it and again after any rewrite: slimming can drop a load-bearing rule. Install the skill-diagnostics plugin from this marketplace when the command is missing.

### When Writing Hooks

Work through these in order: declare, filter, decide, fail, test, document. Do not propose or build a hook that reminds Claude to invoke an LSP intelligence skill before the first edit until Nery reports skipped skills: recall memory `deferred-pretooluse-skill-reminder`.

#### Declare

- Use the three levels of `hooks/hooks.json`: event, matcher group, handler. The input is JSON on stdin. Never write a `"hook"` object or read `$TOOL_INPUT`.
- Write the command in shell form with the placeholder in double quotes: `"command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/<script>\""`. Exec form (`args`) needs a real `.exe` on Windows, and Windows runs only through Git Bash here.
- Set `timeout` on every handler. A command hook defaults to 600 seconds.
- A matcher of letters, digits, `_`, `-` and `|` is an exact tool-name match. `Bash` does not cover `PowerShell`.
- Resolve `node` and `tsc` across every Node manager: plugin hooks and LSP servers get no shell profile.

#### Filter

- Never put `if` on a hook that enforces a policy. The hooks page calls the filter best-effort: it strips leading `VAR=` assignments, and the permissions page strips only `timeout`, `time`, `nice`, `nohup`, `stdbuf`, `command`, `builtin` and `noglob`. Treat `sudo`, `env`, `xargs`, `watch` and `bash -c` as not stripped until a test shows otherwise, so `if: "Bash(git *)"` would skip `sudo git commit --no-verify`.
- Filter inside the script instead, on the words after lexing, never on the raw text. The shell joins quotes, so `g"i"t commit --no-verify` runs git and contains no `git` substring. Parsing costs far less than starting the interpreter.
- Where `if` is allowed, write one permission rule per field. A rule joined with `|` never matches.

#### Decide

- To block, print one JSON object on stdout and exit 0: `hookSpecificOutput.hookEventName` `"PreToolUse"`, `permissionDecision` `"deny"`, and a `permissionDecisionReason` that tells Claude what to do instead. Exit 2 with a reason on stderr also blocks. Exit 1 never blocks.
- Print nothing else on stdout. A second line turns the output into plain text or a parse failure.
- To pass a call, print nothing and exit 0. Silence leaves the decision to the permission flow; it never approves.
- A guard that cannot read or parse its own input denies the call and says why.
- Hooks that match one event run in parallel, and the strictest decision wins: `deny`, then `defer`, `ask`, `allow`.

#### Fail

- Set `"onFailure": "block"` on a check hook, so a broken hook never passes in silence. Declaring `onFailure` makes Claude Code 2.1.295 the plugin's minimum: older versions let a hook that cannot start pass the call.
- A hook that runs an interpreter starts from a launcher script, which checks the interpreter and its minimum version first. When either is missing, it prints `systemMessage` and `additionalContext` and exits 0, because with `"onFailure": "block"` a missing interpreter would block every call, not only the guarded ones.
- A guard whose job is to deny is the exception: when its tool is missing it denies the commands it guards and says what to install.
- Past those checks, a crash, a timeout or an exit code other than 0 or 2 blocks. That is the intent.

#### Test

- A hook in `settings.json` loads on save, with no restart; a plugin hook needs `/reload-plugins`. Test right after each edit.
- Run the script with `env -i`, an empty `HOME` and a minimal `PATH` for each Node manager.
- Test one call made from a subagent before the README says the hook covers them: plugin hooks run inside subagents, and the input carries `agent_id` and `agent_type`.
- Test in `default` and in `bypassPermissions` mode before the README states what the hook blocks: the docs do not say it runs in both.

#### Document

- Under Limitations in the README, name what the hook does not reach:
  - a tool the matcher leaves out, such as the PowerShell tool when `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` turns it on;
  - the policies that turn hooks off, `allowManagedHooksOnly` and `disableAllHooks`;
  - the surfaces where it does not run, per [compatibility](../../docs/compatibility.md).
- State that a hook is a barrier for Claude, not a security boundary, and that it never sees what a person types in their own terminal. The docs say to enforce a hard allow or deny through permissions.

### When Writing Evals

- Plugins get evals by default; Nery decides which plugins skip them. Write evals only for a plugin he approved.
- Never work from memory: load the plugin-evals skill, use the Claude Code Docs MCP tools, and read the Claude Code changelog for the installed version, the four before it and every newer one. Apply what changed. Never invent or assume a format or behavior.
- Cases run in `dontAsk` mode, so writes under `.claude/` are denied and `userConfig` cannot be set: grade the attempt and the reply. Recall memory `plugin-eval-dontask-mode`.
- Give the plugin an entry in `.github/scripts/evals-config.json`: the tools the cases need, `max_cost_usd` and the `cost_basis` it was measured from.
- Run `run-evals.sh` only on Nery's request: it spends money. CI runs the suite only for plugins with an `evals/` folder that changed.
- A plugin without evals is tested with the methods the official docs recommend for its component types.

### When Writing User Docs

Applies to the root `README.md`, `docs/`, every plugin `README.md`, `SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md` and the templates.

- READMEs sell: lead with the outcome and why to install, then teach. Never mention maintenance, `.claude/`, internal scripts, CI internals or how we work.
- In a plugin README, resolve every `{{…}}` and `<!-- TODO -->` of the template, delete rows and sections that do not apply but keep every required section, keep exactly one Compatibility row per component type the plugin ships, and give an outcome-first TL;DR with real usage examples.
- The Version badge reads `version` from `plugin.json`. Never hardcode a version in it.
- List every prerequisite with how to install it and its alternatives, and every network call the plugin makes.
- English, second person, active voice, present tense, short sentences. Benefit first, mechanics second.
- Emoji-prefixed `##` headings, one emoji per heading, consistent across docs (📥 install, 🔧 manage, 🧭 compatibility, 🩺 troubleshooting, ❓ FAQ, 🔄 update, 🗑️ uninstall, 📝 changelog, 📄 license).
- Badges in the hero only: shields.io, brand color `D97757`.
- Tables for comparisons, commands per surface, requirements and options.
- GitHub alerts (`> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`), never two back to back without text between.
- `<details>` for per-surface instructions and FAQs, with the most common option `open`.
- **Bold** for UI labels exactly as shown in the app (`/plugin` → **Installed** → **Update now**); *italics* for emphasis or terms.
- Relative links inside the repo; absolute `https://` links outside.
- State the minimum version of every version-gated feature (e.g. "v2.1.292+").

### When Changing a Plugin

After every change inside `plugins/<name>/`, in the same PR:

1. Read the plugin's README and make it match the plugin as it now is: add what the change made missing and remove what it made obsolete.
2. Record the change in the plugin's `CHANGELOG.md` under `## [Unreleased]`, in detail. Each plugin changelog tells the plugin's full story.
3. Decide the bump per When Versioning and Releasing a Plugin.
4. When the change is a version bump, a launch, a removal, a migration or a consolidation, add one short line to the root `CHANGELOG.md`.

Changelog format (Keep a Changelog 2.0.0):

- User-facing language: what changed for the user, not implementation detail. Reference issues as `(#12)`.
- Mark breaking entries with a leading `**Breaking:**` inside their change type.
- The root `CHANGELOG.md` is a summary, never a copy of a plugin changelog. It is grouped by date, newest first, one line per change: `- **plugin-name** 1.2.0 — one-line summary.` Create the `## YYYY-MM-DD` heading when it is missing, with `### Added`, `### Changed` and so on below it.

### When Versioning and Releasing a Plugin

Every time you bump, rename, remove or release a plugin, or decide whether a change needs a new version:

- A change inside `plugins/<name>/` other than its README, to be released.
- A rename or removal of a plugin, or a move to `1.0.0`.
- A question about which version a change carries.

Do this:

1. Invoke the `release-and-versioning` skill with the Skill tool as soon as the case arises, and follow it until its last step.
2. Pick the bump from what changes for the user, and record the change in the plugin's `CHANGELOG.md` under `## [Unreleased]` first.
3. Bump only with `bump-version.mjs` in the plugin's PR, add the root `CHANGELOG.md` line, and never tag by hand.
4. After Nery merges, confirm the release run, the tag and the GitHub Release, and close the fixed issues.

### When Reviewing a Plugin

After building or changing a plugin, before its release. Delegate it to a read-only subagent (the `Explore` type: no Edit or Write) that did not write the plugin. It assumes nothing works until it sees evidence. It loads no CLAUDE.md, rule file or memory, so the delegation message carries the plugin name, these steps and every rule or fact they need: recall memory `agent-file-rules`. The same applies to every delegated audit or check below.

1. Read `.claude/rules/WORKFLOW.md`, `docs/compatibility.md`, the checks in `.github/scripts/check-repo.mjs` and everything under `plugins/<name>/`.
2. Run `claude plugin validate --strict plugins/<name>` and `node .github/scripts/check-repo.mjs`, and quote the output.
3. Manifest: the fields `.claude/skills/plugin-development/SKILL.md` → step 4 sets; paths start with `./`; secrets go through `userConfig`; no hardcoded tokens or personal data.
4. Components: each skill, agent, hook, MCP and LSP server does what the README claims; skill descriptions state what and when; hook scripts fail safe; paths use `${CLAUDE_PLUGIN_ROOT}`.
5. Security: no data exfiltration, no undisclosed network calls, no destructive commands without confirmation, no `curl | sh`, least-privilege tool grants.
6. Compatibility: the README table matches `docs/compatibility.md` for the components actually shipped (e.g. `bin/` ⇒ ❌ Claude app; agents and hooks ⇒ ⚠️ Cowork sessions only).
7. Docs accuracy: every command, flag, version and UI path in the README exists in the current official docs; usage examples match the real skill names (`/<plugin>:<skill>`).
8. Generic: nothing specific to one person, company or language.
9. Changelog: the current version has an entry that matches the actual changes.
10. Report a verdict (**ready**, **ready after fixes** or **not ready**) and a findings table: severity (blocker, major, minor), file:line, problem, evidence (quoted output or doc URL), fix. Mark anything not verified as **unverified**.

Verify every finding against the files and the live docs before fixing it: reviewers over-report. Then apply the confirmed findings in one coherent pass per file and re-read each touched file and its references: recall memory `apply-fixes-holistically`.

### When Using GitHub

Every time you handle an issue or touch GitHub:

- A user issue arrives or is open: read, reproduce, label, reply, fix.
- A commit, branch, push or PR: create, change or carry any of them.
- A failed job, a review comment or a Dependabot alert on a PR.
- A request from Nery for CI work.

Do this:

1. Invoke the `github-workflow` skill with the Skill tool as soon as the case arises, and follow it until its last step.
2. Confirm an issue before you claim anything about it, and verify each review finding against the files and the docs before acting on it.
3. Fix the root cause and commit; never post, label, close, push, open a PR or merge on the marketplace's behalf without Nery's order.
4. Carry the PR until every job is green and no review is open, stop at ready to merge, and wait for his green light.

### When Keeping Docs Consistent

Every time you create, edit or remove any of these:

- A file under `plugins/<name>/`: a component, `plugin.json`, the README or the CHANGELOG.
- The root `README.md` or `CHANGELOG.md`, a file in `docs/`, `.claude-plugin/marketplace.json`, a template, or a community file (`SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, an issue template).
- A pinned tool or Claude Code version in the workflows or in `.claude/CLAUDE.md` → Commands.

And every time before a release, or when Nery asks for a drift or freshness check, over the whole repo.

Do this:

1. Invoke the `plugin-consistency` skill with the Skill tool as soon as you touch the file, and follow it until its last step.
2. Find what the change touches and which files must agree with it.
3. Run the repo's check scripts, compare both sides of every pair, and confirm the claims the change added against live sources.
4. Fix each disagreement in the same change, asking Nery where the right value is a decision, and rerun until clean. Report the raw output.
