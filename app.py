import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from flask_wtf.csrf import CSRFProtect

from config import SECRET_KEY, DATABASE_URL
from models import (
    db,
    User,
    UserProfile,
    HealthAssessment,
    GeneratedPlan,
    PlanHistory
)
from ml.plan_generator import PlanGenerator
from ml.exercise_swapper import exercise_swapper
from ml.wellness_companion import get_recovery_nutrition, get_user_analytics
from ml.program_generator import WeeklyProgramGenerator
from ml.progression_advisor import get_progression_advice

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please sign in to access FitFlow AI."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None


# Initialize the plan generator
plan_generator = PlanGenerator()
weekly_program_generator = WeeklyProgramGenerator()

# JSON storage directory (Preserved as backup/archive)
DATA_DIR = Path(__file__).resolve().parent / "data"
PLANS_FILE = DATA_DIR / "generated_plans.json"
HISTORY_FILE = DATA_DIR / "history.json"
PROFILE_FILE = DATA_DIR / "profile.json"


def initialize_json_storage():
    """Create JSON backup files if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for file_path in [PLANS_FILE, HISTORY_FILE]:
        if not file_path.exists() or file_path.stat().st_size == 0:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)
            except Exception:
                pass


def append_json_backup(file_path, record):
    """Safely append to JSON backup file without throwing error on failure."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        data = []
        if file_path.exists() and file_path.stat().st_size > 0:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        data.insert(0, record)
        temp_file = file_path.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(temp_file, file_path)
    except Exception as e:
        app.logger.warning(f"JSON backup write failed: {e}")


initialize_json_storage()


# =========================================
# AUTHENTICATION ROUTES
# =========================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("register.html")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists. Please sign in.", "error")
            return render_template("register.html")

        try:
            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            # Create default profile for the user
            profile = UserProfile(
                user_id=user.id,
                fitness_goal="general_fitness",
                fitness_level="beginner"
            )
            db.session.add(profile)
            db.session.commit()

            login_user(user)
            flash("Registration successful! Welcome to FitFlow AI.", "success")
            return redirect(url_for("home"))

        except Exception as e:
            db.session.rollback()
            app.logger.exception("Registration error")
            flash("An error occurred during registration. Please try again.", "error")
            return render_template("register.html")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "error")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password. Please try again.", "error")
            return render_template("login.html")

        login_user(user)
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("login"))


# =========================================
# HOMEPAGE / DASHBOARD
# =========================================

@app.route("/")
@login_required
def home():
    return render_template("index.html")


