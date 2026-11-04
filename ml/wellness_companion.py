from datetime import datetime, timedelta
from models import GeneratedPlan, PlanHistory, db


def get_recovery_nutrition(weight_kg=70, duration_min=30, goal="general_fitness"):
    """
    Computes personalized post-workout recovery nutrition and hydration.
    """
    try:
        weight = float(weight_kg) if weight_kg else 70.0
    except (ValueError, TypeError):
        weight = 70.0

    try:
        duration = int(duration_min) if duration_min else 30
    except (ValueError, TypeError):
        duration = 30

    goal = str(goal).lower().strip()

    # Hydration: 12-15ml per minute of exercise + baseline recovery
    target_water_ml = round(duration * 14 + (weight * 3))

    # Protein: tailored to weight & goal
    if goal == "muscle_gain":
        target_protein_g = round(weight * 0.35, 1)  # ~25-30g
        carb_ratio = "2:1 (Carbs to Protein for glycogen synthesis)"
        snacks = [
            {"title": "Greek Yogurt & Berry Bowl", "detail": "1 cup whole Greek yogurt, chia seeds, sliced banana & honey."},
            {"title": "Whey / Plant Recovery Shake", "detail": "1 scoop protein, oat milk, 1 tbsp peanut butter & oats."},
            {"title": "Grilled Chicken & Sweet Potato", "detail": "Lean grilled chicken breast with steamed sweet potato cubes."}
        ]
    elif goal == "weight_loss":
        target_protein_g = round(weight * 0.28, 1)  # lean protein focus
        carb_ratio = "1:1 (Moderate carbs, high fiber to preserve satiety)"
        snacks = [
            {"title": "Boiled Eggs & Crisp Veggies", "detail": "2 boiled eggs with sliced cucumber, bell peppers & hummus."},
            {"title": "Cottage Cheese & Berries", "detail": "Low-fat cottage cheese with crushed walnuts & fresh raspberries."},
            {"title": "Green Protein Smoothie", "detail": "Spinach, unsweetened almond milk, protein powder & green apple."}
        ]
    elif goal == "flexibility":
        target_protein_g = round(weight * 0.22, 1)
        carb_ratio = "Anti-inflammatory & joint nourishing"
        snacks = [
            {"title": "Golden Turmeric Smoothie", "detail": "Almond milk, banana, turmeric pinch, cinnamon & plant protein."},
            {"title": "Avocado & Seed Toast", "detail": "Whole grain toast, smashed avocado, pumpkin seeds & sea salt."},
            {"title": "Coconut Water & Mixed Nuts", "detail": "Pure coconut water with a handful of raw almonds & walnuts."}
        ]
    else:  # general_fitness
        target_protein_g = round(weight * 0.25, 1)
        carb_ratio = "Balanced 2:1 recovery ratio"
        snacks = [
            {"title": "Banana & Almond Butter", "detail": "1 ripe banana with 2 tbsp raw almond butter."},
            {"title": "Hummus & Whole Grain Pita", "detail": "Warm whole wheat pita triangles with roasted garlic hummus."},
            {"title": "Fruit & Protein Shake", "detail": "Blend of mixed berries, Greek yogurt, and chilled water."}
        ]

    return {
        "target_water_ml": target_water_ml,
        "target_protein_g": target_protein_g,
        "carb_ratio": carb_ratio,
        "electrolyte_tip": "If sweating heavily, add a pinch of Himalayan salt or lemon to your water to replenish electrolytes.",
        "recommended_snacks": snacks
    }


def get_user_analytics(user_id):
    """
    Computes streaks, total calories burned, weekly frequency, and milestone badges.
    """
    plans = GeneratedPlan.query.filter_by(user_id=user_id).order_by(GeneratedPlan.generated_at.desc()).all()
    history = PlanHistory.query.filter_by(user_id=user_id).order_by(PlanHistory.created_at.desc()).all()

    total_plans = len(plans)
    completed_sessions = sum(1 for h in history if "Completed" in (h.activity or ""))

    # Calculate total estimated calories
    total_calories = 0
    for p in plans:
        p_json = p.get_plan_json()
        cal = 0
        if isinstance(p_json, dict):
            # Check workout predicted calories
            workout = p_json.get("workout") or p_json.get("workout_plan") or p_json
            if isinstance(workout, dict):
                cal += workout.get("predicted_calories_burned", 0) or 0
            yoga = p_json.get("yoga") or p_json.get("yoga_plan")
            if isinstance(yoga, dict):
                cal += (p.duration or 30) * 3.5  # standard MET yoga burn estimate
        total_calories += cal

    total_calories = round(total_calories)

    # Calculate streak (days with activity)
    active_dates = set()
    for h in history:
        if h.created_at:
            active_dates.add(h.created_at.date())

    streak = 0
    today = datetime.utcnow().date()
    check_date = today

    # If active today or yesterday, count streak backwards
    if today in active_dates:
        curr = today
    elif (today - timedelta(days=1)) in active_dates:
        curr = today - timedelta(days=1)
    else:
        curr = None

    while curr and curr in active_dates:
        streak += 1
        curr = curr - timedelta(days=1)

    # Weekly distribution (Mon - Sun counts over last 30 days)
    weekday_counts = {"Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0}
    day_abbrs = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cutoff = datetime.utcnow() - timedelta(days=30)
    for h in history:
        if h.created_at and h.created_at >= cutoff:
            weekday_counts[day_abbrs[h.created_at.weekday()]] += 1

    # Badges definition
    badges = [
        {
            "id": "first_step",
            "name": "First Step",
            "icon": "🌱",
            "description": "Generated your first fitness plan",
            "unlocked": total_plans >= 1
        },
        {
            "id": "consistency_starter",
            "name": "Consistency Starter",
            "icon": "🔥",
            "description": "Achieved a 3-day active streak",
            "unlocked": streak >= 3
        },
        {
            "id": "session_master",
            "name": "Session Finisher",
            "icon": "🏆",
            "description": "Completed an interactive routine",
            "unlocked": completed_sessions >= 1
        },
        {
            "id": "calorie_crusher",
            "name": "Calorie Crusher",
            "icon": "⚡",
            "description": "Burned over 500 estimated calories",
            "unlocked": total_calories >= 500
        },
        {
            "id": "holistic_athlete",
            "name": "Mind & Body Flow",
            "icon": "🧘",
            "description": "Generated both Yoga and Workout routines",
            "unlocked": any(p.plan_type in ("both", "yoga") for p in plans) and any(p.plan_type in ("both", "workout") for p in plans)
        }
    ]

    # Best streak calculation
    sorted_dates = sorted(active_dates)
    best_streak = 0
    temp_streak = 0
    prev_d = None
    for d in sorted_dates:
        if prev_d and d == prev_d + timedelta(days=1):
            temp_streak += 1
        else:
            temp_streak = 1
        if temp_streak > best_streak:
            best_streak = temp_streak
        prev_d = d
    if streak > best_streak:
        best_streak = streak

    return {
        "total_plans": total_plans,
        "completed_sessions": completed_sessions,
        "current_streak": streak,
        "best_streak": max(best_streak, streak),
        "active_dates": [d.isoformat() for d in sorted_dates],
        "total_calories_burned": total_calories,
        "weekly_activity": weekday_counts,
        "badges": badges
    }
