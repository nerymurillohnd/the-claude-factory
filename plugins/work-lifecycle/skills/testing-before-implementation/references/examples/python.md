# Example: a bug fix in Python, with a pre-existing failure

Judgment to copy: the baseline runs first, so a failure that was already there is reported, not fixed or blamed on the change; the test names its break and fails for that reason before the fix. Don't copy the language, names or numbers.

<example>
<request>
Discounts over 100% make `apply_discount` return a negative price. Fix it so the price never goes below zero.
</request>

<result>
Phase 1. The project runs `uv run pytest`, `uv run ruff check .` and `uv run mypy src` in CI (`.github/workflows/ci.yml`). Tests live in `tests/test_pricing.py` and use plain `assert` with `Decimal` values.

Baseline:
- `uv run pytest -q` → `41 passed, 1 failed`; the failure is `tests/test_tax.py::test_vat_rounding_eu`, unrelated to pricing.
- `uv run ruff check .` → `All checks passed!`
- `uv run mypy src` → `Success: no issues found in 12 source files`

Phase 2. Behavior in testable code: the test-first cycle, at unit level, because `apply_discount` is a pure function.

Phase 3. Break: the test fails if `apply_discount` stops clamping at zero. That is a bug, not a decision: the requirement says the price never goes below zero. Expected value by hand: a 150% discount on 20.00 gives 0.00.

Phase 4, red. Test added to `tests/test_pricing.py`:

```python
def test_discount_over_full_price_clamps_to_zero():
    assert apply_discount(Decimal("20.00"), percent=150) == Decimal("0.00")
```

`uv run pytest tests/test_pricing.py -q -k clamps` → `AssertionError: assert Decimal('-10.00') == Decimal('0.00')`. It fails, not errors, and shows the negative price the request describes.

Phase 5, green. `apply_discount` now returns `max(price - price * percent / 100, Decimal("0.00"))`, quantized as before. `uv run pytest tests/test_pricing.py -q -k clamps` → `1 passed`.

Phase 6. Renamed the local `d` to `discount`; the test stays green.

Phase 7. `uv run pytest -q` → `42 passed, 1 failed`, the same `test_vat_rounding_eu` as the baseline; ruff and mypy unchanged. Committed as `fix(pricing): clamp discounted price at zero`.

## Test-first report

**Baseline:** `uv run pytest -q`, `uv run ruff check .`, `uv run mypy src` → 41 passed and 1 failed; ruff and mypy clean

**Tests**
- `test_discount_over_full_price_clamps_to_zero`: breaks if `apply_discount` stops clamping at zero
  - Red: `uv run pytest tests/test_pricing.py -q -k clamps` → `AssertionError: assert Decimal('-10.00') == Decimal('0.00')`
  - Green: `uv run pytest tests/test_pricing.py -q -k clamps` → `1 passed`

**Final check against baseline**
- New failures: none
- Pre-existing failures: `tests/test_tax.py::test_vat_rounding_eu`, untouched

**Mutation check:** not run; a pricing bug fix with one branch, not high-stakes for this project

**Risks left without a test:** negative discount percentages are not validated anywhere; outside this request, reported for the user to decide
</result>
</example>

## Why each step did what it did

- The baseline caught `test_vat_rounding_eu` before the change, so the final run's failure is shown to be pre-existing instead of fixed silently or blamed on the fix.
- The expected value 0.00 was written by hand from the requirement, not by calling `apply_discount`.
- The neighbouring risk (negative percentages) is reported, not fixed, because it is outside the request.
