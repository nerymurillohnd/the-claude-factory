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
    if (event.type === 'down' && event.button === 'left' && onBar) {
      surface.setState({ ...now, isDragging: true })
      surface.post({ type: 'scrollTo', ratio: ratioOf(event.y, room) } satisfies BodyMessage)
      return
    }
    if (event.type === 'move' && now.isDragging) {
      surface.post({ type: 'scrollTo', ratio: ratioOf(event.y, room) } satisfies BodyMessage)
      return
    }
    if (event.type === 'up' && now.isDragging) {
      surface.setState({ ...now, isDragging: false })
      return
    }
    if (event.type === 'move' && event.button === undefined) {
      const hovered = event.y >= 0 && event.y < room && !onBar ? now.live.first + event.y : null
      if (hovered !== now.hovered) {
        surface.setState({ ...now, hovered })
      }
      return
    }
    if (event.type === 'leave') {
      if (now.hovered !== null) {
        surface.setState({ ...now, hovered: null })
      }
      return
    }
    if (event.type === 'up' && event.button === 'left' && !onBar) {
      if (event.y < 0 || event.y >= room) {
        return
      }
      // A double click is two clicks on the same screen row: the first one may already have
      // turned the body into the file's preview, whose rows are not the tree's. The hooks module
      // opens the row the first click picked.
      const at = Date.now()
      const index = now.live.first + event.y
      const isDouble =
        now.lastClick !== null &&
        now.lastClick.y === event.y &&
        at - now.lastClick.at <= DOUBLE_CLICK_MS
      if (isDouble) {
        surface.setState({ ...now, lastClick: null })
        surface.post({ type: 'open', index } satisfies BodyMessage)
        return
      }
      if (index >= now.live.total) {
        return
      }
      surface.setState({ ...now, lastClick: { y: event.y, at } })
      surface.post({ type: 'click', index } satisfies BodyMessage)
    }
  }

  const room = Math.max(1, surface.rows)
  const thumb = thumbOf(props.first, props.total, room)
  const bar = (row: number): RenderElement => {
    const isThumb = thumb !== null && row >= thumb.start && row < thumb.end
    const glyph = isThumb ? '┃' : '│'
    return (
      <Text key={`bar-${row}`} color={isThumb ? props.barColor : props.trackColor}>
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
        <Box flexGrow={1} flexDirection="column" overflow="hidden">
          <Code
            source={props.code.source}
            path={props.code.path}
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
          weight={segment.isBold === true ? 'bold' : 'regular'}
          strikethrough={segment.isStruck === true}
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
        key={`s${index}-${i}`}
        color={shimmer}
        weight={Math.abs(i - at) <= 1 ? 'bold' : 'regular'}
        inverse={Math.abs(i - at) === 0}
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
            key={line.key}
            flexDirection="row"
            {...(bg === undefined ? {} : { backgroundColor: bg })}
          >
            <Box flexGrow={1} flexDirection="row" overflow="hidden">
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
