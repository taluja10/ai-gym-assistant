from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.models import get_db, User
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

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

@router.post("/onboard")
def onboard_user(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        return {"user_id": existing.id, "name": existing.name, "status": "existing"}
    import uuid
    user = User(id=str(uuid.uuid4()), **data.dict())
    db.add(user)
    db.commit()
    return {"user_id": user.id, "name": user.name, "status": "created"}

@router.get("/list")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "name": u.name, "goal": u.goal, "experience": u.experience, "email": u.email} for u in users]

@router.get("/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.name, "age": user.age, "weight_kg": user.weight_kg,
            "height_cm": user.height_cm, "goal": user.goal, "experience": user.experience,
            "days_per_week": user.days_per_week, "vegetarian": user.vegetarian, "email": user.email}
