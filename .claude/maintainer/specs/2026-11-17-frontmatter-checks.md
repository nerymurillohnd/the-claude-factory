# Frontmatter checks spec (FM-1 to FM-14)

Copied verbatim from Nery's thread message of 2026-11-17. The FM-13 "Verifies" line came before its heading in the original message; it is placed under FM-13 here.

## FM-1 Frontmatter block exists, is placed first and is a mapping

Verifies: line 1 is --- (after stripping a byte-order mark and normalizing CRLF); a closing --- line exists; the YAML between them is a mapping, not a list, scalar or empty.
Why: Claude Code reads the frontmatter only when the opening --- is the first line; otherwise the whole file becomes content and every field is lost.
Source: skills, Frontmatter reference: "Claude Code reads the frontmatter only when the opening --- is the file's first line." Verified.
Coverage: Partial. validate reported No frontmatter block found (unclosed, blank first line, none) and Frontmatter must be a YAML mapping, tested. Missing: a SKILL.md at a plugin's root, which validate doesn't read (plugin validate: "Claude Code doesn't check a SKILL.md at the plugin root"), and skills inside symlinked folders, which it doesn't follow.

## FM-2 Frontmatter parses as strict YAML

Verifies: the block parses under a strict YAML parser that rejects duplicate keys, a value containing : , an unclosed flow collection, an unclosed quote, tabs in indentation and a key indented under a scalar; each error carries its file line.
Why: when the YAML doesn't parse, "the skill still loads with no fields set" (skills), silently dropping the description Claude chooses the skill by. Claude Code's parser accepts some malformed YAML that other tools (upload, packaging, editors) reject.
Coverage: Partial. validate caught an unclosed quote and a tab; it passed duplicate keys, a: b inside a value and [unclosed, tested.

## FM-3 Plain values that read differently than written

Verifies, for each unquoted scalar at any depth: no :  or trailing :; no  # (starts a comment); no leading YAML indicator (-, ?, :, ,, [, ], {, }, #, &, *, !, |, >, ', ", %, @, `); and, for a field that expects text, no value a YAML parser reads as a boolean or null (yes, no, on, off, true, false, null, ~).
Why: the text a human reads and the value a parser builds diverge, so a description loses its tail or a name becomes a boolean. One earlier generation also enforced a house style (no colon and no quotes in any value); that is a project convention, not an official rule.
Source: the risk is general YAML behavior; the docs note boolean fields accept yes, no, on, off, 1, 0 (skills). The indicator list is the YAML spec's, not re-verified in this pass.
Coverage: Not covered.

## FM-4 name format and identity

Verifies: when present, name is a string of 1 to 64 characters, only a-z, 0-9 and -, no leading, trailing or consecutive hyphen, and equal to the skill's folder name; it holds none of the characters Claude Code refuses (<, >, zero-width or control characters, private-use or unassigned characters, bidirectional controls, any blank other than one plain space between words). Severity depends on the surface: the open spec and claude.ai uploads require name; Claude Code makes it optional and defaults to the folder name.
Why: a refused name hides the skill from the / menu; a name unlike its folder renames the command and breaks uploads; a malformed name fails the open standard.
Source: Agent Skills spec, name: "Must be 1-64 characters … Must not contain consecutive hyphens … Must match the parent directory name." skills, Characters a skill name can't hold. skills, How a skill gets its command name. Verified.
Coverage: Not covered. validate passed Other_Name-claude- in a folder named otherwise, tested. Feeds frontmatter-description and size-limits-and-budgets (character counts).

## FM-5 name is written as one plain line

Verifies: the name value is a plain scalar on one line, so its text in the file is exactly the parsed name: not quoted, not a block scalar (|, >), not folded over lines, no anchor, alias or tag, and not a value YAML 1.1 reads as a boolean, number, date or null.
Why: tools that read the name as text (packagers, catalogs, other checks) and the YAML parser must agree.
Source: project convention built on the spec's name rules; not an official rule.
Coverage: Not covered.

## FM-6 Reserved names and words

Verifies: name contains neither anthropic nor claude; the folder is not named synced (any capitalization) in personal, project or managed locations; outside a plugin, the folder or command file is not anthropic-skills and doesn't start with anthropic-skills:.
Why: the Claude API and claude.ai reject the reserved words; Claude Code skips a folder named synced and does not load the anthropic-skills names.
Source: best practices: "Cannot contain reserved words: anthropic, claude". skills, "Reserved name synced" and "Reserved name anthropic-skills". Verified.
Coverage: Not covered.

## FM-7 description is valid

Verifies: present; a non-empty string; at most 1,024 characters; no XML tags.
Why: Claude chooses the skill by its description; the open spec and the API reject one that breaks these limits; angle brackets display as &lt; and &gt; in Claude Code.
Source: Agent Skills spec: "Max 1024 characters. Non-empty." best practices: "Cannot contain XML tags". Verified.
Coverage: Not covered. validate passed an XML tag and 1,100 characters, tested.

## FM-8 Listing cap of description plus when_to_use

Verifies: the combined length of description and when_to_use is at most 1,536 characters, and reports where the 1,536th character falls (the text after it never reaches Claude).
Why: Claude Code truncates the combined text in the skill listing; trigger words past the cap are lost.
Source: skills, Frontmatter reference: "the combined description and when_to_use text is truncated at 1,536 characters". The cap is configurable with skillListingMaxDescChars. Verified.
Coverage: Not covered. Named in the size-limits-and-budgets Receives list; no command produces it. /skill-doctor gives listing cost, not the truncation point.

## FM-9 compatibility is valid

Verifies: when present, a string of 1 to 500 characters.
Source: Agent Skills spec: "Must be 1-500 characters if provided". skills: "Accepts a string of up to 500 characters." Verified.
Coverage: Not covered. validate passed 600 characters, tested.

## FM-10 metadata is a map of strings

Verifies: when present, a mapping whose keys and values are all strings, and whose keys don't reuse frontmatter field names such as paths.
Why: Claude Code "drops a value that isn't a map"; the spec defines string values.
Source: skills, Frontmatter reference. Verified.
Coverage: Not covered. validate passed metadata: {a: 1}, tested.

## FM-11 Field names: unknown, and outside the open spec

Verifies: (a) every key is a field Claude Code recognizes, with exact spelling and hyphens; (b) for a skill that will reach claude.ai uploads, the Skills API or packaging, only the six spec fields are used (name, description, license, compatibility, metadata, allowed-tools). Which applies depends on the skill's origin: account and plugin skills that reach chat or uploads fail (b); a personal skill gets a warning, because enabling it on claude.ai is an upload.
Why: Claude Code "ignores a field it doesn't recognize without reporting an error", so a typo silently disables a setting; an upload with any extra field fails with a hard error.
Source: skills, Frontmatter reference and Using skill frontmatter outside Claude Code. Verified.
Coverage: Not covered. validate --strict passed bogus-key, tested. Feeds frontmatter-description ("whether each field is valid on each target surface").

## FM-12 Field values have the documented types and values

Verifies: booleans (disable-model-invocation, user-invocable, background) hold a documented boolean form; context is fork; effort is one of low, medium, high, xhigh, max; shell is bash or powershell; allowed-tools, disallowed-tools, paths and arguments are a string or a list of strings; model is a value /model accepts or inherit.
Source: skills, Frontmatter reference. Verified.
Coverage: Partial. validate rejected allowed-tools: 42 and shell: fish; it passed user-invocable: maybe, effort: turbo and context: spoon, tested.

## FM-13 Field combinations that cancel each other

Verifies: not disable-model-invocation: true together with user-invocable: false (nobody can invoke the skill); paths set while disable-model-invocation: true (paths then does nothing); agent or background set without context: fork (they apply only with it).
Why: each combination silently disables part of the skill.
Source: skills, Frontmatter reference: background "Only applies with context: fork"; agent applies "when context: fork is set"; the first two combinations follow from the documented meaning of each field (inference, not a quoted rule).
Coverage: Not covered.

## FM-14 allowed-tools shape for the open spec

Verifies: allowed-tools written as a YAML list is flagged for skills meant to work outside Claude Code, where the spec defines a space-separated string; an unscoped Bash, Bash(*) or Bash(:*) is flagged as approving every command.
Source: the spec defines allowed-tools (agentskills.io); Claude Code accepts a string or a list (skills). The "space-separated string" wording in the spec was not re-read in this pass.
Coverage: Not covered.
