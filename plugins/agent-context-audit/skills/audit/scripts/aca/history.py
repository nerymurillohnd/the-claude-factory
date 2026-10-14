"""Run history per repository: the index of runs, the latest pointer, and change since last run.

Finding IDs are content-derived (unit text + category), so the same issue keeps its ID across
runs. A finding whose unit survives but whose category changed is reported as re-categorized,
not as one resolved and one new.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import importlib
from typing import TYPE_CHECKING, cast

from aca.jsonutil import (
    JsonObj,
    as_obj,
    dumps,
    get_list,
    get_obj,
    get_str,
    read_json,
    str_list,
    write_atomic,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from pathlib import Path

    from aca.findings import Finding

INDEX = "index.json"
LATEST = "latest.json"
LOCK = ".lock"
MAX_RUNS = 200
REPORTED = frozenset({"complete", "complete-with-findings", "partial"})
COMPLETE = frozenset({"complete", "complete-with-findings"})


@dataclass
class Change:
    """Findings compared with the previous complete run."""

    previous: str = ""
    new: list[str] = field(default_factory=list)
    resolved: list[str] = field(default_factory=list)
    persisting: list[str] = field(default_factory=list)
    regressed: list[str] = field(default_factory=list)
    recategorized: list[tuple[str, str]] = field(default_factory=list)
    unconfirmed: list[str] = field(default_factory=list)


@contextmanager
def locked(root: Path) -> Generator[None, None, None]:
    """Hold an exclusive lock on the report folder while the index changes (POSIX flock)."""
    fcntl = importlib.import_module("fcntl")
    flock = cast("Callable[[int, int], None]", fcntl.flock)
    exclusive = cast("int", fcntl.LOCK_EX)
    unlock = cast("int", fcntl.LOCK_UN)
    root.mkdir(parents=True, exist_ok=True)
    with (root / LOCK).open("a") as handle:
        flock(handle.fileno(), exclusive)
        try:
            yield
        finally:
            flock(handle.fileno(), unlock)


def read_index(root: Path) -> list[JsonObj]:
    """Every recorded run, oldest first."""
    try:
        return [as_obj(item) for item in get_list(as_obj(read_json(root / INDEX)), "runs")]
    except (OSError, ValueError):
        return []


def _baseline(runs: list[JsonObj]) -> tuple[JsonObj, set[str]]:
    """The run to compare with and the findings of every other reported run.

    The baseline is the last complete run, or the last partial one when no run was complete.
    """
    usable = [run for run in runs if get_str(run, "status") in REPORTED]
    complete = [run for run in usable if get_str(run, "status") in COMPLETE]
    previous = (complete or usable)[-1]
    older = {fid for run in usable if run is not previous for fid in str_list(run.get("findings"))}
    return previous, older


def compare(findings: list[Finding], runs: list[JsonObj], *, partial: bool = False) -> Change:
    """Diff the current findings against the last reported run (a complete one when there is).

    In a partial run, a finding the run did not report may sit in a part it never covered, so
    it is listed as unconfirmed, not resolved.
    """
    if not any(get_str(run, "status") in REPORTED for run in runs):
        return Change()
    previous, older = _baseline(runs)
    before = set(str_list(previous.get("findings")))
    before_units = {str(value): fid for fid, value in get_obj(previous, "units").items()}
    now = {item.fid for item in findings}
    change = Change(previous=get_str(previous, "run_id"))
    change.persisting = sorted(now & before)
    gone = sorted(before - now)
    for item in sorted(findings, key=lambda entry: entry.fid):
        if item.fid in before:
            continue
        old = before_units.get(item.unit)
        if old is not None and old not in now:
            change.recategorized.append((old, item.fid))
            gone = [fid for fid in gone if fid != old]
        elif item.fid in older:
            change.regressed.append(item.fid)
        else:
            change.new.append(item.fid)
    if partial:
        change.unconfirmed = gone
    else:
        change.resolved = gone
    return change


def record(root: Path, entry: JsonObj, latest: JsonObj) -> None:
    """Append this run to the index and point latest.json at it, under the folder lock."""
    with locked(root):
        runs = [*read_index(root), entry][-MAX_RUNS:]
        write_atomic(root / INDEX, dumps({"runs": runs}))
        write_atomic(root / LATEST, dumps(latest))
