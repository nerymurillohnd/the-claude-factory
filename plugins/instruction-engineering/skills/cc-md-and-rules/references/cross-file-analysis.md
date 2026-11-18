# Cross-file analysis: contradictions, overlaps, ambiguities, misplacement

Every file that can be in context at the same time behaves like one document. Defects live between files more often than inside them. Run this analysis in every review or audit, and in a lighter form (step 3 on the subjects you touch) before every write.

## 1. Build the comparison set

List every file that can load together in the situations that matter, using the checker inventory and `--match` for representative files:

- `~/.claude/CLAUDE.md` and `~/.claude/rules/` (user scope applies to this project too);
- ancestor and root CLAUDE.md, `.claude/CLAUDE.md`, CLAUDE.local.md, AGENTS.md when it loads, and everything they import;
- always-on rules, scoped rules (grouped by the files that trigger them), nested CLAUDE.md files;
- the repository facts instructions talk about: manifests, lockfiles, CI, formatter and linter configs, the directories named.

## 2. Extract atomic instructions

Split prose into single instructions. For each, note: subject (what it is about: test runner, error format, migrations, commits), action (do or avoid what), condition (when, for which files or tasks), file and line, and when it loads (always, on which paths, personal). Bullets that hold two instructions become two entries.

## 3. Compare within each subject

Group entries by subject across all files, then check each group for these relations. Name the relation in the finding; it determines the fix.

| Relation | What it looks like | Typical fix |
| :-- | :-- | :-- |
| **Direct contradiction** | Two instructions demand incompatible actions under overlapping conditions ("use Jest" / "use Vitest"; "commit directly to main for hotfixes" / "never commit to main") | Decide with the owner which holds; keep one, scope the exception explicitly |
| **Contradiction with repo truth** | Instruction disagrees with what the repository does (says Jest, `package.json` runs Vitest; names a script or path that doesn't exist) | Follow the repo or ask; fix the line |
| **Scope contradiction** | User scope mandates what this project does differently; an always-on line conflicts with a scoped rule when its files load | Make the broader one conditional or move it |
| **Semantic duplicate** | Same meaning, different words, in one or several files ("throw HttpError from src/lib/errors.ts" / "errors must use the HttpError class") | Keep one canonical line in the right home; delete the other |
| **Subsumption** | One instruction is a special case of another and adds nothing | Delete the special case, or keep it only if it adds a real detail |
| **Partial overlap, diverging details** | Same subject, details differ (error envelope `{error:{code,message}}` vs `{success,error}`; 2 vs 4 spaces) | Pick the true detail, merge into one line |
| **Ambiguity** | Vague terms ("properly", "clean", "when appropriate", "the API" when there are several), undefined referents ("the old service"), unverifiable lines, two "always" rules that cannot both hold in one case, no trigger | Rewrite with a concrete trigger, action and artifact, or ask the owner what it means |
| **Scope mismatch** | Always-on text about one area; scoped rule holding cross-cutting policy; scoped rule whose trigger is a task type ("when writing commit messages") | Move per rules-architecture.md |
| **Level duplicate** | The same instruction in a project file and in `~/.claude/` (user level), or copied across several repositories | Keep it at the level of its audience; propose a shared source for team rules (rules-architecture.md section 6) |
| **Overlapping scoped rules** | Two rules match the same files and diverge | Merge, or narrow the globs |
| **Wrong mechanism** | Procedure in always-on context; zero-exception rule in prose only; formatter settings copied into prose | Skill, hook or deny rule, formatter config (proposed) |
| **Stale or discoverable** | Paths, commands or tools that no longer exist; directory trees; stack descriptions | Delete or correct |
| **No-op** | Claude (and the subagents that receive the file) would act the same without it: generic virtues, training-data idioms, behaviors Claude Code already performs, workflows it discovers itself | Recommend deletion with the counterfactual reason; the user decides |

Also look for gaps the set implies: a rule that references a pointer that does not exist, a scoped rule that never matches, an important rule that loads too late to matter.

## 4. Report

Group findings by subject, most severe first, so the user sees each conflict as one decision:

```markdown
### Error responses (3 files)
- Contradiction (High): CLAUDE.md:14 "return { success, data, error }" vs .claude/rules/api.md:6 "errors as { error: { code, message } }". Both load for src/api files. Decide one envelope; proposed: keep the rule, delete the CLAUDE.md line.
- Duplicate (Medium): .claude/rules/api.md:7 and .claude/rules/backend/errors.md:3 both require HttpError. Keep the backend rule.
```

Follow with the placement verdicts (what should be always-on, scoped, a skill, enforced, deleted) and, when the set is saturated, the target structure from rules-architecture.md.

Quote line references from the baseline; they are review aids, not permanent pointers.
