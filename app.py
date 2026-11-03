
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, jsonify
from ml.plan_generator import PlanGenerator


app = Flask(__name__)

# Initialize the existing plan generator
plan_generator = PlanGenerator()

# JSON storage directory
DATA_DIR = Path(__file__).resolve().parent / "data"

PLANS_FILE = DATA_DIR / "generated_plans.json"
HISTORY_FILE = DATA_DIR / "history.json"
PROFILE_FILE = DATA_DIR / "profile.json"


# =========================================
# JSON STORAGE UTILITIES
# =========================================

DEFAULT_PROFILE = {
    "name": "",
    "age": "",
    "height": "",
    "weight": "",
    "fitness_goal": "general_fitness",
    "fitness_level": "beginner"
}


def initialize_storage():
    """Create JSON files if they do not exist."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    default_files = {
        PLANS_FILE: [],
        HISTORY_FILE: [],
        PROFILE_FILE: DEFAULT_PROFILE
    }

    for file_path, default_data in default_files.items():

        if not file_path.exists() or file_path.stat().st_size == 0:
            write_json(file_path, default_data)


def read_json(file_path, default_data):
    """Read data from a JSON file."""

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return default_data


def write_json(file_path, data):
    """Safely write data to a JSON file."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    temporary_file = file_path.with_suffix(".tmp")

    with open(temporary_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    os.replace(temporary_file, file_path)


initialize_storage()


# =========================================
# HOMEPAGE
# =========================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================
# HEALTH CHECK
# =========================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "success": True,
        "message": "FitFlow AI backend is running!"
    })


# =========================================
# GENERATE FITNESS PLAN
# =========================================

@app.route("/api/generate-plan", methods=["POST"])
def generate_plan():

    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "success": False,
                "error": "Please provide valid JSON data."
            }), 400

        plan_type = data.get("plan_type", "both")
        goal = data.get("goal", "general_fitness")
        fitness_level = data.get("fitness_level", "beginner")
        duration = data.get("duration", 30)
        equipment = data.get("equipment", "none")
        body_part = data.get("body_part")

        try:
            duration = int(duration)
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Duration must be a valid number."
            }), 400

        # Generate using the existing ML module
        result = plan_generator.generate_plan(
            plan_type=plan_type,
            goal=goal,
            fitness_level=fitness_level,
            duration=duration,
            equipment=equipment,
            body_part=body_part
        )

        if not isinstance(result, dict) or result.get("success") is False:
            return jsonify(result), 400

        # Convert the result into standard JSON-compatible data
        result = json.loads(app.json.dumps(result))

        generated_at = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )

        plan_id = str(uuid.uuid4())

        # Store the complete generated plan
        saved_plan = {
            "id": plan_id,
            "generated_at": generated_at,
            "plan_type": plan_type,
            "goal": goal,
            "fitness_level": fitness_level,
            "duration": duration,
            "equipment": equipment,
            "body_part": body_part,
            "plan": result
        }

        plans = read_json(PLANS_FILE, [])
        plans.insert(0, saved_plan)
        write_json(PLANS_FILE, plans)

        # Store a separate history entry
        history = read_json(HISTORY_FILE, [])

        history.insert(0, {
            "id": plan_id,
            "generated_at": generated_at,
            "plan_type": plan_type,
            "goal": goal,
            "fitness_level": fitness_level,
            "duration": duration
        })

        write_json(HISTORY_FILE, history)

        # Preserve the existing API response structure
        result["plan_id"] = plan_id
        result["generated_at"] = generated_at

        return jsonify(result)

    except ValueError as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 400

    except Exception:
        app.logger.exception("Plan generation failed")

        return jsonify({
            "success": False,
            "error": "Something went wrong while generating your plan."
        }), 500


# =========================================
# PREVIOUSLY GENERATED PLANS
# =========================================

@app.route("/api/plans", methods=["GET"])
def get_plans():

    plans = read_json(PLANS_FILE, [])

    return jsonify({
        "success": True,
        "plans": plans
    })


# =========================================
# GET ONE SAVED PLAN
# =========================================

@app.route("/api/plans/<plan_id>", methods=["GET"])
def get_single_plan(plan_id):

    plans = read_json(PLANS_FILE, [])

    for saved_plan in plans:

        if saved_plan.get("id") == plan_id:
            return jsonify({
                "success": True,
                "plan": saved_plan
            })

    return jsonify({
        "success": False,
        "error": "Plan not found."
    }), 404


# =========================================
# GENERATION HISTORY
# =========================================

@app.route("/api/history", methods=["GET"])
def get_history():

    history = read_json(HISTORY_FILE, [])

    return jsonify({
        "success": True,
        "history": history
    })


# =========================================
# USER PROFILE
# =========================================

@app.route("/api/profile", methods=["GET"])
def get_profile():

    profile = read_json(PROFILE_FILE, DEFAULT_PROFILE)

    return jsonify({
        "success": True,
        "profile": profile
    })


@app.route("/api/profile", methods=["POST"])
def update_profile():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Please provide valid profile data."
        }), 400

    allowed_fields = [
        "name",
        "age",
        "height",
        "weight",
        "fitness_goal",
        "fitness_level"
    ]

    profile = read_json(PROFILE_FILE, DEFAULT_PROFILE)

    for field in allowed_fields:
        if field in data:
            profile[field] = data[field]

    # Validate numeric profile fields when provided
    try:
        for field in ["age", "height", "weight"]:
            value = profile.get(field)

            if value not in ("", None):
                number = float(value)

                if number <= 0:
                    raise ValueError

                profile[field] = number

    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "error": "Age, height and weight must be positive numbers."
        }), 400

    write_json(PROFILE_FILE, profile)

    return jsonify({
        "success": True,
        "message": "Profile updated successfully.",
        "profile": profile
    })


# =========================================
# BMI CALCULATOR
# =========================================

@app.route("/api/bmi", methods=["POST"])
def calculate_bmi():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Please provide valid height and weight."
        }), 400

    try:
        height = float(data.get("height"))
        weight = float(data.get("weight"))

        if height <= 0 or weight <= 0:
            raise ValueError

        height_meters = height / 100
        bmi = weight / (height_meters ** 2)

    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "error": "Enter valid positive height and weight values."
        }), 400

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obesity"

    return jsonify({
        "success": True,
        "bmi": round(bmi, 2),
        "category": category
    })


# =========================================
# RUN APPLICATION
# =========================================

if __name__ == "__main__":
    app.run(debug=True)
