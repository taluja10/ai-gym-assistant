from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.models import get_db, GymEquipment

router = APIRouter()

@router.get("/gym/{gym_id}")
def get_gym_equipment(gym_id: str, db: Session = Depends(get_db)):
    equipment = db.query(GymEquipment).filter(GymEquipment.gym_id == gym_id).all()
    return [{"id": e.id, "machine": e.machine_name, "exercises": e.exercises_enabled} for e in equipment]
