# Lessons from real prompt-writing sessions

Read before clarifying any request. Each lesson comes from a real session: what happened, why it failed or worked, and how it applies to the prompts you write now.

## Contents

- Writing the prompt
- Working with the user

## Writing the prompt

### Aspiration is not specification

- **What happened:** A draft for an audit-agent team asked for audits "at the level of" named security firms. Most of the text was firm names.
- **Why it failed:** Neither the agent nor the user could check whether the instruction was met. It cost tokens and steered nothing.
- **How it applies:** Replace prestige references and adjectives with verifiable criteria and a definition of done the output can be checked against.

### Let the target model discover what only it can see

- **What happened:** The first rewrite of that prompt fixed the agent structure, tools, and installed plugins. The user pushed back: the structure was being defined without knowing what was on their machine.
- **Why it failed:** The prompt froze guesses about an environment the target model could inspect directly.
- **How it applies:** State the environment as a hypothesis to verify and the limits of authority as binding. Fix the interface, the definition of done, and the boundaries; let the target model discover the implementation details.

### Detail where the domain needs it

- **What happened:** In the same session the user called the prompt "too basic" and supplied full checklists for each audit area.
- **Why it failed:** Discovery replaces facts about the machine, not domain standards. Thin criteria produce thin audits.
- **How it applies:** Be lean on what the target model can discover and rich on the standards, checks, and criteria it cannot infer.

### Do not freeze facts the target model was asked to research

- **What happened:** A user asked for a prompt that would research each social platform's current profile and limits. The delivered prompt hardcoded the character limits instead.
- **Why it failed:** It contradicted the request and froze values that change.
- **How it applies:** When the user wants live research, the prompt instructs the target model to research and cite current values, not to use embedded ones.

### Verify the brief's facts, in both directions

- **What happened:** In an environment-setup prompt, Claude correctly fixed the OS edition from the real system, but claimed a language version was the latest stable before searching; a newer one had shipped.
- **Why it matters:** Correcting the user from memory is as damaging as copying their mistakes.
- **How it applies:** Check stated facts against evidence or a search before accepting or contradicting them, and say which you did.

### Sequence by root cause and gate each phase

- **What worked:** The same prompt put environment-variable repair in its own phase before any installation, because installing on a corrupted PATH caused recurring drift. Each phase was blocked until the previous one validated.
- **How it applies:** For repair, migration, or setup work, order phases so causes are fixed before symptoms, and gate progress on explicit validation.

### Drop rhetorical role framing

- **What worked:** Removing "you are legendary"-style framing from a draft in favor of a precise role, constraints, and protocol.
- **How it applies:** One accurate sentence of role plus concrete constraints; no flattery or hype.

### When the input does not match the description, ask first

- **What worked:** The attached document did not match what the user described. Claude named the mismatch and asked before building. Once confirmed, it preserved the document verbatim, prioritized completeness and sequencing over speed, and kept every phase read-only until the user approved writes per batch.
- **How it applies:** Name input mismatches before writing. When the user says "without omitting anything," preserve source material verbatim inside the prompt. Gate writes behind the user's approval for repository work.

### Respect the platform's hard constraints

- **What happened:** A skill was delivered with a reserved word in its name and a description over the 1,024-character limit, right after Claude had cited both constraints.
- **Why it failed:** The constraint was known and not checked.
- **How it applies:** When a prompt produces configuration, skills, or files governed by platform rules, check those rules before delivering and instruct the target model to verify them against current docs.

### Final versions, not proposals

- **What happened:** A user asked for deliverables "to officialize," derived from an audit, with no invented specifications.
- **How it applies:** When the user wants final output, the prompt says so, requires deriving content from the stated sources, and forbids drafts, options, and hedging.

### Proportionality

- **What worked:** A rule from an earlier prompt library: "a one-line fix doesn't need an MCP inspection pipeline."
- **How it applies:** Scale phases, gates, and verification to the risk of the task.

### Computer-use prompts start with a state check

- **What happened:** Claude opened a browser through desktop control without checking what was running and disrupted the user's work.
- **How it applies:** Prompts that drive a desktop or browser start by observing current state and avoid touching windows or processes outside the task.

### Domain facts come from the canonical source

- **What worked:** For prompts about a business's products, pointing the target model to the business's canonical source (a reference skill or named files) instead of embedding product facts from memory.
- **How it applies:** Product facts, IDs, prices, counts, and contacts change. The prompt names the canonical source and tells the target model to use its values verbatim. Compliance or framing rules the user states for their domain go in the prompt as hard constraints.

### Reasoning, not procedure

- **What happened:** Each failure in a prompt-writing skill was patched with another rule: a mandatory template, numbered checks, validators. The user rejected it: a task that is about understanding had been turned into a procedure, and a review then found new contradictions caused by the added mechanics.
- **Why it failed:** Rigid procedures crowd out judgment where the task needs it, and every added rule can collide with another.
- **How it applies:** When the task calls for judgment, state the purpose, the reason and the boundaries, and let the target model reason. Keep exact steps for what is fragile (commands, sequences, formats).

### Do not invent frameworks or terminology

- **What happened:** A design introduced "three kinds of prompt" that no documentation defines. The user asked whether there really were three kinds; there were not, and the label had confused more than it clarified.
- **Why it failed:** An invented taxonomy reads as established fact and forces later text to follow it.
- **How it applies:** Use the user's words and the documentation's terms. Introduce a category or label only when the task needs it, and define it where it first appears.

### Say exactly what is and is not done

- **What happened:** An instruction said "this skill never carries out the user's request", when the user's request was the prompt itself. The user flagged it as ambiguous.
- **Why it failed:** A broad negation contradicted the very thing the text was for.
- **How it applies:** When a prompt sets a limit, name precisely what the model does and what it leaves alone, rather than a sweeping "never".

## Working with the user

- **Deliver only what was asked.** A request for a short social caption got a full video analysis. Scope your reply to the request, and scope the prompts you write the same way.
- **Do not re-confirm approved content.** Once the user approves something, act on it; repeated confirmation rounds on approved material wear the user out.
