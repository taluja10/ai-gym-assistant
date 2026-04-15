from backend.config import settings

def get_next_weight(last_weight: float, reps_completed: int, reps_target: int) -> tuple[float, str]:
    """
    Core progression logic.
    Returns (next_weight, message)
    """
    if reps_target == 0:
        return last_weight, "Maintain current weight."
    
    ratio = reps_completed / reps_target

    if ratio >= settings.REP_SUCCESS_THRESHOLD:
        next_w = last_weight + settings.WEIGHT_INCREMENT_KG
        return next_w, f"All reps completed! Increase to {next_w}kg next session."
    elif ratio >= settings.REP_STRUGGLE_THRESHOLD:
        return last_weight, f"Good effort! Maintain {last_weight}kg and aim for cleaner reps."
    else:
        next_w = max(last_weight - settings.WEIGHT_DECREMENT_KG, 2.5)
        return next_w, f"Let's dial it back to {next_w}kg and nail the form. Build from there."

def calculate_starting_weight(experience: str, exercise_name: str, body_weight_kg: float) -> float:
    """
    Calculate beginner starting weight based on body weight and experience.
    Uses conservative multipliers for machine-based exercises.
    """
    multipliers = {
        "beginner": {
            "compound_lower": 0.40,  # leg press, squat
            "compound_upper": 0.30,  # chest press, row
            "isolation":      0.10,  # curls, laterals
        },
        "intermediate": {
            "compound_lower": 0.70,
            "compound_upper": 0.55,
            "isolation":      0.18,
        },
        "advanced": {
            "compound_lower": 1.0,
            "compound_upper": 0.80,
            "isolation":      0.25,
        }
    }

    lower_compounds = {"Leg Press","Smith Machine Squat","Goblet Squat","Dumbbell Lunge","Smith Romanian Deadlift","Dumbbell RDL"}
    upper_compounds = {"Machine Chest Press","Dumbbell Bench Press","Smith Machine Bench","Lat Pulldown","Cable Row","Seated Cable Row","Dumbbell Row","Machine Shoulder Press","Smith Machine OHP"}
    
    exp = multipliers.get(experience, multipliers["beginner"])
    
    if exercise_name in lower_compounds:
        raw = body_weight_kg * exp["compound_lower"]
    elif exercise_name in upper_compounds:
        raw = body_weight_kg * exp["compound_upper"]
    else:
        raw = body_weight_kg * exp["isolation"]
    
    # Round to nearest 2.5
    return round(raw / 2.5) * 2.5

def evaluate_session_performance(sets: list) -> dict:
    """
    Evaluate a completed session and generate per-exercise progression decisions.
    sets: list of dicts with {exercise_name, weight_kg, reps_target, reps_completed}
    Returns: {exercise_name: {next_weight, message, performance}}
    """
    from collections import defaultdict
    grouped = defaultdict(list)
    for s in sets:
        grouped[s["exercise_name"]].append(s)
    
    results = {}
    for ex_name, ex_sets in grouped.items():
        avg_completion = sum(s["reps_completed"] for s in ex_sets) / sum(s["reps_target"] for s in ex_sets)
        last_weight = ex_sets[-1]["weight_kg"]
        next_w, msg = get_next_weight(last_weight, int(avg_completion * 10), 10)
        results[ex_name] = {
            "current_weight": last_weight,
            "next_weight": next_w,
            "avg_completion_pct": round(avg_completion * 100, 1),
            "message": msg,
            "performance": "great" if avg_completion >= 1.0 else ("solid" if avg_completion >= 0.8 else "challenging")
        }
    return results
