from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, Date, DateTime, JSON, Text, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
from backend.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def new_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id            = Column(String, primary_key=True, default=new_uuid)
    name          = Column(String, nullable=False)
    email         = Column(String, unique=True, nullable=False)
    age           = Column(Integer)
    weight_kg     = Column(Float)
    height_cm     = Column(Float)
    goal          = Column(String)        # muscle_gain | fat_loss | maintain | strength
    experience    = Column(String)        # beginner | intermediate | advanced
    gym_id        = Column(String, ForeignKey("gyms.id"))
    days_per_week = Column(Integer, default=4)
    vegetarian    = Column(Boolean, default=False)
    reminder_time = Column(String, default="08:00")
    created_at    = Column(DateTime, default=datetime.utcnow)

    sessions   = relationship("WorkoutSession", back_populates="user")
    snapshots  = relationship("ProgressSnapshot", back_populates="user")
    diet_plans = relationship("DietPlan", back_populates="user")
    gym        = relationship("Gym", back_populates="users")

class Gym(Base):
    __tablename__ = "gyms"
    id         = Column(String, primary_key=True, default=new_uuid)
    name       = Column(String)
    location   = Column(String)
    users      = relationship("User", back_populates="gym")
    equipment  = relationship("GymEquipment", back_populates="gym")

class GymEquipment(Base):
    __tablename__ = "gym_equipment"
    id                = Column(String, primary_key=True, default=new_uuid)
    gym_id            = Column(String, ForeignKey("gyms.id"))
    machine_name      = Column(String)
    exercises_enabled = Column(JSON)    # list of exercise names
    gym               = relationship("Gym", back_populates="equipment")

class Exercise(Base):
    __tablename__ = "exercises"
    id                 = Column(String, primary_key=True, default=new_uuid)
    name               = Column(String, unique=True)
    muscle_group       = Column(String)   # chest | back | shoulders | legs | arms | core
    equipment_required = Column(String)
    difficulty         = Column(String)   # beginner | intermediate | advanced
    video_cue          = Column(Text)

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"
    id         = Column(String, primary_key=True, default=new_uuid)
    user_id    = Column(String, ForeignKey("users.id"))
    date       = Column(Date)
    split_type = Column(String)  # push | pull | legs | full_body | upper | lower
    status     = Column(String, default="planned")  # planned | completed | skipped
    notes      = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    sets = relationship("WorkoutSet", back_populates="session", cascade="all, delete-orphan")

class WorkoutSet(Base):
    __tablename__ = "workout_sets"
    id              = Column(String, primary_key=True, default=new_uuid)
    session_id      = Column(String, ForeignKey("workout_sessions.id"))
    exercise_id     = Column(String, ForeignKey("exercises.id"))
    exercise_name   = Column(String)
    set_number      = Column(Integer)
    reps_target     = Column(Integer)
    reps_completed  = Column(Integer)
    weight_kg       = Column(Float)
    rpe             = Column(Integer)  # 1-10

    session  = relationship("WorkoutSession", back_populates="sets")
    exercise = relationship("Exercise")

class ProgressSnapshot(Base):
    __tablename__ = "progress_snapshots"
    id                   = Column(String, primary_key=True, default=new_uuid)
    user_id              = Column(String, ForeignKey("users.id"))
    week_start           = Column(Date)
    body_weight_kg       = Column(Float)
    strength_index       = Column(Float)
    total_volume_kg      = Column(Float)
    sessions_completed   = Column(Integer)
    sessions_planned     = Column(Integer)
    insights             = Column(Text)
    created_at           = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="snapshots")

class DietPlan(Base):
    __tablename__ = "diet_plans"
    id               = Column(String, primary_key=True, default=new_uuid)
    user_id          = Column(String, ForeignKey("users.id"))
    calories_target  = Column(Integer)
    protein_target_g = Column(Integer)
    carbs_target_g   = Column(Integer)
    fats_target_g    = Column(Integer)
    meals            = Column(JSON)
    vegetarian       = Column(Boolean, default=False)
    generated_at     = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="diet_plans")
