import re
import json
import random

from config import EXERCISEDB_FILE


class WorkoutGenerator:

    # Basic equipment available in the user's plan.
    EQUIPMENT_OPTIONS = {
        "none": ["body weight"],
        "basic": [
            "body weight",
            "dumbbell",
            "band",
            "resistance band"
        ],
        "full_gym": None
    }

    # Equipment that should not be assumed available
    # in a basic or no-equipment workout.
    EXTRA_EQUIPMENT_TERMS = [
        "exercise ball",
        "stability ball",
        "swiss ball",
        "bosu ball",
        "medicine ball",
        "bench",
        "cable machine",
        "leverage machine",
        "smith machine",
        "barbell",
        "kettlebell",
        "sled machine",
        "stationary bike",
        "elliptical machine",
        "suspension trainer",
    ]
    BEGINNER_ALLOWED_EXERCISE_IDS = {
    "0659",  # Wall push-up

    # Upper-leg flexibility
    "1512",  # All fours squad stretch
    "1511",  # Hamstring stretch
    "1576",  # Leg up hamstring stretch
    "0613",  # Lying side quads stretch
    "1424",  # Seated glute stretch
    "2567",  # Seated piriformis stretch
    "1585",  # Runners stretch

    # Lower-leg flexibility
    "1368",  # Ankle circles
    "1377",  # Calf stretch with hands against wall
    "1390",  # Seated calf stretch

    # Back flexibility
    "1405",  # Back pec stretch
    "1346",  # Kneeling lat stretch
    "0690",  # Seated lower back stretch
    "1358",  # Side lying floor stretch
    "1362",  # Sphinx
    "1363",  # Spine stretch
    "1365",  # Upper back stretch

    # Shoulder flexibility
    "0669",  # Rear deltoid stretch
}

    BEGINNER_EXCLUSION_TERMS = [
        "one arm push up",
        "single arm push up",
        "archer push up",
        "clap push up",
        "shoulder tap",
        "hindu push up",
        "chest dip",
        "straight bar dip",
        "parallel bar dip",
        "handstand",
        "planche",
        "muscle up",
        "pistol squat",
        "plyo",
        "superman push up",
        "clock push up",
        "decline push up",
        "push up (wall) v. 2",
        "dynamic chest stretch",
        "chest stretch",
    ]

    def __init__(self):
        self.exercise_data = self._load_data()

    def _load_data(self):
        with open(EXERCISEDB_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    def _normalize(self, value):
        return str(value or "").strip().lower()

    def _clean_text(self, value):
        if not isinstance(value, str):
            return ""
        return " ".join(value.split())

    def _get_instructions(self, exercise):
        instructions = exercise.get("instructions", {})

        if isinstance(instructions, dict):
            text = instructions.get("en", "")
        elif isinstance(instructions, str):
            text = instructions
        else:
            text = ""

        if isinstance(text, list):
            return [
                self._clean_text(step)
                for step in text
                if self._clean_text(step)
            ]

        cleaned = self._clean_text(text)
        return [cleaned] if cleaned else []

    def _has_unavailable_equipment(self, exercise):
        name = self._normalize(exercise.get("name"))

        instructions = " ".join(
            self._get_instructions(exercise)
        ).lower()

        searchable_text = f"{name} {instructions}"

        return any(
            term in searchable_text
            for term in self.EXTRA_EQUIPMENT_TERMS
        )

    def _is_beginner_suitable_by_name(self, exercise_name):
        normalized_name = re.sub(
            r"[-_]+", " ", exercise_name.lower()
        )

        return not any(
            term in normalized_name
            for term in self.BEGINNER_EXCLUSION_TERMS
        )

    def _goal_body_parts(self, goal):
        goals = {
            "weight_loss": [
                "cardio", "waist", "upper legs", "lower legs"
            ],
            "muscle_building": [
                "chest", "back", "upper arms", "shoulders",
                "upper legs", "lower arms", "lower legs"
            ],
            "flexibility": [
                "upper legs", "lower legs", "back", "shoulders"
            ],
            "general_fitness": [
                "chest", "back", "waist", "upper arms",
                "upper legs", "shoulders", "cardio"
            ]
        }

        return goals[goal]

    def _get_training_volume(self, fitness_level, goal):
        settings = {
            "beginner": {
                "sets": 2,
                "reps": "8-10",
                "rest_seconds": 60
            },
            "intermediate": {
                "sets": 3,
                "reps": "10-12",
                "rest_seconds": 45
            },
            "advanced": {
                "sets": 4,
                "reps": "10-15",
                "rest_seconds": 30
            }
        }

        result = settings[fitness_level].copy()

        if goal == "weight_loss":
            result["reps"] = {
                "beginner": "10-12",
                "intermediate": "12-15",
                "advanced": "15-20"
            }[fitness_level]

        return result

    def generate_plan(
        self,
        goal="general_fitness",
        fitness_level="beginner",
        duration=15,
        equipment="none",
        body_part=None
    ):

        goal = self._normalize(goal)
        fitness_level = self._normalize(fitness_level)
        equipment = self._normalize(equipment)

        valid_goals = [
            "weight_loss",
            "muscle_building",
            "flexibility",
            "general_fitness"
        ]

        valid_levels = [
            "beginner",
            "intermediate",
            "advanced"
        ]

        if goal not in valid_goals:
            raise ValueError("Invalid fitness goal.")

        if fitness_level not in valid_levels:
            raise ValueError("Invalid fitness level.")

        if equipment not in self.EQUIPMENT_OPTIONS:
            raise ValueError(
                "Equipment must be none, basic, or full_gym."
            )

        if duration not in [15, 30, 45, 60]:
            raise ValueError(
                "Duration must be 15, 30, 45, or 60 minutes."
            )

        if body_part:
            body_part = self._normalize(body_part)

            valid_body_parts = {
                self._normalize(item.get("body_part"))
                for item in self.exercise_data
            }

            if body_part not in valid_body_parts:
                raise ValueError("Invalid target body part.")

        allowed_equipment = self.EQUIPMENT_OPTIONS[equipment]

        suitable_exercises = []

        for exercise in self.exercise_data:

            exercise_equipment = self._normalize(
                exercise.get("equipment")
            )

            # Apply equipment filter.
            if (
                allowed_equipment is not None
                and exercise_equipment not in allowed_equipment
            ):
                continue

            # Reject exercises requiring unavailable equipment.
            if (
                equipment in ["none", "basic"]
                and self._has_unavailable_equipment(exercise)
            ):
                continue

            # Beginner allowlist: only reviewed exercises.
            if fitness_level == "beginner":
                exercise_id = str(exercise.get("id", ""))

                if exercise_id not in self.BEGINNER_ALLOWED_EXERCISE_IDS:
                    continue

            suitable_exercises.append(exercise)

        # Apply target body-part filter.
        if body_part:
            suitable_exercises = [
                exercise
                for exercise in suitable_exercises
                if self._normalize(
                    exercise.get("body_part")
                ) == body_part
            ]

        else:
            target_parts = self._goal_body_parts(goal)

            suitable_exercises = [
                exercise
                for exercise in suitable_exercises
                if self._normalize(
                    exercise.get("body_part")
                ) in target_parts
            ]

        # Avoid repeated exercise names.
        unique_exercises = []
        seen_names = set()

        for exercise in suitable_exercises:
            name = self._normalize(exercise.get("name"))

            if name and name not in seen_names:
                seen_names.add(name)
                unique_exercises.append(exercise)

        if not unique_exercises:
            return {
                "success": False,
                "message": (
                    "No exercises match the selected filters. "
                    "Try another body part or equipment option."
                )
            }

        exercise_count = {
            15: 4,
            30: 6,
            45: 8,
            60: 10
        }[duration]

        selected_exercises = random.sample(
            unique_exercises,
            min(exercise_count, len(unique_exercises))
        )

        volume = self._get_training_volume(
            fitness_level,
            goal
        )

        total_seconds = duration * 60
        base_seconds = total_seconds // len(selected_exercises)
        extra_seconds = total_seconds % len(selected_exercises)

        plan = []

        for index, exercise in enumerate(selected_exercises):

            slot_seconds = base_seconds

            if index < extra_seconds:
                slot_seconds += 1

            plan.append({
                "sequence": index + 1,
                "id": exercise.get("id"),
                "name": self._clean_text(
                    exercise.get("name", "Unknown exercise")
                ),
                "body_part": exercise.get("body_part", ""),
                "muscle_group": exercise.get("muscle_group", ""),
                "equipment": exercise.get("equipment", ""),
                "sets": volume["sets"],
                "reps": volume["reps"],
                "rest_seconds": volume["rest_seconds"],
                "allocated_time_seconds": slot_seconds,
                "instructions": self._get_instructions(exercise),
                "image": exercise.get("image", ""),
                "gif_url": exercise.get("gif_url", "")
            })

        return {
            "success": True,
            "plan_type": "Workout",
            "goal": goal,
            "fitness_level": fitness_level,
            "equipment": equipment,
            "target_body_part": body_part or "Goal-based selection",
            "requested_duration_minutes": duration,
            "allocated_duration_seconds": sum(
                item["allocated_time_seconds"] for item in plan
            ),
            "total_exercises": len(plan),
            "training_volume": volume,
            "exercises": plan,
            "note": (
                "ExerciseDB does not provide difficulty labels. "
                "Beginner exclusions are based on exercise names "
                "and are not a complete safety assessment. "
                "Allocated time is a planning estimate, not a "
                "verified exercise duration."
            )
        }


if __name__ == "__main__":

    generator = WorkoutGenerator()

    result = generator.generate_plan(
        goal="muscle_building",
        fitness_level="beginner",
        duration=15,
        equipment="basic",
        body_part="chest"
    )

    print(json.dumps(
        result,
        indent=4,
        ensure_ascii=False
    ))
