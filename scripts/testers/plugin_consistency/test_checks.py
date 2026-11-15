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

from testers.release.helpers import Marketplace, changelog, git

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


EVALS_WORKFLOW = """name: Evals
on:
  pull_request:
    paths:
      - plugins/*/evals/**
{paths}  workflow_dispatch:
"""


PC13 = "PC-13 .github/workflows/{path}: reads secrets.{name}, which only {owners} may read"
EVALS_WITH_GUARD = """\
env:
  CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
run: if [[ -n ${ANTHROPIC_API_KEY:-} ]]; then exit 1; fi
"""


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

    def bump(self, new: str, sections: dict[str, str]) -> None:
        """Set demo to a new version with these changelog sections and its catalog row."""
        self.m.add_plugin(
            "demo",
            new,
            changelog_text=changelog("demo", sections),
            manifest=LISTING,
            entry={"category": "development"},
        )
        self.m.write("README.md", root_readme({"🛠️ Development": [catalog_row("demo", new)]}))

    def ids(self, *, offline: bool = False) -> list[str]:
        """Return the check ids the fixture reports."""
        return [f.check_id for f in check(self.m.root, offline=offline)]


class ChecksTest(unittest.TestCase):
    """PC-01 to PC-05 and PC-12."""

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

    def test_pc04_current_version_untagged_after_merge_passes(self) -> None:
        """On main, before release.yml tags it, the current version needs no tag."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.bump("0.2.0", {"0.2.0": "- New.", "0.1.0": "- First."})
            f.m.commit()
            f.m.push()
            self.assertEqual(f.ids(), [])

    def test_pc04_older_heading_untagged_after_merge_fails(self) -> None:
        """An older version that never got its tag stays reported once a newer one is current."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.bump("0.2.1", {"0.2.1": "- Fix.", "0.2.0": "- New.", "0.1.0": "- First."})
            f.m.commit()
            f.m.push()
            messages = [str(x) for x in check(f.m.root)]
            self.assertEqual(
                messages,
                ["PC-04 plugins/demo/CHANGELOG.md: [0.2.0] has no tag demo--v0.2.0"],
            )

    def test_pc05_runs_with_main_flag_on_detached_head(self) -> None:
        """CI checks out a commit, not a branch; main=True still enforces PC-05."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            text = changelog("demo", {"0.1.0": "- First."}, unreleased="- Pending.")
            f.m.write("plugins/demo/CHANGELOG.md", text)
            f.m.commit()
            _ = git(f.m.root, "checkout", "-q", "--detach")
            ids = [x.check_id for x in check(f.m.root, offline=True, main=True)]
            self.assertEqual((f.ids(offline=True), ids), ([], ["PC-05"]))

    def test_pc12_suite_missing_from_the_evals_workflow_paths(self) -> None:
        """A plugin with an evals/ suite must be a path that triggers evals.yml."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.write("plugins/demo/evals/case/prompt.md", "---\ntags: [effort-low]\n---\n\nHi.\n")
            f.m.write(".github/workflows/evals.yml", EVALS_WORKFLOW.format(paths=""))
            missing = [str(x) for x in check(f.m.root, offline=True)]
            f.m.write(
                ".github/workflows/evals.yml",
                EVALS_WORKFLOW.format(paths="      - plugins/demo/**\n"),
            )
            expected = "PC-12 .github/workflows/evals.yml: plugins/demo has an eval suite but no"
            self.assertEqual(
                (missing, f.ids(offline=True)), ([f"{expected} `plugins/demo/**` path"], [])
            )

    def test_pc13_secret_read_by_the_wrong_workflow(self) -> None:
        """Each Claude credential secret may be read only by the workflows that own it."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.write(
                ".github/workflows/claude.yml",
                "with:\n  anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}\n",
            )
            f.m.write(
                ".github/workflows/validate.yaml",
                "env:\n  T: ${{ secrets['CLAUDE_CODE_OAUTH_TOKEN'] }}\n",
            )
            found = sorted(str(x) for x in check(f.m.root, offline=True))
        self.assertEqual(
            found,
            [
                PC13.format(
                    path="claude.yml", name="ANTHROPIC_API_KEY", owners="claude-code-review.yml"
                ),
                PC13.format(
                    path="validate.yaml",
                    name="CLAUDE_CODE_OAUTH_TOKEN",
                    owners="claude.yml, evals.yml",
                ),
            ],
        )

    def test_pc13_each_secret_in_its_own_workflow(self) -> None:
        """The owning workflows pass, and a shell guard on the variable is not a read."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.write(
                ".github/workflows/claude-code-review.yml",
                "with:\n  anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}\n",
            )
            f.m.write(
                ".github/workflows/claude.yml",
                "with:\n  claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}\n",
            )
            f.m.write(
                ".github/workflows/evals.yml",
                EVALS_WITH_GUARD,
            )
            self.assertNotIn("PC-13", f.ids(offline=True))

    def test_pc12_reads_only_the_pull_request_paths(self) -> None:
        """A plugin listed under paths-ignore, not paths, doesn't trigger evals.yml."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.write("plugins/demo/evals/case/prompt.md", "---\ntags: [effort-low]\n---\n\nHi.\n")
            ignored = "    paths-ignore:\n      - plugins/demo/**\n"
            f.m.write(".github/workflows/evals.yml", EVALS_WORKFLOW.format(paths=ignored))
            self.assertEqual(f.ids(offline=True), ["PC-12"])

    def test_pc13_matches_secret_names_in_any_case(self) -> None:
        """GitHub reads secret names case-insensitively, so a lowercase read is still a read."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.write(
                ".github/workflows/claude.yml", "with:\n  k: ${{ secrets.anthropic_api_key }}\n"
            )
            found = [str(x) for x in check(f.m.root, offline=True)]
        expected = PC13.format(
            path="claude.yml", name="ANTHROPIC_API_KEY", owners="claude-code-review.yml"
        )
        self.assertEqual(found, [expected])

    def test_pc12_skips_a_repository_without_the_evals_workflow(self) -> None:
        """Without evals.yml there is nothing to keep in step."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.m.write("plugins/demo/evals/case/prompt.md", "---\ntags: [effort-low]\n---\n\nHi.\n")
            self.assertEqual(f.ids(offline=True), [])

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

    def test_main_flag(self) -> None:
        """--main enforces PC-05 on a detached commit; a changelog date is never a finding."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(Path(tmp))
            f.bump("0.2.0", {"0.2.0": "- New.", "0.1.0": "- First."})
            text = changelog("demo", {"0.2.0": "- New.", "0.1.0": "- First."}, unreleased="- P.")
            f.m.write("plugins/demo/CHANGELOG.md", text)
            f.m.commit()
            _ = git(f.m.root, "checkout", "-q", "--detach")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                codes = (
                    cli.main(["--root", str(f.m.root)]),
                    cli.main(["--root", str(f.m.root), "--main"]),
                )
        lines = out.getvalue().splitlines()
        self.assertEqual(codes, (0, 1))
        self.assertEqual([line.split()[0] for line in lines], ["PC-05"])

    def test_date_check_flag_is_gone(self) -> None:
        """--date-check, and PC-11 with it, no longer exist: the flag is a usage error."""
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            _ = cli.main(["--offline", "--date-check"])
        self.assertEqual(raised.exception.code, 2)

    def test_finding_text(self) -> None:
        """A finding prints as `<id> <path>: <message>`."""
        self.assertEqual(str(Finding("PC-01", "a/b", "msg")), "PC-01 a/b: msg")


if __name__ == "__main__":
    _ = unittest.main()
