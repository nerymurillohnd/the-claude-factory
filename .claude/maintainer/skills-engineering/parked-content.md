# Parked content from runtime-contract.md (original, baseline commit)

Verbatim passages moved out of scope on 2026-11-14. Not part of the plugin. Each block names its future owner and original lines.


## Frontmatter and naming (future frontmatter-description reviewer) — original lines 105-358

## 2. Frontmatter contract

### 2.1 File structure and parsing

A skill requires a top-level `SKILL.md`. Its structure is YAML
frontmatter followed by Markdown instructions:

``` yaml
---
name: example-skill
description: >-
  Performs a defined task. Use when the user requests that task or
  provides the relevant inputs.
---

# Instructions

Operational instructions begin here.
```

Rules: - The opening `---` must be the first line for Claude Code to
recognize frontmatter. - YAML must parse. Claude Code may still load the
body when YAML is malformed, but metadata is empty and the description
cannot trigger the skill. - Field names must match the accepted spelling
exactly. Claude Code silently ignores unknown or misspelled fields. -
Use lowercase hyphenated field names, except the documented
`when_to_use` field. - Boolean values may be expressed as `true`,
`false`, `yes`, `no`, `on`, `off`, `1`, or `0`, case-insensitively, in
Claude Code. - A client implementation may choose stricter or more
lenient malformed-YAML handling. The cited client guidance recommends
skipping a skill if its description is missing or empty; on parse
failure, skip; on a name mismatch or overlong name, warn and load.

**Audit failure:** frontmatter is not the first line, YAML is invalid, a
required target-specific field is absent, a field is misspelled, or a
field unsupported by the target surface is present.

### 2.2 Required fields depend on the target

  ------------------------------------------------------------------------------
  Target                             `name`        `description` Accepted
                                                                 frontmatter
  -------------------- -------------------- -------------------- ---------------
  Claude Code            Optional; defaults Recommended; primary Claude Code's
                          to directory name        trigger field full skill
                                                                 field set

  Agent Skills                     Required             Required Six standard
  specification                                                  fields only

  claude.ai upload                 Required             Required Six standard
                                                                 fields only

  Skills API                       Required             Required Six standard
                                                                 fields only

  `package_skill.py`               Required             Required Six standard
  packaging                                                      fields only
  ------------------------------------------------------------------------------

The six standard fields are: - `name` - `description` - `license` -
`compatibility` - `metadata` - `allowed-tools`

**Critical compatibility rule:** a field accepted by Claude Code is not
necessarily accepted by the specification, claude.ai, the Skills API, or
packaging. An upload or package operation fails with an unexpected-key
error when non-standard fields such as `argument-hint` are present. If a
skill must run on multiple surfaces, use only the intersection of their
supported fields unless separate surface-specific artifacts are
deliberately maintained.

Claude Code's optionality does not override the stricter upload
contract. Conversely, the specification's directory-name rule is not
identical to Claude Code's command-name behavior.

