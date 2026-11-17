# Sources

Where to verify each platform fact before writing it into a skill, how to read those sources, and how to settle them when they disagree. Platform facts change between releases; a fact from memory is a guess until a current source confirms it.

## Contents

- The official sources
- How to read them
- When sources disagree
- Record what you verified

## The official sources

Consult the source that owns the fact:

- **Agent Skills specification and guides**, https://agentskills.io: the portable format every client shares. The specification (fields, limits, folder layout, `skills-ref validate`), best practices, optimizing descriptions, evaluating skills, using scripts.
- **Claude Platform docs**, https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview and the pages it links: how skills run on claude.ai, the Claude API and Managed Agents; authoring best practices; skills for enterprise; the Skills API guide (uploads, versions, limits); the code execution tool's list of preinstalled packages.
- **Claude Code docs**, https://code.claude.com/docs/en/skills and the pages it links: locations, every frontmatter field, substitutions, injected commands, invocation, `context: fork`, troubleshooting. For related features: sub-agents (preloading), hooks (hooks in skills), plugins (components, reference, loading, marketplaces) and plugin evals.
- **Claude Code changelog**: what changed in each version, including fields and behaviors the docs haven't caught up with.
- **Anthropic's guides and articles**: "The Complete Guide to Building Skills for Claude" (PDF), the engineering article "Equipping agents for the real world with Agent Skills", and the public skills at https://github.com/anthropics/skills as worked examples.
- **Claude Help Center**, https://support.claude.com: creating and uploading skills on claude.ai, plans and settings.
- **Claude Academy**, https://academy.claude.com: courses and tutorials on building skills.

When the session has a documentation tool for one of these (a docs MCP server, a docs-research skill), use it first: it searches the current pages.

## How to read them

- Read the whole page or section, not a search snippet: the condition that changes the answer is often a paragraph away.
- Follow the page's links to the related pages; a field's limits are often documented on the feature it belongs to.
- Fetch the Markdown version of a docs page where the site offers one, and save a long page to a file before reading it, so nothing is truncated.
- Find the version in use (`claude --version` in Claude Code) and check the changelog for it and the releases around it: a feature may need a newer version than the user has, or may have changed since the docs were written.
- Check every surface the skill targets: a fact true in Claude Code can be false on claude.ai or the API.

## When sources disagree

Resolve by the surface the skill runs on. The source that owns a surface wins for that surface; for a skill that runs on several, follow the strictest.

Known disagreements and their resolution:

- **Description content.** Most sources say what the skill does and when to use it; some say only when to trigger it. Write what it does in terms of capability, then when, and never a summary of its workflow.
- **Description length.** 1,024 characters in the specification and for uploads, enforced; Claude Code cuts `description` plus `when_to_use` at 1,536 in its listing, configurable. A support article's 200-character limit is outdated. Keep to 1,024 for any skill that leaves Claude Code.
- **`allowed-tools`.** The PDF guide says it restricts tools; Claude Code's docs say it grants permission and restricts nothing. Claude Code's docs win for Claude Code; other clients vary, and the specification marks the field experimental.
- **Emphasis.** The PDF guide recommends "CRITICAL" headers and repeating key points; the specification's guides, skill-creator and Claude Code's docs favor reasons over capitals. Write plain instructions with reasons; fix a skipped rule by placement, a gate or a hook.
- **Body size.** 500 lines and 5,000 tokens (specification, Claude Code) versus 5,000 words (PDF guide). Use the stricter.
- **Table of contents threshold.** 100 lines (Platform best practices) versus 300 (skill-creator). Use 100.
- **Portability.** The PDF guide says skills work identically everywhere; the Platform docs say custom skills don't sync between surfaces and each runtime differs. The Platform docs are right: test on each surface.

When the docs and the installed binary disagree, trust the binary's behavior (`--help`, real output) and the changelog, and mark the fact as taken from them. When the requester's instruction contradicts an official source, follow the source, show the requester both, and let them decide if it changes what they asked for.

## Record what you verified

For each platform fact the skill states, keep in your working notes the source, the date you read it, and the version it applies to. In the skill itself, write only the fact, and a version where the behavior depends on one ("Claude Code v2.1.233 or later"). Never write a date or "currently" into the skill: it goes stale. In your report, list the facts you couldn't verify and what they affect.
