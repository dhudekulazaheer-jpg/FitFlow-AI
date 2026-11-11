"""
FitFlow AI Online RAG (Retrieval-Augmented Generation) + ICL Engine.

Pipeline:
1. Clinical Safety Gate: Screens for uncleared surgery or acute contraindications.
2. Vector Retrieval: Queries `RAGRetriever` over `yoga.json`, `exercises.json`, and `health_rules.json`.
3. In-Context Learning (ICL): Constructs an augmented prompt containing user biometrics,
   safety precautions, and retrieved knowledge chunks with explicit source citations.
4. Online LLM Generation: Sends the augmented prompt to an online Generative AI provider
   (Google Gemini, Groq, or OpenAI) and returns grounded, personalized recommendations.
"""

import json
import os
import urllib.error
import urllib.request

from ml.health_safety import evaluate_health_safety
from ml.rag_retriever import rag_retriever


def _get_provider_config():
    """Detect configured online LLM provider dynamically from environment variables."""
    gemini_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if gemini_key:
        return {
            "provider": "gemini",
            "api_key": gemini_key,
            "model": (os.getenv("GEMINI_MODEL") or "gemini-2.5-flash").strip(),
        }

    groq_key = (os.getenv("GROQ_API_KEY") or "").strip()
    if groq_key:
        return {
            "provider": "groq",
            "api_key": groq_key,
            "model": (os.getenv("GROQ_MODEL") or "openai/gpt-oss-120b").strip(),
        }

    openai_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if openai_key:
        return {
            "provider": "openai",
            "api_key": openai_key,
            "model": (os.getenv("OPENAI_MODEL") or "gpt-4o-mini").strip(),
        }

    return None


def _build_icl_prompt(query, retrieved_docs, profile=None, safety_eval=None):
    """Build an In-Context Learning (ICL) prompt combining user context and retrieved docs."""
    profile = profile or {}
    safety_eval = safety_eval or {}

    user_context_lines = [
        f"- Fitness Level: {profile.get('fitness_level', 'beginner')}",
        f"- Primary Goal: {str(profile.get('fitness_goal', 'general_fitness')).replace('_', ' ')}",
    ]
    if profile.get("age"):
        user_context_lines.append(f"- Age: {profile['age']}")
    if profile.get("weight"):
        user_context_lines.append(f"- Weight: {profile['weight']} kg")

    warnings = safety_eval.get("warnings", [])
    safety_block = (
        "\n".join(f"- {w}" for w in warnings)
        if warnings
        else "- No active injury contraindications reported."
    )

    docs_blocks = []
    for idx, doc in enumerate(retrieved_docs, start=1):
        meta = doc.get("metadata", {})
        steps = " | ".join(doc.get("instructions", [])[:3])
        docs_blocks.append(
            f"[Doc {idx}] {doc['title']} (Type: {doc['doc_type'].upper()}, "
            f"Source: {doc['source_file']}, Relevance: {doc['similarity_pct']}%)\n"
            f"Target/Focus: {meta.get('target') or meta.get('focus') or meta.get('body_part', 'General')}\n"
            f"Equipment: {meta.get('equipment', 'body weight')}\n"
            f"Benefits: {doc.get('benefits', '')}\n"
            f"Steps: {steps}"
        )

    retrieved_context = "\n\n".join(docs_blocks) if docs_blocks else "No matching records retrieved."

    system_instruction = (
        "You are FitFlow AI Clinical Wellness & Fitness Coach.\n"
        "You MUST follow strict Retrieval-Augmented Generation (RAG) & In-Context Learning (ICL) rules:\n"
        "1. Base your exercise and yoga pose recommendations strictly on the Retrieved Knowledge Base Documents provided.\n"
        "2. Explicitly cite each recommended movement inline using its tag, e.g. [Doc 1: Boat Pose] or [Doc 2: Glute Bridge].\n"
        "3. Tailor duration, hold times, sets/reps, breathing rhythm, and safety modifications to the User Biometrics and Clinical Precautions.\n"
        "4. Never recommend movements that violate the listed Clinical Precautions.\n"
        "5. Keep the formatting crisp, encouraging, and structured with clear Markdown headings and bullet points."
    )

    user_prompt = (
        f"### USER BIOMETRICS & PROFILE\n"
        f"{chr(10).join(user_context_lines)}\n\n"
        f"### ACTIVE CLINICAL PRECAUTIONS\n"
        f"{safety_block}\n\n"
        f"### RETRIEVED KNOWLEDGE BASE DOCUMENTS\n"
        f"{retrieved_context}\n\n"
        f"### USER REQUEST\n"
        f"{query}\n\n"
        f"### REQUIRED OUTPUT STRUCTURE\n"
        f"1. **Tailored Overview** (briefly connect the request to user goals/safety)\n"
        f"2. **Recommended Routine** (list 3-5 poses/exercises from the retrieved docs with citations, sets/reps or hold durations, and form/breathing cues)\n"
        f"3. **Safety & Recovery Tip** (specific modification or hydration cue)"
    )

    return system_instruction, user_prompt


