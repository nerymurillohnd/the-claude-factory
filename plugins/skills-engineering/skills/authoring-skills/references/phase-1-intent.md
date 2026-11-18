# Phase 1: Intent

How to capture the requester's full intent, goal and use cases before anything is designed.

The requester's part is to say what they want; yours is to understand it fully and deliver a skill that achieves it.

1. Read the request and everything given with it, in full, even when it looks simple. Separate what is asked, what lies behind it, what it implies and covers (who, where, with what inputs, what must not change) and what success looks like.
2. If the work was done in this conversation or exists in the project (runbooks, style guides, review comments), extract the corrections first, then the steps that worked, the formats accepted and the context supplied. Each correction becomes a rule or a gotcha.
3. State the goal in one sentence: what the model must do, for whom, and why it doesn't do it well today.
4. Write two or three use cases, each with a trigger, steps and a result someone can check, such as a file that exists or a count that matches. They guide the design and the self-review.
5. Where any part of the intent is unclear, ask instead of filling the gap: with `AskUserQuestion`, or in your reply where it isn't available. Ask only for what the requester alone knows, such as who uses the skill, what goes wrong today, a good result, what stays under their control or which systems it touches, each with your recommended answer, in as many rounds as the intent needs and only where the answer changes what you build. Never ask design questions, such as which fields or what name: those are yours. Use the requester's words, and explain a term like "frontmatter" when they show no sign of knowing it.

Exit: the requester confirms the goal and the use cases, and no open question would change what you build. Design nothing before this exit.
