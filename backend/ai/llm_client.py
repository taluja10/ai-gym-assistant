import json, re
from typing import Optional
from backend.config import settings

TRAINER_SYSTEM_PROMPT = """You are Alex, an experienced and encouraging personal trainer with 10 years of gym experience.

PERSONALITY RULES (NEVER break these):
- NEVER say "you failed", "you missed", "you can't", or anything negative
- ALWAYS say "let's improve", "next session we'll build on this", "great effort"
- Celebrate showing up — consistency > perfection
- Be specific and actionable, not vague
- Max 2 sentences of motivation per response

WORKOUT GENERATION RULES:
1. Only use exercises from the equipment list provided — never invent equipment
2. Increase weight ONLY by 2.5kg increments
3. Beginners: start at 30-40% body weight on compound lifts (machines, not barbell)
4. If user missed 2+ sessions, reduce volume by 20% this session (be supportive about it)
5. Suggest RPE (Rate of Perceived Exertion) target for each exercise
6. Always include warm-up (5 min treadmill walk) as first item

PROGRESSION LOGIC:
- All reps completed → next session increase weight by 2.5kg
- 80-99% reps completed → maintain same weight
- <80% reps completed → reduce by 2.5kg next session

OUTPUT: Always respond with valid JSON only. No markdown, no explanation outside JSON."""

def call_llm(prompt: str, system: Optional[str] = None) -> str:
    """Call Groq API with fallback to rule-based generation."""
    if not settings.GROQ_API_KEY:
        return _fallback_response(prompt)
    
    try:
        import requests
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system or TRAINER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.3
        }
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=payload, timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return _fallback_response(prompt)
    except Exception:
        return _fallback_response(prompt)

def _fallback_response(prompt: str) -> str:
    """Rule-based fallback when no API key is present."""
    return json.dumps({
        "workout": [],
        "motivation": "Every session is progress. You showed up — that's what matters!",
        "notes": "AI offline — rule-based plan generated"
    })

def generate_workout_with_llm(user_context: dict, equipment: list, last_sessions: list, split: str) -> dict:
    """Main workout generation call."""
    prompt = f"""
Generate a {split.upper()} day workout for this athlete.

ATHLETE PROFILE:
- Name: {user_context.get('name')}
- Age: {user_context.get('age')} | Weight: {user_context.get('weight_kg')}kg | Height: {user_context.get('height_cm')}cm
- Goal: {user_context.get('goal')} | Experience: {user_context.get('experience')}
- Training days/week: {user_context.get('days_per_week')}

AVAILABLE EQUIPMENT (only use these):
{json.dumps(equipment, indent=2)}

LAST 3 SESSIONS (use for progression):
{json.dumps(last_sessions, indent=2)}

TODAY'S SPLIT: {split}

Respond with this exact JSON structure:
{{
  "split": "{split}",
  "warm_up": {{"duration_minutes": 5, "type": "Treadmill Walk", "notes": "Light pace to warm up"}},
  "exercises": [
    {{
      "name": "Exercise Name",
      "muscle_group": "chest",
      "sets": 3,
      "reps_target": 10,
      "weight_kg": 25.0,
      "rest_seconds": 90,
      "rpe_target": 7,
      "progression_note": "Increased from 22.5kg — great consistency!",
      "form_cue": "Keep elbows at 45 degrees"
    }}
  ],
  "cool_down": {{"duration_minutes": 5, "type": "Stretching", "notes": "Focus on worked muscles"}},
  "motivation": "Encouraging message specific to this athlete",
  "estimated_duration_minutes": 55
}}
"""
    raw = call_llm(prompt)
    try:
        cleaned = re.sub(r"```json|```", "", raw).strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return _rule_based_workout(user_context, equipment, last_sessions, split)

