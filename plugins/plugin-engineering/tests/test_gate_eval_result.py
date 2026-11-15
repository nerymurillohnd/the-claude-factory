#!/usr/bin/env python3
"""Tests for the plugin-testing-and-debugging skill's gate_eval_result.py, run as users run it."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "plugin-testing-and-debugging"
    / "scripts"
    / "gate_eval_result.py"
)


def result(**extra: object) -> dict[str, object]:
    """Return a complete two-arm result with meanDelta 0.25 and one clean case."""
    doc: dict[str, object] = {
        "schemaVersion": 1,
        "partial": False,
        "aggregates": {"overallScore": 1.0, "meanDelta": 0.25, "casesPassed": 1, "casesTotal": 1},
        "cases": [
            {
                "name": "demo",
                "aggregates": {"delta": 0.25},
                "arms": {"with": [{"score": 1.0}], "without": [{"score": 0.75}]},
            }
        ],
    }
    doc.update(extra)
    return doc


class GateEvalResultTest(unittest.TestCase):
    """Exit codes: 0 pass, 1 fail, 2 not comparable, 3 unreadable."""

    def run_gate(self, text: str, *args: str) -> tuple[int, str]:
        """Write text as the result file, run the gate on it, and return (exit code, stdout)."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"
            _ = path.write_text(text, encoding="utf-8")
            done = subprocess.run(
                [sys.executable, str(SCRIPT), str(path), *args],
                capture_output=True,
                text=True,
                check=False,
            )
        return done.returncode, done.stdout

    def test_mean_delta_above_the_minimum_passes(self) -> None:
        """MeanDelta 0.25 against 0.2 passes."""
        self.assertEqual(self.run_gate(json.dumps(result()), "--min-mean-delta", "0.2")[0], 0)

    def test_mean_delta_below_the_minimum_fails(self) -> None:
        """MeanDelta 0.1 against 0.2 fails."""
        doc = result(aggregates={"overallScore": 1.0, "meanDelta": 0.1})
        self.assertEqual(self.run_gate(json.dumps(doc), "--min-mean-delta", "0.2")[0], 1)

    def test_nan_passes_no_gate(self) -> None:
        """A NaN delta or score is not a number to compare, so every gate on it fails."""
        doc = result(aggregates={"overallScore": float("nan"), "meanDelta": float("nan")})
        for flag in ("--min-mean-delta", "--min-score"):
            with self.subTest(flag=flag):
                self.assertEqual(self.run_gate(json.dumps(doc), flag, "0.2")[0], 1)

    def test_partial_result_is_not_comparable(self) -> None:
        """A suite that didn't finish is left out of the gate, whatever the documented reason."""
        for reason in ("cost_ceiling", "interrupted", "auth_failed"):
            with self.subTest(reason=reason):
                doc = result(partial=True, partialReason=reason)
                code, out = self.run_gate(json.dumps(doc), "--min-mean-delta", "0.2")
                self.assertEqual(code, 2)
                self.assertIn(f"partial result ({reason})", out)

    def test_timed_out_run_still_gates_on_mean_delta(self) -> None:
        """A run error doesn't imply score 0: the gate still applies and the error is a warning."""
        timed_out = {
            "name": "demo",
            "aggregates": {"delta": 0.25},
            "arms": {"with": [{"error": "timed out after 300s"}], "without": [{"score": 0.75}]},
        }
        code, out = self.run_gate(json.dumps(result(cases=[timed_out])), "--min-mean-delta", "0.2")
        self.assertEqual(code, 0)
        self.assertIn("warning: demo [with run 1] error: timed out after 300s", out)
        low = result(cases=[timed_out], aggregates={"overallScore": 0.5, "meanDelta": 0.1})
        self.assertEqual(self.run_gate(json.dumps(low), "--min-mean-delta", "0.2")[0], 1)

    def test_mock_abort_is_not_comparable(self) -> None:
        """A run a mock aborted scores 0 with error null, so the result is left out of the gate."""
        aborted = {"server": "db", "tool": "query", "reason": "expect failed"}
        case = {"name": "demo", "arms": {"with": [{"error": None, "aborted": aborted}]}}
        code, out = self.run_gate(json.dumps(result(cases=[case])), "--min-mean-delta", "0.2")
        self.assertEqual(code, 2)
        self.assertIn("demo [with run 1] aborted by mock db/query: expect failed", out)

    def test_skipped_paid_graders_is_not_comparable(self) -> None:
        """A run whose judge graders the cost ceiling skipped has a score that isn't comparable."""
        case = {"name": "demo", "arms": {"without": [{"skippedPaidGraders": True}]}}
        code = self.run_gate(json.dumps(result(cases=[case])), "--min-mean-delta", "0.2")[0]
        self.assertEqual(code, 2)

    def test_one_arm_result_fails_a_delta_gate(self) -> None:
        """A one-arm result has no meanDelta, so a requested delta gate fails, never passes."""
        doc = result(aggregates={"overallScore": 1.0, "casesPassed": 1, "casesTotal": 1})
        code, out = self.run_gate(json.dumps(doc), "--min-mean-delta", "0.2")
        self.assertEqual(code, 1)
        self.assertIn("no meanDelta", out)

    def test_unreadable_file_exits_3(self) -> None:
        """Text that is not a JSON object is not an eval result."""
        self.assertEqual(self.run_gate("[1, 2]")[0], 3)


if __name__ == "__main__":
    _ = unittest.main()
