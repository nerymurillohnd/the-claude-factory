---
status: accepted
date: 2026-10-27
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The Biome configuration is `biome.jsonc`, with each setting's reason beside it

## Scope

- The repository's Biome configuration, renamed from `biome.json` to `biome.jsonc`.
- The files that name it: `.claude/CLAUDE.md`, `.claude/skills/building-plugins/references/templates.md`, `.husky/pre-commit`, `scripts/gates.mjs` and DEBT-032.
- Settled records keep the old name as history.
- Out of scope: the plugins, which ship no Biome configuration.

## Context and problem statement

The reasons for the configuration's non-default settings lived only in commit bodies (`809cf90`, `b3ada31`, `d86e3b1`) or nowhere:
- `lineWidth` and `expand`;
- the remaining `!!` patterns;
- the overrides;
- the rules raised or added above the preset.

DEBT-034 existed for exactly that reason: a force-ignore with no recorded reason, which a later reader could not judge. Strict JSON cannot hold a comment, and `files.includes` keeps `json.parser.allowComments` unset, so manifests stay strict. Where should each setting's reason live?

## Decision drivers

- The reason sits where the setting is changed, so an edit to one meets the other.
- One source: the reason is not duplicated in another record that can drift.
- No loosening of the strict JSON parsing that the manifests rely on.

## Considered options

- **Rename to `biome.jsonc` and write a one-line reason beside each non-default setting**: chosen.
- **Keep `biome.json` and list the reasons in one ADR**: rejected, because the reasons would sit apart from the settings and drift with each edit.

## Decision outcome

Chosen option: **`biome.jsonc` with the reasons inline**.
- The configuration reference states that `biome.jsonc` always allows comments and trailing commas. The rest of the repository's JSON keeps its strict parsing, since `json.parser.allowComments` stays unset.
- Measured on 2026-10-27 in a scratch copy and again in the repository: Biome 2.6.3 loads `biome.jsonc`, and `biome rage` reports "Path: biome.jsonc".

### Consequences

- Good, because every non-default setting now says why it exists, and the next unexplained one stands out.
- Good, because no tool reads the configuration by its file name: `git grep` finds the name only in Markdown, the hook's comment and the gates' title and comment.
- Bad, because a tool that only looks for `biome.json` would miss the configuration. The VS Code extension's `requireConfiguration` relies on Biome's own loader, which finds `biome.jsonc`; this is inferred from `crates/biome_lsp/src/session.rs`, not tested in the editor.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Biome reads the renamed file | `biome rage` | "Path: biome.jsonc" | After a Biome upgrade |
| The configuration behaves exactly as before | `biome rage --linter` and `--formatter`, `biome ci . --verbose`, and the findings, before and after | The same 242 enabled rules and formatter settings. The same 170 files, with `biome.json` replaced by `biome.jsonc`. The same 4 `useLiteralKeys` infos, at lines moved by an earlier test change | Once |
| The gates and the hook pass | `npm run lint:js`, `npm run validate`, the gates' tests, `shfmt -d` and `shellcheck` on `.husky/pre-commit` | All pass; 28 of 28 tests; `biome migrate`: "no migration needed" | Each commit |
| The VS Code extension still registers Biome in this repository | Open a file in VS Code with `biome.requireConfiguration: true` | pending | When item 27 lands |

## More information

- Decided by Nery on 2026-10-27, as D4 (a) of `.claude/specs/2026-10-26-biome-config-corrections-and-strictness-design.md` (item 19).
- The same commit drops `style.noNegationElse: "off"`. The rule is not recommended, so the preset already leaves it off. `correctness.noUndeclaredDependencies: "off"` stays: with it on, Biome reports the mods' imports of the engine's `claude-code` module, which no `package.json` declares (measured with `--only`).
