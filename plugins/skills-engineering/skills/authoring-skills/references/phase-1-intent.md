# Phase 1: Understand the user's intent

How to understand what the user wants (Scenario A), propose a skill for a repeated process (Scenario B), or understand what to change in an existing skill (Scenario C), before you design anything.

## Gotchas

- A process you just performed carries its accidents: a command that failed once for a network or permission reason, or a tool missing in this environment, is not a rule of the process. Before a skill you propose in Scenario B states such a limit, check that it holds beyond this session, or leave it out.

## Scenario A: user request

1. Understand
   - Unfold what the user is asking for, and the related work already done in the conversation or the project, if any.
   - Work out what is behind the words: what the user wants, what the request covers and what it implies.
   - Work out the goal the skill must meet.
   - Identify the domain: the field of knowledge the skill works in (e.g., code, auditing, workflows, productivity, databases, APIs, etc.).
2. Ask
   - Ask the user for the context you need when something is missing or unclear.
   - Ask about context only. Decide the technical matters yourself, such as how to build it, what to name it and which fields it needs.
3. Challenge
   - Tell the user when part of the request doesn't apply, is deficient, or has a better way to reach the same goal, and propose it.
   - The decision is theirs.
   - Build only what serves the user's goal.
4. No one to ask
   - In a subagent, or a run with nobody to answer, state each assumption in your reply and go on.
5. Move on
   - Go to Phase 2 only when you can state the goal, what the skill is, what it must achieve or teach Claude, and why it should exist.

## Scenario B: repeated process

The process can be a task that will repeat across sessions, or a procedure you just performed that may serve the user again.

1. Pause
   - Stop the work in progress when you detect the process.
2. Explain
   - Tell the user what you detected, based on the work already done.
   - Explain what a skill is and why you propose one for it: what you saw, and why it will repeat.
   - Explain why it is worth having: the same result every time, and the work it saves.
3. Ask
   - Ask whether they want a skill for it.
4. Wait for approval
   - Wait for the user's answer before you do anything else.
5. Act on the answer
   - If the user says yes, or adds comments, continue with their comments and go to Phase 2.
   - If the user says no, end here and leave this skill.

## Scenario C: existing skill

The request can be the user's own, or the improvements and corrections an audit recommended.

1. Understand
   - Read the existing skill whole, first line to last, with every file it points to.
   - Unfold what the user asks to change, or what the audit recommended, and the goal of the change.
2. Verify the findings
   - When the request follows an audit, check each finding against the skill and the official sources, since a finding can be wrong.
   - Tell the user which findings you reject and why.
3. Ask
   - Ask the user for the context you need when something is missing or unclear.
   - Ask about context only. Decide the technical matters yourself.
4. Challenge
   - Tell the user when part of the request is deficient, or has a better way to reach the same goal, and propose it.
   - The decision is theirs.
   - Change only what serves the goal.
5. No one to ask
   - In a subagent, or a run with nobody to answer, state each assumption in your reply and go on.
6. Move on
   - Go to Phase 2 only when you can state what changes, why, and what stays.
   - Keep the skill's name and folder unless the user asks otherwise.
