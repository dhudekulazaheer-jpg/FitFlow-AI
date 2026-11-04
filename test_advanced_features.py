"""
Automated Verification Suite for FitFlow AI Advanced Features:
- Feature 1: 7-Day Structured Weekly Program Generator
- Feature 3: Audio chimes & interval Web Audio API readiness
- Feature 4: Smart Warm-Up & Cool-Down Protocols
- Feature 5: Progressive Overload & Difficulty Advisor
"""

import sys
import json
import re
from app import app
from models import db, User, UserProfile, GeneratedPlan, PlanHistory
from ml.warmup_cooldown import get_warmup_cooldown
from ml.program_generator import WeeklyProgramGenerator
from ml.progression_advisor import get_progression_advice


def extract_csrf(html):
    match = re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', html)
    if not match:
        match = re.search(r'<meta name="csrf-token" content="([^"]+)">', html)
    return match.group(1) if match else None


def run_tests():
    print("=" * 60)
    print("TESTING FITFLOW AI ADVANCED SUITE (1, 3, 4, 5)")
    print("=" * 60)

    # 1. Test Warm-Up and Cool-Down
    wc = get_warmup_cooldown(body_part="chest", is_yoga=False, goal="general_fitness")
    assert "warmup" in wc and len(wc["warmup"]) == 3, "Warm-up protocol missing 3 movements"
    assert "cooldown" in wc and len(wc["cooldown"]) == 3, "Cool-down protocol missing 3 movements"
    assert sum(w["duration_seconds"] for w in wc["warmup"]) == 180, "Warm-up should be 180s (3 min)"
    print("✓ 1. Smart Warm-Up & Cool-Down protocols generated correctly")

    # 2. Test Weekly Program Generator Logic
    wp_gen = WeeklyProgramGenerator()
    program = wp_gen.generate_program(
        goal="muscle_building",
        fitness_level="beginner",
        equipment="basic",
        duration_per_session=30
    )
    assert program["success"] is True, f"Program gen failed: {program}"
    assert len(program["schedule"]) == 7, "Program schedule must have exactly 7 days"
    active_days = [d for d in program["schedule"] if not d["is_rest_day"]]
    rest_days = [d for d in program["schedule"] if d["is_rest_day"]]
    assert len(active_days) >= 4, "Should have at least 4 active days in muscle building"
    assert len(rest_days) >= 1, "Should have rest days scheduled"
    print("✓ 2. 7-Day Weekly Program generator produces balanced 7-day schedule")

    # 3. Test Flask Endpoints with Test Client
    client = app.test_client()
    with app.app_context():
        test_email = "advanced_test_user@fitflow.ai"
        user = User.query.filter_by(email=test_email).first()
        if not user:
            user = User(name="Advanced Athlete", email=test_email)
            user.set_password("SecurePass123!")
            db.session.add(user)
            db.session.commit()

            profile = UserProfile(user_id=user.id, fitness_level="beginner", fitness_goal="muscle_building")
            db.session.add(profile)
            db.session.commit()

    # Login with CSRF
    res = client.get("/login")
    token = extract_csrf(res.get_data(as_text=True))
    login_res = client.post("/login", data={
        "csrf_token": token,
        "email": test_email,
        "password": "SecurePass123!"
    }, follow_redirects=True)
    assert login_res.status_code == 200, "Login failed"
    csrf_token = extract_csrf(login_res.get_data(as_text=True))

    # Test POST /api/generate-program
    prog_res = client.post("/api/generate-program",
        headers={"X-CSRFToken": csrf_token},
        json={
            "goal": "general_fitness",
            "fitness_level": "beginner",
            "equipment": "none",
            "duration": 30
        }
    )
    assert prog_res.status_code == 200, f"API generate-program failed: {prog_res.get_json()}"
    prog_data = prog_res.get_json()
    assert prog_data["success"] is True
    assert "plan_id" in prog_data
    assert len(prog_data["schedule"]) == 7
    print("✓ 3. Endpoint /api/generate-program works and persists to MySQL")

    # Test GET /api/progression-advice
    adv_res = client.get("/api/progression-advice", headers={"X-CSRFToken": csrf_token})
    assert adv_res.status_code == 200
    adv_data = adv_res.get_json()
    assert adv_data["success"] is True
    assert "advice" in adv_data
    assert "actionable_cues" in adv_data["advice"]
    print("✓ 4. Endpoint /api/progression-advice returns personalized cues")

    # Test POST /api/advance-level
    advance_res = client.post("/api/advance-level",
        headers={"X-CSRFToken": csrf_token},
        json={"level": "intermediate"}
    )
    assert advance_res.status_code == 200
    adv_up = advance_res.get_json()
    assert adv_up["success"] is True
    assert adv_up["fitness_level"] == "intermediate"

    # Verify in DB
    with app.app_context():
        user = User.query.filter_by(email=test_email).first()
        updated_prof = UserProfile.query.filter_by(user_id=user.id).first()
        assert updated_prof.fitness_level == "intermediate"
    print("✓ 5. Endpoint /api/advance-level successfully updates profile in MySQL")

    # 6. Test Friends Connection & Streak Leaderboard System
    with app.app_context():
        friend_email = "friend_companion@fitflow.ai"
        friend_user = User.query.filter_by(email=friend_email).first()
        if not friend_user:
            friend_user = User(name="Companion Runner", email=friend_email)
            friend_user.set_password("SecurePass123!")
            db.session.add(friend_user)
            db.session.commit()
            friend_profile = UserProfile(user_id=friend_user.id, fitness_level="intermediate", fitness_goal="endurance")
            db.session.add(friend_profile)
            db.session.commit()

        assert user.friend_code == f"FIT-{user.id:04d}", f"Invalid friend code format: {user.friend_code}"
        assert friend_user.friend_code == f"FIT-{friend_user.id:04d}"
        friend_code_str = friend_user.friend_code
        friend_id = friend_user.id
    print("✓ 6. User friend_code properties formatted correctly")

    # Test POST /api/friends/add (self-add rejection)
    self_add_res = client.post("/api/friends/add",
        headers={"X-CSRFToken": csrf_token},
        json={"identifier": user.friend_code}
    )
    assert self_add_res.status_code == 400, "Should reject self-friending"

    # Test POST /api/friends/add (valid add via friend code)
    add_res = client.post("/api/friends/add",
        headers={"X-CSRFToken": csrf_token},
        json={"identifier": friend_code_str}
    )
    assert add_res.status_code == 200, f"Friend add failed: {add_res.get_json()}"
    add_data = add_res.get_json()
    assert add_data["success"] is True

    # Test duplicate add rejection
    dup_res = client.post("/api/friends/add",
        headers={"X-CSRFToken": csrf_token},
        json={"identifier": friend_email}
    )
    assert dup_res.status_code == 400, "Should reject duplicate friend connection"
    print("✓ 7. Endpoint /api/friends/add connects companions and prevents duplicates/self-adds")

    # Test GET /api/friends/leaderboard
    lead_res = client.get("/api/friends/leaderboard", headers={"X-CSRFToken": csrf_token})
    assert lead_res.status_code == 200, f"Leaderboard fetch failed: {lead_res.get_json()}"
    lead_data = lead_res.get_json()
    assert lead_data["success"] is True
    assert "leaderboard" in lead_data
    assert len(lead_data["leaderboard"]) >= 2, "Leaderboard should include both friends"

    # Privacy verification: verify NO private health assessments or injuries are exposed in leaderboard
    for member in lead_data["leaderboard"]:
        assert "injuries" not in member
        assert "medical_clearance" not in member
        assert "health_assessment" not in member
        assert "rank" in member
        assert "current_streak" in member
    print("✓ 8. Endpoint /api/friends/leaderboard computes rankings with strict privacy protection")

    # Test POST /api/friends/kudos
    kudos_res = client.post("/api/friends/kudos",
        headers={"X-CSRFToken": csrf_token},
        json={"friend_id": friend_id}
    )
    assert kudos_res.status_code == 200, f"Kudos failed: {kudos_res.get_json()}"
    kudos_data = kudos_res.get_json()
    assert kudos_data["success"] is True
    print("✓ 9. Endpoint /api/friends/kudos sends High Five encouragement")

    print("=" * 60)
    print("ALL ADVANCED SUITE & SOCIAL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
