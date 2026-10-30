# Findings against the plugins and mods live-sources audit

Date: 2026-10-29. Ground truth: `2026-10-29-plugins-and-mods-live-sources-audit.md` (D6 amended after `claude plugin eval --help`). Five read-only auditors, one section each, reports kept as delivered. Status at consolidation: R-1 and R-2 fixed (memory edited); P-8 resolved (the audit was wrong, the plugin is right). R-7 retracted on review: plugins/mods/create says "trust these files over any page, this one included, when they disagree", so the ADR's authority claim is right and the ADR stays (the audit's F8.1 now quotes it). P-9 needed no change (the plugin-evals docs accept a root `plugin.json`). Nothing else has been changed.

Verification: every one of the 67 entries was checked against its cited file. 59 quotes were matched by script, and the other 8 by hand (T-2, T-6, T-8, T-9, T-10, P-1, P-11, P-12: multi-line, escaped or `.jsonc` quotes). All 67 exist as quoted. The judgments (conflict, severity, correction) are the auditors' and are settled in review.


## Instruction files (CLAUDE.md, rules, LESSONS.md)

FINDINGS: 15

- id: I-1
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/CLAUDE.md:53
- quote: "- **Maintainer scope**: everything outside `plugins/`. Its environment is the tools, versions and binaries on Nery's machine."
- conflicts with: F3.3, F7.2, F5.3, D6, §10.1, §10.6, §10.7
- why: La regla define el ámbito por la ubicación y no por la función. Las pruebas de los mods tienen que estar dentro de `plugins/<plugin>/`, y las suites de evals están ahí por defecto. Por eso esta línea los clasifica como ámbito de plugin, cuando en realidad son herramientas del mantenedor que se ejecutan con la build de Nery. En el repo ya hay `tests/*.test.ts(x)` y `evals/` registrados en 7 plugins.
- severity: high
- proposed correction: "- **Maintainer scope**: everything outside `plugins/`, plus the maintainer files the official tools require inside a plugin directory: a mod's `*.test.ts(x)` files, eval suites and any type-check config. They run only on Nery's machine against his build, are judged only by what they tell him, and never by a user's version. Committed, they still ship to users as inert files (everything committed under `plugins/<plugin>/` ships; nothing git-ignored does)."

- id: I-2
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/CLAUDE.md:51
- quote: "nothing from the maintainer's environment leaks into what a plugin ships or needs."
- conflicts with: F3.3, F7.2, D6, §10.6, §10.7
- why: Las herramientas oficiales obligan a que las pruebas de los mods (y, por defecto, los evals) se envíen dentro del plugin. Tal como está escrita, la regla se puede cumplir para los evals, pero para las pruebas de los mods es imposible, y empuja a sacarlas de la carpeta, cosa que `claude plugin test` no admite.
- severity: medium
- proposed correction: "nothing from the maintainer's environment becomes something a plugin needs at runtime. Maintainer files the official tools require inside the plugin directory (mod tests) ship as inert files; keep everything else maintainer-only outside `plugins/` or git-ignored."

- id: I-3
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/CLAUDE.md:71
- quote: "- Tests of plugin scripts live in `scripts/testers/<plugin>/`, which is maintainer scope: their test dependencies never enter a plugin's runtime."
- conflicts with: F7.1, F7.2, §10.6
- why: `claude plugin test` solo encuentra archivos `.test.ts`/`.test.tsx` dentro de la carpeta del mod. Si se aplica la regla al módulo de hooks de un mod, sus pruebas acaban donde el runner oficial no las descubre. Ahora mismo el repo tiene `plugins/*/tests/*.test.ts(x)` en 6 plugins, en contra de lo que dice esta línea.
- severity: high
- proposed correction: "- Tests of plugin scripts live in `scripts/testers/<plugin>/`, which is maintainer scope. A mod's tests are the exception: they live inside the mod's folder (in `tests/`), because `claude plugin test` only finds them there; they import only from the mod and `claude-code/testing`."

- id: I-4
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/CLAUDE.md:59
- quote: "- **Every other file inside a plugin's directory** (its manifest, components, scripts, dependencies, `CHANGELOG.md`): a pull request and a version bump, through `release-and-versioning`."
- conflicts with: F3.3, F3.5, F5.3, F7.2, §10.1
- why: Las pruebas, los evals y la configuración de tipos dentro de `plugins/<plugin>/` caen en "every other file". Por esta regla, un cambio que solo toca una prueba exige subir versión. Son archivos inertes para el usuario y no cambian nada de lo que hace el plugin, que es el mismo criterio que la línea 58 usa para eximir la documentación.
- severity: medium
- proposed correction: Añadir una viñeta: "- **A plugin's maintainer files** (a mod's tests, eval suites, type-check config): a pull request, with no version bump or `CHANGELOG.md` entry, because users never run them; they reach users with the plugin's next version." (O decidir otra política, pero hay que nombrarla de forma explícita.)

- id: I-5
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/CLAUDE.md:87
- quote: "- Keep these git-ignored in `.gitignore` and never commit them: eval results (`eval-results/` and `**/evals/results/`), `.claude/plans/`, `.claude/session-handoff/`, `.claude/memory/` and `.claude/settings.local.json`."
- conflicts with: F8.4, F8.7, §10.4, D6, F5.3
- why: La lista no dice nada del `tsconfig.json` que se genera en la raíz de cada mod. Si se hace commit, se envía a los usuarios y extiende archivos que ellos no tienen. Ya está registrado en 6 plugins (file-tree-pane, macos-grep-guard, model-trace, project-maintainer, tool-ledger, turn-meter), y el gate `mod-tsc:` de `scripts/gates.mjs:519-527` depende de él. Tampoco dice que una suite de evals se puede mantener fuera del plugin con `--eval-dir`.
- severity: medium
- proposed correction: Añadir: "- Never commit a per-mod `tsconfig.json`; type-check mods through one maintainer tsconfig outside `plugins/` (as Anthropic's `mods/tsconfig.json` does), and git-ignore any `tsconfig.json` Claude Code generates at a mod's root." Y sobre los evals, decidir: "eval suites live outside `plugins/` and run with `--eval-dir`", o dejar escrito que se envían como archivos inertes.

- id: I-6
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/CLAUDE.md:68
- quote: "- JavaScript and TypeScript: type-check with `tsc` under the strictest settings and `--noEmit`."
- conflicts with: F6.3, F6.9, F7.4, F8.5, F8.6, §10.5
- why: Aplicada a los mods, la regla presenta `tsc` como el control de calidad. Pero las declaraciones contra las que comprueba solo valen para la build que las escribió, mientras que `claude plugin validate` y `claude plugin test` comprueban el mod contra el motor instalado sin archivos de declaración. Un usuario no necesita TypeScript.
- severity: medium
- proposed correction: Añadir: "For a mod, `tsc` is an editor aid against the declarations of Nery's installed build only; `claude plugin validate` and `claude plugin test` are the checks of record. A mod's user-facing compatibility comes only from its README's minimum Claude Code version."

- id: I-7
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/CLAUDE.md:155
- quote: "Release tags (`<plugin>--v<version>`) are created unsigned by `release.yml`, under the exemption `~/.claude/CLAUDE.md` gives public plugin marketplaces: users never fetch a tag"
- conflicts with: F3.6, F4.5
- why: Los rangos de versión en `dependencies` se resuelven a "the highest git tag that satisfies this range", así que el Claude Code de un usuario sí lee estos tags cuando instala un plugin que depende de otro. El propio `release.yml:5` lo dice: "so plugin dependency ranges resolve against them". Además, `release.yml` crea los tags con `gh release create` y no con `claude plugin tag`, que es el que valida, comprueba que `plugin.json` y la entrada del marketplace coinciden y exige un árbol limpio.
- severity: high
- proposed correction: Sustituir la justificación por una cierta (por ejemplo: "signing in CI would put the signing key in a GitHub secret; users' dependency resolution reads these tags but does not verify signatures") o volver a decidir la exención con Nery. Además: "Tags follow `claude plugin tag`; run `claude plugin validate` and the version-consistency check before the workflow tags."

- id: I-8
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/CLAUDE.md:37 (y la misma regla en /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/rules/plugins/mcp-component.md:15, /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/rules/readme-md.md:41, /Users/forestalmt/.claude/LESSONS.md:16)
- quote: "- When docs and release notes differ, the release notes win: docs lag releases."
- conflicts with: §2 (precedence), D4
- why: En el orden de precedencia de la auditoría, el binario instalado va por delante de las release notes. D4 enseña que una nota de versión puede hablar de la carga cuando la doc habla de la validación, y en ese caso hay que comprobar con el binario antes de apoyarse en la nota.
- severity: low
- proposed correction: "- Precedence: the installed binary (`--help`, `claude plugin validate`/`test`), then the release notes, then the docs. When a release note and a doc speak of different stages (load vs validate), confirm on the installed build before relying on either."

