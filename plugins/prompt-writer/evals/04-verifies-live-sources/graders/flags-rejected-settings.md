---
type: llm
focus: last_message
weight: 1
---
The user's integration uses settings that current Claude models reject. Judge the reply on these checkable claims:

1. The reply tells the user that at least two of the three settings (non-default `temperature`, assistant prefill, `budget_tokens`) are rejected with an error (HTTP 400) on Opus 5.5, or are otherwise no longer valid there. Saying it only in passing inside the prompt does not count; it must be said to the user.
2. The reply says what replaces them: instructions in the prompt, structured outputs, or the effort setting.
3. The reply separates what it verified in current official pages from what it took from its built-in guidance or could not verify.
4. The reply names the full URL of each official page it read to verify, so the user can open it.

Pass only if claims 1, 2 and 4 hold and claim 3 holds.
