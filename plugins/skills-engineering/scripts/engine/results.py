"""The run folders: create them, recognize them, and remove them safely.

A run folder is created by tempfile.mkdtemp with PREFIX and holds MARKER, either in the system
temp folder or in a session folder that holds SESSION_MARKER. Nothing is removed that isn't a run
folder or a session folder by those marks, and a symlink never counts as either. The sweep also
removes old folders of the earlier entry, frontmatter-checks.py, named with OLD_PREFIX and
OLD_MARKER.
"""

from pathlib import Path
import shutil
import tempfile
import time

PREFIX = "skills-engineering-checks-"
MARKER = ".skills-engineering-results"
SESSION_MARKER = ".skills-engineering-session"
OLD_PREFIX = "auditing-skills-fm-"
OLD_MARKER = ".auditing-skills-results"
MAX_AGE_SECONDS = 24 * 3600


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


def resolve_out(raw: str | None) -> tuple[Path | None, Path | None]:
    """Where a run goes: (the folder to create it in, the checks root to sweep).

    None for the folder means the system temp folder. The path is cut before its first part that
    still holds an unexpanded `${`; a cut path is itself the checks root, an uncut one's parent is.
    A relative path, or one that leaves only a root, goes to the temp folder, so a run never lands
    in the working directory.
    """
    if raw is None:
        return None, None
    parts = Path(raw).parts
    cut = next((i for i, part in enumerate(parts) if "${" in part), len(parts))
    kept = Path(*parts[:cut]) if cut else Path()
    if not kept.is_absolute() or kept == Path(kept.anchor):
        return None, None
    return kept, kept if cut < len(parts) else kept.parent


def _make_folder(parent: Path | None, *, mark_session: bool) -> Path:
    """Create the parent and its session marker when asked, then an empty run folder in it."""
    if parent is not None:
        parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if mark_session and not (parent / SESSION_MARKER).is_file():
            _ = (parent / SESSION_MARKER).write_text("", encoding="utf-8")
    return Path(tempfile.mkdtemp(prefix=PREFIX, dir=parent))


def create(parent: Path | None = None, *, mark_session: bool = False) -> Path:
    """Create a new results folder with its marker; raise OSError when that fails.

    With a parent, the parent is created first, and with mark_session it gets SESSION_MARKER, so
    the session cleanup and the sweep recognize it. A concurrent sweep can remove an empty parent
    between the two steps, so the pair is tried twice.
    """
    try:
        folder = _make_folder(parent, mark_session=mark_session)
    except FileNotFoundError:
        folder = _make_folder(parent, mark_session=mark_session)
    try:
        _ = (folder / MARKER).write_text("", encoding="utf-8")
    except OSError:
        shutil.rmtree(folder, ignore_errors=True)
        raise
    return folder


def remove_run(folder: Path, marker_name: str = MARKER) -> None:
    """Remove a run folder, its marker last, and raise nothing.

    When any entry can't be removed, the marker and the folder stay, so the folder is still
    recognized as a run and a later sweep finishes the removal.
    """
    try:
        entries = list(folder.iterdir())
    except OSError:
        return
    failed = False
    for entry in entries:
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
    try:
        (folder / marker_name).unlink()
        folder.rmdir()
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
            if is_results_folder(entry, prefix, marker_name) and entry.lstat().st_mtime < cutoff:
                remove_run(entry, marker_name)
        except OSError:
            continue


def _is_session_folder(path: Path) -> bool:
    """A real folder, not a symlink, holding SESSION_MARKER as a regular file."""
    marker = path / SESSION_MARKER
    return not path.is_symlink() and path.is_dir() and not marker.is_symlink() and marker.is_file()


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
                marker.unlink()
                child.rmdir()
        except OSError:
            continue


def _is_one_component(name: str) -> bool:
    """A session id usable as one folder name: no separator, NUL, `.` or `..`."""
    return (
        bool(name)
        and name not in {".", ".."}
        and not any(c in name for c in "/\\\0")
        and Path(name).name == name
    )


def remove_session(data: Path, session_id: str) -> None:
    """At a session's end: remove its run folders and its session folder, then sweep.

    Only a real `checks` folder is touched, only a session folder with its marker is entered,
    and only marked run folders are removed; checks/ itself goes when nothing is left in it.
    """
    checks = data / "checks"
    if checks.is_symlink() or not checks.is_dir() or not _is_one_component(session_id):
        return
    folder = checks / session_id
    try:
        if _is_session_folder(folder):
            for entry in list(folder.glob(f"{PREFIX}*")):
                if is_results_folder(entry):
                    remove_run(entry)
            if all(e.name == SESSION_MARKER for e in folder.iterdir()):
                (folder / SESSION_MARKER).unlink()
                folder.rmdir()
    except OSError:
        pass
    sweep(checks)
    try:
        checks.rmdir()
    except OSError:
        return


def sweep(checks_root: Path | None = None) -> None:
    """Remove results folders older than MAX_AGE_SECONDS.

    The temp folder is always swept, under both prefixes. With a checks root, its own runs and
    each session folder's runs are swept too, and a session folder whose marker is older than the
    cutoff is removed once nothing else is left in it.
    """
    cutoff = time.time() - MAX_AGE_SECONDS
    root = Path(tempfile.gettempdir())
    for prefix, marker_name in ((PREFIX, MARKER), (OLD_PREFIX, OLD_MARKER)):
        _sweep_runs(root, prefix, marker_name, cutoff)
    if checks_root is not None:
        _sweep_sessions(checks_root, cutoff)
