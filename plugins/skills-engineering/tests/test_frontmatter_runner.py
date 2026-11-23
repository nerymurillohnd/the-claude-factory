#!/usr/bin/env python3
"""Tests for skill-checks.py: the entry, the runner and the results lifecycle.

Each test copies the plugin's scripts folder into a throwaway folder and replaces the frontmatter
family's checks there with three demo checks, so the runner is exercised as shipped without
changing the real registry. TMPDIR
points at a test folder in every run, so the 24-hour sweep never touches the real temp folder.
"""

import os
from pathlib import Path
import shlex
import shutil
import sys
import tempfile
import time
from typing import override
import unittest

from frontmatter_helpers import SCRIPTS, parse_object, run_python

sys.path.insert(0, str(SCRIPTS))

from engine.results import remove_run

PREFIX = "skills-engineering-checks-"
MARKER = ".skills-engineering-results"
SESSION_MARKER = ".skills-engineering-session"
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
    """The run and check subcommands, the run folder's lifecycle, and the entry."""

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
        family = scripts / "frontmatter" / "__init__.py"
        _ = family.write_text(family.read_text(encoding="utf-8") + DEMO_REGISTRY, encoding="utf-8")
        self.entry = scripts / "skill-checks.py"
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
        self.assertEqual(
            (folder / "summary.json").read_text(encoding="utf-8"),
            '{"checks":['
            '{"check":"frontmatter.demo-ok","status":"ran","findings":1,'
            '"receivers":["comprehension","scripts"]},'
            '{"check":"frontmatter.demo-fail","status":"ran","findings":1,'
            '"receivers":["scripts"]},'
            '{"check":"frontmatter.demo-dep","status":"not_run","findings":0,'
            '"receivers":["runtime-contract"]}]}\n',
        )

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

    def run_out(self, out: str, cwd: Path | None = None) -> Path:
        """Run every check with --out; return the run folder the summary names."""
        code, out_text, err = self.entry_run("run", "--out", out, str(self.skill), cwd=cwd)
        self.assertEqual(code, 0, err)
        last = out_text.splitlines()[-1]
        self.assertTrue(last.startswith("results: "), out_text)
        return Path(last.removeprefix("results: "))

    def test_run_out_creates_run_folder_inside(self) -> None:
        """--out <dir> puts the marked run folder in <dir>, which gets the session marker."""
        (self.tmp / "data").mkdir()
        session = self.tmp / "data" / "checks" / "session-1"
        folder = self.run_out(str(session))
        self.assertEqual(folder.parent, session)
        self.assertTrue((folder / MARKER).is_file())
        self.assertTrue((session / SESSION_MARKER).is_file())

    def test_run_out_hand_written_folder_is_no_session(self) -> None:
        """--out <dir> not shaped <data>/checks/<id> gets the run, no session marker, no sweep."""
        out = self.tmp / "audit-results"
        old_neighbour = self.tmp / f"{PREFIX}neighbour"
        old_neighbour.mkdir()
        _ = (old_neighbour / MARKER).write_text("", encoding="utf-8")
        day_ago = time.time() - 25 * 3600
        os.utime(old_neighbour, (day_ago, day_ago))
        folder = self.run_out(str(out))
        self.assertEqual(folder.parent, out)
        self.assertFalse((out / SESSION_MARKER).exists())
        self.assertTrue(old_neighbour.exists())

    def test_run_out_under_a_file_exits_2(self) -> None:
        """--out below a regular file exits 2 with one line naming the path, and no run folder."""
        blocker = self.tmp / "blocker"
        _ = blocker.write_text("", encoding="utf-8")
        code, out, err = self.entry_run("run", "--out", str(blocker / "sub"), str(self.skill))
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertTrue(err.startswith("skill-checks.py: can't create the results folder"), err)
        self.assertIn(str(blocker), err)
        self.assertEqual(list(self.temp_root.iterdir()), [])

    def replace_demo_ok(self, body: str) -> None:
        """Make the demo-ok check run this body instead of its own."""
        source = f"from common.report import CheckResult\n\n\ndef check(ctx):\n{body}"
        _ = (self.entry.parent / "frontmatter" / "demo_ok.py").write_text(source, encoding="utf-8")

    def test_read_failure_in_run_is_a_read_error(self) -> None:
        """A check that fails reading SKILL.md exits 2 with `can't read <path>`, no run folder."""
        self.replace_demo_ok(
            "    import errno\n"
            "    raise OSError(errno.EIO, 'Input/output error', str(ctx.skill_md))\n"
        )
        code, out, err = self.entry_run("run", str(self.skill))
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(err, f"skill-checks.py: can't read {self.skill}: Input/output error\n")
        self.assertEqual(list(self.temp_root.iterdir()), [])

    def test_read_failure_in_check_is_a_read_error(self) -> None:
        """`check <id>` reports a read failure on one stderr line with exit 2, no traceback."""
        self.replace_demo_ok(
            "    import errno\n"
            "    raise OSError(errno.EIO, 'Input/output error', str(ctx.skill_md))\n"
        )
        code, out, err = self.entry_run("check", "frontmatter.demo-ok", str(self.skill))
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(err, f"frontmatter.demo-ok: can't read {self.skill}: Input/output error\n")

    def test_check_that_raises_leaves_no_run_folder(self) -> None:
        """A check that raises leaves no run folder behind."""
        self.replace_demo_ok("    raise RuntimeError('boom')\n")
        code, out, _ = self.entry_run("run", str(self.skill))
        self.assertEqual((code, out), (1, ""))
        self.assertEqual(list(self.temp_root.iterdir()), [])

    def test_not_a_regular_file_exits_2(self) -> None:
        """A SKILL.md path that is a device, as /dev/null, exits 2 as not a regular file."""
        for command in (("run", "/dev/null"), ("check", "frontmatter.demo-ok", "/dev/null")):
            with self.subTest(command=command[0]):
                code, out, err = self.entry_run(*command)
                self.assertEqual((code, out), (2, ""))
                self.assertEqual(len(err.splitlines()), 1, err)
                self.assertIn("not a regular file: /dev/null", err)

    def test_run_out_literal_session_through_shell(self) -> None:
        """A literal ${CLAUDE_SESSION_ID} in single quotes reaches the script; the run goes up."""
        checks = self.tmp / "data" / "checks"
        (self.tmp / "data").mkdir()
        env = {
            k: v
            for k, v in self.env.items()
            if k not in {"CLAUDE_SESSION_ID", "CLAUDE_PLUGIN_DATA"}
        }
        command = (
            f"{shlex.quote(sys.executable)} {shlex.quote(str(self.entry))} run "
            f"--out '{checks}/${{CLAUDE_SESSION_ID}}' {shlex.quote(str(self.skill))}"
        )
        done = run_python(["-c", command], env=env, python="bash")
        self.assertEqual(done.returncode, 0, done.stderr)
        folder = Path(done.stdout.splitlines()[-1].removeprefix("results: "))
        self.assertEqual(folder.parent, checks)
        self.assertFalse((checks / SESSION_MARKER).exists())

    def test_run_out_literal_root_uses_temp(self) -> None:
        """An --out that starts with an unexpanded variable falls back to the temp folder."""
        folder = self.run_out("${CLAUDE_PLUGIN_DATA}/checks/${CLAUDE_SESSION_ID}")
        self.assertEqual(folder.parent, self.temp_root)

    def test_run_out_relative_uses_temp(self) -> None:
        """A relative --out never writes into the working directory."""
        project = self.tmp / "project"
        project.mkdir()
        folder = self.run_out("results", cwd=project)
        self.assertEqual(folder.parent, self.temp_root)
        self.assertEqual(list(project.iterdir()), [])

    def test_show_and_clean_are_gone(self) -> None:
        """The removed subcommands exit 2 as unknown choices and leave the run folder alone."""
        folder, _ = self.run_all()
        for args in (("show", str(folder), "--reviewer", "scripts"), ("clean", str(folder))):
            with self.subTest(command=args[0]):
                code, out, err = self.entry_run(*args)
                self.assertEqual((code, out), (2, ""), err)
                self.assertIn("invalid choice", err)
        self.assertTrue((folder / MARKER).is_file())

    def test_failed_prerequisite_gives_not_run(self) -> None:
        """A check whose prerequisite reported a finding doesn't run, and says which one."""
        code, out, err = self.entry_run("check", "frontmatter.demo-dep", str(self.skill))
        self.assertEqual(code, 0, err)
        data = parse_object(out)
        self.assertEqual(
            (data["status"], data["reason"], data["findings"]),
            ("not_run", "frontmatter.demo-fail failed", []),
        )

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

    def test_sweep_checks_root(self) -> None:
        """A run with --out sweeps old runs in the checks root and in its marked session folders."""
        day_ago = time.time() - 25 * 3600
        checks = self.tmp / "data" / "checks"

        def run_folder(parent: Path, name: str, *, marked: bool = True, old: bool = True) -> Path:
            path = parent / f"{PREFIX}{name}"
            path.mkdir(parents=True)
            if marked:
                _ = (path / MARKER).write_text("", encoding="utf-8")
            if old:
                os.utime(path, (day_ago, day_ago))
            return path

        def session(parent: Path, name: str, *, old: bool = True) -> Path:
            path = parent / name
            path.mkdir(parents=True)
            marker = path / SESSION_MARKER
            _ = marker.write_text("", encoding="utf-8")
            if old:
                os.utime(marker, (day_ago, day_ago))
            return path

        direct = run_folder(checks, "direct")
        ended = session(checks, "ended")
        ended_run = run_folder(ended, "run")
        live = session(checks, "live", old=False)
        live_run = run_folder(live, "run", old=False)
        plain = checks / "plain"
        plain.mkdir()
        os.utime(plain, (day_ago, day_ago))
        unmarked = run_folder(checks, "unmarked", marked=False)
        elsewhere = session(self.tmp / "elsewhere", "target")
        elsewhere_run = run_folder(elsewhere, "run")
        (checks / "link").symlink_to(elsewhere, target_is_directory=True)
        _ = self.run_out(str(checks / "new"))
        for gone in (direct, ended_run, ended):
            self.assertFalse(gone.exists(), gone)
        for kept in (live_run, plain, unmarked, elsewhere_run):
            self.assertTrue(kept.exists(), kept)

    @unittest.skipIf(os.geteuid() == 0, "root can delete inside a read-only folder")
    def test_remove_run_deletes_marker_last(self) -> None:
        """When part of a run can't be deleted, the rest goes and the marker stays."""
        folder = self.temp_root / f"{PREFIX}partial"
        locked = folder / "locked"
        locked.mkdir(parents=True)
        _ = (locked / "held.json").write_text("{}", encoding="utf-8")
        _ = (folder / "summary.json").write_text("{}", encoding="utf-8")
        _ = (folder / MARKER).write_text("", encoding="utf-8")
        locked.chmod(0o500)
        try:
            remove_run(folder)
        finally:
            locked.chmod(0o700)
        self.assertFalse((folder / "summary.json").exists())
        self.assertTrue((folder / MARKER).is_file())

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
            err, r"^skill-checks\.py: needs Python 3\.12 or later; this is 3\.11\.\d+\.\n$"
        )


if __name__ == "__main__":
    _ = unittest.main()
