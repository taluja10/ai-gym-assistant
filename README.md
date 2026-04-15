# AI Gym Trainer 🏋️

A full-stack AI personal trainer system that behaves like a real gym trainer — adaptive, encouraging, and grounded in realistic progression science.

## Quick Start

### Option A — Standalone HTML (No install needed)
Open `frontend/index.html` in any browser. Full working demo with all 5 sample users, charts, workouts, diet plans, and equipment data. No server required.

### Option B — Full Stack (FastAPI + Streamlit)

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure environment**
```bash
cp .env.example .env
# Add your Groq API key (free at console.groq.com)
# GROQ_API_KEY=gsk_...
```

**3. Start backend**
```bash
uvicorn backend.main:app --reload
# API runs at http://localhost:8000
# Docs at http://localhost:8000/docs
```

**4. Start frontend**
```bash
streamlit run frontend/streamlit_app.py
```

## Project Structure

```
ai_gym_trainer/
├── backend/
│   ├── main.py                  # FastAPI app
│   ├── config.py                # Settings
│   ├── routes/
│   │   ├── users.py             # User management
│   │   ├── workouts.py          # Workout generation + logging
│   │   ├── progress.py          # Analytics
│   │   ├── diet.py              # Diet plans
│   │   ├── equipment.py         # Gym equipment
│   │   └── ai_chat.py           # AI conversation
│   ├── services/
│   │   ├── workout_generator.py # Core generation logic
│   │   ├── progression.py       # Weight progression rules
│   │   ├── analytics.py         # Pandas insights
│   │   ├── diet_planner.py      # Macro calculation
│   │   └── reminder_service.py  # APScheduler
│   ├── ai/
│   │   └── llm_client.py        # Groq/Ollama integration
│   └── database/
│       ├── models.py            # SQLAlchemy ORM
│       └── seed_data.py         # 5 demo users + equipment
├── frontend/
│   ├── index.html               # Standalone full UI (open directly)
│   └── streamlit_app.py         # Streamlit dashboard
└── requirements.txt
```

## Demo Users

| User | Goal | Level |
|------|------|-------|
| Arjun Sharma | Muscle Gain | Beginner |
| Priya Mehta | Fat Loss | Intermediate |
| Rohit Verma | Strength | Intermediate |
| Sneha Iyer | Toning | Beginner |
| Kabir Singh | Muscle Gain | Advanced |

## AI Model Options (Free)

| Provider | Model | Setup |
|----------|-------|-------|
| **Groq** (recommended) | llama3-8b-8192 | Free at console.groq.com |
| Ollama (local) | llama3 | Install ollama.ai |
| HuggingFace | mistral-7b | Free API key |

## Key Features

- **Equipment-aware:** Only suggests exercises your gym has
- **Progressive overload:** 2.5kg increments, backed by completion data  
- **Indian diet plans:** Vegetarian/non-veg with local foods
- **Realistic goals:** Never promises extreme results
- **Encouraging AI:** Positive tone, never negative feedback

## API Endpoints

```
GET  /api/v1/workouts/today/{user_id}     # Today's generated workout
POST /api/v1/workouts/log/{user_id}       # Log completed session
GET  /api/v1/progress/analytics/{user_id} # Progress insights
GET  /api/v1/diet/plan/{user_id}          # Current diet plan
GET  /api/v1/equipment/gym/{gym_id}       # Available machines
POST /api/v1/ai/chat                      # Chat with Alex
```

## Roadmap

- [ ] Phase 1: MVP (this codebase)
- [ ] Phase 2: Groq LLM integration + vector memory (FAISS)
- [ ] Phase 3: Voice trainer (Whisper + TTS)
- [ ] Phase 4: Form detection (MediaPipe)
- [ ] Phase 5: Mobile app (React Native)
