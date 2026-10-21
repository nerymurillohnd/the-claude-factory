---
type: llm
---

PASS if the proposed hook uses the PreModelSwitch event, blocks the switch either by exiting 2 with a message on stderr or by returning hookSpecificOutput.permissionDecision "deny" with a permissionDecisionReason, and checks the target model (the to_model input field or a matcher on the canonical model name such as claude-opus-4-6).
FAIL if it relies on UserPromptSubmit or UserPromptExpansion parsing "/model" text as the main mechanism, uses PostModelSwitch to block, or invents an event or input field that does not exist.
