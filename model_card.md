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

## AI Collaboration Summary

AI was used in four main phases of the project:

1. **Bug fixing**: AI helped identify the Streamlit session-state ordering issue that caused the attempt counter bug.
2. **Feature design**: AI helped shape the multi-step advisor pattern and the move to tool calling for binary search suggestions.
3. **Reliability work**: AI generated guardrail and validation ideas, while the final checks were verified manually and through tests.
4. **Documentation and demo support**: AI helped outline the README and demo structure, which were then edited and validated by hand.

## Helpful AI Suggestion

One useful suggestion was to use **tool calling** instead of free-form text for the advisor. That made the AI output structured and easier to validate.

Why it helped:
- The AI can directly call `analyze_search_space` and `suggest_guess`.
- The app can verify the returned fields without parsing prose.
- The demo confirmed the tool-based workflow returned valid guesses and reasoning.

## Flawed AI Suggestion

One flawed suggestion was to add **exponential penalties** for repeated wrong guesses.

Why it was rejected:
- It would have changed the intended game balance.
- The base project uses a simple and predictable `-5` penalty model.
- Existing tests and manual gameplay showed the exponential version was too aggressive.

## What Worked Well

- AI was strong at pattern recognition and quickly pointed to likely root causes.
- AI was useful for boilerplate such as test cases, guardrail scaffolding, and documentation drafts.
- The structured Gemini tool-calling approach made the advisor much more reliable than parsing free-form text.

## What Did Not Work Well

- AI sometimes missed project-specific context, especially around game design choices.
- Some AI-generated ideas were overengineered for a simple guessing game.
- AI output was not trustworthy on its own, so human review and tests were still required.

## Best Practices Learned

- Use AI for exploration, not authority.
- Verify AI suggestions with tests or a demo before keeping them.
- Keep core logic deterministic and use AI as an assistive layer.
- Prefer structured outputs and guardrails over parsing plain text.

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
- AI suggestions depend on external Gemini quota and availability.

## Reflection on Testing

Testing was the main way changes were validated. The project used:
- Manual gameplay in Streamlit.
- `pytest` for core logic checks.
- `python3 demo.py` for end-to-end scenario coverage.
- The evaluator module for input, output, and state consistency checks.

This matters because the AI advisor is only useful if the deterministic game logic and validation layers keep the system correct.

## Safety and Guardrails

The project includes reliability checks to reduce bad outputs:
- Input validation for user guesses and difficulty.
- Output validation for AI suggestions.
- Game state consistency checks.
- Hint verification against the actual secret number.
- Score logic validation through automated tests.

## Future Improvements

- Add persistent storage for user progress.
- Add adaptive difficulty scaling.
- Add cached or offline fallback AI suggestions.
- Add richer visualizations for guess history.
- Add more formal evaluation of AI suggestion quality across many games.

## Project Impact

The main result is a small but reliable example of AI integration in a real app. The system demonstrates how to combine Gemini, deterministic game logic, guardrails, tests, and a demo script without letting the model control game truth.

## Summary

This project uses Gemini as an assistive reasoning layer, not as the source of game truth. The deterministic game logic, evaluator checks, and tests are the core reliability mechanisms. The AI is helpful, but the system is only trustworthy because the code validates its output before displaying it to the player.
