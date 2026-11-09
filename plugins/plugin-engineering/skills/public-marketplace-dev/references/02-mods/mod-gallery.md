# Interface gallery for mods

The interface elements a Claude Code mod can draw, such as text, buttons, fields, Markdown, code, and diffs, with sample code and descriptions of terminal screenshots.

## Contents

- [Try a sample](#try-a-sample)
- [Pick an element](#pick-an-element)
- [Show text](#show-text)
  - [`Text`](#text)
  - [`Markdown`](#markdown)
  - [`Link`](#link)
- [Show code and changes](#show-code-and-changes)
  - [`Code`](#code)
  - [`Code` as a diff](#code-as-a-diff)
- [Arrange elements](#arrange-elements)
  - [`Box`](#box)
- [Take input](#take-input)
  - [`Button`](#button)
  - [`Input`](#input)
  - [`Select`](#select)
- [Draw pictures](#draw-pictures)
  - [`Raster`](#raster)
  - [`Svg`](#svg)
  - [`Image` and `Client`](#image-and-client)
    - [Draw an `Image` inside tmux](#draw-an-image-inside-tmux)
- [See where a mod can draw](#see-where-a-mod-can-draw)
- [Documentation References](#documentation-references)

A mod draws its interface from elements: text, boxes, buttons, fields, and a few that format content for the mod. The samples here show the code that draws an element, and most come with a screenshot of the result in a terminal pane, so pick an element by how it looks. Each screenshot's alt text also describes the result.

To learn how drawing works, start with [Draw in the interface](https://code.claude.com/docs/en/plugins/mods/interface.md). For the main props and which apps draw each element, see the [elements reference](https://code.claude.com/docs/en/plugins/mods/reference.md#elements). The [type declarations](https://code.claude.com/docs/en/plugins/mods/create.md#get-the-types-for-your-build) list every prop.

## Try a sample

The samples on this page are snippets, not whole mods. Each one is the code for one element and anything nested inside it.

To see a sample in a terminal, create the small mod in these steps and paste the sample into it. The mod adds a `/gallery` command that opens a pane and draws the sample there. A [pane](https://code.claude.com/docs/en/plugins/mods/interface.md#pick-where-to-draw) is a sidebar beside the transcript in a wide fullscreen terminal, or a framed region above the prompt otherwise.

**1. Create the mod**

Create a directory named `gallery` with `.claude-plugin` and `hooks` directories inside it. [Create a mod](https://code.claude.com/docs/en/plugins/mods/create.md#write-a-mod-yourself) explains the files.

Save the manifest as `gallery/.claude-plugin/plugin.json`:

```json gallery/.claude-plugin/plugin.json theme={null}
{
  "name": "gallery",
  "version": "0.1.0",
  "description": "Opens a pane that draws one sample",
  "author": { "name": "Your Name" }
}
```

Name the entry point in `gallery/hooks/hooks.json`:

```json gallery/hooks/hooks.json theme={null}
{
  "modules": ["./register.js"]
}
```

Save the code as `gallery/hooks/register.js`. It adds a `/gallery` command that opens a pane, and draws `Plain text` in that pane:

```javascript gallery/hooks/register.js theme={null}
// Stands in for your own callback in the samples that take one
const noop = () => {}
// The Select sample keeps its choice here
let picked = 'md'

// The Raster sample packs its cells with this function
const DEFAULT_COLOR = 0x01000000
function cellsOf(rows) {
  const numbers = rows.flat().flatMap(([char, color]) => [char.codePointAt(0), color, DEFAULT_COLOR])
  return new Uint8Array(Uint32Array.from(numbers).buffer).toBase64()
}

export function register(on) {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'gallery', description: 'Open the sample pane' })
    return next(e)
  })

  on('command.run', { command: 'gallery' }, async ($) => {
    await $.ui.open({ id: 'gallery', focus: true, closeOnEscape: true })
    return {}
  })

  on('ui.render', { component: 'Pane' }, async ($, e, next) => {
    if (e.requestId !== 'gallery') return next(e)
    const { Box, Text, Button, Input, Select, Link, Markdown, Code, Raster, Svg } = $.ui.resolve(e)
    // Replace the element after return with a sample
    return Text({ children: ['Plain text'] })
  })
}
```

**2. Run the mod**

In the shell, start Claude Code from the directory that holds `gallery`:

```bash theme={null}
claude --plugin-dir ./gallery
```

At the Claude Code prompt, run `/gallery`. A pane opens with `Plain text` in it.

**3. Swap in a sample**

Copy a sample from this page. In `register.js`, paste it over `Text({ children: ['Plain text'] })`, so that it follows `return`, and save the file. Claude Code reloads the module on each save, so run `/gallery` again to see the new sample.

## Pick an element

The samples are grouped by what goes on screen:

* **[Show text](#show-text)**: `Text`, `Markdown`, and `Link`
* **[Show code and changes](#show-code-and-changes)**: `Code`
* **[Arrange elements](#arrange-elements)**: `Box`
* **[Take input](#take-input)**: `Button`, `Input`, and `Select`
* **[Draw pictures](#draw-pictures)**: `Raster`, `Svg`, `Image`, and `Client`

## Show text

Three elements put words on screen: `Text` for the mod's own styling, `Markdown` for content that's already formatted, and `Link` for a URL.

### `Text`

`Text` draws a string with the styles given to it. This sample shows plain text and eight styles, one on each line:

```javascript theme={null}
Box({
  flexDirection: 'column',
  children: [
    Text({ children: ['Plain text'] }),
    Text({ bold: true, children: ['bold'] }),
    Text({ italic: true, children: ['italic'] }),
    Text({ underline: true, children: ['underline'] }),
    Text({ strikethrough: true, children: ['strikethrough'] }),
    Text({ dimColor: true, children: ['dimColor'] }),
    Text({ inverse: true, children: ['inverse'] }),
    Text({ color: 'red', children: ["color: 'red'"] }),
    Text({ backgroundColor: 'blue', children: ["backgroundColor: 'blue'"] }),
  ],
})
```

![A pane with nine lines of text, each named for its style: plain, bold, italic, underline, strikethrough, dimColor in gray, inverse, color red, and backgroundColor blue.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-text-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=90724ce3953d9347b61b6a9266fda451)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. Monospaced, left-aligned text, one style per line, no blank rows: "Plain text" in regular black; "bold" in heavy black; "italic" slanted; "underline" with a line under the word; "strikethrough" with a line through the word; "dimColor" in medium gray; "inverse" as white letters on a black block exactly as wide as the word; "color: 'red'" in red letters on white; "backgroundColor: 'blue'" in dark letters on a bright blue fill that ends where the text ends, leaving the rest of that row white. The rest of the pane is empty.

`dimColor` draws the text in gray. `backgroundColor` fills only as wide as the text.

### `Markdown`

`Markdown` formats text the way Claude's replies are formatted. Pass the content in `text`, not in `children`:

```javascript theme={null}
Markdown({
  text: '## Release notes\n\nThis build has **two** fixes and one `flag`:\n\n- Faster start\n- Fewer prompts\n\n> Quoted text',
})
```

![A pane with a bold heading, Release notes, then a sentence with one bold word and one colored code word, a two-item list, and a quote drawn in italics with a bar on its left.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-markdown-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=e40eacc4e3fbe06eb003f4463f552ec1)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. From the top: "Release notes" in bold with no "##" marks; a blank row; "This build has two fixes and one flag:" in regular black, with "two" in bold and "flag" in blue-violet with no backticks; a blank row; "- Faster start" and "- Fewer prompts" on consecutive rows, each starting with a literal hyphen; a blank row; "Quoted text" in italics, indented by two columns, with a short vertical gray bar at the left edge of that row and no ">" mark.

A heading draws in bold without its `#` marks. Inline code draws in color without its backticks. A quote draws in italics with a bar on its left.

### `Link`

`Link` draws a label followed by its URL:

```javascript theme={null}
Link({ href: 'https://code.claude.com/docs', label: 'Claude Code docs' })
```

![A pane with one line: the label Claude Code docs, then the URL in gray.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-link-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=8217bd2dfb561a8ba57023c6d89ea977)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. A single row: "Claude Code docs" in black, one space, then "https://code.claude.com/docs" in gray. Neither part is underlined or otherwise styled; the rest of the row is empty.

The terminal draws the URL as text after the label. Whether a click opens it depends on the user's terminal.

## Show code and changes

`Code` draws source text with Claude Code's own syntax colors, or a diff. In the VS Code extension, `Code` shows its `source` as plain text, with none of the colors, line numbers, or diff shading in these screenshots.

### `Code`

Name the `language`, or pass a `path` for Claude Code to infer it from. With `startLine`, the lines are numbered from that number:

```javascript theme={null}
Code({
  language: 'javascript',
  startLine: 1,
  source: "const name = 'mods'\nconsole.log('hello ' + name)",
})
```

![A pane with two numbered lines of JavaScript in syntax colors.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-code-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=4e13f5d506d3fdcc59d6d9524f48d2a9)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. Two rows, each with a gray line number ("1", "2") left of the code. Row 1: "const name = 'mods'" with "const" in crimson, "name" and "=" in black, and "'mods'" in dark blue. Row 2: "console.log('hello ' + name)" with "console" in teal, "." in black, "log" in purple, "'hello '" in dark blue, and "(", "+", "name" and ")" in black.

The colors come from the user's theme.

### `Code` as a diff

With `format: 'diff'`, `source` is one or more unified diff hunks:

```javascript theme={null}
Code({
  format: 'diff',
  source: '@@ -1,3 +1,3 @@\n # Mods\n-A mod is a plugin.\n+A mod is a plugin that runs code.\n Read on.',
})
```

![A pane with a four-line diff. The removed line is shaded red and the added line green, each with its line number. In the added line, the words that runs code have a stronger shade.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-diff-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=4f12c9f7229ceccd9b4f47479a7235dd)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. Four rows, each starting with a line number: "1" in gray, then "# Mods" on white; "2" in red, then a red "-" and "A mod is a plugin." on a pale red band; "2" in green, then a green "+" and "A mod is a plugin that runs code." on a pale green band, where " that runs code" (with its leading space) sits on a darker green highlight and the final "." does not; "3" in gray, then "Read on." on white. The red and green bands stretch from the line number almost to the pane's right border. No "@@" header row is shown.

Claude Code draws line numbers in place of the `@@` line. Where a removed line and an added line are alike, the words that changed get a stronger shade.

## Arrange elements

### `Box`

`Box` lays out what's inside it in a row or a column, and can draw a border. This sample puts a row of words above a bordered box:

```javascript theme={null}
Box({
  flexDirection: 'column',
  gap: 1,
  children: [
    Box({
      flexDirection: 'row',
      columnGap: 4,
      children: [Text({ children: ['a row'] }), Text({ children: ['of three'] }), Text({ children: ['items'] })],
    }),
    Box({
      borderStyle: 'round',
      paddingX: 1,
      children: [Text({ children: ["borderStyle: 'round'"] })],
    }),
  ],
})
```

![A pane with three words in a row, four columns apart, then a blank row, then a rounded border around one line of text. The border runs the full width of the pane.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-box-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=cb9263bb02f5c8afb6e5b8450e0cdadc)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. First row: "a row", "of three", "items" in plain black, separated by equal gaps of about four character columns. Then one blank row. Then a nested box with a thin dark border and rounded corners, inset slightly from the pane's left and right edges so it spans nearly the full pane width, holding one row of text, "borderStyle: 'round'", with one column of padding before it. Nothing else is drawn.

The border stretches to the width of the pane.

## Take input

`Button`, `Input`, and `Select` are controls: the user moves between them with Tab and uses the one that has the focus. [Keyboard focus and hotkeys](https://code.claude.com/docs/en/plugins/mods/interface.md#know-which-keys-your-mod-can-receive) covers which keys reach them.

To request keyboard focus for a pane, open it with `focus: true`. Typed letters reach an `Input` once it has the focus. To choose which field has the focus when the pane opens, see [Set a hotkey and the first focus](https://code.claude.com/docs/en/plugins/mods/interface.md#set-a-hotkey-and-the-first-focus).

### `Button`

A button runs `onPress`. This sample shows the default form, a `plain` button with a hotkey, and a dim one:

```javascript theme={null}
Box({
  flexDirection: 'column',
  children: [
    Button({ key: 'save', label: 'Save', onPress: noop }),
    Button({ key: 'next', label: 'Next', hotkey: 'n', plain: true, onPress: noop }),
    Button({ key: 'skip', label: 'Skip', dimColor: true, onPress: noop }),
  ],
})
```

![A pane with three buttons, one per line: Save in brackets, n: Next without brackets and with the n in color, and Skip in brackets in gray.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-button-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=8c638c15e12d9736f327dfcaa797b512)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. Three left-aligned rows with no gaps: "[ Save ]" in bold black, brackets with one space on each side of the label; "n: Next" with the "n" in blue-violet and ": Next" in regular black, no brackets; "[ Skip ]" in bold gray, bracketed like Save. No button is highlighted.

A button that has the focus draws in inverse video. Here the user has pressed Tab twice:

![The same three buttons, with the second one, n: Next, drawn in inverse video.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-button-plain-focused-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=a6224e58d10752a894615047d9824ad9)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. Same three rows as the previous screenshot: "[ Save ]" bold black and "[ Skip ]" bold gray are unchanged. The middle row is highlighted: ": Next" is white on a black block that ends right after "Next", and the "n" cell is white on a blue-violet block, so the hotkey letter keeps its color as a background.

### `Input`

An `Input` is a text field that holds one line by default and runs `onSubmit` when the user presses Enter:

```javascript theme={null}
Input({
  key: 'title',
  label: 'Title',
  placeholder: 'Type a title and press Enter',
  value: '',
  submitLabel: 'save',
  onSubmit: noop,
})
```

Without the focus, the field shows its label and its placeholder:

![A pane with one line: the label Title, then the placeholder Type a title and press Enter in gray.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-input-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=7d580be1aaf5507032e1962b9167d725)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. A single row: "Title:" in regular-weight black, including the colon, one space, then "Type a title and press Enter" in gray. No cursor, no return sign and no "save" are shown.

With the focus, the label turns bold, a cursor appears, and the `submitLabel` shows after `⏎`:

![The same field with its label in bold, a block cursor on the first letter of the placeholder, and a return sign followed by the word save.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-input-focused-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=dcfcce0174480cc624d06c8521734fe7)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. A single row: "Title:" now in bold black; the first placeholder letter "T" drawn white on a black block cursor; the rest, "ype a title and press Enter", in gray; then a gray return-arrow sign "⏎" and the word "save" in dark gray, one space apart, directly after the placeholder.

Typing replaces the placeholder:

![The same field holding the typed letters Rel, followed by the return sign and the word save.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-input-typed-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=4eb6d4443763a21415dad4e426bc747a)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. A single row: "Title:" in bold black, then "Rel" in regular black, then a black block cursor in the empty cell right after "Rel", then a gray "⏎" and "save" in dark gray. The gray placeholder text is gone.

For a field that holds several lines, such as a note or a commit message, set `rows` to 2 or more:

```javascript theme={null}
Input({
  key: 'note',
  label: 'Note',
  placeholder: 'Write a note',
  rows: 4,
  onSubmit: noop,
})
```

The terminal and the Desktop app draw the rows. In the VS Code extension, the field holds one line. `rows` requires Claude Code v2.1.301 or later. On earlier versions the field holds one line.

The field takes up the number of rows set, even when it's empty, up to the height of the pane or band it's drawn in. While the field has focus, longer text scrolls inside it.

* In the terminal, Enter still submits. There, the user starts a new line by typing a backslash and then pressing Enter, or by pressing Shift+Enter where [the terminal emulator supports it](https://code.claude.com/docs/en/terminal-config.md#enter-multiline-prompts). Those are the same keys as in the prompt.
* In the terminal, Up and Down move between the field's rows. From its first and last row they move to the control before or after.
* `onSubmit` and `onInput` receive the whole text with its lines joined by `\n`.

### `Select`

A `Select` lets the user pick one of several options, and runs `onSelect` with the option's `value`:

```javascript theme={null}
Select({
  key: 'format',
  label: 'Format',
  value: picked,
  options: [
    { value: 'md', label: 'Markdown' },
    { value: 'html', label: 'HTML' },
    { value: 'txt', label: 'Plain text' },
  ],
  onSelect: (value) => {
    picked = value
  },
})
```

Closed, it shows its label and the current option:

![A pane with one line: the label Format, the current option Markdown, and a small down arrow.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-select-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=4e3b18268ffd87d2cad06442e6d661a9)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. A single row: "Format:" in regular weight, one space, "Markdown" in black, then after a space a small gray down-pointing triangle "▾". No option list is shown.

Open, it lists its options and marks one:

![The picker open, with its three options listed under the label. The second option, HTML, is drawn in inverse video.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-select-moved-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=deb6ce0a49d213235feedaa79ac658c0)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. Four rows. Header row: "Format:" in bold, "Markdown" in regular black, then a small gray up-pointing triangle "▴". Below it, indented by two columns: "Markdown", "HTML", "Plain text". The "HTML" row is white text on a black block that starts at the left text edge (covering the indent) and ends right after the "L"; the other two options are plain black. The header still reads "Markdown".

After the user picks an option, the list closes:

![The picker closed again, now showing HTML as the current option.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-select-picked-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=f065ab5bc479868f03088dc736f17097)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. A single row: "Format:" in bold, then "HTML" as white letters on a black block exactly as wide as the word, then a small gray down-pointing triangle "▾". The option list is gone.

## Draw pictures

### `Raster`

A `Raster` is a grid of colored character cells, for a heat map, a sparkline, or a game board. The terminal draws it. This sample uses the `cellsOf` function in the starter module, which packs the cells into the string a `Raster` takes. [Draw a grid of colored cells](https://code.claude.com/docs/en/plugins/mods/interface.md#draw-a-grid-of-colored-cells) explains it:

```javascript theme={null}
Raster({
  key: 'grid',
  columns: 3,
  rows: 2,
  cells: cellsOf([
    [['█', 0x2e7d32], ['█', 0xf9a825], ['█', 0xc62828]],
    [['█', 0x2e7d32], ['█', 0x2e7d32], ['█', 0xf9a825]],
  ]),
})
```

![A pane with a small grid of colored blocks, two rows of three: green, amber, and red, then green, green, and amber.](https://mintcdn.com/claude-code/EXkwf0kKMewZsyod/images/mods-el-raster-light.png?fit=max\&auto=format\&n=EXkwf0kKMewZsyod\&q=85\&s=5ed719481d3dd45b568bab696e57bf16)

> **Description of the screenshot:** Inside a light outer frame with a pale gray rounded border, a white pane with a thin dark rounded border and a small gray "×" at its top right. At the top left of the pane, a tiny block three cells wide and two cells tall, each cell a tall narrow rectangle the size of a character cell, with no gaps or borders between cells. Top row: dark green, amber, red. Bottom row: dark green, dark green, amber, so the two bottom-left greens and the top-left green merge into one green shape. The rest of the pane is empty white.

A `Raster` rounds each color to a smaller palette, so `0x2e7d32` draws as `#337733`.

### `Svg`

An `Svg` draws an SVG document in the Desktop app and the VS Code extension:

```javascript theme={null}
Svg({
  alt: 'Three bars of rising height',
  width: 120,
  height: 60,
  source:
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect x="10" y="40" width="20" height="20" fill="#2e7d32"/><rect x="50" y="25" width="20" height="35" fill="#f9a825"/><rect x="90" y="5" width="20" height="55" fill="#c62828"/></svg>',
})
```

In the terminal, a pane that returns only an `Svg` opens empty. To draw something else there, check [`e.surface`](https://code.claude.com/docs/en/plugins/mods/interface#pick-where-to-draw) and return a different tree.

### `Image` and `Client`

Two more elements have no sample here. `Image` draws a PNG or raw pixels in the terminal. `Client` is a region that a second file of the mod draws, for animation and pointer input. The [elements reference](https://code.claude.com/docs/en/plugins/mods/reference.md#elements) lists their props.

An `Image` draws as a picture in these terminals:

* kitty 0.28 or later
* Ghostty
* iTerm2 3.5 or later. Drawing in iTerm2 requires Claude Code v2.1.305 or later.

In any other terminal, the user sees the `Image`'s `alt` text, dimmed, in place of the picture. Write `alt` text that stands on its own, because it also shows in these cases, among others:

* **GNU screen**: a session running inside screen, in any terminal.
* **tmux**: a session running inside tmux that misses a [requirement for drawing inside tmux](#draw-an-image-inside-tmux).
* **Background sessions**: every [background session](https://code.claude.com/docs/en/agent-view.md), whatever terminal it's attached from.
* **iTerm2 outside fullscreen rendering**: in iTerm2 the picture draws only under [fullscreen rendering](https://code.claude.com/docs/en/fullscreen.md), and not while [`CLAUDE_CODE_ALT_SCREEN_FULL_REPAINT`](https://code.claude.com/docs/en/env-vars) is set to `1`. To see the picture, run `/tui fullscreen` at the Claude Code prompt and leave that variable unset.
* **A file path source in iTerm2 or tmux**: in iTerm2 and inside tmux, an `Image` whose `source` names a `file` shows the `alt` text instead of the picture. If the mod has iTerm2 or tmux users, pass the picture as base64 in `source.png` or `source.rgba` rather than as a path in `source.file`.

If the mod's users see the dimmed text in a terminal that draws kitty graphics protocol images with Unicode placeholders, they can set [`CLAUDE_CODE_FORCE_TERMINAL_IMAGES`](https://code.claude.com/docs/en/env-vars) to `1`. They shouldn't set it inside GNU screen, inside tmux older than 3.3, in a tmux popup, or with tmux's `allow-passthrough` off. There they see no picture and a box in place of the `alt` text.

#### Draw an `Image` inside tmux

If an `Image` shows its `alt` text inside tmux, check these requirements along with the [other `alt` text cases](#image-and-client) such as a background session:

* Claude Code v2.1.310 or later
* tmux 3.3 or later
* Claude Code runs in a tmux pane, not a tmux popup
* tmux runs inside kitty 0.28 or later, Ghostty, or iTerm2 3.5 or later
* The tmux options `focus-events` and `allow-passthrough` are `on`. Inside kitty or Ghostty, `allow-passthrough` can also be `all`.
* Inside iTerm2, tmux runs [without `-CC`](https://code.claude.com/docs/en/fullscreen#use-with-tmux), [fullscreen rendering](https://code.claude.com/docs/en/fullscreen.md) is on, and `CLAUDE_CODE_ALT_SCREEN_FULL_REPAINT` is unset.
* Inside iTerm2, the tmux window is no bigger than the iTerm2 window. To check, run `tmux display-message -p '#{window_bigger}'` in that tmux window. If it prints `1`, make the tmux window fit, then restart Claude Code.
* The mod's author passes the picture as `png` or `rgba` bytes, not as a `file` path. A user of a mod they didn't write, for whom the other requirements hold, should ask its author to check this one.

For each tmux option that isn't already set as required, run its command in the shell:

```bash theme={null}
tmux set -g allow-passthrough on
tmux set -g focus-events on
```

Then detach from tmux, attach again, and restart Claude Code. Restart it again whenever tmux is attached from a different terminal. To keep both options across tmux server restarts, [add both lines to `~/.tmux.conf`](https://code.claude.com/docs/en/terminal-config#configure-tmux) too.

## See where a mod can draw

The samples all draw in a pane. A mod can also draw in other places, and call Claude Code to show something for it:

* **Pane and band**: [Pick where to draw](https://code.claude.com/docs/en/plugins/mods/interface.md#pick-where-to-draw)
* **Claude Code's own rows, such as the spinner**: [Change what Claude Code already draws](https://code.claude.com/docs/en/plugins/mods/interface.md#change-what-claude-code-already-draws)
* **Toast, status line, and log line**: [Show something without starting a turn](https://code.claude.com/docs/en/plugins/mods/api.md#show-something-without-starting-a-turn)
* **Question dialog**: [Hold a tool call until the user decides](https://code.claude.com/docs/en/plugins/mods/events.md#hold-a-tool-call-until-the-user-decides)

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/mods/gallery — the full official page, including sections this copy omits.
- https://code.claude.com/docs/en/plugins/mods/interface.md — drawing in the interface: building a pane with tabs step by step, where to draw, keyboard focus and hotkeys, and grids of colored cells.
- https://code.claude.com/docs/en/plugins/mods/reference.md — the elements reference: each element's main props and the apps that draw it.
- https://code.claude.com/docs/en/plugins/mods/create.md — creating a mod and getting the type declarations for a build.
- https://code.claude.com/docs/en/terminal-config.md — terminal configuration: multiline prompts and configuring tmux.
- https://code.claude.com/docs/en/agent-view.md — background sessions.
- https://code.claude.com/docs/en/fullscreen.md — fullscreen rendering and use with tmux.
- https://code.claude.com/docs/en/env-vars — environment variables such as `CLAUDE_CODE_ALT_SCREEN_FULL_REPAINT` and `CLAUDE_CODE_FORCE_TERMINAL_IMAGES`.
- https://code.claude.com/docs/en/plugins/mods/api.md — the mods API, including showing something without starting a turn.
- https://code.claude.com/docs/en/plugins/mods/events.md — mod events, including holding a tool call until the user decides.
- https://code.claude.com/docs/en/plugins/mods/test.md — testing a drawing, such as pressing buttons from a test.
