# Phase 2: Baseline snapshot (steps)

1. Record the git HEAD and the working-tree state, when git is available.
2. Record the start time.
3. Record the installed runtime names and versions, the relevant instruction-discovery configuration, and the approved global, user, and managed source boundaries.
4. Record every symlink inside the approved boundaries, directory links included, with its target. List them with `find <boundary> -type l`, read each target with `ls -ld`, and resolve a chain with `realpath` where it exists. `evidence-collector` has no tool that reads a link, so this table is its only source for symlinks and canonical paths.
