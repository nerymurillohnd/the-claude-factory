# Research procedure

Read when the change crosses a tool boundary or depends on a version (SKILL.md, "Discover and research the actual system"), before recommending or making it. SKILL.md holds the rules and the modes; this file holds only the steps.

1. Read project-evidence.md, linked from SKILL.md, to inspect the installation and configuration and to run safe compiler probes. Read the project's instructions before running any script.
2. Read source-map.md and select every category that applies: types and inference, diagnostics, configuration, modules, declarations, JavaScript interoperability, compilation, migrations, editor tooling, integration boundaries. Record the selected categories and their count.
3. Read the official pages of the selected rows, plus their prerequisites and related links when material. Find the counterparts the project actually uses instead of assuming a named example is present. Investigate a plausible connection before excluding it. Record the relationship each source settles.
4. When a decision depends on a version, an upgrade or another tool's contract, read integration-and-releases.md for release reconciliation and for that counterpart contract; otherwise skip this step. Settle disagreements between documentation, history and local behavior with version-matched observations. Keep the uncertainty when you cannot settle one.
5. Prepare the handoff to execution:
   - the proposed change;
   - the affected producers and consumers;
   - the supporting sources and the versions they apply to;
   - the intended behavior and the relevant negative cases;
   - the `LSP` operations, the native checks and the probe or existing negative fixture;
   - the remaining blockers.

   Do not implement anything that depends on missing essential evidence.

Research and execution may alternate. Finishing a first reading pass does not freeze the assumptions.
