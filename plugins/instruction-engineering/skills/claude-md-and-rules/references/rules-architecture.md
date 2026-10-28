# Instruction architecture: what stays, what moves, how rules are organized

Use this when deciding what belongs in CLAUDE.md versus `.claude/rules/`, when a CLAUDE.md is saturated, when rules need reorganizing, and when choosing between an always-on rule and a `paths`-scoped one. Loader facts it relies on are in loading-semantics.md.

## Contents

1. Signals of a saturated or disorganized instruction set
2. Classification rubric: one home per instruction
3. Always-on versus `paths`-scoped
4. Organizing `.claude/rules/`
5. Presenting a target structure
6. Sharing instructions across projects

## 1. Signals of a saturated or disorganized instruction set

Treat these as structural problems, which call for a structural proposal rather than line edits:

- One file covers several domains (frontend, backend, data, infra, release) or several audiences (team and one person).
- Sections whose content is about one directory or file type while the file loads in every session.
- Numbered procedures, runbooks or checklists inside always-loaded files.
- The same instruction in two places, or two instructions on one subject that disagree.
- Content Claude can discover by reading the repo (directory trees, stack descriptions, dependency lists, formatter settings).
- Emphasis inflation (IMPORTANT, CRITICAL, capitals, `!!`), which usually marks a rule that kept being broken.
- Rules directory with mixed-topic files, tiny fragments, backups, unclear names, or folders that look like scoping but are not.
- More than about 200 lines in a CLAUDE.md, or a large always-loaded total across CLAUDE.md, unscoped rules and imports.

A single signal can justify a targeted fix. Two or more, or any signal in a file that keeps being ignored, justify proposing a target structure (section 5) even when the user only asked for "a review" or "a cleanup".

## 2. Classification rubric: one home per instruction

Classify every instruction, not every section: sections usually mix kinds.

| The instruction... | Home | Test |
| :-- | :-- | :-- |
| Is needed in most tasks, or before Claude knows which files a task touches: verify commands, how to run one test, repository-wide decisions, misleading code that affects any change, workflow and reporting policy | Root `CLAUDE.md` | Would a task that touches only unrelated files still need it? |
| Matters only while working on certain paths or file types: framework conventions of one area, migration rules, test-file conventions, docs style | `.claude/rules/<area>/<topic>.md` with `paths` | Can you name the globs, and is the guidance useless before those files are touched? |
| Is cross-cutting and always needed, but large, independently owned, or a distinct topic (security policy, git and PR workflow, API-wide error contract) | Unscoped rule `.claude/rules/<topic>.md` | Keeping it modular helps ownership; it costs the same context as CLAUDE.md |
| Is owned by a subtree's maintainers and versioned with that code | `<subtree>/CLAUDE.md` | Directory is an ownership boundary |
| Is a procedure: ordered steps, a checklist, a runbook | Skill (see procedures-to-skills.md) | Is it needed only when doing that task? |
| Must happen or never happen, no exceptions | Hook or `permissions.deny`, plus at most one plain line in prose (see escalation.md) | Would one miss be costly or unrecoverable? |
| Is personal | `CLAUDE.local.md` or `~/.claude/` | Would a teammate disagree with it? |
| Is discoverable, generic, stale or untrue | Delete (say why) | Could Claude find it, and would it look? Is it true today? |

A pointer is allowed when a scoped rule or skill is important enough that Claude must know it exists before touching files: one line in CLAUDE.md such as "Database changes: see the migration rule; never edit applied migrations." Do not copy the rule's body.

## 3. Always-on versus `paths`-scoped

Decide per rule file. Scoped rules load only after Claude reads, writes or edits a matching file (Read/Write/Edit or a single-file Bash read). That timing is the deciding factor.

Keep a rule **always-on (no frontmatter)** when any of these holds:

- It shapes decisions made before choosing files: where new code goes, what needs approval, when to stop and ask, dependency policy.
- Its trigger is a task type, not a path: commit messages, PR descriptions, reporting, research, communication.
- It is cross-cutting policy: security and data handling, verification before claiming done, git workflow.
- Missing it once is costly, and enforcement is not (yet) in a hook: keep it visible, and recommend the hook.
- It is short and applies broadly; scoping would save almost nothing.

Scope a rule with **`paths`** when:

- The guidance is about how to write or change specific files: language or framework conventions of one area, file types (migrations, tests, docs, infrastructure), generated or vendored directories (paired with a deny rule when edits must never happen).
- It is long and most sessions never touch its files.
- It is a set of area conventions, even a short one: size is not the main reason to scope. A scoped rule loads with the files it governs and stops competing with repository-wide lines in every other task, which is what the docs recommend for instructions that matter for only part of the codebase. Pair it with a pointer line when part of it is needed before files are chosen.
- Several areas each need different conventions (one rule per area).

Traps when scoping:

