"""The coverage ledger: which lines of each file a worker actually received, proven from its stream.

A worker's claim that it read a file counts for nothing. Every Read result in the stream is parsed
into numbered lines, and a line counts only when its text matches the same line of the snapshot
copy. A file is analyzed only when lines 1..N are all covered; anything less is partial.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aca.snapshot import Snapshot
    from aca.workers import ReadEvent

NUMBERED = re.compile(r"^\s*(\d+)(?:\t|→)(.*)$")


@dataclass
class Ledger:
    """Lines received for one file."""

    sid: str
    total: int
    covered: set[int] = field(default_factory=set)
    mismatched: set[int] = field(default_factory=set)

    @property
    def complete(self) -> bool:
        """True when every line 1..N was received intact."""
        return all(number in self.covered for number in range(1, self.total + 1))

    @property
    def missing(self) -> list[int]:
        """Line numbers never received intact."""
        return [number for number in range(1, self.total + 1) if number not in self.covered]

    def describe(self) -> str:
        """Missing lines as compact ranges, such as 12-40, 77."""
        return compress(self.missing)


def compress(numbers: list[int]) -> str:
    """1,2,3,7 -> '1-3, 7'."""
    parts: list[str] = []
    start = previous = None
    for number in [*sorted(numbers), None]:
        if number is not None and previous is not None and number == previous + 1:
            previous = number
            continue
        if start is not None and previous is not None:
            parts.append(str(start) if start == previous else f"{start}-{previous}")
        start = previous = number
    return ", ".join(parts)


def _matches(received: str, expected: str) -> bool:
    received = received.removesuffix("\r")
    return received == expected or received.rstrip() == expected.rstrip()


def build(reads: list[ReadEvent], snapshot: Snapshot, sids: list[str]) -> dict[str, Ledger]:
    """One ledger per assigned file, from every successful Read of its snapshot copy."""
    ledgers = {sid: Ledger(sid=sid, total=len(snapshot.lines.get(sid, []))) for sid in sids}
    for read in reads:
        if read.is_error:
            continue
        sid = snapshot.sid_for(read.file_path)
        ledger = ledgers.get(sid)
        if ledger is None:
            continue
        lines = snapshot.lines[sid]
        for raw in read.text.split("\n"):
            match = NUMBERED.match(raw)
            if match is None:
                continue
            number = int(match.group(1))
            if not 1 <= number <= len(lines):
                continue
            if _matches(match.group(2), lines[number - 1]):
                ledger.covered.add(number)
            else:
                ledger.mismatched.add(number)
    return ledgers
