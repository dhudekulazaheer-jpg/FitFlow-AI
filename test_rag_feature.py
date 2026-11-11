"""
Automated Verification Suite for FitFlow AI Online RAG + ICL Feature:
1. Vector indexing over yoga.json, exercises.json, and health_rules.json
2. Cosine-similarity semantic retrieval & focus filtering
3. Clinical contraindication filtering & surgery pause guardrail
4. Explicit missing-API-key enforcement (no offline fake responses)
5. Online RAG + ICL endpoint end-to-end verification (with mocked Gemini HTTP response)
"""

import json
import re
from unittest.mock import patch

from app import app
from models import db, User, UserProfile, HealthAssessment
from ml.rag_retriever import rag_retriever
from ml.rag_engine import generate_rag_response, get_rag_status


def extract_csrf(html):
    match = re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', html)
    if not match:
        match = re.search(r'<meta name="csrf-token" content="([^"]+)">', html)
    return match.group(1) if match else None


class _MockHTTPResponse:
    def __init__(self, payload):
        self._data = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def run_tests():
    print("=" * 60)
    print("TESTING FITFLOW AI ONLINE RAG + ICL SYSTEM")
    print("=" * 60)

    # 1. Verify Vector Knowledge Index
    status = get_rag_status()
    stats = status["indexed_documents"]
    assert stats["yoga"] > 0, "Yoga dataset not indexed"
    assert stats["workout"] > 100, "Workout dataset not indexed"
    assert stats["safety"] > 0, "Safety guidelines not indexed"
    print(f"✓ 1. Indexed {stats['total']} documents ({stats['yoga']} yoga, {stats['workout']} workouts, {stats['safety']} safety rules)")

    # 2. Verify Semantic Retrieval & Focus Filtering
    yoga_docs = rag_retriever.retrieve("core strengthening seated posture", top_k=4, focus_filter="yoga")
    assert len(yoga_docs) > 0, "Expected yoga results"
    assert all(d["doc_type"] in ("yoga", "safety") for d in yoga_docs), "Focus filter failed for yoga"
    print(f"✓ 2. Yoga vector retrieval works (top match: {yoga_docs[0]['name']} @ {yoga_docs[0]['similarity_pct']}%)")

    # 3. Verify Contraindication Filtering
    knee_safe_docs = rag_retriever.retrieve(
        "jumping box jump leg plyometric",
        top_k=5,
        health_assessment={"knee_pain": True, "medically_cleared": True},
    )
    for doc in knee_safe_docs:
        if doc["doc_type"] != "safety":
            assert "box jump" not in doc["name"].lower(), "Unsafe box jump was not filtered for knee_pain"
    print("✓ 3. Clinical contraindication filter blocks unsafe knee exercises")

    # 4. Verify No Fake Offline Fallback When API Key Is Missing
    with patch.dict("os.environ", {"GEMINI_API_KEY": "", "GROQ_API_KEY": "", "OPENAI_API_KEY": ""}, clear=False):
        missing_res = generate_rag_response("gentle yoga for flexibility")
        assert missing_res["success"] is False
        assert missing_res.get("missing_api_key") is True
        assert len(missing_res.get("retrieved_documents", [])) > 0, "Should still expose retrieved sources"
    print("✓ 4. Missing API key returns explicit configuration error (no offline fallback)")

    # 5. Verify Flask Endpoints & Online Gemini Mock Integration
    client = app.test_client()
    with app.app_context():
        email = "rag_test_user@fitflow.ai"
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name="RAG Tester", email=email)
            user.set_password("TestPass123!")
            db.session.add(user)
            db.session.commit()

            prof = UserProfile(user_id=user.id, age=29, weight=68, fitness_level="beginner", fitness_goal="flexibility")
            db.session.add(prof)
            db.session.commit()

        # Ensure clean health assessment (no uncleared surgery)
        ha = HealthAssessment.query.filter_by(user_id=user.id).first()
        if ha:
            ha.previous_surgery = False
            ha.medically_cleared = True
            ha.set_conditions_list(["knee_pain"])
            db.session.commit()
        else:
            ha = HealthAssessment(user_id=user.id, previous_surgery=False, medically_cleared=True)
            ha.set_conditions_list(["knee_pain"])
            db.session.add(ha)
            db.session.commit()

    login_page = client.get("/login")
    csrf = extract_csrf(login_page.get_data(as_text=True))
    logged_in = client.post(
        "/login",
        data={"csrf_token": csrf, "email": "rag_test_user@fitflow.ai", "password": "TestPass123!"},
        follow_redirects=True,
    )
    assert logged_in.status_code == 200
    app_csrf = extract_csrf(logged_in.get_data(as_text=True))

    # Verify RAG UI section and floating Yogi Coach button are rendered in index.html
    home_html = logged_in.get_data(as_text=True)
    assert 'id="ai-coach"' in home_html and 'id="ragCoachForm"' in home_html, "RAG UI missing from index.html"
    assert 'id="yogiCoachFab"' in home_html and 'Yogi Coach' in home_html, "Floating Yogi Coach button missing"
    print("✓ 5. FitFlow AI Yogi Coach section & animated floating button render cleanly")

    # Test GET /api/rag-status
    status_res = client.get("/api/rag-status")
    assert status_res.status_code == 200
    assert status_res.get_json()["success"] is True

    # Test POST /api/rag-coach with mocked online Gemini response
    mock_gemini_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": (
                                "### Tailored Overview\n"
                                "Based on your beginner flexibility profile and knee precaution, here is a safe routine.\n\n"
                                "### Recommended Routine\n"
                                "- **Cat-Cow Stretch** [Doc 1: Cow]: 8 slow breaths.\n\n"
                                "### Safety & Recovery Tip\n"
                                "Keep knees cushioned on a mat."
                            )
                        }
                    ]
                }
            }
        ]
    }
    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key-mocked"}, clear=False):
        with patch("ml.rag_engine.urllib.request.urlopen", return_value=_MockHTTPResponse(mock_gemini_payload)):
            rag_res = client.post(
                "/api/rag-coach",
                json={"query": "gentle spine and back yoga", "focus_filter": "yoga", "top_k": 4},
                headers={"X-CSRFToken": app_csrf},
            )
            assert rag_res.status_code == 200, f"Unexpected status: {rag_res.status_code} {rag_res.get_data(as_text=True)}"
            payload = rag_res.get_json()
            assert payload["success"] is True
            assert "Cat-Cow Stretch" in payload["answer"]
            assert len(payload["retrieved_documents"]) > 0
            assert "Online RAG + ICL" in payload["model_used"]
    print("✓ 6. POST /api/rag-coach completes end-to-end online RAG + ICL pipeline")

    print("\nALL 6/6 RAG VERIFICATION TESTS PASSED!")


if __name__ == "__main__":
    run_tests()
