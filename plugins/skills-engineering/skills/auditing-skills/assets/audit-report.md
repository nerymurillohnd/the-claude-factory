# Audit report

## Status

<complete | incomplete — reason>

## Verdict

<PASS | PASS WITH IMPROVEMENTS | FAIL>

## Audited skill

- Reviewer: <agent name>
- Skill: <name> at <path>
- Where it lives: <location>
- How it's invoked: <main conversation | context: fork | preloaded into a subagent>
- Surfaces: <surfaces that load it>
- Purpose: <what the skill is trying to do, in one sentence>

## Summary

- Critical: <n>
- High: <n>
- Medium: <n>
- Low: <n>
- Improvement opportunities: <n>

## Defects

### <Critical | High | Medium | Low> · <short title>

- File: <path within the audited skill>
- Lines: <start>–<end>
- Evidence: `<quoted text from those lines>`
- Point violated: <reference file> §<section>
- Finding: <what is wrong and why it is a defect, stated as its consequence>
- Action: <delete | rewrite | move | improve | adjust | add>
- Fix:
  ````text
  <exact replacement text, or the destination path and the pointer line left behind>
  ````
- Justification: <why this fix is the right one for this skill>

## Improvement opportunities

### <short title>

- File: <path within the audited skill>
- Lines: <start>–<end>
- Point: <reference file> §<section>
- Current: <what exists now>
- Recommended:
  ````text
  <what the reference recommends instead, as actual text or structure>
  ````
- Why for this skill: <why that is better for this skill specifically>

## Checklist exceptions

<each checklist item that could not be completed, with its reason, or None>
