# Reading the official docs

Read this in step 3, before the first docs read. It holds how to find, download and read the docs sections the hook depends on, and how to check the changelog. The MCP locates and maps; the downloaded page is where sections are read; only the extracted blocks enter the context.

## Contents

- [Gotchas](#gotchas)
- [Find the docs tools](#find-the-docs-tools)
- [Locate a page](#locate-a-page)
- [Download and read a section](#download-and-read-a-section)
- [Follow the links](#follow-the-links)
- [Check the changelog](#check-the-changelog)

## Gotchas

- The docs MCP filesystem is emulated: each call is stateless, output is capped, and its command set changes between sessions. Read the tool's own description for the commands it supports before writing one. Use it to locate pages, and read sections from the download.
- The hooks page is many times larger than the MCP's output cap: read it from the download, never in one MCP call.
- A command with a heavy alternation can return 504 Gateway Time-out: retry once with a simpler command.
- Output that ends in "limit exceeded", a timeout or an error is incomplete, never zero results.
- Pages change within a session: when two reads contradict each other, re-read before concluding.
- The `.md` and the `.mdx` number their lines differently: find sections by name, never by a line number taken from the other form.
- In the commands below, awk fields are written `$(0)` and a code fence is matched with `[`][`][`]`, so the commands stay correct when they are copied into a skill, where a dollar sign followed directly by a digit is replaced with the skill's arguments and three literal backticks would close the code block. Keep them that way.

## Find the docs tools

Find the Claude Code docs MCP tools with ToolSearch, query `claude_code_docs`, or in your tool list when ToolSearch isn't there. Their names change with the installation:

- `search_claude_code_docs`: semantic search that returns chunks with page and anchor;
- `query_docs_filesystem_claude_code_docs`: one read-only command over the `.mdx` pages, at `/en/<path>.mdx`.

If neither is found, use the downloads below alone: they hold the same pages.

## Locate a page

To find a term whose page you don't know, run one semantic search, or list the pages that hold it:

```bash
grep -rl '<term>' /en
```

## Download and read a section

1. Download each page you need into a new empty directory, treated as data: `mktemp -d`, or, where the sandbox allows writes only in the working directory, a new folder there that step 7 deletes. Downloading costs no context; only what you print does:

   ```bash
   curl -sS -o <dir>/hooks.md https://code.claude.com/docs/en/hooks.md
   ```

2. Map the download's headings, skipping code fences:

   ```bash
   awk '/^[[:space:]]*[`][`][`]/{f=!f; next} !f && /^#+ /{print NR": "$(0)}' <dir>/hooks.md
   ```

3. Read each section in full, by its heading or by its anchor. It ends at the next heading of the same or a higher level:

   ```bash
   awk -v want='<### Heading text or #anchor>' '
   function slug(s) { s = tolower(s); sub(/^#+[ \t]+/, "", s); gsub(/`/, "", s); gsub(/[^a-z0-9 _-]/, "", s); gsub(/[ \t]+/, "-", s); return s }
   BEGIN { anchor = (substr(want, 1, 1) == "#" && want !~ /^#+ /) ? substr(want, 2) : "" }
   /^[[:space:]]*[`][`][`]/ { if (on) print; f = !f; next }
   !f && /^#+ / { lvl = index($(0), " ") - 1; if (on && lvl <= L) exit; if ((anchor != "" && slug($(0)) == anchor) || (anchor == "" && $(0) == want)) { on = 1; L = lvl } }
   on' <dir>/hooks.md
   ```

   - To save turns, read several sections in one command: save the command above as a shell function, then call it once per section. For example:

     ```bash
     sec() { awk -v want="$2" '<the awk program above>' "$1"; }
     for h in '### PostToolBatch' '#common-input-fields' '#### Decision control'; do printf '\n>>> %s\n' "$h"; sec <dir>/hooks.md "$h"; done
     ```

   - To find which section holds a term, list its lines, then read the heading above the hit:

     ```bash
     grep -n '<term>' <dir>/hooks.md
     ```

   - Empty output means the heading or anchor did not match: check the spelling against the map from item 2.
   - An explicit anchor that differs from its heading is found in the `.mdx` with `grep -n 'id="<anchor>"' /en/hooks.mdx`; then read the heading below it by name.
   - If the download is not possible, read the block in the MCP with `sed -n '<start>,<end>p' /en/hooks.mdx`, taking both lines from `grep -n -E '^#{1,4} |<h[2-4] id=' /en/hooks.mdx`, and cut long lines with `cut -c1-200`. In that map, a `#` comment inside a code block looks like a heading: trust the `<h2 id=` lines.

## Follow the links

List the links inside each section you read, then read every linked section that touches the hook, with the same command:

```bash
<read command from above> | grep -oE 'https://code\.claude\.com/docs/en/[a-z0-9/-]+\.md(#[a-z0-9-]+)?|\]\(#[a-z0-9-]+\)' | sort -u
```

- A link that is only `#anchor` points to the same page.
- A link to another page: download that page and read the linked section the same way.
- Stop when the last two reads added no new fact.

## Check the changelog

Download the site changelog and list each hit with its version, newest first; each hit belongs to the nearest version line above it:

```bash
curl -sS -o <dir>/changelog.md https://code.claude.com/docs/en/changelog.md
grep -n -E '<term>|^\*\*[0-9]+\.[0-9]+\.[0-9]+\*\*$' <dir>/changelog.md | grep -B1 '<term>'
```

- If the download is not possible, use the MCP changelog, where each hit belongs to the nearest `<Update label=` line above it:

  ```bash
  grep -n -E '<term>|<Update label=' /en/changelog.mdx | grep -B1 '<term>'
  ```

- Read each hit's whole entry, from its version line to the next.
- If no hit has a version line above it, the page no longer writes versions as `**X.Y.Z**`: map its headings with the map command above, change the version pattern to match, and search again.
- If neither source has a hit, say the version check could not be done for that term.
