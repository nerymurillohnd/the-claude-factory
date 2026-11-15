#!/usr/bin/env bash
# Seeds a plugin named acme-tools with one agent, db-agent, a tunnel script and no hooks yet.
set -euo pipefail
git init -q
mkdir -p .claude-plugin agents scripts
cat > .claude-plugin/plugin.json << 'EOF'
{ "name": "acme-tools", "version": "0.1.0", "description": "Database helpers for the Acme team" }
EOF
cat > agents/db-agent.md << 'EOF'
---
name: db-agent
description: Runs read-only queries against the reporting database. Use for any question about report data.
tools: Bash, Read
---

You answer questions about the reporting database with read-only SQL through psql on localhost:5432.
EOF
cat > scripts/tunnel.sh << 'EOF'
#!/usr/bin/env bash
# Opens or closes the SSH tunnel to the reporting database: tunnel.sh open|close
set -euo pipefail
case "${1:-}" in
  open) ssh -fN -o ExitOnForwardFailure=yes -S /tmp/acme-db.sock -M -L 5432:reporting.db.internal:5432 bastion.example.test ;;
  close) ssh -S /tmp/acme-db.sock -O exit bastion.example.test ;;
  *) echo "usage: tunnel.sh open|close" >&2; exit 64 ;;
esac
EOF
chmod +x scripts/tunnel.sh
git add -A && git -c user.name=Fixture -c user.email=fixture@example.test commit -qm "Initial plugin"
