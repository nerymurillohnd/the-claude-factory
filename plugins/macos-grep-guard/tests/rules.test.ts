import { describe, expect, test } from 'claude-code/testing'
import type { GrepFinding } from '../hooks/rules'
import { analyze, fallbackDenial, grepDenial, hintsFor, joinPath } from '../hooks/rules'

const CWD = '/repo'

/** The findings for a command run from /repo. */
const greps = (command: string, cwd: string | null = CWD): GrepFinding[] =>
  analyze(command, cwd).greps

describe('recursive grep that reaches the wrapper', () => {
  test('is found in the forms Claude writes', async () => {
    for (const command of [
      'grep -r TODO .',
      'grep -R TODO .',
      'grep --recursive TODO .',
      'grep -rn TODO .',
      'grep -rli TODO .',
      'grep -Rn TODO .',
      'grep -nr TODO .',
      'grep -d recurse TODO .',
      '\\grep -r TODO .',
      'time grep -r TODO .',
      'FOO=1 grep -r TODO .',
      '( grep -r TODO . )',
      'echo $(grep -r TODO .)',
      'echo `grep -r TODO .`',
      'ls && grep -r TODO .',
      'false || grep -r TODO .',
      'true; grep -r TODO .',
    ]) {
      expect(greps(command).length).toBe(1)
    }
  })

  test('is found past a pipe character inside quotes', async () => {
    expect(greps("grep -E 'a|b' -r src")).toEqual([
      { roots: ['/repo/src'], lacksIgnoreChoice: true, lacksBinaryChoice: true },
    ])
  })

  test('starts from the folder an earlier cd moved to', async () => {
    expect(greps('cd sub && grep -rn x .')[0]?.roots).toEqual(['/repo/sub'])
    expect(greps('cd /abs && grep -r x lib')[0]?.roots).toEqual(['/abs/lib'])
    expect(greps('(cd sub && true) && grep -r x .')[0]?.roots).toEqual(['/repo'])
  })

  test('defaults to the current folder', async () => {
    expect(greps('grep -r x')[0]?.roots).toEqual(['/repo'])
  })

  test('reads every path argument', async () => {
    expect(greps('grep -r x src lib')[0]?.roots).toEqual(['/repo/src', '/repo/lib'])
    expect(greps('grep -r -e x src')[0]?.roots).toEqual(['/repo/src'])
    expect(greps('grep -rA 3 x src')[0]?.roots).toEqual(['/repo/src'])
  })

  test('cannot be placed when a root or the folder is uncertain', async () => {
    for (const command of [
      'grep -r x ~/notes',
      'grep -r x "$DIR"',
      'grep -r x src*',
      'cd "$X" && grep -r x .',
      'cd - && grep -r x .',
    ]) {
      expect(greps(command).length).toBe(1)
      expect(greps(command)[0]?.roots ?? null).toBe(null)
    }
    expect(greps('grep -r x .', null)[0]?.roots ?? null).toBe(null)
    expect(greps('grep -r x /abs', null)[0]?.roots).toEqual(['/abs'])
  })

  test('records which explicit choices are missing', async () => {
    expect(greps('grep -rnI x .')[0]).toEqual({
      roots: ['/repo'],
      lacksIgnoreChoice: true,
      lacksBinaryChoice: false,
    })
    expect(greps('grep -r x . --ignore-files')[0]).toEqual({
      roots: ['/repo'],
      lacksIgnoreChoice: false,
      lacksBinaryChoice: true,
    })
    for (const binary of [
      '--binary-files=binary',
      '-a',
      '--text',
      '-W',
      '-I',
      '--no-ignore-binary',
    ]) {
      expect(greps(`grep -r x . ${binary}`)[0]?.lacksBinaryChoice).toBe(false)
    }
  })

  test('passes once both choices are written', async () => {
    expect(greps('grep -rli x . --no-ignore-files --binary-files=binary')).toEqual([])
    expect(greps('grep -r x . --ignore-files -I')).toEqual([])
  })
})

