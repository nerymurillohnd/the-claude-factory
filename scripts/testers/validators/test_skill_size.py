"""scripts/validators/skill-size.py: size limits, the baseline ratchet and loud layout failures.

Each test builds a small repository and a fake `claude` that prints a canned `plugin details`
table, then runs the validator by path with that repository as TCF_ROOT and the fake first on
PATH. No real Claude Code is needed.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from typing import override
import unittest

ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "scripts" / "validators" / "skill-size.py"

DETAILS = """Beta (beta) 0.1.0
  Source: beta@inline

Component inventory
  Skills ({count})  {names}
  Agents (1)  helper
  Hooks (0)

Per-component (rounded)
  component      always-on  on-invoke
{rows}
  helper               ~90       ~1.2k

  On-invoke cost is paid each time a skill or agent fires.
"""


class SkillSizeTests(unittest.TestCase):
    """The validator on small repositories with a fake claude."""

    tmp: Path = Path()

    @override
    def setUp(self) -> None:
        handle = tempfile.TemporaryDirectory()
        self.addCleanup(handle.cleanup)
        self.tmp = Path(handle.name)
        plugin = self.tmp / "plugins" / "beta"
        (plugin / ".claude-plugin").mkdir(parents=True)
        _ = (plugin / ".claude-plugin" / "plugin.json").write_text('{"name": "beta"}')
        (self.tmp / "scripts" / "validators").mkdir(parents=True)
        self.baseline({})

    def skill(self, name: str, lines: int = 10) -> None:
        """A skill folder with a SKILL.md of the given number of lines."""
        folder = self.tmp / "plugins" / "beta" / "skills" / name
        folder.mkdir(parents=True)
        _ = (folder / "SKILL.md").write_text("x\n" * lines)

    def baseline(self, entries: dict[str, int]) -> None:
        """Write the baseline file."""
        path = self.tmp / "scripts" / "validators" / "skill-size-baseline.json"
        _ = path.write_text(json.dumps(entries))

    def fake(self, output: str, code: int = 0) -> Path:
        """A fake claude that prints output and exits with code."""
        folder = self.tmp / "bin"
        folder.mkdir(exist_ok=True)
        script = folder / "claude"
        _ = script.write_text(
            f"#!/bin/sh\ncat <<'END_OF_DETAILS'\n{output}END_OF_DETAILS\nexit {code}\n"
        )
        script.chmod(script.stat().st_mode | stat.S_IXUSR)
        return folder

    def details(self, skills: dict[str, str]) -> Path:
        """A fake claude listing these skills with these on-invoke figures."""
        rows = "\n".join(f"  {name}       ~100      {value}" for name, value in skills.items())
        names = ", ".join(skills)
        return self.fake(DETAILS.format(count=len(skills), names=names, rows=rows))

    def run_with(self, bin_dir: Path | None) -> subprocess.CompletedProcess[str]:
        """Run the validator with TCF_ROOT and an optional fake claude first on PATH."""
        env = dict(os.environ, TCF_ROOT=str(self.tmp))
        if bin_dir is None:
            env["PATH"] = str(Path(sys.executable).parent)
        else:
            env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
        return subprocess.run(
            [sys.executable, str(VALIDATOR)], capture_output=True, text=True, env=env, check=False
        )

    def test_small_skill_passes(self) -> None:
        """A skill within both limits passes."""
        self.skill("alpha")
        result = self.run_with(self.details({"alpha": "~2.1k"}))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("✔ 1 plugin skill(s)", result.stdout)

    def test_over_5000_tokens_fails(self) -> None:
        """~5.1k body tokens is an error for a skill outside the baseline."""
        self.skill("alpha")
        result = self.run_with(self.details({"alpha": "~5.1k"}))
        self.assertEqual(result.returncode, 1)
        self.assertIn("~5100 body tokens", result.stderr)

    def test_exactly_5000_passes_with_warning(self) -> None:
        """~5.0k is within the limit and warns."""
        self.skill("alpha")
        result = self.run_with(self.details({"alpha": "~5.0k"}))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("⚠", result.stdout)

    def test_over_500_lines_fails(self) -> None:
        """501 lines is an error."""
        self.skill("alpha", lines=501)
        result = self.run_with(self.details({"alpha": "~900"}))
        self.assertEqual(result.returncode, 1)
        self.assertIn("501 lines", result.stderr)

    def test_baseline_holds_and_ratchets(self) -> None:
        """A baselined skill passes at its figure, fails above it, and must leave when it fits."""
        self.skill("alpha")
        self.baseline({"beta/alpha": 7000})
        self.assertEqual(self.run_with(self.details({"alpha": "~7.0k"})).returncode, 0)
        grown = self.run_with(self.details({"alpha": "~7.1k"}))
        self.assertEqual(grown.returncode, 1)
        self.assertIn("above its baseline of 7000", grown.stderr)
        fits = self.run_with(self.details({"alpha": "~4.0k"}))
        self.assertEqual(fits.returncode, 1)
        self.assertIn("remove beta/alpha", fits.stderr)

    def test_stale_baseline_entry_fails(self) -> None:
        """A baseline key that names no skill is an error."""
        self.skill("alpha")
        self.baseline({"beta/gone": 6000})
        result = self.run_with(self.details({"alpha": "~1.0k"}))
        self.assertEqual(result.returncode, 1)
        self.assertIn("beta/gone names no plugin skill", result.stderr)

    def test_command_listed_as_skill_is_skipped(self) -> None:
        """Plugin details lists commands/<name>.md as skills; they have no SKILL.md."""
        self.skill("alpha")
        commands = self.tmp / "plugins" / "beta" / "commands"
        commands.mkdir()
        _ = (commands / "init-alpha.md").write_text("x\n")
        result = self.run_with(self.details({"alpha": "~1.0k", "init-alpha": "~600"}))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_changed_layout_stops_loudly(self) -> None:
        """Output without the per-component table exits 2 and names the plugin."""
        self.skill("alpha")
        result = self.run_with(self.fake("Component inventory\n  Skills (1)  alpha\n"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("beta:", result.stderr)
        self.assertIn("on-invoke", result.stderr)

    def test_skill_without_row_stops_loudly(self) -> None:
        """A skill the inventory names but the table lacks exits 2."""
        self.skill("alpha")
        output = DETAILS.format(count=1, names="alpha", rows="  other   ~1   ~2")
        result = self.run_with(self.fake(output))
        self.assertEqual(result.returncode, 2)
        self.assertIn("alpha has 0 rows", result.stderr)

    def test_failed_call_stops_loudly(self) -> None:
        """A plugin details call that exits non-zero exits 2."""
        self.skill("alpha")
        result = self.run_with(self.fake("", code=1))
        self.assertEqual(result.returncode, 2)

    def test_missing_claude_exits_2(self) -> None:
        """Without claude on PATH the check can't run: exit 2."""
        self.skill("alpha")
        result = self.run_with(None)
        self.assertEqual(result.returncode, 2)
        self.assertIn("claude is not on PATH", result.stderr)


if __name__ == "__main__":
    _ = unittest.main()
