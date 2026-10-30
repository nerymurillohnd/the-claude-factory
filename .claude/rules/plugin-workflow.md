# Plugin workflow

Operating guide and map of how the plugin skills work together, for everything under `plugins/`. Each skill holds only its own step-by-step guide, including what differs between a first time and a later one; this file defines the event and what to load. To maintain the project itself, follow `maintainer-workflow.md`.

- Load `versioning` to set the initial version of a new plugin or to update the version of an existing plugin that changed.
- Load `releases` to release a new plugin for the first time or to release an existing plugin that had changes.
- When both apply, load `versioning` first.
