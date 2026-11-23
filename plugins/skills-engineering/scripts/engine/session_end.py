"""The SessionEnd hook's work: remove the ending session's skill-checks results, then sweep.

It reads the hook input JSON from stdin and the plugin's data folder from CLAUDE_PLUGIN_DATA.
A session that ends with reason `resume`, as `/resume` and `/branch` end it, keeps its results:
the conversation goes on, and the 24-hour sweep removes them once they are old. Whatever it
finds, it prints nothing and exits 0: a SessionEnd hook can't change the session's end, and
Claude Code shows its stderr to the user. An unexpected error goes to one line of
`session-end.log` in the data folder instead, a file kept under LOG_LIMIT bytes.
"""

from collections.abc import Callable, Generator
import contextlib
import json
import logging
import os
from pathlib import Path
import sys
from typing import TextIO, override

from engine import results

LOGGER_NAME = "skills-engineering.session-end"
LOG_NAME = "session-end.log"
LOG_LIMIT = 64 * 1024
KEEP_REASONS = frozenset({"resume"})


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


parse_json: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def _field(raw: str, name: str) -> str | None:
    """One string field of the hook input, or None when the input has no such string."""
    try:
        payload = parse_json(raw)
    except ValueError:
        return None
    value = payload.get(name) if isinstance(payload, JsonObject) else None
    return value if isinstance(value, str) else None


def session_id(raw: str) -> str | None:
    """The `session_id` string of the hook input, or None when the input has none."""
    return _field(raw, "session_id")


def _data_folder() -> Path | None:
    """The plugin's data folder from CLAUDE_PLUGIN_DATA, or None when unset or relative."""
    data = os.environ.get("CLAUDE_PLUGIN_DATA", "")
    return Path(data) if data and Path(data).is_absolute() else None


class _OneLine(logging.Formatter):
    """`<message>: <error type>: <error text on one line>`, with no traceback."""

    @override
    def format(self, record: logging.LogRecord) -> str:
        """Render the record and its exception on one line."""
        error = record.exc_info[1] if record.exc_info is not None else None
        kind = type(error).__name__ if error is not None else "Error"
        text = " ".join(str(error).split()) if error is not None else ""
        return f"{record.getMessage()}: {kind}: {text}"


@contextlib.contextmanager
def _error_log() -> Generator[logging.Logger]:
    """A logger that appends to the data folder's log, started over past LOG_LIMIT bytes.

    It writes nowhere when the data folder is unset or relative or the log can't be opened, and
    never to stderr.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.propagate = False
    data = _data_folder()
    stream: TextIO | None = None
    if data is not None:
        log = data / LOG_NAME
        with contextlib.suppress(OSError):
            too_big = log.is_file() and log.stat().st_size > LOG_LIMIT
            stream = log.open("w" if too_big else "a", encoding="utf-8")
    handler: logging.Handler = (
        logging.NullHandler() if stream is None else logging.StreamHandler(stream)
    )
    handler.setFormatter(_OneLine())
    logger.addHandler(handler)
    try:
        yield logger
    finally:
        logger.removeHandler(handler)
        if stream is not None:
            with contextlib.suppress(OSError):
                stream.close()


def _end(raw: str) -> None:
    """Remove this session's results unless the session goes on after a resume."""
    session = session_id(raw)
    data = _data_folder()
    if data is None or session is None or _field(raw, "reason") in KEEP_REASONS:
        return
    results.remove_session(data, session)


def main() -> None:
    """Remove this session's results; exit 0 in every case, logging any unexpected error."""
    try:
        raw = sys.stdin.read()
    except (OSError, UnicodeDecodeError):
        sys.exit(0)
    try:
        _end(raw)
    except Exception:
        with _error_log() as logger:
            logger.exception("session %s", session_id(raw) or "-")
    sys.exit(0)


if __name__ == "__main__":
    main()
