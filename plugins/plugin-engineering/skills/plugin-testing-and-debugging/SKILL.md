---
name: plugin-testing-and-debugging
description: Tests, troubleshoots and debugs Claude Code plugins with the official CLI - claude plugin validate, list, details, eval and eval init, /plugin, /reload-plugins and --plugin-dir - and the documented loading rules. Use when a plugin, marketplace or skills-directory plugin will not install, load, enable, update or run its skills, hooks, MCP or LSP servers; when a copy behaves differently installed than with --plugin-dir; when a plugin keeps loading after being turned off; when reading a plugin error, Errors-tab entry or exit code; when reviewing a plugin or marketplace before publishing; and when writing, running, reading or gating CI on plugin evals and graders. Also use it in cloud sessions and project threads, where plugins load differently. Use it even when the user only pastes an error or says "my plugin doesn't work".
---

# Test, troubleshoot and debug Claude Code plugins

You are the user's plugin test engineer. Three jobs, one discipline:

- **Test**: prove a plugin does what it claims. Files and schema with `claude plugin validate`; behavior with `claude plugin eval`.
- **Troubleshoot**: the user has a message. Find the stage that produces it, the cause the docs give for it, and the fix.
- **Debug**: no message, or the wrong copy, scope or version loaded. Read the loading rules and the state on disk and in settings until one rule explains what happened.

Everything here comes from the official pages "Plugin loading reference", "Troubleshoot plugins", "Test plugins with evals" and "Plugin commands reference" (code.claude.com/docs), checked against Claude Code 2.1.325. Most of it shipped after mid-2026, so do not answer these from memory: read the reference that holds the answer.

## Gotchas

These are the facts that most often turn a reasonable guess into a wrong answer. Read them before the workflow.

**Where the session runs**

- In a cloud session (`CLAUDE_CODE_REMOTE=true`) the repository's `enabledPlugins` and `extraKnownMarketplaces` are not loaded, nothing from the user's own `~/.claude/` is there, and `/plugin` does not exist. A project's cloud threads load even less: only the repositories' root `CLAUDE.md` files and rules, not their skills, agents, hooks, settings or `.mcp.json`. Plugins reach cloud sessions through the claude.ai account, and threads through **Project settings > Plugins**. `claude plugin` commands run there act on the session's VM, not on the user's machine.

**Loading and copies**

- `--plugin-dir` loads the plugin in place. An install from a marketplace loads a copy under `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`, and nothing outside the plugin directory is copied. "Works with `--plugin-dir`, breaks after install" is almost always a path that reaches outside the plugin (`../shared`) or a source-only file. Paths that escape the plugin root are rejected with `path escapes plugin directory`.
- The manifest `version` wins over the marketplace entry's `version`, and both win over the commit SHA. A pinned `"version": "1.0.0"` keeps every user on the cached copy however many commits follow, and `claude plugin update` prints `<name> is already at the latest version`. Bump it, or leave `version` out of both the manifest and the entry to track commits.
- Nothing on disk or in settings reaches a running session until `/reload-plugins` or a new session. A reload that adds or removes a plugin MCP server or the LSP tool is not applied until `/reload-plugins --force`.
- A `--plugin-dir` plugin with the same manifest name replaces an installed one silently: `claude plugin list` still shows the installed row as enabled, and only the `--debug` log records the override.
- `enabledPlugins` merges key by key across six sources; a higher source wins. A project `true` overrides the user's `false`. To turn a project-enabled plugin off for one person, set it `false` in `.claude/settings.local.json`, not in the committed file.
- A plugin under `.claude/skills/` loads only from the session's primary working directory, never from a parent. Started in a subdirectory, it is simply absent. Managed settings can also skip such folders with no error at all.
- Many causes appear only in the debug log, which `claude --debug` writes to `~/.claude/debug/<session-id>.txt` without printing anything to the terminal. `claude --debug-file <path>` writes it to a path you choose, `--debug=mcp,startup` filters categories (only in the `=` form), and `/debug` turns it on mid-session. `references/messages.md`, "Read the debug log", has the details.
- Skills load from `skills/` at the plugin root. A `skills/` inside `.claude-plugin/` is not scanned. Hook event names are case-sensitive (`PostToolUse`). A shell-form hook with an unquoted `${CLAUDE_PLUGIN_ROOT}` breaks when the path has a space.

**Validation**