# =========================================
# HEALTH CHECK (PUBLIC)
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
@login_required
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

        # Optional Health Assessment submitted or fetch user's saved assessment
        health_assessment_data = data.get("health_assessment")

        # If assessment submitted inline, update or create record in MySQL
        if isinstance(health_assessment_data, dict):
            assessment_record = HealthAssessment.query.filter_by(user_id=current_user.id).first()
            if not assessment_record:
                assessment_record = HealthAssessment(user_id=current_user.id)
                db.session.add(assessment_record)

            conditions = health_assessment_data.get("selected_conditions", [])
            assessment_record.set_conditions_list(conditions)

            prev_surg = health_assessment_data.get("previous_surgery")
            if isinstance(prev_surg, str):
                prev_surg = prev_surg.lower() in ("yes", "true", "1")
            assessment_record.previous_surgery = bool(prev_surg)

            assessment_record.affected_body_part = health_assessment_data.get("affected_body_part")
            assessment_record.surgery_date = health_assessment_data.get("surgery_date")

            med_clr = health_assessment_data.get("medically_cleared")
            if isinstance(med_clr, str):
                med_clr = med_clr.lower() in ("yes", "true", "1")
            assessment_record.medically_cleared = bool(med_clr)

            assessment_record.additional_information = health_assessment_data.get("additional_information")
            db.session.commit()
            assessment_to_eval = assessment_record.to_dict()
        else:
            # Check if user already has a saved assessment in MySQL
            saved_assessment = HealthAssessment.query.filter_by(user_id=current_user.id).first()
            assessment_to_eval = saved_assessment.to_dict() if saved_assessment else None

        # Retrieve user age from profile if available
        user_age = current_user.profile.age if (current_user.profile and current_user.profile.age) else None

        # Generate using the ML module with health safety check
        result = plan_generator.generate_plan(
            plan_type=plan_type,
            goal=goal,
            fitness_level=fitness_level,
            duration=duration,
            equipment=equipment,
            body_part=body_part,
            age=user_age,
            health_assessment=assessment_to_eval
        )

        if not isinstance(result, dict) or result.get("success") is False:
            # If health safety paused normal plan generation
            if result.get("health_safety_paused") or result.get("paused"):
                return jsonify({
                    "success": False,
                    "paused": True,
                    "health_safety_paused": True,
                    "error": result.get("message"),
                    "safety_warnings": result.get("safety_warnings", []),
                    "disclaimer": result.get("disclaimer", "")
                }), 400

            return jsonify(result), 400

        # Convert result into standard JSON-compatible data
        result = json.loads(app.json.dumps(result))

        # Attach personalized post-workout recovery nutrition guidance
        user_weight = current_user.profile.weight if (current_user.profile and current_user.profile.weight) else 70.0
        result["recovery_nutrition"] = get_recovery_nutrition(
            weight_kg=user_weight,
            duration_min=duration,
            goal=goal
        )

        generated_at_dt = datetime.utcnow()
        generated_at = generated_at_dt.isoformat()
        plan_id = str(uuid.uuid4())

        # Store the plan in MySQL associated with current_user.id
        saved_plan = GeneratedPlan(
            id=plan_id,
            user_id=current_user.id,
            plan_type=plan_type,
            goal=goal,
            fitness_level=fitness_level,
            duration=duration,
            equipment=equipment,
            body_part=body_part,
            plan_data=json.dumps(result),
            generated_at=generated_at_dt
        )
        db.session.add(saved_plan)

        # Store plan history in MySQL associated with current_user.id
        history_entry = PlanHistory(
            user_id=current_user.id,
            plan_id=plan_id,
            activity=f"Generated {plan_type.title()} Plan",
            created_at=generated_at_dt
        )
        db.session.add(history_entry)
        db.session.commit()

        # Preserve JSON backups as archives
        append_json_backup(PLANS_FILE, {
            "id": plan_id,
            "user_id": current_user.id,
            "generated_at": generated_at,
            "plan_type": plan_type,
            "goal": goal,
            "fitness_level": fitness_level,
            "duration": duration,
            "equipment": equipment,
            "body_part": body_part,
            "plan": result
        })

        append_json_backup(HISTORY_FILE, {
            "id": plan_id,
            "user_id": current_user.id,
            "generated_at": generated_at,
            "plan_type": plan_type,
            "goal": goal,
            "fitness_level": fitness_level,
            "duration": duration
        })

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
        db.session.rollback()
        app.logger.exception("Plan generation failed")
        return jsonify({
            "success": False,
            "error": "Something went wrong while generating your plan."
        }), 500


# =========================================
# PREVIOUSLY GENERATED PLANS
# =========================================

@app.route("/api/plans", methods=["GET"])
@login_required
def get_plans():
    plans = GeneratedPlan.query.filter_by(
        user_id=current_user.id
    ).order_by(GeneratedPlan.generated_at.desc()).all()

    return jsonify({
        "success": True,
        "plans": [p.to_dict() for p in plans]
    })


# =========================================
# GET ONE SAVED PLAN
# =========================================

@app.route("/api/plans/<plan_id>", methods=["GET"])
@login_required
def get_single_plan(plan_id):
    saved_plan = GeneratedPlan.query.filter_by(
        id=plan_id,
        user_id=current_user.id
    ).first()

    if saved_plan:
        return jsonify({
            "success": True,
            "plan": saved_plan.to_dict()
        })

    return jsonify({
        "success": False,
        "error": "Plan not found."
    }), 404


# =========================================
# GENERATION HISTORY
# =========================================

@app.route("/api/history", methods=["GET"])
@login_required
def get_history():
    history_entries = PlanHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(PlanHistory.created_at.desc()).all()

    return jsonify({
        "success": True,
        "history": [h.to_dict() for h in history_entries]
    })


# =========================================
# USER PROFILE
# =========================================

@app.route("/api/profile", methods=["GET"])
@login_required
def get_profile():
    profile = current_user.profile
    profile_data = profile.to_dict() if profile else {
        "name": current_user.name,
        "age": "",
        "gender": "",
        "height": "",
        "weight": "",
        "fitness_goal": "general_fitness",
        "fitness_level": "beginner"
    }

    return jsonify({
        "success": True,
        "profile": profile_data
    })


@app.route("/api/profile", methods=["POST"])
@login_required
def update_profile():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Please provide valid profile data."
        }), 400

    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)

    if "name" in data and data["name"]:
        current_user.name = str(data["name"]).strip()

    if "fitness_goal" in data:
        profile.fitness_goal = data["fitness_goal"]

    if "fitness_level" in data:
        profile.fitness_level = data["fitness_level"]

    if "gender" in data:
        profile.gender = data["gender"]

    # Validate numeric fields
    try:
        for field in ["age", "height", "weight"]:
            if field in data:
                val = data.get(field)
                if val not in ("", None):
                    number = float(val)
                    if number <= 0:
                        raise ValueError
                    setattr(profile, field, number)
                else:
                    setattr(profile, field, None)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Profile updated successfully.",
            "profile": profile.to_dict()
        })

    except (ValueError, TypeError):
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Age, height and weight must be positive numbers."
        }), 400
    except Exception as e:
        db.session.rollback()
        app.logger.exception("Profile update failed")
        return jsonify({
            "success": False,
            "error": "Could not update profile."
        }), 500


