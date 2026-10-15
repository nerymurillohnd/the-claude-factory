# Phase 8: Audit planning (steps)

1. Group the sources by domain. The domains are fixed by file type, and each source keeps its own:
   - A. Codex instruction files, including every `AGENTS.md` even when Claude Code also reads it.
   - B. Claude project, local, ancestor, and global instruction files.
   - C. Claude rule files and their activation and scoping metadata.
   - D. Memory sources.
   - E. Instruction-bearing Markdown extensions: subagent definitions, output styles, and `loop.md`.

   The managed-policy `CLAUDE.md` and the sources that configuration excludes are not assigned to anyone. A pointed-to file takes its domain by the rule in the Scope section of SKILL.md.
2. Use one coordinator and the smallest useful set of independently scoped reviewers. A package may hold sources of several domains, so merge small domains into one package; partition large ones by disjoint file sets. Create no empty packages.
3. Give every audited source exactly one primary reviewer.
4. Split the packages into bounded sizes, keeping each file complete inside a single package. Size them for the context window of the pinned reviewer model (see Limits to declare).
5. Split each file into explicit, contiguous numbered reading ranges.
6. Give each package its candidates, the mechanical findings it must not repeat, and the masked copy of the managed-policy `CLAUDE.md` as an evidence-only source.

If native subagents are unavailable, perform the same bounded passes sequentially and report the limitation. Do not fabricate delegation or peer review.
