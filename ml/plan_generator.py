import json

from ml.yoga_generator import YogaGenerator
from ml.workout_generator import WorkoutGenerator
from ml.health_safety import evaluate_health_safety
from ml.warmup_cooldown import get_warmup_cooldown


class PlanGenerator:

    def __init__(self):
        self.yoga_generator = YogaGenerator()
        self.workout_generator = WorkoutGenerator()

    def generate_plan(
        self,
        plan_type="both",
        goal="general_fitness",
        fitness_level="beginner",
        duration=30,
        equipment="none",
        body_part=None,
        age=None,
        health_assessment=None,
        **kwargs
    ):

        plan_type = str(plan_type).lower().strip()

        if plan_type not in ["yoga", "workout", "both"]:
            return {
                "success": False,
                "message": "Invalid plan type. Choose yoga, workout, or both."
            }

        if duration not in [15, 30, 45, 60]:
            return {
                "success": False,
                "message": "Choose a duration of 15, 30, 45 or 60 minutes."
            }

        # -------------------------------------------------------------
        # HEALTH & SAFETY EVALUATION
        # -------------------------------------------------------------
        safety_eval = evaluate_health_safety(health_assessment)
        if safety_eval.get("paused") or not safety_eval.get("allowed", True):
            return {
                "success": False,
                "paused": True,
                "health_safety_paused": True,
                "message": safety_eval.get("message") or "Plan generation paused for health safety reasons.",
                "safety_warnings": safety_eval.get("warnings", []),
                "disclaimer": safety_eval.get("disclaimer", "")
            }

        safety_warnings = safety_eval.get("warnings", [])
        disclaimer = safety_eval.get("disclaimer", "")

        # YOGA-ONLY PLAN
        if plan_type == "yoga":
            res = self.yoga_generator.generate_plan(
                goal=goal,
                fitness_level=fitness_level,
                duration=duration
            )
            if isinstance(res, dict) and res.get("success", False):
                res["safety_warnings"] = safety_warnings
                res["disclaimer"] = disclaimer
                wc = get_warmup_cooldown(body_part=None, is_yoga=True, goal=goal)
                res["warmup"] = wc["warmup"]
                res["cooldown"] = wc["cooldown"]
                if age is not None:
                    res["user_age"] = age
            return res

        # WORKOUT-ONLY PLAN
        if plan_type == "workout":
            res = self.workout_generator.generate_plan(
                goal=goal,
                fitness_level=fitness_level,
                duration=duration,
                equipment=equipment,
                body_part=body_part
            )
            if isinstance(res, dict) and res.get("success", False):
                res["safety_warnings"] = safety_warnings
                res["disclaimer"] = disclaimer
                wc = get_warmup_cooldown(body_part=body_part, is_yoga=False, goal=goal)
                res["warmup"] = wc["warmup"]
                res["cooldown"] = wc["cooldown"]
                if age is not None:
                    res["user_age"] = age
            return res

        # COMBINED YOGA + WORKOUT PLAN
        if duration == 15:
            return {
                "success": False,
                "message": (
                    "Combined Yoga and Workout plans "
                    "require at least 30 minutes."
                )
            }

        if duration == 30:
            yoga_duration = 15
            workout_duration = 15
        elif duration == 45:
            yoga_duration = 15
            workout_duration = 30
        else:  # 60 minutes
            yoga_duration = 30
            workout_duration = 30

        # Generate Yoga plan
        yoga_plan = self.yoga_generator.generate_plan(
            goal=goal,
            fitness_level=fitness_level,
            duration=yoga_duration
        )

        if not yoga_plan.get("success", False):
            return {
                "success": False,
                "message": "Yoga plan generation failed.",
                "details": yoga_plan
            }

        # Generate Workout plan
        workout_plan = self.workout_generator.generate_plan(
            goal=goal,
            fitness_level=fitness_level,
            duration=workout_duration,
            equipment=equipment,
            body_part=body_part
        )

        if not workout_plan.get("success", False):
            return {
                "success": False,
                "message": "Workout plan generation failed.",
                "details": workout_plan
            }

        # Return combined result with both yoga/workout and yoga_plan/workout_plan for 100% compatibility
        combined_result = {
            "success": True,
            "plan_type": "Combined",
            "goal": goal,
            "fitness_level": fitness_level,
            "requested_duration_minutes": duration,
            "allocated_duration_minutes": (
                yoga_duration + workout_duration
            ),
            "yoga_duration_minutes": yoga_duration,
            "workout_duration_minutes": workout_duration,
            "yoga": yoga_plan,
            "yoga_plan": yoga_plan,
            "workout": workout_plan,
            "workout_plan": workout_plan,
            "safety_warnings": safety_warnings,
            "disclaimer": disclaimer
        }
        if age is not None:
            combined_result["user_age"] = age

        wc = get_warmup_cooldown(body_part=body_part, is_yoga=False, goal=goal)
        combined_result["warmup"] = wc["warmup"]
        combined_result["cooldown"] = wc["cooldown"]

        return combined_result


if __name__ == "__main__":

    generator = PlanGenerator()

    result = generator.generate_plan(
        plan_type="both",
        goal="flexibility",
        fitness_level="beginner",
        duration=30,
        equipment="basic",
        body_part=None
    )

    print(json.dumps(
        result,
        indent=4,
        ensure_ascii=False
    ))
