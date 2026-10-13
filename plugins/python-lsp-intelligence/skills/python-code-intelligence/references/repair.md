# Python repair decisions

## Imports and environments

Compare the editor's selected interpreter with the one supplying the declared package. A PEP 723 script can run in its declared environment while an editor reports missing imports under another interpreter. Correct the demonstrated resolution/declaration problem; a code edit is not evidence that creating or synchronizing an environment is required.

Distribution and import names can differ, and runtime availability differs from published typing. Inspect the import's actual definition and annotations before changing package names or adding stubs. F401 removal can affect exports, registrations or initialization. Read the diagnostic and those consumers before accepting an import-removal fix.

## JSON boundary — Python 3.10 or later

This example requires `typing.TypeGuard`, added to the standard library in Python 3.10. First read the project's supported Python versions. On older targets, use an already-declared `typing_extensions.TypeGuard` only if that dependency is supported, or choose a compatible validation design. This example does not authorize introducing a dependency or raising the minimum version.

Check API availability against the target runtime as well as type annotations: a checker can accept a typing import that the older runtime cannot import.

The decoder's callable interface returns `object`: it promises no schema. Shape/member checks establish the public `str` return type.

```python
import json
from collections.abc import Callable
from typing import TypeGuard

_decode_json: Callable[[str], object] = json.loads


def _is_dictionary(value: object) -> TypeGuard[dict[object, object]]:
    return isinstance(value, dict)


def read_label(text: str) -> str:
    decoded = _decode_json(text)
    if not _is_dictionary(decoded):
        raise ValueError("Expected a JSON object")
    label = decoded.get("label")
    if not isinstance(label, str):
        raise ValueError("Expected a string label")
    return label
```

The predicate promises only object keys/values, not a typed schema. This use reads the mapping; do not reuse a mutable-container narrowing to write incompatible values through other typed aliases. Invalid syntax retains `JSONDecodeError`; missing/non-string labels and wrong top-level shapes raise `ValueError`. Empty strings remain valid. Check acceptance and those rejection paths under the intended contract and active checker policy.

## Check output and source scope

Use the declared Ruff configuration and checking context. For explicit verification, `ruff check --output-format json`, `ruff format --check`, and `basedpyright --outputjson` give separate evidence. Add `--warnings` only when the declared checking policy treats warnings as failures. Capture statuses before filtering JSON; basedpyright warnings and an excluded Ruff target need inspection even when a surrounding command succeeds.

Reread any automatic fix before constructing the next edit. Check affected callers after changing signatures/exports rather than treating a clean definition file as whole-program evidence. Use the installed `ruff rule CODE` explanation for an unfamiliar rule; output severities/defaults can differ between basedpyright and upstream Pyright.

After a repair, rerun the same checking scope. Finish when the relevant findings clear. If the same finding survives three repair/check attempts, stop and report the diagnostic, attempted repairs and missing decision or evidence; do not mark the work clean.
