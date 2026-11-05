---
paths:
  - "scripts/**"
---

# Choosing Where a Maintenance Script Goes

Before you create or save any maintenance script, decide which of the four responsibilities it has. Place it in the matching folder:

- `scripts/generators/`
- `scripts/validators/`
- `scripts/checkers/`
- `scripts/testers/`

The one exception is `scripts/release/`: the version and release scripts that `release.yml`, the version gate and `npm run version:bump` run. They stay together because they run on the `python3` of CI's runner and target Python 3.12, unlike the other folders.

These stay where they are, outside the four folders, because they are not one of the four responsibilities:

- `scripts/gates.mjs`, the gate runner every `npm run` script and CI job calls.
- `scripts/lib.mjs` and `scripts/components.mjs`, libraries the other scripts import.
- `scripts/check-repo.mjs` and `scripts/sync-labels.mjs`, which `package.json` and the gates run by these paths.
- `scripts/basedpyright-maintainer.mjs`, the wrapper of the `basedpyright-` gates.
- `scripts/schemas/` (the JSON schemas the validators read), `scripts/biome-plugins/`, `scripts/categories.json` and the `tsconfig` files: data and configuration, not scripts.

A new script goes in one of the four folders; never add another to the root of `scripts/`.

These are not interchangeable names. Each responsibility has its own inputs, outputs, and place in the software lifecycle. Validators, checkers, and testers all evaluate something, but their scope, context, and consequences are different. Choose the correct folder and stay consistent.

## Generators — `scripts/generators/`

- **Purpose:** Create or transform artifacts.
- **Success criterion:** The artifact is created successfully with no syntactic errors.
- **Typical context:** Generators are constructive. They take an abstract input or template and produce a tangible artifact by creating or modifying files on disk.
- **Objective:** Automate the creation of repetitive code, documentation, or data structures.
- **Examples:** A script that reads official documentation and generates local Markdown files for a skill; a script that compiles schemas or utility classes from a configuration.

## Validators — `scripts/validators/`

- **Purpose:** Check conformance against a formal schema or rule.
- **Success criterion:** The input strictly meets the contract (schema or type).
- **Typical context:** Validators are structural and contractual. They check whether an existing file or data respects a predefined norm. They usually work statically and do not call the network.
- **Objective:** Guarantee that data is not corrupt, malformed, or incomplete before it is processed.
- **Examples:** `validators/marketplace-json-schema.py` validates `marketplace.json` against `marketplace.schema.json`. A missing required key or a wrong type causes failure. It does not check whether the URLs inside the JSON work; it only checks that the JSON has the correct shape.

## Checkers — `scripts/checkers/`

- **Purpose:** Inspect health, state, or external coherence.
- **Success criterion:** The resource exists, is alive, and is accessible.
- **Typical context:** Checkers are operational and state-oriented. They inspect content to audit its health, coherence, or currency in the real world. They often interact with the environment (network, filesystem, Python AST).
- **Objective:** Detect broken links, vulnerable dependencies, format violations, or discrepancies between files.
- **Examples:** `checkers/markdown-urls.py` does not care whether a Markdown file is well written. It only audits whether the web links and anchors still respond live.

## Testers — `scripts/testers/`

- **Purpose:** Evaluate logical behavior and execution contracts.
- **Success criterion:** The logic produces the expected result under the given conditions.
- **Typical context:** Testers are functional and behavioral. They execute parts of the system under controlled conditions (black-box or white-box) and verify that the logic produces the expected result.
- **Objective:** Prevent regressions and ensure the software does exactly what it was intended to do.
- **Exception:** a mod's tests stay in the plugin, as `.claude/CLAUDE.md` → Maintainer files inside a plugin sets.
- **Examples:** A test that feeds a URL-extraction function with trap texts (URLs containing commas, Markdown with escaped parentheses) and verifies that the regular expression extracts precisely what it should.