### 2.3 Frontmatter field reference

  ---------------------------------------------------------------------------------------
  Field                        Claude Code behavior Standard/upload   Audit guidance
                                                    status            
  ---------------------------- -------------------- ----------------- -------------------
  `name`                       Optional; defaults   Standard;         Use 1--64 lowercase
                               to directory name;   required for      alphanumeric
                               controls displayed   specification and characters and
                               command name         uploads           hyphens; avoid
                                                                      leading/trailing or
                                                                      consecutive
                                                                      hyphens; match
                                                                      directory for
                                                                      portable skills

  `description`                Recommended; primary Standard;         Non-empty; state
                               activation signal;   required;         capability and
                               first non-empty body 1--1,024          activation
                               line is fallback if  characters        conditions; include
                               omitted                                natural user
                                                                      keywords

  `when_to_use`                Appended to          Not standard;     Claude
                               description for      upload rejected   Code-specific only
                               discovery; counts                      
                               toward Claude Code                     
                               listing cap                            

  `argument-hint`              Autocomplete hint    Not standard;     Claude
                               for expected         upload rejected   Code-specific only
                               arguments                              

  `arguments`                  Named positional     Not standard;     Only first 64
                               arguments for        upload rejected   names, each at most
                               `$name`                                64 characters, are
                               substitution;                          filled according to
                               space-separated                        the cited Claude
                               string or YAML list                    Code changelog;
                                                                      this application of
                                                                      the changelog
                                                                      wording is an
                                                                      inference

  `disable-model-invocation`   Prevents automatic   Not standard;     Set `true` only
                               invocation and       upload rejected   when invocation
                               preloading into                        must be
                               subagents; default                     user-controlled; it
                               `false`                                also removes the
                                                                      skill from model
                                                                      discovery

  `user-invocable`             `false` makes the    Not standard;     Use to control
                               skill Claude-invoked upload rejected   user-facing
                               only; default `true`                   invocation

  `allowed-tools`              Grants listed tools  Standard;         Does not restrict
                               without asking       optional;         available tools;
                               during the invoking  experimental in   permission/deny
                               turn; grant clears   specification     rules can still
                               on the next user                       override it; eval
                               message                                case permissions
                                                                      cannot widen it

  `disallowed-tools`           Removes tools while  Not standard;     Claude
                               skill is active;     upload rejected   Code-specific
                               restriction clears                     restriction
                               on next user message                   

  `model`                      Model override for   Not standard;     Organization model
                               current turn;        upload rejected   allowlist can
                               `inherit` supported;                   prevent the
                               with fork, selects                     requested model
                               fork model                             

  `effort`                     `low`, `medium`,     Not standard;     With fork, sets
                               `high`, `xhigh`, or  upload rejected   fork effort;
                               `max`, subject to                      environment effort
                               model availability;                    setting can take
                               current-turn                           precedence
                               override                               

  `context`                    `fork` runs skill in Not standard;     Use only when the
                               a forked subagent    upload rejected   skill body contains
                               context                                explicit standalone
                                                                      instructions

  `agent`                      Subagent type used   Not standard;     If omitted,
                               with                 upload rejected   `general-purpose`
                               `context: fork`;                       is used
                               built-ins include                      
                               `Explore`, `Plan`,                     
                               `general-purpose`,                     
                               or custom agents                       

  `background`                 Applies only to      Not standard;     Background fork
                               fork; default        upload rejected   uses narrower
                               `true`; `false`                        background tool set
                               waits for result                       

  `hooks`                      Registers hooks on   Not standard;     `once: true` is
                               invocation for the   upload rejected   honored for
                               rest of the session                    skill-frontmatter
                                                                      hooks; review
                                                                      trust, lock, and
                                                                      count limits

  `paths`                      Glob activation      Not standard;     Files outside that
                               filters relative to  upload rejected   working directory
                               current working                        do not match;
                               directory                              sibling worktrees
                                                                      may not match

  `shell`                      Shell for dynamic    Not standard;     `bash` requirement
                               command blocks;      upload rejected   fails if Git Bash
                               `bash` default or                      is unavailable on
                               `powershell`                           the relevant
                                                                      Windows setup

  `metadata`                   Free-form YAML map;  Standard;         Use a map; avoid
                               Claude Code does not optional;         reusing frontmatter
                               act on contents and  key-value map     field names as
                               drops non-map values                   metadata keys

  `license`                    Accepted but not     Standard;         Use a short license
                               acted on by Claude   optional          name or bundled
                               Code                                   license-file
                                                                      reference

  `compatibility`              Accepted but not     Standard;         Include only
                               acted on by Claude   optional; 1--500  specific runtime
                               Code; up to 500      characters        requirements such
                               characters                             as product, system
                                                                      packages, or
                                                                      network access
  ---------------------------------------------------------------------------------------

Additional limits and behavior: - `allowed-tools` is experimental in the
Agent Skills specification and support varies by implementation. -
Claude Code accepts a space-separated string, comma-separated string, or
YAML list for `allowed-tools`; the specification describes a
space-separated string. - Claude Code's `allowed-tools` grant does not
override deny/ask rules. `allowManagedPermissionRulesOnly` can cause it
to be ignored in project and personal skills;
`strictPluginOnlyCustomization` can remove it in the documented
hook-customization case. - Skill frontmatter hooks run from invocation
until session end unless `once: true` applies. The documented per-source
limit (Claude Code v2.1.304+) is 1,024 hooks and 16,384 aggregate
matcher characters. Project-skill hooks follow workspace trust rules.
Plugin, bundled, and managed-directory skills have the documented
exception to the strict plugin-only customization lock. -
`disable-model-invocation: true` prevents preloading into subagents.

