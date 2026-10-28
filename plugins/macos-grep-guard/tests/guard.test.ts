import type { ProcessRunResult } from 'claude-code'
import { expect, test } from 'claude-code/testing'

type Run = ProcessRunResult
type Answers = {
  uname?: Run
  find?: Run
  nested?: Run
  inside?: Run
  others?: Run
  cached?: Run
  awk?: Run
}
type Call = { argv: readonly string[]; cwd: string | undefined; timeoutMs: number | undefined }

const run = (exitCode: number, stdout: string, stderr = ''): Run => ({
  exitCode,
  stdout,
  stderr,
  isStdoutTruncated: false,
  isStderrTruncated: false,
})
const ok = (stdout = ''): Run => run(0, stdout)
const DARWIN = ok('Darwin\n')
const BASH_OK = { result: { stdout: '', stderr: '', interrupted: false } }

/** Picks the stubbed answer for one process the guard starts. */
function answerFor(argv: readonly string[], answers: Answers): Run {
  const [program, ...rest] = argv
  if (program === 'uname') {
    return answers.uname ?? DARWIN
  }
  if (program === '/usr/bin/find' && rest.includes('-mindepth')) {
    return answers.nested ?? ok()
  }
  if (program === '/usr/bin/find') {
    return answers.find ?? ok()
  }
  if (program === 'awk') {
    return answers.awk ?? ok('0\n')
  }
  if (rest.includes('rev-parse')) {
    return answers.inside ?? ok('true\n')
  }
  if (rest.includes('--others')) {
    return answers.others ?? ok()
  }
  return answers.cached ?? ok()
}

test('a non-Darwin machine is left alone', async ($, on) => {
  const calls: Call[] = []
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => {
    calls.push({ argv: e.argv, cwd: e.init?.cwd, timeoutMs: e.init?.timeoutMs })
    return { value: answerFor(e.argv, { uname: ok('Linux\n') }) }
  })
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: 'grep -r x .' })
  expect(out.deny).toBeUndefined()
  expect(calls.map((call) => call.argv[0])).toEqual(['uname'])
})

test('a refused uname probe lets the command run', async ($, on) => {
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', () => ({ deny: 'policy: no processes' }))
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: 'grep -r x .' })
  expect(out.deny).toBeUndefined()
})

test('every probe passes cwd and a 5 second timeout explicitly', async ($, on) => {
  const calls: Call[] = []
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => {
    calls.push({ argv: e.argv, cwd: e.init?.cwd, timeoutMs: e.init?.timeoutMs })
    return { value: answerFor(e.argv, { find: ok('/repo/.gitignore\n') }) }
  })
  on('tool.call', () => BASH_OK)
  await $.tool.call({ tool: 'Bash', command: 'grep -r x . -I' })
  expect(calls.length).toBe(6)
  for (const call of calls) {
    expect(call.cwd).toBe('/')
    expect(call.timeoutMs).toBe(5000)
  }
})

test('no .gitignore under the root and a binary choice: the grep runs', async ($, on) => {
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => ({ value: answerFor(e.argv, {}) }))
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: 'grep -rn x . -I' })
  expect(out.deny).toBeUndefined()
})

test('no binary choice: denied, naming only the binary flags', async ($, on) => {
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => ({ value: answerFor(e.argv, {}) }))
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: 'grep -rn x .' })
  expect(out.deny).toContain('`--binary-files=binary`')
  expect(out.deny).not.toContain('--no-ignore-files')
})

test('a .gitignore outside any repo: denied', async ($, on) => {
  on('session.cwd', () => ({ value: '/plugins/cache/x' }))
  on('process.run', (_$, e) => ({
    value: answerFor(e.argv, {
      find: ok('/plugins/cache/x/.gitignore\n'),
      inside: run(128, '', 'fatal: not a git repository'),
    }),
  }))
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: 'grep -r x . -I' })
  expect(out.deny).toContain('--no-ignore-files')
})

test('a repo with a .gitignore that ignores nothing here: the grep runs', async ($, on) => {
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => ({ value: answerFor(e.argv, { find: ok('/repo/.gitignore\n') }) }))
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: 'grep -r x . -I' })
  expect(out.deny).toBeUndefined()
})

test('untracked ignored entries: denied', async ($, on) => {
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => ({
    value: answerFor(e.argv, { find: ok('/repo/.gitignore\n'), others: ok('node_modules/\n') }),
  }))
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: 'grep -rli x . -I' })
  expect(out.deny).toContain('--ignore-files')
})

test('a tracked file that matches .gitignore: denied', async ($, on) => {
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => ({
    value: answerFor(e.argv, { find: ok('/repo/.gitignore\n'), cached: ok('tracked.env\n') }),
  }))
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: 'grep -Rn x . -I' })
  expect(out.deny).toContain('--no-ignore-files')
})

test('a refused or timed-out find probe: denied', async ($, on) => {
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) =>
    e.argv[0] === '/usr/bin/find' ? { deny: 'timed out' } : { value: answerFor(e.argv, {}) },
  )
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: 'grep -nr x . -I' })
  expect(out.deny).toContain('--no-ignore-files')
})

