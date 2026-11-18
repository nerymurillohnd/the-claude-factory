# Where an instruction belongs

Decide placement before wording. A well-written line in the wrong home either costs context on every unrelated task, misses the tasks that need it, leaks into other people's sessions, or pretends to enforce what only configuration can enforce.

## The admission test

Keep a candidate instruction only if every answer supports it:

0. **Would Claude act differently if this line did not exist?** Ask it for the main session and for the subagents that receive these files. If the answer is no, the line only costs context and attention on every task: flag it for removal, whether or not the user asked for a review, and let the user decide. Lines that usually fail this test:
   - knowledge from training: language and framework idioms, generic virtues ("write clean, maintainable code", "use meaningful names", "handle errors properly", "follow best practices", "be careful");
   - facts derivable from the code or its config: stack, directory layout, dependency lists, formatter and linter settings, what a script does. Check, do not assume: open the manifest (package.json, pyproject.toml) and the formatter or linter config (biome.json, .prettierrc*, .editorconfig, ruff, rustfmt) before keeping a stack sentence or a style line; a style line the formatter enforces only adds drift risk (the checker reports these as `formatter-enforced`);
   - behaviors Claude Code already enforces or performs by default: reading a file before editing it (the Edit tool requires a prior read); lines that only restate Claude Code's built-in commit and PR guidance. Team-specific commit or PR conventions are not no-ops: keep them in prose, and turn off the built-in guidance with `includeGitInstructions: false` (which also drops the git status snapshot) and set `attribution` when they conflict;
   - workflows Claude discovers on its own in every session (find the tests, run them after a change) when the line adds no project-specific command or exception.
   Treat other "Claude probably does this anyway" lines (explore before changing, ask before risky commands) as candidates to confirm with the user, not as certain no-ops: they are not documented defaults, and project-specific versions ("ask before running migrations on staging") carry information. A line survives when it changes the default: a project-specific command, an exception to the usual idiom, a decision that lives outside the repo, a correction Claude needed twice. Most subagents load the same CLAUDE.md files. Explore, Plan and agents with `omitClaudeMd` start without the user, project and local CLAUDE.md files (managed policy still loads, and subdirectory CLAUDE.md files and matching scoped rules load when they touch those files). The main session still applies CLAUDE.md to their results, so most rules need nothing more; one that must hold inside such an agent stays in CLAUDE.md and is also restated in the delegation prompt.
