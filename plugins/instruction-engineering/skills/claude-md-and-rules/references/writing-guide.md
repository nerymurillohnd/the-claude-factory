# Writing instructions that hold

Every line in an always-loaded file takes a little of Claude's attention on every task. Write fewer, sharper lines.

## Before adding anything: the pre-write protocol

Every addition, however small ("add this to CLAUDE.md", "add a rule for X", "remember that…"), goes through these steps. Appending without reading is how instruction sets accumulate duplicates and contradictions.

1. **Read the target file in full**, and every file that loads in the same situations: user CLAUDE.md and rules, the root file, CLAUDE.local.md, rules whose `paths` cover the area the new instruction is about (use `--match` on a representative file), nested CLAUDE.md files of that area, imports. Run the checker once for the inventory.
2. **Search by meaning, not by the user's words.** List the entities the instruction involves (tools, commands, paths, libraries, file types, the behavior itself) and their synonyms ("Vitest" / "unit tests" / "test runner"; "errors" / "HttpError" / "error envelope"; "don't edit" / "generated" / "read-only"). Grep for each across the comparison set and read every hit in context.
3. **Classify the relation** using the relation table in [cross-file-analysis.md](cross-file-analysis.md) (read it now if you have not in this session; it is short), and act on it:
   - **Already covered**: change nothing; tell the user where it already lives, and whether it loads when it needs to (if not, that is the real problem; see escalation.md).
   - **Partially covered**: extend or sharpen the existing line instead of adding a second one.
   - **Conflicts**: do not add a contradiction. Surface both lines and resolve the pair with the user, or rewrite one with an explicit scope or exception.
   - **New**: decide the home with placement.md and rules-architecture.md; it may not be the file the user named. Place it in the section where it belongs, in the file's existing style, not at the end.
4. **Apply the counterfactual test** to the new line itself (placement.md step 0): if Claude already behaves this way, say so and suggest not adding it, or add it only if the user insists.
5. **Report what else you noticed** while reading: contradictions, duplicates, stale commands, no-op lines, procedures that should be skills. Stop before writing each item and Read the reference for its kind if you have not read it in this session, because it says what to recommend and what to ask: duplicates, contradictions, ambiguity or no-op lines → [cross-file-analysis.md](cross-file-analysis.md); steps, checklists or repeated workflows → [procedures-to-skills.md](procedures-to-skills.md); repeated misbehavior or emphasis → [escalation.md](escalation.md); where something should live → [rules-architecture.md](rules-architecture.md). Mention each briefly with its recommendation; fix them only if asked.

## Shape of a strong line

Sources: Claude Code memory docs ("Write effective instructions"), Anthropic's prompting best practices ("Be clear and direct", "Add context to improve performance", "Tell Claude what to do instead of what not to do", "Use examples effectively") and "Effective context engineering for AI agents". Checked 2026-10-28. Where a point below is this plugin's own judgment rather than a documented claim, it says so.