### 2.4 Naming rules

Portable naming rules: - Use 1--64 lowercase alphanumeric characters and
hyphens. - Do not begin or end with a hyphen; the specification also
prohibits consecutive hyphens. - Match the parent directory name when
targeting the Agent Skills specification or cross-surface uploads. -
Avoid XML tags, reserved names, and generic names such as `helper`,
`utils`, `tools`, `documents`, `data`, or `files`. - Prefer an
action-oriented or gerund name that identifies the capability. - Do not
use the reserved folder name `synced` in any capitalization. - Outside a
plugin, a folder or command named `anthropic-skills` or beginning
`anthropic-skills:` does not load. - Claude Code rejects
zero-width/control characters, private-use or unassigned characters,
direction-changing characters, unusual whitespace, and angle brackets in
command names. - A plugin skill command is namespaced as
`/plugin-name:skill-name`. Frontmatter `name` replaces the final command
segment while the plugin prefix remains. - If the plugin skill's `name`
already includes the plugin prefix, Claude Code v2.1.246+ does not add
it twice; versions v2.1.216--v2.1.245 did. - A single `SKILL.md` at
plugin root is supported as a single skill; set `name` explicitly to
avoid a cache-directory-derived name after marketplace installation.

**Do not collapse the naming distinction:** Claude Code permits a
frontmatter `name` different from the directory name and uses it to
change the command. The Agent Skills specification and upload guidance
require a directory/name match. For portable artifacts, make them match.

## Description and activation (future frontmatter-description reviewer; 3.3 to evals) — original lines 360-450

## 3. Description engineering and activation

### 3.1 Activation model

The description is the principal metadata used to decide whether to load
a skill. The agent generally sees skill name and description before it
reads the full `SKILL.md`; supporting files are loaded when instructions
call for them.

Consequences: - The description carries the activation burden. - A skill
can exist and load successfully but never be invoked if its description
does not match natural user phrasing. - A simple task may not invoke a
skill even when its description appears relevant. - Many installed
skills compete for a limited metadata budget; descriptions may be
shortened, removing important trigger terms. - A skill with
`disable-model-invocation: true` is not discoverable for model-driven
invocation.

### 3.2 Required description content

A good description answers both: 1. What capability or outcome does the
skill provide? 2. Under what user intents, situations, or inputs should
the agent use it?

Write for user intent, not implementation details. Include the primary capability or outcome, concrete situations and user intents that should trigger the skill, natural keywords users are likely to use, and explicit exclusions where needed to prevent false activation. Put the highest-value use case and trigger language first. Keep the description concise and within the strictest target limit of 1,024 characters. Avoid vague descriptions such as "Helps with PDFs", "Processes data", or "Does stuff with files".

Do not use the description as a general dependency or compatibility field. Detailed dependencies, required products, versions, packages, permissions, runtime assumptions, and setup requirements belong in the body of `SKILL.md` or in the standard `compatibility` field when they are relevant to the target and fit that field's purpose and limit. The description's primary job is to help the model decide **when the skill is relevant**. Spending its limited space on implementation prerequisites weakens the activation signal and can crowd out the user intents that should trigger it.

Decision rule: mention a prerequisite in the description only when omitting it would materially cause the skill to be selected for tasks it cannot perform, and even then use a short boundary rather than a dependency inventory. Put the authoritative prerequisite and its handling procedure in the body or `compatibility`. Do not follow an isolated recommendation from secondary educational material when it conflicts with the platform's documented metadata contract or the Agent Skills standard.

**Bad — spending the activation field on implementation details:**

```yaml
description: >-
  Uses Python 3.12, the pandas package, the local filesystem, and
  /opt/tools/renderer to process spreadsheets. Requires network access.
```

This describes prerequisites but does not clearly tell the model which user requests should activate the skill. It also consumes the limited description budget with details that belong in the operational instructions or compatibility metadata.

**Better — capability and trigger first, prerequisites in the body:**

```yaml
description: >-
  Cleans, validates, and transforms spreadsheet files into consistent
  analysis-ready workbooks. Use when the user asks to inspect, repair,
  normalize, or prepare Excel or CSV data for reporting.
```

