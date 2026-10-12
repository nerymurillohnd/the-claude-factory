# Skill audit: <skill name>

- **Path:** <absolute path>
- **Origin:** <synced | plugin | personal | project | web | loose folder>; reaches <surfaces>
- **Verdict:** **<pass | pass with warnings | fail | not determinable>**<, provisional when step 5 says so><, conformance lens only | executability lens only> — <one-line reason>

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
- Recent changes: <none affecting it in Claude Code <oldest> to <newest> | the change and its version>
- Consequence: <what goes wrong, for whom>

## Coverage

A line whose lens or checker did not run says `not checked` and why.

- Files: <n> (listed by <checker | find | Glob>); not inspected: <files and why, or none>
- Checker: <ran (code, cowork, upload, api) | not run: reason>
- Lenses: <which; agent or inline>
- Order and flow: <from the executability lens>
- Verification: <n verified; n corrected; n withdrawn, with why>; changelog read from <oldest> to <newest> (user on <version>, or unknown); unreachable: <sources, or none>
- Not verified live: <items, or none>
- External dependencies: <found or unverified, plus the inventory's `outside` links, or none>