def _call_gemini(api_key, model, system_instruction, user_prompt):
    """Call Google Gemini REST API."""
    models_to_try = [model]
    for fallback in ("gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"):
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    last_error = None
    for candidate_model in models_to_try:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{candidate_model}:generateContent?key={api_key}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 1200,
            },
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "FitFlowAI/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            candidates = body.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                text = "".join(p.get("text", "") for p in parts).strip()
                if text:
                    return text, f"Google Gemini ({candidate_model})"
            last_error = "Gemini returned an empty response."
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            if e.code == 404:
                last_error = f"Model {candidate_model} unavailable (404)"
                continue
            raise RuntimeError(f"Gemini API error ({e.code}): {err_body[:300]}")
        except Exception as e:
            raise RuntimeError(f"Gemini connection failed: {e}")

    raise RuntimeError(last_error or "Gemini API request failed.")


def _discover_groq_chat_models(api_key):
    """Query Groq /models endpoint for currently enabled chat models as a fallback."""
    try:
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/models",
            headers={
                "Accept": "application/json",
                "User-Agent": "FitFlowAI/1.0",
                "Authorization": f"Bearer {api_key}",
            },
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8")).get("data", [])
        excluded = ("whisper", "orpheus", "prompt-guard", "safeguard", "tts", "audio")
        return [
            m["id"]
            for m in data
            if isinstance(m, dict)
            and m.get("id")
            and not any(bad in m["id"].lower() for bad in excluded)
        ]
    except Exception:
        return []


