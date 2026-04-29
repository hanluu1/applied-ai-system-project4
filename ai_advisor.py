import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def get_ai_suggestion(low: int, high: int, history: list, attempts_left: int) -> dict:
    """
    Multi-step agent: narrows the valid search range, then suggests the optimal next guess.

    history: list of {"guess": int, "outcome": "Too High" | "Too Low"}
    Returns: {"suggested_guess": int, "explanation": str,
              "lower_bound": int, "upper_bound": int, "reasoning": str}
    On error: {"error": str}
    """
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        return {"error": "GOOGLE_API_KEY environment variable not set."}

    client = genai.Client(api_key=api_key)

    # Use lists so the closures can write back results
    analysis_result = [None]
    suggestion_result = [None]

    # --- Tool 1: analyze the valid search space ---
    def analyze_search_space(lower_bound: int, upper_bound: int, reasoning: str) -> str:
        """Analyze the current valid search bounds based on guess history.

        Args:
            lower_bound: Tightest lower bound — secret is at or above this value.
            upper_bound: Tightest upper bound — secret is at or below this value.
            reasoning: Step-by-step reasoning for how these bounds were derived.

        Returns:
            Confirmation that the analysis was recorded.
        """
        analysis_result[0] = {
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "reasoning": reasoning,
        }
        return "Analysis recorded."

    # --- Tool 2: commit to a guess ---
    def suggest_guess(guess: int, explanation: str) -> str:
        """Submit the recommended next guess for the player.

        Args:
            guess: The optimal next guess.
            explanation: Brief, player-friendly explanation of why this is the best guess.

        Returns:
            Confirmation that the suggestion was recorded.
        """
        suggestion_result[0] = {"guess": guess, "explanation": explanation}
        return "Suggestion recorded."

    history_text = (
        "\n".join(f"  - Guessed {h['guess']}: {h['outcome']}" for h in history)
        if history
        else "  (no guesses yet)"
    )

    prompt = (
        f"Number guessing game state:\n"
        f"- Secret number range: {low} to {high}\n"
        f"- Attempts remaining: {attempts_left}\n"
        f"- Guess history:\n{history_text}\n\n"
        f"Step 1: Call analyze_search_space to determine the tightest valid bounds "
        f"from the guess history.\n"
        f"Step 2: Call suggest_guess with the binary search midpoint of the valid range."
    )

    try:
        client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[analyze_search_space, suggest_guess],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=False
                ),
                system_instruction=(
                    "You are an expert number-guessing strategist. "
                    "Always use binary search to find the secret number in the fewest guesses. "
                    "Be concise and helpful to the player."
                ),
            ),
        )
    except Exception as e:
        msg = str(e)
        if "api key" in msg.lower() or "api_key" in msg.lower() or "invalid" in msg.lower():
            return {"error": "Invalid GOOGLE_API_KEY."}
        return {"error": f"Gemini error: {msg}"}

    if suggestion_result[0] is None:
        mid = (low + high) // 2
        return {
            "suggested_guess": mid,
            "explanation": "Binary search midpoint (AI did not complete the workflow).",
            "lower_bound": low,
            "upper_bound": high,
            "reasoning": "Fallback.",
        }

    return {
        "suggested_guess": suggestion_result[0]["guess"],
        "explanation": suggestion_result[0]["explanation"],
        "lower_bound": analysis_result[0]["lower_bound"] if analysis_result[0] else low,
        "upper_bound": analysis_result[0]["upper_bound"] if analysis_result[0] else high,
        "reasoning": analysis_result[0]["reasoning"] if analysis_result[0] else "",
    }
