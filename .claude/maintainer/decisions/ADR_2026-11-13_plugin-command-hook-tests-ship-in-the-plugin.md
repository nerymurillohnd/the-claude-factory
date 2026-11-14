---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Tests of a plugin's command hooks live in the plugin and use only the standard library

## Scope

The tests of the `command` hooks that plugins under `plugins/<plugin>/hooks/` ship. Out of scope:
- mods, whose `*.test.ts` and `*.test.tsx` files already live in `plugins/<plugin>/tests/` and run with `claude plugin test`;
- the maintainer scripts' tests in `scripts/testers/`;
- the npm script or CI job that will run the hook tests, still to be designed.

## Context and problem statement

No plugin's command hooks have automated tests yet. A pull request from another session (nerymurillohnd/the-claude-factory#106) put hook tests in the maintainer scope, where they ran with the maintainer's Python and `PATH`. That was review finding 11, left to the owner.

Research in this session found the following:
- The official hooks guide tests a hook by piping its input JSON into the script and reading the exit code.
- No official framework for unit-testing command hooks is documented.
- Anthropic's own `security-guidance` plugin keeps its hook tests inside the plugin (`plugins/security-guidance/tests/`). They use pytest.
- The old CLAUDE.md asked for plugin testing "with the plugin's own testing methods, in isolated environments that do not depend on the maintainer's tools or versions". The promoted CLAUDE.md lost that clause (ADR_2026-11-13_claude-configuration-architecture-on-the-owners-claude-md, More information).

Where should a plugin's hook tests live, and what may they depend on?

## Decision drivers

- A plugin is self-contained and depends on nothing specific to the maintainer's machine (`.claude/rules/plugins.md`).
- The tests run each hook the way Claude Code runs it.
- One place per kind of test, the same way mods already work.

## Considered options

- **In `plugins/<plugin>/tests/`, standard library only, each test running the hook as a subprocess with its input JSON on stdin**: chosen.
- **In `scripts/testers/`, run with the maintainer Python through `uv run`**: rejected because the tests would depend on maintainer tools and versions, and would not travel with the plugin.
- **No automated tests, only piping a sample input by hand**: rejected because nothing would catch a regression before a release.

## Decision outcome

Chosen option: **tests in the plugin, standard library only**, because they keep the plugin self-contained and follow Anthropic's own plugin layout. They also test the hook through the same interface Claude Code uses. The standard library replaces the pytest of Anthropic's example, so that the tests need nothing installed. `.claude/rules/testing.md` (Command hooks) states the rule.

### Consequences

- Good, because the tests ship with the plugin and run on any machine the plugin supports.
- Good, because the location matches the mods' `tests/` folder.
- Bad, because the tests ship to users' caches, adding files they do not run.
- Bad, because no npm script or CI job runs these tests yet, so until one exists each run is manual.

## More information

- Decided by the owner on 2026-11-13, by approving the Testing bullet "Plugins with command hooks" of the Stack section and its rule.
- Pending:
  - the runner for these tests (an npm script and the pull-request workflow);
  - moving the tests of nerymurillohnd/the-claude-factory#106 into the plugin, if that pull request goes ahead.
- Sources:
  - [Hooks guide](https://code.claude.com/docs/en/hooks-guide), testing a hook by piping JSON into it;
  - the `anthropics/claude-code` repository, `plugins/security-guidance/tests/`.
- Related: ADR_2026-11-13_claude-md-points-each-stack-area-to-its-rule.
