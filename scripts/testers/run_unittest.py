#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.15.*"
# dependencies = ["jsonschema[format]", "referencing"]
# ///
"""Run maintainer Python tests on unittest; any skip, expected failure or unexpected success fails.

Usage: scripts/testers/run_unittest.py <test dir>...

A skip means a tool or input is missing, so it is a failure here, and so is an expected failure,
an unexpected success, a directory with no tests and a run with none at all (unittest passes an
empty run). Warnings are errors, while importing the tests and while running them, and so is an
exception Python can only report as unraisable, such as the ResourceWarning of a file left open. A
file named like a test (`test*.py` or `*_test.py`, anywhere under a directory) that discovery did
not load also fails the run, so a test never runs silently. The
dependencies above are every test suite's: Basedpyright reads this script's environment
(`uv sync --script`, then `uv python find --script`) to resolve their imports. Each directory is
discovered as its own top level, with a fresh loader, so it is put on sys.path; test module names
must therefore differ across the directories.
"""

from pathlib import Path
import sys
from typing import TYPE_CHECKING
import unittest
import warnings

if TYPE_CHECKING:
    from collections.abc import Iterator


def cases(suite: unittest.TestSuite) -> Iterator[unittest.TestCase]:
    """Every test case in a suite, nested suites flattened."""
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from cases(test)
        else:
            yield test


def unloaded(directory: str, suite: unittest.TestSuite) -> list[Path]:
    """Files under `directory` named like a test whose module discovery did not load."""
    loaded: set[Path] = set()
    for test in cases(suite):
        module = sys.modules.get(type(test).__module__)
        file = getattr(module, "__file__", None)
        if isinstance(file, str):
            loaded.add(Path(file).resolve())
    named = {*Path(directory).rglob("test*.py"), *Path(directory).rglob("*_test.py")}
    return sorted(f for f in named if f.resolve() not in loaded)


def section(title: str, lines: list[str]) -> str:
    """One failure reason and its items, or nothing when there are no items."""
    return title + ":\n" + "".join(f"  {line}\n" for line in lines) if lines else ""


def main(argv: list[str]) -> int:
    """Discover the tests of every directory, run them in one suite and return the exit code."""
    if not argv:
        _ = sys.stderr.write("usage: scripts/testers/run_unittest.py <test dir>...\n")
        return 2
    warnings.simplefilter("error")
    unraisable: list[str] = []
    sys.unraisablehook = lambda hook: unraisable.append(
        f"{hook.exc_type.__name__}: {hook.exc_value}"
    )
    suite = unittest.TestSuite()
    empty: list[str] = []
    missed: list[str] = []
    for directory in argv:
        found = unittest.TestLoader().discover(directory, top_level_dir=directory)
        if found.countTestCases() == 0:
            empty.append(directory)
        missed += [str(f) for f in unloaded(directory, found)]
        suite.addTest(found)
    result = unittest.TextTestRunner(verbosity=2, warnings="error").run(suite)
    report = "".join(
        [
            section("✖ Files named like tests that discovery did not load", missed),
            section("✖ Unraisable exceptions fail the run", unraisable),
            section("✖ No tests found in", empty or (argv if result.testsRun == 0 else [])),
            section(
                "✖ Skipped tests fail the run (a skip means a tool or input is missing)",
                [f"{test.id()} ({why})" for test, why in result.skipped],
            ),
            section(
                "✖ Expected failures and unexpected successes fail the run",
                [test.id() for test, _tb in result.expectedFailures]
                + [test.id() for test in result.unexpectedSuccesses],
            ),
        ]
    )
    _ = sys.stderr.write(report)
    return 1 if report or not result.wasSuccessful() else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
