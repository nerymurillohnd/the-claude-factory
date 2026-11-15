#!/usr/bin/env python3
"""Gate a CI job on a `claude plugin eval` JSON result (eval-gate).

Maintainer tooling: run it through `npm run evals:gate`, which uses the project's .venv Python.

`claude plugin eval` never fails on the with-minus-without delta, so the evals workflow reads
`aggregates.meanDelta` from the result and fails when the plugin stops helping. Exit codes:
0 the gate passed, 1 it failed, 2 the result is not comparable (partial, judge graders skipped
by the cost ceiling, or a run that errored or a mock aborted, which scores 0 and skews the delta),
3 the file is not an eval result.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import TYPE_CHECKING, TypeGuard

if TYPE_CHECKING:
    from collections.abc import Callable

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_NOT_COMPARABLE = 2
EXIT_UNREADABLE = 3
ARMS = ("with", "without")


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


# Decodes JSON with every object built as JsonObject, so isinstance() narrows it cleanly.
parse_json: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def is_list(value: object) -> TypeGuard[list[object]]:
    """Narrow a decoded JSON value to an array."""
    return isinstance(value, list)


def field(value: object, key: str) -> object:
    """Return value[key] when value is a JSON object, else None."""
    return value.get(key) if isinstance(value, JsonObject) else None


def items(value: object) -> list[object]:
    """Return value when it is a JSON array, else an empty list."""
    return value if is_list(value) else []


def number(value: object) -> float | None:
    """Return value as a float when it is a finite JSON number; NaN compares as nothing."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def run_problems(cases: list[object]) -> tuple[list[str], bool]:
    """List each run's error and mock abort, and report whether judge graders were skipped."""
    problems: list[str] = []
    skipped = False
    for case in cases:
        name = field(case, "name") or "?"
        for arm in ARMS:
            for index, run in enumerate(items(field(field(case, "arms"), arm)), start=1):
                error = field(run, "error")
                if error:
                    problems.append(f"{name} [{arm} run {index}] error: {error}")
                aborted = field(run, "aborted")
                if aborted:
                    where = f"{field(aborted, 'server')}/{field(aborted, 'tool')}"
                    reason = field(aborted, "reason")
                    problems.append(f"{name} [{arm} run {index}] aborted by mock {where}: {reason}")
                if field(run, "skippedPaidGraders"):
                    skipped = True
    return problems, skipped


class Args(argparse.Namespace):
    """The parsed command line, typed."""

    def __init__(self) -> None:
        """Start from the defaults; argparse sets every attribute it parses."""
        super().__init__()
        self.result: Path = Path()
        self.min_mean_delta: float | None = None


def load(path: Path) -> JsonObject | None:
    """Return the result document, or None after saying why it can't be read."""
    try:
        doc = parse_json(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        _ = sys.stderr.write(f"eval-gate: cannot read {path}: {error}\n")
        return None
    if not isinstance(doc, JsonObject):
        _ = sys.stderr.write(f"eval-gate: {path} is not a JSON object\n")
        return None
    return doc


def verdict(doc: JsonObject, min_mean_delta: float | None) -> int:
    """Print the problems and the summary, and return the gate's exit code."""
    if field(doc, "partial"):
        _ = sys.stdout.write(f"not comparable: partial result ({field(doc, 'partialReason')})\n")
        return EXIT_NOT_COMPARABLE
    problems, skipped = run_problems(items(field(doc, "cases")))
    _ = sys.stdout.write("".join(f"{line}\n" for line in problems))
    if skipped:
        _ = sys.stdout.write("not comparable: the cost ceiling skipped judge graders\n")
        return EXIT_NOT_COMPARABLE
    if problems:
        _ = sys.stdout.write("not comparable: a run errored or a mock aborted it\n")
        return EXIT_NOT_COMPARABLE
    aggregates = field(doc, "aggregates")
    mean = number(field(aggregates, "meanDelta"))
    _ = sys.stdout.write(f"overallScore={field(aggregates, 'overallScore')} meanDelta={mean}\n")
    failure = None
    if min_mean_delta is not None and mean is None:
        failure = "no meanDelta: a one-arm run has no baseline to compare"
    elif min_mean_delta is not None and mean is not None and mean < min_mean_delta:
        failure = f"meanDelta {mean} is below {min_mean_delta}"
    if failure:
        _ = sys.stdout.write(f"FAIL: {failure}\n")
        return EXIT_FAILED
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    """Read the result, refuse a result that isn't comparable, and apply the gate."""
    parser = argparse.ArgumentParser(prog="eval-gate", description=__doc__)
    _ = parser.add_argument("result", type=Path, help="the --json result or aggregate-result.json")
    _ = parser.add_argument("--min-mean-delta", type=float, help="minimum aggregates.meanDelta")
    args = parser.parse_args(argv, namespace=Args())
    doc = load(args.result)
    return EXIT_UNREADABLE if doc is None else verdict(doc, args.min_mean_delta)


if __name__ == "__main__":
    sys.exit(main())
