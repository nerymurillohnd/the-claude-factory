#!/usr/bin/env -S PYTHONSAFEPATH=1 uv run --script
# /// script
# requires-python = "==3.15.*"
# dependencies = ["pytest", "jsonschema[format]", "referencing"]
# ///
"""Run maintainer Python tests on pytest; any skipped, xfailed or xpassed test fails the run.

Usage: scripts/tests/run_pytest.py <test path>... [pytest options]

A skip means a tool or input is missing, so it is a failure here, at collection time (a module or
class skipped while collecting) and at run time. The dependencies above are every test suite's:
Basedpyright reads this script's environment (`uv sync --script`, then `uv python find --script`)
to resolve their imports. Tests are imported with importlib, so no test directory is put on
sys.path.
"""

import sys

import pytest

OPTIONS = [
    "--import-mode=importlib",
    "--strict-markers",
    "--strict-config",
    "-p",
    "no:cacheprovider",
    "-W",
    "error",
    "-o",
    "xfail_strict=true",
    "-rsxX",
]


class FailOnSkip:
    """Collect every skipped or xfailed report, so the run can fail on them."""

    def __init__(self) -> None:
        """Start with nothing skipped."""
        self.skipped: list[str] = []

    def pytest_collectreport(self, report: pytest.CollectReport) -> None:
        """Record a module or class skipped while collecting."""
        if report.skipped:
            self.skipped.append(report.nodeid)

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        """Record a test skipped or xfailed in any phase."""
        if report.skipped:
            self.skipped.append(report.nodeid)

    def pytest_sessionfinish(self, session: pytest.Session) -> None:
        """Turn a passing run with skips into a failure."""
        if self.skipped and session.exitstatus == pytest.ExitCode.OK:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED


def main(argv: list[str]) -> int:
    """Run pytest on the given paths and return its exit code."""
    if not argv:
        _ = sys.stderr.write("usage: scripts/tests/run_pytest.py <test path>... [pytest options]\n")
        return 2
    guard = FailOnSkip()
    code = pytest.main([*OPTIONS, *argv], plugins=[guard])
    if guard.skipped:
        _ = sys.stderr.write(
            "✖ Skipped tests fail the run (a skip means a tool or input is missing):\n"
            + "".join(f"  {nodeid}\n" for nodeid in guard.skipped)
        )
        return int(pytest.ExitCode.TESTS_FAILED)
    return int(code)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
