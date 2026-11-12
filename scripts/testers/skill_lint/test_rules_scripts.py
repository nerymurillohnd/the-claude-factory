"""Tests for the script rules (SC)."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from validators.skill_lint.discover import git_modes, load_skill
from validators.skill_lint.model import Severity
from validators.skill_lint.rules_scripts import check, entry_points

from testers.skill_lint.helpers import build_skill, load

EXEC = 0o755
PLAIN = 0o644
RUN_PY = "#!/usr/bin/env python3\nprint('hi')\n"
THREE_FORMS = (
    "python3 scripts/run.py",
    "python3 ${CLAUDE_SKILL_DIR}/scripts/run.py",
    "uv run python ${CLAUDE_PLUGIN_ROOT}/skills/demo-skill/scripts/run.py --x",
)
RUN_MD = "```bash\npython3 scripts/run.py\n```\n"


def _skill_md(body: str = "Hello.\n", extra: str = "") -> str:
    """Return a valid SKILL.md with optional extra frontmatter and a body."""
    head = f"---\nname: demo-skill\ndescription: Demo skill. Use when testing.\n{extra}---\n"
    return head + "\n# Demo\n\n" + body


def _run_block(command: str) -> str:
    """Return a bash fence that runs one command."""
    return f"```bash\n{command}\n```\n"


def _build(root: Path, files: dict[str, str], executable: tuple[str, ...] = ()) -> Path:
    """Build a skill and set the given files executable, the others not."""
    skill = build_skill(root, files)
    for rel in files:
        (skill / rel).chmod(EXEC if rel in executable else PLAIN)
    return skill


def _pairs(files: dict[str, str], executable: tuple[str, ...] = ()) -> list[tuple[str, str]]:
    """Build an untracked skill and return the (rule, path) pairs it reports."""
    with tempfile.TemporaryDirectory() as tmp:
        skill = _build(Path(tmp), files, executable)
        return [(f.rule, f.path) for f in check(load(skill))]


class EntryPointTest(unittest.TestCase):
    """SC-01 and SC-02 apply to entry points only."""

    def test_sc01_entry_without_shebang(self) -> None:
        """A script SKILL.md runs, without a shebang, is SC-01."""
        files = {
            "SKILL.md": _skill_md(_run_block("python3 scripts/run.py")),
            "scripts/run.py": "print('hi')\n",
        }
        pairs = _pairs(files, executable=("scripts/run.py",))
        self.assertEqual(pairs, [("SC-01", "scripts/run.py")])

    def test_sc01_bad_shebang(self) -> None:
        """A shebang that is not /usr/bin/env is SC-01."""
        files = {
            "SKILL.md": _skill_md(_run_block("python3 scripts/run.py")),
            "scripts/run.py": "#!/usr/bin/python3\n",
        }
        pairs = _pairs(files, executable=("scripts/run.py",))
        self.assertEqual(pairs, [("SC-01", "scripts/run.py")])

    def test_sc01_not_for_init_or_imported(self) -> None:
        """__init__.py and an imported module are not entry points."""
        files = {
            "SKILL.md": _skill_md(_run_block("python3 scripts/run.py")),
            "scripts/run.py": "#!/usr/bin/env python3\nimport util\n",
            "scripts/util.py": "VALUE = 1\n",
            "scripts/__init__.py": "",
        }
        with tempfile.TemporaryDirectory() as tmp:
            skill = load(_build(Path(tmp), files, executable=("scripts/run.py",)))
            self.assertEqual(entry_points(skill), {"scripts/run.py"})
            self.assertEqual(check(skill), [])

    def test_sc02_untracked_uses_stat(self) -> None:
        """An untracked entry point without the exec bit is SC-02, read from the file system."""
        files = {
            "SKILL.md": _skill_md(_run_block("python3 scripts/run.py")),
            "scripts/run.py": RUN_PY,
        }
        with tempfile.TemporaryDirectory() as tmp:
            findings = check(load(_build(Path(tmp), files)))
        self.assertEqual([f.rule for f in findings], ["SC-02"])
        self.assertIn("untracked: filesystem mode", findings[0].message)

    def test_sc02_tracked_not_exec(self) -> None:
        """A tracked entry point with git mode 100644 is SC-02, even if executable on disk."""
        files = {
            "SKILL.md": _skill_md(_run_block("python3 scripts/run.py")),
            "scripts/run.py": RUN_PY,
        }
        with tempfile.TemporaryDirectory() as tmp:
            skill = _build(Path(tmp), files, executable=("scripts/run.py",))
            git = shutil.which("git") or "git"
            _ = subprocess.run([git, "init", "-q", tmp], check=True)
            _ = subprocess.run([git, "-C", tmp, "add", "."], check=True)
            _ = subprocess.run(
                [git, "-C", tmp, "update-index", "--chmod=-x", str(skill / "scripts/run.py")],
                check=True,
            )
            findings = check(load_skill(skill / "SKILL.md", mode_reader=git_modes))
        self.assertEqual([f.rule for f in findings], ["SC-02"])
        self.assertIn("100755", findings[0].message)


class InvocationTest(unittest.TestCase):
    """SC-03."""

    def test_sc03_missing_script(self) -> None:
        """A run script that does not exist is SC-03."""
        files = {"SKILL.md": _skill_md(_run_block("python3 ${CLAUDE_SKILL_DIR}/scripts/none.py"))}
        self.assertEqual(_pairs(files), [("SC-03", "SKILL.md")])

    def test_sc03_no_interpreter(self) -> None:
        """A script run without its interpreter is SC-03."""
        files = {
            "SKILL.md": _skill_md(_run_block("${CLAUDE_SKILL_DIR}/scripts/run.py")),
            "scripts/run.py": RUN_PY,
        }
        pairs = _pairs(files, executable=("scripts/run.py",))
        self.assertEqual(pairs, [("SC-03", "SKILL.md")])

    def test_sc03_wrong_interpreter(self) -> None:
        """A Python script run with bash is SC-03."""
        files = {"SKILL.md": _skill_md(_run_block("bash scripts/run.py")), "scripts/run.py": RUN_PY}
        pairs = _pairs(files, executable=("scripts/run.py",))
        self.assertEqual(pairs, [("SC-03", "SKILL.md")])

    def test_sc03_all_three_forms_ok(self) -> None:
        """Relative, ${CLAUDE_SKILL_DIR} and ${CLAUDE_PLUGIN_ROOT} paths are all valid."""
        commands = "\n".join(THREE_FORMS)
        files = {"SKILL.md": _skill_md(_run_block(commands)), "scripts/run.py": RUN_PY}
        self.assertEqual(_pairs(files, executable=("scripts/run.py",)), [])

    def test_sc03_other_variable_ignored(self) -> None:
        """A path under another shell variable is not judged."""
        files = {"SKILL.md": _skill_md(_run_block('python3 "$TMPDIR/x.py"'))}
        self.assertEqual(_pairs(files), [])


class DependencyTest(unittest.TestCase):
    """SC-04, SC-05 and SC-06."""

    def test_sc04_third_party_without_pep723(self) -> None:
        """A non-stdlib import without PEP 723 dependencies is SC-04."""
        files = {
            "SKILL.md": _skill_md("Uses scripts/a.py.\n"),
            "scripts/a.py": "import json\nimport yaml\n",
        }
        self.assertEqual(_pairs(files), [("SC-04", "scripts/a.py")])

    def test_sc04_pep723_ok(self) -> None:
        """A PEP 723 block with dependencies is fine."""
        script = '# /// script\n# dependencies = ["pyyaml"]\n# ///\nimport yaml\n'
        files = {"SKILL.md": _skill_md("Uses scripts/a.py.\n"), "scripts/a.py": script}
        self.assertEqual(_pairs(files), [])

    def test_sc04_empty_dependencies_still_fails(self) -> None:
        """An empty PEP 723 dependencies list does not declare the import."""
        script = "# /// script\n# dependencies = []\n# ///\nimport yaml\n"
        files = {"SKILL.md": _skill_md("Uses scripts/a.py.\n"), "scripts/a.py": script}
        self.assertEqual(_pairs(files), [("SC-04", "scripts/a.py")])

    def test_sc04_stdlib_and_local_ok(self) -> None:
        """Stdlib modules and sibling modules are fine."""
        files = {
            "SKILL.md": _skill_md("Uses scripts/a.py.\n"),
            "scripts/a.py": "import json\nimport util\nfrom util import x\n",
            "scripts/util.py": "x = 1\n",
        }
        self.assertEqual(_pairs(files), [])

    def test_sc05_unmentioned_command(self) -> None:
        """A shell script calling jq, which nothing mentions, is an SC-05 warning."""
        files = {
            "SKILL.md": _skill_md("Uses scripts/a.sh.\n"),
            "scripts/a.sh": "#!/usr/bin/env bash\ncat x | jq .name\n",
        }
        with tempfile.TemporaryDirectory() as tmp:
            skill = _build(Path(tmp), files, executable=("scripts/a.sh",))
            findings = check(load(skill))
        self.assertEqual(
            [(f.rule, f.severity, f.line) for f in findings], [("SC-05", Severity.WARNING, 2)]
        )
        self.assertIn("`jq`", findings[0].message)

    def test_sc05_mentioned_in_compatibility_ok(self) -> None:
        """A command named in compatibility is fine."""
        files = {
            "SKILL.md": _skill_md("Uses scripts/a.sh.\n", extra="compatibility: Requires jq\n"),
            "scripts/a.sh": "#!/usr/bin/env bash\njq .name x\n",
        }
        self.assertEqual(_pairs(files, executable=("scripts/a.sh",)), [])

    def test_sc05_python_subprocess(self) -> None:
        """A program a Python script runs through subprocess is an SC-05 lead."""
        script = "import subprocess\nsubprocess.run(['gh', 'pr', 'list'], check=True)\n"
        files = {"SKILL.md": _skill_md("Uses scripts/a.py.\n"), "scripts/a.py": script}
        self.assertEqual(_pairs(files), [("SC-05", "scripts/a.py")])

    def test_sc05_functions_and_builtins_ok(self) -> None:
        """Functions the script defines, builtins and baseline commands are not reported."""
        script = '#!/usr/bin/env bash\nlog() { echo "$1"; }\nlog hi\ncd /tmp && grep x y\n'
        files = {"SKILL.md": _skill_md("Uses scripts/a.sh.\n"), "scripts/a.sh": script}
        self.assertEqual(_pairs(files, executable=("scripts/a.sh",)), [])

    def test_sc06_global_installs(self) -> None:
        """Pip install with no venv and npm install -g are two SC-06 warnings."""
        script = "#!/usr/bin/env bash\npip install requests\nnpm install -g typescript\n"
        files = {"SKILL.md": _skill_md("Uses scripts/a.sh, pip and npm.\n"), "scripts/a.sh": script}
        pairs = _pairs(files, executable=("scripts/a.sh",))
        self.assertEqual(pairs, [("SC-06", "scripts/a.sh"), ("SC-06", "scripts/a.sh")])

    def test_sc06_pip_in_venv_ok(self) -> None:
        """Pip install in a script that makes a venv is fine."""
        script = "#!/usr/bin/env bash\npython3 -m venv .venv\n.venv/bin/pip install x\n"
        files = {"SKILL.md": _skill_md("Uses scripts/a.sh and python3.\n"), "scripts/a.sh": script}
        self.assertEqual(_pairs(files, executable=("scripts/a.sh",)), [])


if __name__ == "__main__":
    _ = unittest.main()
