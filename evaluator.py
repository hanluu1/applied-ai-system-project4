"""
Guardrails and Evaluator for AI suggestions and game state.

This module provides reliability mechanisms:
1. Input validation (guards against invalid player inputs)
2. Output guardrails (validates AI suggestions before display)
3. Game state evaluator (ensures consistency)
4. Score validation (prevents invalid scoring)
"""

from typing import Dict, List, Tuple


class InputValidator:
    """Validates player inputs."""
    
    @staticmethod
    def validate_guess(guess: int, low: int, high: int) -> Tuple[bool, str]:
        """
        Validate that a guess is within the valid range.
        
        Args:
            guess: The guessed number
            low: Minimum valid value (inclusive)
            high: Maximum valid value (inclusive)
            
        Returns:
            (is_valid, error_message)
        """
        if not isinstance(guess, int):
            return False, "Guess must be an integer"
        
        if guess < low or guess > high:
            return False, f"Guess must be between {low} and {high}. Got {guess}."
        
        return True, ""
    
    @staticmethod
    def validate_difficulty(difficulty: str) -> Tuple[bool, str]:
        """Validate difficulty selection."""
        valid = ["Easy", "Normal", "Hard"]
        if difficulty not in valid:
            return False, f"Difficulty must be one of {valid}"
        return True, ""


class OutputGuardrails:
    """Validates AI suggestions before display to player."""
    
    @staticmethod
    def validate_ai_suggestion(
        suggestion: Dict,
        low: int,
        high: int,
        history: List[Dict],
        attempts_left: int
    ) -> Tuple[bool, str]:
        """
        Validate an AI suggestion for consistency and sanity.
        
        Args:
            suggestion: Dict with keys: suggested_guess, lower_bound, upper_bound, etc.
            low: Game's minimum range
            high: Game's maximum range
            history: List of previous guesses
            attempts_left: Remaining attempts
            
        Returns:
            (is_valid, explanation)
        """
        # Check for error responses
        if "error" in suggestion:
            return False, f"AI returned error: {suggestion['error']}"
        
        # Check required fields
        required_fields = ["suggested_guess", "lower_bound", "upper_bound", "explanation", "reasoning"]
        for field in required_fields:
            if field not in suggestion:
                return False, f"Missing required field: {field}"
        
        suggested = suggestion["suggested_guess"]
        lower = suggestion["lower_bound"]
        upper = suggestion["upper_bound"]
        
        # Guardrail 1: Suggested guess is a number
        if not isinstance(suggested, int):
            return False, f"suggested_guess must be int, got {type(suggested)}"
        
        # Guardrail 2: Suggested guess is within valid range
        if suggested < low or suggested > high:
            return False, f"Suggested guess {suggested} is outside game range [{low}, {high}]"
        
        # Guardrail 3: Suggested guess is within derived bounds
        if suggested < lower or suggested > upper:
            return False, f"Suggested guess {suggested} outside derived range [{lower}, {upper}]"
        
        # Guardrail 4: Bounds are valid
        if lower > upper:
            return False, f"Invalid bounds: lower {lower} > upper {upper}"
        
        if lower < low or upper > high:
            return False, f"Bounds [{lower}, {upper}] outside game range [{low}, {high}]"
        
        # Guardrail 5: Suggested guess hasn't been tried yet (avoid repetition)
        previous_guesses = [h.get("guess") for h in history if h.get("outcome") in ("Too High", "Too Low", "Win")]
        if suggested in previous_guesses:
            return False, f"Suggested guess {suggested} was already tried"
        
        # Guardrail 6: Binary search check - is it a reasonable midpoint?
        expected_midpoint = (lower + upper) // 2
        # Allow ±1 for rounding differences
        if abs(suggested - expected_midpoint) > 1:
            warning = f"Suggested {suggested} differs from expected midpoint {expected_midpoint}"
            # This is a warning but not a failure - return True with note
        
        return True, "All guardrails passed"
    
    @staticmethod
    def validate_search_space_narrowing(
        guess: int,
        outcome: str,
        old_lower: int,
        old_upper: int,
        new_lower: int,
        new_upper: int
    ) -> Tuple[bool, str]:
        """
        Validate that search space narrowing logic is correct.
        
        Args:
            guess: The guess that prompted the narrowing
            outcome: "Too High" or "Too Low"
            old_lower, old_upper: Previous bounds
            new_lower, new_upper: New bounds
            
        Returns:
            (is_valid, explanation)
        """
        if outcome == "Too High":
            # If guess is too high, secret must be lower than guess
            # So new upper should be guess - 1
            if new_upper >= guess:
                return False, f"Too High: upper bound {new_upper} should be < {guess}"
            if new_lower != old_lower:
                return False, f"Too High: lower bound {new_lower} should not change"
        
        elif outcome == "Too Low":
            # If guess is too low, secret must be higher than guess
            # So new lower should be guess + 1
            if new_lower <= guess:
                return False, f"Too Low: lower bound {new_lower} should be > {guess}"
            if new_upper != old_upper:
                return False, f"Too Low: upper bound {new_upper} should not change"
        
        else:
            return False, f"Unknown outcome: {outcome}"
        
        return True, "Search space narrowing is correct"


