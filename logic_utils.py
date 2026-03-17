def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty.
    
    Bug fixed: Hard mode was 1-50 (easier than Normal's 1-100).
    Hard is now 1-200 to make it genuinely harder.
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 200  # FIX: was 1-50, which was easier than Normal (1-100)
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
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
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess: int, secret: int) -> str:
    """
    Compare guess to secret and return the outcome string.
    Returns: "Win", "Too High", or "Too Low"

    FIXME (Bug 1 — backwards hints):
        Original: guess > secret → "Go HIGHER!" (wrong direction!)
        FIX (Copilot Agent mode): guess > secret → "Too High", hint says "Go LOWER!"

    FIXME (Bug 2 — type mismatch):
        Original: secret was cast to str on even attempts in app.py, so
        check_guess received mismatched types and could never return "Win".
        FIX (Copilot Agent + manual review): defensive int() cast on both
        inputs here, and app.py now always passes secret as int.
    """
    # FIX (Copilot Agent): enforce int types defensively on both sides
    guess = int(guess)
    secret = int(secret)

    if guess == secret:
        return "Win"
    elif guess > secret:
        # FIX (Copilot Agent): was "Too High", "📈 Go HIGHER!" — backwards!
        return "Too High"
    else:
        return "Too Low"


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """
    Update score based on outcome and attempt number.

    Bug fixed: "Too High" guesses were rewarded with +5 points on even
    attempts, which incentivized wrong guesses. Now only winning adds
    points; wrong guesses always subtract.
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number - 1)  # FIX: was attempt_number+1
        if points < 10:
            points = 10
        return current_score + points

    # FIX: wrong guesses always cost 5 points, no rewarding mistakes
    return current_score - 5
