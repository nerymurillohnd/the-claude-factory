# Phase 7: Mechanical checks (steps)

Every check here is a rule applied to the inventory and the files, with no reading judgment. Read text from the masked copies, so that no excerpt comes from an original; resolve paths and check that targets exist from the original locations. A threshold that the vendors document comes from the Phase 6 catalog, with its id. A threshold they do not document is chosen by you, approved at Gate 1, and stated in the report with its value and its reason. Whatever needs reading judgment goes to 7.4 as a candidate.

## 7.1 References

1. Imports whose target file does not exist.
2. Imports written inside quotes (they are not loaded).
3. Imports deeper than the documented maximum depth.
4. Links to local files that do not exist. Resolve each relative link from the folder of its own file, without rescuing it from the repository root.
5. Link anchors with no matching heading in the destination file.
6. Pointer edges that `evidence-collector` recorded as prose asking to read a file instead of importing or linking it.

## 7.2 Loading

1. Sources that are dead, shadowed, or truncated, with the exact line where the lost portion starts.
2. Rule frontmatter that cannot be parsed (the rule would then load always).
3. Rule frontmatter keys that Claude Code ignores.
4. Rules whose path patterns match no file.
5. Instruction files above the documented size limit, and `CLAUDE.md` files above the recommended length. When the loader cuts the file at that limit, the cut is item 1 (`dead`) and this item raises no second finding for the same size. A file above a recommended length that nothing cuts is `non-conformant`.
6. Instructions written inside an HTML comment (stripped before injection, so Claude never receives them), noting that comments inside code blocks are preserved.
7. Sources that configuration excludes from loading (for example by a `claudeMdExcludes` pattern). Record each as `not loaded` with the pattern that excludes it. The user chose the exclusion, so it raises no finding, and the source goes to no reviewer.

## 7.3 Duplicates

1. Split each file into units. A paragraph is consecutive lines outside a code fence, ended by a blank line, a heading, a list item, a table row, or a quotation. A list item is its marker line and its indented continuation lines, without its nested items, which are units of their own. A table row is one row, apart from the header and the separator. A quotation is consecutive lines that start with `>`. A fenced code block is one unit. Headings and frontmatter are not units (frontmatter is checked in 7.2). Keep the split, so findings and claims can be related to its units.
2. Find identical units after normalizing whitespace, list markers, letter case, and trailing punctuation. Only units of at least the chosen minimum length count here.
3. For each identical pair, decide from the inventory whether the two copies load into the same context, which means the same session: both always loaded, or one always loaded and the other conditional on path patterns that match. If the inventory does not settle it, send the pair to 7.4.
4. Copies in the same context are a `duplicated` finding. Propose keeping the shared copy and removing or merging the personal one. Where the copies sit in `AGENTS.md` and `CLAUDE.md`, propose importing `AGENTS.md` from `CLAUDE.md`, even though the two files load into different runtimes.
5. Copies in separate contexts are not a finding. Send the pair to 7.4.

## 7.4 Candidates for judgment

1. Mentioned paths that do not exist in the repository.
2. Mentioned package scripts and `make` or `just` targets that do not exist.
3. Mentioned commands of other ecosystems that do not match the evidence.
4. Instructions in an always-loaded file that name concrete paths (possible path-scoped rule).
5. Path-scoped rules whose content is unrelated to their paths (possible general instruction).
6. Memory entries shaped like team norms (possible `CLAUDE.md` content).
7. Pairs of similar instructions across different files.
8. Phrases repeated inside longer units, of at least the chosen phrase length.
9. Identical units shorter than the chosen minimum length that read as instructions.
10. Identical pairs in separate contexts, and pairs whose context the inventory does not settle.