- id: I-9
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/CLAUDE.md:73
- quote: "A plugin's own `package.json` and `package-lock.json` hold only that plugin's runtime dependencies, pinned exactly; Claude Code installs them for users when it caches the plugin."
- conflicts with: F3.7, F3.2
- why: Faltan condiciones que limitan lo que se puede declarar: solo paquetes del registro, `--ignore-scripts`, sin `overrides`, resolución congelada, tiempo límite de 60 s, y `package.json` junto con un lockfile soportado en la raíz del plugin. Tampoco dice que los plugins con ruta relativa de un marketplace local (el clon de Nery) se cargan en sitio y no se copian a la caché.
- severity: low
- proposed correction: "...; Claude Code installs them into the cached copy only when the plugin root has both files: registry packages only, exact pins, no `overrides`, no install scripts (`--ignore-scripts`), 60-second limit. Nery's local-path clone loads in place, so `npm run setup` installs them there."

- id: I-10
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/rules/plugins/plugins-scripts.md:24
- quote: "- Mods, or when the plugin integration requires Node: `#!/usr/bin/env node`."
- conflicts with: F6.2, F6.3, F6.1
- why: El módulo de hooks de un mod es un ES module que Claude Code carga directamente (exporta `register(on, options)`). No se ejecuta como script, no necesita Node ni shebang, y el usuario no necesita Node. Esta línea lleva a declarar Node como prerrequisito en el README.
- severity: high
- proposed correction: "- Node scripts the plugin runs as commands: `#!/usr/bin/env node`. A mod's hooks module is not a script: no shebang, no `chmod +x`, no Node prerequisite; Claude Code loads it directly (load `building-mods`)."

- id: I-11
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/rules/plugins/plugins-scripts.md:42
- quote: "- Node scripts use only `node:` built-in modules, unless the plugin ships its dependencies."
- conflicts with: F6.4
- why: El glob `plugins/*/hooks/**` hace que esta regla se cargue también para los módulos de hooks de los mods. En un mod, la única importación bare permitida es `claude-code` y el resto tienen que ser rutas relativas dentro del plugin. Esta regla permite `node:` y dependencias que se envían con el plugin.
- severity: high
- proposed correction: Añadir: "- A mod's hooks module imports only files inside the plugin by relative path, plus the bare `claude-code`; no `node:` modules, no npm dependencies."

- id: I-12
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/rules/plugins/plugins-scripts.md:53-61 (y 28)
- quote: "## Hook entry-point scripts" … "- Read the hook input as JSON from stdin." … "and options from `CLAUDE_PLUGIN_OPTION_<KEY>`"; línea 28: "- Run `chmod +x` on every hook script"
- conflicts with: F6.1, F6.2, F6.5
- why: El glob `plugins/*/hooks/**` carga estas reglas también para `hooks/` de un mod. En un mod, las opciones llegan como el argumento `options` de `register` (valores de `userConfig` con sus defaults), no por stdin ni por variables de entorno. Además, el módulo no es ejecutable.
- severity: medium
- proposed correction: Al principio de la sección: "These apply to command hooks in `hooks/hooks.json`. A mod's hooks module (named in `modules`) follows `building-mods` instead: it exports `register(on, options)`, reads options from `options`, and needs no shebang or `chmod +x`."

- id: I-13
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/rules/readme-md.md:17
- quote: "| Any other, such as `scripts/testers/<plugin>/…/README.md` | A maintainer note, never shipped to users | Maintainer | Nothing more: keep it accurate |"
- conflicts with: F3.3, §10.7
- why: Cualquier README que se haga commit dentro de `plugins/<plugin>/` (por ejemplo en `tests/` o `evals/`, o el de un mod como en el layout de Anthropic) se envía a los usuarios. Decir "never shipped" es falso para todo lo que está bajo `plugins/`.
- severity: medium
- proposed correction: "| Any other outside `plugins/`, such as `scripts/testers/<plugin>/…/README.md` | A maintainer note, never shipped to users | … |" y añadir una fila: "| Any other inside `plugins/<name>/` | Ships to users in the plugin's cache | Plugin | Follow \"Every README\" |".

- id: I-14
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/rules/scripts/choosing-location.md:8-13 (y 41)
- quote: "Before you create or save any maintenance script, decide which of the four responsibilities it has. Place it in the matching folder:" … "- `scripts/testers/`"
- conflicts with: F7.2, §10.6, D6
- why: Para un tester, la regla manda siempre a `scripts/testers/`, sin la excepción oficial: las pruebas de un mod tienen que estar dentro de la carpeta del mod.
- severity: medium
- proposed correction: Añadir en "Testers": "Exception: a mod's tests live inside the mod's folder (`plugins/<mod>/tests/`), because `claude plugin test` only discovers them there."

- id: I-15
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/rules/plugins/mcp-component.md:76-77
- quote: "- Validate path variables and persistent storage against:\n  https://code.claude.com/docs/en/plugins/components#path-variables-and-persistent-data"
- conflicts with: F4.4
- why: La auditoría sitúa la tabla de dónde se resuelve cada variable en plugins/manifest-reference, "Where each variable resolves". No he comprobado si el ancla actual sigue existiendo, así que es una pregunta y no un error confirmado.
- severity: low
- proposed correction: Apuntar a `https://code.claude.com/docs/en/plugins/manifest-reference` ("Where each variable resolves"), o verificar el ancla actual antes de mantenerla.

Notas (sin hallazgo):
- `scripts/schemas` ya incluye `types`, `experimental.evals` y `modules`.
- `.gitignore` ya tiene `**/evals/results/` (F5.3).
- `building-plugins/references/readme-style.md:16,36` ya obliga a declarar la versión mínima de Claude Code y la de cada función que depende de versión (§10.2, D1).
- Ningún archivo del alcance menciona `/plugin-types` (D2) ni `.claude-plugin/types/`.
- LESSONS.md no tiene más líneas sobre plugins, mods, pruebas, tipos o ámbitos que entren en conflicto.

Archivos leídos:
- /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/maintainer/audits/2026-10-29-plugins-and-mods-live-sources-audit.md
- /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/CLAUDE.md
- /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/rules/readme-md.md
- /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/rules/plugins/mcp-component.md
- /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/rules/plugins/plugins-scripts.md
- /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/rules/scripts/schemas-templates.md
- /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/rules/scripts/maintainer-scripts.md
- /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/rules/scripts/choosing-location.md
- /Users/forestalmt/.claude/LESSONS.md
- Leídos solo como evidencia: package.json, .gitignore, `git ls-files plugins`, .github/workflows/release.yml (grep), scripts/gates.mjs (grep), scripts/schemas (grep), .claude/skills/building-plugins/references/readme-style.md (grep)

No comprobado: si las URLs de mcp-component.md resuelven (no consulté la web), ni el contenido completo de las skills `testing-mods`, `building-mods` y `release-and-versioning`, que quedan fuera del alcance.


## Project skills (.claude/skills)

FINDINGS: 15

- id: S-1
- file:line: .claude/skills/building-mods/SKILL.md:40
- quote: "The mod's own `tsconfig.json` and `types/index.d.ts` are committed."
- conflicts with: F8.4, F8.7, F3.3, §10.4, §10.7
- why: The skill tells authors to commit a per-mod tsconfig.json. The engine generates that file, it extends a git-ignored file users never have, and committed it ships to every user for nothing. Anthropic keeps no per-mod tsconfig. Six plugins already commit one (plugins/{file-tree-pane,macos-grep-guard,model-trace,project-maintainer,tool-ledger,turn-meter}/tsconfig.json; that is repo scope, flagged here only as the effect).
- severity: high
- proposed correction: "Commit `types/index.d.ts`, the mod's contract. Never commit a `tsconfig.json` inside `plugins/<mod>/`: Claude Code writes one for the developer's editor, and a committed one ships to users with no use. Type-check from one repository-level tsconfig outside `plugins/`." Then delete the committed per-mod files in a plugin PR.

- id: S-2
- file:line: .claude/skills/building-mods/SKILL.md:20
- quote: "| Type check | `tsc -p plugins/<mod> --noEmit` |"
- conflicts with: F8.4, F8.7, §10.4, §10.5
- why: The command depends on the per-mod tsconfig that S-1 removes. The table also lists it among the "native tools" without saying it proves nothing beyond the build that wrote the declarations.
- severity: medium
- proposed correction: "| Type check (maintainer aid; valid only for the build that wrote the declarations) | `tsc -p <repository-level tsconfig> --noEmit` |"

- id: S-3
- file:line: .claude/skills/building-mods/SKILL.md:17
- quote: "`plugins/<mod>/.claude-plugin/types/claude-code/index.d.ts` once the mod has loaded"
- conflicts with: F8.1, F8.2, D5
- why: The declarations are written only when a mod loads in an interactive `--plugin-dir` session, or for a mod Claude wrote. "Once the mod has loaded" repeats the D5 error: `-p`, SDK, `plugin test` and `validate` write nothing.
- severity: medium
- proposed correction: "…`index.d.ts` once the mod has loaded in an interactive `claude --plugin-dir plugins/<mod>` session (never `-p`, the SDK, `claude plugin test` or `claude plugin validate`)…"

- id: S-4
- file:line: .claude/skills/building-mods/SKILL.md:38
- quote: "write the change, prove it with validate, test and `tsc`"
- conflicts with: §10.1, §10.5, F6.9, F7.4, F8.5
- why: `tsc` is presented as proof on a par with validate and test. Validate and test run the installed engine with no declarations. `tsc` proves something only against the build that wrote them.
- severity: medium
- proposed correction: "write the change and prove it with `claude plugin validate --strict` and `claude plugin test`, which run the installed engine; a `tsc` run is an editor aid for that build only and proves nothing about users' builds."

