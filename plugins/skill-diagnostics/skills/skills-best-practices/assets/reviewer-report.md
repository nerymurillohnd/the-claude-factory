## <reviewer name>: <skill name>

Skill: <absolute path>
Status: complete | incomplete: <reason>
Files read in full: <n> of <n>
Not inspected: <file · reason · needed by <file:line> | unreferenced>, or none

### Findings

#### <D | I | R | S><n>
- Item: <checklist item ID> · <area file>#<heading>
- Severity: high | medium | low
- Location: <path relative to the skill>:<line or lines>
- Evidence: "<verbatim quote>". For something absent: where the information is needed, and the files read to look for it.
- Defect: <why this text fails the item: what goes wrong, for whom, on which surface>
- Basis: <the rule as the area file states it, with its source tag and strength label>
- Fix: <one concrete change>

Write `No findings.` under Findings when there are none.

### Leads
<check ID> · confirmed as <finding ID> | rejected: <reason>

### Self-check
- [ ] Every inventory file read from its first line to its last, or listed under Not inspected with its reason
- [ ] Every finding has all seven fields filled, none left as a placeholder
- [ ] Every quote re-read at its file:line and matches it verbatim
- [ ] Every finding is on an item I own; none repeats a check the scripts proved or another agent's item
- [ ] Every lead in the brief is confirmed or rejected
- [ ] One root cause is one finding, with every location listed
- [ ] Every Basis comes from a file I read in this run, none from memory
