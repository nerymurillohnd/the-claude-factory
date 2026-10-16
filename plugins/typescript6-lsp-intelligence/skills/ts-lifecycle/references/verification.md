# Verification facet

Read when validating a code/configuration change. The goal is attributable success and failure across the affected contracts, including confidence that the observers actually examined them. This procedure implements the verification rules of SKILL.md.

## Choose evidence by claim

| Claim | Suitable evidence | What it does not prove |
| --- | --- | --- |
| The checker observes this file/contract | Known invalid type/member/import fixture fails with the expected diagnostic at the expected location; restoration clears it | Runtime correctness or adequate assertions |
| Runtime validation rejects invalid input | Valid input succeeds; invalid/boundary input has the specified rejection without unrelated failure | Every possible input is covered |
| Tests detect wrong behavior | Valid, runnable mutation changes behavior and the intended assertion fails | A compile failure is not a killed behavioral mutant |
| Refactoring preserves behavior | Equivalent transformation, such as a complete internal rename, preserves specified outputs/contracts | An incomplete rename that fails compilation tests a different property |
| Imports/declarations work for consumers | Isolated built/packed consumer exercises required module modes and supported compiler/runtime versions | Passing repository-local aliases establish published compatibility |

Use relevant positive and negative tests for changed behavior. For each checking layer relied upon, select an existing executable negative fixture or a small isolated sensitivity probe. If the change is documentation-only, research-only, or the layer is unavailable/irrelevant, record that reason instead of manufacturing a mutation. Missing sensitivity evidence for a required layer remains a verification gap.

## Baseline → controlled defect → restore → pass

1. Record actual tool versions, configuration and file scope, the baseline output of each project check, and existing user changes. Establish an expected-good case. A failure already present in the baseline does not block closing, but report it with its output, and keep it apart from the failure the probe is meant to cause.
2. Choose a deterministic defect and its **oracle**: the specific diagnostic, assertion, rejection or invariant expected to change, in a named file/project/layer. Make the defect relevant to the modified contract. For example, assigning a string to a known number property can test type checking; allowing an invalid boundary value can test runtime assertions. Choose from the actual contract rather than assuming either example applies.
3. Place the probe as the Probes section of SKILL.md requires. By default, use a temporary copy outside the project that keeps the required versions, configuration inheritance, resolution layout, generated inputs and runtime assumptions. Keep outputs and caches in the copy, and confirm that each observation targets the copy, not the original project. Probe inside the project only in `implementation` mode, under the conditions SKILL.md sets.
4. Introduce one controlled defect. Run the expected observer and verify the specific failure, not merely a nonzero exit. For LSP-backed claims, synchronize the changed content and use the bounded freshness/readiness procedure; diagnostic publication need not be immediate. When both native and semantic checking are claimed, exercise both, accounting for actual checker ownership.
5. If the defect is not detected, inspect inclusion, configuration, stale results, suppressions, `any`, assertion reachability and oracle validity. Classify the failure before changing anything. Fix only in-scope causes; unrelated tool/coverage repairs require their own authorization. Do not call the checker globally broken from one invalid probe, or suppress failures to obtain success.
6. Restore only the experimental change using captured content or precise edits, including when execution fails. Verify byte/hash or scoped-diff restoration, preserve concurrent user edits, and rerun the expected-good case. If concurrent edits prevent safe restoration, report the exact remaining probe rather than overwriting them. A failed restoration blocks completion.
7. Run appropriate native project type/checker, lint, tests, build and consumer/runtime checks on the final actual change. Use the project's real scripts and installed toolchain; a framework-specific checker may be necessary. Do not replace it with universal `tsc`, force strictness, weaken checks or silently update dependencies. Isolated success does not establish actual-project freshness or complete scope.

## Mutation and metamorphic testing

Targeted fault injection verifies sensitivity of a selected observer. Full mutation testing systematically alters behavior and measures which changes tests detect; it is not required for every small change. Introduce it when requested or when its scope and value justify it under existing authorization. An installed mutation tool may be useful; the skill does not authorize installing one.

Inspect surviving mutations: an equivalent mutation, uncovered path, weak assertion and incorrect test setup require different responses. Distinguish a killed mutant from compile/runtime infrastructure errors or timeouts according to the tool and evidence. One successful probe proves only that particular detection path.

For metamorphic checks, state the preserved relationship first, such as a complete private-symbol rename retaining output or an input permutation retaining an order-independent result. Verify that the relationship is actually required; public names, serialization and order can be contractual.

Official background: [Stryker introduction](https://stryker-mutator.io/docs/) and [mutant outcomes](https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/). Their scoring model is not a substitute for checking the expected failure in this workflow.

## Reporting

Report each result as observation, inference, contradiction or unavailable evidence (SKILL.md, rule 6), with the command and its output.
