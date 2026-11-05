#!/usr/bin/env node
// @ts-check
// Contract tests for the github-operations agents' frontmatter: the tools Claude Code
// removes from each agent, and the scoped names the plugin's skills, commands and README use.
// A plugin agent at agents/<dir>/<file>.md registers as github-operations:<dir>:<file>
// (https://code.claude.com/docs/en/sub-agents#choose-the-subagent-scope), and subagents can
// spawn nested subagents unless Agent is removed
// (https://code.claude.com/docs/en/sub-agents#let-subagents-spawn-their-own-subagents).
//   node --test "scripts/testers/github-operations/*.test.mjs"

import assert from 'node:assert/strict'
import { readdirSync } from 'node:fs'
import { join, relative, sep } from 'node:path'
import { test } from 'node:test'
import { pluginDir, readText } from '../../lib.mjs'

const PLUGIN = 'github-operations'
const DIR = pluginDir(PLUGIN)
const AGENTS = join(DIR, 'agents')

/** Tools each agent must not have, from its README limits; every agent must also deny Agent. */
const MUST_DENY = {
  'pr-lifecycle:pr-tracker': ['Agent', 'Write', 'Edit', 'NotebookEdit'],
  'pr-lifecycle:pr-fixer': ['Agent'],
  'pr-lifecycle:pr-finalizer': ['Agent', 'Write', 'Edit', 'NotebookEdit'],
  'repo-hygiene:health-diagnostics': ['Agent', 'Edit', 'NotebookEdit'],
}

/**
 * Tools an agent needs for its job; denying them would break it.
 * @type {Record<string, string[]>}
 */
const MUST_KEEP = {
  'repo-hygiene:health-diagnostics': ['Write'],
}

/**
 * @param {string} dir
 * @returns {string[]}
 */
function markdownFiles(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((d) => {
    if (d.isDirectory()) {
      return markdownFiles(join(dir, d.name))
    }
    return d.name.endsWith('.md') ? [join(dir, d.name)] : []
  })
}

/**
 * Top-level `key: value` lines of a file's YAML frontmatter.
 * @param {string} text
 * @returns {Record<string, string>}
 */
function frontmatter(text) {
  const match = /^---\n([\s\S]*?)\n---\n/.exec(text)
  const body = match?.[1]
  assert.ok(body !== undefined, 'the file starts with a frontmatter block')
  /** @type {Record<string, string>} */
  const fields = {}
  for (const line of body.split('\n')) {
    const [, key, value] = /^([A-Za-z]+):\s*(.*)$/.exec(line) ?? []
    if (key !== undefined && value !== undefined) {
      fields[key] = value.trim()
    }
  }
  return fields
}

/**
 * @param {string | undefined} value
 * @returns {string[]}
 */
function toolList(value) {
  return (value ?? '')
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean)
}

const agents = new Map(
  markdownFiles(AGENTS).map((file) => [
    relative(AGENTS, file).replace(/\.md$/, '').split(sep).join(':'),
    frontmatter(readText(file)),
  ]),
)

test('every agent has a contract in this test', () => {
  assert.deepEqual([...agents.keys()].sort(), Object.keys(MUST_DENY).sort())
})

for (const [id, denied] of Object.entries(MUST_DENY)) {
  test(`${id} has no tool its limits forbid`, () => {
    const fields = agents.get(id)
    assert.ok(fields, `agents/${id.split(':').join('/')}.md exists`)
    assert.equal(fields['tools'], undefined, 'limits come from disallowedTools, not a tools list')
    const actual = toolList(fields['disallowedTools'])
    for (const tool of denied) {
      assert.ok(actual.includes(tool), `disallowedTools names ${tool}`)
    }
    for (const tool of MUST_KEEP[id] ?? []) {
      assert.ok(!actual.includes(tool), `disallowedTools keeps ${tool}, which the agent needs`)
    }
  })
}

test('every scoped agent name the plugin references exists', () => {
  const files = [
    join(DIR, 'README.md'),
    ...markdownFiles(join(DIR, 'skills')),
    ...markdownFiles(join(DIR, 'commands')),
    ...markdownFiles(AGENTS),
  ]
  const referenced = new Set(
    files.flatMap((file) =>
      [...readText(file).matchAll(/github-operations:([a-z-]+:[a-z-]+)\b/g)].flatMap((m) =>
        m[1] === undefined ? [] : [m[1]],
      ),
    ),
  )
  assert.ok(referenced.size > 0, 'the plugin references its agents by scoped name')
  for (const id of referenced) {
    assert.ok(agents.has(id), `github-operations:${id} is an agent file`)
  }
})
