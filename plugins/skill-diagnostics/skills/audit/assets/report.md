# Skill audit: <skill name>

- **Path:** <absolute path>
- **Targets:** <targets, and "assumed" when inferred>
- **Verdict:** **<pass | pass with warnings | fail | not determinable>** — <one-line reason>

## Findings

| ID | Lens | Severity | Location | Finding | Fix |
| :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | executability | high | assets/template.md:3 | <one line> | <one line> |
| 2 | conformance, executability | medium | SKILL.md:3 | <one line, for a row both lenses flagged> | <one line> |

No findings: replace the table with `No findings.` and leave out the Evidence section.

## Evidence

### 1 — <short title>

- "<verbatim quote>" (<file:line>), or for something missing: Absent: needed at <file:line>; searched <files>
- Consequence: <what goes wrong, for whom>

## Coverage

- Files: <n> in the skill; not inspected: <files and why, or none>; git-ignored files: <the files | none | not visible to the tools>
- Checker: <ran (target …) | not run: reason>
- Lenses: <conformance, executability; agent or inline>
- Order and flow: <the executability lens's line, or not checked: executability lens not selected>
- Not verified live: <items, or none>
- External dependencies: <names or paths, found or unverified, or none>
