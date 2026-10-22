# How to Work With Nery in This Project

## Rules by Task

Each section below applies to one kind of work. Follow the section for the task at hand before you start it. Skill triggers and quality apply to all of it; then come the sections of a plugin's life: create, skills, evals, user docs and review. Commands live in `.claude/CLAUDE.md` → Commands.

A line that says "Recall memory `<name>`" points to a verified fact or a past correction: read `<name>.md` in the project memory (`.claude/memory/`) before you act on that step. Cross-project lessons live in `~/.claude/LESSONS.md`, which `.claude/CLAUDE.md` already loads.

### Skill Triggers

Every time one of these cases arises, invoke the skill with the Skill tool before you act, and follow it to its last step. The skill holds the full procedure; do not work from a memory of it.

| Every time you ... | Invoke |
| :-- | :-- |
| Scaffold, create, edit or remove a plugin file (a component, a script, `plugin.json`, `LICENSE`, `NOTICE.txt`, the README or the CHANGELOG), or receive one from Nery in his own version | `plugin-development` |
| Write or review a plugin hook, its script, its launcher, its tests or the README text about what it blocks | `plugin-hooks-guidance` |
| Add or edit an MCP server, its `userConfig`, or an agent that uses its tools | `plugin-mcp-guidance` |
| Change a plugin, the root `README.md` or `CHANGELOG.md`, `docs/`, `marketplace.json`, a template, a community file or a pinned version; and, over the whole repo, before a release or on a drift or freshness check | `plugin-consistency` |
| Bump, rename, remove or release a plugin, or decide which version a change carries | `release-and-versioning` |
| Handle an issue, commit, branch, push, PR, review comment, failed job, Dependabot alert, or a request for CI work | `github-workflow` |

The skills hand off to each other, and each lists its own hand-offs in a section of that name. The usual order is `github-workflow` → `plugin-development` (→ `plugin-hooks-guidance` for a hook, `plugin-mcp-guidance` for an MCP server or agent tools) → `plugin-consistency` (→ `release-and-versioning` for a bump or a changelog) → back to `github-workflow` for the PR and the merge. To invoke is to start a skill with the Skill tool; a skill that ends hands back to the one that invoked it, and never re-invokes its caller. When two apply to one change, `github-workflow` governs every push, PR and merge, `release-and-versioning` governs versions and tags, and `plugin-consistency` always runs last before a change is called ready.

Whatever the skill, confirm before you claim, verify each review finding against the files and the docs before acting on it, never post, label, close, push, open a PR, merge, tag or publish without Nery's order, and report the raw output of every check.

### When Checking Quality

Applies to every task.

1. After you edit, write or create a `.py`, `.mjs`, `.ts` or `.sh` file, run the commands for its type in Commands → After Editing a File, right away and before the next task, in this order: formatter, linter, type checker, tests.
2. Pass each strict `tsc` flag with an explicit value: `--strict` does not override an explicit `false` in a tsconfig. Before the first edit of a `.ts`, `.mts`, `.js` or `.mjs` file in a task, tests and scratch scripts included, invoke the TypeScript lifecycle skill (`typescript6-lsp-intelligence:ts-lifecycle`); the post-edit `tsc` hook is not that skill.
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
   - Category: an `id` from `scripts/categories.json`.
   - Components: skills, agents, hooks, MCP, LSP, output styles, monitors, scripts, each justified by a user task.
   - Surfaces: Claude Code and the Claude app by default. Check every component against `docs/compatibility.md`; if a part forces Claude Code-only, say why and get Nery's OK.
   - Requirements: CLIs, accounts, API keys (`userConfig`), dependencies, minimum Claude Code version.
   - Evals: ask Nery whether the plugin gets them (When Writing Evals).
   - Sources: the current official docs for every component type used, with their version-gated features.
2. Scaffold with `new-plugin.mjs`. Pass `--claude-code-only` only when the brief approved it. It creates `plugins/<name>/` with the manifest, README, CHANGELOG and LICENSE, registers the marketplace entry and regenerates the catalog.
3. Build the components with the skills in Skill Triggers and per When Writing Skills. Exercise each one while you build with `claude --plugin-dir plugins/<name>`.
4. Write the README per When Writing User Docs, starting from the scaffolded template.
5. Fill `CHANGELOG.md` → `## [0.1.0]` → `### Added` with what ships, and add `- **<name>** 0.1.0 — <summary>.` under `### Added` in today's heading of the root `CHANGELOG.md`. Move that line to the merge day if the PR merges on a later day.
6. Write the evals when Nery approved them (When Writing Evals).
7. Stop and tell Nery the plugin is built. While he is still shaping it, run only the cheap checks each edit needs, and do not run or announce live tests, the full gate sequence or the plugin review: recall memory `no-unrequested-verification-while-designing`. Run the closing checks only once he says it is ready:
   - every step of Before Every Push passes;
   - the plugin review passes (When Reviewing a Plugin) and every confirmed finding is fixed;
   - Nery runs the Claude app check in a Cowork session and a chat conversation, unless the plugin is Claude Code-only.
8. Open the PR with the `github-workflow` skill. After the first push, run `sync-labels.mjs` to create the `plugin: <name>` label.
9. Hand off: what was built, the raw gate output, the surfaces tested and the release step (the `release-and-versioning` skill).

