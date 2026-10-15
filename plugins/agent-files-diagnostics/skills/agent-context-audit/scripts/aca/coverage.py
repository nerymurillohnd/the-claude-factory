"""The coverage ledger: which lines of each file an auditor received, proven from its transcript.

An auditor's claim that it read a file counts for nothing. Claude Code keeps every workflow
agent's transcript under the session folder; every Read result in it is parsed into numbered
lines, and a line counts only when its text matches the same line of the snapshot copy. A file
is analyzed only when lines 1..N are all covered; anything less is partial.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import TYPE_CHECKING

from aca.jsonutil import JsonObj, as_list, as_obj, get_str, loads

if TYPE_CHECKING:
    from pathlib import Path

    from aca.snapshot import Snapshot

NUMBERED = re.compile(r"^\s*(\d+)(?:\t|→)(.*)$")
WORKFLOWS = ("subagents", "workflows")


@dataclass
class ReadEvent:
    """One Read tool call and what came back."""

    file_path: str
    text: str
    is_error: bool = False


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


def _content_text(content: object) -> str:
    if isinstance(content, str):
        return content
    parts: list[str] = []
    for block in as_list(content):
        item = as_obj(block)
        if get_str(item, "type") == "text":
            parts.append(get_str(item, "text"))
    return "\n".join(parts)


def events(path: Path) -> list[JsonObj]:
    """The JSON objects of a transcript or journal, skipping lines that are not JSON."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    found: list[JsonObj] = []
    for line in lines:
        try:
            found.append(as_obj(loads(line)))
        except ValueError:
            continue
    return found


@dataclass
class Transcript:
    """What one agent transcript proves: its reads and the tools it called."""

    reads: list[ReadEvent] = field(default_factory=list)
    tools: set[str] = field(default_factory=set)
    pending: dict[str, str] = field(default_factory=dict)

    def tool_use(self, item: JsonObj) -> None:
        """Record a tool call; a Read call waits for its result."""
        name = get_str(item, "name")
        self.tools.add(name)
        if name == "Read":
            self.pending[get_str(item, "id")] = get_str(as_obj(item.get("input")), "file_path")

    def tool_result(self, item: JsonObj) -> None:
        """Pair a result with its Read call."""
        target = self.pending.pop(get_str(item, "tool_use_id"), None)
        if target is not None:
            error = bool(item.get("is_error"))
            self.reads.append(ReadEvent(target, _content_text(item.get("content")), error))


def reads_from_transcript(path: Path) -> tuple[list[ReadEvent], set[str]]:
    """Every Read event in one agent transcript, and the names of every tool it called."""
    found = Transcript()
    for event in events(path):
        message = as_obj(event.get("message"))
        kind = get_str(event, "type")
        for block in as_list(message.get("content")):
            item = as_obj(block)
            if kind == "assistant" and get_str(item, "type") == "tool_use":
                found.tool_use(item)
            elif kind == "user" and get_str(item, "type") == "tool_result":
                found.tool_result(item)
    return found.reads, found.tools


def find_run_dir(claude_dir: Path, run_id: str) -> Path | None:
    """The folder where Claude Code keeps a workflow run's journal and agent transcripts."""
    projects = claude_dir / "projects"
    if not projects.is_dir():
        return None
    for project in sorted(projects.iterdir()):
        if not project.is_dir():
            continue
        for session in sorted(project.iterdir()):
            candidate = session.joinpath(*WORKFLOWS) / run_id
            if candidate.is_dir():
                return candidate
    return None


def agent_ids(run_dir: Path) -> dict[str, str]:
    """Label -> agent id, from the run's journal."""
    found: dict[str, str] = {}
    for entry in events(run_dir / "journal.jsonl"):
        if get_str(entry, "type") == "started":
            found[get_str(entry, "label")] = get_str(entry, "agentId")
    return found


USAGE_KEYS = (
    "input_tokens",
    "output_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
)


def usage_from_transcript(path: Path) -> dict[str, int]:
    """Token counts summed over every assistant message of one agent transcript."""
    totals: dict[str, int] = dict.fromkeys(USAGE_KEYS, 0)
    totals["requests"] = 0
    for event in events(path):
        if get_str(event, "type") != "assistant":
            continue
        usage = as_obj(as_obj(event.get("message")).get("usage"))
        if not usage:
            continue
        totals["requests"] += 1
        for key in USAGE_KEYS:
            value = usage.get(key)
            if isinstance(value, int):
                totals[key] += value
    return totals


def transcript(run_dir: Path, agent_id: str) -> Path:
    """The transcript file of one agent of the run."""
    return run_dir / f"agent-{agent_id}.jsonl"
