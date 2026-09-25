import pytest

from ui.game_logic import revenue_direction, title_matches


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [(100, 200, "higher"), (200, 100, "lower")],
)
def test_revenue_direction(first, second, expected):
    assert revenue_direction(first, second) == expected


def test_revenue_direction_rejects_tie():
    with pytest.raises(ValueError):
        revenue_direction(100, 100)


@pytest.mark.parametrize(
    ("guess", "title", "expected"),
    [
        ("  THE   MATRIX ", "The Matrix", True),
        ("", "The Matrix", False),
        ("Matrix", "The Matrix", False),
    ],
)
def test_title_matches(guess, title, expected):
    assert title_matches(guess, title) is expected
