---
status: proposed
date: YYYY-MM-DD
decision-makers:
  - "{Accountable person or role}"
consulted:
  - "{Optional person or role consulted}"
informed:
  - "{Optional person or role informed}"
supersedes: none
superseded-by: none
---

<!--
Template for .claude/maintainer/decisions/ADR_<YYYY-MM-DD>_<decision-slug>.md.
Write the new file with the frontmatter above and the body below, and leave this comment out.
- status: proposed, accepted, rejected, deprecated or superseded. The ADRs reference says when each applies.
- date: the registration date, equal to the date in the file name.
- supersedes: the ID of the ADR this record replaces (its file name without .md), or none.
- superseded-by: the ID of the ADR that replaces this one. Required when status is superseded.
- Remove the consulted and informed keys, with their list items, when they would be empty.
- Required sections: Scope, Context and problem statement, Decision drivers, Considered options, Decision outcome and its Consequences.
- Optional sections: Risks and mitigations, Confirmation, Pros and cons of the options, More information. Remove the ones that add nothing.
- In a proposed record, write "proposed" instead of "chosen" in Considered options and "Proposed option" in Decision outcome, and say what is still open.
- Replace every {placeholder}.
- Mark planned evidence as pending. Never present it as observed. If you remove Confirmation, write the pending evidence in More information.
-->

# {Short title naming the decision}

## Scope

{Name the affected components, repository paths, workflows or processes, and what is out of scope.}

## Context and problem statement

{Describe the circumstances and the problem, with links to evidence. Frame the decision as a
question when that helps the reader.}

## Decision drivers

- {Constraint, quality, risk or goal that matters to the choice}
- {Another decision driver}

## Considered options

- **{Chosen option}**: chosen.
- **{Alternative option}**: rejected because {reason}.

## Decision outcome

Chosen option: **{Option name}**, because {why it best meets the decision drivers}.

### Consequences

- Good, because {positive consequence}.
- Bad, because {trade-off or cost}.

<!-- Optional: remove this section when the decision carries no material risk. -->

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| {Risk} | {Likelihood or triggering condition} | {Impact} | {Mitigation} | {Owner} |

<!-- Optional: remove this section when nothing needs to be checked later. -->

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| {Claim or criterion} | {Command, review or check} | {Result, or "pending"} | {Date or condition} |

<!-- Optional: remove this section when the options are already documented well enough above. -->

## Pros and cons of the options

### {Option 1}

{Evidence, examples or links for this option.}

- Good, because {argument supporting the option}
- Neutral, because {argument with no material positive or negative effect}
- Bad, because {argument against the option}

### {Option 2}

{Evidence, examples or links for this option.}

- Good, because {argument supporting the option}
- Neutral, because {argument with no material positive or negative effect}
- Bad, because {argument against the option}

<!-- Optional: remove this section when there is nothing to add. -->

## More information

{Add evidence, related ADRs by ID, implementation timing or pending evidence. For a record written after the decision was made, say when it was made.}
