# MCP elicitation events

Elicitation · ElicitationResult

Sources: https://code.claude.com/docs/en/hooks (read 2026-10-20) and the Claude Code CHANGELOG.md through v2.1.305; changelog-only facts are tagged *(changelog vX.Y.Z)*. Fields listed are in addition to the common input fields. Both support `command`, `http`, `mcp_tool` handlers only. Matcher → MCP server name.

Top-level `decision` from these two events was ignored from v2.1.105 until the fix in v2.1.284.

---

## Elicitation

Docs: [event](https://code.claude.com/docs/en/hooks#elicitation) · [input](https://code.claude.com/docs/en/hooks#elicitation-input) · [output](https://code.claude.com/docs/en/hooks#elicitation-output)

**Fires:** an MCP server requests user input mid-task. By default a dialog appears; a hook can answer instead.

**Input:** `mcp_server_name`, `message`, `mode?` (`form` or `url`), `url?`, `elicitation_id?`, `requested_schema?` (form: JSON Schema whose `properties` keys are the fields to fill).

**Output:** exit 0 and print `hookSpecificOutput` (`hookEventName: "Elicitation"`) with an `action`:

| Goal | Return | Server receives |
|---|---|---|
| Answer for the user | `action: "accept"`, `content: {<property>: value}` | accept + your content |
| Decline | `action: "decline"` | decline |
| Cancel | `action: "cancel"` | cancel |
| Leave it to the user | no output, exit 0 | the user's dialog answer |

In the dialog, Decline sends `decline` and Esc sends `cancel`. Accepting a URL-mode request skips the dialog, so the URL never opens. `reason`, `systemMessage`, `continue` are discarded.

**Other ways to decline:** exit 2 (any printed `hookSpecificOutput` is ignored) or top-level `decision: "block"` (overrides an `action` in the same output). With several matching hooks, a decline from any of them beats accept or cancel. Neither user nor server sees why.

**Pattern (answer one known form):** read stdin, compute `.requested_schema.properties // {} | keys`, and only when it equals exactly the expected field list print an accept; otherwise print nothing so the dialog appears. Confirm with `claude --debug`: the log line ends with `Elicitation resolved by hook: {"action":"accept",...}`.

---

## ElicitationResult

Docs: [event](https://code.claude.com/docs/en/hooks#elicitationresult) · [input](https://code.claude.com/docs/en/hooks#elicitationresult-input) · [output](https://code.claude.com/docs/en/hooks#elicitationresult-output)

**Fires:** after the user responds to an elicitation, before the response goes to the server. **Not run when an Elicitation hook already answered.** Also runs when the user declined or cancelled.

**Input:** `mcp_server_name`, `action` (the user's), `content?`, `mode?`, `elicitation_id?`.

**Output:** exit 0 with `hookSpecificOutput` (`hookEventName: "ElicitationResult"`):

| Goal | Return | Server receives |
|---|---|---|
| Pass through | no output, exit 0 | the user's response |
| Change values | `action: "accept"`, new `content` | accept + your content |
| Block | `action: "decline"` | decline, without the user's values |
| Cancel | `action: "cancel"` | cancel **plus the values the user submitted**; use `decline` to withhold them |

`content` replaces the whole object: carry over fields you aren't changing. A `hookSpecificOutput` without `action` is ignored. Your `action` replaces the user's, so check the input `action == "accept"` before returning accept, or you turn a decline into an accept. Exit 2 and top-level `decision: "block"` also block. `reason`, `systemMessage`, `continue` discarded.
