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
        """A run stopped by the cost ceiling is left out of the gate."""
        doc = result(partial=True, partialReason="cost ceiling")
        self.assertEqual(self.run_gate(json.dumps(doc), "--min-mean-delta", "0.2")[0], 2)

    def test_run_error_is_not_comparable(self) -> None:
        """A run that ended on an API error makes the result not comparable."""
        case = {"name": "demo", "arms": {"with": [{"error": "429"}], "without": []}}
        code, out = self.run_gate(json.dumps(result(cases=[case])), "--min-mean-delta", "0.2")
        self.assertEqual(code, 2)
        self.assertIn("demo [with run 1] error: 429", out)

    def test_unreadable_file_exits_3(self) -> None:
        """Text that is not a JSON object is not an eval result."""
        self.assertEqual(self.run_gate("[1, 2]")[0], 3)


if __name__ == "__main__":
    _ = unittest.main()
