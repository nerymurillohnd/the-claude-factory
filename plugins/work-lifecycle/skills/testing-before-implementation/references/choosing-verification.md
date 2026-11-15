# Choosing how to verify

Read this in phase 2 when the change is not plain testable behavior, or when you need to pick a test level. The test-first cycle is the default; pick another check only when its case below applies, and state which one and why.

## Contents

- [Which check fits the change](#which-check-fits-the-change)
- [Which test level fits the behavior](#which-test-level-fits-the-behavior)
- [Signs you picked the wrong level](#signs-you-picked-the-wrong-level)

## Which check fits the change

- Behavior in code that can be tested: the test-first cycle.
- Legacy code without tests: first a characterization test that pins what the code does today, run green against the current code, so the change has a safety net. Then make the change test-first. The characterization test records today's behavior, bugs included; when the change fixes one of those bugs, update that one assertion as part of the change and say so in the report.
- Visual interface: run the app or take a screenshot, inspect it against the requirement, and record what you checked and what you saw. Behavior behind the interface (validation, state, data flow) still goes test-first.
- Configuration or infrastructure: the tool's own check, with its output recorded: `--dry-run`, a plan command (`terraform plan`, `kubectl diff`), schema validation, or the service's config test.
- Throwaway prototype: no test-first cycle, only with the user's approval, recorded in the report. A prototype that is kept stops being throwaway: add its tests before it is built on.

## Which test level fits the behavior

- Unit: one function or class, with real collaborators wherever they are cheap and deterministic. The default for logic: parsing, calculation, validation, state changes.
- Integration: when the behavior lives in how components meet (a query and its schema, a handler and its middleware, a client and a recorded server response), or when the mocks a unit test would need would be larger than the code under test.
- End-to-end: when the risk is in the full path a user takes, such as sign-in, checkout or an export that crosses several services. Keep these few: they are slow and break for reasons unrelated to the change.

Write the test at the lowest level that can see the break you named in phase 3. A break that only shows when two components meet needs an integration test, however tempting a unit test with mocks is.

## Signs you picked the wrong level

- The test mocks the thing it claims to test, or asserts on how a mock was called rather than on a result.
- The setup is several times longer than the code under test.
- The test passes whatever the production code does: run the mutation check from `writing-good-tests.md` to find out.
- The test fails for reasons the change never touched, such as timing, ordering or shared state: move it down a level, or isolate what it shares.
