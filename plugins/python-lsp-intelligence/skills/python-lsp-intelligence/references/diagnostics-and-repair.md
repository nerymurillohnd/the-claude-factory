# Diagnose and repair Python findings

## Classify the evidence

Retain the diagnostic rule, message, source, file, and location. Compare source versions and active policy before deciding whether an LSP/CLI disagreement is stale analysis, environment divergence, scope divergence, or a reproducible tool defect. Do not label a finding false merely because a different check passed.

| Finding | Inspect first | Defensible correction |
|---|---|---|
| `reportMissingImports` / `reportMissingModuleSource` | Interpreter, declaration, import spelling, search paths, optional dependencies | Correct the demonstrated resolution or declaration defect when authorized |
| `reportMissingTypeStubs` | Runtime import availability versus published typing | Use an existing typed API or provide accurate local stubs when authorized |
| `reportReturnType`, `reportAssignmentType`, `reportArgumentType` | Intended contract and all affected paths/callers | Correct the implementation or explicitly justified contract change |
| `reportAny` / `reportUnknown*` | Source of untyped data and its validation | Establish a runtime-validated boundary and precise types |
| Optional-value rules | The branch in which the value can be absent | Narrow with a real check and preserve rejection/fallback semantics |
| Ruff F821 | The actual binding and execution path | Restore the intended definition/import or correct the name |
| Ruff F401 | Exports, side effects, registration, and consumer coverage | Remove only an actually unnecessary import; preserve unresolved evidence |

`ruff rule CODE` explains the rule in the installed Ruff version. A rule disabled by policy is a coverage fact, not proof that the underlying behavior is safe. An intentionally disabled check should be disclosed when it limits the requested verification, not silently enabled or disabled in the user's project.

## Validate untrusted data

Treat decoded JSON or library-returned `Any` as an external boundary. Establish a value of type `object`, validate its container shape and member types, then return the required public type. Reject invalid JSON, a wrong top-level shape, missing members, and wrong member types as the contract requires. Do not coerce values or invent defaults to satisfy an annotation.

A `TypeGuard` or `TypeIs` predicate must prove the type it promises; a declared predicate is not a runtime check by itself. Type-check the validator too. Some checker rules still flag the untyped decoder call or unknown mapping members, so verify the actual implementation under the active policy rather than assuming an annotation solved every diagnostic.

For a simple boundary:

```python
def positive_count(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError("Expected a positive integer")
    return value
```

Test acceptance of a positive integer and rejection of zero, negatives, booleans, strings, and `None`. Booleans are integer subclasses; that distinction changes behavior.

### JSON with a typed external adapter

The standard decoder returns `Any` in its typing interface. Giving the decoder a callable interface returning `object` is accurate: every returned Python value is an object. It does not claim that decoding validated the schema. The subsequent shape and member checks establish the public `str` contract:

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

This shallow dictionary predicate promises only `object` keys/values, not a validated JSON schema. Invalid syntax preserves `JSONDecodeError`; a wrong shape, absent label, or non-string label raises `ValueError`. Empty strings remain valid strings. No coercion, default, cast, or suppression is involved.

The typed boundary control `references/fixtures/typed_json_boundary.py.fixture` was checked with basedpyright 1.40.2, `recommended` mode, and Ruff 0.17.0 under the supplied profile. Acceptance and rejection paths were tested separately. Other policies and contracts still require their own checks; this is a pattern to adapt, not permission to alter public signatures or decoder behavior.

## Environment and configuration

PEP 723 metadata declares requirements; it does not guarantee that an editor selected the corresponding interpreter. A matching-source CLI success under a known script environment can identify a resolution mismatch, but not automatically prove runtime success. Preserve the code unless evidence identifies a source defect. Environment synchronization, installation, dependency changes, and policy changes need an explicit request.

Invalid options, malformed configurations, missing executables, timeouts, and internal errors are unsuccessful or incomplete analysis. Do not repair them by altering unrelated code, adding ignores, broadening to `Any`, or weakening rules. Report the actual boundary and continue independent authorized work when possible.
