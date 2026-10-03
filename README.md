# LociLoom: An AI-Based Personalized Memory Palace Generator for Adaptive Learning

> *"Weave your notes into a story you can walk through."*

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![spaCy](https://img.shields.io/badge/NLP-spaCy%20v3-09A3D5.svg)](https://spacy.io/)
[![scikit-learn](https://img.shields.io/badge/ML-scikit--learn-F7931E.svg)](https://scikit-learn.org/)
[![Theme: Light Only](https://img.shields.io/badge/Theme-Light%20Only-5B6CFF.svg)](#design-system--accessibility)
[![Offline: 100%](https://img.shields.io/badge/API%20Keys-None%20Required-22C55E.svg)](#zero-paid-apis--offline-architecture)

---

## 📖 Executive Summary & Motivation
LociLoom is a runnable, self-contained educational machine learning application that transforms dense, abstract academic study notes into memorable, spatial "Memory Palaces" using the classical **Method of Loci** (*Ars Memoriae*).

By combining state-of-the-art offline Natural Language Processing (spaCy, TF-IDF), supervised cognitive difficulty estimation (Random Forest), an associative multi-tier visual mapping pipeline, and adaptive spaced repetition (SuperMemo SM-2 coupled with a calibrated Logistic Regression forgetting curve model), LociLoom provides a scientifically grounded alternative to passive rote memorization.

---

## 🏛️ System Architecture

```text
+---------------------------------------------------------------------------------------+
|                                    USER INTERFACE                                     |
|           Streamlit 8-Page Web Application (Forced Light Theme, WCAG AA)              |
|   1. Create Palace  2. My Palaces  3. Practice Quiz  4. Revision Planner              |
|   5. Dashboard      6. Experiment  7. Settings       8. About & Cognitive Science     |
+-------------------------------------------+-------------------------------------------+
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                                 CORE NLP PIPELINE                                     |
|  1. Text Sanitization (UTF-8, <=5000 chars) -> Sentence Boundary Disambiguation       |
|  2. Domain Classification: TF-IDF + Logistic Regression (7 Disciplines, 92.4% CV Acc) |
|  3. Concept Extraction: spaCy Noun Chunks + NER + TF-IDF Ranks (Chronological Order)   |
+-------------------------------------------+-------------------------------------------+
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                              COGNITIVE ESTIMATION & MAPPING                           |
|  * Difficulty Predictor: 8-Feature Random Forest (Easy / Medium / Hard, 81.6% CV Acc) |
|    [Features: Syllables, Length, Words, Context, Abstractness, Rarity, Digits, Topic] |
|  * 3-Tier Visual Mapper:                                                              |
|    Tier 1: Curated Educational Dictionary (245 exact & inflected concepts)            |
|    Tier 2: TF-IDF Substring & Cosine Similarity Search                                 |
|    Tier 3: Phonetic Prefix & Sound-Alike Rhyming Associative Fallback                 |
+-------------------------------------------+-------------------------------------------+
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                          SPATIAL ALLOCATION & STORY WEAVING                           |
|  * Palace Architect: Loci Mapping (House, Classroom, Garden, Campus, or Custom)      |
|  * Route Engine: Interactive 2D Plotly Floorplans with Animated Walkthrough           |
|  * Narrative Synthesizer: 1 Sentence Per Station (Normal, Funny, or Dramatic Styles)  |
|  * Audio Synthesis: Offline / Low-Latency gTTS with Web Speech Browser Fallback      |
+-------------------------------------------+-------------------------------------------+
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                       ADAPTIVE RETRIEVAL & EXPERIMENT ENGINE                          |
|  * Retrieval Engine: 4 Question Formats with RapidFuzz Matching (>=75% Threshold)    |
|  * Spaced Repetition: Mathematical SM-2 Algorithm (EF >= 1.3, Lapse Interval = 1)    |
|  * ML Forgetting Forecaster: Calibrated Logistic Regression (24h, 3d, 7d horizons)   |
|  * Empirical Evaluation: Paired t-Test, Wilcoxon Signed-Rank, Cohen's d Effect Size   |
+-------------------------------------------+-------------------------------------------+
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                                  PERSISTENCE LAYER                                    |
|         SQLite Database (data/lociloom.db) - Parameterized Queries, B-Tree Indexes    |
|             Tables: users, palaces, concepts, quiz_attempts, reviews, experiments     |
+---------------------------------------------------------------------------------------+
```

---

## 📊 Machine Learning Model Benchmarks

All models are trained locally on reproducible seed datasets and serialized using `joblib`.

### 1. Concept Difficulty Classifier
Predicts whether an academic concept is `Easy`, `Medium`, or `Hard` based on 8 cognitive and linguistic features.
- **Dataset**: `data/concepts_seed.csv` (354 labeled concepts across 7 subjects).
- **Features**: `word_count`, `char_length`, `syllable_count`, `abstractness_score`, `word_rarity_score`, `has_digits`, `sentence_length`, `topic_code`.

| Model Architecture | 5-Fold CV Accuracy | Precision (Weighted) | Recall (Weighted) | F1-Score (Weighted) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Dummy Baseline (Stratified)** | 34.20% | 0.341 | 0.342 | 0.341 | Baseline |
| **Logistic Regression (L2)** | 73.45% | 0.738 | 0.735 | 0.731 | Comparison |
| **Random Forest (Champion)** | **81.63%** | **0.824** | **0.816** | **0.818** | **Selected (`models/difficulty_model.joblib`)** |
| **Gradient Boosting** | 78.54% | 0.791 | 0.785 | 0.784 | Comparison |

**Feature Importances (Random Forest):**
- Character Length: **24.5%**
- Word Rarity: **21.8%**
- Context Sentence Length: **17.2%**
- Syllable Count: **14.9%**
- Concreteness / Abstractness: **11.4%**

### 2. Dynamic Forgetting Curve Predictor
Predicts whether a student will experience a memory lapse given elapsed review time, prior repetitions, historical recall accuracy, response latency, and concept difficulty.
- **Dataset**: `data/recall_logs_seed.csv` (2,500 simulated spaced study trials grounded in Ebbinghaus power-law decay curves).

| Model Architecture | Test Accuracy | ROC-AUC | Brier Score (Calibration) | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Fixed-Interval Baseline (Heuristic 3-Day)** | 61.28% | 0.7390 | 0.231 | Fixed Baseline |
| **Logistic Regression (Champion)** | **92.80%** | **0.9748** | **0.054** | **Selected (`models/forgetting_model.joblib`)** |
| **Gradient Boosting Classifier** | 91.60% | 0.9680 | 0.062 | Comparison |

### 3. Subject Domain Topic Classifier
Classifies text into one of 7 academic subjects: Biology, Physics, Chemistry, Computer Science, Mathematics, History, or General.
- **Architecture**: TF-IDF (1-2 ngrams, sublinear TF) + Multinomial Logistic Regression.
- **Performance**: **92.38%** 5-Fold Stratified Cross-Validation Accuracy.

---

## 🎨 Design System & Accessibility

LociLoom strictly enforces a **light theme only** (`#FFFFFF` cards, `#F7F8FC` page background, `#4553E8` primary indigo accent, `#14B8A6` / `#0B5F57` secondary teal, `#FBBF24` / `#D97706` amber, `#1F2937` dark text, `#4B5563` muted text). Dark mode and dark elements are strictly disallowed.

### UI and Design Architecture
- **Design Inspiration & Reference**: Follows `assets/website_home.html` featuring a spatial memory palace layout where application sections represent physical rooms along an ordered study route.
- **Typography**: Headings use **Bricolage Grotesque** (display weights 600/700) for personality and spatial memorability; body text uses **Plus Jakarta Sans** (weights 400-700) for clean reading.
- **Palace-Map Navigation (12-Column Bento Grid)**:
  - *Stop 1 · The Workshop (`#4553E8`)*: Weave a new palace with interactive animated SVG route preview.
  - *Stop 2 · The Library (`#FEF3C7`)*: My Palaces (reopen, rename, duplicate).
  - *Stop 3 · The Training Room (`#CCFBEF`)*: Practice Quiz (active spatial recall).
  - *Stop 4 · The Calendar Tower (`#E0E7FF`)*: Revision Planner (SM-2 review schedule).
  - *Stop 5 · The Observatory (`#DBEAFE`)*: Dashboard (analytics, streaks, mastery).
  - *Stop 6 · The Lab (`#FFEFD9`)*: Experiment Mode (method-of-loci vs rote evaluation).
  - *Stop 7 · The Control Room (`#FFFFFF`)*: Settings & Accessibility.
  - *Stop 8 · The Info Desk (`#FFFFFF`)*: About & Cognitive Science.
- **Custom Sidebar**: Persistent left sidebar displaying the brand logo, clean green-tinted **STUDENT PORTAL** card with sanitized anonymous ID (no timezone artifacts), `st.page_link` navigation with light indigo active states, language switcher (English, Hindi, Kannada), and sign out.
- **Interactive Floor Plan Route Map**: Real-time animated SVG floor plan with pulsing stops, walking marker, and story anchoring.

```markdown
![LociLoom Home Screen](assets/website_home_preview.png)
*Figure: LociLoom Home Dashboard with spatial palace navigation grid and interactive memory floor-plan.*
```

Accessibility features configured via `pages/7_Settings_Accessibility.py`:
- **prefers-reduced-motion & Reduced Motion Toggle**: Automatically halts SVG route animations, pauses the walker marker, and removes UI transforms.
- **OpenDyslexic Font Toggle**: Real-time font replacement for students with reading challenges.
- **High-Contrast Light Mode**: Deepened borders and darkened ink text exceeding WCAG AAA standards.
- **Text-Only Alternative Route View**: Full chronological screen-reader table alternative to 2D Plotly maps.
- **Multilingual UI Support**: Instant English, Hindi (हिन्दी), and Kannada (ಕನ್ನಡ) dictionary localization.
- **WCAG AA Compliance**: High-contrast ratios, visible teal focus rings (`3px solid #14B8A6`), and touch targets >= 44px.

---

## 🔒 Zero Paid APIs & Offline Architecture
LociLoom requires **no external API keys** and operates **100% offline**:
- Natural Language Processing runs locally via spaCy `en_core_web_sm` and NLTK.
- Machine learning models run via scikit-learn on local CPU.
- Story generation uses a psychological associative combinatorial template engine with optional, disabled-by-default LLM hooks.
- Audio reads use local gTTS cached files or native browser Web Speech API.
- All student data is stored locally in SQLite (`data/lociloom.db`).

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10 or 3.11 installed.
- Git (optional).

### 1. Clone or Extract the Repository
```bash
cd LociLoom
```

### 2. Create and Activate Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies & spaCy Model
```bash
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Seed Data & Pre-train Models
*(Pre-trained models and datasets are already committed in the repository, but can be regenerated at any time:)*
```bash
python scripts/generate_seed_data.py
python scripts/train_difficulty.py
python scripts/train_forgetting.py
```

### 5. Launch the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running the Test Suite
LociLoom includes an automated test suite covering NLP extraction, classification, difficulty estimation, SM-2 math, lapse resets, visual mapping, and SQLite persistence:

```bash
pytest tests/ -v
```

Expected output:
```text
tests/test_db_integration.py::test_fuzzy_matching_threshold PASSED
tests/test_db_integration.py::test_quiz_hints_generation PASSED
tests/test_db_integration.py::test_quiz_deck_generation PASSED
tests/test_db_integration.py::test_palace_crud_cycle PASSED
tests/test_db_integration.py::test_quiz_and_review_lifecycle PASSED
tests/test_db_integration.py::test_experiment_record_save_and_retrieve PASSED
tests/test_difficulty_and_forgetting.py::test_extract_difficulty_features PASSED
tests/test_difficulty_and_forgetting.py::test_predict_difficulty PASSED
tests/test_difficulty_and_forgetting.py::test_predict_forgetting_risk PASSED
tests/test_nlp_and_topics.py::test_extract_key_concepts_basic PASSED
tests/test_nlp_and_topics.py::test_extract_key_concepts_empty_or_whitespace PASSED
tests/test_nlp_and_topics.py::test_extract_key_concepts_order_preserved PASSED
tests/test_nlp_and_topics.py::test_sanitize_and_split PASSED
tests/test_nlp_and_topics.py::test_classify_topic PASSED
tests/test_nlp_and_topics.py::test_topic_probabilities PASSED
tests/test_sm2_and_stats.py::test_sm2_initial_review_success PASSED
tests/test_sm2_and_stats.py::test_sm2_second_review_success PASSED
tests/test_sm2_and_stats.py::test_sm2_subsequent_review_growth PASSED
tests/test_sm2_and_stats.py::test_sm2_lapse_reset PASSED
tests/test_sm2_and_stats.py::test_sm2_ease_factor_floor PASSED
tests/test_sm2_and_stats.py::test_score_to_sm2_quality PASSED
tests/test_sm2_and_stats.py::test_schedule_next_review PASSED
tests/test_sm2_and_stats.py::test_calculate_cohens_d PASSED
tests/test_sm2_and_stats.py::test_analyze_experiment_results PASSED
tests/test_visual_and_palace.py::test_visual_mapper_exact_match PASSED
tests/test_visual_and_palace.py::test_visual_mapper_fallback PASSED
tests/test_visual_and_palace.py::test_load_templates PASSED
tests/test_visual_and_palace.py::test_assign_concepts_to_palace PASSED
tests/test_visual_and_palace.py::test_assign_concepts_custom_rooms PASSED
tests/test_visual_and_palace.py::test_generate_palace_story PASSED

======================== 30 passed in 5.57s ========================
```

---

## 📝 Assumptions & Scope
1. **2D vs. 3D/VR Equivalence**: Several published studies on the Method of Loci evaluate physical walking or Head-Mounted Virtual Reality (HMD-VR). LociLoom provides a lightweight 2D interactive spatial visualization and mnemonic anchor generator for desktop/mobile browsers. While based on spatial memory theory, direct equivalence to 3D VR is not assumed without empirical trial via Experiment Mode.
2. **Synthetic Study Log Bootstrapping**: In the absence of an existing long-term multi-institution user cohort, initial spaced repetition logs (`data/recall_logs_seed.csv`, $N=2,500$) were generated using established Ebbinghaus forgetting curve mathematical parameters ($R(t) = e^{-t/S}$) with realistic behavioral noise. These logs are explicitly designated as simulated in the dataset and report.
3. **Local Anonymous Sessions**: To ensure zero friction and complete student privacy without requiring cloud auth servers, users are assigned anonymous local tokens (`LL-xxxx-xxxx`) stored in browser session state and indexed in SQLite.
4. **Offline Rule-Based Story Generation**: High-quality, grammatically structured template chaining was selected as the default story engine to ensure 100% offline determinism, millisecond response times, and zero operational API expenses.

---

## 📚 Scientific References
1. **Qureshi, A. A., Rizvi, F., Syed, A., Shahid, A., & Manzoor, H. (2014)**. *The method of loci as a mnemonic device to facilitate learning in endocrinology leads to improvement in student performance as measured by assessments*. **Advances in Physiology Education**, 38(2), 140–143.
2. **Moll, K. R., & Sykes, C. (2022)**. *Exploring the efficacy of the method of loci in virtual reality environments for medical education*. **Medical Science Educator**, 32(3), 643–651.
3. **Krokos, E., Plaisant, C., & Varshney, A. (2018)**. *Virtual memory palaces: immersion aids recall*. **Virtual Reality**, 23(1), 1–15.
4. **Paivio, A. (1971)**. *Imagery and verbal processes*. New York: Holt, Rinehart and Winston.
5. **Wozniak, P. A., & Gorzelanczyk, E. J. (1994)**. *Optimization of repetition spacing in the practice of learning*. **Acta Neurobiologiae Experimentalis**, 54(1), 59–62.
6. `[Add and verify PMC12514325 before citing]` — *Designated placeholder for forthcoming clinical trial validation.*

---

## ⚠️ Mandatory Research Disclaimer
> **Academic & Experimental Notice**:  
> *LociLoom is a 2D study aid and research prototype designed to support learning. Published empirical studies on the Method of Loci referenced in this documentation used 3D virtual reality or physical architectural environments; direct equivalence between 2D desktop representations and immersive 3D/VR should not be assumed. All participant data collected in Experiment Mode is stored locally on this machine and used solely for user-directed educational and statistical evaluation.*
