#!/usr/bin/env node
// End-to-end tests for the maintenance scripts. Each test runs against a fresh temp copy of the
// repository (TCF_ROOT), so the real working tree is never modified.
//   node --test ".github/scripts/tests/*.test.mjs"

import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { afterEach, beforeEach, describe, test } from 'node:test';
import { fileURLToPath } from 'node:url';

const REAL_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
let root;

function copyRepo() {
  const dir = mkdtempSync(join(tmpdir(), 'tcf-'));
  cpSync(REAL_ROOT, dir, {
    recursive: true,
    filter: (src) => !/[/\\](\.git|node_modules)([/\\]|$)/.test(src.slice(REAL_ROOT.length)),
  });
  return dir;
}

/** Run a script from the temp copy, so its own lib.mjs resolves ROOT to the temp copy. */
function run(script, args = []) {
  const r = spawnSync(process.execPath, [join(root, '.github', 'scripts', script), ...args], {
    cwd: root,
    encoding: 'utf8',
    env: { ...process.env, TCF_ROOT: root },
  });
  return { code: r.status, out: `${r.stdout}${r.stderr}` };
}

const read = (p) => readFileSync(join(root, p), 'utf8');
const write = (p, s) => writeFileSync(join(root, p), s);
const json = (p) => JSON.parse(read(p));

function scaffold(name = 'demo-tool', category = 'productivity', extra = []) {
  const r = run('new-plugin.mjs', ['--name', name, '--category', category, '--description', 'Does demo things.', ...extra]);
  assert.equal(r.code, 0, r.out);
}