- id: S-5
- file:line: .claude/skills/building-mods/SKILL.md:43
- quote: "A top-level function declaration imported from another file of the mod loads from 2.1.299; the docs page still says it fails, so confirm with validate the first time you rely on it."
- conflicts with: D4
- why: It states loading as settled fact and treats the item as usable. D4 says to treat imported helpers that take `$` as unsupported until validate on the installed build passes them, because the release note speaks of loading and the docs of validation.
- severity: low
- proposed correction: "Treat a function imported from another file that receives `$` as unsupported until `claude plugin validate` on the installed build passes it; if you then rely on it, state 2.1.299 as the minimum."

- id: S-6
- file:line: .claude/skills/building-mods/SKILL.md:90 (also .claude/skills/testing-mods/references/version-drift.md:20)
- quote: "Validate names the hooks skipped under managed settings (2.1.299)."
- conflicts with: D3
- why: 2.1.304 removed validate's notes about where hooks run, and it is not stated whether the 2.1.299 note survived. The audit says not to rely on either note, yet this line makes it a README source.
- severity: medium
- proposed correction: Delete the sentence. Take organization effects only from `/en/plugins/mods/admin`. In version-drift.md:20, mark the 2.1.299 note **[unverified after 2.1.304]**.

- id: S-7
- file:line: .claude/skills/building-mods/SKILL.md:95
- quote: "tell users to run `claude plugin validate` themselves before installing."
- conflicts with: §10.1, owner principle (validation is maintainer tooling users never run), F3.2
- why: It pushes validation onto users. A marketplace user also has no plugin folder before installing; they get only the cache copy after install. The README disclosure built from validate's lines is what users need.
- severity: medium
- proposed correction: Replace with "list in the README everything the mod hooks and calls (the list built above); never ask users to run validate, tests or type checks."

- id: S-8
- file:line: .claude/skills/building-plugins/assets/README-template.md:164
- quote: "a mod runs with your permissions and no sandbox; `claude plugin validate <path to the plugin folder>` shows everything it hooks and calls."
- conflicts with: §10.1, owner principle, F3.2, F6.8
- why: This is the user-facing form of S-7: it asks users to run maintainer validation on a folder they don't have before installing.
- severity: medium
- proposed correction: "a mod runs with your permissions and no sandbox. Install it only if you trust this marketplace; the Hooks line above lists everything it hooks and calls." Drop `<path to the plugin folder>` from the KEEP list in check-readme-placeholders.py and from the templates.md:12 note.

- id: S-9
- file:line: .claude/skills/testing-mods/SKILL.md:37-40
- quote: "4. **Type check.** Type-check the hooks and the tests against the declarations Claude Code writes for the installed build … Then run `tsc -p <dir> --noEmit`. Claude Code adds a root `tsconfig.json` that extends the generated one when the mod has none."
- conflicts with: §10.4, §10.5, F8.4, F8.5, F8.7, §10.1
- why: Type checking is a required step of a workflow whose goal is "how to prove a mod works". It relies on the generated per-mod tsconfig, and it can't apply to the cached user copy (step 7), which has no declarations. A type check proves nothing beyond the maintainer's build. validate and test (steps 3 and 5) already cover the installed engine.
- severity: high
- proposed correction: Make it optional and maintainer-only: "4. **Type check (optional, this marketplace's own mods only).** It proves only against the build that wrote the declarations. Refresh them in an interactive `--plugin-dir` session, check that the header build equals `claude --version`, then run `tsc` from the repository-level tsconfig outside `plugins/`. Never commit the root `tsconfig.json` Claude Code adds to the mod. Proof of behavior comes from steps 3 and 5."

- id: S-10
- file:line: .claude/skills/plugin-hooks-guidance/SKILL.md:98
- quote: "Run `claude plugin validate --strict plugins/<name>` and the plugin's tests, which live in `scripts/testers/<plugin>/`"
- conflicts with: F7.1, F7.2, D6, §10.6
- why: The skill's trigger covers any plugin's hooks.json, which includes a mod's. It tells the reader that a plugin's tests live outside the plugin. A mod's `*.test.ts` must stay inside the mod folder for `claude plugin test` to find them.
- severity: medium
- proposed correction: Add: "A mod's tests (`*.test.ts`, `*.test.tsx`) stay inside `plugins/<name>/` and run with `claude plugin test plugins/<name>` (`testing-mods`); only tests of a non-mod hook's scripts live in `scripts/testers/<plugin>/`." Also add a Hand-offs row: a hooks module → `building-mods`.

- id: S-11
- file:line: .claude/skills/building-plugins/assets/README-template.md:211
- quote: "| 🧩 Mods | ✅ every Claude Code session except a Desktop session on WSL |"
- conflicts with: F6.7, D1
- why: Hooks run in those sessions, but drawing appears only in the terminal, Desktop and VS Code. VS Code needs extension 2.1.299+, or 2.1.304+ without feature flags. A mod that draws gets a ✅ it doesn't earn in `-p`, the SDK, Remote Control or cloud sessions.
- severity: medium
- proposed correction: "✅ hooks in every Claude Code session except Desktop on WSL; ⚠️ drawing only in the terminal, Desktop and VS Code (extension v2.1.299+, v2.1.304+ without feature flags)". Change docs/compatibility.md first, since the template copies it.

- id: S-12
- file:line: .claude/skills/building-plugins/references/manifest-and-components.md:84
- quote: "A plugin whose `hooks/hooks.json` lists a JavaScript module under `modules` (v2.1.287+)."
- conflicts with: F6.1, F6.2, F6.7, D1
- why: The hooks module may be `.ts`, `.mts`, `.cts` or `.tsx` as well as JS. The floor leaves out Desktop 2.1.286 and the per-feature minimums D1 lists.
- severity: low
- proposed correction: "A plugin whose `hooks/hooks.json` has `modules`, one path to a hooks module (`.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.mts`, `.cts` or `.tsx`). Mods need v2.1.287 in the terminal, v2.1.286 in Desktop; newer features carry their own minimum."

- id: S-13
- file:line: .claude/skills/building-plugins/references/manifest-and-components.md:17
- quote: "Component directories sit at the plugin root: `skills/<name>/SKILL.md`, `commands/*.md` (older form; use skills), `agents/*.md`, `hooks/hooks.json`, `.mcp.json`, `.lsp.json`, `output-styles/`, `themes/`, `monitors/monitors.json`, `bin/`, `settings.json`."
- conflicts with: F4.3
- why: The standard layout also includes `workflows/`, which line 52 of the same file treats as a component key. The list is incomplete against the official layout.
- severity: low
- proposed correction: Add `workflows/` to the list.

- id: S-14
- file:line: .claude/skills/testing-plugins/references/eval-policy.md:74-76
- quote: "Ship everything a case needs inside the plugin." / "An eval directory other than `evals/`: `\"experimental\": { \"evals\": \"quality/evals\" }` in `plugin.json`, or `--eval-dir` on both `init` and the run."
- conflicts with: F3.3, F5.3, D6 (as amended: `--eval-dir` is a "Directory name (below the plugin)" per `claude plugin eval --help` 2.1.314), §10.7
- why: It never says that a suite committed under the plugin directory ships to every user's cache as inert files. Every eval directory, `--eval-dir` included, sits below the plugin, so the suite can't be kept out of what users receive.
- severity: low
- proposed correction: Add: "A suite lives below the plugin (`evals/`, or the directory `experimental.evals` or `--eval-dir` names, which `--help` defines as below the plugin), so a committed suite reaches every user's cached copy as inert files and never runs there. Keep it free of secrets and of anything large." Reword line 74: "Put everything a case needs in the plugin's components or the case's fixtures."

- id: S-15
- file:line: .claude/skills/testing-plugins/references/eval-policy.md:16 (rule implemented in .claude/skills/testing-plugins/scripts/changed-eval-plugins.sh)
- quote: "**Edited** = one of its components or dependencies changed: any file under the plugin directory except its eval directory and the documents `README.md`, `CHANGELOG.md`, `LICENSE*` and `NOTICE*` at its root."
- conflicts with: F7.2, F8.4, §10.1
- why: For a mod, a change only to its `*.test.ts` files or to a generated `tsconfig.json` counts as a component edit and triggers a paid full CI eval run. Both are maintainer files that change nothing users run.
- severity: low
- proposed correction: Exclude `*.test.ts`, `*.test.tsx` and `tsconfig.json` from "edited", in both the text and changed-eval-plugins.sh.

No finding: no file mentions `/plugin-types` (D2). Every stated mod floor in the skills matches 2.1.287 terminal / 2.1.286 Desktop. Nothing tells the reader to commit `.claude-plugin/types/` or to move mod tests out of the mod folder, apart from S-10. building-mods:99 (tested-with version in CHANGELOG, minimum in the README) agrees with §10.2.

