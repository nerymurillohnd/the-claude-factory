"""The private work folder: redacted copies of every audited source, which workers read.

Workers never open the originals of in-scope sources (deny rules enforce it), so credentials
in a settings file or an instruction file never reach a model, and every line number in a
finding refers to the same text the run hashed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
import shutil
import tempfile
from typing import TYPE_CHECKING

from aca.redact import redact_lines
from aca.sources import EVIDENCE, IN_SCOPE

if TYPE_CHECKING:
    from aca.inventory import Inventory

UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
WORK_MODE = 0o700


@dataclass
class Snapshot:
    """Where each source's redacted copy lives and what it says."""

    work: Path
    paths: dict[str, Path] = field(default_factory=dict)
    lines: dict[str, list[str]] = field(default_factory=dict)

    def sid_for(self, path: str) -> str:
        """Return the source ID whose snapshot path (or its file name) is path, else ''."""
        target = Path(path)
        for sid, snap in self.paths.items():
            if target in {snap, snap.resolve()} or target.name == snap.name:
                return sid
        return ""


def make_workdir(parent: Path | None = None) -> Path:
    """Create a private temporary folder (mode 0700) for one run."""
    work = Path(
        tempfile.mkdtemp(prefix="agent-context-audit-", dir=str(parent) if parent else None)
    )
    work.chmod(WORK_MODE)
    return work.resolve()


def snapshot_name(sid: str, display: str) -> str:
    """A flat, readable file name for a source's copy."""
    flat = display.replace("~/", "home/").replace("/", "__")
    return f"{sid}-{UNSAFE_CHARS.sub('_', flat)}"


def write(inventory: Inventory, work: Path) -> Snapshot:
    """Write the redacted copy of every audited and evidence source."""
    snap = Snapshot(work=work)
    folder = work / "snap"
    folder.mkdir(mode=WORK_MODE)
    for source in inventory.sources:
        if source.status not in {IN_SCOPE, EVIDENCE}:
            continue
        lines = redact_lines(source.lines)
        path = folder / snapshot_name(source.sid, source.display)
        text = "\n".join(lines) + ("\n" if lines else "")
        _ = path.write_text(text, encoding="utf-8")
        snap.paths[source.sid] = path
        snap.lines[source.sid] = lines
    return snap


def remove(work: Path) -> None:
    """Delete the work folder and everything in it."""
    shutil.rmtree(work, ignore_errors=True)
