"""
test_game_logic.py
------------------
Pytest suite for logic_utils.py.

Test groups:
    Starter tests      — provided with the original assignment
    Phase 2 tests      — written to verify each specific bug fix
    Challenge 1 tests  — advanced edge-case suite (negative numbers,
                         extremely large values, whitespace, zero,
                         type coercion, unknown difficulty strings)

How to run:
    pytest tests/test_game_logic.py -v          (from project root)
    pytest test_game_logic.py -v                (from tests/ folder)

Challenge 1 note:
    Copilot was prompted: "Identify three potential edge-case inputs that
    might still break this game and generate pytest cases for each."
    Copilot suggested: negative numbers, extremely large values, and
    whitespace-only strings. We extended the suite further to cover zero,
    unknown difficulty strings, and score floor behaviour.
"""

import pytest
from logic_utils import (
    check_guess,
    parse_guess,
    get_range_for_difficulty,
    update_score,
)


# ── Starter tests (provided) ──────────────────────────────────────────────────

def test_winning_guess():
    """Secret 50, guess 50 -> should be a win."""
    assert check_guess(50, 50) == "Win"


def test_guess_too_high():
    """Secret 50, guess 60 -> should report Too High."""
    assert check_guess(60, 50) == "Too High"


def test_guess_too_low():
    """Secret 50, guess 40 -> should report Too Low."""
    assert check_guess(40, 50) == "Too Low"


# ── Phase 2 tests — bug regression ───────────────────────────────────────────

def test_high_guess_returns_too_high_not_too_low():
    """Bug 1 regression: extreme high guess must return Too High, never Too Low."""
    assert check_guess(99, 1) == "Too High"


def test_low_guess_returns_too_low_not_too_high():
    """Bug 1 regression: extreme low guess must return Too Low, never Too High."""
    assert check_guess(1, 99) == "Too Low"


def test_check_guess_win_with_int_types():
    """Bug 2 regression: int-vs-int comparison must correctly detect a win."""
    assert check_guess(42, 42) == "Win"


def test_check_guess_handles_boundary_values():
    """Boundary: guess equals low boundary value of 1."""
    assert check_guess(1, 1) == "Win"
    assert check_guess(1, 2) == "Too Low"
    assert check_guess(2, 1) == "Too High"


def test_attempts_starts_at_zero():
    """Bug 3 regression: first-attempt win must yield full 100 points."""
    score = update_score(current_score=0, outcome="Win", attempt_number=1)
    assert score == 100


def test_hard_range_is_wider_than_normal():
    """Bug 4 regression: Hard range must be wider than Normal range."""
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert (hard_high - 1) > (normal_high - 1)


def test_easy_range_is_narrower_than_normal():
    """Easy range must be narrower than Normal range."""
    _, easy_high = get_range_for_difficulty("Easy")
    _, normal_high = get_range_for_difficulty("Normal")
    assert easy_high < normal_high


def test_parse_guess_valid_integer():
    ok, value, err = parse_guess("42")
    assert ok is True and value == 42 and err is None


def test_parse_guess_empty_string():
    ok, value, err = parse_guess("")
    assert ok is False and value is None and err is not None


def test_parse_guess_non_numeric():
    ok, value, err = parse_guess("hello")
    assert ok is False and value is None


def test_parse_guess_decimal_rounds_to_int():
    """Decimal input like '7.9' should parse as int 7 without crashing."""
    ok, value, err = parse_guess("7.9")
    assert ok is True and value == 7


# ── Challenge 1: Advanced edge-case tests ─────────────────────────────────────
# Copilot was prompted: "Identify three edge-case inputs that might still break
# this game and generate pytest cases for each."
# Copilot identified: negative numbers, extremely large values, whitespace strings.
# We extended further to cover zero, type coercion, unknown difficulty, score floor.

class TestNegativeNumbers:
    """
    Edge case group 1 — negative number inputs.

    Copilot suggestion: "Negative numbers are valid integers so parse_guess
    will accept them, but they fall outside the game range and check_guess
    should still handle them without crashing."
    Verified: parse_guess accepts negatives (it does not range-validate),
    and check_guess handles them correctly via numeric comparison.
    """

    def test_parse_guess_negative_number_is_accepted(self):
        """parse_guess should accept negative integers without erroring."""
        ok, value, err = parse_guess("-5")
        assert ok is True
        assert value == -5
        assert err is None

    def test_check_guess_negative_guess_vs_positive_secret(self):
        """-5 is always less than any positive secret — must return Too Low."""
        assert check_guess(-5, 50) == "Too Low"

    def test_check_guess_negative_secret(self):
        """check_guess must handle a negative secret without raising an exception."""
        assert check_guess(-10, -10) == "Win"
        assert check_guess(-5, -10) == "Too High"
        assert check_guess(-15, -10) == "Too Low"

    def test_parse_guess_negative_decimal(self):
        """Negative decimals like '-3.7' should parse to -3."""
        ok, value, err = parse_guess("-3.7")
        assert ok is True
        assert value == -3


