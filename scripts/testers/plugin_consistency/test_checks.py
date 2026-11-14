#!/usr/bin/env python3
"""Tests for plugin-consistency: one passing and one failing case per check."""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
import struct
import tempfile
import unittest

from validators.plugin_consistency import cli
from validators.plugin_consistency.checks import Finding, check

from testers.release.helpers import Marketplace, changelog

WORDS = " ".join(["word"] * 40)
LISTING: dict[str, object] = {
    "icon": "./.claude-plugin/icon.png",
    "documentationUrl": "https://example.com/docs",
    "supportUrl": "https://example.com/support",
    "privacyPolicyUrl": "https://example.com/privacy",
}


def png(width: int, height: int) -> bytes:
    """Return the first bytes of a PNG with the given size: enough for its IHDR chunk."""
    return b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0dIHDR" + struct.pack(">II", width, height)


def write_icon(root: Path, name: str, width: int = 1024, height: int = 1024) -> None:
    """Write a plugin's icon.png and its SVG source."""
    icon = root / "plugins" / name / ".claude-plugin" / "icon.png"
    icon.parent.mkdir(parents=True, exist_ok=True)
    _ = icon.write_bytes(png(width, height))
    source = root / "scripts" / "generators" / "plugin-icons" / f"{name}.svg"
    source.parent.mkdir(parents=True, exist_ok=True)
    _ = source.write_text("<svg/>\n", encoding="utf-8")


def plugin_readme(name: str) -> str:
    """Return a README that passes PC-06 and PC-07 for name."""
    badge = (
        "https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com"
        f"%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2F{name}%2F.claude-plugin"
        "%2Fplugin.json&query=%24.version"
    )
    commands = "\n".join(
        f"claude plugin {verb} {name}@the-claude-factory"
        for verb in ("install", "update", "uninstall")
    )
    head = f"# {name}\n\n[![Version]({badge})](./CHANGELOG.md)\n\n{WORDS}\n\n"
    return f"{head}```bash\n{commands}\n```\n"


def catalog_row(name: str, version: str) -> str:
    """Return a root README catalog row for name."""
    return (
        f"| [**{name}**](./plugins/{name}#readme)<br>`{name}@the-claude-factory` | Does it. "
        f"| 💻 Code only | `{version}` | 🎯 Skills |"
    )


def root_readme(rows: dict[str, list[str]], counts: dict[str, int] | None = None) -> str:
    """Return a root README whose catalog has one section per category with its rows."""
    head = ["# Factory", "", "## 📦 Catalog", "", "| Category | Plugins |", "| :-- | :--: |"]
    sections: list[str] = []
    for title, lines in rows.items():
        count = (counts or {}).get(title, len(lines))
        head.append(f"| [{title}](#x) | {count} |")
        sections += ["", f"### {title}", "", "| Plugin | What | Works | Version | Includes |"]
        sections += ["| :-- | :-- | :-- | :--: | :-- |", *lines]
    return "\n".join([*head, *sections, "", "## 🤝 Contributing", ""]) + "\n"


class Fixture:
    """A consistent marketplace with demo 0.1.0 (category development), released and tagged."""

    def __init__(self, tmp: Path) -> None:
        """Build, commit, push and tag the fixture."""
        self.m: Marketplace = Marketplace(tmp)
        self.m.add_plugin(
            "demo",
            "0.1.0",
            changelog_text=changelog("demo", {"0.1.0": "- First."}),
            manifest=LISTING,
            entry={"category": "development"},
        )
        write_icon(self.m.root, "demo")
        self.m.write("plugins/demo/README.md", plugin_readme("demo"))
        self.m.write("README.md", root_readme({"🛠️ Development": [catalog_row("demo", "0.1.0")]}))
        self.m.commit()
        self.m.push()
        self.m.tag("demo--v0.1.0")

    def ids(self, *, offline: bool = False) -> list[str]:
        """Return the check ids the fixture reports."""
        return [f.check_id for f in check(self.m.root, offline=offline)]


