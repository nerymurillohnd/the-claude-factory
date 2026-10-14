# Step 1: Clarify intent

Work out what the user wants and why, from what they said and what you already know, and ask only what would change the prompt. Technical choices stay yours.

## Contents

- Read the request
- Understand the user
- Ask in one clarify round
- Decide when to proceed

## Read the request

Determine whether the user needs:

- A new prompt.
- A rewrite or refinement.
- An audit of an existing prompt: list its problems before the fixed version, and say in the design notes how each was fixed.
- A prompt adapted to another model or environment.
- A reusable instruction artifact.
- A multi-stage prompting workflow.

For follow-ups, use the existing objective and prior deliverables. Do not restart discovery unless the goal or circumstances have changed.

## Understand the user

- Treat brief, ambiguous or unstructured requests as starting points, not as failures by the user.
- Identify, from the whole request:
  - what must happen and why, and for whom;
  - where and how the prompt will be invoked: a chat, a command, an agent, a system prompt, a pipeline;
  - the inputs it will receive: files, images, web pages or other external content;
  - the tools and capabilities it needs;
  - the constraints, including restrictions, safety rules and rules the user calls non-negotiable;
  - any structure, phases or order the user intends;
  - the methods or decision criteria the user prefers;
  - what evidence would show success, and which quality dimensions matter most: accuracy on edge cases, consistency, relevance, tone, privacy, use of the given context, latency, cost.
- A request can mix a draft and an idea: the idea is the goal, the draft is material to work on.
- Read the form as well as the words: a point the user repeats is a priority, and a jump or an unfinished sentence marks a gap to fill from context or to ask about. Note the languages the user mixes and the domain terms they use: keep their terms in the prompt.
- Use what the conversation and the accessible project materials already hold; do not ask for information already provided.
- Distinguish confirmed information from assumptions, and do not invent preferences, project facts, available tools or requirements.
- Check a fact the user states when the material they shared or an official page can confirm it, and say which you checked. Record any other fact as the user's statement: running tools on their project to check it slides into doing the task.
- When material the user attached does not match what they described, name the mismatch and ask before building on it.

## Ask in one clarify round

- Ask only questions whose answers would materially change the prompt or the recommendation: at most four in the round, fewer when possible. Questions about the language the target model answers in, and about the surface, plan, platform or data retention that the model choice depends on, count within that limit. When more than four matter, ask in this order: the objective and what a good result looks like, where the prompt will run, the constraints, the output language.
- Ask about what the user knows: their circumstances, where they will use the prompt, their priorities and boundaries, and what a good result looks like. Handle technical choices yourself unless they need a user decision about cost, access, risk or authorization.
- Prompt engineering has three prerequisites. Ask for a missing one in this round, in the user's terms, only when its answer would change the prompt; otherwise state it as an assumption: success criteria ("what does a good result look like?"), a way to test them ("how will you tell it worked?"), and a first draft (the user's own when they bring one; otherwise the prompt you write is the draft). A missing prerequisite is a question to ask, never a reason to refuse.
- When the user names something Claude loads (a command, a skill, an agent) and it is unclear whether they want that file or a prompt so Claude creates it, ask which, in their terms.
- When the request is unclear, state your interpretation in a sentence, and pair each question with your proposed direction and its reason.

## Decide when to proceed

- Proceed as soon as the objective is clear enough; a clear request goes straight to the next step.
- For low-risk ambiguity, proceed with a brief, explicit assumption. An assumption is low-risk when getting it wrong changes only wording or format, not the objective, the target model, the actions the prompt authorizes, or legal, financial or safety content. Never proceed under any other assumption: when the answers leave one, ask one follow-up, of at most two questions, only about that point. That follow-up is the last question before writing.
- Once the user approves something, act on it; do not ask them to confirm it again.
