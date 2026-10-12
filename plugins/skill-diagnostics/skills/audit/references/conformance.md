# Conformance lens

Answers one question: **does the skill follow the documented rules and recommendations, and does it work on every surface it is meant for?** It does not judge whether a model could execute the skill without guessing; that is the executability lens.

Facts live in `fields.md` and `surfaces.md`, next to this file. Read both before step 3.

## Contents

- Input
- Steps
- Checklist
- Severity
- Output

## Input

- The skill directory (absolute path) and its origin.
- Its file inventory: every file under it, with relative paths, from the orchestrator. Its `outside` entries are links that leave the skill: name them as external dependencies; never read them or list them as not inspected. One whose `exists` is false is a broken link.
- The checker's JSON report (all four surfaces), or the line `checker not run: <reason>`.
- The paths of `fields.md`, `surfaces.md`, `examples.md` and the `assets/examples/` folder.
- Disputed findings, only on a second round, with your previous report block: answer only those. Re-check each against the files and the evidence given, correct it or withdraw it, and return that block with the corrected rows and a closing line `Withdrawn: <ID — why, or none>`.

Missing checker report: run the checklist without it and note `checker not run` in the output.

## Steps

1. **Read everything.** Take the file list from your task message, hidden files included; it is the whole inventory you work from, and any gap in it is reported by the orchestrator. Read every file on the inventory with the Read tool, from its first line to its last; when Read returns part of a file, continue from the next line until the end. Read images and check they show what the text says; read every page of a PDF. A file Read cannot open (a binary) or that the user's settings or hooks block is recorded as not inspected, with the reason, and never worked around. You have no search tool: every finding rests on what you read.
2. **Checker findings.** Take each checker finding as reported; do not re-judge it. Read the `file:line` it points to only to quote that line verbatim as its evidence. Map its severity: `error` → high, `warning` → medium; an `info` finding is a note, not a finding (leave it out). For a portability problem, the severity table in `surfaces.md` (Portability findings) overrides the mapping when the context it names applies (for example, an instruction depends on a skipped feature); say why. When the quoted line shows a false positive, drop the finding and say so.
3. **Checklist.** Walk the checklist below on every file it applies to. Mark each item pass, fail or n/a. An item the files cannot show (runtime behavior, triggering in practice) is n/a. Read `examples.md` first, and the example in `assets/examples/` for each profile the skill uses (fork, hooks, a script, dynamic context, preloaded into an agent). A difference from an example is a finding only when a checklist item explains it.
4. **Live check.** When a failing item depends on a field or behavior that may have changed, fetch the owning page listed in `fields.md` or `surfaces.md` and read that section. A live page that contradicts the reference wins: report the difference. Unreachable page: keep the finding and mark it `not verified live`.
5. **Report** with the output format below: failures only, each with its evidence.

## Checklist

Labels say how strong each item is (see `fields.md`). A **[default]** item is reported as low, with the alternative, unless breaking it breaks something.

### Description and triggering

- [rec] Says what the skill does first, then when to use it, in the words a user would type.
- [default] Does not summarize the procedure.
- [default] Covers every capability the body offers; a capability missing from the description never triggers.
- [default] Tells sibling skills apart by the kind of request, not by naming them.

### Scope and content

- [rec] One coherent job; no repetition of a sibling skill's job.
- [rec] Every paragraph is something the model would get wrong without it; no explanation of things the model already knows.
- [rec] Moderate detail: the main path plus the edge cases a model would get wrong; the rest is left to its judgment. A body that tries to cover every case is a finding.
- [rec] Prescriptive only where the task is fragile (exact commands, sequences, formats); elsewhere it states the goal and why.
- [rec] Teaches a method that generalizes, not the answer to one instance.
- [rec] Concrete commands, paths and values; one default where several approaches compete, with a short escape hatch.
- [rec] Examples are concrete (real values, real paths), not abstract.
- [rec] Quality-critical output has a validate → fix → repeat loop with an exit.
- [rec] One term per concept.
- [rec] No dates or version-dependent statements in the instructions; history, if needed, in a collapsed "old patterns" note.