class ChecksTest(unittest.TestCase):
    """PC-01 to PC-10."""

    def test_consistent_fixture_passes(self) -> None:
        """The fixture as built has no finding, online or offline."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            self.assertEqual((f.ids(), f.ids(offline=True)), ([], []))

    def test_pc01_name_mismatch(self) -> None:
        """plugin.json's name differs from its folder and entry."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.write(
                "plugins/demo/.claude-plugin/plugin.json", '{"name": "other", "version": "0.1.0"}\n'
            )
            self.assertIn("PC-01", f.ids(offline=True))

    def test_pc01_unlisted_folder(self) -> None:
        """A plugin folder the marketplace doesn't list is reported."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.write("plugins/stray/.claude-plugin/plugin.json", '{"name": "stray"}\n')
            self.assertIn("PC-01", f.ids(offline=True))

    def test_pc02_renamed_plugin_still_listed(self) -> None:
        """A renames key that is still a listed plugin is reported."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.write_marketplace({"renames": {"demo": None}})
            self.assertIn("PC-02", f.ids(offline=True))

    def test_pc03_force_remove_off(self) -> None:
        """ForceRemoveDeletedPlugins must be true."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.write_marketplace({"forceRemoveDeletedPlugins": False})
            self.assertEqual(f.ids(offline=True), ["PC-03"])

    def test_pc04_changelog_version_without_tag(self) -> None:
        """A released changelog version with no tag is reported, but not offline."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            text = changelog("demo", {"0.1.0": "- First.", "0.0.9": "- Older."})
            f.m.write("plugins/demo/CHANGELOG.md", text)
            self.assertEqual((f.ids(), f.ids(offline=True)), (["PC-04"], []))

    def test_pc04_skips_the_version_being_released(self) -> None:
        """The work tree's new version, not on origin/main yet, needs no tag."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            text = changelog("demo", {"0.2.0": "- New.", "0.1.0": "- First."})
            f.m.add_plugin(
                "demo",
                "0.2.0",
                changelog_text=text,
                manifest=LISTING,
                entry={"category": "development"},
            )
            f.m.write("README.md", root_readme({"🛠️ Development": [catalog_row("demo", "0.2.0")]}))
            self.assertEqual(f.ids(), [])

    def test_pc05_unreleased_notes_on_main(self) -> None:
        """On main, [Unreleased] holds no notes."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            text = changelog("demo", {"0.1.0": "- First."}, unreleased="- Pending.")
            f.m.write("plugins/demo/CHANGELOG.md", text)
            self.assertEqual(f.ids(offline=True), ["PC-05"])

    def test_pc06_placeholder_and_short_readme(self) -> None:
        """A leftover placeholder and a README under 40 words outside code are each reported."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.write("plugins/demo/README.md", plugin_readme("demo") + "{{emoji}}\n")
            self.assertEqual(f.ids(offline=True), ["PC-06"])
            short = plugin_readme("demo").replace(WORDS, "Too short.")
            f.m.write("plugins/demo/README.md", short)
            self.assertEqual(f.ids(offline=True), ["PC-06"])

    def test_pc07_readme_names_another_plugin(self) -> None:
        """The badge and commands must name the plugin itself."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.write("plugins/demo/README.md", plugin_readme("other"))
            self.assertEqual(sorted(set(f.ids(offline=True))), ["PC-07"])

    def test_pc08_missing_catalog_row(self) -> None:
        """Every listed plugin has one catalog row."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.write("README.md", root_readme({"🛠️ Development": []}, {"🛠️ Development": 0}))
            self.assertEqual(f.ids(offline=True), ["PC-08"])

    def test_pc08_row_version_section_and_count(self) -> None:
        """A row with the wrong version, under the wrong category, or a wrong count is reported."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.write("README.md", root_readme({"🛠️ Development": [catalog_row("demo", "9.9.9")]}))
            self.assertEqual(f.ids(offline=True), ["PC-08"])
            f.m.write("README.md", root_readme({"🛡️ Security": [catalog_row("demo", "0.1.0")]}))
            self.assertEqual(f.ids(offline=True), ["PC-08"])
            rows = {"🛠️ Development": [catalog_row("demo", "0.1.0")]}
            f.m.write("README.md", root_readme(rows, {"🛠️ Development": 2}))
            self.assertEqual(f.ids(offline=True), ["PC-08"])

    def test_pc09_icon_missing_undeclared_or_wrong_shape(self) -> None:
        """An undeclared, missing, non-PNG, non-square or undersized icon is reported."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            icon = f.m.root / "plugins/demo/.claude-plugin/icon.png"
            _ = icon.write_bytes(png(1024, 512))
            self.assertEqual(f.ids(offline=True), ["PC-09"])
            _ = icon.write_bytes(png(256, 256))
            self.assertEqual(f.ids(offline=True), ["PC-09"])
            _ = icon.write_bytes(b"not a png, just some bytes")
            self.assertEqual(f.ids(offline=True), ["PC-09"])
            icon.unlink()
            self.assertEqual(f.ids(offline=True), ["PC-09"])
            write_icon(f.m.root, "demo")
            f.m.add_plugin(
                "demo",
                "0.1.0",
                changelog_text=changelog("demo", {"0.1.0": "- First."}),
                manifest={**LISTING, "icon": "./logo.png"},
                entry={"category": "development"},
            )
            self.assertEqual(f.ids(offline=True), ["PC-09"])

    def test_pc09_missing_and_stray_svg_source(self) -> None:
        """A listed plugin without its SVG source, and a source without a plugin, are reported."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            sources = f.m.root / "scripts/generators/plugin-icons"
            _ = (sources / "demo.svg").rename(sources / "gone.svg")
            self.assertEqual(f.ids(offline=True), ["PC-09", "PC-09"])

    def test_pc10_listing_url_missing_or_not_https(self) -> None:
        """Each listing URL field is set to an https:// URL."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.add_plugin(
                "demo",
                "0.1.0",
                changelog_text=changelog("demo", {"0.1.0": "- First."}),
                manifest={**LISTING, "supportUrl": "http://example.com"},
                entry={"category": "development"},
            )
            self.assertEqual(f.ids(offline=True), ["PC-10"])
            manifest = {k: v for k, v in LISTING.items() if k != "privacyPolicyUrl"}
            f.m.add_plugin(
                "demo",
                "0.1.0",
                changelog_text=changelog("demo", {"0.1.0": "- First."}),
                manifest=manifest,
                entry={"category": "development"},
            )
            self.assertEqual(f.ids(offline=True), ["PC-10"])


class CliTest(unittest.TestCase):
    """The command line's output and exit codes."""

    def test_exit_codes_and_text(self) -> None:
        """Exit 0 and no output when clean; exit 1 and one line per finding otherwise."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                clean = cli.main(["--root", str(f.m.root), "--offline"])
            f.m.write_marketplace({"forceRemoveDeletedPlugins": False})
            out_bad = io.StringIO()
            with contextlib.redirect_stdout(out_bad):
                bad = cli.main(["--root", str(f.m.root), "--offline"])
        self.assertEqual((clean, out.getvalue()), (0, ""))
        self.assertEqual(bad, 1)
        self.assertTrue(out_bad.getvalue().startswith("PC-03 .claude-plugin/marketplace.json: "))

    def test_finding_text(self) -> None:
        """A finding prints as `<id> <path>: <message>`."""
        self.assertEqual(str(Finding("PC-01", "a/b", "msg")), "PC-01 a/b: msg")


if __name__ == "__main__":
    _ = unittest.main()
