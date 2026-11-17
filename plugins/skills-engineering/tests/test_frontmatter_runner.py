#!/usr/bin/env python3
"""Tests for frontmatter-checks.py: the entry, the runner and the results lifecycle.

Each test copies the skill's scripts folder into a throwaway folder and registers three demo
checks there, so the runner is exercised as shipped without changing the real registry. TMPDIR
points at a test folder in every run, so the 24-hour sweep never touches the real temp folder.
"""

import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
from typing import override
import unittest

from frontmatter_helpers import SCRIPTS, is_list, parse_object, run_python

PREFIX = "auditing-skills-fm-"
MARKER = ".auditing-skills-results"
PYTHON_311 = Path("/usr/bin/python3.11")

DEMO_OK = """\
from common.report import CheckResult, Finding


def check(ctx):
    text = ctx.skill_md.read_text(encoding="utf-8")
    findings = []
    if "bad" in text:
        findings.append(Finding(
            check="frontmatter.demo-ok", rule="bad-word", line=2, column=7, field="name",
            found="bad", expected="No bad word.", basis="convention", surfaces=("claude-code",),
        ))
    return CheckResult(
        check="frontmatter.demo-ok", status="ran", reason=None, skill=ctx.folder_name,
        findings=findings, data={"chars": len(text)},
    )
"""

DEMO_FAIL = """\
from common.report import CheckResult, Finding


def check(ctx):
    return CheckResult(
        check="frontmatter.demo-fail", status="ran", reason=None, skill=ctx.folder_name,
        findings=[Finding(
            check="frontmatter.demo-fail", rule="always", line=None, column=None, field=None,
            found=None, expected="Never.", basis="inference", surfaces=("upload",),
        )],
        data={},
    )
"""

DEMO_DEP = """\
from common.report import CheckResult


def check(ctx):
    raise AssertionError("a check whose prerequisite failed must never run")
"""

DEMO_REGISTRY = """

from frontmatter import demo_dep, demo_fail, demo_ok

CHECKS = (
    CheckSpec("frontmatter.demo-ok", demo_ok.check, ("comprehension", "scripts")),
    CheckSpec("frontmatter.demo-fail", demo_fail.check, ("scripts",)),
    CheckSpec(
        "frontmatter.demo-dep", demo_dep.check, ("runtime-contract",), ("frontmatter.demo-fail",)
    ),
)
"""


