#!/usr/bin/env node
// A stand-in for the Tailwind CSS language server: it speaks just enough of the protocol for the
// MCP server's client. STUB_MODE=no-project answers every getProject with null.

const NO_PROJECT = process.env['STUB_MODE'] === 'no-project'

/** @param {object} message */
function send(message) {
  const body = JSON.stringify({ jsonrpc: '2.0', ...message })
  process.stdout.write(`Content-Length: ${Buffer.byteLength(body)}\r\n\r\n${body}`)
}

/** @param {{ id?: number, method?: string, params?: any }} message */
function handle({ id, method, params }) {
  if (method === 'exit') {
    process.exit(0)
  }
  switch (method) {
    case 'initialize':
      send({ id, result: { capabilities: {} } })
      return
    case 'textDocument/didOpen':
    case 'textDocument/didChange': {
      const { uri, version } = params.textDocument
      send({
        method: 'textDocument/publishDiagnostics',
        params: {
          uri,
          version,
          diagnostics: [
            {
              range: { start: { line: 0, character: 12 }, end: { line: 0, character: 16 } },
              severity: 2,
              code: 'cssConflict',
              message: "'flex' applies the same CSS properties as 'block'.",
            },
          ],
        },
      })
      return
    }
    case '@/tailwindCSS/getProject':
      send({ id, result: NO_PROJECT ? null : { version: '4.3.3' } })
      return
    case 'textDocument/codeAction':
      send({
        id,
        result: [
          {
            title: "Delete 'block'",
            kind: 'quickfix',
            edit: {
              changes: {
                [params.textDocument.uri]: [
                  {
                    range: { start: { line: 0, character: 12 }, end: { line: 0, character: 22 } },
                    newText: 'flex',
                  },
                ],
              },
            },
          },
        ],
      })
      return
    case '@/tailwindCSS/sortSelection':
      send({
        id,
        result: {
          classLists: params.classLists.map((/** @type {string} */ l) =>
            l.split(' ').sort().join(' '),
          ),
        },
      })
      return
    case 'shutdown':
      send({ id, result: null })
      return
    default:
      if (id !== undefined) {
        send({ id, result: null })
      }
  }
}

let buffer = Buffer.alloc(0)
process.stdin.on('data', (/** @type {Buffer} */ chunk) => {
  buffer = Buffer.concat([buffer, chunk])
  for (;;) {
    const headerEnd = buffer.indexOf('\r\n\r\n')
    if (headerEnd < 0) {
      return
    }
    const length = Number(
      /Content-Length: (\d+)/u.exec(buffer.subarray(0, headerEnd).toString())?.[1],
    )
    if (buffer.length < headerEnd + 4 + length) {
      return
    }
    const body = buffer.subarray(headerEnd + 4, headerEnd + 4 + length).toString()
    buffer = buffer.subarray(headerEnd + 4 + length)
    handle(JSON.parse(body))
  }
})
