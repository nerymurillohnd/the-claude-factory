#!/usr/bin/env python3
"""Report every suppression in the given files, or in every file Git tracks.

Exit codes: 0 no suppression, 1 suppressions found (each listed), 2 a file could not be read or
parsed, so it could not be checked.
"""

from pathlib import Path
import shutil
import subprocess
import sys
import tokenize

from validators.find_suppressions.scan import Suppression, scan_file


def tracked_files() -> list[Path]:
    """Every file Git tracks in the current repository."""
    git = shutil.which("git")
    if git is None:
        msg = "git is not installed, so the tracked files can't be listed"
        raise OSError(msg)
    listing = subprocess.run([git, "ls-files", "-z"], capture_output=True, text=True, check=True)
    return [Path(name) for name in listing.stdout.split("\0") if name]


def main(argv: list[str]) -> int:
    """Scan the files named in argv, or every tracked file when argv is empty."""
    paths = [Path(arg) for arg in argv] if argv else tracked_files()
    found: list[Suppression] = []
    failed = False
    for path in paths:
        if not path.is_file():
            continue
        try:
            found.extend(scan_file(path))
        except (OSError, UnicodeDecodeError, SyntaxError, tokenize.TokenError) as error:
            _ = sys.stderr.write(f"{path}: could not be checked: {error}\n")
            failed = True
    for item in found:
        _ = sys.stdout.write(f"{item.path}:{item.line}: {item.kind}: {item.text}\n")
    if found:
        files = len({item.path for item in found})
        noun = "suppression" if len(found) == 1 else "suppressions"
        _ = sys.stdout.write(
            f"{len(found)} {noun} in {files} file(s): fix the cause instead of silencing it.\n"
        )
    if failed:
        return 2
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
