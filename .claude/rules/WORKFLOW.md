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
9. Hand off: what was built, the raw gate output, the surfaces tested and the release step (When Releasing).

### When Writing Plugins

Scope:

- Cover the plugin's whole domain in one install, and build each part as simply as it can be while staying safe, stable and efficient in Claude Code. Every component earns its place with a user task no other component of the plugin covers.
- Build for any user of the public marketplace, never for Forestal MT, Nery's machine or the tools he uses. Nery's machine is a test bench, never a finding: recall memory `plugins-are-for-third-parties`.
- When Nery hands over his own version of a plugin file, edit his file in place, and copy it into the plugin only after he reviews it and says so: recall memory `stage-external-plugin-files`.
- A required tool, dependency, account or integration never rules a plugin out: it becomes a prerequisite in the README, with how to install it and its alternatives.
- Read the official docs for each component type before you write it.

Files:

- Every plugin ships `LICENSE`, `CHANGELOG.md` and `README.md`.
- A plugin that bundles, derives from or wires in third-party material or integrations also ships `NOTICE.txt`: the plugin's copyright and license, then each third-party source with its repository, version or commit, license and the files derived from it.
- Keep `version` in `plugin.json`, at `0.1.0` for the first release, and add `keywords`. Never set `version` on a marketplace entry. Change `displayName` to relabel a plugin.
- Name each skill for what it does, not how it is implemented.
- Declare hooks in `hooks/hooks.json`. A plugin agent's frontmatter `hooks` is ignored.
- Give a plugin its own `package.json` or Python environment only when its architecture needs one; the plugin's complexity must justify every dependency. Set it up the way the current plugins reference says, and ship Node dependencies only with an npm or Bun lockfile: other lockfiles leave no `node_modules`.
- After moving or creating files, delete `.DS_Store` files and orphaned cache directories.
- Keep `metadata` in `plugin.json` and `onFailure` on hooks even when the claude.ai sync warns about them: recall memory `claudeai-sync-warnings`.

Components:

- Agents: recall memory `agent-file-rules` before writing or editing one, and memory `subagent-skill-preload` before relying on `skills:` in its frontmatter.
- `userConfig` options: recall memory `plugin-userconfig-behavior` for how they behave on install, update and synced copies.
- MCP servers: recall memory `claude-app-plugin-mcp-connector` for how the Claude app connects a plugin's http server, and memory `claude-code-desktop-vs-cli` for `${VAR}` headers that expand empty in the desktop app.
- Mods: recall memory `claude-code-mods-facts` for `register.ts`, static validation, `decider: 'person'`, tests and the type declarations.

Scripts:

- Start with `#!/usr/bin/env <interpreter>` (no version), commit as `100755`, and call by path through `${CLAUDE_PLUGIN_ROOT}` or `${CLAUDE_SKILL_DIR}`.
- Make network calls only when the plugin's purpose requires them, and disclose each one in the README.

Use:

- When Nery uses a plugin for his own work, he installs the marketplace and the plugin like any other user. `--plugin-dir` is only for building and testing.

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
3. Decide the bump per When Versioning a Plugin.
4. When the change is a version bump, a launch, a removal, a migration or a consolidation, add one short line to the root `CHANGELOG.md`.

Changelog format (Keep a Changelog 2.0.0):

- User-facing language: what changed for the user, not implementation detail. Reference issues as `(#12)`.
- Mark breaking entries with a leading `**Breaking:**` inside their change type.
- The root `CHANGELOG.md` is a summary, never a copy of a plugin changelog. It is grouped by date, newest first, one line per change: `- **plugin-name** 1.2.0 — one-line summary.` Create the `## YYYY-MM-DD` heading when it is missing, with `### Added`, `### Changed` and so on below it.

### When Versioning a Plugin

| Bump | When |
| :-- | :-- |
| **major** | Breaking: a removed or renamed skill, agent or command; changed config keys; a new required dependency; a change to behavior users rely on |
| **minor** | A new component, option or capability, backwards compatible |
| **patch** | A bug fix, prompt wording fix, performance gain or internal refactor with the same behavior |

