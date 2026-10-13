# Python identity and change impact

## Aliases and public names

With `from library import target as local`, renaming the exported symbol can require changing its definition, import name, and registered entry-point strings while leaving `local(...)` untouched. Query both the definition and the alias to discover usage. If the task renames the alias itself, change its local calls as well. Distinguish the requested public name from every similarly spelled local variable.

Inspect `__all__`, package re-exports, decorators, public imports, declared entry points, and downstream consumers before removing a public symbol. A console-script entry point also has a calling convention: a registered function requiring arguments may expose a separate contract problem. Do not change that contract incidentally during a rename.

## Consumers outside ordinary static references

- pytest fixture parameters and decorator/registry names.
- `getattr`, computed imports, and string-based dispatch.
- package entry points, task names, serialized module paths, and patch targets.
- generated code and templates that name Python symbols.

These are candidate mechanisms to inspect, not an assertion that every server misses every such use. Search the bare name and qualified names in the relevant authorized source and metadata. An exact text hit is not always a use of the intended definition, and no text hit cannot rule out computed names.

## Workspace and freshness

Check the loaded workspace and configured project rather than equating scope with a remembered working directory. Files changed by command execution, generation, or code actions may be unsynchronized; inspect the current source and refresh through supported client operations. A same-sized reference list does not prove the index has the current content.

The first query can already be complete. Treat warm-up as a testable cause of a partial answer, not a mandatory ritual. After bounded retries, retain the actual coverage limit and continue with explicit source evidence.

## Safe edit scope

List definition, import sites, known consumers, metadata registrations, and unverified external uses. Use semantic identity to propose edits, review the diff, and test intended behavior. Explain public API compatibility decisions before removing old names. Preserve unrelated aliases and same-named symbols.