Then document Python, package versions, executable paths, network requirements, and fallback behavior in a dedicated prerequisites section of `SKILL.md` or in `compatibility` where appropriate.

Description voice guidance differs between sources: one recommends
third-person capability phrasing and another recommends imperative
phrasing such as "Use this skill when...". Both require explicit use
conditions. Choose a consistent formulation and validate it with real
trigger tests rather than treating either voice convention as a
universal parser requirement.

Claude Code-specific details: - `when_to_use` is appended to
`description` for the skill listing. - The combined text is subject to a
1,536-character listing cap, configurable through
`skillListingMaxDescChars`. - The overall listing budget is influenced
by `skillListingBudgetFraction` and `SLASH_COMMAND_TOOL_CHAR_BUDGET`;
less-used skills may have descriptions dropped first. - Angle brackets
are escaped for display. Do not use XML tags in descriptions intended
for the specification or API.

### 3.3 Trigger evaluation

Evaluate descriptions using realistic prompts that do not name the
skill. Include: - positive prompts expressed in varied natural
language; - near-neighbor prompts that should trigger a different
skill; - negative prompts that must not trigger this skill; - prompts
where the user describes the outcome without naming the domain; -
prompts with missing dependencies or unsupported inputs.

If a positive prompt fails, improve specificity and add the language
users naturally use. If a negative prompt triggers, clarify the boundary
or state what the skill does not cover. Do not add keywords from failed
negative prompts indiscriminately; that overfits the description.

Claude Code guidance identifies `claude plugin eval` and a
`tool_used: Skill` grader as ways to measure whether natural prompts
invoke the skill. Re-run trigger evaluations after description changes.

**Anti-patterns** - Capability-only description with no activation
conditions. - Broad language that competes with unrelated skills. -
Implementation details instead of user situations. - Key trigger phrase
buried after low-value text. - Description exceeding 1,024 characters on
standard/upload targets. - Assuming that successful installation proves
correct activation.

## Script audit (scripts reviewer; secrets to security) — original lines 566-580

### 4.4 Script audit

-   Put scripts inside the skill directory, usually in `scripts/`.
-   State required runtimes and versions, packages, and other
    prerequisites.
-   List available scripts in `SKILL.md`.
-   Explicitly say whether each script must be executed or read as
    reference.
-   Prefer execution: only script output enters context in the
    documented runtime behavior.
-   Make referenced scripts executable where required (`chmod +x`).
-   Install packages locally rather than changing the user's global
    environment.
-   Never embed API keys, passwords, tokens, or other credentials in
    scripts or skill content.

## Progressive-disclosure size guidance (size limits) — original lines 521-531

Recommended progressive-disclosure pattern: - Keep `SKILL.md` as the
overview, routing logic, and operational workflow. - Move large schemas,
detailed tables, examples, and conditional procedures into focused
reference files. - Load only the reference needed for the current
task. - For reference files longer than 100 lines, include a table of
contents. - Keep `SKILL.md` below 500 lines and approximately 5,000
tokens as a recommendation, not a hard universal runtime limit. - A
loaded skill remains in context across turns in Claude Code; unnecessary
body content creates recurring token cost. The cited compaction behavior
retains the first 5,000 tokens of each skill and has a combined
25,000-token budget for re-attached skills.

## API and plugin upload limits (size limits) — original lines 979-983

-   Session supports up to 500 skills, counted as a deduplicated set
    across agents.
-   API upload limits in the source: under 30 MB uncompressed and at
    most 20 skills per request. A plugin can contain up to 5,000 files
    and 200 MB.

## Known disagreements (rows on name, description, voice, allowed-tools syntax, name match go to frontmatter-description; the rest folded into runtime-contract areas) — original lines 1021-1102

## 9. Known disagreements and unresolved evidence

