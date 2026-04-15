from backend.database.models import SessionLocal, User, Gym, GymEquipment, Exercise, WorkoutSession, WorkoutSet, ProgressSnapshot, DietPlan
from datetime import date, datetime, timedelta
import uuid, random

DEMO_GYM_ID    = "gym-demo-001"
DEMO_USERS     = [
    {"id":"u1","name":"Arjun Sharma",  "email":"arjun@demo.com",  "age":22,"weight_kg":68,"height_cm":175,"goal":"muscle_gain","experience":"beginner",     "days_per_week":4,"vegetarian":False},
    {"id":"u2","name":"Priya Mehta",   "email":"priya@demo.com",   "age":27,"weight_kg":58,"height_cm":162,"goal":"fat_loss",   "experience":"intermediate", "days_per_week":5,"vegetarian":True},
    {"id":"u3","name":"Rohit Verma",   "email":"rohit@demo.com",   "age":35,"weight_kg":90,"height_cm":180,"goal":"strength",  "experience":"intermediate", "days_per_week":4,"vegetarian":False},
    {"id":"u4","name":"Sneha Iyer",    "email":"sneha@demo.com",   "age":24,"weight_kg":52,"height_cm":158,"goal":"tone",      "experience":"beginner",     "days_per_week":3,"vegetarian":True},
    {"id":"u5","name":"Kabir Singh",   "email":"kabir@demo.com",   "age":30,"weight_kg":78,"height_cm":178,"goal":"muscle_gain","experience":"advanced",    "days_per_week":5,"vegetarian":False},
]

GYM_EQUIPMENT = [
    {"machine_name":"Chest Press Machine",   "exercises_enabled":["Machine Chest Press","Incline Machine Press"]},
    {"machine_name":"Cable Machine",         "exercises_enabled":["Cable Fly","Tricep Pushdown","Face Pull","Cable Row","Cable Curl","Overhead Cable Tricep"]},
    {"machine_name":"Lat Pulldown Machine",  "exercises_enabled":["Lat Pulldown","Close-Grip Pulldown","Straight-Arm Pulldown"]},
    {"machine_name":"Smith Machine",         "exercises_enabled":["Smith Machine Squat","Smith Machine Bench","Smith Machine OHP","Smith Romanian Deadlift"]},
    {"machine_name":"Leg Press Machine",     "exercises_enabled":["Leg Press","Calf Raises on Leg Press","Narrow Stance Leg Press"]},
    {"machine_name":"Shoulder Press Machine","exercises_enabled":["Machine Shoulder Press","Seated Rear Delt Fly"]},
    {"machine_name":"Dumbbells (up to 30kg)","exercises_enabled":["Dumbbell Curl","Lateral Raise","Dumbbell RDL","Goblet Squat","Dumbbell Bench Press","Dumbbell Row","Hammer Curl","Dumbbell Lunge"]},
    {"machine_name":"Treadmill",             "exercises_enabled":["Treadmill Walk","Treadmill Run","Incline Walk"]},
    {"machine_name":"Leg Curl Machine",      "exercises_enabled":["Lying Leg Curl","Seated Leg Curl"]},
    {"machine_name":"Leg Extension Machine", "exercises_enabled":["Leg Extension"]},
    {"machine_name":"Pec Deck Machine",      "exercises_enabled":["Pec Deck Fly","Rear Delt Pec Deck"]},
    {"machine_name":"Seated Row Machine",    "exercises_enabled":["Seated Cable Row","Chest-Supported Row"]},
]

