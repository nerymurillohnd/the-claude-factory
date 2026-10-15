"""A fixture built once per test module, with its inventory, snapshot and deterministic checks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile

import _aca_support
from aca import checks, evidence, inventory, knowledge, paths, snapshot, topics, validate


@dataclass
class Built:
    """The fixture and what the deterministic stages produced for it."""

    temp: tempfile.TemporaryDirectory[str]
    fixture: _aca_support.Fixture
    inventory: inventory.Inventory
    snapshot: snapshot.Snapshot
    result: checks.Checks

    def sid(self, display: str) -> str:
        """The manifest ID of a display path."""
        return next(source.sid for source in self.inventory.sources if source.display == display)

    def display(self, sid: str) -> str:
        """The display path of a manifest ID."""
        source = self.inventory.by_sid(sid)
        return source.display if source else sid

    def checker(self) -> validate.Checker:
        """A validation context over every audited source."""
        allowed = frozenset(source.sid for source in self.inventory.audited)
        defaults = knowledge.load().defaults
        return validate.Checker(self.inventory, self.snapshot, defaults, allowed)


def make() -> Built:
    """Build the fixture in a temporary folder and run inventory, snapshot and checks on it."""
    temp = tempfile.TemporaryDirectory()
    fixture = _aca_support.build(Path(temp.name))
    env = paths.detect_env(_aca_support.environment(fixture))
    repo = paths.repo_root(paths.resolve(fixture.repo))
    found = inventory.build(repo, env, fixture.report_root)
    work = Path(temp.name) / "work"
    work.mkdir()
    snap = snapshot.write(found, work)
    for source in found.sources:
        if source.sid in snap.lines:
            source.lines = snap.lines[source.sid]
    inventory.index_units(found)
    facts = evidence.collect(fixture.repo, found.files)
    taxonomy = topics.load_topics(knowledge.KNOWLEDGE / "topics.json")
    result = checks.run(found, snap, facts, taxonomy)
    return Built(temp=temp, fixture=fixture, inventory=found, snapshot=snap, result=result)
