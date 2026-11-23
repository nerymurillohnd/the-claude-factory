"""What a check receives about the skill it checks."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Context:
    """The skill's SKILL.md, its folder, the folder's name as given and as resolved, and options.

    folder_name is the name of the folder as the path was given, so a symlinked folder keeps the
    name Claude Code loads it under; resolved_folder_name follows every symlink.
    """

    skill_md: Path
    skill_dir: Path
    folder_name: str
    resolved_folder_name: str
    options: dict[str, object]
