#!/usr/bin/env node
// @ts-check
// Checks skill-diagnostics' workflows/evals.js, which neither Biome nor tsc can read: Claude Code
// runs a workflow script as the body of an async function, after an `export const meta = {...}`
// literal, with a top-level return and the injected globals agent, parallel, pipeline, phase,
// log and args (https://code.claude.com/docs/en/workflows#what-the-saved-script-looks-like;
// the Workflow tool's `script` field: https://code.claude.com/docs/en/agent-sdk/typescript#workflow).
// The tests prove the body compiles, that meta is a pure literal with the phases the script
// names, and that the script returns its result shape when run against stubs.
//   node --test "scripts/testers/skill-diagnostics/*.test.mjs"

import assert from 'node:assert/strict'
import { join } from 'node:path'
import { test } from 'node:test'
import { pluginDir, readText } from '../../lib.mjs'

const SCRIPT = join(pluginDir('skill-diagnostics'), 'workflows', 'evals.js')
const GLOBALS = ['agent', 'parallel', 'pipeline', 'phase', 'log', 'args']
const META_START = /^export const meta = /m

/** @type {new (...args: string[]) => (...values: unknown[]) => Promise<unknown>} */
const AsyncFunction = Object.getPrototypeOf(async () => undefined).constructor

const source = readText(SCRIPT)

/** The script as Claude Code runs it: the same text with `export ` dropped from the meta line. */
function body() {
  assert.match(source, META_START, 'the script declares `export const meta = ` at line start')
  return source.replace(META_START, 'const meta = ')
}

/**
 * The index just past the string literal that opens at `start`, escapes included.
 * @param {string} text
 * @param {number} start
 * @returns {number}
 */
function skipString(text, start) {
  const quote = text[start]
  let i = start + 1
  while (i < text.length && text[i] !== quote) {
    i += text[i] === '\\' ? 2 : 1
  }
  return i + 1
}

/**
 * The text of the meta literal: from its `{` to the matching `}`, skipping strings.
 * @returns {string}
 */
function metaText() {
  const match = META_START.exec(source)
  assert.ok(match, 'no `export const meta = ` line')
  const start = match.index + match[0].length
  assert.equal(source[start], '{', 'meta is not an object literal')
  let depth = 0
  let i = start
  while (i < source.length) {
    const c = source[i] ?? ''
    if ('\'"`'.includes(c)) {
      i = skipString(source, i)
      continue
    }
    depth += Number('{['.includes(c)) - Number('}]'.includes(c))
    if (depth === 0) {
      return source.slice(start, i + 1)
    }
    i++
  }
  assert.fail('meta literal is not closed')
}

const ESCAPES = /** @type {Record<string, string>} */ ({ n: '\n', t: '\t', r: '\r' })
const KEY = /^[A-Za-z_$][\w$]*/
const SCALAR = /^(?:-?\d+(?:\.\d+)?|true|false|null)(?![\w$])/
const SPACE = /\s/

/**
 * Parses a JavaScript literal made only of objects, arrays, strings (template strings without
 * `${`), numbers, true, false and null, with identifier or string keys and trailing commas.
 * Anything else (a call, a variable, a spread, an interpolation, a computed key, a shorthand or a
 * method) throws a SyntaxError, which is what "meta is a pure literal" means: unlike an eval in a
 * sandbox, nothing in the text runs, and no global can stand in for a value.
 */
class LiteralParser {
  /** @param {string} text */
  constructor(text) {
    this.text = text
    this.i = 0
  }

  /** @returns {unknown} */
  parse() {
    const result = this.value()
    this.ws()
    if (this.i !== this.text.length) {
      this.bad('text after the literal')
    }
    return result
  }

  ws() {
    while (this.i < this.text.length && SPACE.test(this.text[this.i] ?? '')) {
      this.i++
    }
  }

  /**
   * @param {string} why
   * @returns {never}
   */
  bad(why) {
    const near = JSON.stringify(this.text.slice(this.i, this.i + 30))
    throw new SyntaxError(`${why} at offset ${this.i}: ${near}`)
  }

