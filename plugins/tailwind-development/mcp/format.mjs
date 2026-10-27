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

/** @param {Fix} fix */
const replacement = (fix) =>
  `line ${fix.line}: replace ${JSON.stringify(fix.oldText)} with ${JSON.stringify(fix.newText)}`

/** The first quoted name at the start of a diagnostic message. */
const LEADING_QUOTED_NAME = /^'([^']+)'/u

/**
 * The class a cssConflict diagnostic is about: the first quoted name of its message, as in
 * "'flex' applies the same CSS properties as 'block'."
 * @param {Finding} finding
 */
const conflictClass = (finding) => LEADING_QUOTED_NAME.exec(finding.message)?.[1] ?? finding.message

/**
 * Groups the findings to list: the server reports a class conflict once per class involved, each
 * with a fix that keeps that class and deletes the others. Those alternatives exclude each other,
 * so they become one entry to choose from, keyed by the class list their fixes rewrite.
 * @param {readonly Finding[]} findings
 * @returns {Finding[][]}
 */
function entries(findings) {
  /** @type {Map<string, Finding[]>} */
  const conflicts = new Map()
  /** @type {Finding[][]} */
  const list = []
  for (const finding of findings) {
    const fix = finding.fixes[0]
    if (finding.rule !== 'cssConflict' || fix === undefined) {
      list.push([finding])
      continue
    }
    const key = `${fix.line}:${fix.oldText}`
    const group = conflicts.get(key)
    if (group === undefined) {
      const created = [finding]
      conflicts.set(key, created)
      list.push(created)
    } else {
      group.push(finding)
    }
  }
  return list
}

/**
 * The findings as plain text, one entry per problem, with each fix's exact replacement. A class
 * conflict lists one alternative per class it could keep.
 * @param {string} relativePath
 * @param {readonly Finding[]} findings
 */
export function findingsText(relativePath, findings) {
  if (findings.length === 0) {
    return `Tailwind CSS: no diagnostics in ${relativePath}.`
  }
  const all = entries(findings)
  const shown = all.slice(0, MAX_DIAGNOSTICS)
  const lines = [
    `Tailwind CSS diagnostics in ${relativePath} (${all.length}). Each fix is the language server's exact replacement:`,
  ]
  for (const group of shown) {
    const [first] = group
    if (first === undefined) {
      continue
    }
    const where = `${relativePath}:${first.line}:${first.column} ${first.severity} [${first.rule}]`
    if (group.length > 1) {
      const names = group.map((f) => `'${conflictClass(f)}'`).join(', ')
      lines.push(
        `- ${where} ${names} apply the same CSS properties. Keep one: apply only the fix of the class you keep.`,
      )
      group.forEach((finding, index) => {
        const fix = finding.fixes[0]
        if (fix !== undefined) {
          lines.push(
            `  ${String.fromCodePoint(97 + index)}) keep '${conflictClass(finding)}' (${fix.title}), ${replacement(fix)}`,
          )
        }
      })
      continue
    }
    lines.push(`- ${where} ${first.message}`)
    for (const fix of first.fixes) {
      lines.push(`  fix (${fix.title}), ${replacement(fix)}`)
    }
  }
  if (all.length > shown.length) {
    lines.push(
      `… and ${all.length - shown.length} more; call check_file to list them after fixing these.`,
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