Files read (paths under .claude/skills/):
- Read in full: building-mods/SKILL.md; testing-mods/SKILL.md, references/{github-marketplace,testing,troubleshooting,version-drift}.md, scripts/{check-mod.sh,fetch-github-mod.sh}; building-plugins/SKILL.md, references/{manifest-and-components,mcp-hooks-and-lifecycle,mcp-servers,public-readiness,readme-style,repo-layouts,sources,templates,validation-messages,versioning-and-release}.md, assets/{plugin-template.json,CHANGELOG-template.md,NOTICE-template.txt}; README-template.md mod-related sections (lines 40-60, 155-225); testing-plugins/SKILL.md, references/{eval-policy,mcp-live-checks}.md; release-and-versioning/SKILL.md; plugin-hooks-guidance/SKILL.md.
- Scanned by grep for audit topics only: README-template.md outside the sections above; building-plugins assets/LICENSE-template and scripts/*.py; testing-plugins references/troubleshooting.md, assets/evals-ci.yml, scripts/changed-eval-plugins.sh; release-and-versioning scripts/*.py; plugin-categories/SKILL.md and scripts/check-catalog-categories.py; plugin-renames-and-removals/SKILL.md and scripts/*.py; maintaining-user-docs/SKILL.md, references/root-readme.md, assets/root-readme-template.md.
- Not opened: pyrightconfig.json (config only).


## Records and memory (memory, ADRs, debt, specs, handoff)

FINDINGS: 12

- id: R-1
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/memory/tests-are-maintainer-tooling.md:3, :11, :15
- quote: (3) `"... so never judge them by the user's Claude Code version and never let their files live in a plugin's folder"`; (11) `Tests, evals, type checks (`mod-tsc`, `claude plugin test`) and the files they need (`.claude-plugin/types/`, a mod's `tsconfig.json`) exist only for the maintainer`; (15) `Any maintainer artifact found under `plugins/<plugin>/` is a scope leak: report it and propose moving it to maintainer scope.`
- conflicts with: F7.1, F7.2, D6 (as amended: `--eval-dir` is a directory below the plugin), §10.6, F5.3, F8.3
- why: Mod tests must officially stay inside the mod folder, and eval suites cannot leave the plugin directory either, so "never let their files live in a plugin's folder" and "scope leak" direct Claude to propose impossible moves; it also calls `claude plugin test` a type check and lumps the git-ignored (never shipped) `.claude-plugin/types/` with committed files.
- severity: high
- proposed action: edit memory. Description (line 3): `"Tests, evals, validation and type checks are maintainer tooling; a user only runs the installed plugin, so judge them only on the maintainer's build. Users' compatibility is the README's declared minimum"`. Line 11: `Tests (`claude plugin test`), evals, `claude plugin validate` and type checks exist only for the maintainer to know a plugin works on his build before publishing. A user never runs them. Everything committed under `plugins/<plugin>/` ships to users as files; nothing git-ignored does (`.claude-plugin/types/` is git-ignored and never ships).` Line 15: `judge a test or gate only by what it tells the maintainer on his own build; users' versions belong to the README's declared minimum. A mod's `*.test.ts(x)` and a plugin's eval suite must stay inside the plugin directory (official constraint) and ship as inert files. Other committed maintainer-only files under `plugins/<plugin>/` that the official tools do not require there (a per-mod `tsconfig.json`) ship for nothing: report them and propose moving them to maintainer scope (a repository-level tsconfig).`

- id: R-2
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/memory/MEMORY.md:34
- quote: `- [Tests are maintainer tooling](tests-are-maintainer-tooling.md) — tests, evals, type checks and their files serve only the maintainer; users run the plugin, never its tests; maintainer files under plugins/ are a scope leak`
- conflicts with: F7.2, D6 (amended), §10.6
- why: The index hook repeats the "scope leak" claim, which every session loads and which marks officially required in-plugin tests and evals as leaks.
- severity: medium
- proposed action: edit the line to `- [Tests are maintainer tooling](tests-are-maintainer-tooling.md) — tests, evals, validation and type checks serve only the maintainer's build; users' compatibility is the README minimum; mod tests and eval suites must stay in the plugin folder`

- id: R-3
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/session-handoff/2026-10-29-1511.md:45
- quote: `Needs a durable fix (a setup step that copies or regenerates them, or `mod-tsc` failing with a clear message), proposed to Nery. First action: ask Nery which option he wants.`
- conflicts with: F8.1, F8.2, F8.3, F8.5, F8.7, §10.3, §10.4, §10.5
- why: Every option keeps a `mod-tsc` gate that depends on development-only engine declarations and per-mod tsconfig files; the audit shows those prove only against the build that wrote them, that `claude plugin validate` and `claude plugin test` already check mods against the installed engine without declarations, and that Anthropic uses one repository-level tsconfig and no per-mod tsconfig. The options miss the fix the audit points to.
- severity: high
- proposed action: in the next handoff, replace item 1's options with: `(a) drop `mod-tsc` from the pre-push gates, since `claude plugin validate` + `claude plugin test` check mods on the installed engine with no declarations; or (b) move the mods' type check to one maintainer-scope tsconfig outside `plugins/` (Anthropic's `mods/tsconfig.json` pattern, F8.7) and remove the per-mod `tsconfig.json` files through plugin PRs. Copying or regenerating `.claude-plugin/types/` in setup is rejected.` First action: ask Nery (a) or (b).

- id: R-4
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/session-handoff/2026-10-29-1511.md:47
- quote: `The mods' `.claude-plugin/types/` in the main checkout were written by Claude Code 2.1.310, and the CLI is 2.1.312: `mod-tsc` checks against stale declarations. First action: Nery opens an interactive `claude` session in the main checkout, then check line 1 of ...index.d.ts`.
- conflicts with: F8.5, §10.5, F6.9, F7.4
- why: It treats refreshed declarations as part of the release proof; once `mod-tsc` is retired or moved (R-3), stale declarations block nothing, since validate and test run the installed engine. The installed CLI is now 2.1.314, not 2.1.312.
- severity: medium
- proposed action: in the next handoff, fold into item 1 and drop as a separate item; if Nery picks (b), refreshing declarations becomes an editor-only step, not a tracked open item.

- id: R-5
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/session-handoff/2026-10-29-1511.md:42 and :98
- quote: (42) `In a fresh worktree, `git push` fails in the pre-push hook (`mod-tsc:*`) until it has the mods' `.claude-plugin/types/` folders (item 1).`; (98) `Learning: in a fresh worktree, `npm ci` plus `npm run setup` aren't enough to push: `mod-tsc` needs the mods' git-ignored `.claude-plugin/types/` (item 1).`
- conflicts with: F8.2, F8.3, §10.3
- why: Accurate as observation, but it frames the declarations as a push prerequisite, while the audit classes them as a development artifact for the developer's build; the lesson to carry is that the gate is the defect, not the setup.
- severity: low
- proposed action: in the next handoff reword line 98 to `Learning: `mod-tsc` depends on git-ignored engine declarations that only an interactive `--plugin-dir` session writes, so it cannot run in a fresh worktree or CI; see item 1 for retiring or moving it.`

- id: R-6
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/maintainer/technical-debt/pending-debt.md:101, :107, :117, :118
- quote: (101) `creates the `mod-tsc:<plugin>` gate for any plugin with a `tsconfig.json`, and nothing refreshes the engine's declarations before it runs.`; (107) `` `tsc` runs against declarations from an older build after an update.``; (117) `name `mod-tsc` for what it checks, and check the declarations' `// Written by Claude Code <version>.` header against `claude --version` before `tsc`.`; (118) `closes when a mod with no tests fails the gate, a test run with its summary removed fails it, and stale declarations are reported.`
- conflicts with: F8.4, F8.5, F8.7, §10.4, §10.5
- why: The `mod-tsc` third of DEBT-010 presumes per-mod tsconfig and engine declarations as a gate worth hardening; the audit makes it redundant with validate and test on the installed engine. The `mod-test` parts (keying on `modules`, lost pipe summary) stay valid.
- severity: medium
- proposed action: edit the debt (keep open). Delete the line 107 inference; replace line 117 with `- retire `mod-tsc` or move the mods' type check to one maintainer-scope tsconfig (decision in handoff item 1); no declarations-freshness check.`; change line 118 to `closes when a mod with no tests fails the gate and a test run with its summary removed fails it.` Keep line 101 as a confirmed fact until the gate changes.

- id: R-7
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/maintainer/decisions/ADR_2026-10-22_mod-guardrails-follow-engine-declarations.md:18, :23, :34, :47
- quote: (18) `They also say to trust the declarations the engine writes for the installed build over any page (Create a mod → Get type definitions for your version; Reference, opening note).`; (23) `The live official docs win over project text, and the docs name the installed declarations as the authority.`; (34) `because it follows the contract the docs designate`; (47) `planned stale-declarations gate and weekly mod check`
- conflicts with: F8.1, F8.5, F8.6, §10.5, F7.4, D1
- why: The docs say to trust the engine-written copy over the older GitHub copy (F8.6), not over the docs pages, and give declarations no role in loading or running a mod (F8.1). The chosen answer `{ decision: 'ask', reason }` is the documented one, but asserting the declaration-only `plugin` field, the README promise built on it and the "stale-declarations gate" mitigation rest on the misread authority. The 2.1.307 floor is a legitimate feature minimum (D1), but its justification should be `claude plugin test` on builds 2.1.306/2.1.307, not the declarations.
- severity: medium
- proposed action: supersede with a new ADR, e.g. `ADR_<date>_mod-guardrails-follow-the-documented-tool-check-answer`: the guard answers the documented `{ decision, reason }`; authority is the docs plus what `claude plugin test` and a `--debug-file` session show on the maintainer's installed build; engine declarations are an authoring aid only; the README's declared minimum (2.1.307, from the per-build test runs) is what speaks to users; the stale-declarations gate is dropped. Set `superseded-by` on the old ADR.

- id: R-8
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/maintainer/decisions/ADR_2026-10-27_biome-checks-every-tsconfig-with-auto-expand.md:16, :37
- quote: (16) `- the mods' `plugins/file-tree-pane/tsconfig.json`, `plugins/project-maintainer/tsconfig.json`, `plugins/tool-ledger/tsconfig.json` and `plugins/turn-meter/tsconfig.json`.`; (37) `**Exclude the plugin tsconfig files with a regular `!plugins/*/tsconfig.json`**: rejected, because four files would stay unchecked.`
- conflicts with: F8.4, F8.7, §10.4, F3.3
- why: It treats the per-mod root `tsconfig.json` files as legitimate plugin files to keep checked; the audit shows they are generated development files that ship to users for nothing, and Anthropic keeps none per mod. The core decision (Biome checks every tsconfig with `expand: "auto"`) still holds for the maintainer tsconfigs.
- severity: low
- proposed action: no supersede now. When the per-mod tsconfig files are removed (R-3 option b), the ADR recording that removal partly supersedes this one (scope narrows to the maintainer tsconfigs; the line 37 rationale lapses).

