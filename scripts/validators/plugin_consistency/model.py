#!/usr/bin/env python3
"""The finding every plugin-consistency check returns."""

from __future__ import annotations

from dataclasses import dataclass
from typing import override


@dataclass(frozen=True)
class Finding:
    """One inconsistency, at a repository path."""

    check_id: str
    path: str
    message: str

    @override
    def __str__(self) -> str:
        """Return the finding as `<id> <path>: <message>`."""
        return f"{self.check_id} {self.path}: {self.message}"