1. **Can Claude find it by reading the repo, and would it actually look?** If both are yes, leave it out (framework conventions, directory layout, dependency lists, anything in package.json or the formatter config).
2. **What goes wrong without it?** Name the recurring mistake, the costly rediscovery, or the decision that lives outside the repo (a meeting, a deploy process, a person's head). No nameable failure, no line.
3. **Who needs it, and when?** All projects for one person, one repository, one subtree, one set of file types, one task type, or this task only.
4. **Can it have exceptions?** Guidelines can; Claude is allowed to judge that one doesn't apply. A rule with zero exceptions belongs in configuration.
5. **Is it true right now?** Commands, paths, script names, versions: verify against the repository, not memory.

## Mechanism map

| Content | Home | Why |
| :-- | :-- | :-- |
| Personal preference true in every project (communication, reporting, language) | `~/.claude/CLAUDE.md` | Loads everywhere for this user only |
| Separable personal convention (one topic) | `~/.claude/rules/<topic>.md` | Modular; add `paths` only for file-type habits, and remember the base is the session's working directory |
| Team convention needed in several repositories | Shared rules directory linked into each repo's `.claude/rules/`, or a plugin | One source of truth; linked rules from outside the project need approval and only unscoped ones load; a plugin cannot ship always-on text (its conventions become skills that load on demand). See rules-architecture.md section 6 |
| Repository facts every task needs: exact verify commands, misleading code, decisions not in the repo, corrections made twice | `./CLAUDE.md` or `./.claude/CLAUDE.md` (pick one) | Shared via git, loads every session |
| Convention for one area or file type, or one convention across scattered paths | `.claude/rules/<topic>.md` with `paths:` | Loads only when matching files are touched |
| Conventions owned by a subtree's maintainers, versioned with that code | `<subtree>/CLAUDE.md` | Loads on demand when Claude works there |
| Personal note for this checkout (sandbox URL, local test data) | `CLAUDE.local.md`, git-ignored | Not shared; not a secret store |
| Multi-step procedure, runbook, checklist, reference material needed sometimes | Skill (`.claude/skills/<name>/SKILL.md`; `disable-model-invocation: true` when it has side effects) | Only name and description load until used |
| Must always or never happen (never edit `src/gen/`, never read `.env`, always format after edit) | Hook (`command` hook exits 2 to block; `http` hook returns a 2xx JSON decision) or `permissions.deny`; sandbox for OS-level limits | Enforced by the harness, not the model |
| Mechanical style (indentation, import order, quotes) | Formatter or linter config, optionally a PostToolUse hook | Machine-checkable; prose copy drifts |
| Response style that might be switched off (length, tone, role) | Output style | One active at a time |
| What Claude learned from corrections | Auto memory | Claude-owned lifecycle |
| Acceptance criteria for one task | The task prompt or a spec file | Not permanent context |
| Organization policy | Managed CLAUDE.md for guidance plus managed settings for enforcement | Cannot be excluded; still not enforcement by itself |

## Scope decisions

**User scope** (`~/.claude/`): keep only what is portable across unrelated repositories. Never mandate a package manager, framework, test command, deploy command or database pattern globally; a project that differs then carries a contradiction Claude resolves arbitrarily. When a personal default is useful but can collide, write it conditionally: "Unless the project specifies otherwise, ...". Changes here affect every repository, so treat them as higher-risk than project edits and get the owner's explicit approval.

**Project scope**: one canonical root file. Do not keep both `./CLAUDE.md` and `./.claude/CLAUDE.md` with overlapping content. Team-shared content only; personal content goes to CLAUDE.local.md or user scope.

**Subtree CLAUDE.md vs central scoped rule** (from the large-codebase guide):

| Choose | When |
| :-- | :-- |
| `<dir>/CLAUDE.md` | The directory is an ownership boundary and its owners maintain their conventions with the code |
| `.claude/rules/x.md` + `paths` | You want one discoverable catalog, or the same convention spans scattered paths |
| Skill | The content is a procedure, not a standing convention |

Never encode the same policy in both a nested CLAUDE.md and a scoped rule.

**Unscoped vs scoped rules**: splitting one always-loaded file into ten unscoped rule files improves organization, not context cost. Only `paths` reduces what loads.

**Conditional user rules**: a user rule with `paths: ["**/*.md"]` matches against whatever project the session runs in; write it as a personal default that yields to project requirements.

## AGENTS.md projects

If a repository already keeps instructions in AGENTS.md for other agents, keep one source of truth: either rely on Claude Code reading AGENTS.md (no CLAUDE.md on the path) or add a CLAUDE.md containing `@AGENTS.md` plus only Claude-specific lines below it. Warn that a personal CLAUDE.local.md stops AGENTS.md from loading by default.

## Enforcement hand-off

When an instruction belongs in configuration, still deliver value without silently changing settings:

1. Keep (or write) a short plain-language line if Claude benefits from knowing the rule exists, for example `src/gen/ is generated by scripts/codegen.ts; regenerate instead of editing`.
2. Propose the enforcing configuration as a separate, explicit recommendation with the exact snippet and where it goes, for example:

```json
{
  "permissions": {
    "deny": ["Edit(/src/gen/**)"]
  }
}
```

(`Edit` rules cover every built-in editing tool, Write included; a `Write(path)` rule is accepted but never matches. A single leading `/` anchors at the settings source: in project and local settings that is the session's primary working directory (so a rule written for the repository root misses when sessions start in a subdirectory), and in `~/.claude/settings.json` it is `~/.claude/`. Use a `//`-absolute or `~/` path in user settings and per-package settings for subdirectory launches. Deny rules do not stop a script that opens files itself; the sandbox does.) A PreToolUse hook that exits 2 for paths under the protected directory is the alternative when the rule needs logic. Verify these details against the current permissions and hooks pages before handing them over. Settings and hooks are executable configuration that applies to everyone who trusts the folder; change them only when the user asks for that change.
