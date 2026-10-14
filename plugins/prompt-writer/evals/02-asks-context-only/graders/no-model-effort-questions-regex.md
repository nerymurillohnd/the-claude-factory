---
type: regex
target: last_message
match: not_contains
flags: i
weight: 0.5
---
(which|what|prefer|choose|pick|want)[^?\n]{0,60}\b(model|effort level|XML|temperature|thinking budget)\b[^?\n]*\?
