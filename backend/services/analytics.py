from sqlalchemy.orm import Session
from backend.database.models import WorkoutSession, WorkoutSet, ProgressSnapshot, User
from datetime import date, timedelta
import json

def get_progress_analytics(db: Session, user_id: str) -> dict:
    """Generate comprehensive progress analytics for a user."""
    user = db.query(User).filter(User.id == user_id).first()
    snapshots = (db.query(ProgressSnapshot)
                 .filter(ProgressSnapshot.user_id == user_id)
                 .order_by(ProgressSnapshot.week_start).all())
    
    sessions = (db.query(WorkoutSession)
                .filter(WorkoutSession.user_id == user_id)
                .order_by(WorkoutSession.date).all())
    
    # Consistency
    total_planned = sum(s.sessions_planned for s in snapshots) if snapshots else 0
    total_completed = sum(s.sessions_completed for s in snapshots) if snapshots else 0
    consistency_pct = round((total_completed / total_planned * 100) if total_planned > 0 else 0, 1)
    
    # Strength trend
    strength_data = [{"week": str(s.week_start), "index": round(s.strength_index, 1)} for s in snapshots]
    strength_change = 0
    if len(snapshots) >= 2:
        first_s = snapshots[0].strength_index
        last_s  = snapshots[-1].strength_index
        strength_change = round(((last_s - first_s) / first_s) * 100, 1) if first_s else 0
    
    # Volume trend
    volume_data = [{"week": str(s.week_start), "volume": int(s.total_volume_kg)} for s in snapshots]
    
    # Body weight trend
    weight_data = [{"week": str(s.week_start), "weight": round(s.body_weight_kg, 1)} for s in snapshots]
    
    # Session heatmap (last 8 weeks)
    eight_weeks_ago = date.today() - timedelta(weeks=8)
    recent_sessions = [s for s in sessions if s.date and s.date >= eight_weeks_ago]
    session_map = {str(s.date): s.status for s in recent_sessions}
    
    # Generate insights
    insights = _generate_insights(consistency_pct, strength_change, snapshots, user)
    
    return {
        "user_name": user.name if user else "User",
        "consistency_pct": consistency_pct,
        "total_sessions_completed": total_completed,
        "strength_change_pct": strength_change,
        "strength_data": strength_data,
        "volume_data": volume_data,
        "weight_data": weight_data,
        "session_heatmap": session_map,
        "insights": insights,
        "current_streak": _calculate_streak(sessions),
    }

def _calculate_streak(sessions) -> int:
    streak = 0
    for s in reversed(sessions):
        if s.status == "completed":
            streak += 1
        elif s.status == "skipped":
            break
    return streak

def _generate_insights(consistency_pct, strength_change, snapshots, user) -> list:
    insights = []
    
    if strength_change > 0:
        insights.append({
            "type": "positive",
            "icon": "💪",
            "text": f"Your strength index increased by {strength_change}% — that's real progress!"
        })
    elif strength_change < -5:
        insights.append({
            "type": "neutral",
            "icon": "📊",
            "text": "Strength dipped slightly — happens to everyone. Let's refocus this week."
        })
    
    if consistency_pct >= 85:
        insights.append({"type":"positive","icon":"🔥","text":f"You hit {consistency_pct}% of planned sessions. Elite consistency!"})
    elif consistency_pct >= 70:
        insights.append({"type":"positive","icon":"✅","text":f"{consistency_pct}% session completion — solid work. Aim for 85% this week."})
    else:
        missed = round((1 - consistency_pct/100) * sum(s.sessions_planned for s in snapshots))
        insights.append({"type":"neutral","icon":"📅","text":f"Missed {missed} sessions recently. Let's rebuild the habit — 3 this week is enough."})
    
    if snapshots and len(snapshots) >= 2:
        w_change = snapshots[-1].body_weight_kg - snapshots[0].body_weight_kg
        goal = user.goal if user else "maintain"
        if goal == "muscle_gain" and w_change > 0:
            insights.append({"type":"positive","icon":"📈","text":f"Weight up {round(w_change, 1)}kg since you started. Muscle-building is working!"})
        elif goal == "fat_loss" and w_change < 0:
            insights.append({"type":"positive","icon":"📉","text":f"Down {round(abs(w_change), 1)}kg since you started. Keep the deficit sustainable."})
    
    if not insights:
        insights.append({"type":"neutral","icon":"🎯","text":"Keep showing up consistently — results compound over time."})
    
    return insights
