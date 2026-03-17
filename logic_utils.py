"""
logic_utils.py
--------------
Core game logic for the Game Glitch Investigator guessing game.

All functions in this module are pure Python — no Streamlit dependency —
making them independently testable with pytest.

Functions:
    get_range_for_difficulty(difficulty) -> tuple[int, int]
    parse_guess(raw)                     -> tuple[bool, int | None, str | None]
    check_guess(guess, secret)           -> str
    update_score(current_score, outcome, attempt_number) -> int

Refactored from app.py using Copilot Agent mode (Phase 2).
PEP 8 compliance reviewed and enforced (Challenge 3).
"""


def get_range_for_difficulty(difficulty: str) -> tuple:
    """Return the inclusive (low, high) number range for a given difficulty level.

    The range determines the pool of possible secret numbers. A wider range
    makes the game harder because the player has more values to search through.

    Args:
        difficulty (str): One of "Easy", "Normal", or "Hard".

    Returns:
        tuple[int, int]: A (low, high) pair representing the inclusive range.
            - "Easy"   -> (1, 20)    narrowest range, most forgiving
            - "Normal" -> (1, 100)   default range
            - "Hard"   -> (1, 200)   widest range, fewest attempts allowed
            - unknown  -> (1, 100)   safe fallback to Normal

    Bug fixed:
        Hard mode originally returned (1, 50), which is a *smaller* search
        space than Normal's (1, 100). Despite fewer attempts, the smaller pool
        made Hard genuinely easier. Fixed by expanding Hard to (1, 200).

    Example:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
        >>> get_range_for_difficulty("Hard")
        (1, 200)
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        # FIX: was (1, 50) — easier than Normal. Now genuinely harder.
        return 1, 200
    return 1, 100  # Safe fallback for unknown difficulty strings


def parse_guess(raw: str) -> tuple:
    """Parse a raw string from the user input field into a validated integer guess.

    Handles empty input, None, plain integers, and decimal strings. Decimal
    values are truncated (not rounded) to the nearest integer via int(float()).

    Args:
        raw (str | None): The raw string value from the Streamlit text input.
            May be None, empty, a valid integer string, a decimal string,
            or a non-numeric string.

    Returns:
        tuple: A three-element tuple (ok, guess_int, error_message) where:
            - ok (bool):              True if parsing succeeded, False otherwise.
            - guess_int (int | None): The parsed integer, or None on failure.
            - error_message (str | None): A human-readable error, or None on success.

    Examples:
        >>> parse_guess("42")
        (True, 42, None)
        >>> parse_guess("")
        (False, None, 'Enter a guess.')
        >>> parse_guess("7.9")
        (True, 7, None)
        >>> parse_guess("abc")
        (False, None, 'That is not a number.')
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except (ValueError, TypeError):
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess: int, secret: int) -> str:
    """Compare a player's guess against the secret number and return the outcome.

    Both inputs are defensively cast to int before comparison to guard against
    accidental type mismatches (e.g., if a caller passes a string). This was
    the root cause of Bug 2 in the original app — secret was cast to str on
    even-numbered attempts, making equality checks always fail.

    Args:
        guess (int): The player's guessed number.
        secret (int): The secret number the player is trying to find.

    Returns:
        str: One of three outcome strings:
            - "Win"      if guess == secret
            - "Too High" if guess >  secret  (player should guess lower)
            - "Too Low"  if guess <  secret  (player should guess higher)

    Bug fixed (backwards hints):
        Original code returned "Too High" with the message "Go HIGHER!" when
        the guess was above the secret — the exact wrong direction. The outcome
        label ("Too High") was always correct; the mapped hint message in app.py
        was backwards. Both are now correct.

    Bug fixed (type mismatch):
        Original app.py cast secret to str on even attempts, causing
        int == str comparisons that always returned False. Defensive int()
        casting here ensures correct numeric comparison regardless of caller.

    Examples:
        >>> check_guess(50, 50)
        'Win'
        >>> check_guess(60, 50)
        'Too High'
        >>> check_guess(40, 50)
        'Too Low'
    """
    # Defensive cast: guard against str/float inputs from the caller
    guess = int(guess)
    secret = int(secret)

    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Calculate and return the updated score after a guess attempt.

    Winning rewards the player with points that decrease the longer they take.
    Wrong guesses always deduct 5 points regardless of direction. The minimum
    win bonus is 10 points, ensuring a win is always rewarded even on the
    final allowed attempt.

    Args:
        current_score (int): The player's score before this guess.
        outcome (str): The result of the guess — one of "Win", "Too High",
            or "Too Low" (as returned by check_guess).
        attempt_number (int): The 1-based count of attempts used so far.
            Attempt 1 yields the maximum win bonus (100 points).

    Returns:
        int: The updated score after applying the outcome's point change.

    Scoring rules:
        - Win:     points = max(100 - 10 * (attempt_number - 1), 10)
        - Wrong:   current_score - 5  (same penalty for Too High and Too Low)

    Bug fixed:
        Original code rewarded "Too High" guesses with +5 points on even
        attempts, which perversely incentivised wrong guesses. Now all wrong
        guesses are penalised equally at -5 points.

    Examples:
        >>> update_score(0, "Win", 1)
        100
        >>> update_score(100, "Win", 5)
        160
        >>> update_score(100, "Too High", 3)
        95
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number - 1)
        if points < 10:
            points = 10
        return current_score + points

    # Both "Too High" and "Too Low" deduct 5 points — no asymmetric penalties
    return current_score - 5
