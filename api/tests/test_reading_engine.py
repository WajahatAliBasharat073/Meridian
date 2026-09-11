from datetime import date, timedelta

from app.engines.reading import ReadingBookFixture, ReadingSessionFixture, compute_reading_stats


def _book(id_: int, status: str, category: str | None = None, finished: date | None = None) -> ReadingBookFixture:
    return ReadingBookFixture(id=id_, status=status, category=category, finished_date=finished)


def _session(book_id: int, on: date, page: int | None) -> ReadingSessionFixture:
    return ReadingSessionFixture(book_id=book_id, date=on, page_reached=page)


def test_status_counts_are_real_counts() -> None:
    books = [
        _book(1, "reading"),
        _book(2, "reading"),
        _book(3, "to_read"),
        _book(4, "completed", finished=date(2026, 9, 1)),
    ]
    stats = compute_reading_stats(books, [], date(2026, 9, 15))
    assert stats.reading_count == 2
    assert stats.to_read_count == 1
    assert stats.completed_count == 1


def test_completed_this_month_and_year_use_finished_date() -> None:
    books = [
        _book(1, "completed", finished=date(2026, 9, 5)),  # this month
        _book(2, "completed", finished=date(2026, 3, 1)),  # this year, not this month
        _book(3, "completed", finished=date(2024, 1, 1)),  # neither
    ]
    stats = compute_reading_stats(books, [], date(2026, 9, 15))
    assert stats.completed_this_month == 1
    assert stats.completed_this_year == 2
    assert stats.completed_count == 3


def test_pages_read_is_the_delta_between_sessions_not_the_raw_pages() -> None:
    sessions = [
        _session(1, date(2026, 8, 28), 50),  # before the window -- sets the baseline
        _session(1, date(2026, 9, 2), 80),  # +30 in-window
        _session(1, date(2026, 9, 10), 120),  # +40 in-window
    ]
    stats = compute_reading_stats([_book(1, "reading")], sessions, date(2026, 9, 15))
    assert stats.pages_read_this_month == 70


def test_pages_read_never_counts_a_backward_jump_as_negative() -> None:
    # A correction (re-reading, or fixing a typo'd page number) must not
    # subtract from the total.
    sessions = [
        _session(1, date(2026, 9, 1), 100),
        _session(1, date(2026, 9, 5), 40),  # went "backward"
    ]
    stats = compute_reading_stats([_book(1, "reading")], sessions, date(2026, 9, 15))
    assert stats.pages_read_this_month == 100  # only the first session's delta from 0


def test_streak_counts_consecutive_days_ending_today() -> None:
    today = date(2026, 9, 15)
    sessions = [
        _session(1, today, 10),
        _session(1, today - timedelta(days=1), 5),
        _session(1, today - timedelta(days=2), 1),
    ]
    stats = compute_reading_stats([_book(1, "reading")], sessions, today)
    assert stats.streak_days == 3


def test_streak_still_counts_if_today_not_yet_logged_but_yesterday_was() -> None:
    today = date(2026, 9, 15)
    sessions = [_session(1, today - timedelta(days=1), 5), _session(1, today - timedelta(days=2), 1)]
    stats = compute_reading_stats([_book(1, "reading")], sessions, today)
    assert stats.streak_days == 2


def test_streak_is_zero_after_a_gap() -> None:
    today = date(2026, 9, 15)
    sessions = [_session(1, today - timedelta(days=3), 5)]
    stats = compute_reading_stats([_book(1, "reading")], sessions, today)
    assert stats.streak_days == 0


def test_top_categories_counts_across_all_books_with_a_category() -> None:
    books = [
        _book(1, "reading", category="technical"),
        _book(2, "completed", category="technical"),
        _book(3, "to_read", category="fiction"),
        _book(4, "reading", category=None),
    ]
    stats = compute_reading_stats(books, [], date(2026, 9, 15))
    assert stats.top_categories[0] == ("technical", 2)
    assert ("fiction", 1) in stats.top_categories