- `claude plugin validate` checks files and schema, not behavior. It does not read a `SKILL.md` at the plugin root, does not follow symlinks, and from a marketplace directory does not read the component files of plugins listed in other directories: validate each plugin directory too. Unknown fields and missing frontmatter fail only with `--strict`.
- Validate again after every round of fixes: a warning can hide another. On 2.1.325 a hook under a misspelled event prints `unknown hook event; entry ignored at runtime`, and the unquoted-`${CLAUDE_PLUGIN_ROOT}` warning for that hook appears only once the event name is fixed.
- `engines["claude-code"]` in `plugin.json` (v2.1.323) is a valid field: a plugin outside its stated range is not installed, updated or loaded, and install and update pick the newest version that fits. Check it when a plugin silently refuses to install, update or load on one machine.

**Evals**

- `claude plugin eval` runs real model calls on the user's account. Agree scope and cost before the first run. It is a shell command only; there is no `/plugin` form.
- The default `--threshold` is `1.0`, so any case below perfect exits 1. A run that ends on an API error scores 0 without grading and makes the command exit non-zero, in either arm, even when every case passes.
- `Δ` never changes the exit code. To fail a build when the plugin stops helping, read `aggregates.meanDelta` from the JSON result (`scripts/gate_eval_result.py` does this and refuses partial results). `meanDelta` exists only in a two-arm run, so a CI job that gates on it cannot use `--ablation none`; keep `--ablation none` for quick grader iteration and for suites that gate on score alone.
- Put the target first: `--tag`, `--allow-tools` and `--json` take values, so a target after them is read as their value. Under `--json` or without a terminal an untrusted directory is refused with exit 1 unless `--trust-plugin` is passed.
- In a two-arm run every `tool_used` grader on `Skill` is excluded from the score (`scored: false`). A "must not invoke the skill" check needs `min: 0`, `max: 0` and `arm: both`. Regex graders are JavaScript: use `flags: i`, never `(?i)`. A `files` target lists created paths, not contents. Each run is isolated: no user settings, CLAUDE.md, personal MCP servers or other plugins.
- Real plugin MCP servers do not start in a run. Mock them under `evals/mocks/<server>/<tool>.md`, with `<server>` as named in the plugin's MCP configuration.

## Pick the job

First check where the session runs (`echo "$CLAUDE_CODE_REMOTE"`, and whether the task came from a project). In a cloud session or thread, read `references/environments.md` before anything else: it says what is supposed to load there and where each fix goes.

1. The user has an exact message, an Errors-tab entry or a failing command: troubleshoot. Read `references/messages.md` and search it for the message text.
2. No message, or the wrong copy, scope or version loaded, or a change "did nothing": debug. Read `references/loading.md` and go to the section its symptom list names.
3. The user wants to know whether the plugin works, or is about to publish: test. Use the pre-publish check below, and `references/evals.md` for behavior.
4. A message says `hooks module not loaded` or `hooks module did not load`: the plugin is a mod. Its tests run with `claude plugin test [directory]`; its troubleshooting is at https://code.claude.com/docs/en/plugins/mods/troubleshoot.

## Diagnose: one cause, every place it reaches, one verification

Work from evidence, not from attempts. Changing something and re-running to see what happens hides the cause and leaves its other effects in place.

Progress:
- [ ] 1. Capture the facts: the exact message, the command or action that produced it, the surface (terminal, desktop, VS Code, cloud, `-p`, CI), the directory the session started in, and `claude --version`.
- [ ] 2. Read the state before changing anything: `claude plugin list --json` (look at `id`, `scope`, `enabled`, `installPath`, `errors`, `notes`, `projectEnabled`), `claude plugin details <name>`, `claude plugin marketplace list`, the `/plugin` Errors tab, and `claude plugin validate <dir>` for the user's own plugin.
- [ ] 3. Place it: which stage did the plugin reach (declared in settings, fetched to disk, loaded in the session), and which origin is it (`@<marketplace>`, `@inline`, `@skills-dir`, `@synced`)?
- [ ] 4. Name the cause from the reference entry that matches, quoting the message or rule. When two causes fit, use the state from step 2 to rule one out before going on.
- [ ] 5. Sweep for the cause's other effects: the same cause in other plugins of the marketplace, other scopes, the installed copy and the `--plugin-dir` copy, the other people who clone the repository, CI. One root cause often explains several symptoms the user reported separately.
- [ ] 6. Apply every fix the causes require, in one pass. Say which files change and why, and leave the user's committed files alone when a personal file fixes it (`.claude/settings.local.json`).
- [ ] 7. Apply the change to the session: `/reload-plugins` (with `--force` when it asks), or a new session.
- [ ] 8. Verify once, with what the reference entry says shows once the fix works (an Errors entry gone, `Successfully installed plugin: ...`, `Reloaded:` with no errors line, a skill listed in the details pane). Run the check yourself when you can.

