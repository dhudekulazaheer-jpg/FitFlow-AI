"""
Progressive Overload & Difficulty Advisor Module for FitFlow AI
Tracks user session completions and delivers intelligent progressive overload
recommendations to prevent training plateaus and safely advance fitness levels.
"""

from models import PlanHistory, UserProfile, GeneratedPlan, db


def get_progression_advice(user_id):
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    history = PlanHistory.query.filter_by(user_id=user_id).all()
    plans = GeneratedPlan.query.filter_by(user_id=user_id).all()

    current_level = (profile.fitness_level if profile and profile.fitness_level else "beginner").lower().strip()
    completed_sessions = sum(1 for h in history if "Completed" in (h.activity or ""))

    # Progressive Overload Logic
    if current_level == "beginner":
        if completed_sessions >= 3:
            ready_to_advance = True
            recommended_level = "intermediate"
            title = "Progressive Overload Milestone: Ready for Intermediate!"
            message = (
                f"You have conquered {completed_sessions} workout & yoga sessions! "
                "Your neuromuscular foundation is solid. To stimulate continuous muscle adaptation "
                "and fat oxidation, progressive overload is essential."
            )
            cues = [
                "Increase resistance or dumbbell weight by 5% to 10%.",
                "Progress from Beginner to Intermediate routines for multi-joint compound movements.",
                "Shorten rest intervals between sets from 60s to 45s."
            ]
        else:
            ready_to_advance = False
            recommended_level = "beginner"
            sessions_needed = max(1, 3 - completed_sessions)
            title = "Foundation Phase: Building Movement Quality"
            message = (
                f"You have completed {completed_sessions} session(s). Complete {sessions_needed} more session(s) "
                "to unlock your automated level progression to Intermediate."
            )
            cues = [
                "Focus on slow 3-second eccentric (lowering) tempo on every rep.",
                "Prioritize full range of motion over speed.",
                "Maintain consistent nasal diaphragmatic breathing throughout sets."
            ]
    elif current_level == "intermediate":
        if completed_sessions >= 6:
            ready_to_advance = True
            recommended_level = "advanced"
            title = "Elite Performance Milestone: Ready for Advanced!"
            message = (
                f"Outstanding dedication with {completed_sessions} completed sessions! "
                "You are ready for Advanced protocols featuring high-density circuits and peak posture holds."
            )
            cues = [
                "Advance to Advanced routines to incorporate explosive plyometrics and deep poses.",
                "Add an extra working set to your primary compound movements.",
                "Incorporate paused reps (1-second static contraction at the bottom)."
            ]
        else:
            ready_to_advance = False
            recommended_level = "intermediate"
            sessions_needed = max(1, 6 - completed_sessions)
            title = "Hypertrophy & Endurance Consolidation"
            message = (
                f"Completed {completed_sessions} sessions at Intermediate level. Complete {sessions_needed} more "
                "to unlock automated advancement to Advanced."
            )
            cues = [
                "Push the last 2 reps of each set close to technical failure.",
                "Deepen yoga hold durations from 45s to 60s.",
                "Prioritize post-workout hydration and 20g+ recovery protein."
            ]
    else:  # advanced
        ready_to_advance = False
        recommended_level = "advanced"
        title = "Peak Athletic Mastery"
        message = (
            f"You are training at an Advanced level with {completed_sessions} completed sessions! "
            "Continue applying micro-progressions to optimize athletic conditioning."
        )
        cues = [
            "Periodize your training: Alternate high-intensity weeks with active recovery weeks.",
            "Integrate advanced breath retention (Kumbhaka) in yoga poses.",
            "Focus on rotational power and isometric core stability."
        ]

    return {
        "current_level": current_level,
        "completed_sessions": completed_sessions,
        "ready_to_advance": ready_to_advance,
        "recommended_level": recommended_level,
        "title": title,
        "message": message,
        "actionable_cues": cues
    }