Do not erase these differences during an audit:

  -----------------------------------------------------------------------
  Topic                   Difference              Operational resolution
  ----------------------- ----------------------- -----------------------
  Required `name` and     Optional in Claude      Validate against the
  `description`           Code; required by       strictest target;
                          specification,          require both for
                          claude.ai, API, and     portable skills
                          packaging               

  Description length      1,024-character         Stay within 1,024
                          standard/API limit;     characters
                          Claude Code listing cap 
                          is 1,536 combined with  
                          `when_to_use`,          
                          configurable            

  Description voice       Third-person guidance   Ensure capability plus
                          versus imperative       activation condition;
                          phrasing                evaluate with trigger
                                                  tests

  Skill precedence        Claude Code             Test exact
                          documentation says      client/source collision
                          Enterprise \> Personal  behavior
                          \> Project; client      
                          guidance says Project   
                          \> User                 

  Script working          One source describes    Use explicit
  directory               skill-root-relative     substituted absolute
                          execution; Claude Code  paths
                          runs in session shell   
                          directory               

  Cross-surface sync      API/platform custom     Identify artifact type
                          skills are separate;    and sync mechanism
                          account-synced          
                          claude.ai skills have   
                          documented sync paths   

  Built-in subagents      Transcript says         Distinguish preload
                          built-ins cannot access from invocation access
                          skills; page text says  
                          they do not preload,    
                          but can invoke with     
                          Skill tool              

  ZIP root layout         claude.ai packaging     Package separately per
                          expects skill folder at target
                          ZIP root; API accepts   
                          root `SKILL.md`         

  `allowed-tools`         Standard describes      Use portable syntax and
  syntax/lifetime         space-separated         do not assume grant
                          experimental field;     persists
                          Claude Code accepts     
                          string/list forms and   
                          turn-scoped grant       

  Directory name vs       Standard requires       Match for portability
  `name`                  match; Claude Code      
                          allows override         
  -----------------------------------------------------------------------

Other distinctions: - The 500-line and 5,000-token recommendations are
compatible; they are guidance, not identical hard limits. - Claude.ai
package installation capability does not imply universal network access;
network availability may be restricted by user/admin settings. - A
session can load a symlinked skill that the validator skips. - A plugin
skill's name in a plugin agent's `skills` list remains undocumented in
the source extraction. - References from a skill into another installed
plugin at runtime remain undocumented. - `@` file-reference syntax in
local skill bodies is not directly specified by the extracted sources. -
`${CLAUDE_SKILL_DIR}` behavior in synced local sessions and
skill-frontmatter hooks remains unverified. - Symlink behavior for
claude.ai/API uploads, Managed Agents repository discovery, and
individual symlinked files in personal/project skills remains
unverified.

## Anti-pattern catalogue (frontmatter, description, script and secrets rows go to their owners; the rest folded into runtime-contract areas) — original lines 1104-1188

## 10. Anti-pattern catalogue

  ----------------------------------------------------------------------------
  Anti-pattern               Why it fails            Required correction
  -------------------------- ----------------------- -------------------------
  Frontmatter not at         Claude Code treats      Put opening `---` on line
  byte/line start            metadata as body text   1

  Malformed YAML             Skill may load without  Parse YAML before release
                             metadata and never      
                             trigger                 

  Unknown field copied from  Upload/package rejects  Restrict frontmatter to
  Claude Code into API       unsupported keys        six standard fields for
  package                                            cross-surface uploads

  Missing description        Discovery/activation    Add a specific, non-empty
                             fails or client skips   description
                             skill                   

  Generic description        Poor matching and false Describe task, user
                             triggers                situation, keywords, and
                                                     boundaries

  Overlong description       Standard target rejects Keep under 1,024
                             or listing truncates it characters

  Directory/name mismatch    Specification/upload    Match folder and `name`
                             validation fails        

  Reference file mentioned   Agent does not know     Name exact path and load
  generically                when to load it         condition at workflow
                                                     step

  Deep reference chains      Agent may only          Link references directly
                             partially inspect       from `SKILL.md`
                             nested references       

  Script treated as prose    Source code consumes    Tell agent to execute it
                             context unnecessarily   

  Bare relative script path  `cd` changes the shell  Use `${CLAUDE_SKILL_DIR}`
                             base directory          or
                                                     `${CLAUDE_PROJECT_DIR}`

  Parent-relative plugin     Cached plugin omits     Bundle dependency or use
  dependency                 files outside plugin    permitted marketplace
                             root                    symlink

  Hard-coded plugin install  Cache/version path      Use plugin path variables
  path                       changes                 

  Plugin component under     Plugin loader does not  Put skills under
  `.claude-plugin/skills/`   scan it                 plugin-root `skills/`

  Backslash paths            Platform/manifest       Use forward slashes
                             validation failure      

  Symlink assumed to be      Validator skips         Test actual session
  validated                  symlinked entries       loading

  Broad `Bash` pre-approval  Grants shell execution  Scope permission to exact
                             too broadly             command

  Secrets in skill or script Distributed files       Use secure
                             expose credentials      environment/credential
                                                     store

  Local filesystem skill     Cowork/cloud does not   Enable account skill or
  assumed in cloud           read local personal     use supported repository
                             folder                  route

  Skill preloaded into a     Subagent lacks          Make instructions
  fresh subagent without     conversation context    self-contained and pass
  standalone instructions                            required inputs

  `allowed-tools` assumed to It grants pre-approval; Use tool
  restrict tools             it does not define the  restrictions/deny
                             full available tool     controls where required
                             pool                    

  Validator success treated  Validator omits         Run target-surface
  as runtime proof           plugin-root and symlink integration tests
                             cases                   
  ----------------------------------------------------------------------------

