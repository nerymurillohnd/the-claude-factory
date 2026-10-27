// The pane's body on the terminal and the desktop: the rows or the file in view, its scrollbar,
// the shimmer of what Claude touches, and the person's keys, clicks and hovers, which it posts
// to the hooks module. It measures its own height and reports it, so the hooks module sends
// exactly the rows that fit, whatever the header above it takes.

import type { ClientModule, ClientPointerEvent, ClientSurface, RenderElement } from 'claude-code'

import type { BodyLine, BodyMessage, BodyProps, Segment } from './body.ts'
import { DOUBLE_CLICK_MS, SHIMMER_MS, thumbOf } from './body.ts'

type Local = {
  rows: number
  columns: number
  hovered: number | null
  /** The screen row and time of the last click, which a second click there makes a double. */
  lastClick: { y: number; at: number } | null
  isDragging: boolean
  phase: number
  /** What the tick reads: the latest props' shimmer, set on every draw. */
  live: { hasShimmer: boolean; total: number; first: number; isPointerOff: boolean }
}

const firstState = (rows: number, columns: number): Local => ({
  rows,
  columns,
  hovered: null,
  lastClick: null,
  isDragging: false,
  phase: 0,
  live: { hasShimmer: false, total: 0, first: 0, isPointerOff: false },
})

