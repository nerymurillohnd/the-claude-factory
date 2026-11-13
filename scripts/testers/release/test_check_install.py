#!/usr/bin/env python3
"""Tests for check-install.sh, run against a stub `claude` placed first on PATH."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / "release" / "check-install.sh"

# The stub logs each call with its isolation variables, fails when STUB_FAIL matches the
# arguments, and answers `plugin list --json` with one install per name in STUB_PLUGINS.
STUB = """#!/usr/bin/env bash
set -euo pipefail
printf '%s|%s|%s\\n' "${CLAUDE_CONFIG_DIR:-}" "${CLAUDE_CODE_PLUGIN_CACHE_DIR:-}" "$*" \\
  >>"${STUB_LOG}"
if [[ -n ${STUB_FAIL:-} && "$*" == *"${STUB_FAIL}"* ]]; then exit 3; fi
if [[ "$*" == "plugin list --json" ]]; then
  cat "${STUB_LIST}"
fi
"""


class CheckInstallTest(unittest.TestCase):
    """The order of the commands, their isolation, failures and cleanup."""

    def _run(
        self, tmp: Path, args: list[str], *, fail: str = "", errors: bool = False, mod: bool = False
    ) -> tuple[int, list[str]]:
        """Run the script with the stub and return (exit code, logged calls)."""
        bin_dir, work = tmp / "bin", tmp / "work"
        bin_dir.mkdir()
        work.mkdir()
        stub = bin_dir / "claude"
        _ = stub.write_text(STUB, encoding="utf-8")
        stub.chmod(0o755)
        installs: list[dict[str, object]] = []
        for name in [a for a in args[2:] if not a.startswith("-")]:
            path = tmp / "installs" / name
            (path / "tests").mkdir(parents=True)
            if mod:
                _ = (path / "tests" / "pane.test.tsx").write_text("", encoding="utf-8")
            item: dict[str, object] = {
                "id": f"{name}@the-claude-factory",
                "version": "1.0.0",
                "installPath": str(path),
            }
            if errors:
                item["errors"] = ["boom"]
            installs.append(item)
        listing = tmp / "list.json"
        _ = listing.write_text(json.dumps(installs), encoding="utf-8")
        log = tmp / "log.txt"
        env = {
            **os.environ,
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "STUB_LOG": str(log),
            "STUB_LIST": str(listing),
            "STUB_FAIL": fail,
            "TMPDIR": str(work),
        }
        bash = shutil.which("bash") or "bash"
        done = subprocess.run(
            [bash, str(SCRIPT), *args], env=env, capture_output=True, text=True, check=False
        )
        self.assertEqual(list(work.iterdir()), [], "the temporary folder was left behind")
        calls = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
        return done.returncode, calls

    def test_local_runs_commands_in_order(self) -> None:
        """A local check adds ./, installs, lists, then checks each plugin, all isolated."""
        with tempfile.TemporaryDirectory() as tmp:
            code, calls = self._run(Path(tmp), ["--from", "local", "demo"])
        self.assertEqual(code, 0)
        config, cache, _ = calls[0].split("|")
        self.assertTrue(config.endswith("/config"))
        self.assertTrue(cache.endswith("/cache"))
        self.assertEqual(Path(config).parent, Path(cache).parent)
        commands = [c.split("|")[2] for c in calls]
        self.assertEqual(
            commands[:4],
            [
                "plugin marketplace add ./",
                "plugin install demo@the-claude-factory",
                "plugin list --json",
                "plugin details demo",
            ],
        )
        self.assertTrue(commands[4].startswith("plugin validate --strict "))
        self.assertEqual(len(commands), 5)

    def test_ref_source_string(self) -> None:
        """A ref adds the GitHub marketplace at that ref."""
        with tempfile.TemporaryDirectory() as tmp:
            _, calls = self._run(Path(tmp), ["--from", "main", "demo"])
        self.assertEqual(
            calls[0].split("|")[2], "plugin marketplace add nerymurillohnd/the-claude-factory#main"
        )

    def test_failure_propagates_and_cleans_up(self) -> None:
        """A failing install fails the run, and the temporary folder is still removed."""
        with tempfile.TemporaryDirectory() as tmp:
            code, calls = self._run(Path(tmp), ["--from", "local", "demo"], fail="plugin install")
        self.assertNotEqual(code, 0)
        self.assertEqual(len(calls), 2)

    def test_load_errors_fail(self) -> None:
        """A plugin that lists load errors fails the run."""
        with tempfile.TemporaryDirectory() as tmp:
            code, _ = self._run(Path(tmp), ["--from", "local", "demo"], errors=True)
        self.assertEqual(code, 1)

    def test_runs_plugin_test_only_for_mods(self) -> None:
        """`claude plugin test` runs only when the install has *.test.ts(x) files."""
        with tempfile.TemporaryDirectory() as tmp:
            _, plain = self._run(Path(tmp), ["--from", "local", "demo"])
        with tempfile.TemporaryDirectory() as tmp:
            _, mod = self._run(Path(tmp), ["--from", "local", "demo"], mod=True)
        self.assertFalse(any("|plugin test " in c for c in plain))
        self.assertTrue(mod[-1].split("|")[2].startswith("plugin test "))

    def test_several_plugins_in_order(self) -> None:
        """Plugins install in the order given."""
        with tempfile.TemporaryDirectory() as tmp:
            _, calls = self._run(Path(tmp), ["--from", "main", "one", "two"])
        installs = [c.split("|")[2] for c in calls if "|plugin install " in c]
        self.assertEqual(
            installs,
            ["plugin install one@the-claude-factory", "plugin install two@the-claude-factory"],
        )

    def test_usage_errors_exit_2(self) -> None:
        """No plugin, no --from, or an option where a ref belongs is a usage error."""
        for args in (["--from", "local"], ["demo"], ["--from", "--x", "demo"]):
            with tempfile.TemporaryDirectory() as tmp:
                self.assertEqual(self._run(Path(tmp), args)[0], 2, args)


if __name__ == "__main__":
    _ = unittest.main()
