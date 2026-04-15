from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from backend.database.models import get_db, User, DietPlan
from backend.ai.llm_client import call_llm
from backend.services.workout_generator import get_todays_split, get_user_equipment, get_last_sessions

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    user_id: str
    message: str
    history: Optional[List[ChatMessage]] = []

def build_alex_system_prompt(user, equipment, last_sessions, diet) -> str:
    split = get_todays_split(user)
    return f"""You are Alex, an experienced and encouraging personal trainer AI.

CURRENT ATHLETE:
- Name: {user.name} | Age: {user.age} | Weight: {user.weight_kg}kg | Height: {user.height_cm}cm
- Goal: {user.goal} | Experience: {user.experience} | Days/week: {user.days_per_week}
- Diet: {"Vegetarian" if user.vegetarian else "Non-vegetarian"}

TODAY'S SPLIT: {split}
LAST SESSIONS: {last_sessions}
NUTRITION: {diet.calories_target if diet else 2200} kcal | {diet.protein_target_g if diet else 130}g protein
GYM EQUIPMENT: {[e['machine'] for e in equipment]}

RULES: Never say "you failed". Always encouraging. Use Indian foods for diet. Only suggest equipment they have. Be concise and specific."""

@router.post("/chat")
def chat_with_trainer(request: ChatRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        return {"reply": "Profile not found.", "trainer": "Alex"}
    equipment = get_user_equipment(db, user)
    last_sessions = get_last_sessions(db, request.user_id, limit=2)
    diet = db.query(DietPlan).filter(DietPlan.user_id == request.user_id).order_by(DietPlan.generated_at.desc()).first()
    system = build_alex_system_prompt(user, equipment, last_sessions, diet)
    history_text = "\n".join(f"{m.role.upper()}: {m.content}" for m in (request.history or [])[-6:])
    full_prompt = f"{history_text}\nUSER: {request.message}" if history_text else request.message
    response = call_llm(full_prompt, system=system)
    import json, re
    try:
        data = json.loads(re.sub(r"```json|```", "", response).strip())
        reply = data.get("motivation") or data.get("message") or str(data)
    except Exception:
        reply = response
    return {"reply": reply, "trainer": "Alex"}

@router.get("/motivation/{user_id}")
def get_motivation(user_id: str, db: Session = Depends(get_db)):
    from backend.ai.llm_client import generate_motivation_message
    from backend.database.models import WorkoutSession
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"message": "Keep showing up — consistency beats perfection every time."}
    recent = db.query(WorkoutSession).filter(WorkoutSession.user_id == user_id).order_by(WorkoutSession.date.desc()).limit(7).all()
    missed = sum(1 for s in recent if s.status == "skipped")
    streak = sum(1 for s in recent if s.status == "completed")
    return {"message": generate_motivation_message(user.name, streak, missed), "streak": streak}
