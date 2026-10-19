# Svelte language server troubleshooting

> Precedence: the language-tools changelogs and the Claude Code docs win over this file.

## Contents

- [The LSP tool returns an error](#the-lsp-tool-returns-an-error)
- [No diagnostics appear after an edit](#no-diagnostics-appear-after-an-edit)
- [Results are empty or wrong](#results-are-empty-or-wrong)
- [False errors about generated types](#false-errors-about-generated-types)
- [Known open issues](#known-open-issues)
- [Official sources](#official-sources)

## The LSP tool returns an error

Claude Code returns an error for each LSP call on a file whose server it cannot start. Check, in this order:

1. **Binary.** The error names it (`Executable not found in $PATH: "svelteserver"`). The user can confirm it in the shell they start `claude` from, which is where Claude Code takes the server's `PATH`. Give them this command to run in their own terminal; do not run it with the Bash tool, whose result proves nothing about the server:

   ```sh
   # for the user, in the terminal they start claude from
   command -v svelteserver || echo "svelteserver not found"
   ```

   Missing means the user installs it globally with `npm install -g svelte-language-server`; in `/plugin`, the **Errors** tab shows `Executable not found in $PATH: "svelteserver"`. Tell the user; do not install packages without their confirmation.
2. **File type**: the plugin maps only `.svelte`. A `.ts`, `.js`, `.svelte.ts` or `.svelte.js` file needs a TypeScript language server the user installed separately.
3. **Session type**: cloud sessions never start plugin language servers. Use the project check (`npm run check`) there.
4. **Reload**: after installing the binary, the user runs `/reload-plugins`. When adding the LSP tool would invalidate the prompt cache, Claude Code holds the reload and prints a line that ends `Run /reload-plugins --force to apply.`; the user runs that to apply it.

## No diagnostics appear after an edit

- If nothing appears even after a change that must break, first prove the language server answers: `documentSymbol` on a non-empty `.svelte` file must list its symbols. If the project check is the silent one, follow rule 9 of the skill.
- The server starts on the first LSP call or the first edit of a `.svelte` file, not at session start, and its first answer can come late.
- Diagnostics after an edit appear as `Found N new diagnostic issues in M files`; only new issues are reported, so an unchanged error does not repeat.
- `claude --debug` logs `LSP server <name> failed to start: <reason>` when the server crashes at start.

## Results are empty or wrong

- Wrong position: positions are 1-based; place the position on the first character of the name. Use `documentSymbol` to get the line, then read that line for the column.
- Empty `workspaceSymbol`: the `query` was empty or too short.
- Results that ignore the project's configuration, in a SvelteKit 3 project or in a worktree under `.claude/worktrees/`: the server is older than 0.18.5 (0.18.4 reads SvelteKit 3's config from `vite.config`; 0.18.5 finds config under dot directories). The user checks the version in their own terminal with `npm ls -g svelte-language-server` and updates it.
- Stale results after moving, creating or deleting route files: a known server crash (see below). Ask the user to run `/reload-plugins`, then confirm with the project check (`npm run check`).
- Props typed `any` unexpectedly: if the component writes `$props<…>()` with type arguments, destructured props become `any` (known issue). Prefer `let { … }: Props = $props();`.

## False errors about generated types

`Cannot find module './$types'` or `Cannot find type definition file for '$app/types'` means SvelteKit's generated files are missing. Generate them before trusting diagnostics (the project's `check` script also runs this):

```sh
npx --no-install svelte-kit sync
```

Since SvelteKit 3 the generated tsconfig lives in `node_modules/$app/tsconfig`, so dependencies must be installed.

Types of an installed `@types/*` package missing (`Cannot find name 'process'`, an unknown global): a `types` array in the tsconfig, which `@tsconfig/svelte` and the Vite Svelte template set (`"types": ["svelte", "vite/client"]`), limits ambient types to the packages it lists. Tell the user to add the package to that array; do not remove the array.

## Known open issues

Issues and pending fixes in `sveltejs/language-tools`; check whether each is still open, or released, before citing it to the user:

| Issue | Symptom |
| --- | --- |
| #3108 | Server crashes or partly stops when route files are moved, created or deleted (SvelteKit 3) |
| #3080 | Reading the Svelte config from `vite.config.js/ts` can be wrong |
| #3124 | Type arguments on `$props()` make destructured props `any` |
| #3063 | TypeScript 7 crashes svelte2tsx and svelte-check; use `--tsgo` with TypeScript 7 and TypeScript 6 both installed, as the svelte-check README says |
| Unreleased fix | `svelte-check --tsgo` leaves out TypeScript files the tsconfig lists; a pending changeset (`.changeset/quick-dogs-appear.md` in the repository) fixes it. Check the svelte-check changelog for the release before trusting a `--tsgo` result |

Re-check an issue before citing it:

```sh
curl -sS 'https://api.github.com/repos/sveltejs/language-tools/issues/3108' | grep -m1 '"state"'
```

## Official sources

- Claude Code code intelligence and troubleshooting: https://code.claude.com/docs/en/plugins/code-intelligence and https://code.claude.com/docs/en/plugins/troubleshooting
- Language server changelog: `curl -sS https://raw.githubusercontent.com/sveltejs/language-tools/master/packages/language-server/CHANGELOG.md`
- svelte-check changelog: `curl -sS https://raw.githubusercontent.com/sveltejs/language-tools/master/packages/svelte-check/CHANGELOG.md`
- Releases: https://github.com/sveltejs/language-tools/releases
