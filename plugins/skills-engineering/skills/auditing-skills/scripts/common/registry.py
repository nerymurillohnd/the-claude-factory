"""The frontmatter checks, in run order, with the reviewers that receive each result."""

import argparse
from collections.abc import Callable
from dataclasses import dataclass

from frontmatter import (
    compatibility,
    description,
    field_values,
    listing_cap,
    metadata,
    name_format,
    name_plain,
    plain_values,
    yaml_syntax,
)

from common.context import Context
from common.report import CheckResult

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


@dataclass(frozen=True, slots=True)
class CheckSpec:
    """One check: its id, its function, who receives its result, and what it requires.

    `requires` names checks that must run clean first: when one of them did not run or reported
    a finding, this check returns `not_run` with the reason "<check> failed". `options` adds the
    check's own command-line options, which keep their defaults under `run`.
    """

    check: str
    run: Callable[[Context], CheckResult]
    receivers: tuple[str, ...]
    requires: tuple[str, ...] = ()
    options: Callable[[argparse.ArgumentParser], None] | None = None


CHECKS: tuple[CheckSpec, ...] = (
    CheckSpec(
        yaml_syntax.CHECK, yaml_syntax.check, ("frontmatter-description", "runtime-contract")
    ),
    CheckSpec(
        plain_values.CHECK,
        plain_values.check,
        ("frontmatter-description",),
        requires=(yaml_syntax.CHECK,),
    ),
    CheckSpec(
        name_format.CHECK,
        name_format.check,
        ("frontmatter-description", "size-limits-and-budgets"),
        requires=(yaml_syntax.CHECK,),
    ),
    CheckSpec(
        name_plain.CHECK,
        name_plain.check,
        ("frontmatter-description",),
        requires=(yaml_syntax.CHECK,),
    ),
    CheckSpec(
        description.CHECK,
        description.check,
        ("frontmatter-description", "size-limits-and-budgets"),
        requires=(yaml_syntax.CHECK,),
    ),
    CheckSpec(
        listing_cap.CHECK,
        listing_cap.check,
        ("size-limits-and-budgets", "frontmatter-description"),
        requires=(yaml_syntax.CHECK,),
        options=listing_cap.options,
    ),
    CheckSpec(
        compatibility.CHECK,
        compatibility.check,
        ("frontmatter-description", "size-limits-and-budgets"),
        requires=(yaml_syntax.CHECK,),
    ),
    CheckSpec(
        metadata.CHECK,
        metadata.check,
        ("frontmatter-description",),
        requires=(yaml_syntax.CHECK,),
    ),
    CheckSpec(
        field_values.CHECK,
        field_values.check,
        ("frontmatter-description",),
        requires=(yaml_syntax.CHECK,),
    ),
)


def find(check_id: str) -> CheckSpec | None:
    """The registered check with this id, if any."""
    return next((spec for spec in CHECKS if spec.check == check_id), None)