1. **Lead with the action, or with a short trigger and then the action.** "Run…", "Use…", "Put…"; "When changing a public request field, update…". A line that states a wish or a value ("tests should pass", "we care about performance") gives Claude nothing to do.
2. **Concrete enough to verify.** "Use 2-space indentation", not "format properly". "API handlers live in `src/api/handlers/`", not "keep files organized".
3. **Say what to do, not only what to avoid.** The prompting guide's advice is to tell Claude what to do instead of what not to do; a bare prohibition names the wrong path and leaves the right one to guesswork. When a tempting default exists, put the contrast in the same line: "Send email through `mailer.send()` in `src/lib/mail.ts`, not the raw SMTP client." Find the alternative in the repo (manifest, existing helper, canonical file) before rewriting; if there is none, ask the user instead of inventing one. Keep a pure prohibition for a hard boundary with nothing to offer instead ("Never commit `.env` files"), and when it must never bend, enforce it (escalation.md); the prose line then only explains.
4. **Trigger, action, canonical artifact.** "When changing a public request field, update `openapi.yaml` and its contract test." Use this shape for correctness-sensitive conventions; plain preferences can stay one clause.
5. **A check when one exists.** "Confirm with `pnpm vitest run <file>`; if it cannot run, report the command and the blocker." Claude finishes better when it can check itself.
6. **The reason, in one clause, when it changes a decision.** "Use the retry helper in `src/lib/retry.ts`, not the copies in `src/legacy/`: they predate idempotency keys and can double-charge." The prompting guide notes that Claude generalizes from the explanation, so add the reason when the line looks arbitrary or goes against a common idiom, when Claude must judge whether a new case is covered, or when the user gave one. Leave it out when the action explains itself. If the reasoning needs more than a sentence or two, it is a decision record or a skill: link it rather than inlining prose.
7. **Point to an example before pasting one.** This plugin's rule for always-loaded files (the prompting guide's 3–5 diverse examples are for prompts and skills): the best example is a canonical file in the repo ("follow `src/api/routes/invoices.ts`"), because it stays true as the code changes. Inline an example only when the format itself is the instruction and the repo has no single source for it (a commit message shape, a log line), and then keep it short with every detail intended: the guide asks for diverse examples precisely so Claude does not pick up unintended patterns, and a lone example is where that risk is highest. Several varied examples (wrapped in `<example>` tags so they are not read as instructions) belong in a skill, where they load only when needed. Do not stack edge cases into always-on files.
8. **Pointers, not copies.** Name the file, exported symbol or section (`src/lib/errors.ts`, `HttpError`), not a pasted code block or line numbers that drift.
9. **Exact commands, copied from the source of truth.** Read `package.json` scripts, `Makefile`, `pyproject.toml`, CI workflows. Include how to run a single test.
10. **Plain, calm register.** No IMPORTANT, CRITICAL, ALL CAPS, `!!`, threats, rewards, personas, "think step by step", "be thorough", "don't be lazy". The Claude Code best-practices page says current models follow a plainly worded line and that piling on emphasis mostly makes Claude over-apply the rule; the prompting guide adds that newer models are more responsive to the system prompt and can overtrigger on aggressive language. Write "Use X when Y", not "CRITICAL: you MUST use X". A plain lowercase "never" is fine for a rule with no exceptions. If a line keeps being missed, emphasis is not the fix: the file is too long, the line is vague, it conflicts with another, or it is a zero-exception rule that belongs in a hook.
11. **The right altitude.** Specific enough to act on, general enough to cover cases the line does not list: state the rule with one concrete anchor, not an if/else tree for every situation (brittle and costly to maintain) and not a slogan (nothing to act on).
12. **Bullets under headers, one instruction each.** Markdown headers and bullets are the documented structure for CLAUDE.md and rules; prefer them. Use a short paragraph only where a trade-off needs explaining, and XML tags only to fence examples or quoted material. When to use numbered steps or tables, compact tables, imports versus pointers: format-and-links.md.
13. **Current state, without dates or copied versions.** Write the rule as it is now. Dates, "as of", "until March" and "recently migrated" go stale, and a version number copied from the manifest or lockfile drifts from it. Keep a version only when it changes what Claude writes and Claude would not otherwise check it ("Write React 18 code; React 19 APIs such as `use()` and Actions are not available here"). For a migration in progress, name the current way and the old pattern to leave alone, not the date. Put ownership and review dates in an HTML comment, which is stripped before Claude sees the file. The skill-authoring best practices state this rule for skills ("Avoid time-sensitive information", with an "old patterns" section for legacy behavior); the same reasoning applies to always-loaded files.

## What to leave out

The test for every line: would Claude act differently without it? If not, leave it out (placement.md, admission test step 0). In particular:

- Directory trees, architecture overviews, dependency lists, framework basics, language style rules the formatter enforces.
- Generic virtues ("write clean, production-ready code", "follow best practices", "use meaningful names", "handle errors properly").
- Lines that restate what Claude Code already enforces or does by default: reading a file before editing it, restating its built-in commit and PR guidance (team-specific commit and PR conventions are not this; keep them, see placement.md step 0).
- One-task acceptance criteria.
- Long procedures (put them in a skill) and long reference material (skill or a doc Claude is pointed to).
- Secrets, tokens, customer data, internal hostnames that must not leak: instruction files are plain text, often committed, and imported by tools.
- Model identity claims, guessed training cutoffs, model IDs and effort levels (these belong in settings).
- Statements about the future ("we will migrate to X") and dated or versioned statements ("as of March", "since v2.3", a version copied from the lockfile); write the current rule (item 13 above).

## Structure