class RunnerTest(unittest.TestCase):
    """The run, show and clean subcommands, and the entry that starts them."""

    def __init__(self, method_name: str = "runTest") -> None:
        """Hold the throwaway folders each test builds; setUp fills them, tearDown removes them."""
        super().__init__(method_name)
        self.tmp: Path = Path()
        self.entry: Path = Path()
        self.temp_root: Path = Path()
        self.skill: Path = Path()
        self.env: dict[str, str] = {}

    @override
    def setUp(self) -> None:
        """Copy the scripts, register the demo checks, and write one skill."""
        self.tmp = Path(tempfile.mkdtemp())
        scripts = self.tmp / "plugin" / "scripts"
        _ = shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
        for name, source in (
            ("demo_ok", DEMO_OK),
            ("demo_fail", DEMO_FAIL),
            ("demo_dep", DEMO_DEP),
        ):
            _ = (scripts / "frontmatter" / f"{name}.py").write_text(source, encoding="utf-8")
        registry = scripts / "common" / "registry.py"
        _ = registry.write_text(
            registry.read_text(encoding="utf-8") + DEMO_REGISTRY, encoding="utf-8"
        )
        self.entry = scripts / "frontmatter-checks.py"
        self.temp_root = self.tmp / "temp-root"
        self.temp_root.mkdir()
        self.skill = self.tmp / "skills" / "demo-skill" / "SKILL.md"
        self.skill.parent.mkdir(parents=True)
        _ = self.skill.write_text("---\nname: bad\n---\nbody\n", encoding="utf-8")
        self.env = {**os.environ, "TMPDIR": str(self.temp_root)}

    @override
    def tearDown(self) -> None:
        """Remove the throwaway folders."""
        shutil.rmtree(self.tmp)

    def entry_run(
        self, *args: str, cwd: Path | None = None, python: str = sys.executable
    ) -> tuple[int, str, str]:
        """Run the entry with these arguments; return its exit code, stdout and stderr."""
        done = run_python([str(self.entry), *args], cwd=cwd, env=self.env, python=python)
        return done.returncode, done.stdout, done.stderr

    def run_all(self) -> tuple[Path, list[str]]:
        """Run every check; return the results folder and the summary lines before it."""
        code, out, err = self.entry_run("run", str(self.skill))
        self.assertEqual(code, 0, err)
        lines = out.splitlines()
        self.assertTrue(lines[-1].startswith("results: "), out)
        return Path(lines[-1].removeprefix("results: ")), lines[:-1]

    def test_run_writes_one_file_per_check(self) -> None:
        """One summary line per check, then the folder holding summary, marker and results."""
        folder, lines = self.run_all()
        self.assertEqual(
            lines,
            [
                "frontmatter.demo-ok ran 1 finding(s) -> comprehension, scripts",
                "frontmatter.demo-fail ran 1 finding(s) -> scripts",
                "frontmatter.demo-dep not_run 0 finding(s) -> runtime-contract",
            ],
        )
        names = sorted(p.name for p in folder.iterdir())
        self.assertEqual(
            names,
            [
                MARKER,
                "frontmatter.demo-dep.json",
                "frontmatter.demo-fail.json",
                "frontmatter.demo-ok.json",
                "summary.json",
            ],
        )
        self.assertEqual(folder.parent, self.temp_root)
        self.assertTrue(folder.name.startswith(PREFIX))
        summary = parse_object((folder / "summary.json").read_text(encoding="utf-8"))
        checks = summary.get("checks")
        self.assertTrue(is_list(checks))

    def test_result_file_matches_the_single_check(self) -> None:
        """Each result file holds exactly what `check <id>` prints for that check."""
        folder, _ = self.run_all()
        for check in ("frontmatter.demo-ok", "frontmatter.demo-fail", "frontmatter.demo-dep"):
            code, out, err = self.entry_run("check", check, str(self.skill))
            self.assertEqual(code, 0, err)
            self.assertEqual((folder / f"{check}.json").read_text(encoding="utf-8"), out)

    def test_two_runs_give_identical_files(self) -> None:
        """Two runs write byte-identical result files to two different folders."""
        first, _ = self.run_all()
        second, _ = self.run_all()
        self.assertNotEqual(first, second)
        for name in ("frontmatter.demo-ok.json", "frontmatter.demo-dep.json", "summary.json"):
            self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())

    def test_failed_prerequisite_gives_not_run(self) -> None:
        """A check whose prerequisite reported a finding doesn't run, and says which one."""
        code, out, err = self.entry_run("check", "frontmatter.demo-dep", str(self.skill))
        self.assertEqual(code, 0, err)
        data = parse_object(out)
        self.assertEqual(
            (data["status"], data["reason"], data["findings"]),
            ("not_run", "frontmatter.demo-fail failed", []),
        )

    def test_show_by_reviewer(self) -> None:
        """Show --reviewer prints exactly the checks whose receivers include that reviewer."""
        folder, _ = self.run_all()
        code, out, err = self.entry_run("show", str(folder), "--reviewer", "scripts")
        self.assertEqual(code, 0, err)
        shown = [parse_object(line)["check"] for line in out.splitlines()]
        self.assertEqual(shown, ["frontmatter.demo-ok", "frontmatter.demo-fail"])
        code, out, _ = self.entry_run("show", str(folder), "--reviewer", "feature-fit")
        self.assertEqual((code, out), (0, ""))

    def test_show_by_check(self) -> None:
        """Show --check prints that check's result line."""
        folder, _ = self.run_all()
        code, out, err = self.entry_run("show", str(folder), "--check", "frontmatter.demo-ok")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, (folder / "frontmatter.demo-ok.json").read_text(encoding="utf-8"))

    def test_show_refuses_unknown_names_and_foreign_folders(self) -> None:
        """An unknown check or reviewer, or a folder the runner didn't create, exits 2."""
        folder, _ = self.run_all()
        for args in (
            ("--check", "frontmatter.nope"),
            ("--reviewer", "nobody"),
        ):
            code, out, _ = self.entry_run("show", str(folder), *args)
            self.assertEqual((code, out), (2, ""))
        foreign = self.temp_root / f"{PREFIX}foreign"
        foreign.mkdir()
        code, out, _ = self.entry_run("show", str(foreign), "--reviewer", "scripts")
        self.assertEqual((code, out), (2, ""))

    def test_clean_removes_its_folder(self) -> None:
        """Clean removes a results folder the runner created."""
        folder, _ = self.run_all()
        code, out, err = self.entry_run("clean", str(folder))
        self.assertEqual((code, out), (0, f"removed {folder}\n"), err)
        self.assertFalse(folder.exists())

    def test_clean_refuses_what_it_did_not_create(self) -> None:
        """/, the home folder, the cwd, a symlink, and a prefixed folder with no marker survive."""
        folder, _ = self.run_all()
        link = self.temp_root / f"{PREFIX}link"
        link.symlink_to(folder, target_is_directory=True)
        unmarked = self.temp_root / f"{PREFIX}unmarked"
        unmarked.mkdir()
        cwd = self.tmp / "cwd"
        cwd.mkdir()
        for target in (Path("/"), Path.home(), cwd, link, unmarked):
            code, out, _ = self.entry_run("clean", str(target), cwd=cwd)
            self.assertEqual((code, out), (2, ""), target)
            self.assertTrue(target.exists(), target)
        self.assertTrue((folder / MARKER).exists())

    def test_clean_refuses_a_marked_folder_outside_the_temp_root(self) -> None:
        """A prefixed, marked folder that isn't directly in a temp folder survives."""
        elsewhere = self.tmp / "elsewhere" / f"{PREFIX}x"
        elsewhere.mkdir(parents=True)
        _ = (elsewhere / MARKER).write_text("", encoding="utf-8")
        code, out, _ = self.entry_run("clean", str(elsewhere))
        self.assertEqual((code, out), (2, ""))
        self.assertTrue(elsewhere.exists())

    def test_sweep_removes_only_old_marked_folders(self) -> None:
        """A run removes marked folders older than 24 hours, and keeps everything else."""
        day_ago = time.time() - 25 * 3600

        def results_folder(name: str, *, marked: bool, parent: Path | None = None) -> Path:
            path = (parent or self.temp_root) / f"{PREFIX}{name}"
            path.mkdir(parents=True)
            if marked:
                _ = (path / MARKER).write_text("", encoding="utf-8")
            os.utime(path, (day_ago, day_ago))
            return path

        old = results_folder("old", marked=True)
        unmarked = results_folder("unmarked", marked=False)
        target = results_folder("target", marked=True, parent=self.tmp / "elsewhere")
        link = self.temp_root / f"{PREFIX}link"
        link.symlink_to(target, target_is_directory=True)
        fresh = results_folder("fresh", marked=True)
        os.utime(fresh)
        _ = self.run_all()
        self.assertFalse(old.exists())
        for kept in (unmarked, target, link, fresh):
            self.assertTrue(kept.exists(), kept)

    def test_unreadable_input_creates_no_folder(self) -> None:
        """Run on a missing file exits 2 and leaves no results folder behind."""
        code, out, _ = self.entry_run("run", str(self.tmp / "missing" / "SKILL.md"))
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(list(self.temp_root.iterdir()), [])

    def test_unknown_check_exits_2(self) -> None:
        """Check with an id no registry entry has exits 2."""
        code, out, err = self.entry_run("check", "frontmatter.nope", str(self.skill))
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1, err)

    def test_any_working_directory_and_isolated_mode(self) -> None:
        """The entry finds its packages from any folder and under -I, and writes no bytecode."""
        elsewhere = self.tmp / "elsewhere-cwd"
        elsewhere.mkdir()
        for flags in ((), ("-I",)):
            done = run_python(
                [*flags, str(self.entry), "check", "frontmatter.demo-ok", str(self.skill)],
                cwd=elsewhere,
                env=self.env,
            )
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(parse_object(done.stdout)["check"], "frontmatter.demo-ok")
        caches = [
            p for p in self.entry.parent.rglob("*") if p.name == "__pycache__" or p.suffix == ".pyc"
        ]
        self.assertEqual(caches, [])

    @unittest.skipUnless(PYTHON_311.exists(), "needs /usr/bin/python3.11")
    def test_python_below_the_floor_exits_2(self) -> None:
        """Python 3.11 gets exit 2 and the floor message, never a SyntaxError."""
        code, out, err = self.entry_run("run", str(self.skill), python=str(PYTHON_311))
        self.assertEqual((code, out), (2, ""))
        self.assertRegex(
            err, r"^frontmatter-checks\.py: needs Python 3\.12 or later; this is 3\.11\.\d+\.\n$"
        )


if __name__ == "__main__":
    _ = unittest.main()
