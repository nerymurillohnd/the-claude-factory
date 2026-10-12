# Skill audit: <skill name>

- **Path:** <absolute path>
- **Targets:** <targets, "assumed" when inferred>
- **Verdict:** **<pass | pass with warnings | fail | not determinable>**<, provisional when verification.md (Unreachable sources) says so> — <one-line reason>

## Findings

| ID | Lens | Severity | Location | Finding | Fix |
| :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | executability | high | assets/template.md:3 | <one line> | <one line> |
| 2 | conformance, executability | medium | SKILL.md:3 | <one line> | <one line> |

No findings: write `No findings.` and leave out Evidence.

## Evidence

### 1 — <short title>

- "<verbatim quote>" (<file:line>), or Absent: needed at <file:line>
- Official source: <URL> — "<verbatim quote>", or internal (the skill's own text is the evidence)
- Recent changes: <none affecting it in <date> to <date> | the change and its source>
- Consequence: <what goes wrong, for whom>

## Coverage

A line whose lens or checker did not run says `not checked` and why.

- Files: <n> (listed by <checker | find | Glob>); not inspected: <files and why, or none>
- Checker: <ran (targets) | not run: reason>
- Lenses: <which; agent or inline>
- Order and flow: <from the executability lens>
- Verification: <n verified; n corrected; n withdrawn, with why>; changes checked <date> to <date> in <each source checked>; unreachable: <sources, or none>
- Not verified live: <items, or none>
- External dependencies: <found or unverified, plus the inventory's `outside` links, or none>