/** Keep only the Compatibility rows whose text contains one of `keep`. */
function pruneCompat(name, keep) {
  const p = `plugins/${name}/README.md`;
  const text = read(p);
  const start = text.search(/^## .*Compatibility/m);
  const end = text.indexOf('\n## ', start + 1);
  const section = text
    .slice(start, end)
    .split('\n')
    .filter((l) => !l.startsWith('| ') || /^\| (Component|:--)/.test(l) || keep.some((k) => l.includes(k)))
    .join('\n');
  write(p, text.slice(0, start) + section + text.slice(end));
}

/** Simulate a maintainer finishing the plugin: add one skill, resolve TODOs, trim the Compatibility table. */
function resolveTodos(name = 'demo-tool') {
  mkdirSync(join(root, `plugins/${name}/skills/demo`), { recursive: true });
  write(`plugins/${name}/skills/demo/SKILL.md`, '---\ndescription: Demo skill. Use when testing.\n---\nDo it.\n');
  const p = `plugins/${name}/README.md`;
  write(p, read(p).replace(/<!--\s*(TODO|TEMPLATE)[\s\S]*?-->\n?/g, ''));
  pruneCompat(name, ['Skills']);
  assert.equal(run('catalog.mjs').code, 0);
}

beforeEach(() => {
  root = copyRepo();
});
afterEach(() => {
  rmSync(root, { recursive: true, force: true });
});

describe('check-repo', () => {
  test('passes on the pristine repository', () => {
    const r = run('check-repo.mjs');
    assert.equal(r.code, 0, r.out);
  });

  test('fails on a freshly scaffolded plugin until its TODOs are resolved', () => {
    scaffold();
    const before = run('check-repo.mjs');
    assert.equal(before.code, 1);
    assert.match(before.out, /unresolved TODO\/TEMPLATE comments/);

    resolveTodos();
    const after = run('check-repo.mjs');
    assert.equal(after.code, 0, after.out);
  });

  test('flags a plugin directory missing from marketplace.json', () => {
    mkdirSync(join(root, 'plugins', 'orphan', '.claude-plugin'), { recursive: true });
    const r = run('check-repo.mjs');
    assert.equal(r.code, 1);
    assert.match(r.out, /plugins\/orphan.*not listed/);
  });

  test('flags a version on the marketplace entry', () => {
    scaffold();
    resolveTodos();
    const mp = json('.claude-plugin/marketplace.json');
    mp.plugins[0].version = '9.9.9';
    write('.claude-plugin/marketplace.json', `${JSON.stringify(mp, null, 2)}\n`);
    const r = run('check-repo.mjs');
    assert.equal(r.code, 1);
    assert.match(r.out, /do not set version on the entry/);
  });

  test('flags a manifest name that differs from the entry name', () => {
    scaffold();
    resolveTodos();
    const p = 'plugins/demo-tool/.claude-plugin/plugin.json';
    write(p, read(p).replace('"name": "demo-tool"', '"name": "other"'));
    const r = run('check-repo.mjs');
    assert.equal(r.code, 1);
    assert.match(r.out, /must equal the entry name/);
  });

  test('flags a missing required README section', () => {
    scaffold();
    resolveTodos();
    const p = 'plugins/demo-tool/README.md';
    write(p, read(p).replace(/^## 🧭 Compatibility$/m, '## Platforms'));
    const r = run('check-repo.mjs');
    assert.equal(r.code, 1);
    assert.match(r.out, /missing the "Compatibility" section/);
  });

  test('requires a valid metadata.surfaces declaration', () => {
    scaffold();
    resolveTodos();
    const p = 'plugins/demo-tool/.claude-plugin/plugin.json';
    const m = json(p);
    m.metadata.surfaces = ['cowork'];
    write(p, `${JSON.stringify(m, null, 2)}\n`);
    const r = run('check-repo.mjs');
    assert.equal(r.code, 1);
    assert.match(r.out, /metadata\.surfaces must be one of/);
  });

  test('a bin/ plugin must be declared Claude Code-only', () => {
    scaffold();
    resolveTodos();
    mkdirSync(join(root, 'plugins/demo-tool/bin'), { recursive: true });
    write('plugins/demo-tool/bin/tool', '#!/bin/sh\necho hi\n');
    const r = run('check-repo.mjs');
    assert.equal(r.code, 1);
    assert.match(r.out, /bin\/, which makes Cowork refuse the plugin/);
    assert.match(r.out, /no row for Executables/);
  });

  test('a Claude Code-only plugin passes when declared everywhere', () => {
    scaffold('lang-tool', 'language-support', ['--claude-code-only']);
    mkdirSync(join(root, 'plugins/lang-tool/bin'), { recursive: true });
    write('plugins/lang-tool/bin/tool', '#!/bin/sh\necho hi\n');
    const p = 'plugins/lang-tool/README.md';
    write(p, read(p).replace(/<!--\s*(TODO|TEMPLATE)[\s\S]*?-->\n?/g, 'it needs bin/ executables'));
    pruneCompat('lang-tool', ['Executables']);
    assert.equal(run('catalog.mjs').code, 0);
    assert.deepEqual(json('plugins/lang-tool/.claude-plugin/plugin.json').metadata.surfaces, ['claude-code']);
    assert.match(read(p), /works%20in-Claude%20Code%20only-/);
    assert.match(read('README.md'), /💻 Code only/);
    const r = run('check-repo.mjs');
    assert.equal(r.code, 0, r.out);
  });

  test('flags Compatibility rows for components the plugin does not ship', () => {
    scaffold();
    resolveTodos();
    const p = 'plugins/demo-tool/README.md';
    write(p, read(p).replace('| 🎯 Skills |', '| 🤖 Agents | ✅ | ✅ | ➖ |\n| 🎯 Skills |'));
    const r = run('check-repo.mjs');
    assert.equal(r.code, 1);
    assert.match(r.out, /lists Agents, which the plugin doesn't ship/);
  });

  test('flags a stale README catalog', () => {
    scaffold();
    resolveTodos();
    write('README.md', read('README.md').replace(/demo-tool@the-claude-factory/, 'stale'));
    const r = run('check-repo.mjs');
    assert.equal(r.code, 1);
    assert.match(r.out, /catalog is out of date/);
  });
});

describe('new-plugin', () => {
  test('rejects names Claude Code reserves for Anthropic', () => {
    const r = run('new-plugin.mjs', ['--name', 'claude-helper', '--category', 'productivity', '--description', 'x']);
    assert.equal(r.code, 1);
    assert.match(r.out, /passes as an Anthropic plugin name/);
  });

  test('rejects unknown categories', () => {
    const r = run('new-plugin.mjs', ['--name', 'demo-tool', '--category', 'nope', '--description', 'x']);
    assert.equal(r.code, 1);
    assert.match(r.out, /Unknown category/);
  });

  test('registers the entry, renders templates and updates the catalog', () => {
    const before = json('.claude-plugin/marketplace.json').plugins;
    scaffold();
    const mp = json('.claude-plugin/marketplace.json');
    const expected = [
      ...before,
      { name: 'demo-tool', source: './plugins/demo-tool', description: 'Does demo things.', category: 'productivity' },
    ].sort((a, b) => a.name.localeCompare(b.name));
    assert.deepEqual(mp.plugins, expected);
    const manifest = json('plugins/demo-tool/.claude-plugin/plugin.json');
    assert.equal(manifest.version, '0.1.0');
    assert.equal(manifest.displayName, 'Demo Tool');
    assert.doesNotMatch(read('plugins/demo-tool/README.md'), /\{\{\w+\}\}/);
    assert.ok(existsSync(join(root, 'plugins/demo-tool/LICENSE')));
    const readme = read('README.md');
    assert.match(readme, /\[\*\*Demo Tool\*\*\]\(\.\/plugins\/demo-tool#readme\)/);
    assert.match(readme, new RegExp(`plugins-${before.length + 1}-D97757`));
    assert.equal(run('catalog.mjs', ['--check']).code, 0);
  });

  test('refuses to overwrite an existing plugin', () => {
    scaffold();
    const r = run('new-plugin.mjs', ['--name', 'demo-tool', '--category', 'productivity', '--description', 'x']);
    assert.equal(r.code, 1);
    assert.match(r.out, /already exists/);
  });
});

describe('bump-version', () => {
  test('refuses to release an empty [Unreleased] section', () => {
    scaffold();
    const r = run('bump-version.mjs', ['demo-tool', 'minor']);
    assert.equal(r.code, 1);
    assert.match(r.out, /\[Unreleased\] is empty/);
  });

  test('bumps plugin.json and rolls the changelog with links', () => {
    scaffold();
    const p = 'plugins/demo-tool/CHANGELOG.md';
    write(p, read(p).replace('## [Unreleased]\n', '## [Unreleased]\n\n### Fixed\n\n- A bug.\n'));
    const r = run('bump-version.mjs', ['demo-tool', 'minor']);
    assert.equal(r.code, 0, r.out);
    assert.equal(json('plugins/demo-tool/.claude-plugin/plugin.json').version, '0.2.0');
    const log = read(p);
    assert.match(log, /## \[Unreleased\]\n\n## \[0\.2\.0\] - \d{4}-\d{2}-\d{2}\n\n### Fixed\n\n- A bug\./);
    assert.match(log, /\[Unreleased\]: .*compare\/demo-tool--v0\.2\.0\.\.\.HEAD/);
    assert.match(log, /\[0\.2\.0\]: .*releases\/tag\/demo-tool--v0\.2\.0/);
    assert.match(read('README.md'), /`0\.2\.0`/);
  });

  test('bumps the marketplace version and root changelog', () => {
    write('CHANGELOG.md', read('CHANGELOG.md').replace('## [Unreleased]\n', '## [Unreleased]\n\n### Added\n\n- Something.\n'));
    const r = run('bump-version.mjs', ['marketplace', 'patch']);
    assert.equal(r.code, 0, r.out);
    assert.equal(json('.claude-plugin/marketplace.json').version, '0.1.1');
    assert.match(read('CHANGELOG.md'), /## \[0\.1\.1\] - /);
    assert.equal(run('check-repo.mjs').code, 0);
  });
});

describe('check-version-bump', () => {
  const git = (...args) => execFileSync('git', args, { cwd: root, encoding: 'utf8' });
  function initRepo() {
    git('init', '-q', '-b', 'main');
    git('config', 'user.email', 'test@example.com');
    git('config', 'user.name', 'Test');
    git('add', '-A');
    git('commit', '-qm', 'base');
  }

  test('fails when shipped files change without a bump, passes after bumping', () => {
    scaffold();
    initRepo();
    mkdirSync(join(root, 'plugins/demo-tool/skills/demo'), { recursive: true });
    write('plugins/demo-tool/skills/demo/SKILL.md', '---\ndescription: Demo.\n---\nDo it.\n');
    git('add', '-A');
    git('commit', '-qm', 'change');

    const before = run('check-version-bump.mjs', ['HEAD~1']);
    assert.equal(before.code, 1);
    assert.match(before.out, /version is still 0\.1\.0/);

    const p = 'plugins/demo-tool/CHANGELOG.md';
    write(p, read(p).replace('## [Unreleased]\n', '## [Unreleased]\n\n### Added\n\n- Demo skill.\n'));
    assert.equal(run('bump-version.mjs', ['demo-tool', 'minor']).code, 0);
    git('add', '-A');
    git('commit', '-qm', 'bump');
    const after = run('check-version-bump.mjs', ['HEAD~2']);
    assert.equal(after.code, 0, after.out);
  });

  test('does not require a bump for README-only edits', () => {
    scaffold();
    initRepo();
    write('plugins/demo-tool/README.md', `${read('plugins/demo-tool/README.md')}\nMore docs.\n`);
    git('commit', '-qam', 'docs');
    const r = run('check-version-bump.mjs', ['HEAD~1']);
    assert.equal(r.code, 0, r.out);
  });
});

describe('lib', () => {
  test('changelogSection extracts one version body', async () => {
    const { changelogSection } = await import(join(REAL_ROOT, '.github/scripts/lib.mjs'));
    const text = '# C\n\n## [Unreleased]\n\n## [1.1.0] - 2026-01-02\n\n- b\n\n## [1.0.0] - 2026-01-01\n\n- a\n\n[1.1.0]: x\n';
    assert.equal(changelogSection(text, '1.1.0'), '- b');
    assert.equal(changelogSection(text, '1.0.0'), '- a');
    assert.equal(changelogSection(text, '2.0.0'), null);
  });

  test('anchor matches GitHub heading slugs, keeping emoji variation selectors', async () => {
    const { anchor } = await import(join(REAL_ROOT, '.github/scripts/catalog.mjs'));
    assert.equal(anchor('⚡ Productivity'), '-productivity');
    assert.equal(anchor('🛠️ Development'), '️-development');
    assert.equal(anchor('🧪 Testing & Quality'), '-testing--quality');
  });
});
