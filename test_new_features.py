import json
import re
from app import app
from models import db, User

def extract_csrf(html):
    match = re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', html)
    if not match:
        match = re.search(r'<meta name="csrf-token" content="([^"]+)">', html)
    return match.group(1) if match else None

def test_features():
    client = app.test_client()

    with app.app_context():
        u = User.query.filter_by(email="feature_test@test.com").first()
        if not u:
            u = User(name="Feature Tester", email="feature_test@test.com")
            u.set_password("Password123!")
            db.session.add(u)
            db.session.commit()

    # Login
    res = client.get("/login")
    token = extract_csrf(res.get_data(as_text=True))
    res = client.post("/login", data={
        "csrf_token": token,
        "email": "feature_test@test.com",
        "password": "Password123!"
    }, follow_redirects=True)
    assert res.status_code == 200
    home_html = res.get_data(as_text=True)
    csrf_token = extract_csrf(home_html)

    # 1. Test Generate Plan has recovery_nutrition
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
    pdata = res.get_json()
    assert "recovery_nutrition" in pdata
    assert pdata["recovery_nutrition"]["target_water_ml"] > 0
    assert len(pdata["recovery_nutrition"]["recommended_snacks"]) > 0
    plan_id = pdata["plan_id"]
    print("✓ 1. Recovery Nutrition generated with workout plan successfully")

    # 2. Test Swap Exercise
    res = client.post("/api/swap-exercise",
        headers={"X-CSRFToken": csrf_token},
        json={
            "plan_id": plan_id,
            "current_name": "Push Up",
            "is_yoga": False,
            "body_part": "chest"
        }
    )
    assert res.status_code == 200
    sdata = res.get_json()
    assert sdata["success"] is True
    assert "new_exercise" in sdata and sdata["new_exercise"]["name"]
    print("✓ 2. Smart Exercise Swap API works and updates database plan")

    # 3. Test Complete Session Logger
    res = client.post("/api/complete-session",
        headers={"X-CSRFToken": csrf_token},
        json={
            "plan_id": plan_id,
            "routine_name": "Full Body Strength",
            "duration": 30
        }
    )
    assert res.status_code == 200
    cdata = res.get_json()
    assert cdata["success"] is True
    assert "analytics" in cdata
    print("✓ 3. Interactive Session completion logging works")

    # 4. Test Analytics & Badges
    res = client.get("/api/analytics")
    assert res.status_code == 200
    adata = res.get_json()["analytics"]
    assert "total_plans" in adata
    assert "current_streak" in adata
    assert "badges" in adata and len(adata["badges"]) >= 5
    print("✓ 4. Progress, Streaks & Achievement Badges API works")

    # 5. Test Dedicated Nutrition Endpoint
    res = client.post("/api/nutrition",
        headers={"X-CSRFToken": csrf_token},
        json={"duration": 45, "goal": "weight_loss"}
    )
    assert res.status_code == 200
    ndata = res.get_json()["nutrition"]
    assert ndata["target_water_ml"] > 500
    print("✓ 5. Nutrition calculator endpoint works")

    print("\nALL 5 NEW FEATURE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_features()
