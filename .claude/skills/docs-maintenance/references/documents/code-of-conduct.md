# Code of conduct

How to create `CODE_OF_CONDUCT.md` from `assets/CODE_OF_CONDUCT-template.md`.

## Produces

`CODE_OF_CONDUCT.md` at the repository root. GitHub looks in `.github/`, then the root, then `docs/`, uses the first it finds, and shows it as the Code of conduct tab and in the community profile.

## When

- When the repository becomes public.
- When the Contributor Covenant publishes a new version, or the reporting method changes.

## Sources

Read 2026-11-10:

- Contributor Covenant 3.0 (`https://www.contributor-covenant.org/version/3/0/`), licensed CC BY-SA 4.0: the text marks its two adaptation points with `[NOTE: …]`; the Attribution section must stay.
- GitHub Docs, "Adding a code of conduct to your project" (`github/docs` at `f309096`): research codes of conduct and "consider carefully whether you are willing and able to enforce it"; the community profile marks it added "if the file is not empty and does not state that the project has no code of conduct"; follow the source's attribution guidelines.

Confirm that the reporting contact reaches someone who acts on it, and never weaken the Covenant's terms.

## Placeholders

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{reportingMethod}}` | How to report a possible violation, privately | A channel that exists and reaches a maintainer who acts on it |

The template's second adaptation point is an instruction comment in "Addressing and Repairing Harm": keep the Covenant's enforcement ladder, or replace it with the project's own enforcement policy.

## Procedure

1. Copy the template to `CODE_OF_CONDUCT.md` and delete its header comment.
2. Replace `{{reportingMethod}}` with a private reporting channel the maintainer actually reads, such as a monitored email address. A GitHub security advisory is not one: it is for vulnerabilities.
3. Review "Addressing and Repairing Harm", then delete its instruction comment.
4. Keep the Attribution section unchanged.
5. Run the checks.

## Rules

Official:

- The Covenant text is kept verbatim except its two adaptation points.
- The Attribution section stays, as CC BY-SA 4.0 requires.

This repository:

- The code of conduct names a reporting channel that only the maintainer reads, never a public issue.

## Checks

- The repository's community profile (Insights → Community standards) shows "Code of conduct" as added after the push.
- `diff` against the official 3.0 text, with the two adaptation points restored, shows no difference.

## Never

- Never adopt a code of conduct the maintainer cannot enforce.
- Never invent a contact address.
