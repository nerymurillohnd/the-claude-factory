"""Before/after proof that the audit changed nothing: source hashes and git state.

Workers cannot write (no write tool exists for them) and the script writes only the report, so a
changed hash cannot come from the audit; it means the user changed the file while the audit ran.
Such files are reported as "changed during audit" and make the run partial, because their
current text was not the text audited.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from aca import paths
from aca.claude_config import mcp_subset
from aca.jsonutil import dumps
from aca.sources import EVIDENCE, IN_SCOPE, current_digest, digest_bytes

if TYPE_CHECKING:
    from pathlib import Path

    from aca.inventory import Inventory


@dataclass
class GitState:
    """HEAD and working-tree status, as git reports them."""

    available: bool = False
    head: str = ""
    status: str = ""


@dataclass
class Integrity:
    """What changed between the start and the end of the run."""

    changed: list[str] = field(default_factory=list)
    vanished: list[str] = field(default_factory=list)
    git_changed: bool = False
    git_before: GitState = field(default_factory=GitState)
    git_after: GitState = field(default_factory=GitState)

    @property
    def clean(self) -> bool:
        """True when every audited source and the git state are as they were."""
        return not self.changed and not self.vanished and not self.git_changed


def git_state(repo: Path) -> GitState:
    """Read HEAD and the porcelain status without taking optional locks."""
    head = paths.run_git(repo, ["rev-parse", "HEAD"])
    status = paths.run_git(repo, ["status", "--porcelain=v1", "-z", "--untracked-files=all"])
    if head is None and status is None:
        return GitState()
    return GitState(available=True, head=(head or "").strip(), status=status or "")


def _subset_digest(path: Path, repo: Path) -> str:
    """Hash the audited subset of ~/.claude.json exactly as discovery built it."""
    subset = mcp_subset(path, repo)
    return digest_bytes(dumps(subset).encode("utf-8")) if subset else ""


def check(inventory: Inventory, before: GitState) -> Integrity:
    """Hash every audited and evidence source again and compare git state."""
    result = Integrity(git_before=before)
    for source in inventory.sources:
        if source.status not in {IN_SCOPE, EVIDENCE} or not source.sha256:
            continue
        subset = source.subset
        now = _subset_digest(source.path, inventory.repo) if subset else current_digest(source)
        if not now:
            result.vanished.append(source.sid)
        elif now != source.sha256:
            result.changed.append(source.sid)
    result.git_after = git_state(inventory.repo)
    if before.available:
        result.git_changed = (before.head, before.status) != (
            result.git_after.head,
            result.git_after.status,
        )
    return result
