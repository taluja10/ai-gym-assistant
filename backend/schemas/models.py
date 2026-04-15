from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class UserCreate(BaseModel):
    name: str
    email: str
    age: int
    weight_kg: float
    height_cm: float
    goal: str
    experience: str
    days_per_week: int = 4
    vegetarian: bool = False
    gym_id: str = "gym-demo-001"

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

class ChatRequest(BaseModel):
    message: str
    user_name: str = "Athlete"
