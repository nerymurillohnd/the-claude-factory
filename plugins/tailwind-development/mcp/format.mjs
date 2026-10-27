// Turns the language server's diagnostics into the text Claude reads, as a tool result or as the
// additionalContext of the PostToolUse hook.

/** Diagnostics listed in one answer; the rest are counted. */
export const MAX_DIAGNOSTICS = 30

/**
 * @typedef {object} Fix
 * @property {string} title the server's quick-fix title, such as "Replace with 'mx-auto'"
 * @property {number} line 1-based
 * @property {string} oldText
 * @property {string} newText
 */

/**
 * @typedef {object} Finding
 * @property {number} line 1-based
 * @property {number} column 1-based
 * @property {'error' | 'warning' | 'information' | 'hint'} severity
 * @property {string} rule the server's diagnostic code, such as cssConflict
 * @property {string} message
 * @property {Fix[]} fixes
 */

/**
 * The findings as plain text, one block per finding, with each fix's exact replacement.
 * @param {string} relativePath
 * @param {readonly Finding[]} findings
 */
export function findingsText(relativePath, findings) {
  if (findings.length === 0) {
    return `Tailwind CSS: no diagnostics in ${relativePath}.`
  }
  const shown = findings.slice(0, MAX_DIAGNOSTICS)
  const lines = [
    `Tailwind CSS diagnostics in ${relativePath} (${findings.length}). Apply each fix with Edit:`,
  ]
  for (const finding of shown) {
    lines.push(
      `- ${relativePath}:${finding.line}:${finding.column} ${finding.severity} [${finding.rule}] ${finding.message}`,
    )
    for (const fix of finding.fixes) {
      lines.push(
        `  fix (${fix.title}), line ${fix.line}: replace ${JSON.stringify(fix.oldText)} with ${JSON.stringify(fix.newText)}`,
      )
    }
  }
  if (findings.length > shown.length) {
    lines.push(
      `… and ${findings.length - shown.length} more; call check_file to list them after fixing these.`,
    )
  }
  return lines.join('\n')
}

/**
 * The PostToolUse hook output: the findings as additionalContext. Without findings it is empty, so
 * the hook adds nothing, unless the file's previous check had findings: then it says the file is
 * clean now, so Claude knows its fix worked instead of reading silence.
 * @param {string} relativePath
 * @param {readonly Finding[]} findings
 * @param {boolean} [hadFindings] whether the previous check of this file reported any
 */
export function findingsHookOutput(relativePath, findings, hadFindings = false) {
  if (findings.length === 0 && !hadFindings) {
    return ''
  }
  return JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'PostToolUse',
      additionalContext:
        findings.length === 0
          ? `Tailwind CSS: no diagnostics left in ${relativePath}.`
          : findingsText(relativePath, findings),
    },
  })
}

/** @type {Readonly<Record<number, Finding['severity']>>} */
const SEVERITIES = { 1: 'error', 2: 'warning', 3: 'information', 4: 'hint' }

/**
 * @param {number | undefined} severity LSP DiagnosticSeverity
 * @returns {Finding['severity']}
 */
export function severityName(severity) {
  return (severity === undefined ? undefined : SEVERITIES[severity]) ?? 'warning'
}
