---
description: "Seeded defect (guide section 11), CI only. A user asks in plain words, with no slash command, to check a ten-file skill whose output-deciding defect lives only in one script's argument list: render.py accepts en, fr and de, while the country table, a template and SKILL.md treat es as supported. Claude must invoke skills-best-practices on its own, run the three scripts, launch all six agents, report the defect, record a fail verdict and change no file. finds-defect is scored in both arms and measures what the plugin adds. Grants needed: claude plugin eval . --case '<name>' --trust-plugin --scaffold --allow-tools Write Edit 'Bash(python3 *)' 'Bash(claude --version)' 'WebFetch(domain:code.claude.com)' 'WebFetch(domain:platform.claude.com)' 'WebFetch(domain:support.claude.com)' 'WebFetch(domain:claude.com)' 'WebFetch(domain:agentskills.io)' 'WebFetch(domain:github.com)' 'WebFetch(domain:raw.githubusercontent.com)'; without the WebFetch grants the verifier cannot reach the official sources and the verdict is provisional. Bash forces the OS sandbox (bubblewrap and socat on Linux)."
tags: [audit, agents, defect]
max_turns: 120
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Agent, Bash]
---

Can you check my skill in skills/invoice-pack before I share it with my team? I want to know if anything in it is broken.
