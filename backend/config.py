import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./gym_trainer.db")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = "llama3-8b-8192"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "gym-trainer-secret-2024")
    VECTOR_STORE_PATH: str = "./data/vector_store"
    
    # Progression rules
    WEIGHT_INCREMENT_KG: float = 2.5
    WEIGHT_DECREMENT_KG: float = 2.5
    REP_SUCCESS_THRESHOLD: float = 1.0   # 100% reps = increase
    REP_STRUGGLE_THRESHOLD: float = 0.8  # <80% reps = decrease

    # Goal constants
    MAX_FAT_LOSS_KG_PER_WEEK: float = 1.0
    MIN_FAT_LOSS_KG_PER_WEEK: float = 0.5
    BEGINNER_MUSCLE_GAIN_KG_PER_MONTH: float = 1.5
    INTERMEDIATE_MUSCLE_GAIN_KG_PER_MONTH: float = 0.75

settings = Settings()