- id: R-9
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/maintainer/decisions/ADR_2026-10-21_ci-checks-maintainer-tooling-and-plugin-structure.md:40
- quote: `| Local only | The tests in `scripts/tests/<plugin>/` (Node, Python, `by_path.sh`), `claude plugin test`, the mods' `tsc`, and Biome, ShellCheck, shfmt, ruff, mypy, basedpyright and `tsc` on `plugins/` |`
- conflicts with: §10.4, §10.5, F8.7
- why: Records "the mods' `tsc`" (per-mod tsconfig plus engine declarations) as a standing local gate; the CI/local split itself is unaffected.
- severity: low
- proposed action: keep; the decision that retires or moves `mod-tsc` (R-3) names this ADR as partly superseded for that row only.

- id: R-10
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/maintainer/decisions/ADR_2026-10-26_maintainer-tools-cover-the-whole-repository.md:15
- quote: `` `tsc`, whose projects (`scripts/`, `.claude/hooks/`, each plugin) already cover every JavaScript and TypeScript file``
- conflicts with: F8.4, F8.7, §10.4
- why: Relies on a per-plugin tsc project for mods, which the audit classes as a generated file shipped for nothing.
- severity: low
- proposed action: no edit (settled record); cite it as affected in the ADR that decides R-3.

- id: R-11
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/maintainer/decisions/ADR_2026-10-21_remove-markdownlint.md:19
- quote: `and plugins are tested only through evals.`
- conflicts with: F5.1, F5.2, F7.1, §10.1
- why: Plugins are also checked by `claude plugin validate`, `--plugin-dir` live loads and, for mods, `claude plugin test`, which the project's gates run; the premise is factually wrong, though the decision (remove markdownlint) does not depend on it.
- severity: low
- proposed action: no supersede (decision stands); note only if the ADR is ever revisited.

- id: R-12
- file:line: /Users/forestalmt/Claude/repositories/the-claude-factory/.claude/maintainer/technical-debt/closed-debt.md:96
- quote: `The same docs say to trust the declarations the engine writes for the installed build over any page (Create a mod → Get type definitions for your version), and the 2.1.308 declarations pin `plugin` on a hook's `ask`, put it to a person and let no classifier's allow settle it.`
- conflicts with: F8.1, F8.6
- why: Same misread authority as R-7; as a closed entry it is history and governs nothing.
- severity: low
- proposed action: leave the closed entry unchanged; the correction lives in the ADR that supersedes R-7, which its "Superseded by" field can name once it exists.

Files read (in full or every relevant passage):
- `.claude/maintainer/audits/2026-10-29-plugins-and-mods-live-sources-audit.md` (full)
- `.claude/session-handoff/2026-10-29-1511.md` (full)
- `.claude/maintainer/technical-debt/pending-debt.md`: index; DEBT-010, 023, 028 in full; DEBT-016, 035, 037 relevant lines; others skimmed (not about mods, testing or types)
- `.claude/maintainer/technical-debt/closed-debt.md`: index; DEBT-005, 019, 004, 034, 032 relevant parts; others skimmed
- `.claude/maintainer/decisions/`: in full: mod-guardrails-follow-engine-declarations, building-mods-skill-holds-mod-authoring, mod-readmes-state-the-tested-claude-code-version, biome-checks-every-tsconfig-with-auto-expand. Keyword passages: ci-checks-maintainer-tooling-and-plugin-structure, maintainer-tools-cover-the-whole-repository, remove-markdownlint, mod-guardrails-fail-closed-for-records, mod-knowledge-in-a-path-scoped-rule (superseded), instruction-engineering-joins-the-marketplace (consistent with F5.3), plugins-ship-runtime-npm-dependencies-through-claude-code-install (consistent with F3.7), ci-installs-claude-code-from-signed-apt, maintainer-only-root-package-json, tsc-hook-policy-defaults-user-wins and tsc-decides-index-signature-keys-not-biome (TS LSP plugins and maintainer tsc, outside the audit), testing-plugins-owns-live-mcp-checks, workflow-is-a-stage-map, plugin-tooling-rule-folds-into-claude-md, scaffold-writes-identity-not-readme-content, maintainer-operating-model. All remaining ADRs keyword-swept and skimmed; none states a mod, test, type or manifest fact the audit contradicts (Python-floor ADRs concern Python, outside the audit).
- `.claude/memory/`: all 34 files plus MEMORY.md; read in full: tests-are-maintainer-tooling, guard-not-testable-here, no-tests-inside-skills, claude-code-builds-on-disk, plugins-are-for-third-parties, stage-external-plugin-files, claudeai-sync-warnings, collapsible-detail-is-fine, deferred-pretooluse-skill-reminder, no-gates-unless-asked, official-docs-over-project-rules, search-history-before-unverified, plugins-never-pre-approve-tools; the rest keyword-swept, no conflict.
- `.claude/specs/`: all 10 swept. model-trace-design (minimum v2.1.299 plus tested v2.1.312, consistent with D1); github-operations-0.5.0-design (`evals/` inside the plugin, required per amended D6, not reported); biome-config-corrections-and-strictness-design (lines 224, 757-761 describe the per-mod tsconfig state of the time; spec done; covered by R-8); plugin-docs-create-and-update-design (allows minimum and "Tested with", consistent); the rest do not touch mods or testing.


## Repository tooling, user docs and shipped files

FINDINGS: 13

- id: T-1
- file:line: plugins/file-tree-pane/tsconfig.json, plugins/macos-grep-guard/tsconfig.json, plugins/model-trace/tsconfig.json, plugins/project-maintainer/tsconfig.json, plugins/tool-ledger/tsconfig.json, plugins/turn-meter/tsconfig.json (all committed = shipped)
- quote: `"extends": "./.claude-plugin/types/tsconfig.json"` (plus `include` hooks/tests/types; two add `allowImportingTsExtensions`)
- conflicts with: F8.4, F8.3, F6.2, F6.3, F3.3, §10.4, §10.7
- why: Each is a generated development file that reaches every user's cache, where it extends `.claude-plugin/types/tsconfig.json`, which is git-ignored and never shipped; it is broken and useless there. The mod file table lists no tsconfig and Anthropic's mods carry none (F8.7).
- severity: medium
- scope: plugin (6 PRs + version bumps, or one batched release run)
- proposed correction: `git rm` all six; ship in each mod's next patch release with a CHANGELOG line "removed a development file shipped by mistake".

- id: T-2
- file:line: .gitignore (whole file; no entry for mod-root tsconfigs)
- quote: `# Plugin eval results` / `**/evals/results/` … (no `plugins/*/tsconfig.json`)
- conflicts with: F8.4, §10.4, §10.7
- why: An interactive `--plugin-dir` session writes a root tsconfig into any mod that lacks one; after T-1 the next dev session recreates it untracked and the next `git add` ships it again.
- severity: medium
- scope: maintainer
- proposed correction: Add `plugins/*/tsconfig.json` to .gitignore with a comment "written by Claude Code in dev sessions; never shipped (F8.4)". No non-mod plugin commits a tsconfig today, so the pattern is safe.

