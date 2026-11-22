"""Check that the marketplace, manifests, changelogs, READMEs and catalog agree."""

import argparse
import json
from pathlib import Path
import sys

from scripts.checks.plugin_consistency.checks import check
from scripts.release.repo import GitError


class Args(argparse.Namespace):
    """The parsed command line, typed."""

    def __init__(self) -> None:
        """Start from the defaults; argparse sets every attribute it parses."""
        super().__init__()
        self.root: Path = Path()
        self.offline: bool = False
        self.main: bool = False
        self.json: bool = False


def main(argv: list[str] | None = None) -> int:
    """Print one line per finding; exit 1 on any finding or git failure, 2 on usage errors."""
    parser = argparse.ArgumentParser(prog="plugin-consistency", description=__doc__)
    _ = parser.add_argument("--root", type=Path, default=Path(), help="repository root")
    _ = parser.add_argument("--offline", action="store_true", help="skip PC-04 (remote tags)")
    _ = parser.add_argument("--json", action="store_true", help="print the findings as JSON")
    _ = parser.add_argument(
        "--main", action="store_true", help="enforce PC-05 as on main, even on a detached commit"
    )
    args = parser.parse_args(argv, namespace=Args())
    try:
        findings = check(args.root, offline=args.offline, main=args.main)
    except GitError as error:
        _ = sys.stderr.write(f"plugin-consistency: {error}\n")
        return 1
    if args.json:
        data = [{"id": f.check_id, "path": f.path, "message": f.message} for f in findings]
        _ = sys.stdout.write(json.dumps(data, indent=2) + "\n")
    else:
        _ = sys.stdout.write("".join(f"{finding}\n" for finding in findings))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
