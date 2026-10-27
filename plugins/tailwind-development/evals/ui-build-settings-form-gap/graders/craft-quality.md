---
type: llm
arm: with-only
---

Judge the craft of the interface in the final response, from its markup and its explanation.

PASS if all of these hold:
- The response states which element is primary (in words such as primary, most important, or first), and the markup gives that element, and no other, the strongest visual treatment (largest or boldest type, or the only solid fill for an action).
- Secondary and tertiary elements are visibly stepped down from the primary one through size, weight or colour.
- Spacing groups related items more tightly than unrelated ones.

FAIL if no element is identified as primary, if two or more elements share the strongest treatment, or if every element has the same weight.
