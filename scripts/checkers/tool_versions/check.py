#!/usr/bin/env python3
"""Read the uv tool pins from package.json and compare each with PyPI's latest version.

Dependabot reads package.json's dependencies and uv.lock, but not the versions inside the
tools:install npm script, so nothing else tells the maintainers when one of these tools has a
newer release.
"""

from collections.abc import Callable
from dataclasses import dataclass
import json
import re

PIN = re.compile(
    r"uv tool install\s+(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)(?:==(?P<version>[^\s&;]+))?"
)
PYPI = "https://pypi.org/pypi/{name}/json"

type Fetch = Callable[[str], bytes]


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


# Decodes JSON with every object built as JsonObject, so isinstance() narrows it cleanly.
parse_json: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


@dataclass(frozen=True)
class Pin:
    """One tool and the version tools:install installs."""

    name: str
    version: str


@dataclass(frozen=True)
class Status:
    """A pin, PyPI's latest version of it, and whether they match."""

    pin: Pin
    latest: str

    @property
    def current(self) -> bool:
        """Whether the pin is PyPI's latest version."""
        return self.pin.version == self.latest


def pins(package_json: str) -> list[Pin]:
    """Return each `uv tool install name==version` of package.json's tools:install script."""
    data = parse_json(package_json)
    scripts = data.get("scripts") if isinstance(data, JsonObject) else None
    install = scripts.get("tools:install") if isinstance(scripts, JsonObject) else None
    if install is None:
        msg = "package.json has no tools:install script"
        raise ValueError(msg)
    if not isinstance(install, str):
        msg = "package.json's tools:install is not a command string"
        raise TypeError(msg)
    found: list[Pin] = []
    for match in PIN.finditer(install):
        version = match.group("version")
        if version is None:
            msg = f"tools:install installs {match.group('name')} without ==version"
            raise ValueError(msg)
        found.append(Pin(match.group("name"), version))
    return found


def latest(name: str, fetch: Fetch) -> str:
    """PyPI's latest version of the project, from its JSON API."""
    data = parse_json(fetch(PYPI.format(name=name)).decode("utf-8"))
    info = data.get("info") if isinstance(data, JsonObject) else None
    version = info.get("version") if isinstance(info, JsonObject) else None
    if version is None:
        msg = f"PyPI returned no version for {name}"
        raise ValueError(msg)
    if not isinstance(version, str):
        msg = f"PyPI returned a version for {name} that is not text"
        raise TypeError(msg)
    return version


def compare(tools: list[Pin], fetch: Fetch) -> list[Status]:
    """Each pin with PyPI's latest version; a failed fetch is raised, never read as current."""
    return [Status(pin, latest(pin.name, fetch)) for pin in tools]
