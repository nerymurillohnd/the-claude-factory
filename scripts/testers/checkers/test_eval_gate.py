#!/usr/bin/env python3
"""Tests for eval-gate: the mean-delta gate on a `claude plugin eval` JSON result."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from checkers import eval_gate as gate


def _result(**extra: object) -> dict[str, object]:
    """Return a complete two-arm result with meanDelta 0.25 and one clean case."""
    case: dict[str, object] = {
        "name": "demo",
        "aggregates": {"delta": 0.25},
        "arms": {"with": [{"score": 1.0}], "without": [{"score": 0.75}]},
    }
    doc: dict[str, object] = {
        "schemaVersion": 1,
        "partial": False,
        "aggregates": {"overallScore": 1.0, "meanDelta": 0.25, "casesPassed": 1, "casesTotal": 1},
        "cases": [case],
    }
    doc.update(extra)
    return doc


class EvalGateTest(unittest.TestCase):
    """Exit codes: 0 pass, 1 fail, 2 not comparable, 3 unreadable."""

    def _run(self, doc: object, *args: str) -> tuple[int, str]:
        """Write doc as JSON, run the gate on it, and return (exit code, stdout)."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"
            _ = path.write_text(json.dumps(doc), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = gate.main([str(path), *args])
        return code, out.getvalue()

    def test_mean_delta_above_the_minimum_passes(self) -> None:
        """MeanDelta 0.25 against 0.2 passes."""
        self.assertEqual(self._run(_result(), "--min-mean-delta", "0.2")[0], 0)

    def test_mean_delta_below_the_minimum_fails(self) -> None:
        """MeanDelta 0.1 against 0.2 fails and says why."""
        doc = _result(aggregates={"overallScore": 1.0, "meanDelta": 0.1})
        code, out = self._run(doc, "--min-mean-delta", "0.2")
        self.assertEqual(code, 1)
        self.assertIn("meanDelta 0.1 is below 0.2", out)

    def test_nan_mean_delta_fails(self) -> None:
        """NaN compares false against any minimum, so it counts as no meanDelta."""
        doc = _result(aggregates={"overallScore": 1.0, "meanDelta": float("nan")})
        code, out = self._run(doc, "--min-mean-delta", "0.2")
        self.assertEqual(code, 1)
        self.assertIn("no meanDelta", out)

    def test_partial_result_is_not_comparable(self) -> None:
        """Each documented partialReason leaves the result out of the gate."""
        for reason in ("cost_ceiling", "interrupted", "auth_failed"):
            with self.subTest(reason=reason):
                doc = _result(partial=True, partialReason=reason)
                code, out = self._run(doc, "--min-mean-delta", "0.2")
                self.assertEqual(code, 2)
                self.assertIn(reason, out)

    def test_skipped_paid_graders_are_not_comparable(self) -> None:
        """A run whose judge graders were skipped is left out of the gate."""
        case = {"name": "demo", "arms": {"with": [{"skippedPaidGraders": True}], "without": []}}
        self.assertEqual(self._run(_result(cases=[case]), "--min-mean-delta", "0.2")[0], 2)

    def test_one_arm_result_fails_the_delta_gate(self) -> None:
        """Without a baseline arm there is no meanDelta to gate on."""
        doc = _result(aggregates={"overallScore": 1.0})
        code, out = self._run(doc, "--min-mean-delta", "0.2")
        self.assertEqual(code, 1)
        self.assertIn("no meanDelta", out)

    def test_run_error_is_a_warning_and_still_gates(self) -> None:
        """A run that timed out is still graded, so it is printed and the gate still applies."""
        case = {
            "name": "demo",
            "arms": {"with": [{"error": "timed out after 300s"}], "without": []},
        }
        code, out = self._run(_result(cases=[case]), "--min-mean-delta", "0.2")
        self.assertEqual(code, 0)
        self.assertIn("warning: demo [with run 1] error: timed out after 300s", out)

    def test_unknown_schema_version_exits_3(self) -> None:
        """Only schemaVersion 1 is a result this gate knows how to read."""
        self.assertEqual(self._run(_result(schemaVersion=2), "--min-mean-delta", "0.2")[0], 3)

    def test_mock_abort_is_not_comparable(self) -> None:
        """An aborted run scores 0 and can inflate meanDelta, so the result is left out."""
        aborted = {"server": "s", "tool": "t", "reason": "budget"}
        case = {"name": "demo", "arms": {"with": [], "without": [{"aborted": aborted}]}}
        code, out = self._run(_result(cases=[case]), "--min-mean-delta", "0.2")
        self.assertEqual(code, 2)
        self.assertIn("demo [without run 1] aborted by mock s/t: budget", out)

    def test_unreadable_file_exits_3(self) -> None:
        """Text that is not a JSON object is not an eval result."""
        self.assertEqual(self._run([1, 2])[0], 3)


if __name__ == "__main__":
    _ = unittest.main()
