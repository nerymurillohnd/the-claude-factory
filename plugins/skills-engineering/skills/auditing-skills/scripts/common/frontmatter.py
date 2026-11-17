"""The audited SKILL.md read once for a check: the file, its YAML root and its top-level fields.

A check that needs the frontmatter calls load and gets either a root mapping with its fields,
or the reason there is none: no block, a block that isn't a mapping, or a ReadError.
"""

from collections.abc import Iterator
from dataclasses import dataclass

from common import skill_file
from common.context import Context
from common.skill_file import SkillFile
from common.yaml_reader import Node, ReadError, read

# The not_run reason the checks share for a missing block, which claude plugin validate reports.
NO_BLOCK_REASON = "no frontmatter block: claude plugin validate reports it"


@dataclass(frozen=True, slots=True)
class Loaded:
    """A SKILL.md and what its frontmatter holds.

    `root` is the YAML root when it was read, `error` the ReadError when it wasn't, and
    `fields` the top-level pairs by key text when the root is a mapping.
    """

    file: SkillFile
    root: Node | None
    error: ReadError | None
    fields: dict[str, tuple[Node, Node]]

    @property
    def lines(self) -> list[str]:
        """The frontmatter's lines; index 0 is file line 2."""
        block = self.file.block
        return [] if block is None else block.yaml_text.split("\n")

    def line_text(self, line: int) -> str:
        """The text of a 1-based file line inside the frontmatter, or "" outside it."""
        index = line - 2
        return self.lines[index] if 0 <= index < len(self.lines) else ""

    def field_at(self, line: int) -> str | None:
        """The top-level key whose value holds a 1-based file line, when the fields are known."""
        owner: str | None = None
        for name, (key, _value) in self.fields.items():
            if key.line <= line:
                owner = name
        return owner


def load(ctx: Context) -> Loaded:
    """Read the audited SKILL.md and its frontmatter, never raising for its content."""
    file = skill_file.read(ctx.skill_md)
    if file.block is None or file.problem is not None:
        return Loaded(file=file, root=None, error=None, fields={})
    try:
        root = read(file.block.yaml_text, file.block.first_yaml_line)
    except ReadError as error:
        return Loaded(file=file, root=None, error=error, fields={})
    fields: dict[str, tuple[Node, Node]] = {}
    if root.kind == "map":
        fields = {key.value: (key, value) for key, value in root.pairs}
    return Loaded(file=file, root=root, error=None, fields=fields)


def values(node: Node) -> Iterator[Node]:
    """The node and every value under it, keys left out, in document order; no alias followed."""
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        stack.extend(reversed([value for _key, value in current.pairs] + current.items))
