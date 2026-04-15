from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import users, workouts, progress, diet, ai_chat, equipment
from backend.database.models import Base, engine
from backend.services.reminder_service import start_scheduler

app = FastAPI(title="AI Gym Trainer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(users.router,      prefix="/api/v1/users",     tags=["Users"])
app.include_router(workouts.router,   prefix="/api/v1/workouts",  tags=["Workouts"])
app.include_router(progress.router,   prefix="/api/v1/progress",  tags=["Progress"])
app.include_router(diet.router,       prefix="/api/v1/diet",      tags=["Diet"])
app.include_router(ai_chat.router,    prefix="/api/v1/ai",        tags=["AI Chat"])
app.include_router(equipment.router,  prefix="/api/v1/equipment", tags=["Equipment"])

@app.on_event("startup")
async def startup_event():
    from backend.database.seed_data import seed_database
    seed_database()
    start_scheduler()

@app.get("/")
def root():
    return {"status": "AI Gym Trainer is running", "docs": "/docs"}
