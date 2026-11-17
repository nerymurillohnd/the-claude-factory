"""Read a SKILL.md and find its frontmatter block, the way Claude Code finds it.

Claude Code reads the frontmatter only when the opening `---` is the file's first line. A UTF-8
byte-order mark, CRLF line ends and a trailing space or tab on either marker still read normally
(checked on Claude Code 2.1.326). U+2028 and the other Unicode line separators stay inside their
line: only LF, CRLF and CR end a line.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

type Problem = Literal["no-opening-marker", "unclosed", "empty"]
type Encoding = Literal["utf16-bom", "invalid-byte"]

MARKER = "---"
UTF8_BOM = b"\xef\xbb\xbf"
UTF16_BOMS = (b"\xff\xfe", b"\xfe\xff")


@dataclass(frozen=True, slots=True)
class Block:
    """The YAML between the markers: the opening marker is line 1, so the YAML starts on line 2."""

    close_line: int
    yaml_text: str
    first_yaml_line: int = 2


@dataclass(frozen=True, slots=True)
class Undecodable:
    """Why the bytes aren't UTF-8, where the first bad byte is (1-based), and that byte in hex."""

    kind: Encoding
    message: str
    line: int
    column: int
    found: str


@dataclass(frozen=True, slots=True)
class SkillFile:
    """A SKILL.md as decoded text, with its frontmatter block or the reason it has none."""

    text: str | None
    decode_error: Undecodable | None
    had_bom: bool
    had_crlf: bool
    block: Block | None
    problem: Problem | None


def _is_marker(line: str) -> bool:
    """A marker line is `---`, with any trailing spaces or tabs."""
    return line.rstrip(" \t") == MARKER


def _undecodable(error: Undecodable, *, had_bom: bool) -> SkillFile:
    """A file whose bytes could not be read as UTF-8."""
    return SkillFile(
        text=None, decode_error=error, had_bom=had_bom, had_crlf=False, block=None, problem=None
    )


def _bad_byte(data: bytes, start: int) -> Undecodable:
    """Locate the first byte that isn't UTF-8; everything before it decodes."""
    before = data[:start].decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    line = before.count("\n") + 1
    column = len(before) - (before.rfind("\n") + 1) + 1
    return Undecodable(
        kind="invalid-byte",
        message=f"not valid UTF-8 at byte {start}",
        line=line,
        column=column,
        found=f"0x{data[start]:02X}",
    )


def parse(raw: bytes) -> SkillFile:
    """Decode the bytes of a SKILL.md and locate its frontmatter block."""
    if raw.startswith(UTF16_BOMS):
        bom = Undecodable(
            kind="utf16-bom",
            message="the file starts with a UTF-16 byte-order mark",
            line=1,
            column=1,
            found=" ".join(f"0x{byte:02X}" for byte in raw[:2]),
        )
        return _undecodable(bom, had_bom=True)
    had_bom = raw.startswith(UTF8_BOM)
    data = raw.removeprefix(UTF8_BOM)
    try:
        decoded = data.decode("utf-8")
    except UnicodeDecodeError as error:
        return _undecodable(_bad_byte(data, error.start), had_bom=had_bom)
    had_crlf = "\r\n" in decoded
    text = decoded.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    block: Block | None = None
    problem: Problem | None = None
    if not _is_marker(lines[0]):
        problem = "no-opening-marker"
    else:
        close = next((i for i in range(1, len(lines)) if _is_marker(lines[i])), None)
        if close is None:
            problem = "unclosed"
        else:
            block = Block(close_line=close + 1, yaml_text="\n".join(lines[1:close]))
            if not block.yaml_text.strip():
                problem = "empty"
    return SkillFile(
        text=text,
        decode_error=None,
        had_bom=had_bom,
        had_crlf=had_crlf,
        block=block,
        problem=problem,
    )


def read(path: Path) -> SkillFile:
    """Read a SKILL.md from disk; see parse."""
    return parse(path.read_bytes())