test('explicit choices: no probe runs and the grep runs', async ($, on) => {
  const calls: Call[] = []
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => {
    calls.push({ argv: e.argv, cwd: e.init?.cwd, timeoutMs: e.init?.timeoutMs })
    return { value: answerFor(e.argv, {}) }
  })
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: 'grep -rli x . --ignore-files -I' })
  expect(out.deny).toBeUndefined()
  expect(calls.map((call) => call.argv[0])).toEqual(['uname'])
})

test('an earlier cd: the guard checks the folder the session moved to', async ($, on) => {
  const roots: string[] = []
  on('session.cwd', () => ({ value: '/repo/sub' }))
  on('process.run', (_$, e) => {
    if (e.argv[0] === '/usr/bin/find') {
      roots.push(e.argv[1] ?? '')
    }
    return { value: answerFor(e.argv, {}) }
  })
  on('tool.call', () => BASH_OK)
  await $.tool.call({ tool: 'Bash', command: 'grep -r x . -I' })
  expect(roots).toEqual(['/repo/sub'])
})

test('awk IGNORECASE is denied where awk ignores it, and allowed where it does not', async ($, on) => {
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => ({ value: answerFor(e.argv, {}) }))
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: "awk 'BEGIN{IGNORECASE=1} /x/' f" })
  expect(out.deny).toContain('tolower')
})

test('gawk installed as awk: IGNORECASE is allowed', async ($, on) => {
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => ({ value: answerFor(e.argv, { awk: ok('1\n') }) }))
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: "awk 'BEGIN{IGNORECASE=1} /x/' f" })
  expect(out.deny).toBeUndefined()
})

test('an error result with a BSD signature gets the macOS hint', async ($, on) => {
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => ({ value: answerFor(e.argv, {}) }))
  on('tool.call', () => ({
    result: 'Error: Exit code 1\nuniq: invalid option -- w',
    text: 'Exit code 1\nuniq: invalid option -- w',
    isError: true,
  }))
  const out = await $.tool.call({ tool: 'Bash', command: 'uniq -w1 </dev/null' })
  expect(out.context?.[0]).toContain('awk')
})

test('a successful result with a BSD error on stderr gets the hint', async ($, on) => {
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => ({ value: answerFor(e.argv, {}) }))
  on('tool.call', () => ({
    result: {
      stdout: '',
      stderr: 'find: -printf: unknown primary or operator',
      interrupted: false,
    },
  }))
  const out = await $.tool.call({ tool: 'Bash', command: "sh -c 'find . -printf %p' | head" })
  expect(out.context?.[0]).toContain('stat -f')
})

test('a signature in stdout from cat gets no hint', async ($, on) => {
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => ({ value: answerFor(e.argv, {}) }))
  on('tool.call', () => ({
    result: { stdout: 'uniq: invalid option -- w', stderr: '', interrupted: false },
  }))
  const out = await $.tool.call({ tool: 'Bash', command: 'cat notes.md' })
  expect(out.context).toBeUndefined()
})

test('a nested repository under the root: denied, though the outer git reports nothing', async ($, on) => {
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => ({
    value: answerFor(e.argv, {
      find: ok('/repo/vendor/lib/.gitignore\n'),
      nested: ok('/repo/vendor/lib/.git\n'),
    }),
  }))
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: 'grep -rl x . -I' })
  expect(out.deny).toContain('--no-ignore-files')
})

test('a nested repository probe that fails: denied', async ($, on) => {
  on('session.cwd', () => ({ value: '/repo' }))
  on('process.run', (_$, e) => ({
    value: answerFor(e.argv, {
      find: ok('/repo/.gitignore\n'),
      nested: run(1, '', 'find: /repo/locked: Permission denied'),
    }),
  }))
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: 'grep -rl x . -I' })
  expect(out.deny).toContain('--no-ignore-files')
})

test('an unknown session folder: denied, saying the folder cannot be placed', async ($, on) => {
  on('session.cwd', () => ({ deny: 'no session folder' }))
  on('process.run', (_$, e) => ({ value: answerFor(e.argv, {}) }))
  on('tool.call', () => BASH_OK)
  const out = await $.tool.call({ tool: 'Bash', command: 'grep -rl x . -I' })
  expect(out.deny).toContain('cannot tell which folder')
  expect(out.deny).toContain('--no-ignore-files')
})

test('an unknown session folder and an absolute root that ignores nothing: the grep runs', async ($, on) => {
  const roots: string[] = []
  on('session.cwd', () => ({ deny: 'no session folder' }))
  on('process.run', (_$, e) => {
    if (e.argv[0] === '/usr/bin/find') {
      roots.push(e.argv[1] ?? '')
    }
    return { value: answerFor(e.argv, { find: ok('/repo/.gitignore\n') }) }
  })
  on('tool.call', () => BASH_OK)
  const relative = await $.tool.call({ tool: 'Bash', command: 'grep -rl x . -I' })
  expect(relative.deny).toContain('absolute search path')
  const absolute = await $.tool.call({ tool: 'Bash', command: 'grep -rl x /repo -I' })
  expect(absolute.deny).toBeUndefined()
  expect(roots).toEqual(['/repo', '/repo'])
})
