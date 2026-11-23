"""The frontmatter checks, in run order, with the reviewers that receive each result."""

from engine.spec import CheckSpec

from frontmatter import (
    allowed_tools,
    compatibility,
    description,
    field_combinations,
    field_values,
    listing_cap,
    metadata,
    name_format,
    name_plain,
    plain_values,
    yaml_syntax,
)

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
    CheckSpec(
        field_combinations.CHECK,
        field_combinations.check,
        ("frontmatter-description",),
        requires=(yaml_syntax.CHECK,),
    ),
    CheckSpec(
        allowed_tools.CHECK,
        allowed_tools.check,
        ("frontmatter-description", "runtime-contract"),
        requires=(yaml_syntax.CHECK,),
    ),
)
