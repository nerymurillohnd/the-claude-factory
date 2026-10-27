---
type: llm
arm: with-only
---

Judge the craft of the interface in the final response, from its markup and its explanation.

PASS if all of these hold:
- One element is primary, and the markup gives it, and no other, the strongest visual treatment (largest and boldest type, or the only solid fill for an action). When the response includes an explanation, it names that element as primary; when the user asked for markup only, the markup alone must make the primary element unmistakable.
- Secondary and tertiary elements are visibly stepped down from the primary one through size, weight or colour.
- Spacing groups related items more tightly than unrelated ones.

FAIL if no element is clearly primary, if two or more elements share the strongest treatment, or if every element has the same weight.
