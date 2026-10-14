# Step 7: Follow-ups, only when they apply

Use this step when the task's nature and goals need more than one prompt, because the next instructions depend on a result nobody has seen yet. Deliver the first prompt complete, draft the follow-ups after it, and revise each draft when the user brings back the output it depends on.

## Contents

- When to use follow-ups
- Draft the follow-ups
- When the user returns

## When to use follow-ups

- Default to one self-contained prompt; the target model can work through phases and wait for approval inside it.
- Use follow-ups only when reviewing an intermediate result will change the next instructions: an audit before the fix, a plan before the build, a first draft before the revision.
- A fixed automated sequence, whose stages can all be written now, is not a follow-up: write all its stages in Step 5.

## Draft the follow-ups

- Write the first prompt complete and final, like any other deliverable.
- Write each follow-up as a draft after it, in the order it would run. Mark it **Draft** above its block, give it no metadata until it is finalized, and never present it as ready to paste.
- Above each draft, state what it waits for: the artifact the user should bring back, what you will assess in it, and the decision that assessment enables.
- Write the drafts from what is known now, and name the assumptions about the earlier output that each draft rests on, so the user can see what may change.
- Tell the user they can come back with the output to have the next draft checked and adjusted, or run the drafts as they are at their own risk.

## When the user returns

When the user brings back an output, or describes output that disappointed them, even as the first request:

- Compare it with the objective and success criteria.
- Identify what worked and what failed.
- Distinguish prompt problems from missing context, configuration issues, unavailable capabilities, or execution failures.
- Recommend the smallest effective correction, and preserve instructions that already work.
- Then either revise the prompt (raise its `version`), or finalize the next follow-up from its draft: adjust it to what the output showed, check the assumptions it rested on, and deliver it complete with its metadata.

Do not add instructions merely to make the prompt look more comprehensive.
