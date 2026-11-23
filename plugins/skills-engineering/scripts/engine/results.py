"""The run folders: create them, recognize them, and remove them safely.

A run folder is created by tempfile.mkdtemp with PREFIX and holds MARKER, either in the system
temp folder, in a folder the user named, or in a session folder that holds SESSION_MARKER.
Nothing is removed that isn't a run folder or a session folder by those marks, and a symlink
never counts as either. Where the platform allows it, a run is removed through file descriptors,
so a folder swapped for a symlink between the check and the removal is never followed, and a
folder another user owns is never emptied. The sweep also removes old folders of the earlier
entry, frontmatter-checks.py, named with OLD_PREFIX and OLD_MARKER.
"""

import contextlib
import os
from pathlib import Path
import shutil
import stat
import tempfile
import time

PREFIX = "skills-engineering-checks-"
MARKER = ".skills-engineering-results"
SESSION_MARKER = ".skills-engineering-session"
CHECKS = "checks"
OLD_PREFIX = "auditing-skills-fm-"
OLD_MARKER = ".auditing-skills-results"
MAX_AGE_SECONDS = 24 * 3600

# Removal through file descriptors needs O_NOFOLLOW, O_DIRECTORY and the dir_fd forms of open,
# stat, unlink and rmdir, which Windows lacks; there the path-based removal is used.
FD_REMOVAL = (
    hasattr(os, "O_NOFOLLOW")
    and hasattr(os, "O_DIRECTORY")
    and hasattr(os, "getuid")
    and {os.open, os.stat, os.unlink, os.rmdir} <= os.supports_dir_fd
    and os.scandir in os.supports_fd
    and shutil.rmtree.avoids_symlink_attacks
)


def _owned(path: Path) -> bool:
    """True when the current user owns the entry itself, or the platform has no user ids."""
    return not hasattr(os, "getuid") or path.lstat().st_uid == os.getuid()


def is_results_folder(path: Path, prefix: str = PREFIX, marker_name: str = MARKER) -> bool:
    """True for a real folder named with the prefix, holding the marker as a regular file."""
    marker = path / marker_name
    return (
        path.name.startswith(prefix)
        and not path.is_symlink()
        and path.is_dir()
        and not marker.is_symlink()
        and marker.is_file()
    )


def _is_one_component(name: str) -> bool:
    """A name usable as one folder name: no separator, NUL, `.` or `..`."""
    return (
        bool(name)
        and name not in {".", ".."}
        and not any(c in name for c in "/\\\0")
        and Path(name).name == name
    )


def _is_data_folder(path: Path) -> bool:
    """An existing folder that is not a filesystem root, so it can hold a checks folder."""
    return path != Path(path.anchor) and path.is_dir()


def resolve_out(raw: str | None) -> tuple[Path | None, Path | None]:
    """Where a run goes: (the folder to create it in, the checks root to sweep, or None).

    None for the folder means the system temp folder. The path is cut before its first part that
    still holds an unexpanded `${`. The session layout, with a checks root to sweep, applies only
    to `<P>/checks/<id>`, or to a cut path `<P>/checks`, where P is an existing folder that is not
    a filesystem root; the run then goes in `<P>/checks/<id>` or in `<P>/checks` itself. Any other
    absolute path gets the run folder and nothing else. A relative path, or one that leaves only a
    root, goes to the temp folder, so a run never lands in the working directory.
    """
    if raw is None:
        return None, None
    parts = Path(raw).parts
    cut = next((i for i, part in enumerate(parts) if "${" in part), len(parts))
    kept = Path(*parts[:cut]) if cut else Path()
    if not kept.is_absolute() or kept == Path(kept.anchor):
        return None, None
    if cut < len(parts):
        is_session = kept.name == CHECKS and _is_data_folder(kept.parent)
        return kept, kept if is_session else None
    is_session = (
        _is_one_component(kept.name)
        and kept.parent.name == CHECKS
        and _is_data_folder(kept.parent.parent)
    )
    return kept, kept.parent if is_session else None


def _make_folder(parent: Path | None) -> Path:
    """Create the parent when there is one, then an empty run folder in it."""
    if parent is not None:
        parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    return Path(tempfile.mkdtemp(prefix=PREFIX, dir=parent))


def _refresh_session_marker(parent: Path) -> None:
    """Write SESSION_MARKER, or bring its time to now; a symlink in its place is left alone."""
    marker = parent / SESSION_MARKER
    if not marker.is_symlink():
        marker.touch()


def create(parent: Path | None = None, *, mark_session: bool = False) -> Path:
    """Create a new results folder with its marker; raise OSError when that fails.

    With a parent, the parent is created first. With mark_session, SESSION_MARKER is written or
    refreshed after the run folder exists, so a sweep never takes an active session's folder for
    an old one. A concurrent sweep can remove an empty parent between the two steps, so the pair
    is tried twice.
    """
    try:
        folder = _make_folder(parent)
    except FileNotFoundError:
        folder = _make_folder(parent)
    try:
        _ = (folder / MARKER).write_text("", encoding="utf-8")
    except OSError:
        with contextlib.suppress(OSError):
            folder.rmdir()
        raise
    if parent is not None and mark_session:
        try:
            _refresh_session_marker(parent)
        except OSError:
            remove_run(folder)
            raise
    return folder


