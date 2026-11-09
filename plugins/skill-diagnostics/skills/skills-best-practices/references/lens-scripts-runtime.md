# Scripts and runtime lens

What the scripts-and-runtime reviewer checks: whether each bundled script works for an agent on every surface the skill reaches, and whether the skill's Claude Code features are set up to run.

## Items

Each line names the checklist item from [checklist.md](checklist.md), then the area file and heading that hold the rule, then the rule's bold lead-in. Read the rule there; it is not repeated here.

- `SC-1` · [scripts.md#design-for-an-agent](scripts.md#design-for-an-agent) · **Specific error messages**
- `SC-1` · [scripts.md#design-for-an-agent](scripts.md#design-for-an-agent) · **Solve, don't defer.**
- `SC-1` · [scripts.md#design-for-an-agent](scripts.md#design-for-an-agent) · **No "voodoo constants".**
- `SC-2` · [scripts.md#design-for-an-agent](scripts.md#design-for-an-agent) · **No interactive prompts.**
- `SC-2` · [scripts.md#design-for-an-agent](scripts.md#design-for-an-agent) · **A concise `--help`**
- `SC-2` · [scripts.md#design-for-an-agent](scripts.md#design-for-an-agent) · **Structured output**
- `SC-2` · [scripts.md#design-for-an-agent](scripts.md#design-for-an-agent) · **Predictable output size.**
- `SC-2` · [scripts.md#design-for-an-agent](scripts.md#design-for-an-agent) · **Safe to repeat.**
- `SC-3` · [scripts.md#how-to-reference](scripts.md#how-to-reference) · **State prerequisites**
- `SC-3` · [scripts.md#self-contained-dependencies](scripts.md#self-contained-dependencies) · **Declare them inline.**
- `SC-3` · [scripts.md#self-contained-dependencies](scripts.md#self-contained-dependencies) · **Installing packages depends on the surface.**
- `SC-3` · [surfaces.md#runtime-limits-by-surface](surfaces.md#runtime-limits-by-surface)
- `SC-4` · [body-and-structure.md#structure-and-supporting-files](body-and-structure.md#structure-and-supporting-files) · **Say whether to run or read a script**
- `SC-4` · [scripts.md#how-to-reference](scripts.md#how-to-reference) · **List and show the command.**
- `SC-4` · [scripts.md#when-to-bundle](scripts.md#when-to-bundle)
- `SC-5` · [workflows.md#validation-loop](workflows.md#validation-loop)
- `SC-5` · [workflows.md#plan-validate-execute](workflows.md#plan-validate-execute)
- `SC-6` · [scripts.md#design-for-an-agent](scripts.md#design-for-an-agent) · **Exit 0 when Claude needs the output.**
- `CF-2` · [claude-code-features.md#substitutions-and-pre-approved-tools](claude-code-features.md#substitutions-and-pre-approved-tools) · **Name the exact command.**
- `CF-2` · [claude-code-features.md#substitutions-and-pre-approved-tools](claude-code-features.md#substitutions-and-pre-approved-tools) · **Scope of the grant.**
- `CF-7` · [claude-code-features.md#substitutions-and-pre-approved-tools](claude-code-features.md#substitutions-and-pre-approved-tools) · **Where the path placeholders are substituted.**
- `CF-8` · [workflows.md#when-a-skill-runs-other-agents](workflows.md#when-a-skill-runs-other-agents)
- `CF-8` · [claude-code-features.md#substitutions-and-pre-approved-tools](claude-code-features.md#substitutions-and-pre-approved-tools) · **Not after a subagent's result.**
- `CF-5` · [claude-code-features.md#forked-subagents](claude-code-features.md#forked-subagents) · **Forked subagent**
- `CF-5` · [claude-code-features.md#forked-subagents](claude-code-features.md#forked-subagents) · **Forks on Explore or Plan.**
- `TE-8` · [evaluation.md#plugin-eval-suites](evaluation.md#plugin-eval-suites)

## Method

1. Read the area file each pointer names, including one your contract doesn't list, at the step that uses it.
2. Read every script in the inventory in full, from its first line to its last; never run one.
3. For each script, walk its paths: no input, bad input, a missing dependency, a failure halfway. Note what it prints, where (stdout or stderr), how much, and with which exit code.
4. For each script, find the line in `SKILL.md` or a reference that calls or names it, and check that the line says whether to run or read it and gives the exact command.
5. For each dependency a script or command needs, check that the skill declares it and that every surface the brief lists can provide it.
6. Read `allowed-tools` against every command the body runs: each grant names an exact command, and nothing broader.
7. When the skill runs forked (`context: fork`), read it as the subagent would, without the conversation: it has an explicit task and, on Explore or Plan, every rule it needs.
8. Plugin eval cases: for each case the brief lists, read `prompt.md`, `case.yaml` and its graders as `claude plugin eval` would run them, against the rules of the plugin eval suites.
