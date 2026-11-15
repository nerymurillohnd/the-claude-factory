#!/usr/bin/env python3
"""Tests for the plugin-testing-and-debugging skill's ci-evals.sh, with a stub `claude` on PATH."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1] / "skills" / "plugin-testing-and-debugging"
SCRIPT = SKILL / "assets" / "ci-evals.sh"
GATE = SKILL / "scripts" / "gate_eval_result.py"

# The stub stands in for `claude plugin eval`: it writes the result file named after --json and
# exits with STUB_EXIT.
STUB = """#!/usr/bin/env bash
previous=""
for arg in "$@"; do
  if [[ ${previous} == --json ]]; then printf '%s' "${STUB_RESULT}" >"${arg}"; fi
  previous="${arg}"
done
exit "${STUB_EXIT:-0}"
"""

RESULT = (
    '{"schemaVersion": 1, "partial": false, "cases": [],'
    ' "aggregates": {"overallScore": 1.0, "meanDelta": 0.5}}'
)


class CiEvalsTest(unittest.TestCase):
    """The exit code a user's CI sees: 1 fail, 2 not comparable, never 2 for a broken setup."""

    def run_step(self, gate: str, stub_exit: int = 0) -> tuple[int, str]:
        """Run the CI step with the stub; return (exit code, stderr)."""
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            stub = bin_dir / "claude"
            _ = stub.write_text(STUB, encoding="utf-8")
            stub.chmod(0o755)
            env = {
                **os.environ,
                "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                "STUB_RESULT": RESULT,
                "STUB_EXIT": str(stub_exit),
                "RESULT": str(Path(tmp) / "result.json"),
                "GATE_SCRIPT": gate,
            }
            # The template's <minimum mean delta> placeholder is set to a number, as a user would.
            text = SCRIPT.read_text(encoding="utf-8").replace("<minimum mean delta>", "0.2")
            step = Path(tmp) / "ci-evals.sh"
            _ = step.write_text(text, encoding="utf-8")
            done = subprocess.run(
                [shutil.which("bash") or "bash", str(step)],
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
        return done.returncode, done.stderr

    def test_passing_gate_exits_0(self) -> None:
        """A clean run whose delta clears the minimum passes."""
        self.assertEqual(self.run_step(str(GATE))[0], 0)

    def test_missing_gate_script_fails_hard(self) -> None:
        """A gate script that isn't where GATE_SCRIPT points is a setup error (1), not a 2."""
        code, err = self.run_step("/nonexistent/gate_eval_result.py")
        self.assertEqual(code, 1)
        self.assertIn("gate script not found", err)

    def test_partial_run_exits_2(self) -> None:
        """A partial eval run keeps its own exit 2."""
        self.assertEqual(self.run_step(str(GATE), stub_exit=2)[0], 2)

    def test_failing_interrupted_and_terminated_runs_pass_through(self) -> None:
        """Exits 1, 130 and 143 reach CI unchanged, and the gate never runs on that result."""
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "gate-ran"
            spy = Path(tmp) / "spy_gate.py"
            _ = spy.write_text(
                f"from pathlib import Path\n_ = Path({str(marker)!r}).write_text('ran')\n",
                encoding="utf-8",
            )
            for stub_exit in (1, 130, 143):
                with self.subTest(stub_exit=stub_exit):
                    code, err = self.run_step(str(spy), stub_exit=stub_exit)
                    self.assertEqual(code, stub_exit)
                    self.assertNotEqual(err, "")
                    self.assertFalse(marker.exists())


if __name__ == "__main__":
    _ = unittest.main()