  /** @returns {string} */
  string() {
    const q = this.text[this.i]
    this.i++
    let out = ''
    while (this.i < this.text.length && this.text[this.i] !== q) {
      const c = this.text[this.i] ?? ''
      if (q === '`' && c === '$' && this.text[this.i + 1] === '{') {
        this.bad('template interpolation')
      }
      if (c === '\\') {
        const n = this.text[this.i + 1] ?? ''
        out += ESCAPES[n] ?? n
        this.i += 2
      } else {
        out += c
        this.i++
      }
    }
    if (this.text[this.i] !== q) {
      this.bad('unterminated string')
    }
    this.i++
    return out
  }

  /** @returns {string} */
  key() {
    const c = this.text[this.i]
    if (c === "'" || c === '"') {
      return this.string()
    }
    const word = KEY.exec(this.text.slice(this.i))?.[0]
    if (!word) {
      this.bad('expected a key')
    }
    this.i += word.length
    return word
  }

  /**
   * After an entry: steps over a `,`, or requires the closing bracket, which `closes` reads.
   * @param {string} close
   */
  next(close) {
    this.ws()
    if (this.text[this.i] === ',') {
      this.i++
    } else if (this.text[this.i] !== close) {
      this.bad(`expected \`,\` or \`${close}\``)
    }
  }

  /**
   * True, past the bracket, when the list closes here.
   * @param {string} close
   */
  closes(close) {
    this.ws()
    if (this.text[this.i] === close) {
      this.i++
      return true
    }
    return false
  }

  /** @returns {Record<string, unknown>} */
  object() {
    this.i++
    /** @type {Record<string, unknown>} */
    const obj = {}
    while (!this.closes('}')) {
      const key = this.key()
      this.ws()
      if (this.text[this.i] !== ':') {
        this.bad('expected `:` (shorthand and methods are not literals)')
      }
      this.i++
      obj[key] = this.value()
      this.next('}')
    }
    return obj
  }

  /** @returns {unknown[]} */
  array() {
    this.i++
    /** @type {unknown[]} */
    const arr = []
    while (!this.closes(']')) {
      arr.push(this.value())
      this.next(']')
    }
    return arr
  }

  /** @returns {unknown} */
  value() {
    this.ws()
    const c = this.text[this.i] ?? ''
    if (c === '{') {
      return this.object()
    }
    if (c === '[') {
      return this.array()
    }
    if ('\'"`'.includes(c)) {
      return this.string()
    }
    const word = SCALAR.exec(this.text.slice(this.i))?.[0]
    if (!word) {
      this.bad('not a literal value')
    }
    this.i += word.length
    return JSON.parse(word)
  }
}

/**
 * @param {string} text
 * @returns {unknown}
 */
function parseLiteral(text) {
  return new LiteralParser(text).parse()
}

/** @returns {{ name: string, description: string, phases: { title: string }[] }} */
function meta() {
  const parsed = /** @type {any} */ (parseLiteral(metaText()))
  return parsed
}

/**
 * Data shaped by a JSON schema: the i-th array item takes the i-th enum value (mod its length)
 * and a boolean alternating true and false, so a plan has both splits and both trigger kinds.
 * @param {any} schema
 * @param {number} [index]
 * @returns {unknown}
 */
function fake(schema, index = 0) {
  if (schema.enum) {
    return schema.enum[index % schema.enum.length]
  }
  switch (schema.type) {
    case 'object': {
      /** @type {Record<string, unknown>} */
      const out = {}
      for (const [key, sub] of Object.entries(schema.properties ?? {})) {
        out[key] = fake(sub, index)
      }
      return out
    }
    case 'array':
      return [0, 1, 2, 3].map((n) => fake(schema.items, n))
    case 'string':
      return `s${index}`
    case 'integer':
      return index === 0 ? 3 : 1
    case 'number':
      return 100 + index
    case 'boolean':
      return index % 2 === 0
    default:
      return null
  }
}

/** Stubs of the injected globals, recording phases, logs and agent calls. */
function stubs() {
  /** @type {string[]} */
  const phases = []
  /** @type {string[]} */
  const logs = []
  /** @type {{ prompt: string, opts: any }[]} */
  const calls = []
  /**
   * @param {string} prompt
   * @param {any} [opts]
   */
  const agent = (prompt, opts = {}) => {
    calls.push({ prompt, opts })
    return Promise.resolve(opts.schema ? fake(opts.schema) : `report for ${opts.label ?? ''}`)
  }
  /** @param {(() => Promise<unknown>)[]} thunks */
  const parallel = (thunks) => Promise.all(thunks.map((f) => f()))
  /**
   * @param {unknown[]} items
   * @param {((value: any, item?: any, index?: number) => unknown)[]} stages
   */
  const pipeline = (items, ...stages) =>
    Promise.all(
      items.map(async (item, n) => {
        const [first, ...rest] = stages
        let v = await first?.(item, n)
        for (const stage of rest) {
          v = await stage(v, item, n)
        }
        return v
      }),
    )
  /** @param {string} title */
  const phase = (title) => {
    phases.push(title)
  }
  /** @param {string} line */
  const log = (line) => {
    logs.push(line)
  }
  return { agent, parallel, pipeline, phase, log, phases, logs, calls }
}

