# The /goal handoff

Read this when the handoff includes a `/goal` condition: a plan in Claude Code with more than one task and one measurable end state.

## How /goal works

- After each turn, a small fast model checks the condition and keeps Claude working until it holds or is judged impossible.
- The evaluator reads only the conversation. It runs no commands and reads no files, so the condition must ask for evidence printed in the conversation.
- Only the user can type `/goal`; Claude can't invoke it. One goal per session. It doesn't change the permission mode.
- It is unavailable in chat, when hooks are disabled (`disableAllHooks`, or managed settings with `allowManagedHooksOnly`), and without workspace trust.

## When not to give one

- The work has no single measurable end state.
- The plan has one task.
- A goal is already active in the session.
- Any of the unavailable cases above.

In those cases the plan gate and the final report prove completion on their own.

## The condition

Write the plan first; the condition points to it. It never carries the plan, because it holds at most 4,000 characters. Fill every line and keep the whole condition well under the limit:

```text
/goal Execute the approved plan at <plan file path>, task by task, passing each task's check before the next. First invoke the work-lifecycle:planning-before-execution skill and follow its Execution section.
Task: <one line: what gets built or changed>
Done when: <one measurable end state, proven by output printed in this conversation, such as `npm test` exits 0 and a final report listing each task's check command and result>
Solves: <the problem this resolves>
Why it matters: <the impact, so Claude can make sound calls the plan leaves open>
Constraints: <what must not change; stop and ask before push, deploy, publishing, messages to third parties or spending>
```

- Plan file path: the path Claude Code gave for the plan file. When the plan is only in the reply, write "the approved plan above".
- Done when: name output Claude prints, never "the plan is complete", which the evaluator can't see.
- Why it matters: explaining the motivation helps Claude generalize to the cases the plan doesn't cover.
- Constraints: repeat the plan's authorization checkpoints.

After the condition, say that it is well under the 4,000-character limit, with its approximate length to the nearest 50 characters, and tell the user that typing it is their go-ahead to execute.
