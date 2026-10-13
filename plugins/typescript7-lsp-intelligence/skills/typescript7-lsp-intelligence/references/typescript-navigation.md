# Symbol identity and consumer coverage

## Loaded projects

A language server can analyze configured projects, inferred projects, or only currently loaded portions of a workspace. A repeated definition-only reference response does not prove an exported symbol has no callers. Identify relevant package/program boundaries and query a representative source context for each implicated project. Keep retries bounded; do not open every file merely to make a count grow.

Inspect aliases and re-exports independently when the server does not traverse them. Review package `exports`, declaration entry points, public packages, tests, registries, generated consumers, and dynamic lookup names. Search these non-semantic surfaces after LSP discovery, then inspect candidate hits by identity. Textual equality is not a rename set.

Framework files need a client capable of their embedded language/template semantics. A TS-only response does not establish absence of a Svelte/Vue/other component consumer. Use a supported framework-aware client when available; otherwise inspect relevant files and disclose coverage. External consumers of a published API remain an explicit contract boundary.

## Moves and renames

Check the source snapshot, document identity, resolved config, and program membership after a move. A CLI that checked the old file and omitted the moved file cannot refute a current diagnostic in the moved file. Repair a demonstrated source error and establish the intended membership separately; do not call the finding phantom solely because the file moved.

Before changing an API name or signature, inspect definitions, references, implementations, and affected call sites. Preserve an intentional local import alias unless the requested rename includes it. Update explicitly authorized metadata paths and registrations as needed, then verify consumers under their actual programs.

## Calls and implementation

Call hierarchy supplements impact analysis; it does not guarantee every dynamic dispatch, callback, reflection path, or framework consumer is known. Use implementation links for interfaces/abstract methods when exposed, then inspect concrete implementations. Read overload signatures together with the implementation contract; a caller's inferred signature can differ from the body signature.

When a method is unsupported, use supported relationships and inspect the relevant function body. State material dynamic/unloaded coverage once, without turning every lookup into an exhaustive audit.