- Stay in `0.x` while a plugin is new; go to `1.0.0` only when Nery declares its interface stable.
- In `0.x`, a breaking change bumps the minor (`0.y.z` → `0.(y+1).0`) and its changelog entry keeps `**Breaking:**`. From `1.0.0` on, breaking means major.
- Bump with `bump-version.mjs` in the plugin's PR; it turns `[Unreleased]` into the dated section. Never edit a version by hand. A change limited to the README needs no bump.
- Never rename or remove a plugin silently: add `"renames": { "old": "new" }` (or `"old": null` for a removal) to `marketplace.json` and note it in the root changelog.

### When Reviewing a Plugin

After building or changing a plugin, before its release. Delegate it to a read-only subagent (the `Explore` type: no Edit or Write) that did not write the plugin. It assumes nothing works until it sees evidence. It loads no CLAUDE.md, rule file or memory, so the delegation message carries the plugin name, these steps and every rule or fact they need: recall memory `agent-file-rules`. The same applies to every delegated audit or check below.

1. Read `.claude/rules/WORKFLOW.md`, `docs/compatibility.md`, the checks in `.github/scripts/check-repo.mjs` and everything under `plugins/<name>/`.
2. Run `claude plugin validate --strict plugins/<name>` and `node .github/scripts/check-repo.mjs`, and quote the output.
3. Manifest: the fields When Writing Plugins sets; paths start with `./`; secrets go through `userConfig`; no hardcoded tokens or personal data.
4. Components: each skill, agent, hook, MCP and LSP server does what the README claims; skill descriptions state what and when; hook scripts fail safe; paths use `${CLAUDE_PLUGIN_ROOT}`.
5. Security: no data exfiltration, no undisclosed network calls, no destructive commands without confirmation, no `curl | sh`, least-privilege tool grants.
6. Compatibility: the README table matches `docs/compatibility.md` for the components actually shipped (e.g. `bin/` ⇒ ❌ Claude app; agents and hooks ⇒ ⚠️ Cowork sessions only).
7. Docs accuracy: every command, flag, version and UI path in the README exists in the current official docs; usage examples match the real skill names (`/<plugin>:<skill>`).
8. Generic: nothing specific to one person, company or language.
9. Changelog: the current version has an entry that matches the actual changes.
10. Report a verdict (**ready**, **ready after fixes** or **not ready**) and a findings table: severity (blocker, major, minor), file:line, problem, evidence (quoted output or doc URL), fix. Mark anything not verified as **unverified**.

Verify every finding against the files and the live docs before fixing it: reviewers over-report. Then apply the confirmed findings in one coherent pass per file and re-read each touched file and its references: recall memory `apply-fixes-holistically`.

### When Auditing User Docs

Before a release or after editing user docs. Delegate it to a read-only subagent, as for the plugin review. Scope: `README.md`, `docs/*.md`, `plugins/*/README.md`, `SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/*`, or only the path it is given.

1. Accuracy: every `claude …` command, `/plugin …` flow, flag, minimum version and app UI path (Customize → Plugins, + → Plugins, `/plugins` in VS Code) matches the current docs at code.claude.com and claude.com, with the source URL.
2. Links: relative links resolve to existing files, anchors exist (markdownlint reports MD051), and external links point to the right page.
3. Style: follows When Writing User Docs.
4. No leakage: no mention of `.claude/`, maintenance scripts, CI internals, the tooling that maintains the repo or internal process.
5. Consistency: marketplace source `nerymurillohnd/the-claude-factory`, install suffix `@the-claude-factory`, the same compatibility matrix everywhere.
6. Selling: each plugin README leads with the outcome and a TL;DR, with no unresolved TODOs.
7. Report a findings table (severity, file:line, issue, evidence or source, suggested wording) and a pass or fail summary per file.

### When Using GitHub

- Every edit to a plugin's `plugin.json`, skills (`SKILL.md` and its files), agents, hooks, `.mcp.json`, `.lsp.json` or dependencies goes through a PR. Everything else goes by direct push or by PR, as Nery decides.
- Push and open a PR only on Nery's order. Label every PR from `gh label list`.
- Before any push of `main`, recall memory `main-holds-unreleased-hook-workbench`: a push can publish and tag a plugin that is not ready.
- Write commit messages and PR bodies through a quoted heredoc and read them back before pushing: the Bash tool runs zsh. Recall memory `zsh-modifiers-in-shell-strings`.
- When a push fails with a broken pipe while fetch works, retry once with HTTP/1.1: recall memory `github-push-http1-workaround`.
- PR review runs through the Claude workflows in `.github/workflows/`, not a managed review service: recall memory `claude-plan-pro-max`.
- When Nery asks for CI work, offer the open CI items one by one before anything new: recall memory `ci-simplify-skipped-findings`.

