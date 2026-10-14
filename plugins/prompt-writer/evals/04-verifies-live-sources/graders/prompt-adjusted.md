---
type: llm
focus: last_message
weight: 1
---
Judge the system prompt that the reply delivers (the text meant to be pasted):

1. It does not depend on `temperature`, assistant prefill or `budget_tokens`, and does not tell the integration to set them.
2. It gets JSON out through an instruction, or through structured outputs, in a way that works without a prefilled "{".
3. It defines the invoice fields to extract or tells the model where to find them, and says what to do when a field is missing.
4. It does not ask the model to show its reasoning in the response.

Pass only if claims 1, 2 and 4 hold.
