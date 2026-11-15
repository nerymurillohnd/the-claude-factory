# Writing good tests

Read this before writing or changing any test or mock. A good test fails when the code breaks and passes when it works; everything here serves those two properties.

## Contents

- [Name the break](#name-the-break)
- [Test the real thing](#test-the-real-thing)
- [Expected values](#expected-values)
- [Behavior, not text](#behavior-not-text)
- [Mocks](#mocks)
- [The mutation check](#the-mutation-check)
- [Questions before each test](#questions-before-each-test)
- [Warning signs](#warning-signs)

## Name the break

Before writing a test, say in one sentence which change to the production code would make it fail. "Breaks if `parse_amount` stops rounding half-up" names a break. "Tests `parse_amount`" names nothing.

Then say whether that change would be a bug or a decision:

- A bug: the test protects a requirement. Keep it strict.
- A decision: someone could change it on purpose later, such as a default value or a message's wording. Assert only what the requirement fixes, so the test doesn't block a legitimate change.

If you can't name a break, the test catches nothing: drop it, or find the behavior it should pin.

## Test the real thing

- Call the code the way its callers do, through its public interface, with real inputs.
- Use real collaborators when they are fast and deterministic: in-memory data structures, pure functions, a temporary directory, an in-memory or throwaway database the project already uses for tests.
- Assert on results the caller sees: a return value, a raised error, a written file, a stored row, an emitted event. Assert on internal calls only when that call is itself the behavior, such as "sends exactly one email".
- Cover one behavior per test, so a failure names one cause. Several assertions are fine when they describe the same behavior.

## Expected values

- Write the expected value by hand, from the requirement or a worked example: `assert total("2 × 3.50") == Decimal("7.00")`.
- Never compute it with the code under test, or with a copy of its logic. A test that reproduces the algorithm passes whenever the algorithm is consistently wrong.
- For large outputs, compare against a small hand-checked fixture, and keep the fixture next to the test with a line on how it was checked.

## Behavior, not text

- A change detector fails on any change, right or wrong: snapshots of whole outputs nobody reviews, assertions on log text, on private names or on the order of unordered data. It costs a fix on every refactor and catches nothing specific.
- Assert the parts of an output the requirement fixes: the fields, the values, the order when order matters. Leave formatting and wording free unless they are the requirement.
- A snapshot is acceptable only when someone reviews each change to it and the snapshot is small enough to read.

## Mocks

- Mock only at the slow or external level: the network, the clock, randomness, the filesystem outside the project, paid or rate-limited services, hardware.
- Shape each mock like the real thing: the same fields, types, errors and edge cases the real service returns. Take the shape from a recorded real response or the service's documented schema, not from what the code under test happens to read.
- Assert on what the code does with the mock's answer, not on the mock itself. "The mock was called with X" is a test of the mock unless the call is the behavior.
- A test whose setup is mostly mocks is usually at the wrong level: move it up to an integration test with fewer, more real parts.

## The mutation check

The mutation check asks: if this code broke, would a test notice?

- Mental check, for every test: picture the one-line change you named as the break, and confirm the test would fail on it.
- Real check, on high-stakes work: pick the line whose mistake would cost the most (a comparison, a rounding, a permission check, a boundary), change it on purpose (`>=` to `>`, `round` to `floor`, remove a guard), run the tests, confirm at least one fails, then revert and run them again green. Record the line, both runs and their output.
- If no test fails, the code is untested where it matters: add the test that catches it before closing the task.

## Questions before each test

Answer these before writing a test or a mock; a "no" is a reason to change the test first.

1. Can I name the production change that would make this test fail?
2. Does the test call the code the way a real caller does?
3. Is every expected value written by hand?
4. Does every mock stand in for something slow or external, shaped like the real thing?
5. Would the test still pass after a refactor that keeps the behavior?
6. Will it fail, not error, before the code exists, and will the failure message say why?

## Warning signs

Stop and rework the test when you see:

- It passed on its first run, before any code existed.
- Its failure message doesn't mention the behavior, such as `AssertionError` with no values, or `expected true to be false`.
- It asserts that a mock was called, and nothing else.
- Its expected value came from running the code.
- It needs a sleep, a retry or a fixed order of other tests to pass.
- It breaks on a rename or a reformat that kept the behavior.
- Its setup is several times longer than the code it tests.
