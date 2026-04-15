from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.models import get_db, WorkoutSession, User
from backend.services.workout_generator import generate_next_workout, log_workout_session, get_last_sessions
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

router = APIRouter()

class SetLog(BaseModel):
    reps_target: int
    reps_completed: int
    weight_kg: float
    rpe: Optional[int] = 7

class ExerciseLog(BaseModel):
    name: str
    sets: List[SetLog]

class WorkoutLogRequest(BaseModel):
    split: str
    exercises: List[ExerciseLog]
    notes: Optional[str] = ""

@router.get("/today/{user_id}")
def get_todays_workout(user_id: str, db: Session = Depends(get_db)):
    try:
        return generate_next_workout(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/log/{user_id}")
def log_workout(user_id: str, workout: WorkoutLogRequest, db: Session = Depends(get_db)):
    return log_workout_session(db, user_id, workout.dict())

@router.get("/history/{user_id}")
def get_workout_history(user_id: str, limit: int = 10, db: Session = Depends(get_db)):
    return get_last_sessions(db, user_id, limit=limit)

@router.get("/sessions/{user_id}")
def get_all_sessions(user_id: str, db: Session = Depends(get_db)):
    sessions = (db.query(WorkoutSession)
                .filter(WorkoutSession.user_id == user_id)
                .order_by(WorkoutSession.date.desc()).limit(30).all())
    return [{"id": s.id, "date": str(s.date), "split": s.split_type, "status": s.status} for s in sessions]
