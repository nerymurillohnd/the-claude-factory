#!/usr/bin/env python3
"""Gate a CI build on a `claude plugin eval` JSON result.

`claude plugin eval` never fails on the no-plugin delta, so a build that must
fail when the plugin stops helping reads the delta from the result document.
This script does that, and refuses results that are not comparable.

Usage:
  python3 gate_eval_result.py results.json [--min-mean-delta 0.2]
      [--min-case-delta 0.0] [--min-score 0.8]

Exit codes:
  0  every requested gate passed
  1  a gate failed, or a delta gate was requested on a one-arm result
  2  the result is not comparable (partial run, or judge graders skipped by
     the cost ceiling); leave it out of trends
  3  the file could not be read as an eval result

Standard library only. Unknown fields are ignored, as the result format adds
fields without renaming.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import cast

EXIT_OK = 0
EXIT_GATE_FAILED = 1
EXIT_NOT_COMPARABLE = 2
EXIT_UNREADABLE = 3
ARMS = ("with", "without")


def out(line: str) -> None:
    """Write one line to stdout."""
    _ = sys.stdout.write(line + "\n")


def err(line: str) -> None:
    """Write one line to stderr."""
    _ = sys.stderr.write(line + "\n")


def as_dict(value: object) -> dict[str, object]:
    """Return value when it is a JSON object, else an empty one."""
    if isinstance(value, dict):
        items = cast("dict[object, object]", value)
        return {str(k): v for k, v in items.items()}
    return {}


def as_list(value: object) -> list[object]:
    """Return value when it is a JSON array, else an empty one."""
    if isinstance(value, list):
        return list(cast("list[object]", value))
    return []


def as_number(value: object) -> float | None:
    """Return value as a float when it is a JSON number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def run_problems(cases: list[object]) -> tuple[list[str], bool]:
    """List run errors and mock aborts; report whether judge graders were skipped."""
    problems: list[str] = []
    skipped_paid = False
    for case_obj in cases:
        case = as_dict(case_obj)
        name = str(case.get("name", "?"))
        arms = as_dict(case.get("arms"))
        for arm in ARMS:
            for i, run_obj in enumerate(as_list(arms.get(arm)), start=1):
                run = as_dict(run_obj)
                if run.get("error"):
                    problems.append(f"{name} [{arm} run {i}] error: {run['error']}")
                aborted = as_dict(run.get("aborted"))
                if aborted:
                    where = f"{aborted.get('server')}/{aborted.get('tool')}"
                    problems.append(
                        f"{name} [{arm} run {i}] aborted by mock {where}: {aborted.get('reason')}",
                    )
                if run.get("skippedPaidGraders"):
                    skipped_paid = True
    return problems, skipped_paid


def case_delta_failures(cases: list[object], min_case: float) -> list[str]:
    """Return one line per case whose delta is missing or below min_case."""
    failed: list[str] = []
    for case_obj in cases:
        case = as_dict(case_obj)
        delta = as_number(as_dict(case.get("aggregates")).get("delta"))
        if delta is None:
            failed.append(f"case {case.get('name')} has no delta")
        elif delta < min_case:
            failed.append(f"case {case.get('name')} delta {delta} is below {min_case}")
    return failed


def gate_failures(
    args: argparse.Namespace,
    agg: dict[str, object],
    cases: list[object],
) -> list[str]:
    """Apply the requested gates and return one line per failure."""
    failed: list[str] = []
    min_score = as_number(getattr(args, "min_score", None))
    min_mean = as_number(getattr(args, "min_mean_delta", None))
    min_case = as_number(getattr(args, "min_case_delta", None))
    score = as_number(agg.get("overallScore"))
    mean_delta = as_number(agg.get("meanDelta"))

    if min_score is not None and (score is None or score < min_score):
        failed.append(f"overallScore {score} is below {min_score}")
    if min_mean is not None:
        if mean_delta is None:
            failed.append("no meanDelta: one-arm run (--ablation none, or no baseline arm)")
        elif mean_delta < min_mean:
            failed.append(f"meanDelta {mean_delta} is below {min_mean}")
    if min_case is not None:
        failed.extend(case_delta_failures(cases, min_case))
    return failed


def parse_args() -> argparse.Namespace:
    """Parse the command line."""
    p = argparse.ArgumentParser(description="Gate a CI build on a claude plugin eval result.")
    _ = p.add_argument("result", help="results.json or aggregate-result.json")
    _ = p.add_argument("--min-mean-delta", type=float, help="minimum aggregates.meanDelta")
    _ = p.add_argument("--min-case-delta", type=float, help="minimum delta for every case")
    _ = p.add_argument("--min-score", type=float, help="minimum aggregates.overallScore")
    return p.parse_args()


def main() -> int:
    """Read the result, refuse non-comparable runs, apply the gates."""
    args = parse_args()
    path = pathlib.Path(str(getattr(args, "result", "")))
    try:
        with path.open(encoding="utf-8") as f:
            raw = cast("object", json.load(f))
        doc = as_dict(raw)
    except (OSError, ValueError) as e:
        err(f"error: cannot read {path} as an eval result: {e}")
        return EXIT_UNREADABLE
    if not doc:
        err(f"error: {path} is not a JSON object")
        return EXIT_UNREADABLE

    if doc.get("schemaVersion") != 1:
        err(f"warning: schemaVersion is {doc.get('schemaVersion')!r}; written for 1")
    if doc.get("partial"):
        out(f"not comparable: partial result ({doc.get('partialReason')})")
        return EXIT_NOT_COMPARABLE

    cases = as_list(doc.get("cases"))
    problems, skipped_paid = run_problems(cases)
    for line in problems:
        out(line)
    if skipped_paid:
        out("not comparable: the cost ceiling skipped judge graders in at least one run")
        return EXIT_NOT_COMPARABLE

    agg = as_dict(doc.get("aggregates"))
    summary = f"overallScore={agg.get('overallScore')} meanDelta={agg.get('meanDelta')}"
    out(summary + f" casesPassed={agg.get('casesPassed')}/{agg.get('casesTotal')}")
    failed = gate_failures(args, agg, cases)
    for line in failed:
        out("FAIL: " + line)
    return EXIT_GATE_FAILED if failed else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
