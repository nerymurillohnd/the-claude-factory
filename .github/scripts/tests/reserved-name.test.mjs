#!/usr/bin/env node
// Tests for RESERVED_NAME against the plugin-name table of the manifest reference
// (https://code.claude.com/docs/en/plugins/manifest-reference#name).
//   node --test ".github/scripts/tests/*.test.mjs"

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { RESERVED_NAME } from '../lib.mjs'

const REJECTED = [
  'claude',
  'anthropic',
  'anthropics',
  'claude-code',
  'claude-mods',
  'claude-tools',
  'anthropic-tools',
  'anthropics-tools',
  'cc-plugin-tools',
  'Claude-Tools',
  'CLAUDE',
  'claude--tools',
  'claude_tools',
  'claude.tools',
  'Anthropic.Tools',
  'cc--plugin-tools',
  'official-claude-tools',
  'official-anthropic',
  'claude-official',
  'tools-anthropics-official',
  'Official_Claude',
  'claude-less',
]

const ACCEPTED = [
  'claudette',
  'anthropical',
  'officialtools',
  'official-tools',
  'my-tools',
  'cc-plugins',
  // Not listed in the official table, and claude plugin validate 2.1.302 accepts it.
  'cc-plugin',
  'skill-diagnostics',
  'typescript6-lsp-intelligence',
  // A whole word elsewhere is only a warning in the official check, not an error.
  'mcp-for-claude',
]

for (const name of REJECTED) {
  test(`rejects ${name}`, () => {
    assert.ok(RESERVED_NAME.test(name))
  })
}

for (const name of ACCEPTED) {
  test(`accepts ${name}`, () => {
    assert.ok(!RESERVED_NAME.test(name))
  })
}
