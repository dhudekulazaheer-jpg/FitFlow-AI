
import json
import random
import re

from config import YOGA_FILE


class YogaGenerator:

    def __init__(self):
        self.yoga_data = self._load_data()

    def _load_data(self):
        with open(YOGA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    def _normalize(self, value):
        return str(value or "").strip().lower()

    def _clean_text(self, value):
        if not isinstance(value, str):
            return ""

        return re.sub(r"\s+", " ", value).strip()

    def _get_difficulty_rank(self, difficulty):
        levels = {
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3
        }

        return levels.get(self._normalize(difficulty), 3)

    def _goal_keywords(self, goal):
        goal_mapping = {
            "weight_loss": [
                "strength", "core", "legs", "full body",
                "standing yoga", "strengthening yoga"
            ],
            "muscle_building": [
                "strength", "core", "legs", "chest",
                "strengthening yoga"
            ],
            "flexibility": [
                "flexibility", "hamstrings", "hips", "spine",
                "forward bend yoga", "hip opening yoga"
            ],
            "general_fitness": [
                "full body", "strength", "balance", "core",
                "standing yoga"
            ]
        }

        return goal_mapping[goal]

    def _matches_goal(self, pose, keywords):
        searchable_values = [
            pose.get("focus", ""),
            pose.get("category", ""),
            *pose.get("categories", []),
            *pose.get("target_areas", [])
        ]

        searchable_text = " ".join(
            self._normalize(value)
            for value in searchable_values
        )

        return any(
            keyword in searchable_text
            for keyword in keywords
        )

    def _get_instructions(self, pose):
        instructions = pose.get("instruction_steps", {})

        if isinstance(instructions, dict):
            steps = instructions.get("en", [])

        elif isinstance(instructions, list):
            steps = instructions

        else:
            steps = []

        if isinstance(steps, str):
            steps = [steps]

        return [
            self._clean_text(step)
            for step in steps
            if self._clean_text(step)
        ]

    def _get_unique_poses(self, poses):
        unique_poses = []
        seen_names = set()

        for pose in poses:
            sanskrit_name = self._normalize(
                pose.get("sanskrit_name")
            )

            english_name = self._normalize(
                pose.get("name")
            )

            # Prefer Sanskrit name for duplicate detection.
            unique_key = sanskrit_name or english_name

            if not unique_key or unique_key in seen_names:
                continue

            seen_names.add(unique_key)
            unique_poses.append(pose)

        return unique_poses

    def generate_plan(
        self,
        goal="general_fitness",
        fitness_level="beginner",
        duration=15
    ):

        goal = self._normalize(goal)
        fitness_level = self._normalize(fitness_level)

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

        if duration not in [15, 30, 45, 60]:
            raise ValueError(
                "Duration must be 15, 30, 45, or 60 minutes."
            )

        requested_rank = self._get_difficulty_rank(
            fitness_level
        )

        # Filter poses according to fitness level.
        suitable_poses = [
            pose for pose in self.yoga_data
            if self._get_difficulty_rank(
                pose.get("difficulty")
            ) <= requested_rank
        ]

        # Filter poses according to fitness goal.
        keywords = self._goal_keywords(goal)

        matching_poses = [
            pose for pose in suitable_poses
            if self._matches_goal(pose, keywords)
        ]

        # Use other suitable poses if goal matches are limited.
        if len(matching_poses) < 3:
            matching_poses = suitable_poses

        # Prevent repeated Sanskrit pose names.
        unique_poses = self._get_unique_poses(
            matching_poses
        )

        if not unique_poses:
            return {
                "success": False,
                "message": "No suitable yoga poses found."
            }

        pose_count = {
            15: 4,
            30: 6,
            45: 8,
            60: 10
        }[duration]

        selected_poses = random.sample(
            unique_poses,
            min(pose_count, len(unique_poses))
        )

        # Divide the exact session duration into seconds.
        total_seconds = duration * 60
        base_seconds = total_seconds // len(selected_poses)
        extra_seconds = total_seconds % len(selected_poses)

        plan = []

        for index, pose in enumerate(selected_poses):

            pose_seconds = base_seconds

            if index < extra_seconds:
                pose_seconds += 1

            instructions = self._get_instructions(pose)

            description = self._clean_text(
                pose.get("description", "")
            )

            if not description:
                description = " ".join(instructions)

            plan.append({
                "sequence": index + 1,
                "name": self._clean_text(
                    pose.get("name", "Unknown pose")
                ),
                "sanskrit_name": self._clean_text(
                    pose.get("sanskrit_name", "")
                ),
                "difficulty": pose.get("difficulty", ""),
                "focus": pose.get("focus", ""),
                "duration_seconds": pose_seconds,
                "duration_minutes": round(
                    pose_seconds / 60, 2
                ),
                "instructions": instructions,
                "description": description,
                "image": pose.get("image", ""),
                "svg": pose.get("svg", "")
            })

        return {
            "success": True,
            "plan_type": "Yoga",
            "goal": goal,
            "fitness_level": fitness_level,
            "requested_duration_minutes": duration,
            "actual_duration_seconds": sum(
                pose["duration_seconds"] for pose in plan
            ),
            "actual_duration_minutes": duration,
            "total_poses": len(plan),
            "poses": plan,
            "note": (
                "This is a general exercise suggestion. "
                "Use comfortable movements and stop if you "
                "experience pain or discomfort."
            )
        }


if __name__ == "__main__":

    generator = YogaGenerator()

    result = generator.generate_plan(
        goal="flexibility",
        fitness_level="beginner",
        duration=15
    )

    print(json.dumps(
        result,
        indent=4,
        ensure_ascii=False
    ))
