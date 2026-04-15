from datetime import date, timedelta
from sqlalchemy.orm import Session
from backend.database.models import User, WorkoutSession, WorkoutSet, GymEquipment
from backend.ai.llm_client import generate_workout_with_llm, generate_motivation_message
from backend.services.progression import calculate_starting_weight, evaluate_session_performance

WEEKLY_SPLITS = {
    3: ["push", "legs", "pull"],
    4: ["push", "pull", "legs", "push"],
    5: ["push", "pull", "legs", "upper", "lower"],
    6: ["push", "pull", "legs", "push", "pull", "legs"],
}

def get_todays_split(user: User) -> str:
    splits = WEEKLY_SPLITS.get(user.days_per_week, WEEKLY_SPLITS[4])
    day_idx = date.today().weekday()  # 0=Mon, 6=Sun
    if day_idx >= len(splits):
        return "rest"
    return splits[day_idx]

def get_user_equipment(db: Session, user: User) -> list:
    equipment = db.query(GymEquipment).filter(GymEquipment.gym_id == user.gym_id).all()
    result = []
    for eq in equipment:
        result.append({
            "machine": eq.machine_name,
            "exercises": eq.exercises_enabled
        })
    return result

def get_last_sessions(db: Session, user_id: str, limit: int = 3) -> list:
    sessions = (db.query(WorkoutSession)
                .filter(WorkoutSession.user_id == user_id, WorkoutSession.status == "completed")
                .order_by(WorkoutSession.date.desc())
                .limit(limit).all())
    result = []
    for session in sessions:
        sets = db.query(WorkoutSet).filter(WorkoutSet.session_id == session.id).all()
        result.append({
            "date": str(session.date),
            "split": session.split_type,
            "sets": [{"exercise_name": s.exercise_name, "weight_kg": s.weight_kg,
                       "reps_target": s.reps_target, "reps_completed": s.reps_completed,
                       "rpe": s.rpe} for s in sets]
        })
    return result

def generate_next_workout(db: Session, user_id: str) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    split = get_todays_split(user)
    if split == "rest":
        return {"type": "rest", "message": "Rest day today. Your muscles are rebuilding. Stay hydrated!", "split": "rest"}
    
    equipment = get_user_equipment(db, user)
    last_sessions = get_last_sessions(db, user_id)
    
    user_context = {
        "name": user.name, "age": user.age,
        "weight_kg": user.weight_kg, "height_cm": user.height_cm,
        "goal": user.goal, "experience": user.experience,
        "days_per_week": user.days_per_week
    }
    
    workout = generate_workout_with_llm(user_context, equipment, last_sessions, split)
    
    # Calculate missed sessions for motivation
    recent = (db.query(WorkoutSession)
              .filter(WorkoutSession.user_id == user_id)
              .order_by(WorkoutSession.date.desc()).limit(7).all())
    missed = sum(1 for s in recent if s.status == "skipped")
    streak = 0
    for s in recent:
        if s.status == "completed":
            streak += 1
        else:
            break
    
    workout["motivation"] = generate_motivation_message(user.name, streak, missed)
    workout["user"] = user_context
    return workout

def log_workout_session(db: Session, user_id: str, session_data: dict) -> dict:
    """Log a completed workout and calculate next session weights."""
    session = WorkoutSession(
        user_id=user_id,
        date=date.today(),
        split_type=session_data.get("split", "full_body"),
        status="completed",
        notes=session_data.get("notes", "")
    )
    db.add(session)
    db.flush()
    
    sets_logged = []
    for ex in session_data.get("exercises", []):
        for s_num, s_data in enumerate(ex.get("sets", []), 1):
            ws = WorkoutSet(
                session_id=session.id,
                exercise_name=ex["name"],
                set_number=s_num,
                reps_target=s_data.get("reps_target", 10),
                reps_completed=s_data.get("reps_completed", 0),
                weight_kg=s_data.get("weight_kg", 0),
                rpe=s_data.get("rpe", 7)
            )
            db.add(ws)
            sets_logged.append({
                "exercise_name": ex["name"],
                "weight_kg": s_data.get("weight_kg", 0),
                "reps_target": s_data.get("reps_target", 10),
                "reps_completed": s_data.get("reps_completed", 0)
            })
    
    db.commit()
    
    progression = evaluate_session_performance(sets_logged)
    return {
        "session_id": session.id,
        "status": "logged",
        "progression_notes": progression,
        "message": "Session logged! Great work today — consistency is building your foundation."
    }
