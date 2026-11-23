"""Every check family's checks, in run order, and the reviewers a result can go to."""

import frontmatter

from engine.spec import CheckSpec

# Each family's checks by family name, in the order `run` runs the families.
FAMILIES: dict[str, tuple[CheckSpec, ...]] = {
    "frontmatter": frontmatter.CHECKS,
}

CHECKS: tuple[CheckSpec, ...] = tuple(spec for specs in FAMILIES.values() for spec in specs)

# Every reviewer a result can go to; `show --reviewer` refuses any other name.
REVIEWERS: tuple[str, ...] = (
    "content-patterns",
    "runtime-contract",
    "size-limits-and-budgets",
    "knowledge-delta",
    "task-mechanisms",
    "frontmatter-description",
    "comprehension",
    "feature-fit",
    "scripts",
)


def find(check_id: str) -> CheckSpec | None:
    """The registered check with this id, if any."""
    return next((spec for spec in CHECKS if spec.check == check_id), None)
