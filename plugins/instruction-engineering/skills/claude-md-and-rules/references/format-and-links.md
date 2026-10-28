# Format, links and globs

Use this when choosing how to lay out instructions (bullets, numbered steps, tables, prose), when connecting files (imports, pointers to repo files, pointers between rules), and when writing `paths` globs. Loader facts are in loading-semantics.md; wording is in writing-guide.md.

## Contents

1. Choosing the format
2. Tables without padding
3. Imports versus pointers
4. Pointers between rules
5. `paths` globs: braces or separate entries

## 1. Choosing the format

The memory docs ask for markdown headers and bullets ("organized sections are easier for Claude to follow than dense paragraphs"), and the prompting guide reserves numbered lists for steps whose order or completeness matters. The rest of this table is this plugin's judgment.

| Content | Format | Why |
| :-- | :-- | :-- |
| Independent rules | Bullets, one instruction each, under a header that matches how tasks start | Each line can be read, moved or deleted alone |
| Steps whose order matters | Numbered list, short (about three to five steps) | Order is the information; longer runbooks belong in a skill (procedures-to-skills.md) |
| A lookup: three or more rows sharing the same attributes (package → test command, error code → status) | Compact table | Rows line up for comparison; fewer repeated words than bullets |
| Two-column mapping with few rows | Bullets as `key: value` | A table's pipes and separator cost more than they help |
| A trade-off or the reason behind a decision | One short paragraph, or a clause after the rule | Prose carries "because" and "unless" better than fragments |
| Commands or text to copy exactly | Inline code, or a fenced block for multi-line | Marks the literal; code spans also keep `@path` from importing |
| Several examples | A skill, in `<example>` tags | Examples in always-on files cost every session (writing-guide.md item 7) |

Keep headers shallow (`#` and `##`). Use bold sparingly and never as enforcement.

## 2. Tables without padding

Markdown formatters pad tables so the columns line up in an editor. Prettier, for example, aligns table columns unless a row exceeds the print width with `proseWrap: never`. The padding carries no information, but it is part of every load and counts toward the character limits (40,000 characters for on-demand files on a 200K window). A typical four-column command table drops from 546 to 236 characters when the padding is removed.

- Write rows compactly: `| Task | Command |`, separators `| :-- | :-- |`.
- Exclude instruction files from Markdown formatting when the repo has a formatter that touches Markdown: for Prettier, add `CLAUDE.md`, `**/CLAUDE.md`, `CLAUDE.local.md` and `.claude/rules/` to `.prettierignore`. Recommend this; it is a tooling change outside the instruction files.
- The checker reports padded tables as `table-padding`.

## 3. Imports versus pointers

| You write | What happens | Use it for |
| :-- | :-- | :-- |
| `@docs/git.md` (bare) | Expanded into context at launch with the importing file, every session; up to four hops | Content that must be in every session but lives elsewhere for a reason: `@AGENTS.md` shared with other tools, a personal file in your home directory imported from `CLAUDE.local.md` across worktrees |
| `` `docs/git.md` `` or `` `@docs/git.md` `` in a code span | Nothing loads; it is a mention. The `@` inside backticks has no special effect | A pointer Claude follows when the task needs it |
| A rule with `paths` | Loads when Claude reads or edits a matching file | Guidance tied to files, so nobody has to remember the pointer |
| A skill | Description every session, body on demand | Reference material or procedures needed for some tasks |

- An import never saves context: it costs the same as pasting the file in. Splitting a long CLAUDE.md into imports organizes it without shrinking it, and importing a README or a long architecture doc is a common source of bloat.
- A pointer works only if Claude knows when to follow it. Write the trigger with it: "Before changing billing code, read `docs/billing.md`", not "See `docs/billing.md`".
- Pointers to code are good practice. The docs' own example points to `src/lib/errors.ts` rather than copying it, and a pointer stays true as the code changes. Point to stable files and exported names, not line numbers, and check that the path exists.
- When the referenced content applies to a set of files, prefer a scoped rule over a pointer; when it is a procedure, prefer a skill.

## 4. Pointers between rules

Rules load by their own `paths`, never by being mentioned. "See `.claude/rules/api.md`" inside another rule loads nothing; Claude may open it, or may not.

- **Target is always-on**: the pointer is redundant (the rule is already in context). Delete it.
- **Target is scoped, and the source's situation also needs it**: fix the loading instead of relying on Claude to follow a link. Widen the target's `paths` to cover both areas, move the shared lines into the rule that loads in both situations (or an always-on rule if they are cross-cutting), or merge the two rules.
- **Pointer from CLAUDE.md to a scoped rule**: justified when part of the rule is needed before Claude knows which files a task touches. Put the critical line in the pointer itself ("Database changes: applied migrations are immutable; details in `.claude/rules/data/migrations.md`") so it works even if the rule is never opened.
- **Two rules that each restate part of the other**: that is a semantic duplicate, not a link (cross-file-analysis.md). Keep one owner.

## 5. `paths` globs: braces or separate entries

Brace expansion and separate list entries are equivalent for loading: the rule loads when any pattern matches, and neither form loads it sooner or more efficiently. Choose by readability and maintenance:

- **Braces** for variants of one pattern that share a reason: extensions of one file family (`"src/**/*.{ts,tsx}"`), test-file suffixes (`"**/*.{test,spec}.ts"`), sibling directories treated the same way (`"{apps,packages}/*/src/**/*.ts"`).
- **Separate entries** for locations that are related only by the rule's topic or that you may remove independently (`"db/migrations/**"` and `"scripts/migrate.ts"`).
- Keep brace groups few and flat. Each group multiplies the expanded patterns (`{a,b}/{c,d}/*.{ts,tsx}` is eight), a rule's whole list shares a budget of 1,000 expanded patterns, and an over-budget pattern matches nothing. A one-option group (`*.{ts}`) adds nothing.
- Quote every glob. An unquoted value starting with `{` is a YAML flow mapping and one starting with `*` is an alias: either breaks the frontmatter, and the rule then loads in every session.
- Match the base: project rule patterns are relative to the directory holding `.claude/`; `*.ts` is root-only; use `**/` to recurse.
- Test each rule with `--match` on a file that should load it and one that should not.
