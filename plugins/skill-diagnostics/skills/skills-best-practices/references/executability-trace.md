# Executability trace

How to follow a skill as its only executor, from trigger to completion, and record every point where a model would have to guess.

## Contents

- [The trace](#the-trace)
- [Navigation](#navigation)
- [Finding types](#finding-types)
- [Executability severity](#executability-severity)

## The trace

Follow it on one realistic task, taken from the skill's evals when they exist, and on every workflow and every variant that changes the output. Read no rule files (the references of the skill that audits, other than this file) and run none of the audited skill's scripts, though you read their source like any other file. When the audited skill is the auditing skill itself, its references are the files under test: read them as the brief's inventory says, apply none of them as rules, and say so in the report's navigation section: what a naive executor trips on is what any agent would trip on.

1. **Inventory.** List every file, hidden ones included, with whether each script is executable; a link that leaves the skill is an external dependency, never read.
2. **Read everything.** Read every file from its first line to its last; record a file that can't be read, and why.
3. **Map** `SKILL.md`: purpose, inputs and their sources, defaults, placeholders, which file governs which step, outputs and destinations, validation, and when the work is done.
4. **Trace** each workflow and each variant that changes the output, from trigger to completion; stop a branch where information is missing or contradictory and record the exact point.
5. **Simulate each file** as its only executor: what it makes you do, which values you need and where they come from, which decisions it leaves open, and whether its templates match what the instructions require.
6. **Cross-check** for the finding types below, then verify each candidate against every file before it counts.

Record each point at the exact place where you would have to guess, or where two files disagree, with both locations.

## Navigation

Record how you moved through the skill: files you never opened, files you read more than once, and files you read out of the order the workflow uses them.

## Finding types

- A missing workflow step or prerequisite.
- An input, value or placeholder with no source or rule; a placeholder defined and never used.
- Defaults or rules that contradict each other, in one file or across files.
- A condition or variant that is ambiguous or never specified.
- A broken local link, a missing file or a missing dependency.
- A name or identifier that differs between `SKILL.md`, references and assets.
- An output path or format that differs between files.
- An example that contradicts a mandatory instruction.
- A template or asset that can't produce the required output.
- A command or tool call that is incomplete or inconsistent with how the script works.
- Validation that doesn't check what the output requires.
- Missing failure handling where completion depends on it.
- A step that loads a file without pointing to it, or a file that never says when to read it.
- An instruction outside the skill's stated purpose.

## Executability severity

- **Decides the output.** A finding decides the output when, without the missing or conflicting information, a model would reach a different answer or produce different files.
- **Path.** Its path is normal in ordinary use and rare when only a fallback, a failure or an unusual input reaches it.
- **Severity.** Decides output on a normal path = high; on a rare path, or not deciding output = medium.
