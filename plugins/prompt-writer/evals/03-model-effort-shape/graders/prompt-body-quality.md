---
type: llm
focus: last_message
weight: 1
---
Judge the prompt body that the reply delivers (the text meant to be pasted, not the notes around it):

1. It states the goal and who uses the result: a ticket classifier whose urgency 4 and 5 are reviewed by a person the next morning.
2. It defines the four categories (billing, shipping, product, other) and gives checkable criteria for what makes a ticket urgency 1 to 5.
3. It requires the answer to be a single JSON object with the category and the urgency, and nothing else.
4. It does not ask the model to show its reasoning in the response, and it does not mention `temperature`, assistant prefill or `budget_tokens` as things to set.
5. It is written in plain statements with reasons; it does not rely on all-caps emphasis such as CRITICAL or MUST.

Pass only if claims 1 to 4 hold. Claim 5 may fail without failing the case.