Carry a PR to merge in this order:

1. Read the failed jobs and every review, from Claude and from third parties.
2. Verify each finding against the files and the docs before acting on it.
3. Fix the root cause and commit. Push the fix only with Nery's OK.
4. Reply to each review and resolve it.
5. Repeat until every job is green and no review, issue or failed job remains.
6. Stop at ready to merge, tell Nery, and wait for his green light.

### When Releasing

- The plugin PR carries the release: the bump from `bump-version.mjs`, the notes under the new version, and the root `CHANGELOG.md` line. There is no separate release commit.
- Reference fixed issues as `Refs #n`, never `Closes #n`: issues close in the release step.
- Never tag by hand: `release.yml` tags after Validate passes on `main`.

Right after the merge:

1. `gh run list --workflow release.yml --branch main --limit 1` - Read the release run that follows the merge.
2. `gh release view <plugin>--v<version>` - Confirm the tag and the GitHub Release exist.
3. If Validate failed, fix the cause first. Run `gh workflow run release.yml` only when Validate passed and no release run exists.
4. For each fixed issue, per When Handling Issues: comment that the fix is released, label it `status: released`, and close it.

### When Handling Issues

- Nery and Claude Code are the only developers and maintainers. The marketplace has no outside collaborators, and pull requests from users are not accepted.
- Users report through issues. For each one:
  1. Reproduce it, or confirm the report against the code and the current docs.
  2. Label it and draft the reply in English.
  3. Fix the confirmed cause in a PR that references it as `Refs #n`.
  4. Ship the fix in a release, then report on the issue what was fixed.
- Post a reply, label or close an issue only after Nery approves it: it speaks for the marketplace in public.

### When Checking Docs Drift

Only when Nery explicitly asks for a drift or freshness check. Delegate it to a read-only subagent; it reports with evidence and edits nothing unless asked.

1. Gather current facts from live sources only:
   - Claude Code changelog: `/en/changelog` in the Claude Code Docs MCP (or <https://code.claude.com/docs/en/changelog>), every release since `CLAUDE_CODE_VERSION` in `.github/workflows/validate.yml`.
   - Plugin docs: `/en/plugins/*` (install, marketplace-reference, manifest-reference, publish, host-marketplace, troubleshooting).
   - Cross-surface support: <https://claude.com/docs/plugins/platform-support>, <https://claude.com/docs/cowork/guide/plugins>, <https://support.claude.com/en/articles/13837440-use-plugins-in-claude>, <https://support.claude.com/en/articles/16761823>, the Claude app release notes (<https://support.claude.com/en/articles/12138966-release-notes>) and the Claude Desktop changelog (<https://claude.com/docs/cowork/changelog.md>).
   - Latest versions: `npm view @anthropic-ai/claude-code version`, `npm view markdownlint-cli2 version`, and the latest tags of `actions/checkout`, `actions/setup-node` and `rhysd/actionlint`.
2. Compare them against the repo:
   - commands, flags, UI paths and minimum versions: `README.md`, `docs/*.md`, `.claude/templates/plugin/README.md`;
   - the compatibility matrix: `README.md`, `docs/compatibility.md`, `.claude/templates/plugin/README.md`, every `plugins/*/README.md`;
   - manifest and marketplace fields, reserved names: `.github/scripts/lib.mjs`, `check-repo.mjs`, the templates;
   - pinned versions: `.github/workflows/*.yml` and `.claude/CLAUDE.md` → Commands;
   - new capabilities worth adopting, such as new manifest fields or component types.
3. Report a table (file, line, what it says, what's current, source URL, severity: wrong, outdated or opportunity), then the proposed edits by file and the version bumps they need (a README-only edit needs none).

### When Writing a Handoff

- A handoff carries only work on this repository. Leave out other projects, Nery's machines, accounts and user-level settings, and record a test as done as soon as Nery reports it with evidence: recall memory `handoff-repo-scope`.
