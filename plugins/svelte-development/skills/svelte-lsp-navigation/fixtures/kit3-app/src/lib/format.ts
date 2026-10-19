/** Formats a count for display; called from several components. */
export function formatCount(count: number): string {
  return count === 1 ? "1 click" : `${count} clicks`;
}
