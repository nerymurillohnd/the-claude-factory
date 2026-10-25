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
4. Issue handling and resolution
5. Local quality gates
6. Remote quality gates

## Marketplace Plugins

1. Plugin design and planning
2. Plugin creation
3. Plugin testing and evaluation
4. Versioning and releases
   - Before a new plugin is published, or when an existing plugin has changed, load and use the `release-and-versioning` skill.
5. Plugin renames and removals
   - Every time an existing plugin is to be renamed or removed, load and use the `plugin-renames-and-removals` skill.
