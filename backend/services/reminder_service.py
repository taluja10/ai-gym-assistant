from apscheduler.schedulers.background import BackgroundScheduler
import random, logging
from datetime import datetime

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

WORKOUT_REMINDERS = [
    "Time to hit the gym! Today's session is waiting — consistency beats perfection every time.",
    "Your future self thanks you for going today. Let's make it happen!",
    "Skipping is easy. Showing up is what separates the good from the great.",
    "Muscles don't build themselves — but you've been building yours consistently. Keep going!",
    "One hour of training for a lifetime of results. You've got this.",
]

REST_REMINDERS = [
    "Rest day! Your body is rebuilding right now — this is part of the process.",
    "Recovery day — stretch, hydrate, and let your muscles grow.",
    "Active recovery today: a short walk or light stretching goes a long way.",
]

MOTIVATION_POOL = [
    "Consistency matters more than perfection.",
    "The only bad workout is the one that didn't happen.",
    "Progress is slow but it's always happening. Trust the process.",
    "You're stronger than you were last month. That's all that matters.",
    "Small daily improvements lead to stunning yearly results.",
]

def get_daily_reminder(user_name: str, is_rest_day: bool = False) -> dict:
    first_name = user_name.split()[0]
    if is_rest_day:
        msg = random.choice(REST_REMINDERS)
    else:
        msg = random.choice(WORKOUT_REMINDERS)
    motivation = random.choice(MOTIVATION_POOL)
    return {
        "greeting": f"Good morning, {first_name}! 💪",
        "message": msg,
        "motivation": motivation,
        "timestamp": datetime.now().isoformat()
    }

def _daily_check_job():
    """Runs daily — logs reminders (in prod, would send push/email)."""
    logger.info(f"[Scheduler] Daily reminder check at {datetime.now().strftime('%H:%M')}")

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(_daily_check_job, "cron", hour=8, minute=0, id="daily_reminder")
        scheduler.start()
        logger.info("APScheduler started — daily reminders active at 08:00")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
