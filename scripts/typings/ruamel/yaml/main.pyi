from pathlib import Path
from typing import IO

class YAML:
    allow_duplicate_keys: bool
    def __init__(
        self,
        *,
        typ: list[str] | str | None = None,
        pure: bool = False,
        output: object = None,
        plug_ins: list[str] | None = None,
    ) -> None: ...
    def load(self, stream: Path | IO[str] | str) -> object: ...
