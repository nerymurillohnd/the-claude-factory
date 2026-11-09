#!/usr/bin/env python3
"""Save one report of a skill audit, read from standard input, to the file after --output.

Usage: python3 save-report.py --output <file> <<'END_OF_REPORT'
       <the report, exactly as received>
       END_OF_REPORT

Writes the text unchanged, creating the file's folders, and prints one JSON object,
{"saved", "bytes"}. Saving again to the same file replaces it. Exit 0 when the file is
written, 2 for a usage error (no --output, a folder as --output, nothing on standard input),
1 when the file cannot be written. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

DESCRIPTION = (
    "Save one audit report, read from standard input, unchanged to the file after --output."
)

EPILOG = """example:
  python3 save-report.py --output /tmp/skill-audit-demo/agents/security.md <<'END_OF_REPORT'
  ## security-reviewer: my-skill
  ...
  END_OF_REPORT

exit codes:
  0  the file was written; {"saved": <absolute path>, "bytes": <n>} is printed
  1  the file could not be written
  2  usage error: no --output, a folder as --output, or nothing on standard input
"""


class Args(argparse.Namespace):
    """Typed command-line arguments; argparse overwrites these defaults."""

    output: str = ""


def write_atomically(target: Path, data: bytes) -> None:
    """Write data to target through a temporary file in the same folder."""
    target.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=target.parent, prefix=".report-")
    try:
        with os.fdopen(handle, "wb") as stream:
            _ = stream.write(data)
        _ = Path(temporary).replace(target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def main() -> int:
    """Parse the arguments, read standard input, write the file and print its object."""
    parser = argparse.ArgumentParser(
        prog="save-report.py",
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.add_argument(
        "--output",
        required=True,
        help="the file to write, such as <audit folder>/agents/<agent>.md",
    )
    args = parser.parse_args(namespace=Args())

    target = Path(args.output).resolve()
    if target.is_dir():
        parser.error(f"{target} is a folder; pass the path of the report file")
    if sys.stdin.isatty():
        parser.error("pass the report on standard input, through a quoted here-document")
    data = sys.stdin.buffer.read()
    if not data.strip():
        parser.error("nothing on standard input; pass the report through a quoted here-document")

    try:
        write_atomically(target, data)
    except OSError as error:
        _ = sys.stderr.write(f"save-report.py: cannot write {target}: {error}\n")
        return 1
    _ = sys.stdout.write(json.dumps({"saved": str(target), "bytes": len(data)}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