/** @param {unknown} args */
function run(args) {
  const s = stubs()
  const fn = new AsyncFunction(...GLOBALS, body())
  return { s, result: fn(s.agent, s.parallel, s.pipeline, s.phase, s.log, args) }
}

test('the body compiles as an async function with the injected globals', () => {
  assert.doesNotThrow(() => new AsyncFunction(...GLOBALS, body()))
})

test('meta is a pure literal named evals, with a description and phases', () => {
  const m = meta()
  assert.equal(m.name, 'evals')
  assert.equal(typeof m.description, 'string')
  assert.ok(m.description.trim().length > 0, 'empty description')
  assert.ok(Array.isArray(m.phases) && m.phases.length > 0, 'no phases')
  for (const p of m.phases) {
    assert.equal(typeof p.title, 'string')
    assert.ok(p.title.length > 0, 'a phase without a title')
  }
})

test('the literal parser rejects what is not a literal', () => {
  for (const text of [
    '{ a: b }',
    '{ a: f() }',
    '{ ...x }',
    '{ a }',
    '{ [k]: 1 }',
    ['{ a: `x$', '{y}` }'].join(''),
    '{ a() {} }',
  ]) {
    assert.throws(() => parseLiteral(text), SyntaxError, text)
  }
  assert.deepEqual(parseLiteral("{ a: 'x', 'b': [1, true, null,], }"), {
    a: 'x',
    b: [1, true, null],
  })
})

test('every phase the script names is a title in meta.phases', () => {
  const titles = new Set(meta().phases.map((p) => p.title))
  const named = [
    ...[...source.matchAll(/\bphase\(\s*'([^']*)'\s*\)/g)].map((m) => m[1] ?? ''),
    ...[...source.matchAll(/\bphase:\s*'([^']*)'/g)].map((m) => m[1] ?? ''),
  ]
  assert.ok(named.length > 0, 'the script names no phase')
  for (const title of named) {
    assert.ok(titles.has(title), `phase '${title}' is not in meta.phases`)
  }
})

test('with stubs, the script returns its result shape', async () => {
  const { s, result } = run({ skill: '/tmp/demo-skill/' })
  const out = /** @type {Record<string, any>} */ (await result)
  assert.deepEqual(Object.keys(out).sort(), [
    'iteration',
    'quality',
    'report',
    'skill',
    'trigger',
    'workspace',
  ])
  assert.equal(out['skill'], '/tmp/demo-skill')
  assert.equal(out['iteration'], 1)
  assert.equal(out['workspace'], '/tmp/demo-skill-workspace/iteration-1')
  assert.ok(Array.isArray(out['trigger'].rows) && out['trigger'].rows.length > 0)
  assert.equal(typeof out['trigger'].train_pass_rate, 'number')
  assert.equal(typeof out['trigger'].validation_pass_rate, 'number')
  assert.ok(Array.isArray(out['quality']) && out['quality'].length > 0)
  assert.equal(out['quality'][0].graded, true)
  assert.equal(typeof out['report'], 'string')
  const titles = new Set(meta().phases.map((p) => p.title))
  for (const p of s.phases) {
    assert.ok(titles.has(p), `phase('${p}') ran but is not in meta.phases`)
  }
  for (const call of s.calls) {
    assert.ok(
      call.opts.phase === undefined || titles.has(call.opts.phase),
      `agent phase '${call.opts.phase}' is not in meta.phases`,
    )
  }
})

test('without args.skill, the script throws before any agent runs', async () => {
  for (const args of [undefined, {}, { runs: 3 }]) {
    const { s, result } = run(args)
    await assert.rejects(result, /Pass the skill folder/)
    assert.equal(s.calls.length, 0)
  }
})
