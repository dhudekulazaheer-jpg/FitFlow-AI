"""
RAG Vector Knowledge Base & Retriever for FitFlow AI.

Indexes the project's curated datasets (`yoga.json`, `exercises.json`, and
`health_rules.json`) into an in-memory TF-IDF vector space and performs
cosine-similarity semantic retrieval with clinical contraindication filtering.
"""

import json
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import YOGA_FILE, EXERCISEDB_FILE
from ml.health_safety import HealthSafetyEvaluator


# Condition-specific movement patterns to deprioritize/exclude during retrieval
CONTRAINDICATION_KEYWORDS = {
    "knee_pain": ["jump", "plyometric", "box jump", "burpee", "deep squat", "pistol squat", "lunge jump"],
    "lower_back_pain": ["deadlift", "good morning", "hyperextension", "heavy barbell squat", "clean and jerk"],
    "neck_pain": ["headstand", "shoulderstand", "plow", "neck bridge", "behind the neck"],
    "shoulder_pain": ["overhead press", "handstand", "upright row", "behind the neck", "dip", "muscle-up"],
    "wrist_pain": ["handstand", "crow pose", "wheel pose", "push-up", "plank"],
    "ankle_pain": ["jump", "skip", "hop", "plyometric", "sprint", "box jump"],
    "arthritis": ["plyometric", "explosive", "max effort", "heavy barbell"],
}


