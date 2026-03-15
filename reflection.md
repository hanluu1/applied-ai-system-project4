# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").
1. attempt number is not decrease first time submitting the guess
2. the suggestion suggest goes lower when the number is lower than the secret and higher when it is lower
3. the secret was 14 guess 10 the game tell to higher which is right but guess 9 it tells to go lower
4. after win or lose, playing new game didn't work, it wasn't reseting to new game
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
I used both claude and copilot for this project
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
AI correctly suggested an issue related to the difficulty levels in the game. I verified the suggestion by reviewing the code and checking that the values matched the intended difficulty settings
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
When suggesting a fix for the difficulty levels, instead of recommending swapping the values between Normal and Hard, the AI suggested increasing the maximum guessing number for Hard mode to 1000.  
---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed? 
I first tested the live version of the game after each fix. I also asked AI to generate pytest tests that targeted the specific bugs.
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
The main manual test I ran was playing the live version of the game after each fix. This helped me confirm whether the attempt counter, hints, and game reset behavior were working correctly.
- Did AI help you design or understand any tests? How?
AI helped me understand some of the tests, especially when testing the hint suggestion logic. At first I did not understand why a test failed, but AI explained the reason behind the failure and helped me adjust the code to fix it.

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app. 
At first, the hints made it seem like the secret number kept changing during the game, but the issue was actually caused by incorrect hint logic rather than the secret number changing
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit? streamlit rerun the entire app from top to bottom when the user interact with any button on the app so we make sure that the state is put in the right order
- What change did you make that finally gave the game a stable secret number? remove the 
if st.session_state.attempts % 2 == 0:
    secret = str(st.session_state.secret)
else:
    secret = st.session_state.secret

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
  1. Separating AI conversations into different chat threads for each bug was very helpful for tracking debugging progress
  2. having Copilot to review my commit messages to make sure each commit clearly described the changes I pushed.
- What is one thing you would do differently next time you work with AI on a coding task?
Next time, I would spend more time verifying AI suggestions before implementing them to make sure they address the root cause of the problem.
- In one or two sentences, describe how this project changed the way you think about AI generated code.
This project showed me that AI-generated code can be helpful for debugging and explanations, but it still requires careful review and testing by the developer. AI works best as a tool to assist the process rather than replacing it.