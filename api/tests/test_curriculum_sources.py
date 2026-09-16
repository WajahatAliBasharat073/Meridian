"""Regression coverage for scripts/curriculum_sources.py's khangich
question parser -- added after a real bug shipped to the live question
bank: a numbered item's own text that soft-wrapped onto a plain
continuation line was truncated (the wrapped words were silently
dropped), and a lettered sub-item's own wrapped continuation was
mis-attributed back to the numbered item's title instead of the
sub-item. Both corrupted real rows in production before being caught.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import curriculum_sources as cs


def _write_source(tmp_path: Path, body: str) -> None:
    khangich = tmp_path / "machine-learning-interview"
    khangich.mkdir()
    (khangich / "questions.md").write_text(body, encoding="utf-8")


@pytest.fixture(autouse=True)
def _point_at_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cs, "KHANGICH", tmp_path / "machine-learning-interview")


def test_numbered_item_joins_a_wrapped_continuation_line(tmp_path: Path) -> None:
    # This is the exact real-world case that shipped broken: #21's own
    # text wraps onto two plain lines with no leading number or letter.
    _write_source(
        tmp_path,
        "## Machine Learning fundamentals\n"
        "21. Assumptions about linear regression: 3 residual errors follow a normal distribution and\n"
        "independent with each other, output and input have linear distribution, low collinearity\n"
        "between input features.\n"
        "22. Explain the concept of bias vs variance\n",
    )
    records = cs.parse_khangich_questions()
    titles = [r.title for r in records]
    assert (
        "Assumptions about linear regression: 3 residual errors follow a normal distribution "
        "and independent with each other, output and input have linear distribution, low "
        "collinearity between input features" in titles
    )
    # The next item must not have absorbed any of the wrapped text.
    assert "Explain the concept of bias vs variance" in titles


def test_sub_item_continuation_stays_with_the_sub_item_not_the_title(tmp_path: Path) -> None:
    # #43's sub-item "d." wraps onto a plain line -- that continuation
    # belongs to "d.", not to the numbered item's own title, which is
    # exactly what broke: "Explain the decision tree" was corrupted into
    # "Explain the decision tree do we need which".
    _write_source(
        tmp_path,
        "## Machine Learning fundamentals\n"
        "43. Explain the decision tree\n"
        "a. Why do we need a decision tree?\n"
        "d. What is the cost function? Why do we need that cost function? And in which case\n"
        "do we need which\n"
        "e. What does tree pruning mean?\n",
    )
    records = cs.parse_khangich_questions()
    assert len(records) == 1
    record = records[0]
    assert record.title == "Explain the decision tree"
    assert (
        "What is the cost function? Why do we need that cost function? And in which case "
        "do we need which" in record.follow_ups
    )


def test_titles_and_follow_ups_are_capitalized(tmp_path: Path) -> None:
    _write_source(
        tmp_path,
        "## Machine Learning fundamentals\n"
        "29. how to handle unbalanced data.\n"
        "30. how do you inspect missing data\n"
        "a. kernel choice\n",
    )
    records = cs.parse_khangich_questions()
    titles = [r.title for r in records]
    assert "How to handle unbalanced data?" in titles
    inspect_record = next(r for r in records if "inspect" in r.title.lower())
    assert inspect_record.title.startswith("How")
    assert inspect_record.follow_ups == ["Kernel choice"]


def test_answer_appended_after_a_colon_is_still_dropped(tmp_path: Path) -> None:
    # The parser's core job, unaffected by the continuation-joining fix:
    # "Explain X: It is ..." keeps only "Explain X" -- the split only
    # fires when the answer starts with a capital letter (the source's
    # own convention isn't consistent about this; a lowercase-led answer,
    # e.g. real item #47 "Explain MLP: kind of...", is a known separate
    # gap this parser doesn't attempt to close).
    _write_source(
        tmp_path,
        "## Machine Learning fundamentals\n"
        "47. Explain gradient descent: It converges once the loss stops decreasing\n",
    )
    records = cs.parse_khangich_questions()
    assert len(records) == 1
    assert records[0].title == "Explain gradient descent"


def test_discarded_remainder_that_reads_as_a_question_becomes_a_follow_up(tmp_path: Path) -> None:
    # Real item #63: the split logic can't tell "answer follows" apart
    # from "a second, distinct question follows" just from punctuation --
    # when the remainder itself ends in "?", it's the latter, and belongs
    # in follow_ups rather than being silently discarded as an answer.
    _write_source(
        tmp_path,
        "## Machine Learning fundamentals\n"
        "63. Explain RNN Problem. How does LSTM help solve it?\n",
    )
    records = cs.parse_khangich_questions()
    assert len(records) == 1
    assert records[0].title == "Explain RNN Problem"
    assert records[0].follow_ups == ["How does LSTM help solve it?"]


def test_a_line_broken_in_the_source_itself_is_dropped_not_imported_half_finished(
    tmp_path: Path,
) -> None:
    # Real item #33: cuts off mid-word in the source repo itself ("...v.s."
    # presumably meant to continue "v.s. discriminative", never finished).
    # There's no continuation to join and nothing to complete honestly, so
    # this specific known-broken line is dropped rather than shipped as a
    # half sentence -- a complete version of the same question already
    # exists via a different, unrelated source.
    _write_source(
        tmp_path,
        "## Machine Learning fundamentals\n"
        "33. general ML questions like generative v.s.\n"
        "34. What is the difference between type I vs type II error?\n",
    )
    records = cs.parse_khangich_questions()
    titles = [r.title for r in records]
    assert not any("generative" in t.lower() for t in titles)
    assert "What is the difference between type I vs type II error?" in titles


def test_missing_source_file_returns_empty_list() -> None:
    assert cs.parse_khangich_questions() == []
