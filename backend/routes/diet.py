from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.models import get_db

router = APIRouter()

@router.get("/plan/{user_id}")
def get_diet_plan(user_id: str, db: Session = Depends(get_db)):
    from backend.services.diet_planner import get_or_create_diet_plan
    return get_or_create_diet_plan(db, user_id)

@router.post("/regenerate/{user_id}")
def regenerate_diet(user_id: str, db: Session = Depends(get_db)):
    from backend.services.diet_planner import regenerate_diet_plan
    return regenerate_diet_plan(db, user_id)
