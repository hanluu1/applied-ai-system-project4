# Model Card: AI-Enhanced Number Guesser

## Base Project

This project extends the original **Game Glitch Investigator: The Impossible Guesser** Streamlit app. The base project focused on fixing a resetting secret number, swapped hint directions, and attempt/state handling bugs. This version adds an AI advisor, a reliability/evaluation layer, a full end-to-end demo script, and expanded documentation.

## Model and System Role

This repository does not train a custom ML model. Instead, it uses **Google Gemini** as an AI advisor to suggest the next number guess from the current game state. The AI is used as a tool-calling agent that performs two steps:

1. Analyze the valid search range from guess history.
2. Suggest the next guess using binary search.

The game logic itself remains deterministic in `logic_utils.py`.

## Intended Use

- Help a player choose a better next guess.
- Demonstrate a structured AI workflow inside a Streamlit app.
- Show how validation and guardrails can reduce AI errors.
- Support class demonstration and debugging exercises.

## Inputs

- Selected difficulty level: Easy, Normal, or Hard.
- Guess history: prior guesses and outcomes.
- Remaining attempts.
- User-entered guess text.

## Outputs

- Next-guess suggestion from Gemini.
- Short explanation of why the guess is recommended.
- Narrowed search bounds.
- Validation messages when inputs or AI suggestions are invalid.

## Performance and Testing Results

The system was verified with:
- `pytest tests/ -v` resulting in **13 passed tests**.
- `python3 demo.py` resulting in a complete end-to-end demonstration with 5 scenarios.
- Manual gameplay checks in Streamlit for multiple guesses, win/loss states, and AI suggestions.

Testing confirmed that:
- Hint directions are correct.
- Attempt counting works as intended.
- New-game resets clear the prior session state.
- The AI suggestion workflow stays within the valid number range.
- Guardrails catch invalid guesses and inconsistent game states.

## Biases and Limitations

This system is not biased in a demographic sense, but it does have predictable **behavioral biases**:

- **Optimization bias**: The AI prefers binary search and may suggest optimal but not beginner-friendly moves.
- **Overconfidence bias**: The model can sound certain even when the API output is incomplete or malformed.
- **API dependency bias**: Suggestions depend on external Gemini availability and quota.
- **Evaluation bias**: The guardrails mostly test known cases, so unfamiliar failure modes may still slip through.

Additional limitations:
- No persistent user accounts or database storage.
- No adaptive difficulty based on player skill.
- No offline fallback for AI suggestions beyond a simple midpoint fallback.

## Safety and Guardrails

The project includes reliability checks to reduce bad outputs:
- Input validation for user guesses and difficulty.
- Output validation for AI suggestions.
- Game state consistency checks.
- Hint verification against the actual secret number.
- Score logic validation through automated tests.

## AI Collaboration Summary

AI was used in three main ways:
- To help design the architecture of the AI advisor.
- To debug Streamlit state and hint-direction issues.
- To generate initial test and documentation drafts that were then manually verified.

## Helpful AI Suggestion

A useful AI suggestion was to use **tool calling** instead of free-form text for the advisor. That made the AI output structured and easier to validate. I verified the improvement by running the demo script and checking that the AI returned a valid guess plus reasoning in the expected fields.

## Flawed AI Suggestion

A flawed AI suggestion was to add **exponential penalties** for repeated wrong guesses. That would have changed the game balance and broken the simpler scoring model used by the base project. I rejected it after comparing it against the existing scoring tests and manual gameplay behavior.

## Reflection on Testing

Testing was the main way I decided whether a change was correct. I used:
- Manual gameplay in Streamlit.
- `pytest` for logic-level correctness.
- The `demo.py` end-to-end script for multi-scenario verification.
- The evaluator module to test guardrails and state consistency.

## Future Improvements

- Add persistent storage for user progress.
- Add adaptive difficulty scaling.
- Add cached or offline fallback AI suggestions.
- Add richer visualizations for guess history.
- Add more formal evaluation of AI suggestion quality across many games.

## Summary

This project uses Gemini as an assistive reasoning layer, not as the source of game truth. The deterministic game logic, evaluator checks, and tests are the core reliability mechanisms. The AI is helpful, but the system is only trustworthy because the code validates its output before displaying it to the player.
