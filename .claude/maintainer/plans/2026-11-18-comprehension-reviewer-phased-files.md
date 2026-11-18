# Plan: teach `comprehension-reviewer` to flag a phased skill's references that aren't organized by phase

## Context

The owner and Claude found a defect in `authoring-skills`: `scripts-and-hooks.md` was read in phase 3, but its first section was a phase-2 decision, so a model applied that rule late or not at all. No phase stated the order to read its files. The fix (commits 234bd93, 88050a7) taught `authoring-skills` the pattern, in `references/phase-3-design-and-plan.md` steps 8 and 9:

- one phase and one topic per reference;
- the name carries the phase and the topic (`phase-2-placements.md`);
- each phase's files are listed under the phase in step order, with the step and condition that read each;
- the model is told to read them in that order.

No official source sets that pattern. The bases are official:

- "Keep individual reference files focused" (agentskills.io spec);
- "Organize for discovery … by domain or feature" and "Name files descriptively" (platform best practices);
- "telling the agent *when* to load each file" (agentskills.io best practices).

The phase prefix and the explicit order are the owner's convention.

The audit side doesn't check this. `auditing-skills/references/comprehension.md` covers three related points, none of which flags it:

- §2.4, each *instruction* in its phase;
- §2.5, each pointer at its step;
- §5.9, descriptive file names.

**Goal:** `skills-engineering:comprehension-reviewer` flags the same three defects in any phased skill it audits, each with its fix:

1. a reference that serves two phases;
2. a phase with several files and no reading order;
3. a phase-specific file whose name doesn't carry its phase.

The owner chose to extend this reviewer over adding a new agent. The topic is its domain (order, phases, pointers), and a new agent would add one Opus run to every audit and overlap §2.4 and §2.5.

## Approach

A new subsection, **§2.7 "A phased skill's files organized by phase"**, closes Area 2, the order and dependencies area. It goes after §2.6 and before the `---` that opens §3. It is a new subsection, rather than bullets in §2.4, because:

- §2.4 is about instructions inside the body;
- this is about how the files are cut, named and listed;
- a numbered subsection gets its own checklist item, so the reviewer can't skip it.

Draft text, to be refined with `authoring-skills`:

```markdown
### 2.7 A phased skill's files organized by phase

In a skill that works in phases and keeps their detail in files, each file should serve one phase and one topic. A file that holds rules for two phases is opened at one of them, so the rules for the other arrive late or never: Claude reads the file at the step that points to it and applies what fits that step. Where a phase reads several files, the order between them is the order Claude applies them in, and when the skill doesn't state it, Claude picks one. A name that carries the phase and the topic, such as `phase-2-placements.md`, tells Claude from the listing which phase a file belongs to. The bases are sourced: focused reference files, files organized by domain or feature, descriptive names, and saying when to load each file. Cutting files by phase, the phase in the name and the stated order are an inference and the owner's doctrine.

When you audit:

- Skip this section for a skill with no phases, or with no supporting files.
- Map each file to the phases whose steps use its content. Flag every file whose content serves more than one phase, quoting a passage for each phase, and recommend splitting it into one file per phase, with each passage's destination and every pointer updated. A lookup every phase consults on purpose, such as a glossary, a table of values or a template, is not a mixed file.
- Flag every phase that reads more than one file without stating the order, and recommend the files listed under that phase in the order of the steps that read them, each with its condition and the step that reads it, plus one line telling Claude to read them in that order.
- Flag, as an improvement opportunity rather than a defect, a phase-specific file whose name doesn't carry its phase, and recommend the name `phase-<n>-<topic>.md` with every pointer to it updated.
- Set severity by the consequence: a file that makes Claude apply a rule after the step it governs is judged as 2.2; a missing order is a defect when the files' order changes the result, and an improvement otherwise.
```

## Tasks

Each task ends with a signed commit and no push.

1. **Load the designated skills.** Load `skills-engineering:authoring-skills` for the edit; it covers skill content, the reference file and the agent file. Read `comprehension.md` §2 and "Classifying findings" in full, and the agent file in full, before editing. Check:
   - that the official quotes above still read as quoted, through the Claude Code Docs MCP with `anthropic-skills:cc-docs-research` and the agentskills.io pages;
   - whether `authoring-skills/SKILL.md` frames the same pattern in the same terms, so the two skills don't drift.
2. **Edit `plugins/skills-engineering/skills/auditing-skills/references/comprehension.md`:**
   - add the `2.7` line to Contents, after `2.6`;
   - add the §2.7 subsection;
   - in "Classifying findings", add a line only if §2.7's severity rule isn't already covered there.
3. **Edit `plugins/skills-engineering/agents/comprehension-reviewer.md`:**
   - the expertise line "Order and dependencies" gains "and a phased skill's files cut, named and listed by phase";
   - WORKFLOW step 3.2 stays "Order and dependencies (2)", which already includes §2.7;
   - add a checklist item after the 2.6 item: "- [ ] In a phased skill, every file serves one phase and one topic, every phase with several files states their order, and every phase-specific file name carries its phase (2.7)."
4. **Check the other places that describe the reviewer.** Grep `plugins/skills-engineering/` (README, `auditing-skills/SKILL.md`, the other references) for any listing of comprehension's sections or checks, and update each one that enumerates them.
5. **Version and documents.**
   - Run `plugin-releases` to decide the version. Expected: the change stays in the untagged 0.2.0, dated 2026-11-18, as a `### Changed` entry; the skill decides.
   - Then, with `docs-maintenance`, add the plugin CHANGELOG entry in user language, and extend the `skills-engineering` 0.2.0 line in the root `CHANGELOG.md` in the same way.
   - Update the plugin README only if task 4 found a listing there.
6. **Behavioral test.** The installed `comprehension-reviewer` is the synced copy, not this repository's, so test the edited reference directly:
   1. Copy the pre-restructure `authoring-skills` from the scratchpad baseline (`scratchpad/rs/baseline/`) outside the repository.
   2. Launch one general-purpose subagent (Sonnet, read-only by instruction). Have it read only the edited §2.7 and apply it to that copy.
   3. **Pass:** it flags `scripts-and-hooks.md` as serving phases 2 and 4, and flags the phase pointers without a stated order.
   4. **Negative control:** the same subagent applies §2.7 to the current `authoring-skills`. Pass: no 2.7 defect. A naming improvement is acceptable only if one is real.

## Verification

- `npx biome lint` on both edited files, and `npx biome check --write` on the CHANGELOGs.
- `npm run -s lint:frontmatter -- plugins/skills-engineering/agents/comprehension-reviewer.md`
- `npm run -s lint:skills -- plugins/skills-engineering/skills/auditing-skills`, with no finding beyond the baseline. Run it before task 2 to record the baseline.
- `claude plugin validate --strict plugins/skills-engineering`, and `claude --plugin-dir plugins/skills-engineering plugin details skills-engineering`.
- `npm run -s check:consistency` exits 0, and `npm run -s test:plugins` passes.
- Reread both edited files in full after the edit (`skill-standards.md`).
- The task 6 results, both runs, shown raw.

## Out of scope, reported

- Any `lint:skills` finding in `auditing-skills` is reported to the owner, one question per rule id, before any fix.
- The push of the local commits (40 now) needs the owner's authorization.
