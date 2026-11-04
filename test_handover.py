import json
import re
from app import app
from models import db, User, UserProfile, HealthAssessment, GeneratedPlan, PlanHistory

def extract_csrf(html):
    match = re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', html)
    if not match:
        match = re.search(r'name=["\']csrf-token["\']\s+content=["\']([^"\']+)["\']', html)
    if not match:
        match = re.search(r'<meta name="csrf-token" content="([^"]+)">', html)
    return match.group(1) if match else None

def run_tests():
    print("=" * 60)
    print("STARTING FITFLOW AI VERIFICATION TESTS")
    print("=" * 60)

    client = app.test_client()

    with app.app_context():
        # Cleanup test users if they exist
        User.query.filter(User.email.in_(["user_a@test.com", "user_b@test.com"])).delete(synchronize_session=False)
        db.session.commit()

    # 1. Health check endpoint (Public)
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.data}"
    data = res.get_json()
    assert data.get("success") is True
    print("✓ 1. Public health check works")

    # 2. Unauthenticated access blocked
    res = client.get("/")
    assert res.status_code == 302 and "/login" in res.headers.get("Location", "")
    res = client.get("/api/plans")
    assert res.status_code == 302 and "/login" in res.headers.get("Location", "")
    print("✓ 2. Unauthenticated access properly redirected to login")

    # 3. Registration: User A
    res = client.get("/register")
    csrf_token = extract_csrf(res.get_data(as_text=True))
    assert csrf_token is not None, "Failed to get CSRF token on register page"

    res = client.post("/register", data={
        "csrf_token": csrf_token,
        "name": "Alpha",
        "email": "user_a@test.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert "Alpha" in res.get_data(as_text=True)
    print("✓ 3. New user registration (User Alpha) works")

    # 4. Logout User A
    res = client.get("/logout", follow_redirects=True)
    assert "signed out" in res.get_data(as_text=True) or "Sign In" in res.get_data(as_text=True)
    print("✓ 4. User logout works")

    # 5. Duplicate email rejected
    res = client.get("/register")
    csrf_token = extract_csrf(res.get_data(as_text=True))
    res = client.post("/register", data={
        "csrf_token": csrf_token,
        "name": "User Alpha Copy",
        "email": "user_a@test.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects=True)
    assert "already exists" in res.get_data(as_text=True)
    print("✓ 5. Duplicate email registration properly rejected")

    # 6. Login with incorrect password rejected
    res = client.get("/login")
    csrf_token = extract_csrf(res.get_data(as_text=True))
    res = client.post("/login", data={
        "csrf_token": csrf_token,
        "email": "user_a@test.com",
        "password": "WrongPassword!"
    }, follow_redirects=True)
    assert "Invalid email or password" in res.get_data(as_text=True)
    print("✓ 6. Incorrect password properly rejected")

    # 7. Login User A successfully
    res = client.get("/login")
    csrf_token = extract_csrf(res.get_data(as_text=True))
    res = client.post("/login", data={
        "csrf_token": csrf_token,
        "email": "user_a@test.com",
        "password": "Password123!"
    }, follow_redirects=True)
    assert res.status_code == 200
    home_html = res.get_data(as_text=True)
    csrf_token = extract_csrf(home_html)
    assert "Alpha" in home_html
    print("✓ 7. Login with valid credentials works")

    # 8. Profile Update for User A
    res = client.post("/api/profile",
        headers={"X-CSRFToken": csrf_token},
        json={
            "name": "Alpha Champion",
            "age": 28,
            "gender": "male",
            "height": 178,
            "weight": 75,
            "fitness_goal": "muscle_gain",
            "fitness_level": "intermediate"
        }
    )
    assert res.status_code == 200
    pdata = res.get_json()["profile"]
    assert pdata["name"] == "Alpha Champion"
    assert pdata["age"] == 28
    assert pdata["gender"] == "male"
    print("✓ 8. Profile update and retrieval work")

    # 9. Health Assessment save for User A
    res = client.post("/api/health-assessment",
        headers={"X-CSRFToken": csrf_token},
        json={
            "selected_conditions": ["knee_pain", "lower_back_pain"],
            "previous_surgery": "yes",
            "affected_body_part": "Right Knee",
            "surgery_date": "2023-05-15",
            "medically_cleared": "yes",
            "additional_information": "Cleared for low-impact training."
        }
    )
    assert res.status_code == 200
    adata = res.get_json()["assessment"]
    assert "knee_pain" in adata["selected_conditions"]
    assert adata["medically_cleared"] is True
    print("✓ 9. Health assessment save and retrieval work")

    # 10. BMI Calculation
    res = client.post("/api/bmi",
        headers={"X-CSRFToken": csrf_token},
        json={"height": 178, "weight": 75}
    )
    assert res.status_code == 200
    bdata = res.get_json()
    assert "bmi" in bdata and bdata["category"] == "Normal weight"
    print("✓ 10. BMI calculator works")

    # 11. Plan Generation: Yoga (15 min)
    res = client.post("/api/generate-plan",
        headers={"X-CSRFToken": csrf_token},
        json={
            "plan_type": "yoga",
            "goal": "flexibility",
            "fitness_level": "intermediate",
            "duration": 15
        }
    )
    assert res.status_code == 200
    yoga_res = res.get_json()
    assert "plan_id" in yoga_res
    assert len(yoga_res.get("safety_warnings", [])) > 0  # because user has knee_pain & lower_back_pain
    plan_a_id = yoga_res["plan_id"]
    print("✓ 11. Yoga-only plan generation works with health safety warnings")

    # 12. Plan Generation: Workout (30 min)
    res = client.post("/api/generate-plan",
        headers={"X-CSRFToken": csrf_token},
        json={
            "plan_type": "workout",
            "goal": "general_fitness",
            "fitness_level": "beginner",
            "duration": 30,
            "equipment": "none"
        }
    )
    assert res.status_code == 200
    workout_res = res.get_json()
    assert "plan_id" in workout_res
    print("✓ 12. Workout-only plan generation works")

    # 13. Plan Generation: Combined (30 min, 45 min, 60 min)
    for dur in [30, 45, 60]:
        res = client.post("/api/generate-plan",
            headers={"X-CSRFToken": csrf_token},
            json={
                "plan_type": "both",
                "goal": "general_fitness",
                "fitness_level": "beginner",
                "duration": dur,
                "equipment": "none"
            }
        )
        assert res.status_code == 200
        comb = res.get_json()
        assert "yoga" in comb and "yoga_plan" in comb
        assert "workout" in comb and "workout_plan" in comb
    print("✓ 13. Combined plan generation works across all supported durations with dual key compatibility")

    # 14. Retrieve Saved Plans and History for User A
    res = client.get("/api/plans")
    assert res.status_code == 200
    plans_a = res.get_json()["plans"]
    assert len(plans_a) >= 5

    res = client.get("/api/history")
    assert res.status_code == 200
    hist_a = res.get_json()["history"]
    assert len(hist_a) >= 5
    print("✓ 14. Saved plans and plan history correctly saved in MySQL and retrievable")

    # 15. Safety Check: Surgery WITHOUT medical clearance must pause plan generation
    res = client.post("/api/health-assessment",
        headers={"X-CSRFToken": csrf_token},
        json={
            "selected_conditions": ["knee_pain"],
            "previous_surgery": "yes",
            "affected_body_part": "Right Knee",
            "surgery_date": "2024-01-10",
            "medically_cleared": "no",
            "additional_information": "Still recovering, no clearance yet."
        }
    )
    assert res.status_code == 200

    res = client.post("/api/generate-plan",
        headers={"X-CSRFToken": csrf_token},
        json={
            "plan_type": "workout",
            "goal": "general_fitness",
            "fitness_level": "beginner",
            "duration": 30,
            "equipment": "none"
        }
    )
    assert res.status_code == 400
    paused_res = res.get_json()
    assert paused_res.get("paused") is True
    assert paused_res.get("health_safety_paused") is True
    assert "paused" in paused_res.get("error", "").lower()
    print("✓ 15. Safety logic: Uncleared surgery successfully paused plan generation")

    # 16. User Isolation Test: Register User B
    client.get("/logout")
    res = client.get("/register")
    csrf_b = extract_csrf(res.get_data(as_text=True))
    res = client.post("/register", data={
        "csrf_token": csrf_b,
        "name": "User Beta",
        "email": "user_b@test.com",
        "password": "Password456!",
        "confirm_password": "Password456!"
    }, follow_redirects=True)
    assert res.status_code == 200

    # User B should see 0 plans and 0 history
    res = client.get("/api/plans")
    plans_b = res.get_json()["plans"]
    assert len(plans_b) == 0, f"Privacy violation: User B saw {len(plans_b)} plans!"

    res = client.get("/api/history")
    hist_b = res.get_json()["history"]
    assert len(hist_b) == 0, f"Privacy violation: User B saw {len(hist_b)} history items!"

    # User B cannot access User A's specific plan
    res = client.get(f"/api/plans/{plan_a_id}")
    assert res.status_code == 404, "Privacy violation: User B could access User A's plan!"

    # User B's profile is independent
    res = client.get("/api/profile")
    pdata_b = res.get_json()["profile"]
    assert pdata_b["name"] == "User Beta"
    assert pdata_b["age"] in ("", None)
    print("✓ 16. User data privacy and isolation verified: User B cannot access User A's records")

    print("=" * 60)
    print("ALL 16 FITFLOW AI TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
