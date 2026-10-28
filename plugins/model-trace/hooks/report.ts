import {
  formatDate,
  formatSpan,
  formatTime,
  type Row,
  SECTIONS,
  type Summary,
  sectionLabel,
  timeZone,
} from './model'

/** Why the Plugins section is not added to the totals. */
export const ROLLUP =
  "Regroups the uses of each plugin's skills, agents and MCP servers counted above; not added to the totals. A plugin's hooks are not attributed to it: Claude Code doesn't tell mods which plugin a hook belongs to."

/** `1 use`, `2 uses`: a count with its noun. */
const count = (n: number, noun: string, plural = `${noun}s`): string =>
  `${n} ${n === 1 ? noun : plural}`

const cell = (text: string): string => text.replaceAll('|', '\\|').replaceAll('\n', ' ')
const nounOf = (kind: string): string => SECTIONS.find((s) => s.kind === kind)?.noun ?? kind

/** Every use in time order, for the timeline of both reports. */
function timeline(summary: Summary): Array<{ at: number; noun: string; row: Row }> {
  const events: Array<{ at: number; noun: string; row: Row }> = []
  for (const section of summary.sections) {
    if (section.rollup) {
      continue
    }
    for (const row of section.rows) {
      for (const at of row.times) {
        events.push({ at, noun: nounOf(section.kind), row })
      }
    }
  }
  return events.sort((a, b) => a.at - b.at)
}

/** The capability used most, for the headline. */
function mostUsed(summary: Summary): Row | undefined {
  return summary.sections
    .filter((section) => !section.rollup)
    .flatMap((section) => section.rows.filter((row) => !row.derived))
    .sort((a, b) => b.count - a.count)[0]
}

/** The session's report as Markdown. */
export function toMarkdown(summary: Summary, now: number): string {
  const top = mostUsed(summary)
  const lines = [
    '# Model Trace',
    '',
    `- **Date:** ${formatDate(now)} (${timeZone()})`,
    `- **Tracked:** ${formatTime(summary.since)} to ${formatTime(now)} (${formatSpan(now - summary.since)})`,
    `- **Used:** ${count(summary.capabilities, 'capability', 'capabilities')}, ${count(summary.uses, 'use')}`,
    ...(top ? [`- **Most used:** ${top.name} (${top.count})`] : []),
    '',
  ]
  if (summary.sections.length === 0) {
    lines.push('Claude used no skill, agent, MCP server, hook or web tool in this session.', '')
  }
  for (const section of summary.sections) {
    lines.push(`## ${section.title}: ${sectionLabel(section)}`, '')
    if (section.rollup) {
      lines.push(`_${ROLLUP}_`, '')
    }
    lines.push(`| ${nounOf(section.kind)} | Origin | Uses | Times |`, '| :-- | :-- | --: | :-- |')
    for (const row of section.rows) {
      const note = row.note ? ` (${row.note})` : ''
      lines.push(
        `| ${cell(row.name)}${cell(note)} | ${cell(row.origin)} | ${row.count} | ${row.times.map(formatTime).join(', ')} |`,
      )
    }
    lines.push('')
  }
  const events = timeline(summary)
  if (events.length > 0) {
    lines.push('## Timeline', '', '| Time | Kind | Name | Origin |', '| :-- | :-- | :-- | :-- |')
    for (const { at, noun, row } of events) {
      lines.push(`| ${formatTime(at)} | ${noun} | ${cell(row.name)} | ${cell(row.origin)} |`)
    }
    lines.push('')
  }
  return lines.join('\n')
}

const escapeHtml = (text: string): string =>
  text
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')

