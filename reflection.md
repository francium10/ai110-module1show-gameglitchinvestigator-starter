# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

When I first ran the game, it looked functional on the surface — there was a text input, a Submit button, difficulty settings in the sidebar, and a Developer Debug Info panel showing the secret number. However, it quickly became clear that the game was impossible to win fairly. I found four concrete bugs by reading the code carefully.

**Bug 1 — The hints were completely backwards (logic bug in `check_guess`)**
- **Expected:** If my guess was too high (e.g., I guessed 80 and the secret was 50), the hint should say "Go LOWER."
- **What actually happened:** The code said `if guess > secret: return "Too High", "📈 Go HIGHER!"` — meaning when I guessed *above* the secret, it told me to go even *higher*. The hint was the exact opposite of correct, actively misleading the player away from the answer.

**Bug 2 — The secret number silently changed type every other attempt (type-switching bug)**
- **Expected:** The secret number should stay a consistent integer throughout the entire game so that comparisons work reliably.
- **What actually happened:** On even-numbered attempts, the code converted the secret to a *string* (`secret = str(st.session_state.secret)`). This meant `check_guess` was comparing an `int` guess against a `str` secret on those turns, making a correct guess impossible to detect and scrambling the "Too High" / "Too Low" logic through string comparison instead of numeric comparison.

**Bug 3 — The attempts counter started at 1 instead of 0 (off-by-one bug)**
- **Expected:** At the start of a fresh game, the player should have their full number of attempts available (e.g., 8 for Normal difficulty). The counter should start at 0 and increment after each guess.
- **What actually happened:** `st.session_state.attempts` was initialized to `1`, so the player silently lost one attempt before even making a single guess. The "Attempts left" display showed one fewer than it should have right from the start.

**Bug 4 — The "Hard" difficulty range was easier than "Normal" (difficulty misconfiguration bug)**
- **Expected:** Hard mode should be harder than Normal — a wider range with fewer attempts would make sense.
- **What actually happened:** Normal mode used a range of 1–100, but Hard mode used a range of only 1–50, which is *half* the range of Normal. Despite being called "Hard" and giving the player fewer attempts (5 vs 8), the smaller number pool actually made individual guesses more likely to be close. The difficulty label was misleading and the design was logically inconsistent.

---

## 2. How did you use AI as a teammate?

I used Claude (via the Claude.ai chat interface) and GitHub Copilot (Inline Chat and Agent mode in VS Code) as my primary AI tools on this project.

**Correct AI suggestion — refactoring logic into `logic_utils.py`:**
I used Copilot Agent mode with the prompt: *"Move the `check_guess` function to `logic_utils.py`, fix the high/low bug, and update the import in `app.py`."* The Agent correctly identified all four functions in `app.py` that belonged in `logic_utils.py`, moved them, updated the import block at the top of `app.py`, and fixed the backwards hint logic in `check_guess`. I verified this by reviewing the diff the Agent produced line-by-line, then running `pytest` — all three starter tests passed immediately, confirming the logic was correct.

**Incorrect/misleading AI suggestion — testing the type-switching bug:**
When I asked Copilot to generate a test for Bug 2 (the type-switching secret), it suggested using `unittest.mock` to patch `st.session_state` directly inside the test file. This was misleading — importing Streamlit in a pure pytest context would require the full Streamlit runtime and would overcomplicate a simple unit test. I verified it was wrong by trying to run the suggested test, which threw an import error. I simplified the approach: since `check_guess` in `logic_utils.py` now always enforces `int()` on both inputs defensively, I only needed to test that `check_guess(42, 42) == "Win"` — no mocking required at all.

---

## 3. Debugging and testing your fixes

I decided a bug was truly fixed only when two things were both true: the relevant `pytest` test passed, and I could manually reproduce the scenario in the running Streamlit app and see the correct behaviour.

**Test that revealed the most about the code — `test_high_guess_returns_too_high_not_too_low`:**
This test called `check_guess(99, 1)` and asserted the result was `"Too High"`. Before the fix, the original `check_guess` in `app.py` would have returned `"Too High"` with the message `"📈 Go HIGHER!"` — the outcome label was correct but the *hint message was backwards*, actively sending the player in the wrong direction. Writing this test forced me to notice that the bug was actually in two places: the string returned by `check_guess` was fine, but the hint message dictionary in `app.py` had the directions swapped. Separating logic from UI (refactoring into `logic_utils.py`) made this split visible.

**How AI helped with tests:**
Copilot helped me think about `parse_guess` edge cases I hadn't considered — specifically decimal inputs like `"7.9"` and `None` vs empty string. I asked: *"What edge cases could break parse_guess?"* and used its suggestions as a checklist, then wrote the actual test code myself so I understood each assertion. The `test_parse_guess_decimal_rounds_to_int` test came directly from that conversation and passed on the first run.

---

## 4. What did you learn about Streamlit and state?

The secret number kept changing in the original app because of how Streamlit works under the hood. Every time the user interacts with the app — clicking a button, typing in a field, changing a dropdown — Streamlit reruns the entire Python script from the very top. That means any variable assigned at the top level, like `secret = random.randint(1, 100)`, gets reassigned to a brand-new random number on every single interaction. The original code did use `st.session_state` to store the secret, but the guard `if "secret" not in st.session_state` only runs once per session — so the secret was stable within a difficulty level but would silently regenerate if anything triggered a full state reset.

If I were explaining Streamlit reruns to a friend who had never seen it: imagine your entire Python script is like a recipe card. Every time you touch anything on the screen — press a button, type a letter — someone grabs that recipe card, throws it away, and reads it again from the very first line. Variables you set in the middle just disappear unless you store them somewhere that survives the re-read. That "somewhere" is `st.session_state`, which is like a sticky note attached to your browser tab — it persists across reruns as long as the tab is open.

The fix that finally gave the game a stable secret number was ensuring all session state — secret, attempts, score, status, and history — resets together *explicitly* only when the player clicks "New Game," and nowhere else. The key insight was that `st.session_state` keys initialized with `if "key" not in st.session_state` are only set once per session, so as long as we stopped regenerating the secret on difficulty change and only reset on "New Game," the secret stayed stable for the entire game.

---

## 5. Looking ahead: your developer habits

**One habit I want to carry forward — mark the crime scene before asking AI for help.**
Placing `# FIXME: Logic breaks here` comments at the exact line I suspected, before opening Copilot, made my prompts dramatically more specific and useful. Instead of asking "why is my game broken," I could ask "explain line 158 — why does converting secret to a string on even attempts make winning impossible." The more precisely I could point the AI at the problem, the more actionable its response was. I will use this "annotate first, then ask" habit in every future debugging session, including in my RegComplyAI backend work where bugs are often buried in FastAPI middleware or LangChain chain logic.

**One thing I would do differently — manually verify every expected value in AI-generated tests.**
When Copilot generated test cases, I initially accepted them without checking the expected values myself. One test asserted `score == 90` when the actual math gives `100` — a wrong assertion that would have silently passed a broken function rather than caught it. Next time I will trace through the logic by hand for every single `assert` value before committing a generated test. The AI is excellent at generating test *structure*, but the expected values need human verification every time.

**How this project changed the way I think about AI-generated code:**
Before this project, I assumed AI-generated code was either obviously correct or obviously broken. What this showed me is the most dangerous category in between: code that *looks* correct, runs without errors, and fails only under specific runtime conditions — like a type mismatch that silently corrupts results only on even-numbered attempts. I will treat AI-generated code the way I would treat a pull request from a smart but unaccountable developer: read every line, test the edges, and trust the tests more than the explanation.
