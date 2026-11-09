#!/usr/bin/env python3
"""Record the verdict of a skill audit, so that the skill-diagnostics Stop hook clears the skill.

Usage: python3 record-verdict.py --data-dir <dir> <skill-dir> <verdict>

Writes <dir>/verdicts/<skill key> as one JSON object, {"skill", "verdict", "recorded_at"}, and
prints the same object. The skill key is the absolute skill folder with backslashes turned into
slashes, then % as %25, / as %2F and : as %3A. Exit 0 when the verdict is written, 2 for a usage
error, 1 when the file cannot be written. Standard library only.
"""

from __future__ import annotations

import argparse
import contextlib
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import tempfile

VERDICTS = ("pass", "pass-with-warnings", "fail", "not-determinable")
DESCRIPTION = " ".join(
    (
        "Record the verdict of a skill audit, so that the skill-diagnostics gate clears the skill.",
        f"Accepted verdicts: {', '.join(VERDICTS)}.",
    )
)


class Args(argparse.Namespace):
    """Typed command-line arguments; argparse overwrites these defaults."""

    data_dir: str = ""
    skill_dir: str = ""
    verdict: str = ""


def working_directory() -> Path:
    """Return the current folder as the shell names it (PWD) when it is the same folder."""
    current = Path.cwd()
    logical = Path(os.environ.get("PWD", "") or current)
    with contextlib.suppress(OSError):
        if logical.is_absolute() and logical.samefile(current):
            return logical
    return current


def absolute(raw: str) -> str:
    """Return the path absolute and normalized, with / as the separator."""
    path = Path(raw.replace("\\", "/"))
    if not path.is_absolute():
        path = working_directory() / path
    return os.path.normpath(path).replace("\\", "/")


def skill_key(skill: str) -> str:
    """Return the verdict file name for an absolute skill folder; the gate builds the same."""
    return skill.replace("\\", "/").replace("%", "%25").replace("/", "%2F").replace(":", "%3A")


def write_atomically(target: Path, text: str) -> None:
    """Write text to target through a temporary file in the same folder."""
    target.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=target.parent, prefix=".verdict-")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            _ = stream.write(text)
        _ = Path(temporary).replace(target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


EPILOG = """example:
  python3 record-verdict.py --data-dir /path/to/plugin-data ./my-skill pass

exit codes:
  0  the verdict file was written; its JSON object is printed
  1  the verdict file could not be written
  2  usage error, such as a folder without SKILL.md or an unknown verdict
"""


def main() -> int:
    """Parse the arguments, write the verdict file and print its object."""
    parser = argparse.ArgumentParser(
        prog="record-verdict.py",
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.add_argument(
        "--data-dir",
        required=True,
        help="the plugin's data folder (${CLAUDE_PLUGIN_DATA})",
    )
    _ = parser.add_argument("skill_dir", metavar="skill-dir", help="the audited skill folder")
    _ = parser.add_argument("verdict", choices=VERDICTS, help="the audit's verdict")
    args = parser.parse_args(namespace=Args())

    skill = absolute(args.skill_dir)
    if not Path(skill, "SKILL.md").is_file():
        parser.error(f"{skill} holds no SKILL.md; pass the folder of the audited skill")

    record = {
        "skill": skill,
        "verdict": args.verdict,
        "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    text = json.dumps(record)
    target = Path(absolute(args.data_dir), "verdicts", skill_key(skill))
    try:
        write_atomically(target, text + "\n")
    except OSError as error:
        _ = sys.stderr.write(f"record-verdict.py: cannot write {target}: {error}\n")
        return 1
    _ = sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
