# Phase 9: Independent domain review (steps)

## 9.1 Reviewer conditions

1. Launch one reviewer per package, several in parallel.
2. Start each reviewer without the user's settings, hooks, plugins, MCP servers, or memory. Plugin agents meet this only in part: see Limits to declare in SKILL.md for what is and is not isolated.
3. Restrict each reviewer to read-only tools.
4. Require a strict response format.
5. Set a time limit, a turn limit, and, if the user asks, a spend limit for each reviewer. The turn limit holds by instruction only until the agents set `maxTurns`: see Limits to declare.
6. During this phase reviewers may inspect shared repository evidence, but must not audit another reviewer's files or consume their findings.

The full-read requirement (9.2), the reviewer procedure and safeguards (9.3), and the finding format (9.4) are carried out by `instruction-reviewer` (domains A to E). Its definition is `agents/instruction-reviewer.md` at the plugin root.
