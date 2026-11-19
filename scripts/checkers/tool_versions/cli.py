#!/usr/bin/env python3
"""Report each uv tool pinned in tools:install that has a newer release on PyPI.

Exit codes: 0 every pin is PyPI's latest, 1 at least one has a newer release, 2 package.json or
PyPI could not be read, so the pins could not be compared.
"""

import http.client
from pathlib import Path
import sys
from urllib.parse import urlsplit

from checkers.tool_versions.check import Fetch, compare, pins

HOST = "pypi.org"
TIMEOUT = 20


def fetch_pypi(url: str) -> bytes:
    """Read one page of PyPI's JSON API over HTTPS; any other host or scheme is refused."""
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname != HOST:
        msg = f"refusing to open {url}: only https://{HOST}/ is read"
        raise ValueError(msg)
    connection = http.client.HTTPSConnection(HOST, timeout=TIMEOUT)
    try:
        connection.request(
            "GET", parts.path, headers={"Accept": "application/json", "User-Agent": "tool-versions"}
        )
        response = connection.getresponse()
        body = response.read()
        if response.status != http.client.OK:
            msg = f"{url} answered HTTP {response.status}"
            raise OSError(msg)
    finally:
        connection.close()
    return body


def main(argv: list[str], fetch: Fetch = fetch_pypi) -> int:
    """Compare the pins of the package.json named in argv (default ./package.json) with PyPI."""
    package = Path(argv[0]) if argv else Path("package.json")
    try:
        statuses = compare(pins(package.read_text(encoding="utf-8")), fetch)
    except (OSError, ValueError, TypeError) as error:
        _ = sys.stderr.write(f"tool-versions: could not compare the pins: {error}\n")
        return 2
    outdated = [status for status in statuses if not status.current]
    for status in statuses:
        pin = status.pin
        if status.current:
            _ = sys.stdout.write(f"{pin.name} {pin.version}: current\n")
        else:
            _ = sys.stdout.write(f"{pin.name} {pin.version} -> {status.latest}: newer on PyPI\n")
    if outdated:
        _ = sys.stdout.write(
            f"{len(outdated)} tool(s) behind PyPI: update the pins in package.json's tools:install "
            "(and ruff's required-version in pyproject.toml), then run npm run tools:install.\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
