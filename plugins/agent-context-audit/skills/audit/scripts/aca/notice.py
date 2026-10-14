"""The SessionStart notice: announce a new report once, then remember that it was shown.

The plugin's SessionStart hook runs `agent_context_audit.py session-notice`. It finds the
project's report folder the way a run does (the in-repo default, or AGENT_CONTEXT_AUDIT_REPORT_DIR
when the session has that variable), prints the hook output stored in notice.json when its run
differs from the last one shown, and records that run in .notified. It never fails the session:
a missing or unreadable notice means no output.
"""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import TYPE_CHECKING

from aca import paths
from aca.jsonutil import as_obj, dumps, get_obj, get_str, loads, read_json, write_atomic

if TYPE_CHECKING:
    from collections.abc import Mapping

OPTION_ENV = "CLAUDE_PLUGIN_OPTION_SESSION_NOTICE"
OFF_VALUES = frozenset({"false", "0", "no", "off"})
NOTICE = "notice.json"
SHOWN = ".notified"


def enabled(environ: Mapping[str, str]) -> bool:
    """False when the user turned the session_notice option off."""
    return environ.get(OPTION_ENV, "").strip().lower() not in OFF_VALUES


def project_dir(event_text: str, environ: Mapping[str, str]) -> Path:
    """The session's project: CLAUDE_PROJECT_DIR, else the event's cwd, else this process's."""
    chosen = environ.get("CLAUDE_PROJECT_DIR", "")
    if not chosen and event_text.strip():
        try:
            chosen = get_str(as_obj(loads(event_text)), "cwd")
        except ValueError:
            chosen = ""
    return Path(chosen).expanduser() if chosen else Path.cwd()


def mark_shown(root: Path, run_id: str) -> None:
    """Record that this run's notice reached a session (raises OSError)."""
    write_atomic(root / SHOWN, run_id + "\n")


def pending(root: Path) -> str:
    """The hook output to print for the report folder root, or '' when nothing is new."""
    try:
        notice = as_obj(read_json(root / NOTICE))
    except (OSError, ValueError):
        return ""
    run_id = get_str(notice, "run_id")
    output = get_obj(notice, "output")
    if not run_id or not output:
        return ""
    try:
        shown = (root / SHOWN).read_text(encoding="utf-8").strip()
    except OSError:
        shown = ""
    if shown == run_id:
        return ""
    with contextlib.suppress(OSError):
        mark_shown(root, run_id)
    return dumps(output)


def run(event_text: str, environ: Mapping[str, str]) -> str:
    """What the hook prints: the pending notice of the session's project, or ''."""
    if not enabled(environ):
        return ""
    repo = paths.repo_root(paths.resolve(project_dir(event_text, environ)))
    return pending(paths.report_root(repo, environ, None))