## 13.1 Frontmatter parsing (frontmatter-description) — original lines 1243-1254

### 13.1 Frontmatter parsing, validation, and portability edge cases

- The opening YAML delimiter must be the first line of `SKILL.md` for Claude Code to parse frontmatter. Leading text, a byte-order mark, or other content before it can cause the metadata to be treated as body text. Verify the actual first line, not merely the visual appearance in an editor.
- A malformed YAML block can leave a Claude Code skill loadable by its explicit command name while removing metadata-based discovery. Therefore, "the slash command works" does not prove the description was parsed or that automatic activation can work.
- Claude Code silently ignores unknown or misspelled fields. A skill may therefore appear to load while an intended setting has no effect. Validate exact field spelling and target support; do not infer field acceptance from successful loading.
- The Agent Skills client guidance describes a lenient client strategy: skip a skill if `description` is missing or empty; skip if YAML cannot be parsed; warn but load if `name` does not match the directory or exceeds 64 characters. This is client-implementation guidance, not a guarantee that every client behaves this way. Do not rely on lenient loading for a portable deliverable.
- Claude Code accepts YAML boolean spellings including `true`, `false`, `yes`, `no`, `on`, `off`, `1`, and `0`, in any letter case. Prefer canonical `true` and `false` in portable files.
- Claude Code sanitizes skill display text by removing control characters and escaping angle brackets in text passed to Claude. The cited behavior requires Claude Code v2.1.228 or later. Do not use this runtime sanitization as a substitute for valid YAML or target-specific description rules.
- The Claude Code validator described in the source requires v2.1.233 or later. Its availability and version requirement must be checked before instructing an operator to run it.
- Plugin validation can report `No frontmatter block found` or `YAML frontmatter failed to parse: <error>` for invalid skill, agent, or command frontmatter. Preserve the actual diagnostic in the audit evidence.