class TestExtremelyLargeValues:
    """
    Edge case group 2 — extremely large integer inputs.

    Copilot suggestion: "Very large numbers could expose int overflow issues
    in other languages, but Python's arbitrary-precision integers mean this
    should work — worth confirming explicitly."
    Verified: Python handles arbitrarily large ints natively; all three
    functions behave correctly at extreme magnitudes.
    """

    def test_parse_guess_very_large_number(self):
        """A very large number string should parse without overflow."""
        ok, value, err = parse_guess("999999999999")
        assert ok is True
        assert value == 999999999999

    def test_check_guess_large_guess_too_high(self):
        """A huge guess against a normal secret must return Too High."""
        assert check_guess(999999, 50) == "Too High"

    def test_check_guess_large_secret(self):
        """check_guess works correctly when the secret itself is very large."""
        assert check_guess(1000000, 1000000) == "Win"
        assert check_guess(999999, 1000000) == "Too Low"
        assert check_guess(1000001, 1000000) == "Too High"

    def test_update_score_large_attempt_number_hits_floor(self):
        """
        After many wrong attempts, the win bonus floor of 10 points must hold.
        At attempt 20: 100 - 10*(20-1) = 100 - 190 = -90, but floor is 10.
        """
        score = update_score(current_score=0, outcome="Win", attempt_number=20)
        assert score == 10  # floor enforced — never below 10 points for a win


class TestWhitespaceAndBlankInputs:
    """
    Edge case group 3 — whitespace and blank string inputs.

    Copilot suggestion: "A user pressing spacebar and submitting might pass
    a whitespace string like '  ' which is not empty but not numeric either.
    Verify parse_guess handles this gracefully."
    Verified: whitespace-only strings correctly fail as non-numeric.
    """

    def test_parse_guess_whitespace_only(self):
        """A string of spaces is not a valid number — should fail gracefully."""
        ok, value, err = parse_guess("   ")
        assert ok is False
        assert value is None
        assert err == "That is not a number."

    def test_parse_guess_number_with_surrounding_whitespace(self):
        """
        '  42  ' with surrounding spaces — int() in Python strips whitespace,
        so this should parse successfully as 42.
        """
        ok, value, err = parse_guess("  42  ")
        assert ok is True
        assert value == 42

    def test_parse_guess_tab_character(self):
        """A tab character alone is not a valid guess."""
        ok, value, err = parse_guess("\t")
        assert ok is False


class TestZeroAndBoundaryEdgeCases:
    """
    Edge case group 4 — zero and boundary values.

    These were identified manually after reviewing the game's valid range
    (minimum 1 for all difficulties). Zero is technically parseable but
    out of range — the game currently does not range-validate in parse_guess,
    so this group documents the current behaviour explicitly.
    """

    def test_parse_guess_zero_is_accepted(self):
        """Zero parses successfully — range validation is the app's responsibility."""
        ok, value, err = parse_guess("0")
        assert ok is True
        assert value == 0

    def test_check_guess_zero_guess(self):
        """Zero is less than any positive secret number."""
        assert check_guess(0, 50) == "Too Low"

    def test_check_guess_zero_equals_zero(self):
        """Zero vs zero should be a win (edge identity case)."""
        assert check_guess(0, 0) == "Win"


class TestUnknownDifficultyFallback:
    """
    Edge case group 5 — unknown or misspelled difficulty strings.

    If get_range_for_difficulty receives an unexpected value (e.g., a future
    difficulty level or a typo), it should fall back to Normal range safely.
    """

    def test_unknown_difficulty_returns_normal_range(self):
        """Unrecognised difficulty string should return the Normal fallback (1, 100)."""
        assert get_range_for_difficulty("Impossible") == (1, 100)

    def test_empty_difficulty_string_returns_fallback(self):
        """Empty string difficulty should not crash — returns Normal range."""
        assert get_range_for_difficulty("") == (1, 100)

    def test_lowercase_difficulty_does_not_match(self):
        """
        Difficulty matching is case-sensitive. 'easy' != 'Easy'.
        Documents current behaviour — does not raise, falls back to Normal.
        """
        low, high = get_range_for_difficulty("easy")
        assert (low, high) == (1, 100)


class TestScoreSafety:
    """
    Edge case group 6 — score edge cases.

    Verifies the score floor, consistent wrong-guess penalties, and that
    the score can go negative (which is valid — a very bad run should penalise).
    """

    def test_score_can_go_negative(self):
        """Many wrong guesses should push score below zero — this is intentional."""
        score = 0
        for _ in range(25):
            score = update_score(score, "Too High", 1)
        assert score == -125  # 25 * -5

    def test_win_bonus_floor_is_ten(self):
        """Win bonus should never drop below 10 points regardless of attempt count."""
        score = update_score(
            current_score=0, outcome="Win", attempt_number=100)
        assert score == 10

    def test_wrong_guess_penalty_is_symmetric(self):
        """Too High and Too Low should carry identical -5 point penalties."""
        score_high = update_score(50, "Too High", 3)
        score_low = update_score(50, "Too Low", 3)
        assert score_high == score_low == 45