- Planning-time knowledge disappears: "new endpoints go under `src/api/v2/`" must be known before any API file is opened. Keep it always-on or add a pointer line.
- Files Claude never touches directly do not trigger the rule: content produced by a generator command, or edits made through a multi-file Bash command, are not reads of a matching file.
- Two scoped rules that match the same files load together: their guidance must not diverge.
- A scoped rule inside a subdirectory's `.claude/rules/` uses that subdirectory as its base and loads on demand; moving it changes both.
- `paths` must be valid YAML: an unquoted glob starting with `*`, `{` or `[` breaks it and the rule silently becomes always-on, so quote globs.

## 4. Organizing `.claude/rules/`

- **One topic per file**, named for the topic (`api-errors.md`, `migrations.md`), not for the source document (`notes.md`, `misc.md`, `rules2.md`).
- **Folders group by domain or layer** (`frontend/`, `backend/`, `data/`, `testing/`, `workflow/`, `security/`). Folders are for humans only: scoping comes from `paths` in each file.
- **Split** a file that mixes always-on policy with area conventions, or two areas; **merge** fragments that cover one topic; **delete** backups, empty files and stale rules (backups move outside `.claude/rules/`, where they stop loading).
- **Scope overlap check**: list which rules each representative file would load (`--match`) and read those together.
- **Pair** each important scoped rule with a pointer line in CLAUDE.md when it must be known before files are touched.
- **User-level rules** (`~/.claude/rules/`) follow the same layout; their `paths` match against the current project, so keep them generic (`**/*.tsx`), never project-specific.

## 5. Presenting a target structure

When the audit or the request is structural, the deliverable includes a proposal Claude can apply after approval. Show it in this shape (prose is fine for a small set; use the tree and tables when more than a few files move):

```text
Target structure
CLAUDE.md                          always · commands, repo-wide decisions, gotchas, pointers   ~35 lines
CLAUDE.local.md                    always, this checkout only · personal preferences (git-ignored)
.claude/rules/
├── workflow/git-and-prs.md        always · branch, commit and PR policy
├── frontend/components.md         paths: "src/web/**/*.{ts,tsx}"
├── backend/api.md                 paths: "src/server/**/*.ts"
└── data/migrations.md             paths: "db/migrations/**"
.claude/skills/release/SKILL.md    on /release only · release runbook
Proposed enforcement (not applied): PreToolUse hook blocking edits to applied migrations
```

Then:

1. **Keep / migrate / delete table**: every original section or instruction, its decision (keep in CLAUDE.md, move to rule X, move to skill Y, enforce with Z, personal → local, delete), and the one-line reason from the rubric above. State explicitly what stays in the root CLAUDE.md and why (needed in most tasks, or before Claude knows which files a task touches); a proposal that lists only what moves leaves the owner guessing about the rest.
2. **Always-loaded footprint** before and after (lines or characters of CLAUDE.md + unscoped rules + imports).
3. **Risks**: anything whose timing changes (planning-time knowledge now scoped), anything removed as discoverable, decisions the owner must confirm.
4. **Verification**: `--match` positive and negative tests for each scoped rule; fresh-session checks.

Apply only after approval when the user asked for a review or audit; apply directly when they asked for the refactor itself, and still show the structure and table.

## 6. Sharing instructions across projects

When the same rule exists in several repositories, or a project rule repeats a user-level rule, pick one home by who needs it and how it must load:

| Need | Mechanism | What to know |
| :-- | :-- | :-- |
| One person, every project on their machine | `~/.claude/rules/` (or `~/.claude/CLAUDE.md`) | Loads without any approval; `paths` match against the current project; keep content generic. Not shared with teammates |
| A team's conventions in several repos, maintained once | A shared rules directory or file linked into each repo's `.claude/rules/` (`ln -s ~/shared-claude-rules .claude/rules/shared`) | A link whose target is outside the working directory is treated like an external import: nothing loads until the one-time per-project approval, and after approval only linked rules without `paths` load, so scoped shared rules silently never load. Network-path targets are never followed. Edit and Write refuse to write through the link; edit the target. Committed symlinks need the same target path on every machine and break on Windows clones without symlink support. `claudeMdExcludes` can match either the link path or the target |
| The same conventions for a whole team or organization, versioned and installed | A plugin (skills for procedures and reference conventions), or a managed CLAUDE.md for organization-wide guidance | A CLAUDE.md at a plugin's root is not loaded: conventions become skills, which load on demand, so cross-cutting policy (security, git) loses its always-on timing. A managed CLAUDE.md cannot be excluded and loads everywhere |
| A personal note for one repo across its worktrees | `@~/.claude/<project>-notes.md` | Importing it from CLAUDE.local.md still needs that file in each worktree; importing it from the shared CLAUDE.md puts a personal path in a team file (teammates without the file get a missing import). Pick one trade-off and say so |

Raise this unprompted when you see it:

- A project rule that duplicates a rule in `~/.claude/rules/` (or the other way round): keep it at the level of its audience (team rule in the project, personal rule at user level) and delete the other copy.
- The user mentions or the fixtures show the same rule copied across repositories: recommend one shared source (user-level for personal rules; a linked shared directory or a plugin for team rules), with the caveats above.
- A rule with `paths` linked from outside the session's working directory: warn that it will not load, even after approval; make it unscoped, keep a project copy, or convert it to a skill. A link that stays inside the working directory (a shared directory in a monorepo) loads normally.
