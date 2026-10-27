// Finding files by name anywhere under the root, folders never opened included.

import { baseName } from './tree.ts'

// 0 for a name that starts with the needle, 1 for a name that holds it, 2 for a path that
// holds it, -1 for no match. All three are lowercase.
const scoreOf = (name: string, path: string, needle: string): number => {
  if (name.startsWith(needle)) {
    return 0
  }
  if (name.includes(needle)) {
    return 1
  }
  if (path.includes(needle)) {
    return 2
  }
  return -1
}

/**
 * Paths that hold `query`, case-blind, best first: a name that starts with it, then a name
 * that holds it, then a path that holds it; shorter paths first within each.
 */
export const searchPaths = (paths: readonly string[], query: string, limit: number): string[] => {
  const needle = query.trim().toLowerCase()
  if (needle === '') {
    return []
  }
  const scored: { path: string; score: number }[] = []
  for (const path of paths) {
    const lower = path.toLowerCase()
    const name = baseName(lower)
    const score = scoreOf(name, lower, needle)
    if (score !== -1) {
      scored.push({ path, score })
    }
  }
  scored.sort(
    (a, b) => a.score - b.score || a.path.length - b.path.length || (a.path < b.path ? -1 : 1),
  )
  return scored.slice(0, limit).map((hit) => hit.path)
}
