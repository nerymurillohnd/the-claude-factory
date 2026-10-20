# Quality Gate

The commands live in `.claude/CLAUDE.md` → Commands.

## No Progress With Open Issues

- Do not advance to the next step, file or task while a detected issue is open.
- Report an issue as open only when it is blocked on a decision or a spend only Nery can make. Stop and ask.

## After Editing a File

- Run the gates for every `.py`, `.mjs`, `.ts` and `.sh` file you edit, write or create.
- Run them right after the edit, before the next task.
- Run in this order: formatter, linter, type checker, tests.
- Pass each strict `tsc` flag with an explicit value: `--strict` does not override an explicit `false` in a tsconfig.

## Before Every Push

- Run the steps in order.
- Stop at the first failure. Fix the cause, then restart from step 1.
- Report the gates as a table: gate, result and key output line.
