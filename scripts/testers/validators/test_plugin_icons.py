"""scripts/validators/plugin-icons.py: only a declared, square PNG of 512 to 2048 px passes.

Each test runs the validator by path on a small repository under a temporary directory (TCF_ROOT);
the last one runs it on this repository, which must pass.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
from typing import override
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "scripts" / "validators" / "plugin-icons.py"
ICON = "./.claude-plugin/icon.png"


def png(width: int, height: int) -> bytes:
    """A minimal valid grayscale PNG of the given size."""

    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    rows = b"".join(b"\x00" + b"\x00" * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


class PluginIconsTest(unittest.TestCase):
    """The validator on hand-built repositories."""

    root: Path = Path()

    @override
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "plugins").mkdir()
        (self.root / "scripts" / "generators" / "plugin-icons").mkdir(parents=True)

    def plugin(
        self,
        name: str,
        icon: object = ICON,
        image: bytes | None = None,
        *,
        source: bool = True,
    ) -> Path:
        """A plugin with a manifest, an optional icon file and an optional SVG source."""
        meta = self.root / "plugins" / name / ".claude-plugin"
        meta.mkdir(parents=True)
        manifest: dict[str, object] = {"name": name}
        if icon is not None:
            manifest["icon"] = icon
        _ = (meta / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
        if image is not None:
            _ = (meta / "icon.png").write_bytes(image)
        if source:
            svg = self.root / "scripts" / "generators" / "plugin-icons" / f"{name}.svg"
            _ = svg.write_text("<svg/>", encoding="utf-8")
        return meta

    def run_validator(self, root: Path | None = None) -> subprocess.CompletedProcess[str]:
        """The validator's result on `root`, by default the temporary repository."""
        env = {**os.environ, "TCF_ROOT": str(root or self.root)}
        if root == ROOT:
            del env["TCF_ROOT"]
        return subprocess.run(
            [sys.executable, str(VALIDATOR)],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

    def assert_fails(self, *messages: str) -> None:
        """The run fails, and its errors hold each message."""
        result = self.run_validator()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for message in messages:
            self.assertIn(message, result.stderr)

    def test_valid_icons_pass(self) -> None:
        """Square PNGs of 512 and 2048 px pass."""
        _ = self.plugin("small", image=png(512, 512))
        _ = self.plugin("large", image=png(2048, 2048))
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("✔", result.stdout)

    def test_undeclared_icon_fails(self) -> None:
        """A manifest without "icon" fails."""
        _ = self.plugin("demo", icon=None, image=png(1024, 1024))
        self.assert_fails('[plugins/demo] "icon" must be "./.claude-plugin/icon.png", found null')

    def test_other_path_fails(self) -> None:
        """An icon declared at another path fails."""
        _ = self.plugin("demo", icon="./assets/icon.png", image=png(1024, 1024))
        self.assert_fails('found "./assets/icon.png"')

    def test_missing_file_fails(self) -> None:
        """A declared icon with no file fails."""
        _ = self.plugin("demo")
        self.assert_fails("[plugins/demo] .claude-plugin/icon.png is missing")

    def test_symlink_fails(self) -> None:
        """An icon that is a symlink fails."""
        meta = self.plugin("demo")
        target = self.root / "real.png"
        _ = target.write_bytes(png(1024, 1024))
        (meta / "icon.png").symlink_to(target)
        self.assert_fails(".claude-plugin/icon.png is a symlink")

    def test_not_a_png_fails(self) -> None:
        """An icon that is not a PNG fails."""
        _ = self.plugin("demo", image=b"\xff\xd8\xff\xe0 not a png")
        self.assert_fails(".claude-plugin/icon.png is not a PNG file")

    def test_non_square_fails(self) -> None:
        """A non-square icon fails."""
        _ = self.plugin("demo", image=png(1024, 512))
        self.assert_fails("is 1024x512 px; it must be square")

    def test_too_small_fails(self) -> None:
        """An icon under 512 px fails."""
        _ = self.plugin("demo", image=png(256, 256))
        self.assert_fails("is 256x256 px; each side must be 512 to 2048 px")

    def test_too_large_fails(self) -> None:
        """An icon over 2048 px fails."""
        _ = self.plugin("demo", image=png(2049, 2049))
        self.assert_fails("is 2049x2049 px; each side must be 512 to 2048 px")

    def test_two_megabytes_fails(self) -> None:
        """An icon of 2 MB or more fails."""
        padding = b"\x00" * (2 * 1024 * 1024)
        _ = self.plugin("demo", image=png(1024, 1024) + padding)
        self.assert_fails("the directory takes under 2 MB")

    def test_unreadable_manifest_fails(self) -> None:
        """A manifest that is not JSON fails."""
        meta = self.plugin("demo", image=png(1024, 1024))
        _ = (meta / "plugin.json").write_text("{", encoding="utf-8")
        self.assert_fails("[plugins/demo] .claude-plugin/plugin.json cannot be read")

    def test_missing_source_fails(self) -> None:
        """A plugin without its SVG source fails."""
        _ = self.plugin("demo", image=png(1024, 1024), source=False)
        self.assert_fails("scripts/generators/plugin-icons/demo.svg, the icon source, is missing")

    def test_orphan_source_fails(self) -> None:
        """An SVG source without its plugin fails."""
        _ = self.plugin("demo", image=png(1024, 1024))
        orphan = self.root / "scripts" / "generators" / "plugin-icons" / "gone.svg"
        _ = orphan.write_text("<svg/>", encoding="utf-8")
        self.assert_fails("[scripts/generators/plugin-icons/gone.svg] no plugin is named gone")

    def test_arguments_exit_2(self) -> None:
        """Any argument exits 2."""
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "extra"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)

    def test_repository_passes(self) -> None:
        """This repository passes."""
        result = self.run_validator(ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    _ = unittest.main()
