---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Each Claude workflow reads only its own credential secret, and check:consistency enforces it

## Scope

The Claude credential secrets in `.github/workflows/`, the rule `.claude/rules/architecture/claude-workflows.md`, and PC-13 in `check:consistency` (`scripts/validators/plugin_consistency/checks.py`).

## Context and problem statement

Two Claude credentials live in the `claude` environment, and each bills a different account:
- `ANTHROPIC_API_KEY`, a Claude Console service-account key, bills the API account. Only the review uses it (ADR_2026-11-15_claude-review-posts-one-summary-per-push).
- `CLAUDE_CODE_OAUTH_TOKEN` bills the owner's subscription. `@claude` uses it (ADR_2026-11-15_claude-answers-mentions-with-the-owners-subscription), and so do evals (ADR_2026-11-15_evals-ci-gates-on-score-and-delta-with-the-owners-subscription).

GitHub gives a secret only to a step that names it, but nothing stops a workflow change from naming the wrong one. On 2026-11-15 the owner asked to keep this separation strict at all times.

## Decision drivers

- Each workflow bills the account the owner chose for it.
- A mistake is caught before the merge, whether Claude or a person made it.

## Considered options

- **A path-scoped rule plus PC-13 in `check:consistency`, which Validate's blocking `Checks` job runs**: chosen.
- **Two environments, one secret each**: rejected by the owner. Distinct secret names already keep the secrets apart, and PC-13 catches a crossed reference.
- **The rule alone**: rejected, because a rule informs Claude and blocks nothing.

## Decision outcome

Chosen option: **the rule plus PC-13**:
- `secrets.ANTHROPIC_API_KEY` may be read only by `claude-code-review.yml`.
- `secrets.CLAUDE_CODE_OAUTH_TOKEN` may be read only by `claude.yml` and `evals.yml`.
- PC-13 matches `secrets.<NAME>` and `secrets['<NAME>']` in every `.yml` and `.yaml` file under `.github/workflows/`. A shell reference such as `${ANTHROPIC_API_KEY:-}` is not a read.
- The `CLAUDE_CODE_REVIEW` and `CLAUDE_EVALS` switches are repository variables, because a job-level `if:` can't see an environment variable.
- Tests: `test_pc13_secret_read_by_the_wrong_workflow` and `test_pc13_each_secret_in_its_own_workflow` in `scripts/testers/plugin_consistency/test_checks.py`.

### Consequences

- Good, because a pull request that crosses the credentials fails Validate.
- Bad, because adding a new Claude workflow that needs a credential means updating `SECRET_OWNERS` in `checks.py` and the rule together.

## More information

- Decided by the owner on 2026-11-15: "Mantener estrictamente y siempre utilizar el nombre de variable correcto específico para cada caso definido", and the plan approval that added PC-13.
- GitHub's Variables reference: "Environment-level variables are only available on the runner after the job starts executing" (docs.github.com/en/actions/reference/workflows-and-actions/variables, read 2026-11-15).
