"""Run options and the state one audit accumulates across its stages.

The stages run as separate processes between the two workflows, so everything a later stage
needs is written to `state.json` in the run folder by `store` and read back from it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from aca.history import Change
from aca.integrity import GitState
from aca.reconcile import Outcome

if TYPE_CHECKING:
    from pathlib import Path

    from aca.checks import Checks
    from aca.coverage import Ledger
    from aca.findings import ExternalClaim, Finding
    from aca.integrity import Integrity
    from aca.inventory import Inventory
    from aca.jsonutil import JsonObj
    from aca.knowledge import Knowledge
    from aca.paths import Env
    from aca.plan import Package
    from aca.snapshot import Snapshot
    from aca.validate import Rejected

COMPLETE = "complete"
WITH_FINDINGS = "complete-with-findings"
PARTIAL = "partial"
FAILURE = "failure"
EXIT_CODES = {COMPLETE: 0, WITH_FINDINGS: 1, PARTIAL: 2, FAILURE: 3}
EXIT_USAGE = 4
STAGES = ("prepared", "domains-accepted", "review-accepted", "finalized")


@dataclass
class Options:
    """Everything the user can choose for a run."""

    repo: str = "."
    out: str | None = None
    challenge_rounds: int = 1
    offline: bool = False
    keep_work: bool = False


@dataclass
class DomainRun:
    """One package's auditor: how it went and what it proved."""

    package: Package
    status: str = "pending"
    attempts: int = 0
    error: str = ""
    agent_id: str = ""
    ledgers: dict[str, Ledger] = field(default_factory=dict)
    gaps: dict[str, str] = field(default_factory=dict)


@dataclass
class RunState:
    """Everything one audit of one repository produced."""

    options: Options
    env: Env
    repo: Path
    report_root: Path
    run_id: str
    run_dir: Path
    started: str
    stage: str = ""
    claude_version: str = ""
    finished: str = ""
    seconds: float = 0.0
    work: Path | None = None
    inventory: Inventory | None = None
    snapshot: Snapshot | None = None
    knowledge: Knowledge | None = None
    evidence: JsonObj = field(default_factory=dict)
    checks: Checks | None = None
    git_before: GitState = field(default_factory=GitState)
    domains: list[DomainRun] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    claims: list[ExternalClaim] = field(default_factory=list)
    rejected: list[Rejected] = field(default_factory=list)
    verdicts: dict[str, tuple[str, str]] = field(default_factory=dict)
    outcome: Outcome = field(default_factory=Outcome)
    reconciliation: str = "not run"
    verification: str = "not run"
    independent: str = "not run"
    coordinator: str = "not run"
    integrity: Integrity | None = None
    change: Change = field(default_factory=Change)
    usage: list[JsonObj] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    writes: list[str] = field(default_factory=list)
    status: str = ""
    exit_code: int = 0

    def work_tasks(self) -> Path:
        """The folder of the task files the workflow agents read."""
        if self.work is None:
            message = "the run has no work folder: run prepare first"
            raise RuntimeError(message)
        return self.work / "tasks"

    def settle(self) -> None:
        """Decide the run status and exit code from what happened."""
        reported = [item for item in self.findings if item.status in {"final", "open"}]
        if self.failures:
            self.status = FAILURE
        elif self.problems:
            self.status = PARTIAL
        elif reported:
            self.status = WITH_FINDINGS
        else:
            self.status = COMPLETE
        self.exit_code = EXIT_CODES[self.status]
