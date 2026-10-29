#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.15.*"
# dependencies = ["jsonschema[format]", "referencing"]
# ///
"""Run maintainer Python tests on unittest; any skip, expected failure or unexpected success fails.

Usage: scripts/testers/run_unittest.py <test dir>...

A skip means a tool or input is missing, so it is a failure here, and so is an expected failure,
an unexpected success, a directory with no tests and a run with none at all (unittest passes an
empty run). Warnings are errors, while importing the tests and while running them. The
dependencies above are every test suite's: Basedpyright reads this script's environment
(`uv sync --script`, then `uv python find --script`) to resolve their imports. Each directory is
discovered as its own top level, with a fresh loader, so it is put on sys.path; test module names
must therefore differ across the directories.
"""

import sys
import unittest
import warnings


def main(argv: list[str]) -> int:
    """Discover the tests of every directory, run them in one suite and return the exit code."""
    if not argv:
        _ = sys.stderr.write("usage: scripts/testers/run_unittest.py <test dir>...\n")
        return 2
    warnings.simplefilter("error")
    suite = unittest.TestSuite()
    empty: list[str] = []
    for directory in argv:
        found = unittest.TestLoader().discover(directory, top_level_dir=directory)
        if found.countTestCases() == 0:
            empty.append(directory)
        suite.addTest(found)
    result = unittest.TextTestRunner(verbosity=2, warnings="error").run(suite)
    failed = False
    if empty or result.testsRun == 0:
        _ = sys.stderr.write("✖ No tests found in:\n" + "".join(f"  {d}\n" for d in empty or argv))
        failed = True
    if result.skipped:
        _ = sys.stderr.write(
            "✖ Skipped tests fail the run (a skip means a tool or input is missing):\n"
            + "".join(f"  {test.id()} ({why})\n" for test, why in result.skipped)
        )
        failed = True
    if result.expectedFailures or result.unexpectedSuccesses:
        _ = sys.stderr.write(
            "✖ Expected failures and unexpected successes fail the run:\n"
            + "".join(f"  {test.id()}\n" for test, _tb in result.expectedFailures)
            + "".join(f"  {test.id()}\n" for test in result.unexpectedSuccesses)
        )
        failed = True
    return 1 if failed or not result.wasSuccessful() else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
