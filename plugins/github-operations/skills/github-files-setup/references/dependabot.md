# Dependabot

1. When `.github/dependabot.yml` is missing, write one from `<skill-dir>/assets/dependabot.yml`: keep its GitHub Actions entry when the repository has workflows.
2. Detect the repository's package ecosystems from its manifests and add one entry each, with the directory where each manifest lives, a schedule that fits the repository, and its own labels.
3. Validate it with `uvx check-jsonschema@0.39.0 --builtin-schema vendor.dependabot .github/dependabot.yml`. Fix every error and run it again; move on only when it passes.
