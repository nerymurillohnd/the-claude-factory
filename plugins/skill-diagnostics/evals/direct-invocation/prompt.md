---
description: "Direct invocation, CI only: the user runs /skill-diagnostics:skills-best-practices on the seeded-defect fixture, so a description that never triggers can't hide whether the body works. The skill must run and report the seeded defect. Grants needed: claude plugin eval . --case '<name>' --trust-plugin --scaffold --allow-tools Write Edit 'Bash(python3 *)' 'Bash(claude --version)' 'WebFetch(domain:code.claude.com)' 'WebFetch(domain:platform.claude.com)' 'WebFetch(domain:support.claude.com)' 'WebFetch(domain:claude.com)' 'WebFetch(domain:agentskills.io)' 'WebFetch(domain:github.com)' 'WebFetch(domain:raw.githubusercontent.com)'; without the WebFetch grants the verifier cannot reach the official sources and the verdict is provisional. Bash forces the OS sandbox (bubblewrap and socat on Linux)."
tags: [audit, direct]
max_turns: 120
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Agent, Bash]
---

/skill-diagnostics:skills-best-practices skills/invoice-pack
