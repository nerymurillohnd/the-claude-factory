---
status: superseded
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: ADR_2026-11-13_claude-configuration-architecture-on-the-owners-claude-md
---

# One home per kind of Claude configuration, with a lifecycle skill, a skill gate and owner-only permission rules

## Scope

How this repository organizes Claude's own configuration in the maintainer scope:
- `.claude/CLAUDE.md` and `.claude/WORKFLOW.md`;
- `.claude/rules/`, `.claude/skills/`, `.claude/agents/`;
- `.claude/references/`, `.claude/templates/` and `.claude/architecture/`;
- `.claude/settings.json` (plugins, permissions and hooks).

Out of scope: the content of each plugin under `plugins/`, CI workflows (`validate.yml` stays a separate decision), and the owner's user-level settings.

## Context and problem statement

The 2026-11-13 review (`.claude/maintainer/plans/2026-11-13-claude-architecture-proposal.md`) found these problems:
- **Too much loads every session:** 264 lines, two thirds of them `WORKFLOW.md`, which `CLAUDE.md` imports. Four other files repeat its commands.
- **Duplicated subjects:** version levels, release dates, categories and evals are each written two to four times in rules that load together.
- **Orphaned templates:** `.claude/references/` and `.claude/templates/` are named by no instruction and cite files that do not exist.
- **Nothing enforces the governing skill:** no hook makes Claude load the skill that governs a file before editing it.
- **Prose-only guards:** owner-only actions (push, pull requests, merges, workflow dispatch) are guarded by prose alone.
- **Competing third-party plugins:** synced third-party plugins inject a competing process at session start (`superpowers`) and add about 4,775 always-on tokens of unrelated skill listings.

How should Claude's configuration be organized so that every kind of content has one home, loads when it is needed, and the rules that must never be skipped are enforced?

## Decision drivers

- Claude knows which instruction, rule, skill, agent and hook applies to an idea, a change, a fix or a release, without the owner repeating it.
- One source of truth per kind of content; every other place points to it.
- The maintainer scope and the plugin scope stay separate.
- The right mechanism for each job: CLAUDE.md for what every session needs, path rules for area conventions, skills for procedures, agents for isolated work, hooks and permission rules for what must never be skipped.
- Reuse the installed skills and agents first, build only the gaps.
- Simple enough for a 22-plugin project to maintain.

## Considered options

- **One home per kind of content: a short CLAUDE.md with a routing table, path rules, a new `plugin-lifecycle` skill, a skill gate, ask and deny permission rules, and six synced plugins turned off here**: chosen.
- **Keep `WORKFLOW.md` as an always-loaded import**: rejected. Imports load with the importing file, so the 175-line stage catalog costs context in every session while most tasks use one or two stages.
- **Move the stage procedures to `.claude/maintainer/blueprint.md`, as `.claude/architecture/refactor.md` Appendix F proposed**: rejected. Nothing loads a maintainer document by itself, so Claude would still need a pointer and a procedure; a skill loads on demand and carries both.

## Decision outcome

Chosen option: **one home per kind of content**, because it cuts the always-loaded instructions from 264 to about 100 lines and removes the duplicates. It also turns "load the right skill first" and "only the owner authorizes publishing actions" into configuration instead of prose.

The parts the owner settled on 2026-11-13:
- **Instructions:** CLAUDE.md of about 100 lines, no import, with a task-to-skill routing table.
- **Stage catalog:** `WORKFLOW.md` and the drafts' stage content move to the new `plugin-lifecycle` skill.
- **Templates:** `.claude/references/` and `.claude/templates/` move into that same skill.
- **One lifecycle skill:** the new-plugin procedure is one of its branches, not a second skill (D2).
- **Plugin-scope reviewer:** a new read-only agent, `plugin-release-reviewer` on Opus, checks the plugin-scope safety and portability rules (D8).
- **Skill gate:** project hooks deny an Edit or Write until the skill that governs the file was loaded in the session.
- **Permissions:**
  - `permissions.ask` covers push, pull request creation and merge, workflow dispatch, label apply and tag push;
  - `permissions.deny` covers hand edits of `uv.lock` and `package-lock.json`.
- **Synced plugins turned off in this repository:** `superpowers`, `cloudflare`, `feature-dev`, `svelte-development`, `tailwind-development` and `pdf-viewer`.
- **Where maintainer changes are made:** plain cloud sessions or the terminal; Claude Projects threads are for coordination and research (D7). Project skills do not load in those threads, and project hooks run only in single-repository sessions.

### Consequences

- Good, because the always-loaded instructions shrink and each subject has one home.
- Good, because the gate and the permission rules hold whether or not Claude remembers a line of prose.
- Good, because removing the six synced plugins here takes out the competing session-start mandate and about 4,775 always-on tokens (`claude plugin details`, 2026-11-13).
- Bad, because the gate adds one step to small edits: the governing skill must be loaded first.
- Bad, because the gate relies on the Skill tool's hook input, whose schema is not documented. Step 3 of the migration captures a real sample before relying on it.
- Neutral, because the migration runs in eight short steps, each with its own checks and undo, so the old and new homes coexist until each step lands.

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Ask rules skipped | In `bypassPermissions` mode (unverified) | Owner-only actions run without a prompt | Don't use bypass mode in this repository | Nery |
| GitHub MCP tool names differ on the owner's machine | A local server with another name | The MCP ask rules don't match, with no warning | Check `/permissions` and the tool names on the owner's machine | Claude |
| A lost instruction during the CLAUDE.md rewrite | Step 5a | A rule silently disappears | Keep-migrate-delete table plus the `instruction-engineering:reviewer` agent | Claude |

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The six synced plugins are off here | `claude plugin list --json`, filtered to the six ids | pending (migration step 1) | After each claude.ai plugin change |
| Owner-only actions prompt | `git push --dry-run` raises a permission prompt | pending (migration step 1) | After a Claude Code upgrade |
| Hand edits of the lockfiles are refused | An Edit of `uv.lock` is denied | pending (migration step 1) | After a Claude Code upgrade |
| The always-loaded instructions are at most 110 lines | The instruction checker's "Loaded at launch" line | pending (migration step 5a) | Each change to CLAUDE.md |

## More information

- **Decided:** by the owner on 2026-11-13, by approving the recommendations for decisions D1–D8 in the proposal.
- **Source:** the proposal holds the findings, the target tree, the gate design and the eight migration steps.
- **D4 is not a change:** `skill-diagnostics` keeps `on_skill_write: gate`, because `pluginConfigs` is read only from user and managed settings ([settings-reference: pluginConfigs](https://code.claude.com/docs/en/settings-reference#pluginconfigs)), so a repository cannot set it.
- **D5 waits for step 7:** keeping `autoMemoryDirectory` and linking its path to the checkout in cloud sessions is recorded only when it is implemented. The installed build's settings schema says this key is "Ignored if set in projectSettings", while the memory docs say project settings honor it under workspace trust. That conflict must be settled first.
- **D6 needs no record:** the rewording of `CLAUDE.md:65` lands with step 5a.
- **D3 has its own record:** ADR_2026-11-13_changelog-only-changes-take-no-version-bump.
