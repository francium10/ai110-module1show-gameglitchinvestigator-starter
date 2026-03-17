import random
import streamlit as st

# Refactored: all game logic moved to logic_utils.py using Copilot Agent mode.
# app.py now handles UI only — no game logic lives here.
# FIX (Copilot Agent): Updated import after Agent moved all four functions out of app.py
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("A number guessing game — fixed and refactored by Francium Lufwendo")


st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# ── Session state initialisation ──────────────────────────────────────────────
if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

# FIXME: Bug 3 — attempts was initialised to 1, silently stealing the player's
# first attempt before they even guessed.
# FIX (identified manually, confirmed with Copilot Inline Chat): changed 1 → 0
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# ── UI ────────────────────────────────────────────────────────────────────────
st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts used:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# ── New game ──────────────────────────────────────────────────────────────────
if new_game:
    st.session_state.attempts = 0          # FIX: reset to 0, not 1
    st.session_state.secret = random.randint(low, high)
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.success("New game started!")
    st.rerun()

# ── Game over guard ───────────────────────────────────────────────────────────
if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won! 🎉 Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

# ── Submit guess ──────────────────────────────────────────────────────────────
if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.error(err)
        st.session_state.attempts -= 1  # don't penalise invalid input
    else:
        st.session_state.history.append(guess_int)

        # FIXME: Bug 2 — original code converted secret to a str on even attempts:
        #   if attempts % 2 == 0: secret = str(st.session_state.secret)
        # This made check_guess compare int vs str — 42 == "42" is always False
        # in Python, making winning on even-numbered turns impossible.
        # FIX (Copilot Agent + manual diff review): always pass secret as int.
        outcome = check_guess(guess_int, st.session_state.secret)

        # Hint messages live in UI layer (app.py), not in logic (logic_utils.py)
        # FIXME: Bug 1 — original hints were backwards ("Go HIGHER!" when too high).
        # FIX (Copilot Agent): swapped messages to match correct directions.
        hint_messages = {
            "Win":      "🎉 Correct!",
            "Too High": "📉 Go LOWER!",
            "Too Low":  "📈 Go HIGHER!",
        }

        if show_hint:
            st.warning(hint_messages[outcome])

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"
            st.error(
                f"Out of attempts! "
                f"The secret was {st.session_state.secret}. "
                f"Score: {st.session_state.score}"
            )

st.divider()
st.caption(
    "Bugs squashed. This one's actually production-ready.CodePath AI110 · Module 1 ✅")
