# LociLoom: Project Report & Academic Dissertation Outline

**Title:** LociLoom: An AI-Based Personalized Memory Palace Generator for Adaptive Learning  
**Tagline:** Weave your notes into a story you can walk through  
**Degree / Course:** B.Tech / B.E. / M.Sc. Computer Science & Engineering Capstone Project  
**Author / Team:** Anonymous Academic Submission  
**Academic Year:** 2026–2027  

---

## Table of Contents
1. [Chapter 1: Abstract & Introduction](#chapter-1-abstract--introduction)
2. [Chapter 2: Literature Review & Theoretical Foundations](#chapter-2-literature-review--theoretical-foundations)
3. [Chapter 3: Problem Statement, Scope & Objectives](#chapter-3-problem-statement-scope--objectives)
4. [Chapter 4: Overall System Architecture & Engineering Methodology](#chapter-4-overall-system-architecture--engineering-methodology)
5. [Chapter 5: Natural Language Processing & Concept Extraction Pipeline](#chapter-5-natural-language-processing--concept-extraction-pipeline)
6. [Chapter 6: Machine Learning Models: Difficulty Estimation & Forgetting Prediction](#chapter-6-machine-learning-models-difficulty-estimation--forgetting-prediction)
7. [Chapter 7: Multi-Tier Visual Mapping & Spatial Route Synthesis](#chapter-7-multi-tier-visual-mapping--spatial-route-synthesis)
8. [Chapter 8: Adaptive Spaced Repetition & SM-2 Integration](#chapter-8-adaptive-spaced-repetition--sm-2-integration)
9. [Chapter 9: User Interface, Inclusive Design & Accessibility](#chapter-9-user-interface-inclusive-design--accessibility)
10. [Chapter 10: Experimental Evaluation & Research Methodology](#chapter-10-experimental-evaluation--research-methodology)
11. [Chapter 11: Quantitative & Qualitative Results Analysis](#chapter-11-quantitative--qualitative-results-analysis)
12. [Chapter 12: Discussion, Limitations & Ethical Considerations](#chapter-12-discussion-limitations--ethical-considerations)
13. [Chapter 13: Conclusion & Future Roadmap](#chapter-13-conclusion--future-roadmap)
14. [References & Appendices](#references--appendices)

---

## Chapter 1: Abstract & Introduction
### 1.1 Abstract
- Overview of academic memorization challenges in higher education.
- Introduction of LociLoom as a zero-cost, offline, AI-assisted mnemonic synthesizer.
- Summary of core innovations: automated concept extraction, Random Forest cognitive difficulty estimation (81.6% CV accuracy), 3-tier associative visual token mapping, dynamic 2D spatial route rendering, and calibrated Logistic Regression forgetting curve forecasting (92.8% test accuracy, 0.975 ROC-AUC).
- Summary of key empirical findings from controlled counterbalanced trials ($N$ participants, Cohen's $d$ effect sizes).

### 1.2 Introduction & Background
- The cognitive load of modern STEM curricula: exponential growth of declarative facts, terminologies, and multi-step mechanisms.
- Historical context: Simonides of Ceos and the ancient Roman *Ars Memoriae* (Method of Loci).
- The transition from manual mnemonic construction to automated, intelligent learning aids.

### 1.3 Motivation & Real-World Impact
- High student burnout and low long-term retention under passive cramming.
- Inaccessibility of existing commercial memory aids (cloud fees, reliance on high-end VR hardware).
- Need for a lightweight, desktop-accessible, privacy-first study assistant.

---

## Chapter 2: Literature Review & Theoretical Foundations
### 2.1 The Method of Loci in Educational Cognitive Science
- Principles of spatial loci (*loci*) and active images (*imagines agentes*).
- Clinical and educational efficacy: Qureshi et al. (2014) in undergraduate medical endocrinology curricula.
- Virtual Reality implementations: Moll & Sykes (2022) and Krokos, Plaisant & Varshney (2018).
- Critical distinction: Immersive 3D/VR vs. interactive 2D desktop representations.

### 2.2 Dual Coding Theory (Paivio, 1971)
- Structural dissociation of verbal (logogens) and visual (imagens) mental representations.
- Additive effects of dual retrieval pathways on memory stability.

### 2.3 Working Memory & Spatial Cognition
- Baddeley’s multicomponent working memory model: visuospatial scratchpad and phonological loop.
- Hippocampal place cells, grid cells, and evolutionary spatial navigation as an anchor for declarative memory.

### 2.4 Ebbinghaus Forgetting Curves & Spaced Repetition
- Hermann Ebbinghaus’s exponential forgetting equation: $R(t) = e^{-t/S}$.
- Piotr Wozniak’s SuperMemo SM-2 algorithm: dynamic interval expansion and Ease Factor ($EF$) updates.

### 2.5 Modern Digital Mnemonic Aids & Comparative Analysis
- Review of flashcard applications (Anki, Quizlet) and their lack of spatial/associative scaffolding.
- Placeholder for emerging clinical literature: `[Add and verify PMC12514325 before citing]`.

---

## Chapter 3: Problem Statement, Scope & Objectives
### 3.1 Formal Problem Statement
- Students struggle to create mental palaces manually due to high initial cognitive overhead, lack of visual imagination, and difficulty in organizing linear academic notes into spatial pathways.

### 3.2 Research Questions & Hypotheses
- **RQ1**: Can an automated NLP and ML pipeline reliably extract and rank concepts while preserving note chronology?
- **RQ2**: Does an 8-feature machine learning model provide superior difficulty estimation compared to naive length baselines?
- **RQ3**: Does studying with a 2D interactive Memory Palace yield statistically significant recall improvements over standard linear text review?

### 3.3 System Requirements & Design Constraints
- Strict Light Theme Only (`#FFFFFF` base, `#5B6CFF` primary accent).
- Zero paid API keys, zero external internet dependencies (100% offline).
- Sub-second pipeline execution on consumer CPUs without GPU acceleration.
- Local SQLite persistence and full student privacy.

---

## Chapter 4: Overall System Architecture & Engineering Methodology
### 4.1 Architectural Overview
- High-level block diagram: Input -> Preprocessing -> Classification -> Extraction -> Difficulty -> Visual Mapping -> Spatial Loci -> Story Weaving -> Retrieval Quiz -> Revision Scheduling.

### 4.2 Technology Stack Justification
- Python 3.10/3.11, Streamlit, spaCy (`en_core_web_sm`), NLTK, scikit-learn, Plotly, RapidFuzz, SQLite3, gTTS.

### 4.3 Database Schema & Relational Design
- Tables: `users`, `palaces`, `concepts`, `quiz_attempts`, `reviews`, `experiment_records`.
- Indexing strategies for high-frequency queries (`idx_concepts_palace_order`, `idx_reviews_due`, `idx_attempts_user`).

---

## Chapter 5: Natural Language Processing & Concept Extraction Pipeline
### 5.1 Input Sanitization & Boundary Detection
- Handling unstructured student inputs, special characters, whitespace, and maximum length boundaries (5,000 characters).
- Sentence splitting via regex and spaCy sentencizer.

### 5.2 Subject Domain Topic Classification
- TF-IDF vectorization (unigrams + bigrams, sublinear term frequency).
- Multinomial Logistic Regression across 7 academic domains: Biology, Physics, Chemistry, Computer Science, Mathematics, History, General.
- 5-Fold Stratified Cross-Validation evaluation (92.38% accuracy).

### 5.3 Hybrid Concept Extraction Engine
- spaCy noun chunk extraction and Named Entity Recognition (NER).
- TF-IDF domain scoring with lexical frequency weighting.
- Chronological appearance sorting: preserving original discourse flow to ensure narrative coherence in spatial routes.
- Robust rule-based fallback mode for systems without pre-installed language models.

---

## Chapter 6: Machine Learning Models: Difficulty Estimation & Forgetting Prediction
### 6.1 Cognitive Difficulty Classifier
- Theoretical justification of 8 extracted features:
  1. `word_count`, 2. `char_length`, 3. `syllable_count`, 4. `abstractness_score`, 
  5. `word_rarity_score`, 6. `has_digits`, 7. `sentence_length`, 8. `topic_code`.
- Model comparison: Dummy Baseline (34.2%), Logistic Regression (73.5%), Gradient Boosting (78.5%), Random Forest (81.6% CV accuracy).
- Feature importance analysis and model serialization via `joblib`.

### 6.2 Dynamic Forgetting Curve Forecaster
- Mathematical simulation of Ebbinghaus memory decay logs ($N=2,500$ seed trials).
- Calibrated Logistic Regression model ($C=1.0$, L-BFGS) predicting lapse probability.
- Evaluation metrics: 92.8% test accuracy, 0.9748 ROC-AUC, 0.054 Brier score vs. Fixed-Interval 3-Day Baseline (61.28% accuracy, 0.7390 AUC).
- Multi-horizon risk forecasting (24-hour, 3-day, 7-day probabilities).

---

## Chapter 7: Multi-Tier Visual Mapping & Spatial Route Synthesis
### 7.1 Visual Mnemonic Generation Principles
- The need for concrete, tactile, bizarre, or emotionally salient visual proxies (*imagines agentes*).

### 7.2 The 3-Tier Cascading Mapping Algorithm
- **Tier 1**: Exact & inflected match against curated educational dictionary (245 concepts).
- **Tier 2**: Character/sublinear TF-IDF cosine similarity search against dictionary definitions.
- **Tier 3**: Phonetic prefix associations and sound-alike rhyming rule fallback.

### 7.3 Spatial Palace Routing & 2D Map Visualization
- Architectural templates: Cozy Modern House, University Classroom, Botanical Garden, College Campus.
- Custom route parsing: user-entered comma-separated physical landmarks arranged in serpentine coordinate grids.
- Interactive Plotly 2D floorplans with animated step markers and direction vectors.

### 7.4 Narrative Story Synthesizer
- Combinatorial template weaving linking stations sequentially (1 sentence per locus).
- Distinct psychological encoding styles: Normal (exploratory), Funny (absurdist/slapstick), Dramatic (epic/cinematic).

---

## Chapter 8: Adaptive Spaced Repetition & SM-2 Integration
### 8.1 Mathematical Formulation of SM-2
- Ease Factor ($EF$) updates: $EF' = EF + (0.1 - (5 - q) \cdot (0.08 + (5 - q) \cdot 0.02))$.
- Interval progression: $I(1)=1$, $I(2)=6$, $I(n)=I(n-1) \cdot EF$.
- Strict lapse resets: $q < 3 \implies I=1, \text{repetitions}=0$.

### 8.2 Retrieval Score Mapping
- Mapping interactive quiz metrics (accuracy, hints used, response time) into SM-2 quality grades (0 to 5).

### 8.3 Machine Learning Enhanced Revision Scheduling
- Integrating forgetting risk probabilities into the revision calendar to prioritize imminent memory lapses.

---

## Chapter 9: User Interface, Inclusive Design & Accessibility
### 9.1 Streamlit Modular Multi-Page Architecture
- Application lifecycle, page caching, and session state management.

### 9.2 Strict Light Theme Design System
- Justification of light palette (`#FFFFFF`, `#F4F6FB`, `#5B6CFF`) for cognitive clarity and glare reduction.

### 9.3 Accessibility & Universal Design
- OpenDyslexic typography integration for neurodivergent learners.
- High-contrast light mode exceeding WCAG AAA standards.
- Reduced motion toggle disabling animations.
- Accessible text-only route table alternative for screen readers.
- Multilingual UI strings: English, Hindi, Kannada.

---

## Chapter 10: Experimental Evaluation & Research Methodology
### 10.1 Within-Subject Counterbalanced Experimental Design
- Condition A: Standard Linear Text Study (Curriculum Preset List A).
- Condition B: LociLoom Memory Palace Study (Matched Curriculum Preset List B).
- Counterbalancing order to eliminate order effects and fatigue bias.

### 10.2 Experimental Protocol & Timed Phases
- Timed study phase (2 minutes per condition).
- Immediate active recall test (typing concepts and multiple-choice).
- 24-Hour delayed retention test to evaluate consolidation.

### 10.3 Statistical Formulations
- Paired Student's $t$-test and Wilcoxon signed-rank test.
- Cohen’s $d$ formulation: $d = \frac{\bar{X}_B - \bar{X}_A}{s_{\text{pooled}}}$.
- Statistical power considerations and minimum sample size warnings.

---

## Chapter 11: Quantitative & Qualitative Results Analysis
### 11.1 Immediate Recall Performance
- Mean accuracy comparisons (Condition A vs. Condition B).
- Statistical significance tests ($t$-statistic, degrees of freedom, $p$-values).
- Effect size calculations and classification.

### 11.2 24-Hour Delayed Retention Consolidation
- Rate of forgetting over 24 hours in linear reading vs. memory palace encoding.
- Empirical validation of Dual Coding Theory.

### 11.3 Study Time & Efficiency Metrics
- Interaction latency, time per item, and hint dependency.

### 11.4 Qualitative User Experience & Engagement
- 5-Point Likert scale ratings on usability, visual memorability, and learning satisfaction.

---

## Chapter 12: Discussion, Limitations & Ethical Considerations
### 12.1 Interpretation of Findings
- Why spatial anchors enhance retrieval accessibility under cognitive load.
- Role of bizarre and humorous narrative styles in reducing proactive interference.

### 12.2 Limitations & Threats to Validity
- 2D desktop visualization vs. full 3D/VR immersive environments.
- Use of simulated forgetting logs for model bootstrapping in the absence of longitudinal field cohorts.
- Linguistic constraints: English concept extraction vs. multilingual localization.

### 12.3 Ethical Considerations & Data Privacy
- Zero telemetry and local SQLite data isolation.
- Transparent reporting of statistical power and non-generalizable sample sizes.
- Mandatory research disclaimer.

---

## Chapter 13: Conclusion & Future Roadmap
### 13.1 Summary of Contributions
- Fully working, local, end-to-end educational ML application combining cognitive science, NLP, and spaced repetition.

### 13.2 Future Work
- Integration with WebXR for browser-based 3D virtual walkthroughs.
- Automatic diagram and image generation for visual objects via local stable diffusion.
- Multilingual entity extraction supporting Indian regional languages (Hindi, Kannada, Tamil).

---

## References & Appendices
### Primary Literature
- Full bibliographic citations formatted in APA 7th Edition.

### Appendix A: Complete Database Schema DDL
### Appendix B: Feature Engineering Formulas & Code Listings
### Appendix C: Standardized Test Suite Logs (30 Unit Tests)