# =========================================
# HEALTH ASSESSMENT API
# =========================================

@app.route("/api/health-assessment", methods=["GET"])
@login_required
def get_health_assessment():
    assessment = current_user.health_assessment
    return jsonify({
        "success": True,
        "assessment": assessment.to_dict() if assessment else None
    })


@app.route("/api/health-assessment", methods=["POST"])
@login_required
def save_health_assessment():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Invalid health assessment data."
        }), 400

    try:
        assessment = current_user.health_assessment
        if not assessment:
            assessment = HealthAssessment(user_id=current_user.id)
            db.session.add(assessment)

        conditions = data.get("selected_conditions", [])
        assessment.set_conditions_list(conditions)

        prev_surgery = data.get("previous_surgery")
        if isinstance(prev_surgery, str):
            prev_surgery = prev_surgery.lower() in ("yes", "true", "1")
        assessment.previous_surgery = bool(prev_surgery)

        assessment.affected_body_part = data.get("affected_body_part", "").strip() or None
        assessment.surgery_date = data.get("surgery_date", "").strip() or None

        med_cleared = data.get("medically_cleared")
        if isinstance(med_cleared, str):
            med_cleared = med_cleared.lower() in ("yes", "true", "1")
        assessment.medically_cleared = bool(med_cleared)

        assessment.additional_information = data.get("additional_information", "").strip() or None

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Health assessment saved successfully.",
            "assessment": assessment.to_dict()
        })

    except Exception:
        db.session.rollback()
        app.logger.exception("Failed to save health assessment")
        return jsonify({
            "success": False,
            "error": "Could not save health assessment."
        }), 500


# =========================================
# BMI CALCULATOR
# =========================================

@app.route("/api/bmi", methods=["POST"])
@login_required
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
# SMART EXERCISE SWAPPER
# =========================================

@app.route("/api/swap-exercise", methods=["POST"])
@login_required
def swap_exercise():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid request payload."}), 400

    plan_id = data.get("plan_id")
    current_name = data.get("current_name")
    is_yoga = bool(data.get("is_yoga", False))
    body_part = data.get("body_part")
    category = data.get("category")
    target = data.get("target")
    equipment = data.get("equipment", "none")

    if is_yoga:
        new_item = exercise_swapper.get_yoga_alternative(current_name=current_name, category=category)
    else:
        new_item = exercise_swapper.get_workout_alternative(
            current_name=current_name,
            body_part=body_part,
            target_muscle=target,
            equipment=equipment
        )

    if not new_item:
        return jsonify({"success": False, "error": "No alternative exercise found."}), 404

    # If plan_id is provided, update the saved plan in the database
    if plan_id:
        saved_plan = GeneratedPlan.query.filter_by(id=plan_id, user_id=current_user.id).first()
        if saved_plan:
            try:
                plan_dict = saved_plan.get_plan_json()

                def replace_in_obj(obj):
                    if isinstance(obj, dict):
                        name_val = obj.get("name") or obj.get("english_name")
                        if name_val and str(name_val).strip().lower() == str(current_name).strip().lower():
                            obj.update(new_item)
                            return True
                        for k, v in obj.items():
                            if replace_in_obj(v):
                                return True
                    elif isinstance(obj, list):
                        for item in obj:
                            if replace_in_obj(item):
                                return True
                    return False

                replace_in_obj(plan_dict)
                saved_plan.plan_data = json.dumps(plan_dict)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                app.logger.warning(f"Could not update plan JSON on swap: {e}")

    return jsonify({
        "success": True,
        "new_exercise": new_item,
        "message": f"Successfully swapped with {new_item.get('name')}!"
    })


# =========================================
# COMPLETE SESSION LOGGER
# =========================================