def _rule_based_workout(user, equipment, last_sessions, split) -> dict:
    """Deterministic rule-based fallback workout."""
    from backend.services.progression import get_next_weight
    
    split_exercises = {
        "push":     [("Machine Chest Press","chest",3,10),("Dumbbell Bench Press","chest",3,10),
                     ("Machine Shoulder Press","shoulders",3,12),("Lateral Raise","shoulders",3,15),
                     ("Tricep Pushdown","arms",3,12)],
        "pull":     [("Lat Pulldown","back",3,10),("Cable Row","back",3,10),
                     ("Dumbbell Row","back",3,12),("Dumbbell Curl","arms",3,12),("Face Pull","shoulders",3,15)],
        "legs":     [("Leg Press","legs",3,12),("Leg Extension","legs",3,12),
                     ("Lying Leg Curl","legs",3,12),("Goblet Squat","legs",3,10),
                     ("Calf Raises on Leg Press","legs",3,15)],
        "full_body":[("Machine Chest Press","chest",3,10),("Lat Pulldown","back",3,10),
                     ("Leg Press","legs",3,12),("Dumbbell Curl","arms",3,12),("Tricep Pushdown","arms",3,12)],
    }
    
    exercises_list = []
    base_weights = {"beginner":{"Machine Chest Press":20,"Lat Pulldown":25,"Leg Press":40,"Dumbbell Curl":8,"Tricep Pushdown":12,"Lateral Raise":6,"Face Pull":10,"Dumbbell Row":14,"Cable Row":20,"Dumbbell Bench Press":12,"Machine Shoulder Press":20,"Leg Extension":20,"Lying Leg Curl":20,"Goblet Squat":10,"Calf Raises on Leg Press":30},
                    "intermediate":{"Machine Chest Press":40,"Lat Pulldown":45,"Leg Press":80,"Dumbbell Curl":14,"Tricep Pushdown":22,"Lateral Raise":10,"Face Pull":18,"Dumbbell Row":24,"Cable Row":38,"Dumbbell Bench Press":24,"Machine Shoulder Press":35,"Leg Extension":35,"Lying Leg Curl":30,"Goblet Squat":20,"Calf Raises on Leg Press":60},
                    "advanced":{"Machine Chest Press":60,"Lat Pulldown":65,"Leg Press":110,"Dumbbell Curl":20,"Tricep Pushdown":32,"Lateral Raise":14,"Face Pull":25,"Dumbbell Row":32,"Cable Row":55,"Dumbbell Bench Press":36,"Machine Shoulder Press":55,"Leg Extension":50,"Lying Leg Curl":45,"Goblet Squat":28,"Calf Raises on Leg Press":90}}
    
    exp = user.get("experience", "beginner")
    for (ex_name, muscle, sets, reps) in split_exercises.get(split, split_exercises["full_body"]):
        last_w = _find_last_weight(last_sessions, ex_name)
        base_w = base_weights.get(exp, base_weights["beginner"]).get(ex_name, 15)
        w = last_w if last_w else base_w
        exercises_list.append({
            "name": ex_name, "muscle_group": muscle,
            "sets": sets, "reps_target": reps,
            "weight_kg": w, "rest_seconds": 90, "rpe_target": 7,
            "progression_note": f"Target: {reps} reps. Increase to {w+2.5}kg next session if completed.",
            "form_cue": "Controlled movement, full range of motion"
        })
    
    return {
        "split": split,
        "warm_up": {"duration_minutes": 5, "type": "Treadmill Walk", "notes": "5 min at comfortable pace"},
        "exercises": exercises_list,
        "cool_down": {"duration_minutes": 5, "type": "Stretching", "notes": "Hold each stretch 20-30 seconds"},
        "motivation": "Every rep you do today is an investment in the person you're becoming. Let's go!",
        "estimated_duration_minutes": 55
    }

def _find_last_weight(last_sessions, exercise_name) -> float:
    for session in reversed(last_sessions):
        for s in session.get("sets", []):
            if s.get("exercise_name") == exercise_name:
                return s.get("weight_kg", 0)
    return 0

def generate_motivation_message(user_name: str, streak: int, missed: int) -> str:
    messages_streak = [
        f"You're on a {streak}-session streak, {user_name.split()[0]}! That's the kind of consistency that builds real results.",
        f"{streak} sessions strong! The weights will follow the discipline you're building.",
        f"Showing up {streak} times in a row — most people never make it this far. Keep going.",
    ]
    messages_after_miss = [
        f"Welcome back, {user_name.split()[0]}! Life happens. What matters is you're here now.",
        f"Every champion has setbacks. Your comeback starts today — let's make it count.",
        f"The best session is always the next one. You're here, and that's everything.",
    ]
    messages_normal = [
        "Consistency matters more than perfection. One session at a time.",
        "The body achieves what the mind believes. You've got this today.",
        "Progress is slow but it's happening — trust the process.",
    ]
    import random
    if missed > 0:
        return random.choice(messages_after_miss)
    elif streak > 2:
        return random.choice(messages_streak)
    return random.choice(messages_normal)
