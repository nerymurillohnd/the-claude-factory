"""Topic tags and near-duplicate candidates from words alone, before any model is involved.

Keyword matching misses semantic duplicates and semantics alone cannot be reproduced, so the
script proposes candidate pairs here and the auditors confirm or reject them.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import TYPE_CHECKING, cast

from aca.jsonutil import as_obj, read_json, str_list

if TYPE_CHECKING:
    from pathlib import Path

WORD = re.compile(r"[a-z0-9][a-z0-9_.+-]*")
STOPWORDS = frozenset(
    (
        "a",
        "all",
        "always",
        "an",
        "and",
        "any",
        "are",
        "as",
        "at",
        "be",
        "before",
        "by",
        "can",
        "do",
        "does",
        "each",
        "every",
        "for",
        "from",
        "has",
        "have",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "must",
        "never",
        "not",
        "of",
        "on",
        "or",
        "our",
        "should",
        "so",
        "that",
        "the",
        "their",
        "them",
        "then",
        "there",
        "these",
        "this",
        "to",
        "use",
        "used",
        "using",
        "when",
        "where",
        "which",
        "will",
        "with",
        "you",
        "your",
    ),
)
MIN_TOKENS = 6
MIN_SIMILARITY = 0.45
MAX_PAIRS = 200


@dataclass(frozen=True)
class Pair:
    """Two units in different sources whose words overlap enough to compare semantically."""

    left: tuple[str, int, int]
    right: tuple[str, int, int]
    score: float
    shared_topics: tuple[str, ...]


def tokens(text: str) -> frozenset[str]:
    """Content words of a unit, lowercased."""
    found = cast("list[str]", WORD.findall(text.lower()))
    return frozenset(word for word in found if word not in STOPWORDS)


def load_topics(path: Path) -> dict[str, list[str]]:
    """Read the topic taxonomy: topic -> keywords."""
    return {name: str_list(words) for name, words in as_obj(read_json(path)).items()}


def tag(text: str, taxonomy: dict[str, list[str]]) -> list[str]:
    """Topics whose keywords appear in the text."""
    words = tokens(text)
    lowered = text.lower()
    return sorted(
        topic
        for topic, keywords in taxonomy.items()
        if any(
            (keyword in words) if " " not in keyword else (keyword in lowered)
            for keyword in keywords
        )
    )


def jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    """Shared words over all words."""
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def candidate_pairs(
    items: list[tuple[str, int, int, str]],
    taxonomy: dict[str, list[str]],
) -> list[Pair]:
    """Pairs of units (sid, start, end, text) from different sources that look alike."""
    prepared = [
        (sid, start, end, words, tuple(tag(text, taxonomy)))
        for sid, start, end, text in items
        if len(words := tokens(text)) >= MIN_TOKENS
    ]
    pairs: list[Pair] = []
    for index, (sid, start, end, words, topics) in enumerate(prepared):
        for other_sid, other_start, other_end, other_words, other_topics in prepared[index + 1 :]:
            if other_sid == sid:
                continue
            score = jaccard(words, other_words)
            if score >= MIN_SIMILARITY:
                shared = tuple(sorted(set(topics) & set(other_topics)))
                pairs.append(
                    Pair((sid, start, end), (other_sid, other_start, other_end), score, shared)
                )
    pairs.sort(key=lambda pair: (-pair.score, pair.left, pair.right))
    return pairs[:MAX_PAIRS]