EXERCISES = [
    ("Machine Chest Press","chest","Chest Press Machine","beginner"),
    ("Incline Machine Press","chest","Chest Press Machine","intermediate"),
    ("Cable Fly","chest","Cable Machine","intermediate"),
    ("Pec Deck Fly","chest","Pec Deck Machine","beginner"),
    ("Smith Machine Bench","chest","Smith Machine","intermediate"),
    ("Dumbbell Bench Press","chest","Dumbbells (up to 30kg)","beginner"),
    ("Lat Pulldown","back","Lat Pulldown Machine","beginner"),
    ("Close-Grip Pulldown","back","Lat Pulldown Machine","intermediate"),
    ("Cable Row","back","Cable Machine","beginner"),
    ("Seated Cable Row","back","Seated Row Machine","beginner"),
    ("Dumbbell Row","back","Dumbbells (up to 30kg)","beginner"),
    ("Machine Shoulder Press","shoulders","Shoulder Press Machine","beginner"),
    ("Lateral Raise","shoulders","Dumbbells (up to 30kg)","beginner"),
    ("Face Pull","shoulders","Cable Machine","intermediate"),
    ("Rear Delt Pec Deck","shoulders","Pec Deck Machine","beginner"),
    ("Tricep Pushdown","arms","Cable Machine","beginner"),
    ("Overhead Cable Tricep","arms","Cable Machine","intermediate"),
    ("Dumbbell Curl","arms","Dumbbells (up to 30kg)","beginner"),
    ("Hammer Curl","arms","Dumbbells (up to 30kg)","beginner"),
    ("Cable Curl","arms","Cable Machine","beginner"),
    ("Leg Press","legs","Leg Press Machine","beginner"),
    ("Smith Machine Squat","legs","Smith Machine","intermediate"),
    ("Goblet Squat","legs","Dumbbells (up to 30kg)","beginner"),
    ("Leg Extension","legs","Leg Extension Machine","beginner"),
    ("Lying Leg Curl","legs","Leg Curl Machine","beginner"),
    ("Calf Raises on Leg Press","legs","Leg Press Machine","beginner"),
    ("Dumbbell Lunge","legs","Dumbbells (up to 30kg)","beginner"),
    ("Dumbbell RDL","legs","Dumbbells (up to 30kg)","intermediate"),
    ("Treadmill Walk","cardio","Treadmill","beginner"),
    ("Treadmill Run","cardio","Treadmill","beginner"),
]

SPLITS = ["push","pull","legs","push","pull","legs","rest"]

def seed_database():
    db = SessionLocal()
    try:
        if db.query(Gym).filter(Gym.id == DEMO_GYM_ID).first():
            return  # already seeded

        # Gym
        gym = Gym(id=DEMO_GYM_ID, name="FitZone Gym", location="Delhi, India")
        db.add(gym)

        # Equipment
        for eq in GYM_EQUIPMENT:
            db.add(GymEquipment(gym_id=DEMO_GYM_ID, **eq))

        # Exercises
        for (name, muscle, equip, diff) in EXERCISES:
            db.add(Exercise(id=str(uuid.uuid4()), name=name, muscle_group=muscle,
                            equipment_required=equip, difficulty=diff))

        # Users
        for u in DEMO_USERS:
            db.add(User(**u, gym_id=DEMO_GYM_ID))

        db.commit()

        # Sessions + sets (8 weeks history for each user)
        for u in DEMO_USERS:
            _seed_user_history(db, u)

        # Progress snapshots
        for u in DEMO_USERS:
            _seed_progress(db, u)

        # Diet plans
        for u in DEMO_USERS:
            _seed_diet(db, u)

        db.commit()
    finally:
        db.close()

def _seed_user_history(db, u):
    base_date = date.today() - timedelta(weeks=8)
    split_idx = 0
    for day_offset in range(56):
        current_date = base_date + timedelta(days=day_offset)
        if current_date.weekday() == 6:  # skip Sundays
            continue
        split = SPLITS[split_idx % len(SPLITS)]
        split_idx += 1
        if split == "rest":
            continue
        session = WorkoutSession(
            id=str(uuid.uuid4()), user_id=u["id"],
            date=current_date, split_type=split, status="completed"
        )
        db.add(session)
        exercises_for_split = _get_exercises_for_split(split)
        for ex_name in exercises_for_split[:4]:
            base_w = _get_starting_weight(u["experience"], ex_name)
            progression = day_offset * 0.1
            for s in range(1, 4):
                db.add(WorkoutSet(
                    id=str(uuid.uuid4()), session_id=session.id,
                    exercise_name=ex_name, set_number=s,
                    reps_target=10, reps_completed=random.randint(8, 12),
                    weight_kg=round(base_w + progression, 1), rpe=random.randint(6, 8)
                ))

def _get_exercises_for_split(split):
    mapping = {
        "push":     ["Machine Chest Press","Dumbbell Bench Press","Machine Shoulder Press","Lateral Raise","Tricep Pushdown"],
        "pull":     ["Lat Pulldown","Cable Row","Dumbbell Row","Dumbbell Curl","Face Pull"],
        "legs":     ["Leg Press","Smith Machine Squat","Leg Extension","Lying Leg Curl","Calf Raises on Leg Press"],
        "full_body":["Machine Chest Press","Lat Pulldown","Leg Press","Dumbbell Curl","Tricep Pushdown"],
    }
    return mapping.get(split, ["Machine Chest Press","Lat Pulldown","Leg Press"])

