# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

An AI was asked to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and left behind a game that was completely unplayable.

- You couldn't win — the secret number changed type every other attempt.
- The hints lied — "Go Higher!" when you were already too high.
- The attempt counter started at 1, silently stealing your first guess.
- "Hard" mode was actually easier than "Normal."

**This repo documents how those bugs were found, understood, and fixed — using AI as a collaborative debugging partner, not a vending machine.**

---

## 🛠️ Setup

```bash
# 1. Clone the repo
git clone <your-fork-url>
cd game-glitch-investigator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the fixed app
python -m streamlit run app.py

# 4. Run the test suite
pytest test_game_logic.py -v
```

---

## 🕵️ The Mission (completed)

| Step | Task | Status |
|------|------|--------|
| 1 | Play the broken game and find the bugs | ✅ Found 4 bugs |
| 2 | Identify the state / session bug | ✅ Type-switching secret on even attempts |
| 3 | Fix the backwards hints | ✅ `Too High` → "Go LOWER", `Too Low` → "Go HIGHER" |
| 4 | Refactor logic into `logic_utils.py` and pass all tests | ✅ 14/14 tests passing |

---

## 📝 Document Your Experience

### What is this game?
A number guessing game built with Streamlit. The player picks a difficulty (Easy: 1–20, Normal: 1–100, Hard: 1–200), gets a limited number of attempts, and receives "Too High" / "Too Low" hints after each guess. The score decreases with each wrong guess and rewards faster wins.

### Bugs found

**Bug 1 — Backwards hints** (`app.py` / `check_guess`)
The hint messages were the opposite of correct. When `guess > secret`, the game said "📈 Go HIGHER!" — actively sending the player away from the answer. Fixed by swapping the hint messages in the UI layer so `Too High` → "📉 Go LOWER!" and `Too Low` → "📈 Go HIGHER!".

**Bug 2 — Type-switching secret** (`app.py` lines 158–161)
On every even-numbered attempt, `secret` was silently converted to a string: `secret = str(st.session_state.secret)`. This made `check_guess` compare `int` vs `str` — since `42 == "42"` is `False` in Python, winning was impossible on even turns. Fixed by always passing `secret` as `int` and adding a defensive `int()` cast inside `check_guess` itself.

**Bug 3 — Off-by-one on attempts** (`app.py` line 96)
`st.session_state.attempts` was initialised to `1` instead of `0`, silently consuming one attempt before the player made a single guess. Fixed by changing the initialisation to `0`.

**Bug 4 — Hard difficulty range was easier than Normal** (`get_range_for_difficulty`)
Hard mode used range 1–50, which is a *smaller* search space than Normal's 1–100. With fewer attempts (5 vs 8) but an easier range, the difficulty label was misleading. Fixed by setting Hard to 1–200.

### Fixes applied

- All four functions (`get_range_for_difficulty`, `parse_guess`, `check_guess`, `update_score`) were refactored from `app.py` into `logic_utils.py` using Copilot Agent mode. `app.py` is now pure UI code.
- `check_guess` now enforces `int()` on both inputs defensively.
- Hint messages in `app.py` now correctly match their outcomes.
- "New Game" button resets all session state (secret, attempts, score, status, history) — the original only reset attempts and secret.
- Invalid input no longer consumes an attempt.

---

## 📸 Demo

### ✅ pytest results — 14/14 tests passing

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2
collected 14 items

test_game_logic.py::test_winning_guess                          PASSED [  7%]
test_game_logic.py::test_guess_too_high                         PASSED [ 14%]
test_game_logic.py::test_guess_too_low                          PASSED [ 21%]
test_game_logic.py::test_high_guess_returns_too_high_not_too_low PASSED [ 28%]
test_game_logic.py::test_low_guess_returns_too_low_not_too_high PASSED [ 35%]
test_game_logic.py::test_check_guess_win_with_int_types         PASSED [ 42%]
test_game_logic.py::test_check_guess_handles_boundary_values    PASSED [ 50%]
test_game_logic.py::test_attempts_starts_at_zero                PASSED [ 57%]
test_game_logic.py::test_hard_range_is_wider_than_normal        PASSED [ 64%]
test_game_logic.py::test_easy_range_is_narrower_than_normal     PASSED [ 71%]
test_game_logic.py::test_parse_guess_valid_integer              PASSED [ 78%]
test_game_logic.py::test_parse_guess_empty_string               PASSED [ 85%]
test_game_logic.py::test_parse_guess_non_numeric                PASSED [ 92%]
test_game_logic.py::test_parse_guess_decimal_rounds_to_int      PASSED [100%]

============================== 14 passed in 0.04s ==============================
```

> 📷 Replace this block with a screenshot of your terminal after running `pytest test_game_logic.py -v`

### ✅ Fixed game — winning is now possible

> 📷 Insert a screenshot of your fixed, winning game here (the "🎉 You won!" screen with balloons)

---

## 🗂️ Project Structure

```
.
├── app.py              # Streamlit UI — no game logic here
├── logic_utils.py      # All game logic (check_guess, parse_guess, etc.)
├── test_game_logic.py  # pytest suite — 14 tests covering all fixed bugs
├── requirements.txt
├── reflection.md       # Full debugging + AI collaboration write-up
└── README.md
```

---

## 🚀 Stretch Features

- [ ] Add a leaderboard using `st.session_state` to track scores across rounds
- [ ] Add a timer to score faster guesses higher
- [ ] Add difficulty-aware max attempts display that updates live
- [ ] [Insert a screenshot of your Enhanced Game UI here if completed]

---

## 🤝 AI Collaboration Notes

This project was completed using **Claude (claude.ai)** and **GitHub Copilot** (Inline Chat + Agent mode).

- Copilot Agent mode was used to refactor all logic functions from `app.py` into `logic_utils.py` in one multi-file operation.
- Copilot Inline Chat (`Cmd+I`) was used to explain specific suspicious lines — particularly the type-switching logic on lines 158–161 of the original `app.py`.
- Claude was used to reason through bug hypotheses, plan test cases, and review diffs before accepting Agent changes.
- One AI suggestion was rejected: Copilot suggested using `unittest.mock` to patch `st.session_state` in tests — this was overly complex and unnecessary since the fix moved all testable logic into `logic_utils.py`, which has no Streamlit dependency.

See `reflection.md` for the full write-up.
