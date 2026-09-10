from app.schemas import AUTO_REVIEW_STATUSES, resolve_needs_review


def test_solved_with_help_auto_flags_for_review() -> None:
    assert resolve_needs_review("solved_with_help", None) is True


def test_struggled_and_no_idea_also_auto_flag() -> None:
    assert resolve_needs_review("struggled", None) is True
    assert resolve_needs_review("no_idea", None) is True


def test_a_confident_status_does_not_auto_flag() -> None:
    assert resolve_needs_review("already_know", None) is False
    assert resolve_needs_review("easy", None) is False
    assert resolve_needs_review("understood", None) is False


def test_clearing_status_clears_the_flag() -> None:
    assert resolve_needs_review(None, None) is False


def test_explicit_flag_overrides_the_auto_derivation_either_way() -> None:
    # The workflow this exists for: solved with help, but you already
    # understand it well enough not to need a revisit.
    assert resolve_needs_review("solved_with_help", False) is False
    # And the reverse: a status that would not auto-flag, manually flagged.
    assert resolve_needs_review("easy", True) is True


def test_every_auto_review_status_is_a_valid_learning_status() -> None:
    from app.schemas import LEARNING_STATUS_LABELS

    assert set(LEARNING_STATUS_LABELS) >= AUTO_REVIEW_STATUSES
