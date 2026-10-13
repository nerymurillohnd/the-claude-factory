# Sourcing, identity, and dynamic calls

## Same-named functions

Two functions named `render` in unrelated scripts are not automatically one rename target. bash-language-server reference results can include both definitions and both call sets. Trace which definition each caller can reach through its direct/transitive source relationships, command lookup, and runtime context.

Do not discard a candidate merely because its file lacks a direct `source` statement: a parent can load a library before sourcing another file or invoking a function in the same shell. Dynamic source paths and indirect dispatch can also connect consumers. A separately executed child script normally does not inherit unexported parent functions; establish a real export/import or other connection before treating it as a caller. Resolve the relationship, then list confirmed edits and unresolved cases separately.

## Discovery limits

Discovery depends on configured roots, glob patterns, ignored/hidden paths, and what the client has opened. An extensionless executable may contain supported shell code even when the client has no extension mapping for it. Search/read those authorized candidates rather than claiming the server universally indexes or universally ignores them.

The initial query may already be complete. Stable repeated counts are not readiness or identity proof. Verify a known declaration and source snapshot; after bounded retries, report what remains unserved.

## Indirect consumers

- `trap` strings and deferred EXIT/signal invocations.
- function names stored in variables, arrays, aliases, or dispatch tables.
- `eval`, `bash -c`, `sh -c`, and generated command text.
- job definitions, CI, Makefiles, and command launch metadata.

Literal searching cannot exclude computed names. A trap call is a deferred invocation, not an ordinary immediate caller; retain that distinction in impact analysis. Public command names and external launchers may have consumers outside the repository.

For a rename, inspect the definition, source callers, dispatch paths, and metadata. Preserve unrelated definitions and behavior. Verify known launch modes, quoting, arguments, exit statuses, and cleanup paths after the change.
