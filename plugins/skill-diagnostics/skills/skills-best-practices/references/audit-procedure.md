# Audit procedure

How the orchestrator runs an audit, from the validation scripts to the recorded verdict. Only the orchestrator reads this file; the agents never receive it.

## Contents

- [Every audit is complete](#every-audit-is-complete)
- [How an audit runs](#how-an-audit-runs)
- [Validation scripts](#validation-scripts)
- [Script result format](#script-result-format)
- [Skill profile](#skill-profile)
- [Agents](#agents)
- [Why the audit runs subagents](#why-the-audit-runs-subagents)
- [Rules for every brief](#rules-for-every-brief)
- [Saving the reports](#saving-the-reports)
- [Checking an agent report](#checking-an-agent-report)
- [Adversarial verification](#adversarial-verification)
- [Mapping findings to the checklist](#mapping-findings-to-the-checklist)
- [Verdict and recording it](#verdict-and-recording-it)
- [The audit in chat](#the-audit-in-chat)

## Every audit is complete

After an edit and before a release alike, the audit runs all four validation scripts and all six agents on every file of the skill, whichever files changed. No run audits a subset: a change can break a file it didn't touch, such as a script that now contradicts `SKILL.md`. Every audit runs at this one level of rigor, whatever the gate's mode.

## How an audit runs

1. **Trigger.** In Claude Code and Cowork, after a write or an edit inside a skill, the plugin's hooks record the skill as pending and ask Claude to audit it; at the end of the turn the gate also finds skills changed by other means. The user can also run the audit directly.
2. **Scripts, one after another.** Run `check-metadata.py` and read its result, then `check-structure.py`, then `check-runtime.py`, then `check-size.py` ([Validation scripts](#validation-scripts)). Each result shapes the next run: the origin and surfaces from the first decide which rules apply, and the inventory from the second is the file list the third scans. Launch no agent until all four have returned and their results are read. A script that couldn't run makes the verdict not determinable, because the checks it owns were never made. Still run the other scripts and the agents, so the report shows every other finding; a high finding still makes the verdict fail.
3. **Profile.** From the script results and the skill's text, write the skill profile ([Skill profile](#skill-profile)), which decides which patterns the skill needs.
4. **Briefs.** Write one brief for each of the four reviewers and the cold executor from `assets/brief-template.md`, filling every field ([Rules for every brief](#rules-for-every-brief)).
5. **Review.** Launch the four reviewers and the cold executor in one message, so they run in parallel; each returns its report template filled, self-check included. Claude Code refuses a 21st running subagent by default \[CC\]. Save each report as it arrives ([Saving the reports](#saving-the-reports)), then check it before using it ([Checking an agent report](#checking-an-agent-report)).
6. **Adversarial verification.** Pass every finding to the adversarial verifier ([Adversarial verification](#adversarial-verification)).
7. **Verdict.** Map the surviving findings onto [checklist.md](checklist.md) ([Mapping findings to the checklist](#mapping-findings-to-the-checklist)), give the verdict, write the report from `assets/report-template.md` with its Accounting table, save it, and record the verdict ([Verdict and recording it](#verdict-and-recording-it)).
8. **Gate.** In Claude Code and Cowork, the gate lets Claude end its turn only when a verdict exists that is newer than the skill's last change.

## Validation scripts

Run each script with its interpreter as a prefix, in this order, each writing its result with `--output` to a file in the audit folder `SKILL.md` names, so the next script can read it through `--previous`; the scripts create the folder, so never run `mkdir` for it. Don't redirect the output with `>`: Claude Code checks a redirect's target against the edit rules and would ask the user. Claude Code fills in `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_DATA}` only in `SKILL.md` and its `allowed-tools`, not in this file, and the Bash tool's environment doesn't hold them: run the commands as `SKILL.md` gives them. Their form is:

```text
python3 ${CLAUDE_SKILL_DIR}/scripts/check-metadata.py <skill-dir> --output <tmp>/metadata.json
python3 ${CLAUDE_SKILL_DIR}/scripts/check-structure.py <skill-dir> --previous <tmp>/metadata.json --output <tmp>/structure.json
python3 ${CLAUDE_SKILL_DIR}/scripts/check-runtime.py <skill-dir> --previous <tmp>/structure.json --output <tmp>/runtime.json
python3 ${CLAUDE_SKILL_DIR}/scripts/check-size.py <skill-dir> --previous <tmp>/runtime.json --output <tmp>/size.json
```

| Order | Script | Checks | Hands on |
| --- | --- | --- | --- |
| 1 | `check-metadata.py` | Frontmatter starts on line 1 and parses as strict YAML (a strict subset, checked by the script itself); `name` and `description` limits and reserved words; fields each surface rejects; strict-YAML traps; combinations that disable the skill | The skill's origin and the surfaces it reaches |
| 2 | `check-structure.py` | Full file inventory, hidden files included, with each script's executable bit; reference files over 100 lines without a table of contents, and table-of-contents entries that don't match a heading; links more than one level from `SKILL.md`; broken links and unused files; pointers of the form `file.md#anchor` whose file or heading doesn't exist; backslashes in paths; shebang lines | The inventory every reviewer reads |
| 3 | `check-runtime.py` | Unescaped `$` before a digit, `ARGUMENTS` or a name declared in `arguments`; `arguments` names not used; argument placeholders inside `!` commands; bare `allowed-tools: Bash`; scripts not called through `${CLAUDE_SKILL_DIR}`; each `Bash()` pattern in `allowed-tools` that doesn't match the form of the command the body runs; hook fields in the frontmatter (paths, quoting, `onFailure` on Stop-type events); signals of network calls and of reads of credentials or history | Leads for the scripts-and-runtime and security reviewers |
| 4 | `check-size.py` | `SKILL.md` over 500 lines; a body over 5,000 tokens, estimated as characters divided by 2.8; a lead between 4,500 and 5,000 | The size the instructions reviewer weighs when it proposes moving detail into references |

Exit codes: `0` the script ran, even when checks failed; `2` a usage error; `1` it could not run. On `2`, fix the command and run it again. On `1`, the verdict is not determinable; record the script as "couldn't run" in the report.

## Script result format

Each script prints one JSON object on stdout:

```json
{
  "script": "<name>",
  "skill": "<absolute path>",
  "ran": true,
  "checks": [
    {
      "check": "<M|S|R>-<n>",
      "item": "<checklist ID>",
      "kind": "proved | lead",
      "status": "pass | fail | lead",
      "location": "<relative path>:<line> or null",
      "detail": "<at most 300 characters>"
    }
  ],
  "truncated": 0
}
```

- `check-metadata.py` adds `"origin"` (one of `account`, `plugin`, `personal`, `project`, `loose`) and `"surfaces"` (a list).
- `check-structure.py` adds `"inventory"`: a list of `{"path", "lines", "executable"}`.
- `truncated` counts the checks left out when the output hit its bound.
- **Proved** (`kind: proved`, status `pass` or `fail`): the check is mechanical and the script settled it. No agent checks it again; the brief lists it under "Proved by the scripts".
- **Lead** (`kind: lead`, status `lead`): a signal that needs judgment, such as a network call that may match the description. The brief hands it to the agent that owns the item, which confirms it as a finding or rejects it with the reason. A lead on an item a script owns (such as `CF-1` or `FM-6`) goes to no agent: confirm or reject it yourself, with the reason, before mapping.

## Skill profile

Not every skill needs every pattern: "use the ones that fit your task" \[AS\]. The profile records what the skill is, and from it each pattern is required, optional or unnecessary.

The profile also records the surfaces. `check-metadata.py` infers the origin from the folder alone; when the user says the skill must also run on a surface its origin doesn't reach (for example a loose or personal skill that will be uploaded to the Claude app), add that surface and apply its rules, including the frontmatter fields an upload rejects, and say so in the briefs and the report.

| Profile question | Pattern it decides | Area file |
| --- | --- | --- |
| Reference content or task content? | Invocation settings; a task with side effects states what it authorizes | [claude-code-features.md](claude-code-features.md#invocation-control), [body-and-structure.md](body-and-structure.md#writing-the-body) |
| Several steps, or one? | A copyable checklist for a complex workflow | [workflows.md](workflows.md#checklist-for-a-multi-step-workflow) |
| Quality-critical output? | A validation loop | [workflows.md](workflows.md#validation-loop) |
| Batch, destructive or high-stakes operations? | Plan-validate-execute, `--dry-run` in its scripts | [workflows.md](workflows.md#plan-validate-execute), [scripts.md](scripts.md#design-for-an-agent) |
| A required output format? | An output template and examples | [body-and-structure.md](body-and-structure.md#writing-the-body) |
| Runs forked or preloaded into a subagent? | A closed contract: input, single output, what to return when input is missing | [body-and-structure.md](body-and-structure.md#writing-the-body), [claude-code-features.md](claude-code-features.md#forked-subagents) |
| Bundles scripts? | Execute-or-read stated for each; the agent-friendly script rules | [scripts.md](scripts.md#design-for-an-agent) |
| Surfaces it reaches | Which features the skill may depend on | [surfaces.md](surfaces.md#how-the-body-behaves-by-surface) |

A required pattern that is missing, a pattern the profile makes unnecessary, and a pattern that doesn't fit the skill's nature are all findings.

## Agents

Six read-only plugin agents. Only the orchestrator launches them, all six in every audit, as `subagent_type` `skill-diagnostics:<name>`; none of them asks the user anything.

| Agent | `subagent_type` | Lens or method file | Report it fills | Items it owns |
| --- | --- | --- | --- | --- |
| Description reviewer | `skill-diagnostics:description-reviewer` | [lens-description.md](lens-description.md) | `assets/reviewer-report.md` | See [checklist.md](checklist.md#owners-at-a-glance) |
| Instructions reviewer | `skill-diagnostics:instructions-reviewer` | [lens-instructions.md](lens-instructions.md) | `assets/reviewer-report.md` | See [checklist.md](checklist.md#owners-at-a-glance) |
| Scripts-and-runtime reviewer | `skill-diagnostics:scripts-runtime-reviewer` | [lens-scripts-runtime.md](lens-scripts-runtime.md) | `assets/reviewer-report.md` | See [checklist.md](checklist.md#owners-at-a-glance) |
| Security reviewer | `skill-diagnostics:security-reviewer` | [lens-security.md](lens-security.md) | `assets/reviewer-report.md` | See [checklist.md](checklist.md#owners-at-a-glance) |
| Cold executor | `skill-diagnostics:cold-executor` | [executability-trace.md](executability-trace.md) | The template in its agent file | `EX-1` |
| Adversarial verifier | `skill-diagnostics:adversarial-verifier` | [evidence-and-verdict.md](evidence-and-verdict.md) | The template in its agent file | None: it rules on the others' findings |

## Why the audit runs subagents

`default`. The audit is a few focused workers whose long reports would flood the main conversation, so it runs them as subagents with the main session as the orchestrator, by the comparison in [workflows.md](workflows.md#when-a-skill-runs-other-agents). Agent teams are off by default and absent in `claude -p`; a workflow would hold the order in code but needs the user's approval to start, must be turned on in Pro and has no chat equivalent; an orchestrator subagent would lose the user's conversation. The reviewers' results arrive in later turns, where this skill's `allowed-tools` grant no longer applies: there the plugin's `PermissionRequest` hook approves the skill's own scripts, run exactly as `SKILL.md` gives them, and nothing else.

## Rules for every brief

`default`. A subagent receives only the prompt the orchestrator writes, and the orchestrator sees only its final message \[CC\], so the brief carries everything the agent needs for this run.

- **What the agent already has.** Each agent already has, from its own file: its role, the files it reads, its method, its report template and its prohibitions. The brief adds only the fields of `assets/brief-template.md` and repeats none of those. Don't open the agent files: they sit in the plugin's install folder, outside the working directories, and they don't exist in chat.
- **Explicit scope.** "In scope" names the agent's lens file and the IDs of the checklist items it owns, from [checklist.md](checklist.md#owners-at-a-glance). "Out of scope" names the other agents' lens files and lists every check the scripts proved. No item is in two agents' scope.
- **Checkable, not subjective.** The brief holds the agent to the rule in [evidence-and-verdict.md](evidence-and-verdict.md#evidence-and-verification), **Checkable, not subjective.**
- **Evidence for every finding**, in the fields of the report template.
- **Leads, not conclusions.** The script leads in the agent's area are named as leads; the agent confirms or rejects each one.
- **What to return:** the template's path, filled exactly, with the self-check completed.
- **Release line.** Fill `Claude Code release` with the user's version from `claude --version`, or `unknown`; the adversarial verifier reads the changelog range from it.
- **Full paths.** Replace `${CLAUDE_PLUGIN_ROOT}/skills/skills-best-practices` in the brief with the absolute path of this skill's folder, the folder that holds this file's `references/`.
- **No list of changed files.** The brief doesn't name the files that changed, so no agent narrows its review to them.
- **The cold executor's brief** uses the second template in `assets/brief-template.md`: one realistic task, taken from the skill's evals when they exist, and the instruction to follow the trace on every workflow and every variant that changes the output. It carries no scope, no proved checks and no leads.

## Saving the reports

`default`. The report the user reads is a synthesis, so every agent report is kept as it arrived, and the Accounting table in the final report shows what happened to each of its findings. Together they let the user check that no finding was dropped.

- **Who saves them.** The plugin's hooks, not you. When one of the six agents finishes, a `SubagentStop` hook writes its report unchanged to `${CLAUDE_PLUGIN_DATA}/audits/<session id>/agents/<agent>-<agent id>.md`; in auto mode, where an agent delivers its report through `SubagentHandback`, a `PostToolUse` hook on that tool writes the same file. No tool call of yours is involved, so no permission is asked and the text can't be changed on the way. A report sent back and returned again has a new agent id and its own file.
- **Unchanged.** The file is the agent's text as Claude Code handed it to the hook, ending with one newline. Never edit a saved report.
- **If a report is missing.** Without `jq`, or when the hook fails, no file appears. Go on with the audit and say in the report's What ran block which reports weren't saved; it doesn't change the verdict. In chat no hook runs and nothing is saved.
- **How long.** The plugin deletes audit files after 7 days, and uninstalling the plugin deletes the folder. Copy it into the user's project only when the user asks, to the place they name.

## Checking an agent report

Before you use a report, check it against its template:

- every field filled, none left as a placeholder;
- every self-check item ticked;
- every finding on an item the brief put in scope (for the cold executor, `EX-1` only);
- `Status` is `complete`. A report with `Status: incomplete` (including the verifier's) makes that review incomplete.

A report that fails goes back once to its agent with the failed points: resume the same agent with a message (`SendMessage` to its ID or name); when that isn't available, launch it again with the same brief plus the failed points. If it fails again, that review is incomplete and the verdict is not determinable.

## Adversarial verification

Pass every finding to the adversarial verifier, with its evidence and without the reviewer's reasoning (drop the Defect line; keep ID, Item, Severity, Location, Evidence, Basis and Fix; for each cold-executor point, first fill Item `EX-1`, its severity from [executability-trace.md](executability-trace.md#executability-severity), Basis and Fix as [Mapping findings to the checklist](#mapping-findings-to-the-checklist) says, and drop The guess), together with the Claude Code release, the skill's absolute path, its origin, the surfaces it reaches and the profile from the briefs, so the verifier can reread each cited line and judge whether the rule applies. The verifier fills the template in its agent file by [evidence-and-verdict.md](evidence-and-verdict.md#verifying-a-finding).

- A finding the verifier disputes goes back once to the reviewer that made it, with the evidence against it; what still fails is withdrawn.
- A finding ruled "not verified against the official source" is neither upheld nor withdrawn on that ground; when a source that was tried couldn't be reached, the verdict is provisional ([evidence-and-verdict.md](evidence-and-verdict.md#severity-and-verdict)).
- Findings the verifier merged become one finding, at the highest severity, listing every location.

## Mapping findings to the checklist

- Give every item of [checklist.md](checklist.md) one status: pass, fail or n/a. Items owned by `evals` get "not assessed by this audit", with the evaluation in [evaluation.md](evaluation.md) that would assess them.
- A proved script check sets its item directly. An item fails when a surviving finding or a failed proved check names it.
- A failed proved check, and a lead you confirmed yourself, is also written under Findings: its check ID (such as `S-2`) as the finding ID, the item, the location and detail the script gave as Location and Evidence, a Fix, the severity of the item's strength label ([evidence-and-verdict.md](evidence-and-verdict.md#severity-and-verdict)), and `Verifier: proved by <script>`, or `confirmed by the orchestrator` for a lead.
- An item is n/a only when the profile or the origin makes its rule not apply, or when the skill has nothing the rule governs (for example `CF-6` with no `hooks` in the frontmatter, or `CF-5` without `context: fork`); say which.
- Executability points from the cold executor map to `EX-1`, with the severity of [executability-trace.md](executability-trace.md#executability-severity). In the report, each point's Basis is `executability-trace.md` and its type, and its Fix is the one change that removes the guess, such as stating the missing value or the step's condition.
- Read every item's ID from `checklist.md` at this step; never write an item from memory.
- **Accounting.** In the report's Accounting table, list every finding ID of every agent report, the cold executor's points included, and every failed proved check and confirmed lead, once each, with one outcome: `kept as <ID>`, `merged into <ID>`, or `withdrawn` (the reason goes under Withdrawn). Count the findings in each saved report and check that the table has the same number for that agent; a finding with no row is a defect of the report, not of the skill.

## Verdict and recording it

Give the verdict by [evidence-and-verdict.md](evidence-and-verdict.md#severity-and-verdict), then write the report from `assets/report-template.md`.

In Claude Code and Cowork, the last step records the verdict for the gate, with the command as `SKILL.md` gives it:

```text
python3 ${CLAUDE_SKILL_DIR}/scripts/record-verdict.py --data-dir ${CLAUDE_PLUGIN_DATA} <skill-dir> <verdict>
```

`<verdict>` is one of `pass`, `pass-with-warnings`, `fail` or `not-determinable`. Don't run it in chat. It succeeded when it exits 0 and prints the JSON object it wrote, with the same `skill` and `verdict`. On exit 2, fix the command and run it again; on exit 1, report its error in the report: the gate can't clear the skill until a verdict is recorded.

## The audit in chat

Chat loads the skill and ignores agents and hooks \[CP\]. There the audit runs inline:

1. Run the four scripts in the code execution sandbox when it is available, as `python3 scripts/<script>.py`, with paths relative to `SKILL.md`, on the audited skill's folder as uploaded or attached to the conversation. When the sandbox isn't available, or the audited skill's files aren't in it, the scripts couldn't run and the verdict is not determinable.
2. Write the skill profile ([Skill profile](#skill-profile)), and list the checks the scripts proved and the leads they reported, as a brief would. Each lens reads them from here. The Claude Code release is `unknown`.
3. Apply the four lens files one after another: [lens-description.md](lens-description.md), [lens-instructions.md](lens-instructions.md), [lens-scripts-runtime.md](lens-scripts-runtime.md), [lens-security.md](lens-security.md). Record each in `assets/reviewer-report.md`, self-check included. These records are working notes: keep them out of the reply unless the user asks for them; the report carries the findings.
4. Follow [executability-trace.md](executability-trace.md) on the skill and record each point as a finding with Item `EX-1`, its severity by [Executability severity](executability-trace.md#executability-severity), Location, Evidence and Fix.
5. Check each finding against [evidence-and-verdict.md](evidence-and-verdict.md#verifying-a-finding) yourself, and write the ruling and its source in the finding's Verifier field of the report.
6. Write the report from `assets/report-template.md`, with the Accounting table over the findings of steps 3 to 5. It says that no independent reviewers, cold executor or verifier ran, so the trace was done by the same context that read the rules, and that no report was saved.
7. Don't run `record-verdict.py`: no gate reads it in chat.
