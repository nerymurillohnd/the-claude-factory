---
type: llm
focus: last_message
weight: 1
---
The user's request is vague. Judge whether the reply digs into what the user actually wants. Checkable claims:

1. The reply asks its questions grouped into at most four topics. Options, examples or sub-questions that belong to one topic count once; a long unstructured list of more than four separate topics fails.
2. At least two of the topics are about the user's situation or goal: who the suppliers are or what dealing with them involves, what outcome the user wants, who will read or use the result, or how the user will tell the prompt worked.
3. The questions are not generic filler; each topic would change what the prompt says.

Pass only if all three hold. Fail if the reply asks nothing and just writes a prompt, or asks about only one topic.
