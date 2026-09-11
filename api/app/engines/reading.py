"""Pure functions: reading statistics from real books/sessions only.

Same discipline as punctuality.py/theory_pace.py -- a streak or a
pages-read figure with nothing behind it is 0, never a fabricated
number. `page_reached` is a position (see models/life.py's ReadingBook
docstring), so "pages read" in a window is derived from the delta
between consecutive sessions, not summed directly.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class ReadingSessionFixture:
    book_id: int
    date: date
    page_reached: int | None


@dataclass(frozen=True)
class ReadingBookFixture:
    id: int
    status: str
    category: str | None
    finished_date: date | None


@dataclass(frozen=True)
class ReadingStats:
    completed_count: int
    reading_count: int
    to_read_count: int
    completed_this_month: int
    completed_this_year: int
    pages_read_this_month: int
    streak_days: int
    top_categories: list[tuple[str, int]]


def _pages_read_in_window(
    sessions: list[ReadingSessionFixture], window_start: date, window_end: date
) -> int:
    by_book: dict[int, list[ReadingSessionFixture]] = {}
    for s in sessions:
        if s.page_reached is not None:
            by_book.setdefault(s.book_id, []).append(s)

    total = 0
    for book_sessions in by_book.values():
        ordered = sorted(book_sessions, key=lambda s: s.date)
        previous_page = 0
        for s in ordered:
            assert s.page_reached is not None
            delta = max(0, s.page_reached - previous_page)
            if window_start <= s.date <= window_end:
                total += delta
            previous_page = s.page_reached
    return total


def _reading_streak(sessions: list[ReadingSessionFixture], today: date) -> int:
    """Consecutive days with at least one session, ending today or
    yesterday -- not logging *yet* today doesn't zero out an ongoing
    streak, but skipping two days in a row does."""
    active_dates = {s.date for s in sessions}
    if today in active_dates:
        cursor = today
    elif (today - timedelta(days=1)) in active_dates:
        cursor = today - timedelta(days=1)
    else:
        return 0

    streak = 0
    while cursor in active_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def compute_reading_stats(
    books: list[ReadingBookFixture], sessions: list[ReadingSessionFixture], today: date
) -> ReadingStats:
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    completed = [b for b in books if b.status == "completed"]

    return ReadingStats(
        completed_count=len(completed),
        reading_count=sum(1 for b in books if b.status == "reading"),
        to_read_count=sum(1 for b in books if b.status == "to_read"),
        completed_this_month=sum(
            1 for b in completed if b.finished_date and b.finished_date >= month_start
        ),
        completed_this_year=sum(
            1 for b in completed if b.finished_date and b.finished_date >= year_start
        ),
        pages_read_this_month=_pages_read_in_window(sessions, month_start, today),
        streak_days=_reading_streak(sessions, today),
        top_categories=Counter(b.category for b in books if b.category).most_common(5),
    )
