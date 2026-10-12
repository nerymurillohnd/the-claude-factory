# Changelog

All notable changes to **Plugin Test Bench** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-12

### Added

- `test-install` skill: installs the plugin from a commit into a throwaway Claude Code configuration, as a marketplace install copies it; reports files the copy lacks; checks the load in Claude Code's startup report; runs the eval suite against the installed copy; optionally runs real requests and packages a zip for the Claude app; removes everything it created, including its sign-in.
- `review-evals` skill: reviews every eval case for what it proves, how its graders score with and without the plugin, triggering measured as a rate, run isolation and fixtures, and reports a verdict and exact fix per case.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/plugin-test-bench--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-test-bench--v0.1.0