- id: T-3
- file:line: scripts/gates.mjs:518-530
- quote: `.filter((p) => existsSync(join(root, 'plugins', p, 'tsconfig.json')))` … `id: \`mod-tsc:${p}\``, `group: 'local'`, `args: ['-p', join('plugins', p, 'tsconfig.json'), '--noEmit']`
- conflicts with: §10.3, §10.4, §10.5, F8.5, F8.6, F6.9, F7.4
- why: The gate depends on the shipped per-mod tsconfig (T-1) and on a development artifact (`.claude-plugin/types/`) pinned to whatever build wrote it: on disk "Written by Claude Code 2.1.310" (2.1.312 for model-trace) while the installed build is 2.1.314. It blocks every push (Husky `npm run gates`) on a stale or missing artifact and proves nothing about any user's build; `mod-test` and `claude-validate:<p>` already check each mod against the installed engine without declarations.
- severity: high
- scope: maintainer
- proposed correction: Remove the `mod-tsc:*` gates. If a mod type check is still wanted as an editor aid, add one repository-level, non-blocking `scripts/tsconfig.mods.json` shaped like F8.7 (`include` `plugins/*/hooks`, `plugins/*/tests`, `plugins/*/types`; `typeRoots` at the current build's declarations), kept out of `npm run gates` or skipped with a `skipReason` when the declarations are missing or their header ≠ `claude --version`.

- id: T-4
- file:line: scripts/gates.mjs:235-248 (`modTypesBlocker`), scripts/gates.mjs:89-90,667-670 (`blocker` property); scripts/testers/gates.test.mjs:17,75,244-249 (commit b7593ce)
- quote: `` `${types}/ is missing: run npm run setup, or open an interactive claude session with --plugin-dir plugins/${plugin}` ``
- conflicts with: §10.3, §10.5, F8.1, F8.2
- why: It turns a missing development artifact into a hard push failure; its only user is the mod-tsc gate, so it goes obsolete with T-3.
- severity: medium
- scope: maintainer
- proposed correction: Delete `modTypesBlocker` and its tests (gates.test.mjs:244-249); keep the generic `blocker` mechanism and its test (line 75) only if another gate uses it, else remove it too.

- id: T-5
- file:line: .claude/hooks/repo-setup.sh:23-41 and header lines 3-4 (commit a72f7ed)
- quote: `# Copy the missing ones from the main worktree, whose sessions write them.` … `rm -rf "${types}"` / `cp -R "${main_tree}/${types}" "${types}"`
- conflicts with: F8.5, F8.6, §10.3, §10.5
- why: It spreads declarations pinned to whatever build last wrote them in the main worktree (2.1.310/2.1.312) into new worktrees, to feed T-3, using `rm -rf`. The documented truth is "the copy Claude Code writes for your version", which a copy from another tree cannot be.
- severity: medium
- scope: maintainer
- proposed correction: Remove the whole "== mod types" step and its wording in the header comment. When declarations are needed for editing, the developer opens `claude --plugin-dir plugins/<mod>` in that worktree, which writes them for the current build (F8.1, F8.2).

- id: T-6
- file:line: scripts/gates.mjs:12-15
- quote: `The plugins' behavior (the tests in scripts/testers/<plugin>/, claude plugin test, the mods' tsc) and the static analysis of plugin code run only here, before the push, because they depend on the interpreter and the tools of whoever installs the plugin.`
- conflicts with: §10.1, §10.2, F7.4, F8.5
- why: `claude plugin test` and the mods' tsc reflect only the maintainer's installed build and its declarations, never the installer's interpreter or tools; user compatibility comes from the README minimum.
- severity: low
- scope: maintainer
- proposed correction: Reword: these gates run locally because they need the maintainer's installed Claude Code and tools, and they judge only that build. Drop "the mods' tsc" after T-3.

- id: T-7
- file:line: package.json scripts `typecheck`, `typecheck:ts`
- quote: `"typecheck": "node scripts/gates.mjs --only tsc-,mod-tsc:,basedpyright-"`, `"typecheck:ts": "node scripts/gates.mjs --only tsc-,mod-tsc:"`
- conflicts with: §10.5 (follows T-3)
- why: `selectGates` throws on a selector that matches no gate, so removing the mod-tsc gates breaks both scripts.
- severity: low
- scope: maintainer
- proposed correction: Drop `mod-tsc:` from both selectors in the same commit as T-3.

- id: T-8
- file:line: biome.jsonc:366-371
- quote: `// No script writes a tsconfig, so "always" has no reason here, and "auto" checks every tsconfig without reformatting the plugins' ones:` / `"**/tsconfig.json"`
- conflicts with: F8.4, §10.4
- why: The premise assumes committed plugin tsconfigs and that nothing writes a tsconfig; Claude Code does write one at a mod's root. After T-1/T-2, "the plugins' ones" are git-ignored generated files.
- severity: low
- scope: maintainer
- proposed correction: Reword to "Claude Code writes a git-ignored tsconfig at a mod's root in dev sessions; vcs.useIgnoreFile keeps Biome off it", and re-check ADR_2026-10-27_biome-checks-every-tsconfig-with-auto-expand for the stale premise.

- id: T-9
- file:line: scripts/check-repo.mjs:552-570 (`pluginProblems`) and :27-33 (portability rules)
- quote: `...manifestProblems(manifest), ...configFileProblems(dir), ...readmeProblems, ...changelogProblems, ...surfaceProblems`
- conflicts with: §10.7, F3.3, F8.3, F8.4
- why: No policy check rejects committed maintainer-only files under `plugins/<plugin>/` (a mod-root `tsconfig.json`, anything under `.claude-plugin/types/`, `evals/results/`); that gap is how T-1 shipped.
- severity: medium
- scope: maintainer
- proposed correction: Add `shippedArtifactProblems(name)` to check-repo over `git ls-files plugins/<name>`: fail on a root `tsconfig.json`, any path under `.claude-plugin/` other than `plugin.json`, and `evals/results/**`. Leave `*.test.ts(x)`, `tests/**`, `evals/**` suites and `types/index.d.ts` alone (official or required: F6.2, F7.2, D6). Test it in scripts/testers/.

- id: T-10
- file:line: plugins/project-maintainer/evals/** (34 files incl. `fixture.sh`, `case.yaml`, graders) and plugins/skill-diagnostics/evals/** (44 files)
- quote: role: eval suites (maintainer-only), committed in the plugin's `evals/` directory
- conflicts with: F5.3, D6 (as amended), §10.1, §10.7
- why: Both suites reach every user's cache as inert files, runnable `fixture.sh` scripts included, and never run there. Per the amended D6 (`claude plugin eval --help` on 2.1.314: `--eval-dir` is a "Directory name (below the plugin)"), suites cannot move outside the plugin, so like mod tests they are an official constraint, not a defect to fix by relocation.
- severity: low
- scope: plugin (only if suites change; PR + version bump per plugin)
- proposed correction: Keep the suites in place and record the decision (ADR) that eval suites ship as inert files because the tool requires them below the plugin. Keep `**/evals/results/` git-ignored (already). Make sure no README or skill tells users to run them, and that T-9's check exempts `evals/**` except `results/`. Update any project skill or doc that proposes moving suites outside the plugin.

- id: T-11
- file:line: docs/installation.md:14; README.md:47; docs/compatibility.md:17 (mirrored at README.md:235)
- quote: `| A recent Claude Code version | Run claude --version. One-step installs need v2.1.292+ in the shell and v2.1.275+ in a session. |`; `Keep Claude Code current`; mods row `✅ every Claude Code session except a Desktop session on WSL`
- conflicts with: §10.2, D1, F6.7
- why: The user docs never say that each plugin's README declares its own minimum Claude Code version, which §10.2 makes the only compatibility source. The mods row also leaves out the mods floor (terminal 2.1.287, Desktop 2.1.286) and that drawing appears only in the terminal, Desktop and VS Code (extension 2.1.299+, or 2.1.304+ without feature flags), never in `-p` or cloud sessions.
- severity: low
- scope: maintainer
- proposed correction: installation.md row → "The minimum version in the plugin's README (Requirements); one-step installs need …". In compatibility.md, add a note under the mods row: "mods need v2.1.287+ (Desktop v2.1.286+); panels and bands draw only in the terminal, Desktop and VS Code". Mirror it in README "Where plugins work" as .claude/rules/readme-md.md requires.

- id: T-12
- file:line: plugins/turn-meter/README.md:261
- quote: `The band draws in the terminal and the desktop app's **Code** tab. The VS Code extension does not draw it yet: there the mod still counts and alerts, and /turn-meter still works.`
- conflicts with: F6.7
- why: F6.7 says drawing appears in VS Code with extension 2.1.299+ (2.1.304+ without feature flags), and tool-ledger and model-trace state that. The audit does not settle whether bands, as opposed to panes and panels, are excluded there, so this text may be stale.
- severity: low
- scope: plugin (README only: signed commit to main, no PR or bump)
- proposed correction: Check against the live mods docs and release notes 2.1.299–2.1.314 whether bands draw in VS Code. If they do, rewrite the sentence in the tool-ledger form with the extension floors; if not, cite the source.

- id: T-13
- file:line: .github/workflows/release.yml:3-5,38-48
- quote: `Tags follow claude plugin tag: {name}--v{version}` … `gh release create "${tag}" --target "${TARGET_SHA}"`
- conflicts with: F3.6
- why: The tag format matches, but tags are made by `gh release create` instead of `claude plugin tag`, skipping its checks: validate, `plugin.json` matching the marketplace entry, clean tree, refusal of an existing tag. Validate covers part of this, but not the version agreement at tag time.
- severity: low
- scope: maintainer
- proposed correction: Keep the unsigned-tag exemption. In the release job, install Claude Code (as validate.yml does) and run `claude plugin tag plugins/<p>` (or its check-only mode, if `--help` shows one) before `gh release create`, or document why the gh path is equivalent.

Shipped files that do not conflict:
- Must stay (F7.2, §10.6): every `plugins/<mod>/tests/*.test.ts(x)` and the helper `plugins/project-maintainer/tests/fixtures.ts` (Anthropic's `tests/fixtures/` pattern).
- Must stay (amended D6): the `evals/` suites (see T-10).
- Required contracts, not artifacts (F6.2): `plugins/{file-tree-pane,model-trace,tool-ledger,turn-meter}/types/index.d.ts`.
- Mod version floors are all at or above D1/F6.7 and consistent with the features used:
  - file-tree-pane and model-trace declare 2.1.299, with VS Code 2.1.299/2.1.304 stated.
  - tool-ledger and turn-meter declare 2.1.295 and set a `types` key.
  - macos-grep-guard declares 2.1.287 (Desktop 2.1.286); it has no `types` key, no `$.state`, and no `$` passed to imported helpers (D4).
  - project-maintainer declares 2.1.307.
- plugin.json fields are all within F4.2.
- `version` is set only in plugin.json, never in marketplace entries (F3.5).

Files read:
- .claude/maintainer/audits/2026-10-29-plugins-and-mods-live-sources-audit.md
- scripts/gates.mjs
- .claude/hooks/repo-setup.sh
- scripts/check-repo.mjs (portability block, manifestProblems, configFileProblems, pluginProblems)
- scripts/validators/plugin-required-files.py (head)
- scripts/validators/skill-references.py (40-70)
- scripts/validators/readme-catalog-consistency.py (grep)
- scripts/tsconfig.json, scripts/tsconfig.plugins.json, tsconfig.base.json
- biome.jsonc (grep), package.json, .gitignore
- .github/workflows/release.yml
- .github/workflows/validate.yml (grep), claude.yml and claude-code-review.yml (grep)
- scripts/testers/gates.test.mjs (grep)
- git show a72f7ed, git show --stat b7593ce
- README.md (30-50, 225-245, grep)
- docs/compatibility.md
- docs/installation.md (8-18, grep)
- docs/faq.md, docs/managing-plugins.md, docs/troubleshooting.md (grep)
- CONTRIBUTING.md, SECURITY.md, SUPPORT.md (grep)
- the six mods' plugin.json and tsconfig.json
- plugins/project-maintainer/hooks/hooks.json
- the mods' .claude-plugin/types/ (listing, tsconfig.json, .gitignore, d.ts headers)
- plugins/tool-ledger/types/index.d.ts (head)
- plugins/turn-meter/hooks/register.tsx (120-160)
- the mods' README version and surface lines (grep)
- .claude-plugin/marketplace.json
- git ls-files plugins


## Published plugin content

FINDINGS: 11 open (12 raised; P-8 resolved)

- id: P-1
- plugin@version, file:line: mods-engineering@0.1.1, plugins/mods-engineering/skills/cc-mods-guidance/SKILL.md:439-452
- quote: "For distribution tasks:\n- Develop against source, not an installed cache.\n- Verify manifest identity and version.\n- Record the actual tested Claude Code version and surfaces. ..."
- conflicts with: F3.3, F8.3, F8.4, §10.3, §10.4, §10.7
- why: The distribution section never says that everything committed under the plugin directory reaches every user's cache and nothing git-ignored does. It also never says that the generated root `tsconfig.json` and `.claude-plugin/types/` are development artifacts that must not be committed. A user who follows the skill would publish a `tsconfig.json` that extends a file their users never have.
- severity: medium
- proposed correction: add bullets: "- Everything committed under the plugin directory reaches every user's cached copy; git-ignored files never do. - Keep `.claude-plugin/types/` git-ignored (Claude Code writes it with a `.gitignore` of `*`); never commit it. - The root `tsconfig.json` Claude Code adds when the mod has none extends those generated files: it is a development file, so don't commit it into a published plugin (type-check from a tsconfig outside the plugin directory instead)."

- id: P-2
- plugin@version, file:line: mods-engineering@0.1.1, plugins/mods-engineering/skills/cc-mods-guidance/SKILL.md:445
- quote: "- Record the actual tested Claude Code version and surfaces."
- conflicts with: D1, F6.7, §10.2
- why: A user's compatibility comes from the minimum Claude Code version the README declares: the mods floor (2.1.287 terminal, 2.1.286 Desktop) plus the gate of each feature used. The version the author tested on is not that minimum. Recording only the tested version leaves the floor undeclared or inflates it.
- severity: medium
- proposed correction: "- Declare the minimum Claude Code version in the README: the mods floor (v2.1.287 terminal, v2.1.286 Desktop) raised by every feature the mod uses (for example v2.1.299 to leave `types` out of the manifest, VS Code drawing v2.1.299, or v2.1.304 where feature flags aren't fetched). Record separately the version and surfaces you tested on."

- id: P-3
- plugin@version, file:line: mods-engineering@0.1.1, plugins/mods-engineering/skills/cc-mods-guidance/SKILL.md:83-85
- quote: "If declarations are absent, follow the creation guide's documented workflow for generating them. Loading a mod runs code: obtain authorization before loading an unreviewed mod."
- conflicts with: F8.1, F8.2, D5
- why: It doesn't say which sessions write the declarations. Since 2.1.295 only an interactive `--plugin-dir` session, or a mod Claude wrote, writes them. `-p`, the SDK, `claude plugin test` and `claude plugin validate` write nothing, so Claude may try to generate them a way that never produces them.
- severity: low
- proposed correction: "If declarations are absent, generate them as the creation guide documents: load the mod from `--plugin-dir` in an interactive session (or have Claude write the mod). `-p`, SDK sessions, `claude plugin test` and `claude plugin validate` don't write them. Loading a mod runs code: obtain authorization before loading an unreviewed mod."

- id: P-4
- plugin@version, file:line: mods-engineering@0.1.1, plugins/mods-engineering/skills/cc-mods-guidance/SKILL.md:406-408
- quote: "Use the repository's existing type-checking workflow against generated declarations when available. Do not install a compiler merely to make an unverified command work."
- conflicts with: F8.5, F6.9, F7.4, F6.3, §10.5
- why: It doesn't say that a type check proves something only against the build that wrote the declarations, while validate and test check against the installed engine. It also doesn't say that end users need no TypeScript (F6.3). Without that, a clean type check can be reported as proof of compatibility.
- severity: low
- proposed correction: append: "A type check proves the mod only against the build that wrote the declarations; `claude plugin validate` and `claude plugin test` check it against the installed engine. Neither says anything about other users' builds: that is what the README's declared minimum version is for. Users who install the mod need no TypeScript or tsconfig."

- id: P-5
- plugin@version, file:line: mods-engineering@0.1.1, plugins/mods-engineering/README.md:30
- quote: "Claude checks each event, `$` method and element against the declarations your build writes into `.claude-plugin/types/` and the official mod pages"
- conflicts with: F8.2, D5
- why: Unqualified, it implies any build writes the declarations whenever it loads a mod, which is exactly the D5 error. Line 233 of the same README states it correctly.
- severity: low
- proposed correction: "...against the declarations Claude Code writes into `.claude-plugin/types/` when you load the mod from `--plugin-dir` in an interactive session (or when Claude writes it for you), and the official mod pages..."

- id: P-6
- plugin@version, file:line: mods-engineering@0.1.1, plugins/mods-engineering/README.md:205
- quote: "Mods run in Claude Code, v2.1.287 or later."
- conflicts with: F6.7, D1
- why: It omits the Desktop floor (2.1.286) and never says that some features have their own minimum, higher than the floor.
- severity: low
- proposed correction: "Mods run in Claude Code v2.1.287 or later in the terminal and v2.1.286 or later in the Desktop app; some features need newer builds (for example drawing in VS Code: extension v2.1.299+, or v2.1.304+ where feature flags aren't fetched)."

- id: P-7
- plugin@version, file:line: plugin-evals@0.1.2, plugins/plugin-evals/skills/plugin-evals/SKILL.md:59; references/fixtures-and-mocks.md:97; references/case-format.md:22-31 (layout)
- quote: "Ship everything a case needs in the plugin." / "Commit `mocks/.replay/` so CI is repeatable."
- conflicts with: F3.3, F5.3, D6 (amended), §10.1, §10.7
- why: The skill teaches committing suites, fixtures and mock replays inside the plugin. It never says that all of it reaches every user's cache as inert files. `--eval-dir` only takes a directory below the plugin, so a suite always ships, and an author publishing to a public marketplace has to know that.
- severity: medium
- proposed correction: add to SKILL.md §4 Gotchas: "**A committed suite ships.** The eval directory is always below the plugin root, so everything committed there, fixtures and `mocks/.replay/` included, is copied into every user's plugin cache when they install from a marketplace. It never runs there, but it is downloaded: keep secrets, credentials and private data out of prompts, fixtures, transcripts and mocks."

- id: P-8 (RESOLVED, no change to the plugin)
- plugin@version, file:line: plugin-evals@0.1.2, plugins/plugin-evals/skills/plugin-evals/references/case-format.md:35
- quote: "Use plain relative directory names only. An absolute path or `..` is an error as a flag; as a manifest value it prints a `Warning:` and the run falls back to `evals/`."
- conflicts with: none (D6 was wrong and is amended)
- why: Verified by team-lead: on 2.1.314, `claude plugin eval --help` describes `--eval-dir` as "Directory name (below the plugin)". The plugin text is consistent with the binary.
- severity: n/a
- proposed correction: none.

- id: P-9
- plugin@version, file:line: plugin-evals@0.1.2, plugins/plugin-evals/skills/plugin-evals/references/running-and-ci.md:21
- quote: "**A plugin.** Either a directory with `plugin.json` or `.claude-plugin/plugin.json`, or a skills-directory plugin."
- conflicts with: F4.1
- why: Per F4.1 the manifest goes at `.claude-plugin/plugin.json`, and without one the components are found from the layout. A root `plugin.json` is not listed as a valid location, and the sentence can lead an author to put it there.
- severity: low
- proposed correction: if the plugin-evals docs don't explicitly state root `plugin.json`: "**A plugin.** A directory with `.claude-plugin/plugin.json` (the manifest is optional; without it, components are found by the standard layout), or a skills-directory plugin." If they do state it, add the docs quote to sources.md.

- id: P-10
- plugin@version, file:line: hook-engineering@0.2.1, plugins/hook-engineering/skills/hook-development/references/events-session.md:87
- quote: "the type declarations for mods that Claude Code v2.1.305 writes (its built-in `plugin-authoring` skill's `types/claude-code.d.ts`, `ClassicResultFields`) list it as a field Setup reads"
- conflicts with: F8.1, F8.5, F8.6
- why: The declarations a build writes go into the mod's `.claude-plugin/types/` (for example `claude-code/index.d.ts`). `types/claude-code.d.ts` is the layout of the GitHub copy, which is older (2.1.277, F8.6). Attributing the evidence to that path blurs which copy was read.
- severity: low
- proposed correction: "the type declarations Claude Code v2.1.305 writes into a mod's `.claude-plugin/types/` (`claude-code/index.d.ts`, `ClassicResultFields`) list it as a field Setup reads" (if the source really was the built-in skill's bundled file, name its exact path and build instead).

- id: P-11
- plugin@version, file:line: project-maintainer@0.2.3, plugins/project-maintainer/tsconfig.json:2
- quote: "\"extends\": \"./.claude-plugin/types/tsconfig.json\","
- conflicts with: F8.3, F8.4, §10.4, §10.7
- why: This root `tsconfig.json` is git-tracked and reaches every user, but it extends a git-ignored file no user has. It has no runtime role: a development file shipped for nothing.
- severity: medium
- proposed correction: untrack `plugins/project-maintainer/tsconfig.json`, either by git-ignoring it or by moving the type-check config to a maintainer-scope tsconfig outside `plugins/`, the way Anthropic keeps one repository-level `mods/tsconfig.json` (F8.7). It ships through a PR plus a version bump, per CLAUDE.md.

- id: P-12
- plugin@version, file:line: model-trace@0.1.1, tool-ledger@0.1.2, file-tree-pane@0.1.3, macos-grep-guard@0.1.0, turn-meter@0.1.2: plugins/<each>/tsconfig.json (extends line)
- quote: "\"extends\": \"./.claude-plugin/types/tsconfig.json\"" (identical in all five, all git-tracked)
- conflicts with: F8.3, F8.4, §10.4, §10.7
- why: The same defect as P-11 in the other five published mods: a committed development file that ships to users and points to a file that doesn't exist in their copy.
- severity: medium
- proposed correction: same as P-11, for each plugin, in one coordinated change to a maintainer-scope tsconfig.

Note on P-11/P-12: these are shipped files, not teaching content. I include them because the brief's `rg` surfaced them and their effect reaches third parties. `project-maintainer/evals/` also ships; it is inert and covered by D6 as amended (a suite can't sit outside the plugin), so it isn't counted separately. Its `tests/` must stay inside the plugin (§10.6).

## Verified, no conflict

- hook-engineering `references/mods-and-hooks.md`: the mods floors (2.1.287 terminal, 2.1.286 Desktop), the `modules` definition and validate's `hooks:`/`calls:` lines match the audit. Nothing relies on validate's notes about where hooks run (D3).
- hook-engineering `locations-and-scope.md`, `debugging.md`, `audit-checklist.md`, `sources.md` (plugin and mod parts): consistent.
- plugin-test-bench `test-install/SKILL.md:19`: copy-to-cache rule consistent with F3.2/F3.3.
- mods-engineering `SKILL.md:381` ("Verify helper-function and import restrictions"): consistent with D4.
- plugin-evals `case-format.md:31` (results/ to .gitignore), `running-and-ci.md:37` (cache copy), `--disallow-tools` v2.1.299 and the API-error exit 1: consistent with F5.3 and the release notes.
- Mod READMEs: the declared minimums are consistent with each mod's `types` key and `$.state` use. tool-ledger and turn-meter declare `types` and require ≥2.1.295; model-trace and file-tree-pane require ≥2.1.299; macos-grep-guard requires 2.1.287 (2.1.286 Desktop); project-maintainer requires 2.1.307 and uses no `$.state`. The VS Code gates (2.1.299/2.1.304) are stated correctly.
- D2 (`/plugin-types`): no plugin mentions it.

## Files read

- mods-engineering: `.claude-plugin/plugin.json`, `skills/cc-mods-guidance/SKILL.md` (full), `README.md` (full)
- plugin-evals: `.claude-plugin/plugin.json`, `README.md` (full), `skills/plugin-evals/SKILL.md` (full), `references/running-and-ci.md` (full); targeted grep of `references/case-format.md`, `fixtures-and-mocks.md`, `results.md`, `other-formats.md`, `sources.md`
- hook-engineering: `.claude-plugin/plugin.json`, `references/mods-and-hooks.md` (full); grep of the plugin, mod and testing lines in `SKILL.md`, `agents/hook-engineer.md`, `README.md`, `locations-and-scope.md`, `debugging.md`, `audit-checklist.md`, `security-and-trust.md`, `docs-map.md`, `sources.md`, `lifecycle.md`, `handler-fields.md`, `matchers-and-if.md`, `prompt-and-agent-hooks.md`, `events-session.md`
- project-maintainer: `.claude-plugin/plugin.json`, `tsconfig.json`, `git ls-files` listing, grep of `README.md` and `skills/`
- Other `rg` hits: `plugin-test-bench/skills/test-install/SKILL.md`, `plugin-test-bench/skills/review-evals/SKILL.md`, `skill-diagnostics/skills/audit/SKILL.md`, `references/surfaces.md`, `executability.md`, `fallbacks.md`; `tsconfig.json` and `plugin.json` of model-trace, tool-ledger, file-tree-pane, turn-meter, macos-grep-guard; grep of the READMEs of those mods, block-no-verify and plugin-test-bench

Coverage limit: in hook-engineering I read only the parts in scope (plugins, mods, testing), not the full event references.


## Reconciliation

Every finding's final state. Commits are on `main`.

| Findings | State | Where |
| :-- | :-- | :-- |
| I-1 to I-14 | Fixed | `a736011` (CLAUDE.md, rules). I-5's eval-suite proposal was superseded by the amended D6: suites stay below the plugin |
| I-15 | No change | The anchor `components#path-variables-and-persistent-data` exists; the docs link it |
| S-1 to S-15 | Fixed | `2cec0ef`; the lines were then rewritten as single instructions in `67c3124` |
| R-1, R-2 | Fixed | Memory `tests-are-maintainer-tooling` and `MEMORY.md` (git-ignored) |
| R-3 to R-5 | Resolved | The handoff's items 1 and 3 no longer apply: `mod-tsc` is removed (`4a7e467`). The next handoff drops them |
| R-6 | Fixed | DEBT-010 in `245ff8c` |
| R-7 | Retracted | The docs say to trust the declarations over any page; the ADR stands (`75c284d`) |
| R-8, R-9 | Superseded in part | Named in ADR_2026-10-29_mods-commit-no-tsconfig and ADR_2026-10-29_remove-the-mod-tsc-gate |
| R-10 to R-12 | No change | Settled or closed records; their decisions do not depend on the contradicted fact |
| T-1, T-2 | Fixed | `e96c0c9`, `9cd3042` |
| T-3 to T-7 | Fixed | `4a7e467` |
| T-8, T-9 | Fixed | `9cd3042` |
| T-10 | Fixed | ADR_2026-10-29_in-plugin-maintainer-files-take-a-pull-request-without-a-bump; suites stay and ship inert |
| T-11 | Fixed | `aa0db14` |
| T-12 | No change | The render-sites table draws the band only in the terminal and Desktop; turn-meter's README is right |
| T-13 | No change | ADR_2026-10-25_release-tags-are-created-unsigned-by-ci already rejected `claude plugin tag` in `release.yml`, with its revisit trigger |
| P-1 to P-7, P-10 | Fixed | `015b3d1` (released in PR #73), then rewritten as single instructions in PR #74 |
| P-8 | Resolved | The audit was wrong; `--eval-dir` is a directory below the plugin |
| P-9 | No change | The plugin-evals docs accept a root `plugin.json` |
| P-11, P-12 | Fixed | `e96c0c9` |

Follow-up beyond the findings: the skill lines written during this refactor were checked against the skill-writing rules and rewritten (PR #74, `67c3124`), and `testing-mods/references/version-drift.md` became a list of measured traps with no copied versions.