- Group under a few headings that match how tasks start: `Commands` (verify, test one file, typecheck, lint, build), `Conventions` (team decisions not visible in code), `Gotchas` (misleading code, required env, ordering traps), optionally `Change reporting`.
- Bullets, one instruction each. Keep paragraphs for the rare rationale.
- Target under 200 lines per CLAUDE.md; most strong project files are 20 to 80. Length is a maintenance signal; behavior in a fresh session is the acceptance test.
- HTML comments (`<!-- owner: platform team; review after a toolchain change -->`) are stripped before injection: use them for ownership and review notes.

## Rule file template

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "tests/api/**/*.test.ts"
---
# API handlers

- Validate request bodies with the zod schemas in `src/api/schemas/`.
- For a changed request or response field, update `openapi.yaml`; CI fails without it.
- Return errors through `HttpError` in `src/lib/errors.ts`.
```

Quote every glob. Use `**` for recursion. Check each pattern matches the files intended and no others.

## Project CLAUDE.md skeleton

```markdown
# Commands
- Install: `pnpm install --frozen-lockfile`
- Test one file: `pnpm vitest run path/to/file.test.ts`
- Typecheck: `pnpm typecheck`
- Lint: `pnpm lint`

# Conventions
- Errors go through `src/lib/errors.ts`; never throw raw strings.
- `src/legacy/` is still deployed; don't copy its patterns into new code.

# Gotchas
- Integration tests need `DATABASE_URL`; see `.env.example`.
```

Every command above is illustrative: replace each with the repository's real one after reading its manifest, or omit it.

## User CLAUDE.md skeleton

```markdown
# Working preferences
- Project instructions and explicit task requirements win over these defaults when they differ.
- Report what changed, which checks actually ran, and what remains unverified.
- Before relying on a version-sensitive API, check the installed version and its official docs.
```

Add only preferences the owner actually holds (language of conversation vs deliverables, review style, approval boundaries). No stack, no commands.

## Before and after

| Before | After | Why |
| :-- | :-- | :-- |
| `IMPORTANT!!! ALWAYS run the tests` | `Run one file with \`pnpm vitest run <file>\`; run \`pnpm test\` before reporting done.` | Exact command, no emphasis |
| `The project uses React, TypeScript and Vite. src/ contains components/, hooks/, utils/...` | (delete) | Discoverable |
| `NEVER edit src/gen/` | `src/gen/ is generated by \`pnpm codegen\`; change the schema and regenerate.` plus a proposed `Edit(/src/gen/**)` deny rule | Explains the alternative; enforcement moves to config |
| `Follow our API conventions` | Scoped rule with the three conventions and `paths: ["src/api/**/*.ts"]` | Concrete, loads only where relevant |
| `Use pnpm` in `~/.claude/CLAUDE.md` | (move to each pnpm project, or "Use the package manager the lockfile indicates") | User scope must stay portable |
| 60-line release checklist in CLAUDE.md | `.claude/skills/release/SKILL.md` with `disable-model-invocation: true` | Procedure, side effects |
| `Think step by step and be thorough` | (delete; set effort) | Not a control |
| `NEVER use lodash!!!` | `Use native array methods and the helpers in \`src/lib/collections.ts\`, not lodash.` | Action first, alternative taken from the repo, no emphasis |
| `IMPORTANT: don't call Stripe directly, it breaks reconciliation` | `Charge cards through \`billing.charge()\` in \`src/billing/client.ts\`, not the Stripe SDK: direct calls skip the reconciliation ledger.` (scoped to the billing code) | Alternative plus the user's reason in one clause |
| Five pasted webhook payloads | `Validate incoming webhooks against \`WebhookEvent\` in \`src/types/webhooks.ts\`; its test holds a sample payload.` | Points to the canonical source instead of examples that drift |
| `As of March 2026 we use Vitest 2.1.4 (migrated from Jest)` | `Run tests with Vitest (\`pnpm test\`); don't add Jest tests.` | Current state only; the version lives in package.json |

## Editing an existing file

- Keep the author's structure and voice unless restructuring is the task.
- When the request is "add X to CLAUDE.md" and X fails the admission test or belongs elsewhere, say so in one sentence, recommend the better home, and still do what was asked unless it would create a contradiction, a duplicate, or leak personal or secret content into a shared file.
- When adding a line that contradicts another file (user vs project, root vs rule), resolve the pair: rewrite one, scope it, or state the exception explicitly.
