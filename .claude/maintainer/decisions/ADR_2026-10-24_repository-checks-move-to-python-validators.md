---
status: accepted
date: 2026-10-24
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Repository checks move to Python validators

## Scope

- In scope: `scripts/validators/` (plugin names, required files, versions, README catalog, and the four schema validators), the checks `scripts/check-repo.mjs` kept, and the `validate:<script>` entries of the root `package.json`.
- Out of scope: wiring the validators into `scripts/gates.mjs` and CI, which is pending (DEBT-006).

## Context and problem statement

`check-repo.mjs` held every repository policy check in one Node script. Nery ordered separate maintainer scripts, one per concern, each failing with a message that names the file, the field and the cause: plugin-name consistency (the plugin name only, never the marketplace name), required files, versions across files, the README catalog against `plugins/` and each category, and each config file against its schema. Once they existed, `check-repo.mjs` ran the same checks twice. Where should a check live?

## Decision drivers

- One check, one place.
- Each failure names exactly what is wrong.

## Considered options

- **One validator per concern in `scripts/validators/`, and `check-repo.mjs` keeps only what none of them checks**: chosen.
- **Keep the checks in `check-repo.mjs` and add the validators beside it**: rejected because every rule would live twice.

## Decision outcome

Chosen option: **validators own their checks**:

- `check-repo.mjs` no longer checks entry names, sources, directories, renames, the manifest name and homepage, the required files, SemVer, the entry version, `[Unreleased]`, the current version's section or the root CHANGELOG; its three tests of those checks are gone.
- Each validator runs by path and has an npm entry, `npm run validate:<script>`; `package.json` declares no Python dependency.
- A plugin's license file is `LICENSE`, the name every plugin, the scaffold and the READMEs already use.

### Consequences

- Good, because each validator was proven with negative probes on throwaway copies of the repository, and all eight pass on the real one.
- Bad, because no gate runs the validators yet, so CI lost these checks when `check-repo.mjs` dropped them (DEBT-006).
- Bad, because the validators have no automated tests of their own yet; their probes were run by hand.

## More information

- Decided by Nery in the session of 2026-10-24 ("eliminar de los scripts que ya teníamos todo aquello que ya ejecutan los nuevos").
- Related: ADR_2026-10-21_gates-run-from-one-script, ADR_2026-10-21_maintainer-only-root-package-json.
