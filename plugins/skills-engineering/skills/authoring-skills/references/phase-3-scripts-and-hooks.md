# Phase 3: Scripts and hooks

How to design each script and hook phase 2 chose, before the plan is approved: the interface the model meets, the language and dependencies, and the hook's events.

## The interface the model meets

The model reads the script's output to choose its next step. Design for that reader:

- No interactive prompts: the model can't answer one, and the run hangs. Take every input as an argument, flag, environment variable or standard input.
- A `--help` that states the purpose, the arguments and one example.
- Errors that say what failed, what was expected and what to do: "Column 'net_amount' not found in invoices.csv. Columns found: invoice_id, date, gross_amount, tax."
- Results on standard output in a fixed shape (JSON, CSV or set lines); diagnostics on standard error.
- Exit codes that mean something, listed in `--help`.
- Errors handled inside the script, with a report of what it did, instead of a failure the model must interpret.
- Safe to run twice, because the model retries.
- A `--dry-run` for anything destructive, and an explicit flag to really do it.
- Short output by default, with detail behind a flag or in a file.
- A comment on each constant saying why it has that value.

## Language and dependencies

- Prefer the standard library. For packages, declare them inside the script where the language allows it, such as inline metadata run with `uv run`.
- Write shell scripts for bash or POSIX sh, with forward slashes. A skill that supports Windows runs them through Git Bash; state that requirement.

## Hook events

Before choosing a hook's events, consult https://code.claude.com/docs/en/hooks for what each event receives and the decisions it can return.