@app.route("/api/complete-session", methods=["POST"])
@login_required
def complete_session():
    data = request.get_json(silent=True) or {}
    plan_id = data.get("plan_id")
    routine_name = data.get("routine_name", "Fitness Routine")
    duration = data.get("duration", 30)

    try:
        history_entry = PlanHistory(
            user_id=current_user.id,
            plan_id=plan_id,
            activity=f"Completed Session: {routine_name} ({duration}m)",
            created_at=datetime.utcnow()
        )
        db.session.add(history_entry)
        db.session.commit()

        analytics = get_user_analytics(current_user.id)
        return jsonify({
            "success": True,
            "message": "Great job! Workout completed and logged.",
            "analytics": analytics
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Could not log session completion."}), 500


# =========================================
# USER ANALYTICS & STREAKS
# =========================================

@app.route("/api/analytics", methods=["GET"])
@login_required
def get_analytics():
    try:
        analytics = get_user_analytics(current_user.id)
        return jsonify({
            "success": True,
            "analytics": analytics
        })
    except Exception as e:
        app.logger.exception("Failed to retrieve analytics")
        return jsonify({"success": False, "error": "Could not calculate analytics."}), 500


# =========================================
# RECOVERY NUTRITION CALCULATOR
# =========================================

@app.route("/api/nutrition", methods=["POST"])
@login_required
def calculate_nutrition():
    data = request.get_json(silent=True) or {}
    user_weight = current_user.profile.weight if (current_user.profile and current_user.profile.weight) else 70.0
    duration = data.get("duration", 30)
    goal = data.get("goal") or (current_user.profile.fitness_goal if current_user.profile else "general_fitness")

    nutrition = get_recovery_nutrition(weight_kg=user_weight, duration_min=duration, goal=goal)
    return jsonify({
        "success": True,
        "nutrition": nutrition
    })


# =========================================
# 7-DAY STRUCTURED PROGRAM GENERATOR
# =========================================

@app.route("/api/generate-program", methods=["POST"])
@login_required
def generate_weekly_program():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid program request data."}), 400

    profile = current_user.profile
    health_record = current_user.health_assessment

    goal = data.get("goal") or (profile.fitness_goal if profile else "general_fitness")
    fitness_level = data.get("fitness_level") or (profile.fitness_level if profile else "beginner")
    equipment = data.get("equipment", "none")
    duration = int(data.get("duration", 30))
    user_weight = profile.weight if (profile and profile.weight) else 70.0
    user_age = int(profile.age) if (profile and profile.age) else None

    health_assessment_data = data.get("health_assessment")
    if not health_assessment_data and health_record:
        health_assessment_data = health_record.to_dict()

    result = weekly_program_generator.generate_program(
        goal=goal,
        fitness_level=fitness_level,
        equipment=equipment,
        duration_per_session=duration,
        health_assessment=health_assessment_data,
        age=user_age,
        weight_kg=user_weight
    )

    if not result.get("success", False):
        status_code = 403 if result.get("paused") else 400
        return jsonify(result), status_code

    # Save weekly program in GeneratedPlan
    try:
        program_id = str(uuid.uuid4())
        new_plan = GeneratedPlan(
            id=program_id,
            user_id=current_user.id,
            plan_type="weekly_program",
            goal=goal,
            fitness_level=fitness_level,
            duration=duration,
            equipment=equipment,
            plan_data=json.dumps(result),
            generated_at=datetime.utcnow()
        )
        db.session.add(new_plan)
        db.session.flush()

        history_entry = PlanHistory(
            user_id=current_user.id,
            plan_id=program_id,
            activity=f"Generated 7-Day Weekly Program ({goal})"
        )
        db.session.add(history_entry)
        db.session.commit()

        result["plan_id"] = program_id
        return jsonify(result)
    except Exception as e:
        db.session.rollback()
        app.logger.exception("Failed to save weekly program")
        return jsonify(result)


# =========================================
# PROGRESSIVE OVERLOAD & DIFFICULTY ADVISOR
# =========================================

@app.route("/api/progression-advice", methods=["GET"])
@login_required
def get_user_progression_advice():
    try:
        advice = get_progression_advice(current_user.id)
        return jsonify({"success": True, "advice": advice})
    except Exception as e:
        app.logger.exception("Failed to get progression advice")
        return jsonify({"success": False, "error": "Could not determine progression advice."}), 500


@app.route("/api/advance-level", methods=["POST"])
@login_required
def advance_user_level():
    data = request.get_json(silent=True) or {}
    new_level = data.get("level")
    if new_level not in ["beginner", "intermediate", "advanced"]:
        return jsonify({"success": False, "error": "Invalid fitness level."}), 400

    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id, fitness_level=new_level)
        db.session.add(profile)
    else:
        profile.fitness_level = new_level

    try:
        history_entry = PlanHistory(
            user_id=current_user.id,
            activity=f"Advanced fitness level to {new_level.capitalize()}"
        )
        db.session.add(history_entry)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"Congratulations! Your profile has been advanced to {new_level.capitalize()}.",
            "fitness_level": new_level
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Could not update fitness level."}), 500


# =========================================
# RUN APPLICATION
# =========================================

if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"Could not connect to database on startup: {e}")
    app.run(debug=True)
