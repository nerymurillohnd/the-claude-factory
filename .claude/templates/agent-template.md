---
name: {{agentName}}
description: {{agentDescription}}
tools: {{agentTools}}
model: {{agentModel}}
color: {{agentColor}}
---

<!--
  Procedure: .claude/references/agent.md
  Becomes agents/{{agentName}}.md in the plugin.
  name and description are required. name has no colon; description says when Claude should delegate to this subagent.
  tools: comma-separated, such as "Read, Grep, Glob"; delete the line to inherit every tool.
  model: sonnet, opus, haiku, fable, a full model ID, or inherit; delete the line to use the subagent model order.
  color: red, blue, green, yellow, purple, orange, pink or cyan.
  A plugin subagent ignores hooks, mcpServers, permissionMode and initialPrompt; never rely on them here. Delete this comment.
-->

You are {{agentRole}}. Your job is {{agentResponsibility}}.

{{agentInstructions}}
