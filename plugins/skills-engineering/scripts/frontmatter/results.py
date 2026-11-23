"""The per-run results folder: create it, recognize it, sweep old ones and remove it safely.

A results folder is created by tempfile.mkdtemp with PREFIX, directly in a temp folder, and holds
MARKER. Nothing is read from or removed outside a folder that meets all three conditions, and a
symlink never counts as one.
"""

import os
from pathlib import Path
import shutil
import tempfile
import time

PREFIX = "auditing-skills-fm-"
MARKER = ".auditing-skills-results"
MAX_AGE_SECONDS = 24 * 3600


def temp_roots() -> set[Path]:
    """The temp folders a results folder may sit in: TMPDIR, TEMP and TMP, and tempfile's own.

    Every variable tempfile reads counts, not only the folder it picks in this process, so a
    folder created while TMPDIR was set is still recognized after another variable takes over.
    """
    candidates = [os.environ.get(name, "") for name in ("TMPDIR", "TEMP", "TMP")]
    candidates.append(tempfile.gettempdir())
    return {Path(c).resolve() for c in candidates if c}


def is_results_folder(path: Path) -> bool:
    """True for a real folder named with PREFIX, holding MARKER as a regular file."""
    marker = path / MARKER
    return (
        path.name.startswith(PREFIX)
        and not path.is_symlink()
        and path.is_dir()
        and not marker.is_symlink()
        and marker.is_file()
    )


def is_removable(path: Path) -> bool:
    """A results folder that sits directly in one of the temp folders."""
    return is_results_folder(path) and path.parent.resolve() in temp_roots()


def create() -> Path:
    """Create a new results folder with its marker; raise OSError when that fails."""
    folder = Path(tempfile.mkdtemp(prefix=PREFIX))
    try:
        _ = (folder / MARKER).write_text("", encoding="utf-8")
    except OSError:
        shutil.rmtree(folder, ignore_errors=True)
        raise
    return folder


def sweep() -> None:
    """Remove results folders in the temp folder that are older than MAX_AGE_SECONDS."""
    root = Path(tempfile.gettempdir())
    cutoff = time.time() - MAX_AGE_SECONDS
    try:
        entries = list(root.glob(f"{PREFIX}*"))
    except OSError:
        return
    for entry in entries:
        try:
            if is_results_folder(entry) and entry.lstat().st_mtime < cutoff:
                shutil.rmtree(entry)
        except OSError:
            continue