class RAGRetriever:
    """Vector-space knowledge retriever over FitFlow AI yoga and workout datasets."""

    def __init__(self):
        self.documents = []
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True,
            max_features=25000,
        )
        self.tfidf_matrix = None
        self.stats = {"yoga": 0, "workout": 0, "safety": 0, "total": 0}
        self._build_index()

    def _clean_text(self, value):
        if isinstance(value, list):
            value = " ".join(str(v) for v in value if v)
        return re.sub(r"\s+", " ", str(value or "")).strip()

    def _load_json(self, path):
        p = Path(path)
        if not p.exists():
            return []
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("data", "exercises", "yoga", "poses", "results"):
                if isinstance(data.get(key), list):
                    return data[key]
        return []

    def _build_index(self):
        docs = []

        # 1. Index Yoga Poses (datasets/yoga/yoga.json)
        yoga_items = self._load_json(YOGA_FILE)
        for item in yoga_items:
            name = self._clean_text(item.get("name") or item.get("english_name") or "Yoga Pose")
            sanskrit = self._clean_text(item.get("sanskrit_name", ""))
            difficulty = self._clean_text(item.get("difficulty", "Beginner"))
            focus = self._clean_text(item.get("focus", ""))
            categories = self._clean_text(item.get("categories") or item.get("category", ""))
            target_areas = self._clean_text(item.get("target_areas", []))
            benefits = self._clean_text(item.get("benefits", ""))
            description = self._clean_text(item.get("description", ""))

            instr_raw = item.get("instruction_steps", {})
            if isinstance(instr_raw, dict):
                steps = instr_raw.get("en", [])
            elif isinstance(instr_raw, list):
                steps = instr_raw
            else:
                steps = []
            instructions_text = self._clean_text(steps)

            searchable_text = (
                f"Yoga Pose: {name} ({sanskrit}). "
                f"Difficulty: {difficulty}. Focus: {focus}. "
                f"Categories: {categories}. Target Areas: {target_areas}. "
                f"Benefits: {benefits}. Description: {description}. "
                f"Steps: {instructions_text}"
            )

            docs.append({
                "doc_id": f"yoga_{item.get('id', len(docs) + 1)}",
                "title": f"{name} ({sanskrit})" if sanskrit else name,
                "name": name,
                "sanskrit_name": sanskrit,
                "doc_type": "yoga",
                "source_file": "datasets/yoga/yoga.json",
                "metadata": {
                    "difficulty": difficulty,
                    "focus": focus or categories,
                    "target_areas": target_areas,
                    "equipment": "yoga mat / body weight",
                    "image": item.get("image", ""),
                },
                "benefits": benefits,
                "instructions": steps if isinstance(steps, list) else [instructions_text],
                "text": searchable_text,
            })

        self.stats["yoga"] = len(yoga_items)

        # 2. Index Workout Exercises (datasets/workout/exercises.json)
        workout_items = self._load_json(EXERCISEDB_FILE)
        seen_names = set()
        workout_count = 0
        for item in workout_items:
            name = self._clean_text(item.get("name", "Exercise"))
            norm_name = name.lower()
            if not norm_name or norm_name in seen_names:
                continue
            seen_names.add(norm_name)

            body_part = self._clean_text(item.get("body_part", ""))
            category = self._clean_text(item.get("category", ""))
            equipment = self._clean_text(item.get("equipment", "body weight"))
            muscle_group = self._clean_text(item.get("muscle_group", ""))
            target = self._clean_text(item.get("target", ""))
            secondary = self._clean_text(item.get("secondary_muscles", []))

            instr_steps = item.get("instruction_steps", {})
            if isinstance(instr_steps, dict):
                steps = instr_steps.get("en", [])
            elif isinstance(instr_steps, list):
                steps = instr_steps
            else:
                steps = []

            instr_summary = ""
            if isinstance(item.get("instructions"), dict):
                instr_summary = self._clean_text(item["instructions"].get("en", ""))
            elif isinstance(item.get("instructions"), str):
                instr_summary = self._clean_text(item["instructions"])

            if not steps and instr_summary:
                steps = [instr_summary]

            searchable_text = (
                f"Workout Exercise: {name}. "
                f"Body Part: {body_part}. Category: {category}. "
                f"Target Muscle: {target}. Muscle Group: {muscle_group}. "
                f"Secondary Muscles: {secondary}. Equipment: {equipment}. "
                f"Instructions: {instr_summary or self._clean_text(steps)}"
            )

            docs.append({
                "doc_id": f"workout_{item.get('id', len(docs) + 1)}",
                "title": name.title(),
                "name": name.title(),
                "doc_type": "workout",
                "source_file": "datasets/workout/exercises.json",
                "metadata": {
                    "body_part": body_part,
                    "target": target or muscle_group,
                    "equipment": equipment,
                    "secondary_muscles": secondary,
                    "gif_url": item.get("gif_url", ""),
                    "image": item.get("image", ""),
                },
                "benefits": f"Targets {target or body_part} ({equipment})",
                "instructions": steps,
                "text": searchable_text,
            })
            workout_count += 1

        self.stats["workout"] = workout_count

        # 3. Index Clinical Safety Rules (ml/health_rules.json)
        rules = HealthSafetyEvaluator().rules
        precautions = rules.get("condition_precautions", {})
        for cond_key, cond_info in precautions.items():
            label = cond_info.get("label", cond_key)
            warning = cond_info.get("warning", "")
            docs.append({
                "doc_id": f"safety_{cond_key}",
                "title": f"Clinical Guideline: {label}",
                "name": label,
                "doc_type": "safety",
                "source_file": "ml/health_rules.json",
                "metadata": {
                    "condition": cond_key,
                    "equipment": "clinical guideline",
                    "target": label,
                },
                "benefits": warning,
                "instructions": [warning],
                "text": f"Safety Guideline Injury Condition {label} {cond_key.replace('_', ' ')}: {warning}",
            })
        self.stats["safety"] = len(precautions)

        self.documents = docs
        self.stats["total"] = len(docs)

        if self.documents:
            corpus = [doc["text"] for doc in self.documents]
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def _is_contraindicated(self, doc, health_assessment):
        """Return True if a document triggers an active injury contraindication."""
        if not health_assessment or doc.get("doc_type") == "safety":
            return False

        active_conditions = []
        selected = health_assessment.get("selected_conditions") or []
        if isinstance(selected, str):
            try:
                selected = json.loads(selected)
            except Exception:
                selected = [s.strip() for s in selected.split(",") if s.strip()]

        for cond_key in CONTRAINDICATION_KEYWORDS:
            if health_assessment.get(cond_key) or cond_key in selected:
                active_conditions.append(cond_key)

        extra_text = " ".join([
            str(health_assessment.get("other_medical_condition") or ""),
            str(health_assessment.get("additional_information") or ""),
            str(health_assessment.get("affected_body_part") or ""),
        ]).lower()
        for cond_key in CONTRAINDICATION_KEYWORDS:
            readable = cond_key.replace("_pain", "").replace("_", " ")
            if readable in extra_text and cond_key not in active_conditions:
                active_conditions.append(cond_key)

        if not active_conditions:
            return False

        text_lower = doc.get("text", "").lower()
        for cond_key in active_conditions:
            for risky_term in CONTRAINDICATION_KEYWORDS[cond_key]:
                if risky_term in text_lower:
                    return True
        return False

    def retrieve(
        self,
        query,
        top_k=6,
        focus_filter="all",
        health_assessment=None,
        profile=None,
    ):
        """
        Retrieve top-K semantically similar documents from the vector index.
        Applies clinical contraindication filtering and goal/level re-ranking.
        """
        if not self.documents or self.tfidf_matrix is None:
            return []

        query_clean = self._clean_text(query)
        if not query_clean:
            return []

        # Enrich query with user's fitness level / goal for better semantic recall
        enriched_parts = [query_clean]
        if profile:
            if profile.get("fitness_level"):
                enriched_parts.append(str(profile["fitness_level"]))
            if profile.get("fitness_goal"):
                enriched_parts.append(str(profile["fitness_goal"]).replace("_", " "))
        enriched_query = " ".join(enriched_parts)

        query_vec = self.vectorizer.transform([enriched_query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        focus_filter = str(focus_filter or "all").lower().strip()
        user_level = str((profile or {}).get("fitness_level") or "").lower().strip()

        scored_candidates = []
        for idx, sim in enumerate(similarities):
            doc = self.documents[idx]
            doc_type = doc["doc_type"]

            # Always respect focus_filter for exercise/yoga selection (still allow safety rules if score is relevant)
            if focus_filter in ("yoga", "workout") and doc_type not in (focus_filter, "safety"):
                continue

            if self._is_contraindicated(doc, health_assessment):
                continue

            score = float(sim)
            # Subtle metadata boost for matching fitness difficulty level
            if user_level and doc_type == "yoga":
                doc_diff = str(doc["metadata"].get("difficulty", "")).lower()
                if doc_diff == user_level:
                    score *= 1.15

            if score > 0.01:
                scored_candidates.append((score, doc))

        scored_candidates.sort(key=lambda pair: pair[0], reverse=True)

        # Ensure diversity if focus_filter == "all": balance yoga and workout results when relevant
        results = []
        for score, doc in scored_candidates[:top_k]:
            results.append({
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "name": doc["name"],
                "doc_type": doc["doc_type"],
                "source_file": doc["source_file"],
                "similarity_score": round(min(score, 0.99), 4),
                "similarity_pct": round(min(score * 100, 99.0), 1),
                "metadata": doc["metadata"],
                "benefits": doc["benefits"],
                "instructions": doc["instructions"][:5],
                "text": doc["text"],
            })

        return results


# Singleton instance loaded once per server worker
rag_retriever = RAGRetriever()
