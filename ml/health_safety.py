import json
from pathlib import Path

RULES_FILE = Path(__file__).resolve().parent / "health_rules.json"

DEFAULT_RULES = {
    "surgery_rule": {
        "pause_on_uncleared_surgery": True,
        "clearance_required_message": (
            "You indicated previous surgery without confirmed medical clearance to exercise. "
            "For your health and safety, plan generation has been paused. Please consult a qualified "
            "physician or healthcare specialist to receive exercise clearance before proceeding."
        )
    },
    "condition_precautions": {
        "knee_pain": {
            "label": "Knee pain or knee injury",
            "warning": "Knee precaution: Avoid high-impact jumping, heavy deep squats, or sharp knee torsion."
        },
        "lower_back_pain": {
            "label": "Lower back pain",
            "warning": "Lower back precaution: Avoid heavy spinal loading, extreme back extensions, or uncontrolled rotational torque."
        },
        "neck_pain": {
            "label": "Neck or cervical pain",
            "warning": "Neck / cervical precaution: Avoid poses or movements exerting direct pressure or hyperextension on the neck."
        },
        "shoulder_pain": {
            "label": "Shoulder pain or injury",
            "warning": "Shoulder precaution: Avoid heavy overhead loads, behind-the-neck presses, or deep dips."
        },
        "wrist_pain": {
            "label": "Wrist pain or injury",
            "warning": "Wrist precaution: Limit direct full-weight bearing on extended wrists."
        },
        "ankle_pain": {
            "label": "Ankle pain or injury",
            "warning": "Ankle precaution: Avoid plyometric jumping or abrupt lateral direction changes."
        },
        "arthritis": {
            "label": "Arthritis",
            "warning": "Arthritis precaution: Focus on gentle, low-impact range of motion. Never push through joint inflammation."
        }
    },
    "general_disclaimer": (
        "FitFlow AI does not provide medical diagnoses or individual clinical advice. "
        "Always consult a qualified medical professional before undertaking new physical activities."
    )
}


class HealthSafetyEvaluator:
    """Applies conservative health and safety rules based on user assessment."""

    def __init__(self, rules_path=RULES_FILE):
        self.rules = self._load_rules(rules_path)

    def _load_rules(self, rules_path):
        try:
            if Path(rules_path).exists():
                with open(rules_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return DEFAULT_RULES

    def evaluate(self, assessment):
        """
        Evaluates a health assessment dict or model.
        Returns a dictionary:
        {
            "allowed": bool,
            "paused": bool,
            "message": str or None,
            "warnings": list of str,
            "disclaimer": str
        }
        """
        if not assessment:
            return {
                "allowed": True,
                "paused": False,
                "message": None,
                "warnings": [],
                "disclaimer": self.rules.get("general_disclaimer", "")
            }

        # Normalize fields
        if isinstance(assessment, dict):
            prev_surgery = assessment.get("previous_surgery")
            med_cleared = assessment.get("medically_cleared")
            selected_conditions = assessment.get("selected_conditions") or []
            affected_body_part = assessment.get("affected_body_part") or ""
            surgery_date = assessment.get("surgery_date") or ""
        else:
            prev_surgery = getattr(assessment, "previous_surgery", False)
            med_cleared = getattr(assessment, "medically_cleared", False)
            selected_conditions = getattr(assessment, "selected_conditions", [])
            affected_body_part = getattr(assessment, "affected_body_part", "")
            surgery_date = getattr(assessment, "surgery_date", "")

        def is_truthy(val):
            if isinstance(val, bool):
                return val
            if isinstance(val, (int, float)):
                return val != 0
            if isinstance(val, str):
                return val.strip().lower() in ("yes", "true", "1", "t", "y")
            return False

        has_surgery = is_truthy(prev_surgery)
        is_cleared = is_truthy(med_cleared)

        # Handle list in string / json representation
        if isinstance(selected_conditions, str):
            try:
                selected_conditions = json.loads(selected_conditions)
            except Exception:
                selected_conditions = [c.strip() for c in selected_conditions.split(",") if c.strip()]

        # Rule 1: Previous surgery without confirmed medical clearance
        if has_surgery and not is_cleared:
            surgery_msg = self.rules.get("surgery_rule", {}).get(
                "clearance_required_message",
                "You indicated previous surgery without confirmed medical clearance. Plan generation is paused."
            )
            detail = []
            if affected_body_part:
                detail.append(f"Affected area: {affected_body_part}")
            if surgery_date:
                detail.append(f"Surgery date: {surgery_date}")
            if detail:
                surgery_msg += f" ({', '.join(detail)})"

            return {
                "allowed": False,
                "paused": True,
                "message": surgery_msg,
                "warnings": [surgery_msg],
                "disclaimer": self.rules.get("general_disclaimer", "")
            }

        # Collect condition warnings
        precautions = self.rules.get("condition_precautions", {})
        warnings = []
        for cond_key in selected_conditions:
            cond_clean = str(cond_key).strip().lower().replace(" ", "_")
            if cond_clean in precautions:
                warnings.append(precautions[cond_clean]["warning"])
            else:
                # Also check matching by label
                found = False
                for k, v in precautions.items():
                    if v.get("label", "").lower() == str(cond_key).lower():
                        warnings.append(v["warning"])
                        found = True
                        break
                if not found and cond_key:
                    warnings.append(
                        f"Health note for '{cond_key}': Please exercise with caution and discontinue any movement that produces discomfort or pain."
                    )

        return {
            "allowed": True,
            "paused": False,
            "message": None,
            "warnings": warnings,
            "disclaimer": self.rules.get("general_disclaimer", "")
        }


# Convenience singleton
_evaluator = HealthSafetyEvaluator()


def evaluate_health_safety(assessment):
    return _evaluator.evaluate(assessment)