const Body: ClientModule<BodyProps, Local> = (
  props: BodyProps,
  surface: ClientSurface<Local>,
): RenderElement => {
  const { Box, Text, Code } = surface.elements
  const state = surface.state ?? firstState(surface.rows, surface.columns)
  state.live.hasShimmer = props.lines.some((line) => line.shimmer !== null)
  state.live.total = props.total
  state.live.first = props.first
  state.live.isPointerOff = props.isPointerOff

  if (surface.state === undefined) {
    surface.every(SHIMMER_MS, () => {
      const now = surface.state
      if (now?.live.hasShimmer === true) {
        surface.setState({ ...now, phase: now.phase + 1 })
      }
    })
    surface.onKey((event) => {
      const message: BodyMessage = {
        type: 'key',
        key: event.key,
        ctrl: event.ctrl === true,
        shift: event.shift === true,
      }
      surface.post(message)
    })
    surface.onPointer((event) => onPointer(event))
    surface.setState(state)
    surface.post({
      type: 'size',
      rows: surface.rows,
      columns: surface.columns,
    } satisfies BodyMessage)
  } else if (surface.rows !== state.rows || surface.columns !== state.columns) {
    surface.setState({ ...state, rows: surface.rows, columns: surface.columns })
    surface.post({
      type: 'size',
      rows: surface.rows,
      columns: surface.columns,
    } satisfies BodyMessage)
  }

  function onPointer(event: ClientPointerEvent): void {
    const now = surface.state
    if (now === undefined || now.live.isPointerOff) {
      return
    }
    const room = Math.max(1, surface.rows)
    const hasBar = now.live.total > room
    const onBar = hasBar && event.x >= surface.columns - 1
    if (!dragBar(now, event, onBar, room)) {
      pointAt(now, event, onBar, room)
    }
  }

  // A hover, the pointer leaving, or a click on the rows.
  function pointAt(now: Local, event: ClientPointerEvent, onBar: boolean, height: number): void {
    if (event.type === 'move' && event.button === undefined) {
      hover(now, onBar ? null : rowAt(now, event.y, height))
      return
    }
    if (event.type === 'leave') {
      hover(now, null)
      return
    }
    if (event.type === 'up' && event.button === 'left' && !onBar) {
      clickRow(now, event.y, height)
    }
  }

  // A press on the scrollbar, and the drag it starts; false for any other event.
  function dragBar(now: Local, event: ClientPointerEvent, onBar: boolean, height: number): boolean {
    if (event.type === 'down' && event.button === 'left' && onBar) {
      surface.setState({ ...now, isDragging: true })
      surface.post({ type: 'scrollTo', ratio: ratioOf(event.y, height) } satisfies BodyMessage)
      return true
    }
    if (event.type === 'move' && now.isDragging) {
      surface.post({ type: 'scrollTo', ratio: ratioOf(event.y, height) } satisfies BodyMessage)
      return true
    }
    if (event.type === 'up' && now.isDragging) {
      surface.setState({ ...now, isDragging: false })
      return true
    }
    return false
  }

  // The row at screen row `y`, or null past the body's top or bottom.
  function rowAt(now: Local, y: number, height: number): number | null {
    return y >= 0 && y < height ? now.live.first + y : null
  }

  function hover(now: Local, hovered: number | null): void {
    if (hovered !== now.hovered) {
      surface.setState({ ...now, hovered })
    }
  }

  // A left click on screen row `y`.
  function clickRow(now: Local, y: number, height: number): void {
    if (y < 0 || y >= height) {
      return
    }
    // A double click is two clicks on the same screen row: the first one may already have
    // turned the body into the file's preview, whose rows are not the tree's. The hooks module
    // opens the row the first click picked.
    const at = Date.now()
    const index = now.live.first + y
    const isDouble =
      now.lastClick !== null && now.lastClick.y === y && at - now.lastClick.at <= DOUBLE_CLICK_MS
    if (isDouble) {
      surface.setState({ ...now, lastClick: null })
      surface.post({ type: 'open', index } satisfies BodyMessage)
      return
    }
    if (index >= now.live.total) {
      return
    }
    surface.setState({ ...now, lastClick: { y, at } })
    surface.post({ type: 'click', index } satisfies BodyMessage)
  }

  const room = Math.max(1, surface.rows)
  const thumb = thumbOf(props.first, props.total, room)
  const bar = (row: number): RenderElement => {
    const isThumb = thumb !== null && row >= thumb.start && row < thumb.end
    const glyph = isThumb ? '┃' : '│'
    return (
      <Text color={isThumb ? props.barColor : props.trackColor} key={`bar-${row}`}>
        {thumb === null ? ' ' : glyph}
      </Text>
    )
  }

  const rowBg = (index: number, line: BodyLine): string | undefined => {
    if (index === props.selected) {
      return props.selectedBg
    }
    if (index === state.hovered) {
      return props.hoveredBg
    }
    return line.bg ?? undefined
  }

  if (props.code !== null) {
    return (
      <Box flexDirection="row" height={room}>
        <Box flexDirection="column" flexGrow={1} overflow="hidden">
          <Code
            path={props.code.path}
            source={props.code.source}
            startLine={props.code.startLine}
            wrap="truncate-end"
          />
        </Box>
        {thumb !== null && (
          <Box flexDirection="column" width={1}>
            {Array.from({ length: room }, (_, row) => bar(row))}
          </Box>
        )}
      </Box>
    )
  }

  const segmentOf = (segment: Segment, index: number, line: BodyLine): RenderElement[] => {
    if (index !== line.nameIndex || line.shimmer === null) {
      return [
        <Text
          key={`s${index}`}
          {...(segment.color === null ? {} : { color: segment.color })}
          dimColor={segment.isDim === true}
          strikethrough={segment.isStruck === true}
          weight={segment.isBold === true ? 'bold' : 'regular'}
        >
          {segment.text}
        </Text>,
      ]
    }
    // The shimmer: the name in the activity's color, a short bright band sweeping across it.
    const shimmer = line.shimmer
    const width = segment.text.length + 6
    const at = (state.phase % width) - 3
    return Array.from(segment.text, (char, i) => (
      <Text
        color={shimmer}
        inverse={Math.abs(i - at) === 0}
        key={`s${index}-${i}`}
        weight={Math.abs(i - at) <= 1 ? 'bold' : 'regular'}
      >
        {char}
      </Text>
    ))
  }

  return (
    <Box flexDirection="column" height={room}>
      {props.lines.slice(0, room).map((line, row) => {
        const index = props.first + row
        const bg = rowBg(index, line)
        return (
          <Box
            flexDirection="row"
            key={line.key}
            {...(bg === undefined ? {} : { backgroundColor: bg })}
          >
            <Box flexDirection="row" flexGrow={1} overflow="hidden">
              {line.segments.flatMap((segment, i) => segmentOf(segment, i, line))}
            </Box>
            {thumb !== null && bar(row)}
          </Box>
        )
      })}
    </Box>
  )
}

const ratioOf = (y: number, room: number): number =>
  Math.min(1, Math.max(0, y / Math.max(1, room - 1)))

export default Body