describe('grep that is not checked', () => {
  test('runs as BSD grep, which reads no ignore files', async () => {
    for (const command of [
      'command grep -r x .',
      '/usr/bin/grep -r x .',
      'env grep -r x .',
      'sudo grep -r x .',
      'xargs grep -r x',
      "sh -c 'grep -r x .'",
      'bash -c "grep -r x ."',
      'find . -exec grep -r x {} +',
    ]) {
      expect(greps(command)).toEqual([])
    }
  })

  test('is handed to BSD grep by the wrapper itself', async () => {
    for (const command of [
      'grep -rZ x .',
      'grep -r --null x .',
      'grep -r --null-data x .',
      'grep -@r x .',
      'grep -r --config x .',
    ]) {
      expect(greps(command)).toEqual([])
    }
  })

  test('is not recursive', async () => {
    for (const command of [
      'grep -c foo file.txt',
      'ls | grep x',
      'grep -n x a.txt b.txt',
      'echo "grep -r x ."',
      '# grep -r x .',
    ]) {
      expect(greps(command)).toEqual([])
    }
  })

  test('appears only inside a heredoc body', async () => {
    expect(greps('cat <<EOF\ngrep -r x .\nEOF\necho done')).toEqual([])
    expect(greps("cat <<'END' > notes.txt\ngrep -r x .\nEND")).toEqual([])
  })
})

describe('awk IGNORECASE', () => {
  test('is found in an awk program, also inside sh -c', async () => {
    expect(analyze("awk 'BEGIN{IGNORECASE=1} /x/' f", CWD).usesAwkIgnoreCase).toBe(true)
    expect(analyze(`sh -c "awk 'BEGIN{IGNORECASE=1} /x/' f"`, CWD).usesAwkIgnoreCase).toBe(true)
  })

  test('is not reported for other programs', async () => {
    expect(analyze("awk '{print}' f", CWD).usesAwkIgnoreCase).toBe(false)
    expect(analyze('echo IGNORECASE', CWD).usesAwkIgnoreCase).toBe(false)
  })
})

describe('hints', () => {
  test('fire for a verified signature from a program the command ran', async () => {
    const uniq = analyze('uniq -w1 </dev/null', CWD).programs
    expect(
      hintsFor(uniq, 'Exit code 1\nuniq: invalid option -- w\nusage: uniq [-cdiu]').length,
    ).toBe(1)
    const sed = analyze("sed -i 's/a/b/' s.txt", CWD).programs
    expect(hintsFor(sed, 'sed: 1: "s.txt\n": unterminated substitute pattern')[0]).toMatch(
      /sed -i ''/,
    )
    const timeout = analyze('timeout 5 make', CWD).programs
    expect(hintsFor(timeout, 'zsh:1: command not found: timeout').length).toBe(1)
    expect(hintsFor(timeout, 'bash: timeout: command not found').length).toBe(1)
  })

  test('fire for zsh glob errors whatever the program', async () => {
    expect(
      hintsFor(analyze('ls *.log', CWD).programs, 'zsh:1: no matches found: *.log').length,
    ).toBe(1)
  })

  test('do not fire when the program did not run', async () => {
    const cat = analyze('cat notes.md', CWD).programs
    expect(hintsFor(cat, 'uniq: invalid option -- w\nstat: illegal option -- c')).toEqual([])
  })

  test('cover the programs a command runs inside sh -c and xargs', async () => {
    expect(analyze("sh -c 'stat -c %s f'", CWD).programs.has('stat')).toBe(true)
    expect(analyze('ls | xargs grep -P x', CWD).programs.has('grep')).toBe(true)
  })
})

describe('texts', () => {
  test('name only the missing choices', async () => {
    const both = grepDenial(true, true, 'reason')
    expect(both).toContain('--no-ignore-files --binary-files=binary')
    expect(both).toContain('--ignore-files')
    const binaryOnly = grepDenial(false, true, 'reason')
    expect(binaryOnly).toContain('`--binary-files=binary`')
    expect(binaryOnly).not.toContain('--no-ignore-files')
  })

  test('fallback denies a recursive grep and lets anything else run', async () => {
    expect(fallbackDenial('grep -rn x .')).toContain('the guard failed')
    expect(fallbackDenial('ls -la')).toBe(null)
    expect(fallbackDenial(undefined)).toBe(null)
  })

  test('paths are normalised', async () => {
    expect(joinPath('/repo', '../a/./b')).toBe('/a/b')
    expect(joinPath('/repo', '/abs/')).toBe('/abs')
  })
})