def _get_starting_weight(experience, exercise_name):
    weights = {"beginner": {"Machine Chest Press":20,"Lat Pulldown":25,"Leg Press":40,"Dumbbell Curl":8,"Tricep Pushdown":12,"Lateral Raise":6,"Face Pull":10,"Dumbbell Row":14,"Cable Row":20},
               "intermediate":{"Machine Chest Press":35,"Lat Pulldown":40,"Leg Press":70,"Dumbbell Curl":14,"Tricep Pushdown":20,"Lateral Raise":10,"Face Pull":18,"Dumbbell Row":22,"Cable Row":35},
               "advanced":{"Machine Chest Press":55,"Lat Pulldown":60,"Leg Press":100,"Dumbbell Curl":20,"Tricep Pushdown":30,"Lateral Raise":14,"Face Pull":25,"Dumbbell Row":30,"Cable Row":50}}
    return weights.get(experience, weights["beginner"]).get(exercise_name, 15)

def _seed_progress(db, u):
    for w in range(8):
        week_start = date.today() - timedelta(weeks=8-w)
        strength_base = 45 if u["experience"] == "beginner" else (65 if u["experience"] == "intermediate" else 80)
        db.add(ProgressSnapshot(
            id=str(uuid.uuid4()), user_id=u["id"],
            week_start=week_start,
            body_weight_kg=u["weight_kg"] + (0.2 * w if u["goal"] == "muscle_gain" else -0.3 * w),
            strength_index=strength_base + w * 1.5,
            total_volume_kg=round(random.uniform(2800, 4200), 0),
            sessions_completed=random.randint(3, 5),
            sessions_planned=u["days_per_week"],
            insights=f"Week {w+1}: Consistent progress observed."
        ))

def _seed_diet(db, u):
    protein = round(u["weight_kg"] * 2.0)
    calories = round(u["weight_kg"] * (35 if u["goal"] == "muscle_gain" else 27))
    meals = _build_meals(u["vegetarian"], protein, calories)
    db.add(DietPlan(
        id=str(uuid.uuid4()), user_id=u["id"],
        calories_target=calories, protein_target_g=protein,
        carbs_target_g=round(calories * 0.45 / 4),
        fats_target_g=round(calories * 0.25 / 9),
        meals=meals, vegetarian=u["vegetarian"]
    ))

def _build_meals(vegetarian, protein, calories):
    if vegetarian:
        return [
            {"time":"7:30 AM","name":"Breakfast","items":["Paneer bhurji (100g)","2 whole wheat rotis","1 glass milk"],"calories":round(calories*0.25),"protein":round(protein*0.28)},
            {"time":"1:00 PM","name":"Lunch","items":["Dal (1 cup)","Brown rice (1 cup)","Curd (200g)","Salad"],"calories":round(calories*0.30),"protein":round(protein*0.28)},
            {"time":"4:00 PM","name":"Pre-workout snack","items":["Peanuts (30g)","Banana","Green tea"],"calories":round(calories*0.12),"protein":round(protein*0.10)},
            {"time":"7:00 PM","name":"Post-workout","items":["Soya chunks curry (100g)","2 rotis"],"calories":round(calories*0.25),"protein":round(protein*0.26)},
            {"time":"9:30 PM","name":"Dinner","items":["Moong dal soup","Mixed vegetable sabzi","1 roti"],"calories":round(calories*0.08),"protein":round(protein*0.08)},
        ]
    else:
        return [
            {"time":"7:30 AM","name":"Breakfast","items":["4 egg whites + 2 whole eggs","2 whole wheat rotis","1 glass milk"],"calories":round(calories*0.25),"protein":round(protein*0.30)},
            {"time":"1:00 PM","name":"Lunch","items":["Chicken breast 150g / Dal for veg","Brown rice (1 cup)","Salad","Curd"],"calories":round(calories*0.30),"protein":round(protein*0.30)},
            {"time":"4:00 PM","name":"Pre-workout snack","items":["Peanuts (30g)","Banana"],"calories":round(calories*0.10),"protein":round(protein*0.08)},
            {"time":"7:00 PM","name":"Post-workout","items":["Eggs (3 boiled)","Rice (1 cup)"],"calories":round(calories*0.25),"protein":round(protein*0.25)},
            {"time":"9:30 PM","name":"Dinner","items":["Dal / Chicken soup","2 rotis","Vegetables"],"calories":round(calories*0.10),"protein":round(protein*0.07)},
        ]