### Structure

- [rec] `SKILL.md` holds what every run needs; material only some runs need lives in a referenced file, one level deep, linked with when to read it. No file is unused (an `evals/` folder is exempt).
- [rec] Critical rules near the top; instructions written as standing rules for the whole task.
- [rec] Multi-step work has numbered steps or a copyable checklist, and says when the work is done.
- [rec] Where output shape matters, a template or an example shows it.
- [rec] A gotchas section when the domain has traps a reasonable model would fall into.

### Fields and profile

- [req] No combination that disables the skill: `disable-model-invocation: true` with `user-invocable: false`; `disable-model-invocation: true` on a skill an agent preloads.
- [req] `context: fork` only with an explicit task; a fork of plain guidelines returns nothing.
- [req] A fork with `agent: Explore` or `Plan` states every rule it needs: those agents load no CLAUDE.md.
- [observed] No argument placeholder inside a dynamic-context command: the argument runs as shell code. High.
- [req] `paths` only on a skill Claude may start.
- [rec] A forked or preloaded skill states its input and its single final output, and never needs to ask the user.
- [rec] A skill with side effects states what running it authorizes and what still needs the user.
- [req] `allowed-tools` pre-approves the commands the skill runs, and nothing broader.

### Scripts

- [rec] Each bundled script is listed in `SKILL.md` with what it does and whether to run it or read it.
- [rec] Scripts take input by arguments, never by interactive prompts; errors say what failed and what to do.
- [rec] Dependencies are declared, or the script uses only the standard library.
- [rec] A script handles the error cases it can foresee instead of failing and leaving the model to guess.
- [rec] Every constant in a script says why it has that value.
- [req] Packages are installed locally, never globally (Claude Code).
- [rec] A destructive or batch step has a validation or dry-run step before it.
- [req] A script whose output Claude needs exits 0 when it printed that output and reports problems inside it: a failing command's output is cut to about 10,000 characters.

### Hooks

- [req] A hook command reaches the skill's files through `${CLAUDE_PLUGIN_ROOT}` or `${CLAUDE_PROJECT_DIR}`, never `${CLAUDE_SKILL_DIR}`, and quotes each placeholder in shell form.
- [req] A check that relies on `onFailure: "block"` is not on `Stop`, `SubagentStop`, `TaskCompleted` or `TeammateIdle`, where the field does nothing.

### Security

Read every instruction, script and asset for what it would make Claude do. Severity: high when the action does not match the skill's `description`; when it does (a deploy skill that uses the network), list it under requirements the skill must state, and report it only if the skill doesn't state it.

- [req] Network calls, or content fetched from an external URL that the model then follows (that content may carry instructions).
- [req] Reads outside the skill and the user's project: credentials, keys, `~/.ssh`, `.env`, browser or shell history.
- [req] Data sent to an external system.
- [req] Tool calls, file operations or commands that the `description` doesn't announce.

### Portability

- The skill passes the rules in `surfaces.md` on all four surfaces, with the severities given there for its origin.

## Severity

| Severity | Meaning |
| :-- | :-- |
| high | Breaks triggering, execution, safety, or a surface the skill reaches |
| medium | Wastes context, invites a misreading, or hides a requirement |
| low | Style, or a [default] the skill departs from without harm |

## Output

Return exactly this as your final message; the orchestrator merges it:

```markdown
### Conformance — <skill name> (<absolute path>)
Origin: <origin> · Checker: ran | not run (<reason>)
Files read: <n> of <n>

| ID | Severity | Location | Label | Finding | Evidence | Consequence | Fix |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| C1 | high | SKILL.md:3 | req | <one line> | "<verbatim quote>" | <what goes wrong, for whom> | <one line> |

Not inspected: <each file, why, and "needed by <file:line>" or "unreferenced"; or none>
Not verified live: <items, or none>
```

No findings: keep the header and write `No conformance findings.` in place of the table. Second round: add the `Withdrawn:` line last.
