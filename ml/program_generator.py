"""
7-Day Structured Weekly Program Generator for FitFlow AI
Generates balanced, progressive multi-day fitness & yoga splits
tailored to user goals, fitness levels, equipment, and health constraints.
"""

from ml.plan_generator import PlanGenerator
from ml.warmup_cooldown import get_warmup_cooldown
from ml.wellness_companion import get_recovery_nutrition
from ml.health_safety import evaluate_health_safety


class WeeklyProgramGenerator:

    def __init__(self):
        self.plan_generator = PlanGenerator()

    def generate_program(
        self,
        goal="general_fitness",
        fitness_level="beginner",
        equipment="none",
        duration_per_session=30,
        health_assessment=None,
        age=None,
        weight_kg=70
    ):
        # Health safety check
        safety_eval = evaluate_health_safety(health_assessment)
        if safety_eval.get("paused") or not safety_eval.get("allowed", True):
            return {
                "success": False,
                "paused": True,
                "health_safety_paused": True,
                "error": safety_eval.get("message", "Routine generation paused for health safety."),
                "guidance": safety_eval.get("guidance", "Please seek clearance from a qualified healthcare professional.")
            }

        goal = str(goal).lower().strip()
        fitness_level = str(fitness_level).lower().strip()
        equipment = str(equipment).lower().strip()
        session_duration = duration_per_session if duration_per_session in [15, 30, 45, 60] else 30

        # Program Structure based on Goal
        if goal == "muscle_building":
            days_spec = [
                {"day": 1, "name": "Monday", "title": "Upper Body Strength (Chest & Arms)", "type": "workout", "body_part": "chest"},
                {"day": 2, "name": "Tuesday", "title": "Lower Body Power & Core", "type": "workout", "body_part": "upper legs"},
                {"day": 3, "name": "Wednesday", "title": "Vinyasa Mobility & Active Joint Flow", "type": "yoga", "body_part": None},
                {"day": 4, "name": "Thursday", "title": "Back & Postural Strength", "type": "workout", "body_part": "back"},
                {"day": 5, "name": "Friday", "title": "Full Body Functional Conditioning", "type": "both", "body_part": None},
                {"day": 6, "name": "Saturday", "title": "Restorative Yoga & Deep Fascial Release", "type": "yoga", "body_part": None},
                {"day": 7, "name": "Sunday", "title": "Full Muscular Recovery & Nutrition Reset", "type": "rest", "body_part": None}
            ]
        elif goal == "weight_loss":
            days_spec = [
                {"day": 1, "name": "Monday", "title": "High Energy Metabolic Conditioning", "type": "workout", "body_part": "waist"},
                {"day": 2, "name": "Tuesday", "title": "Power Yoga Flow & Core Heat", "type": "yoga", "body_part": None},
                {"day": 3, "name": "Wednesday", "title": "Lower Body Calorie Burn & Endurance", "type": "workout", "body_part": "upper legs"},
                {"day": 4, "name": "Thursday", "title": "Active Recovery Walk & Gentle Mobility", "type": "rest", "body_part": None},
                {"day": 5, "name": "Friday", "title": "Total Body Dynamic Flow & Tone", "type": "both", "body_part": None},
                {"day": 6, "name": "Saturday", "title": "Hatha Balance & Flexibility", "type": "yoga", "body_part": None},
                {"day": 7, "name": "Sunday", "title": "Cellular Rest & Hydration Protocol", "type": "rest", "body_part": None}
            ]
        elif goal == "flexibility":
            days_spec = [
                {"day": 1, "name": "Monday", "title": "Hamstring & Hip Mobility Vinyasa", "type": "yoga", "body_part": None},
                {"day": 2, "name": "Tuesday", "title": "Spinal Alignment & Gentle Core Strength", "type": "both", "body_part": "waist"},
                {"day": 3, "name": "Wednesday", "title": "Shoulder, Neck & Chest Opening Flow", "type": "yoga", "body_part": None},
                {"day": 4, "name": "Thursday", "title": "Gentle Lower Body Activation & Glute Health", "type": "workout", "body_part": "upper legs"},
                {"day": 5, "name": "Friday", "title": "Deep Yin Yoga & Fascial Decompression", "type": "yoga", "body_part": None},
                {"day": 6, "name": "Saturday", "title": "Full Body Balance & Joint Circulation", "type": "yoga", "body_part": None},
                {"day": 7, "name": "Sunday", "title": "Meditation, Rest & Lymphatic Recovery", "type": "rest", "body_part": None}
            ]
        else:  # general_fitness
            days_spec = [
                {"day": 1, "name": "Monday", "title": "Upper Body Strength & Tone", "type": "workout", "body_part": "chest"},
                {"day": 2, "name": "Tuesday", "title": "Vinyasa Flow & Dynamic Core", "type": "yoga", "body_part": None},
                {"day": 3, "name": "Wednesday", "title": "Lower Body Stability & Calves", "type": "workout", "body_part": "lower legs"},
                {"day": 4, "name": "Thursday", "title": "Active Rest & Diaphragmatic Breathwork", "type": "rest", "body_part": None},
                {"day": 5, "name": "Friday", "title": "Combined Flow & Cardio Conditioning", "type": "both", "body_part": None},
                {"day": 6, "name": "Saturday", "title": "Restorative Yoga & Postural Reset", "type": "yoga", "body_part": None},
                {"day": 7, "name": "Sunday", "title": "Nutrient Replenishment & Mental Ease", "type": "rest", "body_part": None}
            ]

        schedule = []
        for spec in days_spec:
            if spec["type"] == "rest":
                schedule.append({
                    "day": spec["day"],
                    "day_name": spec["name"],
                    "focus_title": spec["title"],
                    "is_rest_day": True,
                    "plan_type": "Rest & Recovery",
                    "routine_summary": "Active rest day: 20-30 minute gentle walk, light stretching, and optimal hydration.",
                    "recovery_guidance": "Rest days allow myofibrillar repair and glycogen replenishment, preventing overtraining."
                })
            else:
                day_plan = self.plan_generator.generate_plan(
                    plan_type=spec["type"],
                    goal=goal,
                    fitness_level=fitness_level,
                    duration=session_duration,
                    equipment=equipment,
                    body_part=spec["body_part"],
                    age=age,
                    health_assessment=health_assessment
                )

                # Add Warm-up and Cool-down protocols
                warmup_cooldown = get_warmup_cooldown(
                    body_part=spec["body_part"],
                    is_yoga=(spec["type"] == "yoga"),
                    goal=goal
                )

                # Add Recovery Nutrition
                nutrition = get_recovery_nutrition(
                    weight_kg=weight_kg,
                    duration_min=session_duration,
                    goal=goal
                )

                schedule.append({
                    "day": spec["day"],
                    "day_name": spec["name"],
                    "focus_title": spec["title"],
                    "is_rest_day": False,
                    "plan_type": spec["type"],
                    "duration_minutes": session_duration,
                    "routine": day_plan,
                    "warmup": warmup_cooldown["warmup"],
                    "cooldown": warmup_cooldown["cooldown"],
                    "recovery_nutrition": nutrition
                })

        return {
            "success": True,
            "program_type": "7-Day Weekly Program",
            "goal": goal,
            "fitness_level": fitness_level,
            "equipment": equipment,
            "duration_per_session": session_duration,
            "schedule": schedule,
            "safety_warnings": safety_eval.get("warnings", []),
            "disclaimer": "This weekly program is for general fitness guidance. Listen to your body and adjust intensity as needed."
        }
