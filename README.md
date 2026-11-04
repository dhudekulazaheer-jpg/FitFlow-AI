# ✦ FitFlow AI – Personalized Yoga & Fitness Companion

> An intelligent, data-driven wellness companion that crafts personalized daily workout and yoga routines, multi-day split programs, automated progressive overload suggestions, recovery nutrition targets, and social streak accountability.

[![Tests](https://img.shields.io/badge/tests-30%2F30%20passing-brightgreen)](#automated-testing)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/framework-Flask-lightgrey)](https://palletsprojects.com/p/flask/)
[![MySQL](https://img.shields.io/badge/database-MySQL%208.0-orange)](https://www.mysql.com/)

---

## 🌟 Key Features

### 1. Intelligent Routine & Program Generation
* **Daily Split & 7-Day Programs:** Generate single-session targeted routines or a complete 7-day progressive split (Push, Pull, Legs, Core, Flexibility, Recovery).
* **Dataset-Powered ML Plan Generator:** Curates yoga asanas and resistance exercises matched to fitness level, equipment, available duration, and target muscle groups.
* **Smart Warm-Up & Cool-Down:** Tailors 3-minute warm-up mobility and 3-minute cool-down recovery protocols to the specific body part or yoga focus.
* **Progressive Overload Advisor:** Analyzes session completion history and advises when to advance sets, reps, duration, or jump to intermediate/advanced fitness levels.

### 2. Clinical Health & Safety Screening
* **Medical Screening:** Screens for prior surgeries, chronic joint conditions, and injuries (Lower back, knees, shoulders, neck, wrists).
* **Dynamic Safety Flags & Exercise Swapping:** Flags contraindications (e.g. uncleared spinal fusions, post-op joints) and allows one-click smart exercise swaps with alternatives that protect delicate joints.

### 3. Nutrition & Deep Tissue Recovery
* Calculates personalized recovery hydration targets (ml) and post-session protein recommendations (g).
* Provides culinary replenishment guidance with electrolyte protocols.

### 4. Interactive Workout Guidance & Web Audio Chimes
* Real-time interactive session player with dual Web Audio API chimes (interval countdown alerts & completion chimes).
* YouTube demonstration links for every single yoga pose and workout movement.

### 5. Social Accountability: Circle of Consistency
* **Unique Shareable Friend Codes (`#FIT-XXXX`):** Connect with gym partners and friends.
* **Live Streak Leaderboard:** Compete friendly for highest active workout streak, completed sessions, and burned calories.
* **High-Five Kudos:** Send instant encouraging High Fives (`✋✦`) to keep friends motivated.
* **100% Privacy-Preserving:** Health assessments, medical clearances, and injury histories are strictly private and never exposed to friends.

### 6. Handcrafted Bespoke CSS Art Design
* Pure HTML/CSS vector icons for all system elements (Daily bolt, 7-day calendar, lotus flower, barbell, growth sprout, and golden trophy crests) eliminating OS emoji inconsistencies.
* Responsive, sticky frosted glass navigation bar with smooth scroll elevation.

---

## 🛠️ Architecture & Tech Stack

* **Backend:** Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF (CSRF Protection), Werkzeug
* **Database:** MySQL 8.0 with SQLAlchemy ORM
* **Frontend:** Responsive HTML5, Vanilla CSS3 (Custom Properties & Keyframe Vector Art), Vanilla JavaScript (ES6+ Asynchronous Fetch API & Web Audio API)
* **ML & Analytics Engine:** Custom rule-based progression algorithms, calorie calculators, and exercise replacement index

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10 or higher
* MySQL Server 8.0 running locally or remotely

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
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=fitflow_ai
   ```

5. **Initialize Database & Run Application:**
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 🧪 Automated Testing

FitFlow AI includes a comprehensive 30-test automated verification suite covering database transactions, plan generation, ML progression, and social leaderboards:

```bash
# Run baseline handover tests (16 tests)
python test_handover.py

# Run smart features test suite (5 tests)
python test_new_features.py

# Run advanced 7-day split & social friends test suite (9 tests)
python test_advanced_features.py
```

---

## 👥 Team Collaboration & Contributions

FitFlow AI is the result of collaborative engineering—originating from foundational domain research and prototype architecture, followed by full-scale enterprise modernization, clinical safety systems, and interactive feature engineering.

### 🌟 Rajesh ([@rajesh4275](https://github.com/rajesh4275)) – Project Founder & Lead System Architect
* **Vision & Core Conception:** Conceived the foundational FitFlow AI mission to bridge intelligent routine planning with holistic physical wellness and yoga routines.
* **Domain Research & Exercise Ontology:** Curated and structured the comprehensive repository datasets encompassing multi-tier yoga asanas, resistance movements, calorie expenditure metrics, and anatomical muscle focus taxonomies.
* **Foundational Plan Generation Engine:** Engineered the original algorithmic framework responsible for matching user fitness levels, equipment availability, and target muscle groups into cohesive routines.
* **Initial Web Application & Prototype UI:** Designed the baseline Flask MVC application structure, foundational route controllers, responsive front-end layouts, and interactive styling patterns.

### 🚀 Zaheer Dhudekula ([@dhudekulazaheer-jpg](https://github.com/dhudekulazaheer-jpg)) – Co-Developer & Modernization Lead (Advancing FitFlow to the Next Level)
* **Enterprise Persistence & Security:** Migrated in-memory session structures to an enterprise MySQL 8.0 relational architecture with SQLAlchemy ORM, secure Werkzeug authentication, CSRF defense, and strict multi-user privacy isolation.
* **Clinical Health & Contraindication Safety Engine (`ml/health_safety.py`):** Developed the rule-based medical screening engine detecting contraindicated movements across surgical histories, recovery stages, and chronic joint vulnerabilities.
* **7-Day Split & Progressive Overload Systems:** Engineered the multi-day structured weekly program generator (`ml/program_generator.py`), smart dynamic warm-up/cool-down protocols, and data-driven progressive overload recommendations (`ml/progression_advisor.py`).
* **Real-Time Interactive Workout Experience:** Built the interactive session player featuring synchronized Web Audio API chimes, direct YouTube reference integrations, and real-time exercise swappers.
* **Social Accountability Network:** Created the "Circle of Consistency" friends ecosystem featuring unique `#FIT-XXXX` shareable codes, real-time streak leaderboards, and High-Five encouragement kudos.
* **Editorial UI Overhaul & CSS Art System:** Crafted bespoke HTML/CSS vector icons eliminating system emojis, engineered sticky frosted-glass navigation with scroll elevation, and implemented a 30-test automated verification suite with 100% test pass rate.

---

## 📄 License
This project is developed for educational and wellness development purposes.
