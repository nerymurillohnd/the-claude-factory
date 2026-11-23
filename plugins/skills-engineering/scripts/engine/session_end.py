"""The SessionEnd hook's work: remove the ending session's skill-checks results, then sweep.

It reads the hook input JSON from stdin and the plugin's data folder from CLAUDE_PLUGIN_DATA.
Whatever it finds, it prints nothing and exits 0: a SessionEnd hook can't change the session's
end, and Claude Code shows its stderr to the user.
"""

from collections.abc import Callable
import json
import os
from pathlib import Path
import sys

from engine import results


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


parse_json: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def session_id(raw: str) -> str | None:
    """The `session_id` string of the hook input, or None when the input has none."""
    try:
        payload = parse_json(raw)
    except ValueError:
        return None
    value = payload.get("session_id") if isinstance(payload, JsonObject) else None
    return value if isinstance(value, str) else None


def main() -> None:
    """Remove this session's results; exit 0 in every case."""
    data = os.environ.get("CLAUDE_PLUGIN_DATA", "")
    try:
        raw = sys.stdin.read()
    except (OSError, UnicodeDecodeError):
        sys.exit(0)
    session = session_id(raw)
    if data and Path(data).is_absolute() and session is not None:
        results.remove_session(Path(data), session)
    sys.exit(0)


if __name__ == "__main__":
    main()
