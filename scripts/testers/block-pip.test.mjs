#!/usr/bin/env node
// @ts-check
// Tests for the PreToolUse hook .claude/hooks/block-pip.sh: every pip command is denied, and a
// word "pip" inside a quoted argument is not a command.
//   node --test "scripts/testers/*.test.mjs"

import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { dirname, join } from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'

const HOOK = join(
  dirname(fileURLToPath(import.meta.url)),
  '..',
  '..',
  '.claude',
  'hooks',
  'block-pip.sh',
)

/**
 * The hook's decision for one Bash command: "deny" or "pass".
 * @param {string} command
 * @returns {string}
 */
function decide(command) {
  const run = spawnSync('bash', [HOOK], {
    input: JSON.stringify({ tool_name: 'Bash', tool_input: { command } }),
    encoding: 'utf8',
  })
  assert.equal(run.status, 0, `hook exited ${run.status}: ${run.stderr}`)
  return run.stdout.includes('"permissionDecision":"deny"') ? 'deny' : 'pass'
}

const DENIED = [
  'pip install requests',
  'pip3 install ruff',
  'pip3.12 list',
  '/usr/bin/pip3 freeze',
  'python3 -m pip install x',
  'python -mpip install x',
  'python3.12 -m ensurepip',
  'ensurepip',
  'uv pip install x',
  'sudo pip install x',
  'env -i PATH=/bin pip install x',
  'FOO=1 BAR=2 pip install x',
  'cd src && pip install -e .',
  'false || pip install x',
  'ls; pip list',
  'echo x | xargs pip install',
  'echo ok\npip install x',
  'echo $(pip --version)',
  'echo "$(pip --version)"',
  'echo "version: $(python3 -m pip --version)"',
  '(pip install x)',
  "echo 'quoted' && pip install x",
  'echo "a|b" | pip install x',
  'cat <<EOF\n$(pip install x)\nEOF',
  "git commit -F - <<'EOF'\nmessage\nEOF\npip install x",
]

const PASSED = [
  'grep -iE "a|pip|b" file.txt',
  "grep -E 'x|pip|y' file.txt",
  'git commit -m "use uv | never pip install"',
  "echo 'a && pip install x'",
  'echo "pip; pip3"',
  "printf '%s\\n' 'pip (no) & more'",
  'git commit -m "say \\"a | pip\\" here"',
  'uv tool install ruff==0.17.2',
  'uvx check-jsonschema@0.39.0 --version',
  'echo pip',
  'pipx --version',
  "git commit -q -F - <<'EOF'\nfix: stop using pip\n\npip install x was replaced by uv\nEOF",
  'cat <<-"END"\n\tpip install x\n\tEND',
]

test('deny every pip command', () => {
  for (const command of DENIED) {
    assert.equal(decide(command), 'deny', command)
  }
})

test('pass a pip word that sits inside a quoted argument or is not pip', () => {
  for (const command of PASSED) {
    assert.equal(decide(command), 'pass', command)
  }
})
