# 🏗️ System Architecture Diagram

## Overview

The AI-Enhanced Number Guesser is a multi-layered system combining game logic, AI-powered suggestions, and client-side evaluation.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT UI LAYER                          │
│  • Difficulty Selection (Easy/Normal/Hard)                       │
│  • Input: Player Guess                                           │
│  • Display: Hints, Score, Attempts                               │
│  • Buttons: Submit, New Game, Ask AI                             │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│              SESSION STATE MANAGEMENT (Streamlit)                │
│  • secret: int (secret number)                                   │
│  • attempts: int (current attempt count)                         │
│  • score: int (current game score)                               │
│  • status: str ("playing"/"won"/"lost")                          │
│  • history: list[dict] (guess history)                           │
│  • ai_suggestion: dict | None                                    │
└─────────────────────────────────────────────────────────────────┘
        ↓                                  ↓
┌──────────────────────────┐    ┌──────────────────────────┐
│   GAME LOGIC LAYER       │    │   AI ADVISOR LAYER       │
│   (logic_utils.py)       │    │   (ai_advisor.py)        │
│                          │    │                          │
│ • get_range_for_..()     │    │ Uses Gemini API with     │
│ • parse_guess()          │    │ Tool Use for binary      │
│ • check_guess()          │    │ search strategy          │
│ • update_score()         │    │                          │
│                          │    │ Multi-step workflow:     │
│ Input: difficulty,       │    │ 1. Analyze search space  │
│        guess int         │    │ 2. Suggest next guess    │
│ Output: outcome,         │    │                          │
│         message,score    │    │ Input: range, history    │
│                          │    │ Output: suggestion,      │
│                          │    │         reasoning        │
└──────────────────────────┘    └──────────────────────────┘
        ↓                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│         RELIABILITY LAYER (Guardrails & Evaluation)              │
│  • Input Validation: Number ranges, type checking                │
│  • Output Guardrails: AI suggestion sanity checks                │
│  • Evaluator: Test AI suggestions against history                │
│  • Score Validation: Penalties/rewards within bounds             │
└─────────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│  • Google Gemini API: AI suggestions & binary search             │
│  • Environment: GOOGLE_API_KEY                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Game Initialization
```
User Selects Difficulty
    ↓
get_range_for_difficulty()
    ↓
Random Secret Generated & Stored in Session State
    ↓
Game Ready (status = "playing")
```

### 2. Player Submits Guess (Main Loop)
```
Player Input → parse_guess() 
    ↓
[Valid?] → No → Error Message + History Record
    ↓ Yes
[Checked] → check_guess() 
    ↓
(outcome, message) returned
    ↓
update_score() 
    ↓
Session State Updated (attempts++, score, history)
    ↓
[outcome == "Win"?]
    ├─→ Yes → status = "won" → Show Score
    ├─→ No → [attempts >= limit?]
    │       ├─→ Yes → status = "lost"
    │       └─→ No → Continue Playing
    └─→ Display Hint (if enabled)
```

### 3. AI Advisor Workflow (Multi-Step)
```
User Clicks "Ask AI" → Gemini API Called
    ↓
Tool 1: analyze_search_space()
    • Analyzes valid bounds from history
    • Logic: if guess was "Too High" → upper_bound = guess
    •        if guess was "Too Low" → lower_bound = guess
    ↓
Tool 2: suggest_guess()
    • Calculates midpoint of valid range
    • Binary search strategy
    ↓
Result: {suggested_guess, explanation, lower_bound, upper_bound, reasoning}
    ↓
UI Displays AI Suggestion + Reasoning
```

### 4. Reliability Evaluation
```
AI Suggestion Generated
    ↓
Guardrail Checks:
  1. Is suggested_guess within valid range?
  2. Has this guess already been tried?
  3. Do bounds match game rules?
  4. Is suggestion logically consistent?
    ↓
[All checks pass?]
    ├─→ Yes → Display Suggestion
    └─→ No → Show Warning or Fallback
```

## Component Responsibilities

| Component | Purpose | Input | Output |
|-----------|---------|-------|--------|
| **app.py** | UI orchestration & state management | User actions | Rendered UI |
| **logic_utils.py** | Core game logic & scoring | Difficulty, guess, secret | Outcome, message, score |
| **ai_advisor.py** | AI-powered suggestions via Gemini | Range, history, attempts | Suggestion with reasoning |
| **evaluator.py** | Validates & tests suggestions | Suggestions, history | Pass/fail report |
| **demo.py** | End-to-end testing & verification | None (automated) | Test results |

## Key Design Decisions

1. **Stateless Logic Functions**: All game logic in `logic_utils.py` is pure (no side effects), making it testable and reusable.

2. **Tool-Based AI Reasoning**: The AI advisor uses Gemini's tool-calling feature for structured, verifiable suggestions rather than free-form text.

3. **Session-Based Games**: Each game is isolated in Streamlit session state, allowing multiple parallel games without interference.

4. **Guardrails Before Display**: Suggestions are validated before shown to the player, preventing misleading AI outputs.

5. **Binary Search Strategy**: The AI uses an optimal number-guessing algorithm (binary search), teaching the player efficient strategies.

## Integration Points

- **Streamlit ↔ Logic**: Session state bridges UI to pure logic functions
- **Logic ↔ AI Advisor**: History and ranges passed to AI for context
- **AI Advisor ↔ Evaluator**: Suggestions evaluated before display
- **Evaluator ↔ UI**: Validation results inform user feedback
