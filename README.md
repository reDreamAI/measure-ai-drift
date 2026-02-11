# Measure-AI-Drift

## This project aims at testing souvereign LLMs in therapeutic context against propietary systems focusing on stochastic drift and consistency.


<img width="602" height="283" alt="dialogue_test_evaluation" src="https://github.com/user-attachments/assets/fd494f0a-2ac8-470d-8884-06be2c89a893" />

<img width="1065" height="29" alt="plan_example" src="https://github.com/user-attachments/assets/b96405b3-dbb1-4098-84b3-4f1fda21d21e" />

### Example trials for evaluation

trial_01.json:
{
  "temperature": 0.5,
  "plan": "<plan> empowerment / mastery </plan>",
  "response": "You're considering the possibility of either seeing who's entering the room or being able to move. That could significantly change the dynamics of the situation. If you could move, where would you go or what would you do as the door opens?",
  "plan_usage": {
    "prompt_tokens": 660,
    "completion_tokens": 10,
    "total_tokens": 670,
    "model": "llama-3.3-70b-versatile"
  },
  "response_usage": {
    "prompt_tokens": 1264,
    "completion_tokens": 49,
    "total_tokens": 1313,
    "model": "llama-3.3-70b-versatile"
  },
  "strategies": [
    "empowerment",
    "mastery"
  ]
}

trial_03-json
{
  "temperature": 0.5,
  "plan": "<plan> empowerment / mastery </plan>",
  "response": "You're considering having the ability to see who's entering or being able to move as a way to regain control in this situation. If you could see who it is, what would you hope to see or experience that would make you feel more at ease or empowered?",
  "plan_usage": {
    "prompt_tokens": 660,
    "completion_tokens": 10,
    "total_tokens": 670,
    "model": "llama-3.3-70b-versatile"
  },
  "response_usage": {
    "prompt_tokens": 1264,
    "completion_tokens": 54,
    "total_tokens": 1318,
    "model": "llama-3.3-70b-versatile"
  },
  "strategies": [
    "empowerment",
    "mastery"
  ]
}