def _call_openai_compatible(base_url, api_key, model, provider_label, system_instruction, user_prompt):
    """Call OpenAI-compatible chat completions endpoint (Groq or OpenAI)."""
    models_to_try = [model]
    if provider_label == "Groq":
        for fallback in ("openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b", "llama-3.1-8b-instant"):
            if fallback not in models_to_try:
                models_to_try.append(fallback)

    last_error = None
    discovered_checked = False
    idx = 0
    while idx < len(models_to_try):
        candidate_model = models_to_try[idx]
        idx += 1
        payload = {
            "model": candidate_model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.4,
            "max_tokens": 1200,
        }
        req = urllib.request.Request(
            base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "FitFlowAI/1.0",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            choices = body.get("choices", [])
            if choices:
                text = choices[0].get("message", {}).get("content", "").strip()
                if text:
                    return text, f"{provider_label} ({candidate_model})"
            last_error = f"{provider_label} returned an empty response."
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            if e.code in (400, 404) and "model" in err_body.lower():
                last_error = f"{provider_label} model {candidate_model} unavailable ({e.code})"
                if provider_label == "Groq" and not discovered_checked:
                    discovered_checked = True
                    for dyn in _discover_groq_chat_models(api_key):
                        if dyn not in models_to_try:
                            models_to_try.append(dyn)
                continue
            raise RuntimeError(f"{provider_label} API error ({e.code}): {err_body[:300]}")

    raise RuntimeError(last_error or f"{provider_label} API request failed.")


def generate_rag_response(
    query,
    focus_filter="all",
    top_k=5,
    profile=None,
    health_assessment=None,
):
    """
    Execute the complete online RAG pipeline for FitFlow AI.
    """
    query = str(query or "").strip()
    if not query:
        return {
            "success": False,
            "error": "Please enter a question or fitness request for the AI Coach.",
        }

    # 1. Clinical Safety Gate
    safety_eval = evaluate_health_safety(health_assessment)
    if safety_eval.get("paused") or not safety_eval.get("allowed", True):
        return {
            "success": False,
            "paused": True,
            "health_safety_paused": True,
            "error": safety_eval.get("message") or "AI plan generation paused for health safety reasons.",
            "safety_warnings": safety_eval.get("warnings", []),
            "disclaimer": safety_eval.get("disclaimer", ""),
            "retrieved_documents": [],
        }

    # 2. Vector Retrieval from yoga.json, exercises.json, health_rules.json
    retrieved_docs = rag_retriever.retrieve(
        query=query,
        top_k=top_k,
        focus_filter=focus_filter,
        health_assessment=health_assessment,
        profile=profile,
    )

    if not retrieved_docs:
        return {
            "success": False,
            "error": "No matching exercises or yoga poses were found in the knowledge base for that query. Try describing a muscle group, pose, or goal.",
            "retrieved_documents": [],
        }

    # 3. Check Online LLM Provider Configuration (No offline fake responses)
    provider_cfg = _get_provider_config()
    if not provider_cfg:
        return {
            "success": False,
            "missing_api_key": True,
            "error": (
                "Online LLM API key is not configured. Please add GEMINI_API_KEY "
                "(free at aistudio.google.com), GROQ_API_KEY, or OPENAI_API_KEY to your "
                ".env file or Render Environment Variables to enable online RAG generation."
            ),
            "retrieved_documents": retrieved_docs,
            "safety_warnings": safety_eval.get("warnings", []),
            "disclaimer": safety_eval.get("disclaimer", ""),
        }

    # 4. In-Context Learning (ICL) Prompt Construction
    system_instruction, user_prompt = _build_icl_prompt(
        query=query,
        retrieved_docs=retrieved_docs,
        profile=profile,
        safety_eval=safety_eval,
    )

    # 5. Online LLM Generation
    provider = provider_cfg["provider"]
    try:
        if provider == "gemini":
            answer, model_used = _call_gemini(
                provider_cfg["api_key"],
                provider_cfg["model"],
                system_instruction,
                user_prompt,
            )
        elif provider == "groq":
            answer, model_used = _call_openai_compatible(
                "https://api.groq.com/openai/v1/chat/completions",
                provider_cfg["api_key"],
                provider_cfg["model"],
                "Groq",
                system_instruction,
                user_prompt,
            )
        else:
            answer, model_used = _call_openai_compatible(
                "https://api.openai.com/v1/chat/completions",
                provider_cfg["api_key"],
                provider_cfg["model"],
                "OpenAI",
                system_instruction,
                user_prompt,
            )
    except Exception as exc:
        return {
            "success": False,
            "upstream_error": True,
            "error": str(exc),
            "retrieved_documents": retrieved_docs,
            "safety_warnings": safety_eval.get("warnings", []),
            "disclaimer": safety_eval.get("disclaimer", ""),
        }

    return {
        "success": True,
        "query": query,
        "answer": answer,
        "model_used": f"{model_used} · Online RAG + ICL",
        "retrieved_documents": retrieved_docs,
        "knowledge_base_stats": rag_retriever.stats,
        "safety_warnings": safety_eval.get("warnings", []),
        "disclaimer": safety_eval.get("disclaimer", ""),
    }


def get_rag_status():
    """Return index statistics and online LLM configuration status."""
    cfg = _get_provider_config()
    return {
        "indexed_documents": rag_retriever.stats,
        "api_configured": cfg is not None,
        "provider": cfg["provider"] if cfg else None,
        "model": cfg["model"] if cfg else None,
    }
