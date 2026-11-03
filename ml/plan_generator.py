
import json

from ml.yoga_generator import YogaGenerator
from ml.workout_generator import WorkoutGenerator


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
        body_part=None
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

        # YOGA-ONLY PLAN
        if plan_type == "yoga":

            return self.yoga_generator.generate_plan(
                goal=goal,
                fitness_level=fitness_level,
                duration=duration
            )

        # WORKOUT-ONLY PLAN
        if plan_type == "workout":

            return self.workout_generator.generate_plan(
                goal=goal,
                fitness_level=fitness_level,
                duration=duration,
                equipment=equipment,
                body_part=body_part
            )

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

        # Return combined result
        return {
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
            "yoga_plan": yoga_plan,
            "workout_plan": workout_plan
        }


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