When a fix needs something only the user can do (a terminal they own, an administrator, a credential), say exactly what to run or ask for and what they will see when it worked.

### Report a diagnosis in this shape

```markdown
## Diagnosis
For each problem: symptom → stage and origin → cause, quoting the message or rule and naming the reference section.

## Fixes
Numbered, in the order to apply them, each with the exact file or command and why.

## Also affected
What else the same causes reach, or "nothing else" with the reason.

## Verify
The commands to run once all fixes are in, and what each prints when it worked.
```

## Pre-publish check

Run this before a plugin or marketplace goes to other people.

1. `claude plugin validate <plugin-dir> --strict` for every plugin directory, and `claude plugin validate . --strict` from the marketplace root. Read every error and warning; fix them all, then validate again until it prints none. On 2.1.325 the output also has a "Plugin directory checks" block (README, LICENSE, icon): it matters only for a submission to the plugin directory, and fails the run only with `--profile directory` (from `claude plugin validate --help`; not yet on the docs pages).
2. Check what validation does not read: a `SKILL.md` at a plugin root, symlinked component directories, `skills/` placed inside `.claude-plugin/`, hook matchers, files a script reads outside the plugin (`require('../shared')`), hook scripts that do nothing, and `disable-model-invocation: true` left on a skill Claude should invoke.
3. Load it the way users will: install from the marketplace (a local-path marketplace works for this), start a new session, and check `claude plugin details <name>` lists every skill, agent, hook and server. A `--plugin-dir` test alone does not prove the installed copy works.
4. Measure behavior with evals: at least one case per skill on natural phrasing, one negative case, graders on the result and on the steps (`references/evals.md`).

## Evals in brief

Read `references/evals.md` before writing or running a suite; it holds every field, grader, flag, exit code and result field. The order that keeps cost and noise down:

1. Agree scope and cost with the user, and check `claude --version` (2.1.269 or later) and `git --version` (2.31 or later when git is installed).
2. Create cases with `claude plugin eval init` (interview) or `claude plugin eval init --bare <case>` (blank template, no terminal needed). The templates in `assets/eval-case/`, `assets/eval-negative-case/` and `assets/mock-tool.md` follow the documented format.
3. Give each case a grader on the result (regex over a produced file, or a short `llm` rubric with concrete PASS and FAIL conditions) and one on the steps (`tool_used` or `tool_order`). Add a negative case so the suite does not reward a skill that fires on everything.
4. Iterate graders cheaply with one arm: `claude plugin eval . --case <name> --runs 1 --ablation none`. Confirm any change at the default three runs, with the baseline, before trusting it.
5. Read the report from the top: verdict and tiles, then each case card, then the failed graders' explanations. A `Δ` near zero with the `tool_used: Skill` grader failing means the skill's description does not trigger on the prompt's phrasing: change the description once, based on what the report shows, then run the same suite again.
6. For CI, start from `assets/ci-evals.sh` and gate on the delta with `scripts/gate_eval_result.py`. A suite's files can be checked before any spend: on 2.1.325, a run with no credential still loads every case, prints `N case file(s) failed to load` for broken ones, and stops as partial at $0 (observed behavior, not on the docs pages).

## Where the answers are

- `references/messages.md`: every documented message, by the stage that produces it (where `/plugin` runs, add a marketplace, install, enable and update, installed but not working, build, host, organization policy), plus the conventions all `claude plugin` commands share (exit codes, scopes, `--json` result lines). Read it when there is a message to look up.
- `references/loading.md`: the three stages, origins, `enabledPlugins` precedence, the files under `~/.claude/plugins/`, in-place and copied plugins, versions and updates, name conflicts. Read it when something loaded wrong or not at all with no message, or to explain why.
- `references/evals.md`: running, writing, grading, mocking, CI and reading results for `claude plugin eval`. Read it for any eval work.
- `references/environments.md`: what loads in a cloud session and in a project's cloud thread, how to test and debug there, and where each fix goes. Read it whenever the session is not the user's own terminal.
- `scripts/gate_eval_result.py`: `python3 scripts/gate_eval_result.py results.json --min-mean-delta 0.2` exits 0 when the gate passes, 1 when it fails, 2 when the result is not comparable (partial, or judge graders skipped by the cost ceiling). Standard library only.
- `assets/`: eval case and mock templates, and a CI step.

## Version and source check

Most flags and messages carry a minimum version, written beside them in the references. Before telling the user a flag or message applies, compare it with their `claude --version`. When a reference and the installed build disagree, `claude plugin <subcommand> --help` on that build wins for flags, and the changelog (https://code.claude.com/docs/en/changelog) wins for behavior. Say which you checked.
