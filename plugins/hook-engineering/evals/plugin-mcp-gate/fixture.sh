#!/usr/bin/env bash
# Seeds a plugin named acme-tools that declares one MCP server, warehouse, with a drop_table tool.
set -euo pipefail
git init -q
mkdir -p .claude-plugin server
cat > .claude-plugin/plugin.json << 'EOF'
{ "name": "acme-tools", "version": "0.1.0", "description": "Warehouse tools for the Acme team" }
EOF
cat > .mcp.json << 'EOF'
{ "mcpServers": { "warehouse": { "command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/server/index.js"] } } }
EOF
cat > server/README.md << 'EOF'
# warehouse MCP server

Tools: list_tables, query (read-only SQL), drop_table. drop_table takes one argument, `table`, the table's name.
EOF
git add -A && git -c user.name=Fixture -c user.email=fixture@example.test commit -qm "Initial plugin"