def _remove_entries(fd: int, marker_name: str) -> bool:
    """Remove every entry but the marker in the folder open as fd; False when one stays."""
    with os.scandir(fd) as listing:
        entries = [(entry.name, entry.is_dir(follow_symlinks=False)) for entry in listing]
    removed = True
    for name, is_dir in entries:
        if name == marker_name:
            continue
        try:
            if is_dir:
                shutil.rmtree(name, dir_fd=fd)
            else:
                os.unlink(name, dir_fd=fd)
        except OSError:
            removed = False
    return removed


def _remove_run_fd(folder: Path, marker_name: str) -> None:
    """Remove a run through file descriptors: never through a symlink, never another's folder."""
    parent_fd = os.open(folder.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        fd = os.open(folder.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
        try:
            info = os.fstat(fd)
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
                return
            marker = os.stat(marker_name, dir_fd=fd, follow_symlinks=False)
            if not stat.S_ISREG(marker.st_mode) or not _remove_entries(fd, marker_name):
                return
            os.unlink(marker_name, dir_fd=fd)
        finally:
            os.close(fd)
        os.rmdir(folder.name, dir_fd=parent_fd)
    finally:
        os.close(parent_fd)


def _remove_run_path(folder: Path, marker_name: str) -> None:
    """Remove a run by its path, where file-descriptor removal isn't available."""
    if folder.is_symlink():
        return
    failed = False
    for entry in list(folder.iterdir()):
        if entry.name == marker_name:
            continue
        try:
            if entry.is_dir() and not entry.is_symlink():
                shutil.rmtree(entry)
            else:
                entry.unlink()
        except OSError:
            failed = True
    if failed:
        return
    (folder / marker_name).unlink()
    folder.rmdir()


def remove_run(folder: Path, marker_name: str = MARKER) -> None:
    """Remove a run folder, its marker last, and raise nothing.

    When any entry can't be removed, the marker and the folder stay, so the folder is still
    recognized as a run and a later sweep finishes the removal.
    """
    try:
        if FD_REMOVAL:
            _remove_run_fd(folder, marker_name)
        else:
            _remove_run_path(folder, marker_name)
    except OSError:
        return


def _sweep_runs(root: Path, prefix: str, marker_name: str, cutoff: float) -> None:
    """Remove the marked run folders directly in root that are older than the cutoff."""
    try:
        entries = list(root.glob(f"{prefix}*"))
    except OSError:
        return
    for entry in entries:
        try:
            if (
                is_results_folder(entry, prefix, marker_name)
                and _owned(entry)
                and entry.lstat().st_mtime < cutoff
            ):
                remove_run(entry, marker_name)
        except OSError:
            continue


def _is_session_folder(path: Path) -> bool:
    """A real folder, not a symlink, holding SESSION_MARKER as a regular file."""
    marker = path / SESSION_MARKER
    return not path.is_symlink() and path.is_dir() and not marker.is_symlink() and marker.is_file()


def _remove_session_folder(folder: Path) -> None:
    """Remove an empty session folder, marker first; restore the marker when rmdir fails.

    A run created between the emptiness check and rmdir makes rmdir fail; the marker comes back,
    so the folder stays a session folder that the session end and the sweep still clean.
    """
    marker = folder / SESSION_MARKER
    marker.unlink()
    try:
        folder.rmdir()
    except OSError:
        with contextlib.suppress(OSError):
            marker.touch()
        raise


def _sweep_sessions(checks_root: Path, cutoff: float) -> None:
    """Sweep old runs in each session folder, and remove an old session folder left empty."""
    _sweep_runs(checks_root, PREFIX, MARKER, cutoff)
    try:
        children = list(checks_root.iterdir())
    except OSError:
        return
    for child in children:
        try:
            if not _is_session_folder(child):
                continue
            _sweep_runs(child, PREFIX, MARKER, cutoff)
            marker = child / SESSION_MARKER
            others = [e for e in child.iterdir() if e.name != SESSION_MARKER]
            if not others and marker.lstat().st_mtime < cutoff:
                _remove_session_folder(child)
        except OSError:
            continue


def remove_session(data: Path, session_id: str) -> None:
    """At a session's end: remove its run folders and its session folder, then sweep.

    Only a real `checks` folder is touched, only a session folder with its marker is entered,
    and only marked run folders are removed; checks/ itself goes when nothing is left in it.
    """
    checks = data / CHECKS
    if checks.is_symlink() or not checks.is_dir() or not _is_one_component(session_id):
        return
    folder = checks / session_id
    try:
        if _is_session_folder(folder):
            for entry in list(folder.glob(f"{PREFIX}*")):
                if is_results_folder(entry):
                    remove_run(entry)
            if all(e.name == SESSION_MARKER for e in folder.iterdir()):
                _remove_session_folder(folder)
    except OSError:
        pass
    sweep(checks)
    try:
        checks.rmdir()
    except OSError:
        return


def sweep(checks_root: Path | None = None) -> None:
    """Remove results folders older than MAX_AGE_SECONDS.

    The temp folder is always swept, under both prefixes, and only folders the current user owns.
    With a checks root, its own runs and each session folder's runs are swept too, and a session
    folder whose marker is older than the cutoff is removed once nothing else is left in it.
    """
    cutoff = time.time() - MAX_AGE_SECONDS
    root = Path(tempfile.gettempdir())
    for prefix, marker_name in ((PREFIX, MARKER), (OLD_PREFIX, OLD_MARKER)):
        _sweep_runs(root, prefix, marker_name, cutoff)
    if checks_root is not None:
        _sweep_sessions(checks_root, cutoff)
