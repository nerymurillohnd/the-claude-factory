# Workflow

These rules set how to work on this project. Depending on the context, resume the work from the stage or area it belongs to, and apply its procedure to what is already built.

1. Management, Maintenance and Quality Gates
2. Marketplace Plugins

## Management, Maintenance and Quality Gates

1. Decision records
   - Every time Nery makes an important decision, load and use the `project-maintainer:write-records` skill.
2. Pending and resolved tasks
   - Every time an idea, task or conflict resolution could not be carried out, load and use the `project-maintainer:write-records` skill to log it.
   - Every time a pending item from the point above is withdrawn, completed or closed, load and use the `project-maintainer:write-records` skill to record it.
3. User documentation
   - To write, update or check the marketplace's own user documentation, load and use the `maintaining-user-docs` skill.
4. Issue handling and resolution
5. Local quality gates
6. Remote quality gates

## Marketplace Plugins

1. Plugin design and planning
2. Plugin creation
   - To create, scaffold, write or fix a plugin, load and use the `building-plugins` skill.
   - To create, scaffold or edit a mod, or a plugin that contains mods, load and use the `building-mods` skill. For the plugin's other components, also load `building-plugins`.
3. Plugin testing and evaluation
   - To build or run the eval suite of a plugin that contains no mods, to run the live checks of a ready plugin's MCP servers and MCP hooks, or to diagnose its install, load or marketplace errors, load and use the `testing-plugins` skill.
   - To test and troubleshoot a mod, or a plugin that contains mods, load and use the `testing-mods` skill.
4. Versioning and releases
   - Before a new plugin is published, or when an existing plugin has changed, load and use the `release-and-versioning` skill.
5. Plugin renames and removals
   - Every time an existing plugin is to be renamed, merged into another, removed, retired or deprecated, load and use the `plugin-renames-and-removals` skill.
