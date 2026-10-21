# Hook audit: <scope>

**Claude Code version:** <`claude --version`, or "not provided">
**Verified against:** docs sections <list, fetched YYYY-MM-DD> · changelog <user's version>→<latest> · or "<source> not reachable: version-sensitive claims marked unverified"
**Verdict:** <ready | ready with risks | not ready> — <one sentence why>

## Hooks reviewed

| # | Event | Type | Source | Runs when |
| :-- | :-- | :-- | :-- | :-- |
| 1 | `Stop` | prompt | `.claude/settings.json` | Trusted interactive sessions and `-p` |

## Findings

### <severity> (<impact>): <short title>

- **Where:** <file:line>
- **Evidence:** <the line, field or log entry>
- **Why it matters:** <the behavior it causes, with the doc section>
- **Fix:**

```json
<complete corrected handler>
```

## Checklist

| Section | Pass | Fail | n/a |
| :-- | :-- | :-- | :-- |
| A. Every hook | | | |
| B. Prompt and agent | | | |
| C. Background | | | |
| D. Scripts and security | | | |
| E. PowerShell | | | |
| F. Evidence | | | |
| G. Configuration | | | |
| H. Input and output | | | |
| I. Events and wiring | | | |
| J. Mods | | | |

## Not covered

<out-of-scope parts the hooks touch, one line each, or "None">

## Sources

- <doc section links>
