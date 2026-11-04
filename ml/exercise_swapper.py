import json
import random
from pathlib import Path
from config import YOGA_FILE, EXERCISEDB_FILE


class ExerciseSwapper:
    """Provides smart alternative exercises and yoga poses matching category and targets."""

    def __init__(self):
        self.yoga_data = self._load_json(YOGA_FILE)
        self.workout_data = self._load_json(EXERCISEDB_FILE)

    def _load_json(self, path):
        try:
            if Path(path).exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def get_yoga_alternative(self, current_name, category=None):
        """Finds a different yoga pose, prioritizing same category or general poses."""
        if not self.yoga_data:
            return None

        current_lower = str(current_name).strip().lower()

        # Try to find poses in the same category
        candidates = []
        if category:
            cat_lower = str(category).strip().lower()
            candidates = [
                p for p in self.yoga_data
                if str(p.get("category_name", "")).strip().lower() == cat_lower
                and str(p.get("english_name", "")).strip().lower() != current_lower
            ]

        # If not enough, pick any pose that is not current
        if not candidates:
            candidates = [
                p for p in self.yoga_data
                if str(p.get("english_name", "")).strip().lower() != current_lower
            ]

        if not candidates:
            return None

        chosen = random.choice(candidates)
        return {
            "name": chosen.get("english_name", "Alternative Pose"),
            "sanskrit_name": chosen.get("sanskrit_name_adapted", ""),
            "category": chosen.get("category_name", "Yoga"),
            "target": chosen.get("category_name", "Flexibility"),
            "duration": "1-2 minutes",
            "instructions": chosen.get("pose_description", "Hold pose steadily while maintaining calm, deep diaphragmatic breathing.")
        }

    def get_workout_alternative(self, current_name, body_part=None, target_muscle=None, equipment="none"):
        """Finds an alternative workout exercise matching target body part / equipment."""
        if not self.workout_data:
            return None

        current_lower = str(current_name).strip().lower()
        candidates = []

        # Filter by body part or target muscle
        if body_part:
            bp_lower = str(body_part).strip().lower()
            candidates = [
                ex for ex in self.workout_data
                if str(ex.get("bodyPart", "")).strip().lower() == bp_lower
                and str(ex.get("name", "")).strip().lower() != current_lower
            ]

        if not candidates and target_muscle:
            tm_lower = str(target_muscle).strip().lower()
            candidates = [
                ex for ex in self.workout_data
                if str(ex.get("target", "")).strip().lower() == tm_lower
                and str(ex.get("name", "")).strip().lower() != current_lower
            ]

        # Fallback to any exercise not current
        if not candidates:
            candidates = [
                ex for ex in self.workout_data
                if str(ex.get("name", "")).strip().lower() != current_lower
            ]

        if not candidates:
            return None

        chosen = random.choice(candidates)
        raw_instructions = chosen.get("instructions", [])
        if isinstance(raw_instructions, list):
            instructions_text = " ".join(raw_instructions)
        else:
            instructions_text = str(raw_instructions or "Perform repetitions with controlled tempo and continuous form.")

        return {
            "name": chosen.get("name", "Alternative Exercise").title(),
            "bodyPart": chosen.get("bodyPart", body_part or "Full Body").title(),
            "target": chosen.get("target", target_muscle or "Cardio").title(),
            "equipment": chosen.get("equipment", equipment).title(),
            "instructions": instructions_text,
            "sets": "3 sets",
            "reps": "10-12 reps"
        }


# Singleton instance
exercise_swapper = ExerciseSwapper()
