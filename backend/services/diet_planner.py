import math
from sqlalchemy.orm import Session
from backend.database.models import User, DietPlan
import uuid
from datetime import datetime

def calculate_macros(user: User) -> dict:
    """Calculate TDEE and macro targets."""
    # Harris-Benedict BMR
    if user.weight_kg and user.height_cm and user.age:
        bmr = 10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age + 5
    else:
        bmr = 1800

    activity_multiplier = {3: 1.375, 4: 1.55, 5: 1.725, 6: 1.9}.get(user.days_per_week, 1.55)
    tdee = bmr * activity_multiplier

    goal_adjustments = {"muscle_gain": 300, "fat_loss": -500, "maintain": 0, "strength": 200, "tone": -200}
    calories = round(tdee + goal_adjustments.get(user.goal, 0))
    
    protein_per_kg = 2.0 if user.goal in ["muscle_gain","strength"] else 1.8
    protein_g = round(user.weight_kg * protein_per_kg)
    fats_g    = round(calories * 0.25 / 9)
    carbs_g   = round((calories - protein_g * 4 - fats_g * 9) / 4)
    
    return {"calories": calories, "protein_g": protein_g, "carbs_g": carbs_g, "fats_g": fats_g}

def build_meal_plan(user: User, macros: dict) -> list:
    cal = macros["calories"]
    prot = macros["protein_g"]
    veg = user.vegetarian

    if veg:
        return [
            {"time":"7:30 AM","name":"Breakfast","emoji":"🌅",
             "items":["Paneer bhurji (100g)","2 whole wheat rotis","1 glass milk (250ml)","1 banana"],
             "calories":round(cal*0.25),"protein":round(prot*0.27),
             "prep":"Scramble paneer with onions, tomatoes, cumin. Pair with warm rotis."},
            {"time":"10:30 AM","name":"Mid-morning snack","emoji":"🥜",
             "items":["Roasted peanuts (40g)","Green tea"],
             "calories":round(cal*0.08),"protein":round(prot*0.08),
             "prep":"A handful of peanuts — great protein and healthy fats."},
            {"time":"1:00 PM","name":"Lunch","emoji":"☀️",
             "items":["Dal (1 cup cooked)","Brown rice (1 cup)","Curd / raita (200g)","Mixed vegetable sabzi","Salad"],
             "calories":round(cal*0.30),"protein":round(prot*0.28),
             "prep":"Dal + rice = complete protein. Curd adds probiotics and extra protein."},
            {"time":"4:30 PM","name":"Pre-workout","emoji":"⚡",
             "items":["Soya chunks (50g dry)","Banana","1 glass milk"],
             "calories":round(cal*0.15),"protein":round(prot*0.18),
             "prep":"Eat 60-90 min before training. Soya is a complete plant protein."},
            {"time":"8:00 PM","name":"Post-workout dinner","emoji":"🌙",
             "items":["Moong dal (1 cup)","2 wheat rotis","Paneer (50g) OR tofu","Sautéed vegetables"],
             "calories":round(cal*0.18),"protein":round(prot*0.15),
             "prep":"Light dinner to support recovery overnight."},
            {"time":"10:00 PM","name":"Before bed","emoji":"😴",
             "items":["1 glass warm milk","2 almonds"],
             "calories":round(cal*0.04),"protein":round(prot*0.04),
             "prep":"Casein-like protein from milk supports overnight muscle repair."},
        ]
    else:
        return [
            {"time":"7:30 AM","name":"Breakfast","emoji":"🌅",
             "items":["4 egg whites + 2 whole eggs (scrambled)","2 whole wheat rotis","1 glass milk (250ml)","1 banana"],
             "calories":round(cal*0.25),"protein":round(prot*0.28),
             "prep":"High-protein start. Eggs provide all 9 essential amino acids."},
            {"time":"10:30 AM","name":"Mid-morning snack","emoji":"🥜",
             "items":["Boiled eggs (2)","Roasted peanuts (20g)"],
             "calories":round(cal*0.09),"protein":round(prot*0.10),
             "prep":"Quick protein boost to keep hunger at bay."},
            {"time":"1:00 PM","name":"Lunch","emoji":"☀️",
             "items":["Chicken breast 150g / Dal (veg option)","Brown rice (1 cup)","Salad","Curd (150g)"],
             "calories":round(cal*0.30),"protein":round(prot*0.28),
             "prep":"Lean protein + complex carbs for sustained energy."},
            {"time":"4:30 PM","name":"Pre-workout","emoji":"⚡",
             "items":["Banana","Peanuts (20g)","1 boiled egg"],
             "calories":round(cal*0.10),"protein":round(prot*0.09),
             "prep":"Light, fast-digesting — eat 60 min before training."},
            {"time":"8:00 PM","name":"Post-workout dinner","emoji":"🌙",
             "items":["Eggs (3 boiled) OR chicken 100g","Brown rice / 2 rotis","Dal OR vegetables"],
             "calories":round(cal*0.22),"protein":round(prot*0.22),
             "prep":"Critical recovery window. High protein dinner for muscle synthesis."},
            {"time":"10:00 PM","name":"Before bed","emoji":"😴",
             "items":["1 glass warm milk","2 almonds"],
             "calories":round(cal*0.04),"protein":round(prot*0.03),
             "prep":"Slow-digesting protein for overnight recovery."},
        ]

def get_or_create_diet_plan(db: Session, user_id: str) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    existing = db.query(DietPlan).filter(DietPlan.user_id == user_id).order_by(DietPlan.generated_at.desc()).first()
    if existing:
        return {
            "calories_target": existing.calories_target,
            "protein_target_g": existing.protein_target_g,
            "carbs_target_g": existing.carbs_target_g,
            "fats_target_g": existing.fats_target_g,
            "meals": existing.meals,
            "vegetarian": existing.vegetarian,
            "goal": user.goal
        }
    return regenerate_diet_plan(db, user_id)

def regenerate_diet_plan(db: Session, user_id: str) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    macros = calculate_macros(user)
    meals = build_meal_plan(user, macros)
    plan = DietPlan(
        id=str(uuid.uuid4()), user_id=user_id,
        calories_target=macros["calories"], protein_target_g=macros["protein_g"],
        carbs_target_g=macros["carbs_g"], fats_target_g=macros["fats_g"],
        meals=meals, vegetarian=user.vegetarian, generated_at=datetime.utcnow()
    )
    db.add(plan)
    db.commit()
    return {"calories_target":macros["calories"],"protein_target_g":macros["protein_g"],
            "carbs_target_g":macros["carbs_g"],"fats_target_g":macros["fats_g"],
            "meals":meals,"vegetarian":user.vegetarian,"goal":user.goal}