const STYLE = `
:root{--bg:#faf9f7;--card:#ffffff;--text:#1f1e1c;--muted:#6b6862;--line:#e7e4de;--accent:#c96442;--chip:#f1efeb}
@media (prefers-color-scheme:dark){:root{--bg:#1a1917;--card:#23221f;--text:#ecebe8;--muted:#a19e97;--line:#3a3833;--accent:#e08a6a;--chip:#2e2d29}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:960px;margin:0 auto;padding:40px 16px 64px}
h1{font-size:28px;margin:0 0 4px;letter-spacing:-.01em}
.sub{color:var(--muted);margin:0 0 28px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:12px;margin-bottom:28px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;min-width:0}
.kpi b{display:block;font-size:24px;font-variant-numeric:tabular-nums;overflow-wrap:break-word}
.kpi span{color:var(--muted);font-size:13px;overflow-wrap:break-word}
section{min-width:0;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:16px}
section h2{display:flex;justify-content:space-between;align-items:baseline;gap:12px;font-size:17px;margin:0 0 10px}
section h2 small{color:var(--muted);font-weight:500;font-size:13px;white-space:nowrap}
.bar{height:6px;border-radius:3px;background:var(--chip);overflow:hidden;margin-bottom:14px}
.bar i{display:block;height:100%;background:var(--accent)}
.scroll{overflow-x:auto;max-width:100%}
table{width:100%;border-collapse:collapse;font-size:14px}
th{text-align:left;color:var(--muted);font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.04em;padding:6px 8px;border-bottom:1px solid var(--line)}
td{padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top;overflow-wrap:break-word}
tr:last-child td{border-bottom:0}
td.n{text-align:right;font-variant-numeric:tabular-nums;color:var(--accent);font-weight:600}
td.t,td.time{color:var(--muted);font-variant-numeric:tabular-nums;font-size:13px}
.origin{color:var(--muted);font-size:13px}
.nw,td.n,td.time{white-space:nowrap}
.note{display:block;color:var(--muted);font-size:12px}
.rollup{color:var(--muted);font-size:13px;margin:0 0 12px}
.empty{color:var(--muted)}
footer{color:var(--muted);font-size:12px;margin-top:24px}
`

/** The session's report as one self-contained HTML page: no script, no external resource. */
export function toHtml(summary: Summary, now: number): string {
  const top = mostUsed(summary)
  const sections = summary.sections
    .map((section) => {
      // A bar shows the section's share of the totals, so rows left out of them don't fill it.
      const counted = section.rows
        .filter((row) => !row.derived)
        .reduce((n, row) => n + row.count, 0)
      const share = summary.uses ? Math.min(100, Math.round((counted / summary.uses) * 100)) : 0
      const rows = section.rows
        .map(
          (row) =>
            `<tr><td>${escapeHtml(row.name)}${row.note ? `<span class="note">${escapeHtml(row.note)}</span>` : ''}</td><td class="origin">${escapeHtml(row.origin)}</td><td class="n">${row.count}</td><td class="t">${row.times.map((at) => `<span class="nw">${formatTime(at)}</span>`).join(' · ')}</td></tr>`,
        )
        .join('')
      const rollup = section.rollup ? `<p class="rollup">${escapeHtml(ROLLUP)}</p>` : ''
      const bar = section.rollup
        ? ''
        : `<div class="bar" title="${share}% of all uses"><i style="width:${share}%"></i></div>`
      return `<section><h2>${escapeHtml(section.title)}<small>${sectionLabel(section)}</small></h2>${bar}${rollup}<div class="scroll"><table><thead><tr><th>${nounOf(section.kind)}</th><th>Origin</th><th style="text-align:right">Uses</th><th>Times</th></tr></thead><tbody>${rows}</tbody></table></div></section>`
    })
    .join('')
  const events = timeline(summary)
  const timelineHtml = events.length
    ? `<section><h2>Timeline<small>${events.length} entries</small></h2><div class="scroll"><table><thead><tr><th>Time</th><th>Kind</th><th>Name</th><th>Origin</th></tr></thead><tbody>${events
        .map(
          ({ at, noun, row }) =>
            `<tr><td class="time">${formatTime(at)}</td><td>${noun}</td><td>${escapeHtml(row.name)}</td><td class="origin">${escapeHtml(row.origin)}</td></tr>`,
        )
        .join('')}</tbody></table></div></section>`
    : ''
  const empty =
    summary.sections.length === 0
      ? '<p class="empty">Claude used no skill, agent, MCP server, hook or web tool in this session.</p>'
      : ''
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Model Trace · ${formatDate(now)}</title><style>${STYLE}</style></head>
<body><main><h1>Model Trace</h1><p class="sub">${formatDate(now)} · ${formatTime(summary.since)} to ${formatTime(now)} · ${escapeHtml(timeZone())}</p>
<div class="kpis"><div class="kpi"><b>${summary.capabilities}</b><span>${summary.capabilities === 1 ? 'capability' : 'capabilities'} used</span></div><div class="kpi"><b>${summary.uses}</b><span>${summary.uses === 1 ? 'use' : 'uses'}</span></div><div class="kpi"><b>${formatSpan(now - summary.since)}</b><span>tracked</span></div><div class="kpi"><b>${top ? top.count : 0}</b><span>${top ? `${top.count === 1 ? 'use' : 'uses'} of ${escapeHtml(top.name)}` : 'most used'}</span></div></div>
${empty}${sections}${timelineHtml}<footer>Made by the Model Trace plugin. Names and counts only: no commands, arguments or prompts.</footer></main></body></html>
`
}
