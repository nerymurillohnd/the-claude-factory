# Skill audit: <skill name>

- **Path:** <absolute path>
- **Targets:** <targets, and "assumed" when inferred>
- **Verdict:** **<pass | pass with warnings | fail | not determinable>** — <one-line reason>

## Findings

| ID | Lens | Severity | Location | Finding | Fix |
| :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | executability | high | assets/template.md:3 | <one line> | <one line> |
| 2 | conformance, executability | medium | SKILL.md:3 | <one line; a joined row names every lens that flagged it> | <one line> |

No findings: replace the table with `No findings.` and leave out the Evidence section.

## Evidence

### 1 — <short title>

- "<verbatim quote>" (<file:line>), or for something missing: Absent: needed at <file:line>; read <files>
- Consequence: <what goes wrong, for whom> (one bullet per joined finding)

## Coverage

- Files: <n> in the skill (listed by <checker | find | Glob>); not inspected: <files and why, or none>
- Checker: <ran (target …) | not run: reason>
- Lenses: <conformance, executability; agent or inline>
- Order and flow: <the executability lens's line, or not checked: executability lens not selected>
- Not verified live: <items, or none>
- External dependencies: <names or paths, found or unverified, or none>
