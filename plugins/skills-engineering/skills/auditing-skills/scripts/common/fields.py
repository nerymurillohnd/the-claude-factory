"""The frontmatter field tables every check reads, and nowhere else.

Taken from the Claude Code frontmatter reference (2.1.326), the Agent Skills specification and
the upload validator of anthropics/skills (`quick_validate.py`).
"""

# Every field the Claude Code frontmatter reference lists, in its table order.
CLAUDE_CODE_FIELDS: tuple[str, ...] = (
    "name",
    "description",
    "when_to_use",
    "argument-hint",
    "arguments",
    "disable-model-invocation",
    "user-invocable",
    "allowed-tools",
    "disallowed-tools",
    "model",
    "effort",
    "context",
    "agent",
    "background",
    "hooks",
    "paths",
    "shell",
    "metadata",
    "license",
    "compatibility",
)

# The fields of the Agent Skills specification, the only ones an upload accepts.
SPEC_FIELDS: tuple[str, ...] = (
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
)

BOOLEAN_FIELDS: tuple[str, ...] = ("disable-model-invocation", "user-invocable", "background")

# The boolean forms Claude Code accepts, matched case-insensitively.
BOOLEAN_FORMS: frozenset[str] = frozenset({"true", "false", "yes", "no", "on", "off", "1", "0"})

EFFORT_LEVELS: tuple[str, ...] = ("low", "medium", "high", "xhigh", "max")

# Aliases /model accepts, plus inherit; a full model id is checked by its form, not this list.
MODEL_VALUES: tuple[str, ...] = (
    "default",
    "best",
    "fable",
    "sonnet",
    "opus",
    "haiku",
    "sonnet[1m]",
    "opus[1m]",
    "opusplan",
    "inherit",
)

# Fields whose value is text, where a YAML boolean or null reads differently than written.
TEXT_FIELDS: tuple[str, ...] = (
    "name",
    "description",
    "when_to_use",
    "argument-hint",
    "model",
    "effort",
    "context",
    "agent",
    "shell",
    "license",
    "compatibility",
)

# The source each rule area rests on.
SOURCES: dict[str, str] = {
    "claude-code": "https://code.claude.com/docs/en/skills#frontmatter-reference",
    "open-spec": "https://agentskills.io/specification",
    "best-practices": (
        "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices"
    ),
    "upload": (
        "https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/quick_validate.py"
    ),
}