**Decision:** when a target is not explicitly stated, distinguish two outcomes. For a Claude Code-only artifact, assess the Claude Code contract and report portability limitations. For a cross-surface artifact, use the strictest common contract: valid YAML, `name` and `description`, and only the six standard fields (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`). Never silently apply the permissive Claude Code field set to an upload target.

## 13.2 Field semantics (frontmatter-description; runtime consequences kept in runtime-contract) — original lines 1256-1279

### 13.2 Additional frontmatter field semantics

The field matrix in section 2.3 is the primary reference. Apply these additional details when the corresponding Claude Code-only field appears:

- `arguments` declares named positional substitutions. It may be written as a space-separated string or YAML list. The extraction reports that only the first 64 argument names, each up to 64 characters, are filled in. The source of that limit is a Claude Code changelog entry referring to "argument names"; applying it specifically to the `arguments` field is an inference because the changelog wording does not name the field. Flag use beyond the limit as unsupported by the extracted evidence; do not invent behavior for excess placeholders.
- `argument-hint` is an autocomplete hint, with examples such as `[issue-number]` or `[filename] [format]`. It is a Claude Code-specific field and is rejected by the six-field upload contract.
- `when_to_use` is appended to `description` in the Claude Code listing and shares the 1,536-character combined listing cap. It is not a standard field and is rejected by the six-field upload contract.
- `shell` selects the shell for dynamic `!` command blocks. The documented values are `bash` (default) and `powershell`. If `shell: bash` is required but Git Bash is unavailable on Windows, the skill fails with a shell requirement error. Audit the actual runtime dependency; do not assume Bash exists merely because the host is Windows or because a script has a shebang.
- `disallowed-tools` removes named tools from Claude Code's available pool while the skill is active; the restriction clears when the next user message arrives. It cannot remove `EndConversation` while any other tool remains. It is not part of the standard upload schema.
- `model` applies for the current turn, is not saved to settings, accepts the same values as `/model` or `inherit`, and is subject to the organization's `availableModels` allowlist. With `context: fork`, it selects the forked subagent's model.
- `effort` applies for the current turn and overrides session effort, but not `CLAUDE_CODE_EFFORT_LEVEL`. With `context: fork`, it sets the forked subagent's effort. Documented values are `low`, `medium`, `high`, `xhigh`, and `max`, subject to model availability.
- `background` applies only with `context: fork`. `false` waits for the forked subagent's result; the default is `true`. Backgrounded forks use the narrower tool set that applies to background subagents.
- `paths` patterns are relative to Claude Code's current working directory. Files outside that directory do not match; a sibling worktree is not automatically included merely because it was added with `/add-dir`. Command files do not accept `paths`.
- `metadata` must be a YAML map for Claude Code to retain it; a non-map value is dropped. Claude Code does not act on its contents. Do not reuse frontmatter field names such as `paths` as metadata keys. The standard describes metadata as a string-to-string map and recommends reasonably unique key names.
- `license` is accepted by Claude Code but not acted on there. The standard permits a license name or a reference to a bundled license file; keep it short.
- `compatibility` is accepted by Claude Code but not acted on there. The standard allows 1–500 characters and describes environment requirements such as intended product, system packages, or network access. Include it only when there are specific environment requirements. It is not a replacement for the detailed operational instructions in the `SKILL.md` body.
- `allowed-tools` is a pre-approval mechanism, not a tool-availability restriction. It does not itself remove tools from the model's pool. Deny and ask rules can still override it. It is experimental in the standard and support may vary by implementation.
- In Claude Code v2.1.282 and later, `allowManagedPermissionRulesOnly` can cause `allowed-tools` grants to be ignored in project and personal skills. `strictPluginOnlyCustomization` can also affect whether a skill's frontmatter hooks and `allowed-tools` are retained; evaluate the actual policy and skill source type.
- In eval runs, neither a case's `allowed_tools` nor a skill's `allowed-tools` can widen the tools permitted by the eval configuration.
- `hooks` in skill frontmatter are registered when the skill is invoked and can remain active for the rest of the session, including later turns. `once: true` is honored for skill-frontmatter hooks and removes a hook after its first successful run; it is ignored in settings files and agent frontmatter. Project-skill frontmatter hooks follow the workspace trust rule for hooks in settings, including the documented `-p` behavior.
- Hook limits in Claude Code v2.1.304 or later are per skill source per session: each source can register at most 1,024 hooks, and their matchers can total at most 16,384 characters. Project skills, personal skills, and each plugin are separate sources. Under `strictPluginOnlyCustomization`, a skill retains frontmatter hooks only when it is a plugin skill, bundled skill, or skill in the managed settings directory. An `ask` prompt labels a hook from skill frontmatter as `[skill]`.
- A skill with `disable-model-invocation: true` cannot be preloaded into a subagent because preloading draws from the set of skills Claude can invoke.

When auditing a field, record its scope, default, lifetime, policy interaction, and target acceptance separately. Do not compress "accepted by parser", "has runtime effect", and "accepted by upload schema" into one yes/no property.

## 13.3 API upload metadata (size limits) — original lines 1281-1283

### 13.3 API upload metadata and request limits

`display_name` and the Skills API, Managed Agents and plugin upload limits are not `SKILL.md` frontmatter fields; never insert them into the YAML block. Their values and which surface each applies to are in `size-limits-and-budgets.md` §7–§8.

## 13.4 Naming and collisions (frontmatter-description; precedence kept in runtime-contract) — original lines 1285-1296

### 13.4 Naming, invocation, and collisions

- In a personal or project skill directory, the frontmatter `name` controls the slash-menu command when set; otherwise the directory name is used. The directory name can still invoke the skill when a different `name` is set.
- In a plugin skill, the plugin prefix remains and `name` replaces the final command segment. For example, a plugin skill under `my-plugin/skills/review/` normally appears as `/my-plugin:review`; setting `name: audit` changes the final segment to `/my-plugin:audit`.
- If `name` already includes the plugin prefix, Claude Code v2.1.246 and later does not add the prefix twice. Versions v2.1.216 through v2.1.245 did double it. Treat this as a version-specific historical behavior, not a current naming recommendation.
- A single skill at the plugin root can load without a `skills/` directory or manifest `skills` key. Set its `name` explicitly; otherwise a marketplace install can name it after the cache directory rather than the plugin.
- Avoid a skill folder named `synced` in any capitalization. Outside a plugin, a folder or command named `anthropic-skills`, or beginning with `anthropic-skills:`, does not load.
- Claude Code refuses command names/frontmatter names containing control or zero-width characters, private-use or unassigned characters, direction-changing characters, whitespace other than a single plain space between words, or angle brackets. In a plugin `skills/` folder, such characters in the folder name become hyphens in the command name.
- Standard and platform naming guidance requires lowercase alphanumeric characters and hyphens, 1–64 characters, no leading/trailing hyphen, no consecutive hyphens, and a directory match. Claude Code permits a different frontmatter `name` from the directory and uses it as a command override. For portability, match the directory and `name` unless the Claude Code-only override is intentional and documented.
- The source recommends gerund names as one option, while also allowing noun phrases and action-oriented names. Avoid vague names (`helper`, `utils`, `tools`), generic names (`documents`, `data`, `files`), reserved brand terms, and inconsistent naming within a skill collection.
- Enterprise, personal, and project precedence differs across sources. Plugin skills are namespaced and can coexist with ordinary skills. Do not generalize precedence across clients. Skills-directory plugin conflicts can cause an installed or synced plugin copy to be reported as not loaded. Inspect the actual runtime's loaded/not-loaded report.
- Managed Agents repository skills can coexist with attached skills and skills from other mounted repositories; each is announced with its path.

## 13.11 Security and isolation (security) — original lines 1390-1397

### 13.11 Security and isolation checks

- Treat broad filesystem globs, paths outside the skill directory, and path traversal (`../`) as filesystem-scope risks. The cited platform risk assessment classifies unintended filesystem access scope as Medium; adjust severity to the actual consequence and target.
- MCP server references extend access beyond the skill itself. Verify each fully qualified server/tool dependency and the permissions it exposes; the cited platform risk assessment classifies MCP references as High review risk, but this is a review tier, not an automatic finding severity.
- Test whether the skill works in isolation. A skill that references files not included in its own directory may fail when detached from its development repository or installed elsewhere.
- Keep packages local to the skill/runtime where possible; do not install packages globally into the user's machine when the runtime supports a local installation.
- Never put API keys, passwords, tokens, or other credentials in skill content or distributed scripts. Use environment variables or secure credential stores. Files distributed in a plugin are received by every person who installs that plugin.
- The cited risk tiers are assessment guidance, not automatic severity labels. A broad path or MCP dependency must be evaluated for actual access, exposure, and impact before classifying the finding.

## 12. Overall verdict rules (deleted: shared verdict replaces it) — original lines 1228-1237

## 12. Overall verdict rules

The overall verdict summarizes release readiness; it does not replace individual severities. Apply these rules:

- **PASS:** all mandatory requirements for the declared target are met; the core workflow and relevant failure paths have been tested; no unresolved finding materially affects correctness, safety, or operation. Low-severity improvements may remain if they do not undermine the declared capability.
- **PASS WITH CONDITIONS:** the skill is usable on the named target, but specific bounded conditions remain. State each condition, its owner or dependency if known, and the exact restriction on use. Do not use this verdict for a mandatory contract violation or a critical unresolved risk.
- **FAIL:** a mandatory requirement is violated, a core capability cannot work as declared, a material safety/security issue remains, or the artifact cannot be deployed on its declared target.
- **NOT VERIFIABLE:** available files or test access are insufficient to establish whether the skill meets the target contract. State precisely what evidence is missing. This is not a pass and must not be presented as one.

When auditing multiple targets, report a verdict for each target and then a portfolio-level verdict. The portfolio-level verdict cannot be PASS if any required target fails.