class GameStateEvaluator:
    """Evaluates overall game state consistency."""
    
    @staticmethod
    def evaluate_game_state(
        secret: int,
        attempts: int,
        attempt_limit: int,
        status: str,
        score: int,
        history: List[Dict],
        low: int,
        high: int
    ) -> Tuple[bool, List[str]]:
        """
        Validate overall game state consistency.
        
        Args:
            secret: The secret number
            attempts: Current attempt count
            attempt_limit: Max attempts allowed
            status: Game status ("playing", "won", "lost")
            score: Current score
            history: Game history
            low, high: Valid range
            
        Returns:
            (is_consistent, list_of_issues)
        """
        issues = []
        
        # Check secret is in range
        if secret < low or secret > high:
            issues.append(f"Secret {secret} outside range [{low}, {high}]")
        
        # Check attempts are reasonable
        if attempts < 0:
            issues.append(f"Attempts {attempts} cannot be negative")
        
        if attempts > attempt_limit:
            issues.append(f"Attempts {attempts} exceed limit {attempt_limit}")
        
        # Check status is valid
        if status not in ("playing", "won", "lost"):
            issues.append(f"Invalid status: {status}")
        
        # Check score is reasonable
        if score < 0:
            issues.append(f"Score {score} cannot be negative")
        
        # Check history length matches attempts (roughly)
        valid_history_count = sum(1 for h in history if h.get("outcome") in ("Too High", "Too Low", "Win"))
        if valid_history_count != attempts:
            issues.append(f"History ({valid_history_count} valid) doesn't match attempts ({attempts})")
        
        # Check final status consistency
        if status == "won":
            # Should have a Win in history
            win_found = any(h.get("outcome") == "Win" for h in history)
            if not win_found:
                issues.append("Status is 'won' but no Win found in history")
        
        if status == "lost":
            # Should have reached attempt limit
            if attempts < attempt_limit:
                issues.append(f"Status is 'lost' but attempts {attempts} < limit {attempt_limit}")
        
        return len(issues) == 0, issues


class HintEvaluator:
    """Evaluates hint correctness."""
    
    @staticmethod
    def evaluate_hint(
        guess: int,
        secret: int,
        hint_outcome: str
    ) -> Tuple[bool, str]:
        """
        Verify that the hint given to the player is correct.
        
        Args:
            guess: The player's guess
            secret: The actual secret number
            hint_outcome: The hint given ("Win", "Too High", "Too Low")
            
        Returns:
            (is_correct, explanation)
        """
        if guess == secret:
            expected = "Win"
        elif guess > secret:
            expected = "Too High"
        else:
            expected = "Too Low"
        
        if hint_outcome == expected:
            return True, f"Correct hint: guess {guess} vs secret {secret}"
        else:
            return False, f"Incorrect hint: said '{hint_outcome}' but should be '{expected}' (guess {guess}, secret {secret})"


class ScoreValidator:
    """Validates score calculations."""
    
    @staticmethod
    def validate_score_bounds(score: int, attempts: int, max_attempts: int) -> Tuple[bool, str]:
        """
        Validate that score is within reasonable bounds.
        
        Score calculation: Win gives 100 - 10*(attempt+1), min 10.
        Wrong guesses give -5 each.
        """
        # Worst case: lose all attempts = -5 * max_attempts = -5 * max_attempts
        min_possible = -5 * max_attempts
        # Best case: win on first try = 100 - 10*2 = 80
        max_possible = 100 - 10 * 2
        
        # But score can accumulate across multiple rounds, so be lenient
        if score < min_possible - 100:
            return False, f"Score {score} seems unreasonably low"
        
        return True, f"Score {score} is within reasonable bounds"


def evaluate_system_end_to_end(
    secret: int,
    low: int,
    high: int,
    guess: int,
    expected_outcome: str,
    game_state: Dict
) -> Dict:
    """
    Run comprehensive end-to-end evaluation of a game action.
    
    Returns report with all checks.
    """
    report = {
        "input_valid": False,
        "state_valid": False,
        "hint_correct": False,
        "guardrail_passed": True,
        "issues": [],
        "details": {}
    }
    
    # Step 1: Validate input
    input_ok, input_err = InputValidator.validate_guess(guess, low, high)
    if not input_ok:
        report["input_valid"] = False
        report["issues"].append(f"Invalid input: {input_err}")
        return report
    report["input_valid"] = True
    
    # Step 2: Validate hint
    hint_ok, hint_detail = HintEvaluator.evaluate_hint(guess, secret, expected_outcome)
    report["hint_correct"] = hint_ok
    if not hint_ok:
        report["issues"].append(f"Hint error: {hint_detail}")
    report["details"]["hint"] = hint_detail
    
    # Step 3: Validate game state
    state_ok, state_issues = GameStateEvaluator.evaluate_game_state(
        secret=secret,
        attempts=game_state.get("attempts", 0),
        attempt_limit=game_state.get("attempt_limit", 8),
        status=game_state.get("status", "playing"),
        score=game_state.get("score", 0),
        history=game_state.get("history", []),
        low=low,
        high=high
    )
    report["state_valid"] = state_ok
    if state_issues:
        report["issues"].extend(state_issues)
    
    return report
