/** What the pane shows in its body: the tree, one file's content, or a diff. */
export type FileTreeView =
  | { kind: 'tree' }
  | { kind: 'preview'; path: string }
  | { kind: 'diff'; path: string; isDir: boolean }

/** The right column of the tree: modification date, age, or size. */
export type FileTreeColumn = 'date' | 'age' | 'size'

declare module 'claude-code' {
  interface PluginState {
    'file-tree-pane': {
      /** The folder the tree shows, absolute. */
      root: string
      /** Whether `/file-tree <path>` pinned the root, so it no longer follows the cwd. */
      isPinned: boolean
      /** Expanded folders, as paths relative to the root. */
      expanded: string[]
      /** The selected row's path relative to the root, or null. */
      selected: string | null
      view: FileTreeView
      /**
       * What the right column shows once the Σ button switched it, or null for the Right column
       * setting; null too after `/clear`, so the setting applies again.
       */
      column: FileTreeColumn | null
      /** The search the person typed. */
      query: string
    }
  }
}
