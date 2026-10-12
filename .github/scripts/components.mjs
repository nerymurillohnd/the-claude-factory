// Detects which component types a plugin ships, from its standard layout and manifest.

import { existsSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { loadManifest, pluginDir } from './lib.mjs';

export const COMPONENT_TYPES = [
  { id: 'skills', emoji: '🎯', label: 'Skills' },
  { id: 'commands', emoji: '⌨️', label: 'Commands' },
  { id: 'agents', emoji: '🤖', label: 'Agents' },
  { id: 'hooks', emoji: '🪝', label: 'Hooks' },
  { id: 'mcp', emoji: '🔌', label: 'MCP' },
  { id: 'lsp', emoji: '🧠', label: 'LSP' },
  { id: 'outputStyles', emoji: '🎨', label: 'Output styles' },
  { id: 'monitors', emoji: '📡', label: 'Monitors' },
  { id: 'workflows', emoji: '🔁', label: 'Workflows' },
  { id: 'themes', emoji: '🌈', label: 'Themes' },
  { id: 'bin', emoji: '⚙️', label: 'Executables' },
];

function countFiles(dir, predicate) {
  if (!existsSync(dir)) return 0;
  let n = 0;
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) n += countFiles(full, predicate);
    else if (predicate(entry, full)) n += 1;
  }
  return n;
}

/** Returns { skills: 2, agents: 1, ... } with only the component types present. */
export function detectComponents(name) {
  const dir = pluginDir(name);
  const manifest = loadManifest(name) ?? {};
  const found = {};
  const set = (id, n) => {
    if (n > 0) found[id] = n;
  };

  set('skills', countFiles(join(dir, 'skills'), (f) => f === 'SKILL.md') + (existsSync(join(dir, 'SKILL.md')) ? 1 : 0));
  set('commands', countFiles(join(dir, 'commands'), (f) => f.endsWith('.md')));
  set('agents', countFiles(join(dir, 'agents'), (f) => f.endsWith('.md')));
  set('hooks', existsSync(join(dir, 'hooks', 'hooks.json')) || manifest.hooks ? 1 : 0);
  set('mcp', existsSync(join(dir, '.mcp.json')) || manifest.mcpServers ? 1 : 0);
  set('lsp', existsSync(join(dir, '.lsp.json')) || manifest.lspServers ? 1 : 0);
  set('outputStyles', countFiles(join(dir, 'output-styles'), (f) => f.endsWith('.md')));
  set('monitors', existsSync(join(dir, 'monitors', 'monitors.json')) || manifest.experimental?.monitors ? 1 : 0);
  set('workflows', countFiles(join(dir, 'workflows'), (f) => f.endsWith('.js')));
  set('themes', countFiles(join(dir, 'themes'), (f) => f.endsWith('.json')));
  set('bin', countFiles(join(dir, 'bin'), () => true));
  return found;
}

export function componentBadges(found) {
  return COMPONENT_TYPES.filter((t) => found[t.id])
    .map((t) => `${t.emoji} ${t.label}`)
    .join(' · ');
}
