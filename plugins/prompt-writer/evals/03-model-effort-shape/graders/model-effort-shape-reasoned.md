---
type: llm
focus: last_message
weight: 1
---
The user needs a prompt for a latency-bound, high-volume classifier called once per ticket through the API. Judge the reply's recommendations on these checkable claims:

1. It names a target model and gives a reason tied to this case (speed, latency or cost at volume). Sonnet 5.5 is the expected choice; another choice passes only if the reason clearly rests on the one-second latency and the single-call use.
2. It names why at least one other Claude model was not chosen (for example Fable 5.1 or Opus 5.5 being heavier than a one-second classifier needs).
3. It states an effort level, low or medium, with a short reason. A high, xhigh or max effort fails this claim.
4. It recommends running this as a single-turn API call, not an interactive session.
5. It delivers one prompt and says, or clearly implies, that no follow-up prompts or stages are needed. It does not offer several alternative prompts.

Pass only if claims 1, 3 and 5 hold and at least one of 2 or 4 holds.