### When Writing Skills

Plugin skills ship to users and follow the rules below. Skills that only govern work on this repository, in `.claude/skills/`, follow "Project skills" at the end of this section.

- Description: what it does and when to use it, third person, at most about 500 characters, with specific trigger phrases.
- Body: headers, numbered steps and bullets; under 500 lines and about 5,000 tokens, following [agentskills.io best practices](https://agentskills.io/skill-creation/best-practices):
  - Each line is something the model would get wrong without it. The main path stays in `SKILL.md`; situational paths go to `references/` with a "read when …" trigger. Leave layout and rare cases to the model.
  - Be prescriptive only where the task is fragile (exact commands, sequences, formats); elsewhere state the goal and why.
  - Give one default with a short escape hatch, not a menu.
  - Include a short input and output example, and a template for any output that must keep its shape.
- Word guidance that needs judgment for the whole task ("after every edit", not "once").
- Links: from `SKILL.md`, relative to the skill folder; from a file under `references/`, relative to that file and only to templates, such as `[template](../assets/template.md)`. References never link to each other and stay one level deep.
- Use `${CLAUDE_PLUGIN_ROOT}/...` for other files of the plugin. Never reference a file outside the plugin, and never use `../` to leave the skill folder: the install copies only the plugin.
- Audit every plugin skill with `/skill-diagnostics:audit` after writing it and again after any rewrite: slimming can drop a load-bearing rule. Install the skill-diagnostics plugin from this marketplace when the command is missing.

#### Project skills

- Frontmatter holds only `name` and `description`: one sentence, at most 120 characters.
- Body, in this order: title; context in two or three sentences; role; rules; gotchas (only facts the model would get wrong without them); the workflow as a checklist with one short line per step; the details of each step.
- Be exact where the task is fragile (commands, sources, formats); where several methods work, state the goal and why. Write procedures, not declarations, and add a validation loop where the skill produces claims.
- Never write a `${CLAUDE_*}` variable literally in the body: Claude Code substitutes it when the skill loads.
- Pair every project skill with a trigger section in this file: "Every time you ...", four steps, the first of which invokes the skill.
- Before relying on a skill, dry-run it with a read-only subagent on a realistic scenario and fix the gaps. A new skill loads only after the session restarts.

### When Writing Evals

- Plugins get evals by default; Nery decides which plugins skip them. Write evals only for a plugin he approved.
- Never work from memory: load the plugin-evals skill, use the Claude Code Docs MCP tools, and read the Claude Code changelog for the installed version, the four before it and every newer one. Apply what changed. Never invent or assume a format or behavior.
- Runs never ask for permission: a tool you did not grant is removed, Bash writes stay in the run's workspace, no `.claude/` directory loads (not even one a `scaffold_script` wrote), and the temporary home has no `userConfig` values. Grade the attempt and the reply. Source: `/en/plugin-evals` → "Grant tools" and "How runs are isolated".
- Give the plugin an entry in `scripts/evals-config.json`: the tools the cases need, `max_cost_usd` and the `cost_basis` it was measured from.
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

### When Reviewing a Plugin

After building or changing a plugin, before its release. Delegate it to a read-only subagent (the `Explore` type: no Edit or Write) that did not write the plugin. It assumes nothing works until it sees evidence. It loads no CLAUDE.md, rule file or memory, so the delegation message carries the plugin name, these steps and every rule or fact they need: recall memory `agent-file-rules`. The same applies to every delegated review.

1. Read `.claude/rules/WORKFLOW.md`, the pairs map in `.claude/skills/plugin-consistency/SKILL.md` → step 2, `docs/compatibility.md`, the checks in `scripts/check-repo.mjs` and everything under `plugins/<name>/`.
2. Run `claude plugin validate --strict plugins/<name>` and `node scripts/check-repo.mjs`, and quote the output.
3. Manifest: the fields `.claude/skills/plugin-development/SKILL.md` → step 4 sets; paths start with `./`; secrets go through `userConfig`; no hardcoded tokens or personal data.
4. Components: each skill, agent, hook, MCP and LSP server does what the README claims; skill descriptions state what and when; hook scripts fail safe; paths use `${CLAUDE_PLUGIN_ROOT}`.
5. Security: no data exfiltration, no undisclosed network calls, no destructive commands without confirmation, no `curl | sh`, least-privilege tool grants.
6. Compatibility: the README table matches `docs/compatibility.md` for the components actually shipped (e.g. `bin/` ⇒ ❌ Claude app; agents and hooks ⇒ ⚠️ Cowork sessions only).
7. Docs accuracy: every command, flag, version and UI path in the README exists in the current official docs; usage examples match the real skill names (`/<plugin>:<skill>`).
8. Generic: nothing specific to one person, company or language.
9. Changelog: the current version has an entry that matches the actual changes.
10. Report a verdict (**ready**, **ready after fixes** or **not ready**) and a findings table: severity (blocker, major, minor), file:line, problem, evidence (quoted output or doc URL), fix. Mark anything not verified as **unverified**.

Verify every finding against the files and the live docs before fixing it: reviewers over-report. Then apply the confirmed findings in one coherent pass per file and re-read each touched file and its references: recall memory `apply-fixes-holistically`.
