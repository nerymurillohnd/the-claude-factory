# Orchestrate subagents at scale with dynamic workflows

> Dynamic workflows orchestrate many subagents from a script Claude writes and the user can rerun. Use them for codebase audits, large migrations, and cross-checked research. This file covers when to use a workflow, how runs are approved, saved, distributed in a plugin, and parameterized, what the script looks like and the rules for editing it, runtime limits, and how runs are managed, resumed, and turned off.

## Contents

- [Availability](#availability)
- [What a workflow is](#what-a-workflow-is)
- [When to use a workflow](#when-to-use-a-workflow)
  - [Watch the run](#watch-the-run)
- [Have Claude write a workflow](#have-claude-write-a-workflow)
  - [Ask for a workflow in your prompt](#ask-for-a-workflow-in-your-prompt)
  - [Approve the plan before it runs](#approve-the-plan-before-it-runs)
  - [Save the workflow for reuse](#save-the-workflow-for-reuse)
  - [Distribute a workflow in a plugin](#distribute-a-workflow-in-a-plugin)
  - [Pass input to a saved workflow](#pass-input-to-a-saved-workflow)
- [Example workflow prompts](#example-workflow-prompts)
  - [Audit many files for the same issue](#audit-many-files-for-the-same-issue)
  - [Keep fixing until a check passes](#keep-fixing-until-a-check-passes)
  - [Migrate many files in parallel](#migrate-many-files-in-parallel)
  - [Review every changed file and write one summary](#review-every-changed-file-and-write-one-summary)
  - [Research a topic across many sources](#research-a-topic-across-many-sources)
  - [Find issues until the list stops growing](#find-issues-until-the-list-stops-growing)
  - [What the saved script looks like](#what-the-saved-script-looks-like)
  - [Edit a saved script](#edit-a-saved-script)
- [How a workflow runs](#how-a-workflow-runs)
  - [Prompt caching in a fan-out](#prompt-caching-in-a-fan-out)
  - [Behavior and limits](#behavior-and-limits)
- [Manage runs](#manage-runs)
  - [Resume after a pause](#resume-after-a-pause)
    - [Which agents run again](#which-agents-run-again)
  - [When an agent stalls and restarts](#when-an-agent-stalls-and-restarts)
  - [Cost](#cost)
  - [Turn workflows off](#turn-workflows-off)
- [Documentation References](#documentation-references)

## Availability

> **Note:** Dynamic workflows are available on all paid plans, with Anthropic API access, and on Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry. On Pro, turn them on from the Dynamic workflows row in `/config`.

## What a workflow is

A dynamic workflow is a JavaScript script that orchestrates many [subagents](https://code.claude.com/docs/en/sub-agents.md) at once. Claude writes the script for the task the user describes, and a runtime executes it in the background while the session stays responsive.

Use a workflow when a task needs more agents than one conversation can coordinate, or when the orchestration should be codified as a script that can be read and rerun. Examples include a codebase-wide bug sweep, a 500-file migration, a research question that needs sources cross-checked against each other, and a hard plan worth drafting from several independent angles before committing to one.

## When to use a workflow

[Subagents](https://code.claude.com/docs/en/sub-agents.md), [skills](https://code.claude.com/docs/en/skills.md), [agent teams](https://code.claude.com/docs/en/agent-teams.md), and workflows can all run a multi-step task. The difference is who holds the plan:

| | Subagents | Skills | Agent teams | Workflows |
| :- | :- | :- | :- | :- |
| What it is | A worker Claude spawns | Instructions Claude follows | A lead agent supervising peer sessions | A script the runtime executes |
| Who decides what runs next | Claude, turn by turn | Claude, following the prompt | The lead agent, turn by turn | The script |
| Where intermediate results live | Claude's context window | Claude's context window | A shared task list | Script variables |
| What's repeatable | The worker definition | The instructions | The team definition | The orchestration itself |
| Scale | A few delegated tasks per turn | Same as subagents | A handful of long-running peers | Dozens to hundreds of agents per run |
| Interruption | Restarts the turn | Restarts the turn | Teammates keep running | Resumable in the same session |

A workflow moves the plan into code. With subagents, skills, and agent teams, Claude is the orchestrator: it decides turn by turn what to spawn or assign next, and every result goes into a context window. A workflow script holds the loop, the branching, and the intermediate results itself, so Claude's context holds only the final answer.

Moving the plan into code also lets a workflow apply a repeatable quality pattern, not just run more agents: it can have independent agents adversarially review each other's findings before they are reported, or draft a plan from several angles and weigh them against each other, for a more trustworthy result than a single pass.

### Watch the run

Workflows run in the background, so the session stays responsive while agents work.

- Run `/workflows` at any time to list running and completed workflows, then select one to open its progress view.
- When the session has only one run, `/workflows` skips the list and opens that run.
- To stop a running workflow from the list without opening it, select it and press `x`.

The progress view shows each phase with its agent counts. The footer lists the key for each action:

| Key | Action |
| :- | :- |
| `↑` / `↓` | Select a phase or agent |
| `Enter` or `→` | Drill into the selected phase, then into an agent's detail. In the detail, `Enter` expands or collapses it |
| `Esc` or `←` | Back out one level |
| `j` / `k` | Scroll within the agent detail when it overflows |
| `f` | Filter the agent list in the selected phase by status. Press again to cycle |
| `p` | Pause or resume the run |
| `x` | Stop the selected agent, or stop the whole workflow when focus is on the run |
| `r` | Restart the selected running agent |
| `s` | [Save](#save-the-workflow-for-reuse) the run's script as a command |

The agent detail lists the agent's prompt, its recent tool calls, and its result. Each call shows its state, such as still running or failed. When the agent keeps a task list of its own, the detail shows it too, with each task's status.

Press `Enter` to expand the detail. The prompt and result then show in full, and each listed call shows its input and the start of its result.

## Have Claude write a workflow

There are two ways to have Claude write a workflow for a task:

* [Ask for a workflow](#ask-for-a-workflow-in-your-prompt) in the prompt, either in plain words or by including the keyword `ultracode`, and Claude writes one for the task.
* [Let Claude decide with ultracode](https://code.claude.com/docs/en/workflows#let-claude-decide-with-ultracode): set `/effort ultracode` and Claude plans a workflow for every substantive task in the session.

A workflow command that already exists can also be run: a [bundled workflow](https://code.claude.com/docs/en/workflows#bundled-workflows) like `/deep-research`, or one that has been [saved](#save-the-workflow-for-reuse).

### Ask for a workflow in your prompt

To run a single task as a workflow without changing the session's effort level, include the keyword `ultracode` in the prompt. A direct request in plain words, for example "use a workflow" or "run a workflow", also works: Claude treats it as the same opt-in.

```text wrap theme={null}
ultracode: audit every API endpoint under src/routes/ for missing auth checks
```

Claude Code highlights the keyword in the input, and Claude writes a workflow script for the task instead of working through it turn by turn. The keyword only chooses how Claude structures the work: the agents' tool calls receive the same permission checks and [sandboxing](https://code.claude.com/docs/en/sandboxing.md) as any other tool call in the session.

If the run does what was wanted, [save it as a command](#save-the-workflow-for-reuse) afterward. If an orchestrator already exists in another form, such as a folder of subagent prompts or a skill that fans work out, point Claude at it and ask for a workflow that does the same thing.

### Approve the plan before it runs

In the CLI, the per-run prompt shows the planned phases and these options:

* **Yes, run it**: start the run
* **Yes, and don't ask again for `<name>` in `<path>`**: start, and skip this prompt for this workflow in this project from now on. Claude Code offers this option when a bundled, saved, or plugin workflow is run by name, not for a script Claude wrote for the current task.
* **View raw script**: read the script before deciding
* **No**: cancel

`Ctrl+G` opens the script in the editor. With **Yes, run it** or **No** selected, press `Tab` to [add a comment](https://code.claude.com/docs/en/permissions.md#add-a-comment-when-you-answer-a-permission-prompt) to the answer.

Whether this prompt appears depends on the [permission mode](https://code.claude.com/docs/en/permission-modes.md):

| Permission mode | When you're prompted |
| :- | :- |
| Auto | First launch only. Any **Yes** records consent in your user settings, and later launches start without prompting. Skipped entirely when ultracode is on |
| Manual, accept edits | Every run, unless you've selected **Yes, and don't ask again** for that workflow in this project |
| Bypass permissions | Claude Code doesn't prompt you. The run starts immediately |
| `claude -p`, Agent SDK | Claude Code doesn't prompt you |

In `claude -p` and the Agent SDK, Claude Code never shows this prompt. It runs the Workflow tool call through the same [permission evaluation](https://code.claude.com/docs/en/agent-sdk/permissions.md#how-permissions-are-evaluated) as the rest of the session, so deny rules, ask rules, and `dontAsk` mode apply to the launch as they apply to every tool call. To let the workflow start in these runs, use one of these:

* **Permission rule**: add `Workflow` to the allow rules to approve every workflow, or `Workflow(<name>)` to approve one saved workflow by name.
* **Auto permission mode**: run in [auto mode](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode), where the classifier reviews the call and can approve it.
* **Bypass permissions mode**: run in bypass permissions mode.
* **A hook**: return `"allow"` for the call from a [`PreToolUse`](https://code.claude.com/docs/en/hooks#pretooluse) hook. In [plan mode](https://code.claude.com/docs/en/permission-modes.md#analyze-before-you-edit-with-plan-mode), the workflow does not start on the hook's approval alone, so use a permission rule or the host's approval there instead.
* **The host**: a [`--permission-prompt-tool`](https://code.claude.com/docs/en/cli-reference#cli-flags) or, with the Agent SDK, a [`canUseTool`](https://code.claude.com/docs/en/agent-sdk/permissions) callback approves it.

In the Desktop app, an approval card shows the workflow name, the phase list, and a token-usage caution, with **Once**, **Always**, and **Deny** actions. The progress view appears in the Background tasks side pane.

The subagents the workflow spawns use the user's [permission rules](https://code.claude.com/docs/en/settings-reference.md#permission-settings), and Claude Code picks their permission mode by the rules under [which permission mode a subagent runs in](https://code.claude.com/docs/en/sub-agents.md#permission-modes). To avoid prompts on a long run, add the tools the agents need to the allow rules before starting.

### Save the workflow for reuse

When Claude writes a workflow for a task that will be repeated, save that run's script as a command. A process like a review run on every branch then runs the same orchestration each time.

Run `/workflows`, select the run to keep, and press `s`. In the save dialog, Tab toggles between the two save locations:

* `.claude/workflows/` in the project: shared with everyone who clones the repo
* `~/.claude/workflows/` in the home directory: available in every project, visible only to the user. If [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/en/env-vars) is set, this location is the `workflows/` directory under that path.

The save dialog shows the resolved path for the personal location. Press Enter to save. The workflow runs as `/<name>` in future sessions from either location.

### Distribute a workflow in a plugin

To share a workflow across teams or repositories, include it in a [plugin](https://code.claude.com/docs/en/plugins/overview.md). Place the script in a `workflows/` directory at the plugin root, or point to a different location with the [`workflows` manifest field](https://code.claude.com/docs/en/plugins/manifest-reference#fields).

Plugin workflows are namespaced by the plugin name. A plugin called `acme-tools` containing a script whose `meta.name` is `release-audit` runs as `/acme-tools:release-audit`.

### Pass input to a saved workflow

A saved workflow can accept input through the `args` parameter. The script reads it as a global named `args`. Use it to supply a research question, a list of target paths, or a configuration object at invocation time instead of editing the script for each run.

The following prompt runs a saved workflow with a list of issue numbers:

```text wrap theme={null}
Run /triage-issues on issues 1024, 1025, and 1030
```

Claude passes the list as structured data, so the script can call array and object methods on `args` directly without parsing it first. If `args` is omitted, the global is `undefined` inside the script.

## Example workflow prompts

A workflow fits best when the task is larger than one agent can hold in context, or when the same step needs to run across many items. The prompts below show common shapes. Each one asks Claude to write and run a workflow for that task; the user does not write the script.

### Audit many files for the same issue

Fan out one agent per file, then collect and verify the findings.

```text wrap theme={null}
use a workflow to audit every route handler under src/routes/ for missing authentication checks, and adversarially verify each finding before reporting it
```

### Keep fixing until a check passes

Run a checker, fix what failed, and repeat until it passes or stops making progress.

```text wrap theme={null}
use a workflow to run npx tsc --noEmit and keep fixing the reported errors until the type check passes or two rounds in a row make no progress
```

### Migrate many files in parallel

Discover the files to migrate, transform each one in an isolated copy so edits do not conflict, and verify each result.

```text wrap theme={null}
use a workflow to migrate every component under src/components/ from JavaScript to TypeScript, working on each file in its own isolated copy
```

### Review every changed file and write one summary

Run a reviewer per file, then pass all the findings to one agent that ranks and deduplicates them.

```text wrap theme={null}
use a workflow to review every file changed in this PR for correctness issues, then merge the per-file findings into one ranked summary
```

### Research a topic across many sources

Fan out readers across changelogs, issues, and docs, then synthesize. The bundled `/deep-research` workflow does this; a narrower version can also be described.

```text wrap theme={null}
use a workflow to research how our three competitors handle rate limiting: read their public docs and recent changelog entries in parallel, then compare the approaches
```

### Find issues until the list stops growing

Keep searching in rounds and stop when new rounds turn up nothing new.

```text wrap theme={null}
use a workflow to find flaky tests in this repo: run the suite repeatedly, record which tests fail intermittently, and stop once two rounds in a row find nothing new
```

### What the saved script looks like

A [saved workflow](#save-the-workflow-for-reuse) file in `.claude/workflows/` holds a `meta` block followed by a script body that orchestrates subagents. It usually needs no editing; this is the shape of a small one, for recognizing what Claude generated:

```javascript theme={null}
export const meta = {
  name: 'audit-routes',
  description: 'Audit every route handler for missing auth checks',
}

const found = await agent('List every .ts file under src/routes/.', {
  schema: { type: 'object', required: ['files'], properties: { files: { type: 'array', items: { type: 'string' } } } },
})

const audits = await pipeline(found.files, file =>
  agent(`Audit ${file} for missing authentication checks.`, { label: file }),
)

return audits.filter(Boolean)
```

Script API:

- The body is plain JavaScript with top-level `await`.
- `agent()` spawns one subagent, `pipeline()` runs one per item in a list, and `parallel()` runs a set of agent tasks at the same time and waits for all of them.
- An `agent()` call resolves to `null` if it is stopped mid-run or hits an unrecoverable API error. `pipeline()` keeps each `null` in the results array, which is why the example ends with `.filter(Boolean)` to drop those entries, including the slot of [an agent that stalled on every attempt](#when-an-agent-stalls-and-restarts).
- In [auto mode](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode), the prompt a script passes to `agent()` does not count as a request from the user when the classifier reviews that subagent's actions, because Claude Code marks it as text the script computed.

Structured output with `schema`:

- If an `agent()` call passes a `schema`, that subagent returns JSON matching the shape instead of prose.
- Claude Code checks the schema before starting the subagent: when it can prove the schema contradicts itself, the call fails with an error naming the contradiction, and the subagent never starts. One contradiction it can prove is a `required` key that `additionalProperties: false` rules out.
- If the subagent's output still fails validation after five attempts, the call fails with an error that includes the last validation failure. To change the attempt count, set [`MAX_STRUCTURED_OUTPUT_RETRIES`](https://code.claude.com/docs/en/env-vars).

### Edit a saved script

To change a [saved workflow](#save-the-workflow-for-reuse), edit its `.js` file or ask Claude to make the change. Before editing or asking, run the `/workflow-authoring` [bundled skill](https://code.claude.com/docs/en/skills.md#bundled-skills) to load the script-writing reference Claude works from. The skill requires Claude Code v2.1.248 or later.

To run the edited version in the current session, run [`/reload-skills`](https://code.claude.com/docs/en/commands#all-commands) to re-read the workflow directories, then run `/<name>` again.

Claude Code applies these rules to each part of the file when it loads and runs the script:

* **`meta` block**: keep `export const meta` as the first statement, and keep it a plain object literal with a `name` and a `description`. If it contains anything other than literal values, such as a variable, a function call, or a spread, Claude Code drops `/<name>` from `/` autocomplete.
* **Body**: besides `agent()`, `pipeline()`, and `parallel()`, the body can call `phase()` to group the agents that follow under a title in the progress view, call `log()` to show a message above the phases, and read the [`args`](#pass-input-to-a-saved-workflow) global. If the body has a syntax error, Claude Code reports it when the workflow runs.
* **`phases`**: if they are listed in `meta`, give each entry exactly the title passed to `phase()`. A `phase()` title with no entry gets a progress group of its own.
* **Timestamps and randomness**: Claude Code makes `Date.now()`, `Math.random()`, and a no-argument `new Date()` throw inside the script, so that a [relaunched run](#resume-after-a-pause) repeats the same `agent()` calls. Pass a timestamp in through `args` instead.

The [script of a single run](#how-a-workflow-runs) can also be edited rather than the saved copy. [Resume after a pause](#resume-after-a-pause) covers which agents run again when an edited script is relaunched. For the Workflow tool's inputs, see its entry in the [Agent SDK reference](https://code.claude.com/docs/en/agent-sdk/typescript.md#workflow).

## How a workflow runs

The workflow runtime executes the script in an isolated environment, separate from the conversation. Intermediate results stay in script variables instead of landing in Claude's context.

- Unless Claude starts a run from a script file's path, Claude Code writes the run's script to a file under the session's directory in `~/.claude/projects/`. Claude receives the script's path when the run starts, so the user can ask for it. That file can be opened to read the orchestration Claude wrote, diffed against a previous run's script, or edited, after which Claude can relaunch from the edited version.
- Claude can start a workflow only from a script file the session is already allowed to read. To run a script kept outside the working directory, first add its directory with [`/add-dir`](https://code.claude.com/docs/en/permissions#working-directories) or a [Read allow rule](https://code.claude.com/docs/en/permissions.md#read-and-edit).
- The runtime tracks each agent's result as the run progresses, which is what makes a run [resumable](#resume-after-a-pause) within the same session.

### Prompt caching in a fan-out

Agents in the same run can read each other's [prompt cache](https://code.claude.com/docs/en/prompt-caching.md#subagents-and-the-cache). Two agents that run with the same model, effort level, agent type, tools, output schema, and working directory build the same tools-and-system-prompt prefix, so an agent that starts after a matching sibling's response has begun reads that sibling's cache on its first request.

### Behavior and limits

The runtime applies the following constraints:

| Constraint | Why |
| :- | :- |
| No mid-run user input | A run pauses on its own only for agent permission prompts and a [usage-limit wait](https://code.claude.com/docs/en/workflows#when-a-run-hits-your-usage-limit). For sign-off between stages, run each stage as its own workflow |
| No direct filesystem or shell access from the workflow itself | Agents read, write, and run commands. The script coordinates the agents |
| No module loading: a script that contains `import()` fails before the run starts | The script body is plain JavaScript. Put work that needs a library in an agent's task |
| Up to 16 concurrent agents by default, fewer when Claude Code has fewer CPUs available, including inside a CPU-limited container. To change the limit, set [`CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS`](https://code.claude.com/docs/en/env-vars#variables) to a value from 1 to 256, which requires Claude Code v2.1.269 or later | Bounds local resource use |
| In a fan-out, agents that share the first agent's prompt-cache prefix start up to 5 seconds after it by default | All but the first read the [prefix the first agent cached](#prompt-caching-in-a-fan-out) instead of each processing it uncached |
| Up to 4,096 items in a single `parallel()` or `pipeline()` call: the runtime rejects a longer list with an error | A silent cap would drop part of the workload without telling the script |
| 1,000 agents total per run | Prevents runaway loops |

## Manage runs

Once a run starts, manage it from the `/workflows` view, or by expanding its progress line in the task panel below the input box.

A stopped run stays in the task panel while any of its agents' processes are still running. Stopping it again makes Claude Code re-signal those processes.

### Resume after a pause

Resume a paused run from `/workflows` by selecting it and pressing `p`. For a stopped run, ask Claude to relaunch the workflow with the same script. If agents from the stopped run have not exited yet, Claude Code refuses the relaunch until they have, so a second copy of those agents cannot run alongside them.

#### Which agents run again

Claude Code replays the run in the order agents start, and each agent either returns its saved result or runs again:

* **Completed**: returns its saved result. The first agent whose prompt differs from the previous run, because the script was edited or an earlier agent returned something different, runs again, and so does every agent after it, even ones that completed.

  Before v2.1.305, completed agents could also run again when an unedited script was relaunched whose `pipeline()` items or `parallel()` tasks ran more than one agent each. To stop those reruns for new runs, update Claude Code.
* **Still running when stopped**: starts over. Stopping the whole run does not count any agent as failed.
* **Failed**: runs again, and so does every agent the script starts after it, even ones that completed. Stopping one agent alone, by selecting it in [`/workflows`](#watch-the-run) and pressing `x`, counts as failing.

That last case means a failure in the middle of a fan-out reruns work that already finished. If a script starts A, B, C, and D in that order and B fails, relaunching returns A from cache and runs B, C, and D again.

If a script that started A, B, C, and D is edited so that it starts A, C, B, and D, the second agent to start is now C, where the previous run started B. Relaunching returns A from cache and runs C, B, and D again.

### When an agent stalls and restarts

An agent whose output stops arriving for long enough starts over from the same prompt. In [`/workflows`](#watch-the-run), its name gains a `(retry 1)` suffix and its detail shows `attempt 2 (stalled)`. The restart is automatic and needs no action.

- The new attempt starts without the stalled attempt's transcript.
- Files the stalled attempt already changed stay changed, and the tokens it spent stay in the run's total.
- The stall window is how long Claude Code waits for output from an agent before it ends the attempt. Time the agent spends waiting on its own tool calls or on a [usage-limit reset](https://code.claude.com/docs/en/workflows#when-a-run-hits-your-usage-limit) does not count toward the stall window.

An agent restarts at most five times, counting any restart requested with `r`. If the sixth attempt stalls as well, the `agent()` call fails, and the start of the error says why:

* `agent stalled on all 6 attempts`: every attempt went the whole window without output. If the agent's work keeps it silent that long, lengthen the window
* `agent lost its reply on all 6 attempts`: every attempt's response stream went silent and Claude Code gave up waiting on it. Lengthening the stall window doesn't help, since a [streaming idle watchdog](https://code.claude.com/docs/en/network-config.md#streaming-idle-watchdogs) ended the response first and `CLAUDE_STREAM_IDLE_TIMEOUT_MS` sets that watchdog's timeout
* `agent abandoned after 6 attempts`: the attempts ended in different ways, which the error lists in order

To give an agent more time to produce output before the window ends:

* **One agent**: pass `stallMs` in milliseconds on its `agent()` call, such as `agent(prompt, { stallMs: 1800000 })` for 30 minutes
* **Every agent**: set [`CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS`](https://code.claude.com/docs/en/env-vars#variables), which also applies to subagents outside workflows

Whether the run continues after the failure depends on how the script called the agent:

* **Inside [`parallel()` or `pipeline()`](#what-the-saved-script-looks-like)**: the run carries on with `null` in place of the agent's result
* **Awaited directly**: the run ends with the error

To try again, ask Claude to relaunch the workflow. [Resume after a pause](#resume-after-a-pause) covers what runs again.

### Cost

A workflow spawns many agents, so a single run can use meaningfully more tokens than working through the same task in conversation. Runs count toward the plan's usage and rate limits.

To control spend:

- Before committing to a large task, run the workflow on a small slice first: one directory instead of the whole repo, or a narrow question instead of a broad one.
- The `/workflows` view shows each agent's token usage as the run progresses, and the run can be stopped there at any time, usually without losing completed work. [Resume after a pause](#resume-after-a-pause) covers what a stopped run keeps.
- The runtime's [agent caps](#behavior-and-limits) limit how many agents a single run can spawn, which bounds the cost of a runaway script.
- To keep runs to fewer agents, choose the `small` [size guideline](https://code.claude.com/docs/en/workflows#set-a-size-guideline).

Claude Code also flags a run that grows unusually large. When a workflow schedules more than 25 agents, or its projected token total passes 1.5 million, its progress line in the task panel below the input box shows a `Large workflow` warning. The warning points to [`/workflows`](#watch-the-run), where the run can be stopped.

Claude Code picks each workflow agent's model in the same [order it uses for subagents](https://code.claude.com/docs/en/sub-agents.md#choose-a-model). A model the script names for a stage counts as the per-invocation model in that order. When nothing else assigns one, the agent runs on the session's model.

### Turn workflows off

Workflows are available in the CLI, the Desktop app, the IDE extensions, [non-interactive mode](https://code.claude.com/docs/en/headless.md) with `claude -p`, and the [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md). The same disable settings apply on every surface.

When workflows are disabled:

* `/workflows`, the workflow commands, and the `/workflow-authoring` skill are unavailable
* The `ultracode` keyword no longer triggers a run, and the **Ultracode** toggle is removed from `/effort`

A run that was already in progress keeps going.

## Documentation References

- Source page: https://code.claude.com/docs/en/workflows (full workflows guide, including ultracode, bundled workflows, usage-limit waits, and size guidelines)
- https://code.claude.com/docs/en/sub-agents.md - create custom subagents, the worker primitive workflows orchestrate; subagent permission modes and model selection order
- https://code.claude.com/docs/en/skills.md - skills, including bundled skills such as `/workflow-authoring`
- https://code.claude.com/docs/en/agent-teams.md - agent teams compared with workflows
- https://code.claude.com/docs/en/sandboxing.md - sandboxing applied to agents' tool calls
- https://code.claude.com/docs/en/permissions.md - permission prompt comments, working directories, Read and Edit rules (also linked as https://code.claude.com/docs/en/permissions)
- https://code.claude.com/docs/en/permission-modes.md - auto mode, plan mode, and which modes prompt for a workflow
- https://code.claude.com/docs/en/agent-sdk/permissions.md - how the Agent SDK evaluates permissions and the `canUseTool` callback (also linked as https://code.claude.com/docs/en/agent-sdk/permissions)
- https://code.claude.com/docs/en/hooks - the `PreToolUse` hook
- https://code.claude.com/docs/en/cli-reference - CLI flags such as `--permission-prompt-tool`
- https://code.claude.com/docs/en/settings-reference.md - permission settings
- https://code.claude.com/docs/en/env-vars - `CLAUDE_CONFIG_DIR`, `MAX_STRUCTURED_OUTPUT_RETRIES`, `CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS`, `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS`
- https://code.claude.com/docs/en/plugins/overview.md - distributing workflows in a plugin
- https://code.claude.com/docs/en/plugins/manifest-reference - the `workflows` manifest field
- https://code.claude.com/docs/en/commands - all commands, including `/reload-skills`
- https://code.claude.com/docs/en/agent-sdk/typescript.md - the Workflow tool's inputs
- https://code.claude.com/docs/en/prompt-caching.md - subagents and the prompt cache
- https://code.claude.com/docs/en/network-config.md - streaming idle watchdogs
- https://code.claude.com/docs/en/headless.md - non-interactive mode with `claude -p`
- https://code.claude.com/docs/en/agent-sdk/overview.md - the Agent SDK
