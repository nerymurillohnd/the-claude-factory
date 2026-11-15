# Example: a new function in TypeScript, mocking only the network

Judgment to copy: the mock stands in only for the external service and is shaped like its real response; the tests assert on what the function returns, and a first test that passed too early is caught and fixed. Don't copy the language, names or numbers.

<example>
<request>
Add `fetchExchangeRate(from, to)` to `src/rates.ts`. It calls the rates API and returns the rate as a number; if the API returns no rate for the pair, it should throw `RateNotFoundError`.
</request>

<result>
Phase 1. `package.json` scripts: `test` runs `vitest run`, `lint` runs `eslint .`, `typecheck` runs `tsc --noEmit`. Existing tests in `src/*.test.ts` mock `fetch` with `vi.stubGlobal`, using recorded responses under `test/fixtures/`.

Baseline: `npm test` → `Tests 27 passed (27)`; `npm run lint` → no output, exit 0; `npm run typecheck` → exit 0.

Phase 2. Testable behavior: test-first, unit level. The rates API is external, so it is the one thing mocked, with the recorded response `test/fixtures/rates-usd.json` (`{"base":"USD","rates":{"EUR":0.92,"GBP":0.79}}`).

Phase 3, first behavior. Break: fails if `fetchExchangeRate` stops reading `rates[to]` from the response. Expected value by hand from the fixture: 0.92.

Phase 4, red. `rates.test.ts`:

```ts
it("returns the rate for the pair", async () => {
  vi.stubGlobal("fetch", mockFetch("test/fixtures/rates-usd.json"));
  await expect(fetchExchangeRate("USD", "EUR")).resolves.toBe(0.92);
});
```

`npx vitest run src/rates.test.ts` → `SyntaxError: The requested module './rates' does not provide an export named 'fetchExchangeRate'`. That is an error, not a failure: exported a stub that throws `new Error("not implemented")`, ran again → `AssertionError: promise rejected "Error: not implemented" instead of resolving`. Now it fails for the named reason.

Phase 5, green. Implemented the call and the lookup. `npx vitest run src/rates.test.ts` → `1 passed`.

Phase 3, second behavior. Break: fails if a missing pair stops throwing `RateNotFoundError`. A decision fixed by the request, so the test asserts the error type, not its message.

Phase 4, red. The test for `fetchExchangeRate("USD", "JPY")` passed on its first run: the code threw a `TypeError` from reading `undefined`, and the test only asserted `rejects.toThrow()`. It tested nothing. Tightened to `rejects.toBeInstanceOf(RateNotFoundError)` → `AssertionError: expected TypeError to be an instance of RateNotFoundError`.

Phase 5, green. Added the check and the error class. `npx vitest run src/rates.test.ts` → `2 passed`.

Phase 7. `npm test` → `Tests 29 passed (29)`; lint and typecheck exit 0, as the baseline.

## Test-first report

**Baseline:** `npm test`, `npm run lint`, `npm run typecheck` → 27 passed; lint and types clean

**Tests**
- `returns the rate for the pair`: breaks if the function stops reading `rates[to]`
  - Red: `npx vitest run src/rates.test.ts` → `promise rejected "Error: not implemented" instead of resolving`
  - Green: `npx vitest run src/rates.test.ts` → `1 passed`
- `throws RateNotFoundError for a missing pair`: breaks if a missing pair stops raising that error
  - Red: `npx vitest run src/rates.test.ts` → `expected TypeError to be an instance of RateNotFoundError`
  - Green: `npx vitest run src/rates.test.ts` → `2 passed`

**Final check against baseline**
- New failures: none
- Pre-existing failures: none

**Mutation check:** not run; not high-stakes

**Risks left without a test:** API timeouts and non-200 responses; the request names no behavior for them, so the user decides
</result>
</example>

## Why each step did what it did

- The missing export was an error, not a red: a stub made the test fail for the reason that matters.
- The second test passing early was the warning sign that it tested nothing; tightening the assertion made it catch the real break.
- Only `fetch` was mocked, with a recorded real response, so the tests exercise the real parsing.
