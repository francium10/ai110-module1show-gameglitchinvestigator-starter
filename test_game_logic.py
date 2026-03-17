"""
test_game_logic.py
------------------
Pytest suite for logic_utils.py.

Starter tests (provided): test_winning_guess, test_guess_too_high, test_guess_too_low
New tests (added in Phase 2): targeting each specific bug that was fixed.

How to run: pytest test_game_logic.py -v
"""

from logic_utils import check_guess, parse_guess, get_range_for_difficulty, update_score


# ── Starter tests (provided) ──────────────────────────────────────────────────

def test_winning_guess():
    """Secret 50, guess 50 → should be a win."""
    result = check_guess(50, 50)
    assert result == "Win"


def test_guess_too_high():
    """Secret 50, guess 60 → should report Too High."""
    result = check_guess(60, 50)
    assert result == "Too High"


def test_guess_too_low():
    """Secret 50, guess 40 → should report Too Low."""
    result = check_guess(40, 50)
    assert result == "Too Low"


# ── New tests — Bug 1: backwards hints ───────────────────────────────────────
# Copilot suggested these tests when prompted:
# "Generate pytest cases that verify check_guess returns the correct
#  direction string when the guess is above or below the secret."

def test_high_guess_returns_too_high_not_too_low():
    """
    Bug 1 regression: original code returned 'Too High' with message 'Go HIGHER!'
    (wrong direction). This test confirms the outcome label itself is correct.
    A guess of 99 against secret 1 must be 'Too High', never 'Too Low'.
    """
    assert check_guess(99, 1) == "Too High"


def test_low_guess_returns_too_low_not_too_high():
    """
    Bug 1 regression: a guess of 1 against secret 99 must be 'Too Low'.
    """
    assert check_guess(1, 99) == "Too Low"


# ── New tests — Bug 2: type-switching secret ──────────────────────────────────
# Copilot initially suggested using unittest.mock to patch session_state,
# which was overly complex. We simplified to just testing check_guess directly
# with int inputs, which is what the fixed code guarantees.

def test_check_guess_win_with_int_types():
    """
    Bug 2 regression: original code cast secret to str on even attempts,
    making 42 == '42' always False. This confirms int-vs-int comparison works.
    """
    assert check_guess(42, 42) == "Win"


def test_check_guess_handles_boundary_values():
    """Edge case: guess equals the low boundary (1)."""
    assert check_guess(1, 1) == "Win"
    assert check_guess(1, 2) == "Too Low"
    assert check_guess(2, 1) == "Too High"


# ── New tests — Bug 3: off-by-one on attempts ────────────────────────────────

def test_attempts_starts_at_zero():
    """
    Bug 3 regression: attempts was initialised to 1, stealing one attempt.
    This test is a documentation test — we can't call st.session_state here,
    but we verify that update_score on attempt 1 gives the max win points (90),
    which only works correctly if attempt counting starts from 1 (first real guess).
    """
    score = update_score(current_score=0, outcome="Win", attempt_number=1)
    assert score == 100  # 100 - 10*(1-1) = 100 — first-guess win gets full points


# ── New tests — Bug 4: Hard difficulty range ──────────────────────────────────

def test_hard_range_is_wider_than_normal():
    """
    Bug 4 regression: Hard was 1-50, which is easier than Normal's 1-100.
    Hard must now have a larger range than Normal.
    """
    normal_low, normal_high = get_range_for_difficulty("Normal")
    hard_low, hard_high = get_range_for_difficulty("Hard")
    normal_range = normal_high - normal_low
    hard_range = hard_high - hard_low
    assert hard_range > normal_range, (
        f"Hard range ({hard_range}) should be wider than Normal range ({normal_range})"
    )


def test_easy_range_is_narrower_than_normal():
    """Easy should always be easier (smaller range) than Normal."""
    _, easy_high = get_range_for_difficulty("Easy")
    _, normal_high = get_range_for_difficulty("Normal")
    assert easy_high < normal_high


# ── New tests — parse_guess edge cases ───────────────────────────────────────
# Copilot suggested these when we asked: "What edge cases could break parse_guess?"

def test_parse_guess_valid_integer():
    ok, value, err = parse_guess("42")
    assert ok is True
    assert value == 42
    assert err is None


def test_parse_guess_empty_string():
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None
    assert err is not None


def test_parse_guess_non_numeric():
    ok, value, err = parse_guess("hello")
    assert ok is False
    assert value is None


def test_parse_guess_decimal_rounds_to_int():
    """Floats like '7.9' should parse as int 7 without crashing."""
    ok, value, err = parse_guess("7.9")
    assert ok is True
    assert value == 7
