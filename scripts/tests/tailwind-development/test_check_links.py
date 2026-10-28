#!/usr/bin/env python3
"""Tests for plugins/tailwind-development/scripts/check-links.py.

Run: python3 -m unittest discover -s scripts/tests/tailwind-development -v
Standard library only. A local HTTP server stands in for the docs site, so no
test reaches the network.
"""

from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from typing import ClassVar, override
import unittest

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "plugins" / "tailwind-development" / "scripts" / "check-links.py"
BAD_ARGUMENT = 2
PAGE = '<html><body><h2 id="good">Good</h2></body></html>'


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    """Run check-links.py by path with args."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False
    )


class CheckLinksTest(unittest.TestCase):
    """Run the script against a local server.

    /page.html has the id "good"; /old answers 301 to /old/, whose index has the
    same id; anything else answers 404.
    """

    site: ClassVar[tempfile.TemporaryDirectory[str]]
    server: ClassVar[ThreadingHTTPServer]
    base: ClassVar[str]

    @classmethod
    @override
    def setUpClass(cls) -> None:
        cls.site = tempfile.TemporaryDirectory()
        root = Path(cls.site.name)
        _ = (root / "page.html").write_text(PAGE, encoding="utf-8")
        (root / "old").mkdir()
        _ = (root / "old" / "index.html").write_text(PAGE, encoding="utf-8")
        handler = partial(SimpleHTTPRequestHandler, directory=str(root))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    @override
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.site.cleanup()

    def run_on(self, markdown: str) -> subprocess.CompletedProcess[str]:
        """Write markdown to a file and run the script on it."""
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "reference.md"
            _ = file.write_text(markdown, encoding="utf-8")
            return run_script(str(file))

    def test_valid_page_and_anchor_pass(self) -> None:
        """A live page and an id on it exit 0."""
        result = self.run_on(f"- [Good]({self.base}/page.html#good): ok\n")
        assert result.returncode == 0, result.stdout
        assert "[OK] All 1 links and anchors resolved" in result.stdout

    def test_redirect_is_followed(self) -> None:
        """A redirect to a live page with the anchor passes."""
        result = self.run_on(f"See {self.base}/old#good.\n")
        assert result.returncode == 0, result.stdout

    def test_missing_anchor_fails(self) -> None:
        """An anchor the page lacks is reported and exits 1."""
        result = self.run_on(f"[x]({self.base}/page.html#gone)\n")
        assert result.returncode == 1
        assert f"{self.base}/page.html#gone -> anchor #gone not found on page" in result.stdout

    def test_missing_page_fails(self) -> None:
        """A page that answers 404 is reported and exits 1."""
        result = self.run_on(f"[x]({self.base}/nope.html)\n")
        assert result.returncode == 1
        assert f"{self.base}/nope.html -> HTTP 404" in result.stdout

    def test_placeholders_and_trailing_punctuation_are_skipped(self) -> None:
        """URLs with placeholders are not fetched, and a trailing period is dropped."""
        text = f"`{self.base}/x@<v>` `${{CLAUDE_PLUGIN_ROOT}}/a` {self.base}/page.html.\n"
        result = self.run_on(text)
        assert result.returncode == 0, result.stdout
        assert "[OK] All 1 links and anchors resolved" in result.stdout

    def test_missing_path_exits_2(self) -> None:
        """A path that does not exist exits 2 and names it."""
        result = run_script("/no/such/file.md")
        assert result.returncode == 2
        assert "/no/such/file.md" in result.stderr


if __name__ == "__main__":
    _ = unittest.main()
