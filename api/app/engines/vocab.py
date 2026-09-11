"""Pure function: which words go in today's vocabulary review, and in
what order.

Same day-seeded-jitter discipline as engines/curriculum.py's ranking: a
learner who reviews nothing still sees a different set day to day, but
the order is stable across repeated loads of the *same* day rather than
reshuffling on every page refresh.

No mastery ladder here (unlike question_progress) -- `learning_status`
is the whole signal. Priority is: words flagged for revisit first, then
difficult words, then words never yet reviewed, then words still being
learned, then words already known (lowest priority, but not excluded --
occasional reinforcement of a known word is still useful review).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

_PRIORITY = {
    "need_to_revisit": 0,
    "difficult": 1,
    None: 2,
    "learning": 3,
    "known": 4,
}


@dataclass(frozen=True)
class VocabWordFixture:
    id: int
    word: str
    learning_status: str | None


def _day_jitter(word_id: int, day_ordinal: int) -> int:
    return (word_id * 31 + day_ordinal * 17) % 97


def build_daily_review(
    words: list[VocabWordFixture], today: date, count: int = 10
) -> list[VocabWordFixture]:
    day_ordinal = today.toordinal()
    ranked = sorted(
        words,
        key=lambda w: (_PRIORITY.get(w.learning_status, 2), _day_jitter(w.id, day_ordinal)),
    )
    return ranked[:count]
