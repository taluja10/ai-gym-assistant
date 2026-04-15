from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.models import get_db

router = APIRouter()

@router.get("/analytics/{user_id}")
def get_analytics(user_id: str, db: Session = Depends(get_db)):
    from backend.services.analytics import get_progress_analytics
    return get_progress_analytics(db, user_id)
