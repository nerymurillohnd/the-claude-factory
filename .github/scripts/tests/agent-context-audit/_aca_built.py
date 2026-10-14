"""The known-answer fixture run through the inventory, the snapshot and every deterministic check.

Test modules wrap make() in their own cached function and clean its temporary folder in their
tearDownModule, so no two modules share a folder that one of them deletes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile

import _aca_support
from aca import (
    checks,
    config_checks,
    evidence,
    inventory,
    knowledge,
    paths,
    snapshot,
    topics,
    validate,
)


@dataclass
class Built:
    """The fixture, its inventory and snapshot, and what the deterministic checks found."""

    temp: tempfile.TemporaryDirectory[str]
    fixture: _aca_support.Fixture
    inventory: inventory.Inventory
    snapshot: snapshot.Snapshot
    knowledge: knowledge.Knowledge
    result: checks.Checks

    def sid(self, display: str) -> str:
        """The manifest ID of a display path."""
        for source in self.inventory.sources:
            if source.display == display:
                return source.sid
        message = f"{display} is not in the manifest"
        raise KeyError(message)

    def display(self, sid: str) -> str:
        """The display path of a manifest ID."""
        source = self.inventory.by_sid(sid)
        return source.display if source else sid

    def checker(self) -> validate.Checker:
        """A validation context allowed to report on every source."""
        allowed = frozenset(source.sid for source in self.inventory.sources)
        return validate.Checker(self.inventory, self.snapshot, self.knowledge.defaults, allowed)


def make() -> Built:
    """Build the fixture in a new temporary folder and run the deterministic layer on it."""
    temp = tempfile.TemporaryDirectory()
    fixture = _aca_support.build(Path(temp.name))
    env = paths.detect_env({"HOME": str(fixture.home)})
    found = inventory.build(paths.repo_root(fixture.repo), env, fixture.report_root)
    snap = snapshot.write(found, snapshot.make_workdir(Path(temp.name)))
    facts = evidence.collect(found.repo, found.files)
    taxonomy = topics.load_topics(knowledge.KNOWLEDGE / "topics.json")
    result = checks.run(found, snap, facts, taxonomy)
    bundled = knowledge.load()
    context = checks.Context(found, snap, facts, result)
    config_checks.check_settings(context, bundled)
    config_checks.check_codex_config(context)
    return Built(temp, fixture, found, snap, bundled, result)
