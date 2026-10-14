# Step 3: Select the session mode

Recommend the kind of session the user should run the prompt in, with a reason; you never run it yourself. Decide before writing, because the session mode changes what the prompt says.

## Contents

- Interactive or non-interactive
- Plan mode or execution
- How the mode changes the prompt
- In the reply

## Interactive or non-interactive

- **Interactive:** a Claude app conversation or a Claude Code session the user follows. Recommend it when the user will steer, review intermediate results or answer questions.
- **Non-interactive:** the prompt runs to the end with nobody answering. Recommend one of these:
  - **A single API call** for extraction, classification, transformation and pipelines.
  - **Claude Code non-interactive mode** (`claude -p`, or the Agent SDK) for CI jobs, scripts and scheduled runs: it executes one prompt and exits.
  - **A long-running autonomous agent** when the task is large, well specified and nobody will be watching.

## Plan mode or execution

These modes apply to Claude Code sessions (the CLI, the desktop app's Code tab, the IDE extensions, cloud sessions).

- **Plan mode:** Claude reads files and runs read-only commands to explore, then proposes a plan without editing the source; the user approves the plan before anything changes. Recommend it when the approach is uncertain, the change spans several files, the code is unfamiliar to the user, or the user wants to review consequential changes before they happen. Tell the user how to enter it: `Shift+Tab`, `/plan` before the prompt, or `claude --permission-mode plan`.
- **Execution:** Claude carries out the prompt directly. Recommend it when the scope is clear and the change is small: if the diff fits in one sentence, skip the plan, because planning adds overhead. Recommend it too when the prompt itself already gates its phases on the user's approval.
- **Non-interactive runs use execution.** A plan needs someone to approve it.
- **Never recommend a permission mode for execution** (manual, accept edits, auto, don't ask, bypass): that is the user's own preference. Write the prompt so it holds under any of them: put the approval gates for risky or irreversible actions in the prompt itself.
- **In the Claude app**, where these modes do not apply, write the prompt to deliver the plan first and wait for the user's go-ahead when the user should review before anything changes.

## How the mode changes the prompt

| Mode | Write the prompt to… |
| :-- | :-- |
| Interactive | allow clarifying questions and check-ins at the points where the user's answer changes the work; leave out the target model's unattended-run blocks |
| Non-interactive | make every decision itself: state the assumptions to take, never ask the user, and say what to do when blocked; include the target model's unattended-run guidance from its prompting files, and give the harness handling they describe in the setup |
| Plan mode | ask for exploration and a plan the user can approve (what will change, in which files, in what order, how it will be checked), not for edits |
| Execution | ask for the work itself, with its success criteria and the checks to run before reporting it done |

For any non-interactive run, tell the user to put the full specification in the first turn.

## In the reply

Set `session_mode` and `claude_code_mode` in the deliverable's metadata, and give the session mode in the reply's "Session mode" line: interactive or non-interactive, plan mode or execution for Claude Code, the one reason that decided it, and how to start that mode.
