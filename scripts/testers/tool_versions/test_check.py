#!/usr/bin/env python3
"""Tests for tool-versions: reading the pins, and comparing them with PyPI's latest release."""

from collections.abc import Callable
import json
import unittest

from checkers.tool_versions.check import Pin, Status, compare, pins

INSTALL = (
    "uv tool install ruff==0.17.5 && uv tool install basedpyright==1.40.2"
    " && uv tool install check-jsonschema==0.39.0"
)

type Fetch = Callable[[str], bytes]


def package(install: str) -> str:
    """A package.json whose tools:install script is the given command."""
    return json.dumps({"scripts": {"tools:install": install}})


def pypi(versions: dict[str, str]) -> Fetch:
    """A fake fetch that answers PyPI's JSON API from a name-to-version table."""

    def fetch(url: str) -> bytes:
        name = url.rstrip("/").split("/")[-2]
        if name not in versions:
            msg = f"no such project: {name}"
            raise OSError(msg)
        return json.dumps({"info": {"version": versions[name]}}).encode()

    return fetch


class PinsTest(unittest.TestCase):
    """The pins come from package.json's tools:install script."""

    def test_reads_every_pin(self) -> None:
        """Each `uv tool install name==version` becomes one pin, in order."""
        expected = [
            Pin("ruff", "0.17.5"),
            Pin("basedpyright", "1.40.2"),
            Pin("check-jsonschema", "0.39.0"),
        ]
        self.assertEqual(pins(package(INSTALL)), expected)

    def test_missing_script_is_an_error(self) -> None:
        """A package.json without tools:install has nothing to check: that is an error."""
        with self.assertRaises(ValueError):
            _ = pins(json.dumps({"scripts": {}}))

    def test_unpinned_install_is_an_error(self) -> None:
        """A tool installed without ==version can't be compared: that is an error."""
        with self.assertRaises(ValueError):
            _ = pins(package("uv tool install ruff"))


class CompareTest(unittest.TestCase):
    """Each pin is current or outdated against PyPI's latest version."""

    def test_current_and_outdated(self) -> None:
        """A pin equal to PyPI's version is current; a different one is outdated."""
        fetch = pypi({"ruff": "0.17.5", "basedpyright": "1.41.0", "check-jsonschema": "0.39.0"})
        result = compare(pins(package(INSTALL)), fetch)
        self.assertEqual(
            [(item.pin.name, item.latest, item.current) for item in result],
            [
                ("ruff", "0.17.5", True),
                ("basedpyright", "1.41.0", False),
                ("check-jsonschema", "0.39.0", True),
            ],
        )
        self.assertIsInstance(result[0], Status)

    def test_asks_pypi_json_api(self) -> None:
        """The version comes from https://pypi.org/pypi/<name>/json."""
        asked: list[str] = []

        def fetch(url: str) -> bytes:
            asked.append(url)
            return json.dumps({"info": {"version": "1.0"}}).encode()

        _ = compare([Pin("zizmor", "1.0")], fetch)
        self.assertEqual(asked, ["https://pypi.org/pypi/zizmor/json"])

    def test_unreachable_index_is_an_error(self) -> None:
        """A fetch that fails is raised, never reported as current."""
        with self.assertRaises(OSError):
            _ = compare([Pin("missing-tool", "1.0")], pypi({}))


if __name__ == "__main__":
    _ = unittest.main()
