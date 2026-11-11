# ✦ FitFlow AI – Personalized Yoga, Fitness & RAG Coach

> An intelligent, data-driven wellness platform combining **Online Retrieval-Augmented Generation (RAG) + In-Context Learning (ICL)**, supervised machine learning, clinical health safety guardrails, multi-day split programs, progressive overload guidance, and social streak accountability.

[![Live Demo](https://img.shields.io/badge/live-Render%20Deployment-183D32)](https://fitflow-ai-3wf4.onrender.com)
[![Tests](https://img.shields.io/badge/tests-36%2F36%20passing-brightgreen)](#automated-testing)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/framework-Flask-lightgrey)](https://palletsprojects.com/p/flask/)
[![Database](https://img.shields.io/badge/database-Supabase%20PostgreSQL%20%7C%20MySQL-orange)](https://supabase.com/)

---

## 🌟 Key Features

### 1. Online RAG + In-Context Learning (ICL) Yogi Coach
* **Vector Knowledge Retrieval (`ml/rag_retriever.py`):** Indexes **1,373 curated records** (`48` yoga poses from `datasets/yoga/yoga.json`, `1,318` unique workout movements from `datasets/workout/exercises.json`, and `7` clinical guidelines from `ml/health_rules.json`) using TF-IDF (`ngram_range=(1, 2)`) and Cosine Similarity.
* **In-Context Learning & Grounded Generation (`ml/rag_engine.py`):** Augments online LLM generation (**Groq**, **Google Gemini**, or **OpenAI**) with the user's biometrics, active clinical precautions, and retrieved knowledge base chunks with inline `[Doc X: Name]` citations.
* **Transparent Two-Step UI & Pure CSS Avatar:** Displays both retrieved source cards (with similarity match `%`) and the generated coaching routine, accessible anytime via the animated **Pure HTML & CSS Floating Yogi Coach Button**.

### 2. Intelligent Routine & Program Generation
* **Daily Split & 7-Day Programs:** Generate single-session targeted routines or a complete 7-day progressive split (Push, Pull, Legs, Core, Flexibility, Recovery).
* **ML & Dataset-Powered Plan Engine:** Combines our Scikit-Learn `RandomForestRegressor` calorie model ($R^2 = 0.8602$, trained on Kaggle's Gym Members Exercise Dataset) with curated yoga and resistance routines.
* **Smart Warm-Up & Cool-Down:** Tailors 3-minute warm-up mobility and 3-minute cool-down recovery protocols to the specific body part or yoga focus.
* **Progressive Overload Advisor:** Analyzes session completion history and advises when to advance sets, reps, duration, or jump to intermediate/advanced fitness levels.

### 3. Clinical Health & Safety Screening
* **Medical Screening:** Screens for prior surgeries, chronic joint conditions, and injuries (lower back, knees, shoulders, neck, wrists, ankles, arthritis).
* **Automated Safety Pause & Contraindication Filtering:** Halts risky plan generation on uncleared surgeries, blocks high-impact/contraindicated movements inside both routine generation and RAG retrieval, and provides one-click smart exercise swaps.

### 4. Nutrition & Deep Tissue Recovery
* Calculates personalized recovery hydration targets (`ml`) and post-session protein recommendations (`g`).
* Provides culinary replenishment guidance with electrolyte protocols.

### 5. Interactive Workout Guidance & Web Audio Chimes
* Real-time interactive session player with dual Web Audio API chimes (interval countdown alerts & completion chimes).
* YouTube demonstration links for yoga poses and workout movements.

### 6. Social Accountability: Circle of Consistency
* **Unique Shareable Friend Codes (`#FIT-XXXX`):** Connect with gym partners and friends.
* **Live Streak Leaderboard:** Friendly accountability rankings for active workout streaks, completed sessions, and burned calories.
* **High-Five Kudos:** Send instant encouraging High Fives (`✋✦`) to keep friends motivated.
* **100% Privacy-Preserving:** Health assessments, medical clearances, and injury histories remain strictly private and are never exposed to friends.

### 7. Handcrafted Bespoke Pure CSS Vector Design
* Pure HTML/CSS vector art for system icons and the animated meditating **Yogi Coach** floating avatar—eliminating OS emoji inconsistencies.
* Responsive, sticky frosted-glass navigation bar with smooth scroll elevation.

---

## 🛠️ Architecture & Tech Stack

* **Backend:** Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF (CSRF Protection), Werkzeug, Gunicorn
* **GenAI & RAG Pipeline:** Scikit-Learn TF-IDF Vectorizer + Cosine Similarity, In-Context Learning (ICL) Prompt Augmentation, Online LLM APIs (Groq / Google Gemini / OpenAI)
* **Machine Learning:** Scikit-Learn (`RandomForestRegressor`), Pandas, NumPy, Joblib
* **Cloud Database:** Supabase PostgreSQL (`psycopg[binary]`) & Aiven / Local MySQL 8.x (`PyMySQL` + `cryptography`) with SSL, plus SQLite local fallback
* **Frontend:** Responsive HTML5, Vanilla CSS3 (Custom Properties & Keyframe Vector Art), Vanilla JavaScript (ES6+ Fetch API & Web Audio API)
* **Cloud Hosting:** Render Web Service (`https://fitflow-ai-3wf4.onrender.com`)

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10 or higher
* Supabase PostgreSQL, MySQL 8.x, or SQLite (auto-fallback for local development)
* An online LLM API key (`GROQ_API_KEY`, `GEMINI_API_KEY`, or `OPENAI_API_KEY`) for Yogi Coach RAG generation

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rajesh4275/ICL-gen-AI-project.git
   cd ICL-gen-AI-project
   ```

2. **Set up a Python Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your_secure_secret_key_here
   # Cloud PostgreSQL (Supabase Session Pooler) or MySQL, or omit for local SQLite
   DATABASE_URL=postgresql://postgres.<ref>:PASSWORD@aws-1-region.pooler.supabase.com:5432/postgres
   # Online LLM API key for Yogi Coach RAG (Groq, Gemini, or OpenAI)
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Initialize Database & Run Application:**
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 🧪 Automated Testing

FitFlow AI includes a **36-test automated verification suite** covering database isolation, plan generation, clinical safety, progressive overload, social leaderboards, and the Online RAG + ICL pipeline:

```bash
# Run baseline handover tests (16 tests)
python test_handover.py

# Run smart features test suite (5 tests)
python test_new_features.py

# Run advanced 7-day split & social friends test suite (9 tests)
python test_advanced_features.py

# Run Online RAG + ICL & Yogi Coach UI test suite (6 tests)
python test_rag_feature.py
```

---

## 👥 Contributors & Credits

* **Rajesh** ([@rajesh4275](https://github.com/rajesh4275)) – **Original Project Creator & ML Architect**  
  Conceived FitFlow AI, sourced the Kaggle gym & yoga/exercise datasets, trained the Random Forest calorie prediction pipeline ($R^2 = 0.86$), and built the foundational plan generator prototype.

* **Zaheer Dhudekula** ([@dhudekulazaheer-jpg](https://github.com/dhudekulazaheer-jpg)) – **Full-Stack Feature Engineer, GenAI RAG & Cloud Lead**  
  Engineered the **Online RAG + In-Context Learning (ICL) Yogi Coach** (`ml/rag_retriever.py`, `ml/rag_engine.py`) with animated pure HTML/CSS floating avatar, clinical health safety guardrails, 7-day split & progressive overload modules, social streak leaderboards & kudos, Supabase PostgreSQL / MySQL SSL cloud deployment on Render, and full 36-test automated verification.

---

## 📄 License
This project is developed for educational and wellness development purposes.
